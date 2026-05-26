"""
Núcleo do RAG demonstrativo.

Aqui vivem as funções puras (sem Streamlit) que materializam o ciclo do RAG
descrito na aula:

    1. Fase offline  -> embed_and_store: embeda o documento e persiste no banco vetorial
    2. Fase runtime  -> retrieve: embeda a pergunta e busca os trechos mais próximos
                     -> build_prompt: injeta os trechos recuperados no prompt
                     -> generate: o modelo responde com o contexto injetado

O banco vetorial é o sqlite-vec: um SQLite comum com uma extensão que adiciona
busca por similaridade. Por ser um arquivo `.db`, a base "populada" na fase
offline fica persistida e é reaproveitada em toda pergunta depois.
"""

import os
import sqlite3

import sqlite_vec
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings

# Dimensão do vetor produzido pelo modelo de embedding do Gemini (gemini-embedding-001).
EMBEDDING_DIM = 3072

# Modelos do Gemini (mesmos padrões usados nos outros projetos do repositório).
EMBEDDING_MODEL = "gemini-embedding-001"
CHAT_MODEL = "gemini-3-pro-preview"


# ---------------------------------------------------------------------------
# Banco vetorial (sqlite-vec)
# ---------------------------------------------------------------------------
def get_db(path: str) -> sqlite3.Connection:
    """Abre (ou cria) o banco sqlite-vec e garante o schema.

    O sqlite-vec é carregado como uma extensão do SQLite. Depois disso, ganhamos
    a tabela virtual `vec0`, que sabe guardar vetores e buscar os mais parecidos.
    """
    conn = sqlite3.connect(path, check_same_thread=False)

    # Carrega a extensão sqlite-vec nesta conexão.
    conn.enable_load_extension(True)
    sqlite_vec.load(conn)
    conn.enable_load_extension(False)

    # Tabela "comum" com o texto original de cada documento.
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS docs (
            id      INTEGER PRIMARY KEY AUTOINCREMENT,
            source  TEXT NOT NULL,
            content TEXT NOT NULL
        )
        """
    )

    # Tabela virtual do sqlite-vec que guarda o vetor de cada documento.
    # O rowid desta tabela é o mesmo id da tabela `docs` (é assim que ligamos
    # o vetor de volta ao texto original).
    conn.execute(
        f"""
        CREATE VIRTUAL TABLE IF NOT EXISTS vec_docs USING vec0(
            embedding float[{EMBEDDING_DIM}]
        )
        """
    )
    conn.commit()
    return conn


def count_docs(conn: sqlite3.Connection) -> int:
    """Quantos trechos já foram embedados e persistidos na base."""
    return conn.execute("SELECT COUNT(*) FROM docs").fetchone()[0]


def clear_base(conn: sqlite3.Connection) -> None:
    """Esvazia a base vetorial (apaga textos e vetores) para retestar do zero."""
    conn.execute("DELETE FROM docs")
    conn.execute("DELETE FROM vec_docs")
    conn.commit()


# ---------------------------------------------------------------------------
# Modelos do Gemini
# ---------------------------------------------------------------------------
def get_embeddings(task_type: str) -> GoogleGenerativeAIEmbeddings:
    """Modelo de embedding.

    `task_type` faz a pergunta e os documentos viverem no mesmo espaço,
    otimizado para recuperação:
        - RETRIEVAL_DOCUMENT -> ao guardar os documentos
        - RETRIEVAL_QUERY    -> ao buscar com a pergunta do usuário
    É o MESMO modelo nos dois casos — é isso que permite comparar os vetores.
    """
    return GoogleGenerativeAIEmbeddings(
        model=EMBEDDING_MODEL,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
        task_type=task_type,
    )


def get_chat() -> ChatGoogleGenerativeAI:
    """Modelo de geração (o que escreve a resposta final)."""
    return ChatGoogleGenerativeAI(
        model=CHAT_MODEL,
        google_api_key=os.getenv("GOOGLE_API_KEY"),
    )


# ---------------------------------------------------------------------------
# Fase 1 (offline): embedar e persistir
# ---------------------------------------------------------------------------
def doc_exists(conn: sqlite3.Connection, source: str) -> bool:
    """Já existe um documento com esse nome (source) na base?"""
    row = conn.execute(
        "SELECT 1 FROM docs WHERE source = ? LIMIT 1", (source,)
    ).fetchone()
    return row is not None


def embed_and_store(conn: sqlite3.Connection, source: str, text: str) -> bool:
    """Embeda um documento e o persiste no banco vetorial.

    Deduplicação por nome: se já existe um documento com esse `source`, não
    reembeda (evita vetores duplicados na base). Retorna True se inseriu,
    False se pulou por já existir.

    Nesta demo cada documento é 1 chunk (1 doc = 1 vetor) — simples de propósito.
    Em produção você quebraria documentos grandes em pedaços menores.
    """
    if doc_exists(conn, source):
        return False

    embeddings = get_embeddings(task_type="RETRIEVAL_DOCUMENT")
    vector = embeddings.embed_documents([text])[0]

    cur = conn.execute(
        "INSERT INTO docs (source, content) VALUES (?, ?)", (source, text)
    )
    doc_id = cur.lastrowid

    # Liga o vetor ao texto usando o mesmo id (rowid).
    conn.execute(
        "INSERT INTO vec_docs (rowid, embedding) VALUES (?, ?)",
        (doc_id, sqlite_vec.serialize_float32(vector)),
    )
    conn.commit()
    return True


# ---------------------------------------------------------------------------
# Fase 2 (runtime): recuperar (retrieve)
# ---------------------------------------------------------------------------
# A query abaixo é o coração do retrieve. `embedding MATCH ?` pede ao sqlite-vec
# os vetores mais próximos do vetor da pergunta; `k = ?` diz quantos vizinhos trazer
# (o sqlite-vec exige essa constraint nas buscas KNN, em vez de LIMIT); `distance` é o
# quão longe cada trecho está (menor = mais parecido). É a busca por significado em SQL.
RETRIEVE_SQL = """
    SELECT docs.source, docs.content, vec_docs.distance
    FROM vec_docs
    JOIN docs ON docs.id = vec_docs.rowid
    WHERE vec_docs.embedding MATCH ?
      AND k = ?
    ORDER BY vec_docs.distance
