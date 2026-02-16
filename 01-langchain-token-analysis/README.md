# 01 - Análise de Tokens com LangChain

## Descrição

Dashboard interativo com Streamlit que demonstra como capturar e analisar métricas de uso de tokens ao trabalhar com diferentes modelos de IA usando LangChain. Compara o consumo de tokens entre:

- **Providers**: Anthropic (Claude) vs Google (Gemini)
- **Modelos**: Claude Sonnet, Haiku vs Gemini Pro, Flash
- **Idiomas**: Português (BR) vs Inglês

## Objetivos de Aprendizado

- Entender como o LangChain captura métricas de tokens
- Comparar consumo de tokens entre diferentes providers
- Analisar diferenças de tokenização entre idiomas
- Aplicar boas práticas de análise de custos de LLMs
- Visualizar dados com Streamlit e Plotly

## Requisitos

- Python 3.8+
- API Key da Anthropic (Claude)
- API Key do Google (Gemini)

## Como Executar

### Opção 1: Usando Dev Container (Recomendado)

**Pré-requisitos**:
- Docker instalado
- Visual Studio Code com extensão "Dev Containers"

**Passos**:
1. Abra o repositório no VS Code
2. Clique em "Reopen in Container" quando aparecer o prompt
3. Aguarde a construção do container
4. Navegue até o projeto:
   ```bash
   cd 01-langchain-token-analysis
   ```
5. Instale as dependências do projeto:
   ```bash
   pip install -r requirements.txt
   ```
6. Configure suas API keys (veja seção abaixo)
7. Execute:
   ```bash
   streamlit run main.py
   ```

### Opção 2: Instalação Local

**Pré-requisitos**:
- Python 3.8+

**Passos**:

#### 1. Clonar e Navegar

```bash
cd projetos-auxiliares/01-langchain-token-analysis
```

#### 2. Criar Ambiente Virtual

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows
```

#### 3. Instalar Dependências

```bash
pip install -r requirements.txt
```

### Configurar API Keys (Ambas Opções)

Copie o arquivo `.env.example` para `.env` e adicione suas chaves:

```bash
cp .env.example .env
```

Edite o arquivo `.env`:
```
ANTHROPIC_API_KEY=sk-ant-sua-chave-aqui
GOOGLE_API_KEY=sua-chave-google-aqui
```

**Como obter as API keys**:

- **Anthropic**: https://console.anthropic.com/
- **Google**: https://makersuite.google.com/app/apikey

### Executar Dashboard

```bash
streamlit run main.py
```

O dashboard será aberto automaticamente no navegador.

### Usar o Dashboard

1. Na barra lateral, selecione os **providers** desejados (Anthropic, Google ou ambos)
2. Selecione os **modelos** de cada provider
3. Selecione os **idiomas** (Português, Inglês ou ambos)
4. Clique em **Executar Análise**
5. Visualize os resultados: métricas, tabelas, gráficos e respostas completas

## Estrutura de Arquivos

```
01-langchain-token-analysis/
├── README.md              # Este arquivo
├── requirements.txt       # Dependências Python
├── .env.example          # Template de configuração
├── main.py               # Dashboard Streamlit
├── prompts.py            # Gerenciamento de prompts
└── llms.py               # Modelos LLM e execução
```

### Módulos

- **main.py**: Dashboard Streamlit com sidebar de configuração, métricas, tabelas comparativas, gráficos Plotly e respostas completas
- **prompts.py**: Define e gerencia prompts em múltiplos idiomas usando dataclasses Python
- **llms.py**: Implementa factory para criação de modelos LLM e função de execução com captura de tokens

## Conceitos Principais

### Métricas de Tokens no LangChain

O LangChain captura métricas de tokens automaticamente via `usage_metadata` no `AIMessage`:

```python
result = model.invoke(prompt)
usage = result.usage_metadata
# {'input_tokens': 45, 'output_tokens': 312, 'total_tokens': 357}
```

### Tokenização

Diferentes modelos tokenizam texto de forma diferente:

- **Português** geralmente requer mais tokens que inglês (15-35% a mais)
- **Providers** usam diferentes algoritmos de tokenização
- **Modelos** do mesmo provider compartilham o tokenizador

**Exemplo**:
- Frase em inglês: "Artificial Intelligence" → ~2-3 tokens
- Frase em português: "Inteligência Artificial" → ~4-5 tokens

### Métricas Capturadas

Para cada execução, o dashboard captura e exibe:

1. **Input tokens**: Tokens do prompt enviado
2. **Output tokens**: Tokens da resposta gerada
3. **Total tokens**: Soma de input + output

Estas métricas são essenciais para:
- Estimar custos de uso da API
- Otimizar prompts
- Comparar eficiência entre modelos

## Resultados Esperados

Ao executar a análise no dashboard, você verá:

1. **Métricas resumo**: Total de tokens, modelos testados e número de execuções
2. **Tabela comparativa**: Detalhamento de tokens por modelo e idioma
3. **Gráfico de barras**: Comparação visual de input/output tokens
4. **Comparação de idiomas**: Diferença percentual entre PT e EN por provider
5. **Respostas completas**: Texto gerado por cada modelo em expanders

## Troubleshooting

### Erro: "ANTHROPIC_API_KEY não configurada"

Certifique-se de:
1. Ter criado o arquivo `.env` a partir do `.env.example`
2. Ter adicionado sua API key válida no arquivo `.env`
3. Estar executando o script na pasta do projeto

### Erro: "Module not found"

Execute:
```bash
pip install -r requirements.txt
```

### Erro de autenticação na API

Verifique se suas API keys são válidas e estão ativas:
- Anthropic: https://console.anthropic.com/
- Google: https://makersuite.google.com/app/apikey

## Recursos Adicionais

- [Documentação LangChain](https://python.langchain.com/)
- [Anthropic API Docs](https://docs.anthropic.com/)
- [Google AI Studio](https://ai.google.dev/)
- [Streamlit Docs](https://docs.streamlit.io/)
- [Plotly Docs](https://plotly.com/python/)

## Licença

Este projeto é parte do material educacional da disciplina de AIOps e Inteligência Artificial com Engenharia Cloud.
