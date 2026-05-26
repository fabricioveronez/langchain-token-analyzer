"""
Demo de RAG — recuperar e injetar conhecimento externo.

Interface de chat que torna o ciclo do RAG visível:
    - Sidebar: carrega documentos e os embeda na base (fase offline)
    - Chat: pergunta -> recupera -> injeta no prompt -> o modelo responde (fase runtime)

O expander "ver o que o RAG fez" abre a caixa-preta: mostra os trechos recuperados
com o score de cada um e o prompt final montado, antes da resposta.
"""

import os
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

import rag

load_dotenv()

# A base vetorial fica em data/base.db. Esse diretório é montado como volume no
# docker-compose, então a base sobrevive entre execuções (fase offline reaproveitada).
DATA_DIR = Path(__file__).parent / "data"
DB_PATH = DATA_DIR / "base.db"
DOCS_DIR = DATA_DIR / "docs"


def validate_environment() -> bool:
    """Valida se a API key do Google está configurada."""
    google_key = os.getenv("GOOGLE_API_KEY")
    if not google_key or google_key.startswith("your-"):
        return False
    return True


@st.cache_resource
def get_connection():
    """Conexão única com o banco vetorial (reaproveitada entre interações)."""
    DATA_DIR.mkdir(exist_ok=True)
    return rag.get_db(str(DB_PATH))


def load_example_docs(conn) -> int:
    """Lê os documentos de exemplo de data/docs/ e os embeda na base.

    Retorna quantos foram realmente adicionados (ignora os que já estavam na base).
    """
    arquivos = sorted(DOCS_DIR.glob("*.md")) + sorted(DOCS_DIR.glob("*.txt"))
    adicionados = 0
    for arquivo in arquivos:
        if rag.embed_and_store(conn, arquivo.name, arquivo.read_text(encoding="utf-8")):
            adicionados += 1
    return adicionados


# ---------------------------------------------------------------------------
# Página
# ---------------------------------------------------------------------------
st.set_page_config(page_title="RAG — recuperar e injetar", page_icon="🔎")
st.title("🔎 RAG — recuperar e injetar conhecimento externo")
st.caption(
    "Faça uma pergunta: o sistema busca o trecho relevante na base e injeta no "
    "prompt antes do modelo responder."
)

if not validate_environment():
    st.error(
        "⚠️ Configure a variável `GOOGLE_API_KEY` no arquivo `.env` "
        "(use o `.env.example` da raiz como referência)."
    )
    st.stop()

conn = get_connection()

if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------------------------
# Sidebar — fase offline: popular a base
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("📁 Base de conhecimento")
    st.caption("Fase offline: embeda os documentos e persiste no banco vetorial.")

    st.metric("Trechos na base", rag.count_docs(conn))

    uploads = st.file_uploader(
        "Carregar documentos (.md / .txt)",
        type=["md", "txt"],
        accept_multiple_files=True,
    )
    if st.button("Embedar e salvar na base", disabled=not uploads):
        adicionados = 0
        with st.spinner("Embedando e persistindo..."):
            for arquivo in uploads:
                texto = arquivo.read().decode("utf-8")
                if rag.embed_and_store(conn, arquivo.name, texto):
                    adicionados += 1
        pulados = len(uploads) - adicionados
        msg = f"{adicionados} documento(s) adicionado(s)."
        if pulados:
            msg += f" {pulados} já estava(m) na base (ignorado(s))."
        st.success(msg)
        st.rerun()

    st.divider()
    if st.button("Carregar documentos de exemplo"):
        with st.spinner("Embedando os runbooks e post-mortems de exemplo..."):
            n = load_example_docs(conn)
        if n:
            st.success(f"{n} documento(s) de exemplo adicionado(s).")
        else:
            st.info("Os documentos de exemplo já estão na base.")
        st.rerun()

    if st.button("🗑️ Limpar base", help="Apaga todos os trechos para retestar do zero"):
        rag.clear_base(conn)
        st.session_state.messages = []
        st.success("Base esvaziada.")
        st.rerun()

# ---------------------------------------------------------------------------
# Chat — fase runtime: recuperar, injetar, gerar
# ---------------------------------------------------------------------------
# Reexibe o histórico.
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg["role"] == "assistant" and msg.get("retrieved") is not None:
            with st.expander("🔎 ver o que o RAG fez"):
                st.markdown("**Trechos recuperados (ordenados por proximidade):**")
                for item in msg["retrieved"]:
                    st.markdown(
                        f"- `{item['source']}` — distância: `{item['distance']:.4f}`"
                    )
                st.markdown("**Prompt montado (contexto injetado + pergunta):**")
                st.code(msg["prompt"], language="text")

if pergunta := st.chat_input("Pergunte algo sobre os documentos da base..."):
    st.session_state.messages.append({"role": "user", "content": pergunta})
    with st.chat_message("user"):
        st.markdown(pergunta)

    with st.chat_message("assistant"):
        if rag.count_docs(conn) == 0:
            # Base vazia: não há o que recuperar nem injetar. Conversa direto com o
            # modelo, sem RAG — útil para contrastar a resposta sem contexto externo.
            with st.spinner("Sem base — respondendo direto com o modelo..."):
                resposta = rag.generate(rag.get_chat(), pergunta)
            st.markdown(resposta)
            st.caption("⚠️ Base vazia — resposta gerada sem RAG (sem contexto recuperado).")
            st.session_state.messages.append(
                {"role": "assistant", "content": resposta}
            )
        else:
            with st.spinner("Recuperando, injetando e gerando..."):
                recuperados = rag.retrieve(conn, pergunta, k=3)
                prompt = rag.build_prompt(pergunta, recuperados)
                resposta = rag.generate(rag.get_chat(), prompt)

            st.markdown(resposta)
            with st.expander("🔎 ver o que o RAG fez"):
                st.markdown("**Trechos recuperados (ordenados por proximidade):**")
                for item in recuperados:
                    st.markdown(
                        f"- `{item['source']}` — distância: `{item['distance']:.4f}`"
                    )
                st.markdown("**Prompt montado (contexto injetado + pergunta):**")
                st.code(prompt, language="text")

            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": resposta,
                    "retrieved": recuperados,
                    "prompt": prompt,
                }
            )