"""


def retrieve(conn: sqlite3.Connection, question: str, k: int = 3) -> list[dict]:
    """Embeda a pergunta e devolve os `k` trechos mais próximos por significado."""
    embeddings = get_embeddings(task_type="RETRIEVAL_QUERY")
    query_vector = embeddings.embed_query(question)

    rows = conn.execute(
        RETRIEVE_SQL, (sqlite_vec.serialize_float32(query_vector), k)
    ).fetchall()

    return [
        {"source": source, "content": content, "distance": distance}
        for source, content, distance in rows
    ]


# ---------------------------------------------------------------------------
# Fase 2 (runtime): injetar (o "augmented" do RAG)
# ---------------------------------------------------------------------------
def build_prompt(question: str, retrieved: list[dict]) -> str:
    """Monta o prompt final concatenando os trechos recuperados + a pergunta.

    Este é o passo que faz ser RAG: recuperar sem injetar é só busca.
    O contexto recuperado é colado no prompt e mandado junto com a pergunta.
    """
    contexto = "\n\n".join(
        f"[Trecho {i + 1} — fonte: {item['source']}]\n{item['content']}"
        for i, item in enumerate(retrieved)
    )

    return (
        "Você é um assistente de operações (SRE). Responda à pergunta usando "
        "APENAS o contexto recuperado abaixo. Se a resposta não estiver no "
        "contexto, diga que não encontrou na base.\n\n"
        "=== CONTEXTO RECUPERADO ===\n"
        f"{contexto}\n"
        "=== FIM DO CONTEXTO ===\n\n"
        f"Pergunta: {question}"
    )


# ---------------------------------------------------------------------------
# Fase 2 (runtime): gerar
# ---------------------------------------------------------------------------
def generate(chat: ChatGoogleGenerativeAI, prompt: str) -> str:
    """Manda o prompt (já com o contexto injetado) para o modelo e retorna o texto.

    O gemini-3-pro-preview pode devolver `content` como uma lista de blocos
    (cada um com 'type'/'text') em vez de uma string simples. Normalizamos para
    texto puro, concatenando só os blocos de texto.
    """
    response = chat.invoke(prompt)
    content = response.content

    if isinstance(content, str):
        return content

    if isinstance(content, list):
        partes = [
            bloco.get("text", "")
            for bloco in content
            if isinstance(bloco, dict) and bloco.get("type") == "text"
        ]
        return "\n".join(p for p in partes if p)

    return str(content)
