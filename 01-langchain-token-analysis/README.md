# 01 - Análise de Tokens com LangChain

## Descrição

Projeto educacional que demonstra como capturar e analisar métricas de uso de tokens ao trabalhar com diferentes modelos de IA usando LangChain. Compara o consumo de tokens entre:

- **Providers**: Anthropic (Claude) vs Google (Gemini)
- **Modelos**: Claude Sonnet, Haiku vs Gemini Pro, Flash
- **Idiomas**: Português (BR) vs Inglês

## Objetivos de Aprendizado

- Entender como o LangChain captura métricas de tokens
- Aprender a usar callbacks personalizados para monitoramento
- Comparar consumo de tokens entre diferentes providers
- Analisar diferenças de tokenização entre idiomas
- Aplicar boas práticas de análise de custos de LLMs

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
   python main.py
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

### Executar Análise

```bash
python main.py
```

### Ver Resultados

O relatório será gerado em `results/report.md`

## Estrutura de Arquivos

```
01-langchain-token-analysis/
├── README.md              # Este arquivo
├── requirements.txt       # Dependências Python
├── .env.example          # Template de configuração
├── main.py               # Script principal
├── prompts_pt.json       # Prompts em português
├── prompts_en.json       # Prompts em inglês
└── results/              # Relatórios gerados
    └── report.md
```

## Conceitos Principais

### Callbacks do LangChain

O LangChain fornece callbacks para capturar métricas durante a execução. Neste projeto, usamos um callback personalizado:

```python
from langchain_core.callbacks import BaseCallbackHandler

class TokenCounterCallback(BaseCallbackHandler):
    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0

    def on_llm_end(self, response, **kwargs):
        # Captura tokens ao final da execução
        # Extrai informações de usage_metadata
        pass

# Uso
callback = TokenCounterCallback()
result = model.invoke(prompt, config={"callbacks": [callback]})
print(f"Tokens usados: {callback.input_tokens} + {callback.output_tokens}")
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

Para cada execução, o script captura:

1. **Input tokens**: Tokens do prompt enviado
2. **Output tokens**: Tokens da resposta gerada
3. **Total tokens**: Soma de input + output

Estas métricas são essenciais para:
- Estimar custos de uso da API
- Otimizar prompts
- Comparar eficiência entre modelos

## Resultados Esperados

Ao executar a análise, você deverá observar:

1. **Português vs Inglês**: Português usa consistentemente mais tokens (15-35% a mais)
2. **Claude vs Gemini**: Diferenças na tokenização entre providers
3. **Modelos grandes vs pequenos**: Mesma tokenização, mas respostas diferentes em qualidade/tamanho
4. **Eficiência**: Comparação de tokens por modelo para o mesmo prompt

### Exemplo de Saída

```
=== Análise de Tokens com LangChain ===

Carregando prompts...

--- Testando modelos Anthropic ---

Modelo: claude-3-5-sonnet-20241022
  - Executando em português...
    ✓ Input: 45, Output: 312, Total: 357
  - Executando em inglês...
    ✓ Input: 38, Output: 289, Total: 327

Modelo: claude-3-haiku-20240307
  - Executando em português...
    ✓ Input: 45, Output: 245, Total: 290
  - Executando em inglês...
    ✓ Input: 38, Output: 221, Total: 259

--- Testando modelos Google ---
...

--- Gerando relatório ---

Relatório gerado em: results/report.md

✅ Análise concluída com sucesso!
```

## Interpretando o Relatório

O relatório `results/report.md` contém:

### 1. Resumo Executivo
Visão geral da análise realizada

### 2. Comparação por Provider
Tabelas com médias de tokens por modelo e idioma

### 3. Comparação de Idiomas
Percentual de diferença entre português e inglês

### 4. Insights
Observações automáticas sobre os padrões encontrados

### 5. Análise Detalhada
Análise específica do prompt testado

### 6. Conclusões
Recomendações práticas baseadas nos dados

## Próximos Passos

Para expandir este projeto:

1. **Mais providers**: Adicionar OpenAI, Cohere, etc.
2. **Análise de custos**: Multiplicar tokens pelo preço por token
3. **Mais idiomas**: Testar espanhol, francês, alemão
4. **Visualizações**: Criar gráficos com matplotlib/seaborn
5. **Análise de latência**: Medir tempo de resposta
6. **Diferentes tipos de prompts**: Comparar prompts curtos, médios e longos
7. **Streaming**: Testar uso de tokens com respostas em streaming

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
- [Guia de Tokenização](https://platform.openai.com/tokenizer)

## Licença

Este projeto é parte do material educacional da disciplina de AIOps e Inteligência Artificial com Engenharia Cloud.
