# 05 — RAG: recuperar e injetar conhecimento externo

Demonstração didática de **RAG (Retrieval-Augmented Generation)**: o sistema busca o
trecho relevante de uma base externa e **injeta no prompt** antes do modelo responder.

O objetivo aqui não é um RAG de produção, e sim **tornar o ciclo visível**: você vê os
trechos recuperados, o score de cada um e o prompt final montado — a "costura" que
normalmente fica escondida.

## A ideia em uma frase

> RAG é a seleção automática de contexto: antes de o modelo responder, um sistema
> recupera o pedaço de conhecimento que responde à pergunta e o concatena ao prompt.
> **Recuperar sem injetar é só busca — o que faz ser RAG é injetar.**

## As duas fases do RAG

Esta demo separa explicitamente as duas fases:

1. **Offline — embedar e persistir (acontece antes, uma vez).**
   Cada documento da base passa por um modelo de *embedding*, que o transforma num
   vetor (a representação do seu significado). Esse vetor é guardado num **banco
   vetorial**. Aqui usamos o `sqlite-vec` — um SQLite com busca por similaridade — então
   a base fica num arquivo `data/base.db`, persistido em volume e reaproveitado depois.

2. **Runtime — recuperar e injetar (a cada pergunta).**
   A pergunta passa pelo **mesmo modelo de embedding** e vira um vetor. O banco compara
   esse vetor com os guardados e devolve os mais próximos (busca por significado). Os
   trechos recuperados são **injetados no prompt** e só então o modelo responde.

## O que observar (objetivos de aprendizado)

- **Busca por significado, não por palavra.** Pergunte "por que meu container fica
  reiniciando sem parar?" — a base não tem essa frase, mas recupera o runbook de
  `CrashLoopBackOff`, porque o significado é vizinho.
- **O "augmented" é literal.** No expander "ver o que o RAG fez", veja o prompt montado:
  o trecho recuperado é concatenado à pergunta e mandado junto para o modelo.
- **O score do retrieve.** Cada trecho recuperado vem com sua distância (menor = mais
  parecido) — é o ranking da busca semântica visível.
- **Persistência da fase offline.** O arquivo `data/base.db` aparece no host depois de
  popular a base e sobrevive a reinícios do container.

## Requisitos

- Docker e Docker Compose
- Uma `GOOGLE_API_KEY` (Gemini) no arquivo `.env` da **raiz do repositório**
  (use o `.env.example` da raiz como referência)

## Como executar

```bash
cd 05-rag-retrieve-inject
docker compose up --build
```

Acesse `http://localhost:8501`.

1. Na barra lateral, clique em **"Carregar documentos de exemplo"** (runbooks e
   post-mortems de incidentes reais de produção) ou faça upload dos seus `.md`/`.txt`.
2. No chat, pergunte algo como *"por que meu container fica reiniciando sem parar?"*.
3. Abra o expander **"ver o que o RAG fez"** para inspecionar os trechos recuperados
   (com score) e o prompt montado.

## Estrutura de arquivos

```
05-rag-retrieve-inject/
├── README.md            # este arquivo
├── compose.yml          # 1 serviço (app Streamlit) + volume para persistir a base
├── Dockerfile           # imagem Python 3.11 com uv
├── pyproject.toml       # dependências (streamlit, langchain-google-genai, sqlite-vec)
├── app.py               # interface de chat (sidebar = offline, chat = runtime)
├── rag.py               # núcleo do RAG: get_db, embed_and_store, retrieve, build_prompt, generate
└── data/
    ├── docs/            # documentos de exemplo (runbooks e post-mortems)
    └── base.db          # banco vetorial gerado em runtime (não versionado)
```

## Detalhes técnicos

- **Embeddings:** `gemini-embedding-001` (3072 dimensões). Usa `task_type` distinto para
  documentos (`RETRIEVAL_DOCUMENT`) e pergunta (`RETRIEVAL_QUERY`) — é o mesmo modelo nos
  dois casos, o que faz pergunta e documentos viverem no mesmo espaço e poderem ser
  comparados.
- **Geração:** `gemini-3-pro-preview` via `langchain-google-genai`.
- **Banco vetorial:** `sqlite-vec`. O retrieve é uma query SQL legível
  (`... WHERE embedding MATCH ? ORDER BY distance LIMIT ?`) — veja `RETRIEVE_SQL` em
  `rag.py`.
- **Chunking:** 1 documento = 1 chunk (simples de propósito, dado o tamanho da base).

## Fora de escopo (de propósito)

Comparação lexical vs. semântica, busca híbrida, re-ranking e chunking real ficam de
fora para manter a demo focada no ciclo **recuperar → injetar → gerar**.
