# Projetos de AIOps e Inteligência Artificial com Engenharia Cloud

Repositório com projetos de exemplo para as aulas de pós-graduação em **AIOps e Inteligência Artificial com Engenharia Cloud**.

## Estrutura do Repositório

Este repositório é composto de pastas numeradas, onde cada pasta contém um projeto completo com:

- **Código-fonte** da solução
- **README** explicando o projeto, objetivos e como executá-lo
- **Arquivos de configuração** necessários

## Projetos

| # | Projeto | Descrição |
|---|---------|-----------|
| 01 | [langchain-token-analysis](./01-langchain-token-analysis/) | Análise de tokens com LangChain comparando modelos Claude e Gemini em PT/EN |
| 02 | [context-window-monitor](./02-context-window-monitor/) | Dashboard Streamlit para visualizar crescimento da janela de contexto em conversas com Gemini |
| 03 | [temperature-topk-topp](./03-temperature-topk-topp/) | Dashboard Streamlit para explorar parâmetros de sampling (temperature, top_k, top_p) com Gemini 3 Pro |
| 04 | [long-term-memory](./04-long-term-memory/) | Demonstração de memória de longo prazo (persiste entre sessões) com Streamlit + Gemini, usando uv |
| 05 | [rag-retrieve-inject](./05-rag-retrieve-inject/) | Demo de RAG (embed→persist→retrieve→inject) com Streamlit, Gemini e sqlite-vec |

## Como Usar

### Opção 1: Dev Container (Recomendado)

Este repositório está configurado para usar **Dev Containers**, facilitando a configuração do ambiente de desenvolvimento.

**Pré-requisitos**:
- Docker instalado e em execução
- Visual Studio Code
- Extensão "Dev Containers" instalada no VS Code

**Passos**:
1. Abra o repositório no VS Code
2. Quando aparecer o prompt "Reopen in Container", clique em "Reopen in Container"
3. Aguarde a construção do container (primeira vez pode demorar alguns minutos)
4. Navegue até o projeto desejado e siga as instruções do README específico

**Vantagens**:
- Ambiente Python padronizado (3.11)
- Não precisa instalar Python localmente
- Extensões do VS Code pré-configuradas
- Isolamento completo de dependências

### Opção 2: Instalação Local

1. Navegue até a pasta do projeto desejado
2. Leia o README específico do projeto
3. Siga as instruções de instalação e execução

## Requisitos Gerais

- Python 3.8+
- Docker (para alguns projetos)
- Ferramentas cloud conforme especificado em cada projeto

## Contribuição

Para adicionar novos projetos:

1. Crie uma nova pasta numerada (ex: `01-nome-projeto`)
2. Adicione um README descrevendo o projeto
3. Inclua todo o código necessário
4. Faça um commit com a nova estrutura

---

**Pós-Graduação em AIOps e Inteligência Artificial com Engenharia Cloud**
