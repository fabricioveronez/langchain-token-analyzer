FROM python:3.11-slim

# uv: gerenciador de dependências usado no repositório.
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

# Instala as dependências primeiro (camada cacheável).
COPY pyproject.toml ./
RUN uv pip install --system --no-cache -r pyproject.toml

# Código da aplicação.
COPY rag.py app.py ./

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
