# Projeto 02 - Monitor de Janela de Contexto

Dashboard interativo com Streamlit para visualizar em tempo real o crescimento da janela de contexto em conversas com modelos LLM (Google Gemini).

## 📋 Descrição

Este projeto demonstra visualmente como a janela de contexto (context window) cresce durante uma conversa com um modelo de IA. A cada interação, você pode ver:

- **Crescimento acumulado de tokens** (input + output)
- **Composição da janela de contexto** (histórico completo da conversa)
- **Métricas agregadas** (total de tokens, média por mensagem, custos estimados)
- **Impacto de diferentes tipos de mensagens** no consumo de tokens

## 🎯 Objetivos de Aprendizado

Ao usar este projeto, você irá:

1. **Entender como tokens se acumulam** em conversas multi-turn
2. **Visualizar o impacto** de mensagens longas vs curtas no consumo
3. **Compreender limites de contexto** dos modelos Gemini
4. **Calcular custos estimados** baseados no uso de tokens
5. **Experimentar com diferentes modelos** (Flash vs Pro)
6. **Praticar monitoramento** usando LangChain 1.x com `usage_metadata`

## 🔧 Requisitos

- Python 3.8 ou superior
- Google API Key (Gemini)
- Navegador web moderno
- Dependências Python (veja `requirements.txt`)

## 🚀 Como Executar

### Opção 1: Instalação Local com venv

```bash
# 1. Entre no diretório do projeto
cd 02-context-window-monitor

# 2. Crie e ative o ambiente virtual
python -m venv venv
source venv/bin/activate  # Linux/Mac
# ou
venv\Scripts\activate  # Windows

# 3. Instale as dependências
pip install -r requirements.txt

# 4. Configure a API key
cp .env.example .env
# Edite o arquivo .env e adicione sua GOOGLE_API_KEY

# 5. Execute o dashboard
streamlit run app.py
```

O dashboard será aberto automaticamente em `http://localhost:8501`

### Opção 2: Dev Container (Recomendado)

Se você está usando VS Code com Docker:

1. Abra o projeto no VS Code
2. Pressione `F1` e selecione "Dev Containers: Reopen in Container"
3. Aguarde o container ser construído
4. Configure o `.env` com sua API key
5. Execute `streamlit run app.py` no terminal integrado

## 📁 Estrutura de Arquivos

```
02-context-window-monitor/
├── app.py                      # Aplicação Streamlit principal
├── chat_manager.py             # Gerenciamento de conversação com LangChain
├── visualizations.py           # Componentes de visualização (gráficos)
├── metrics.py                  # Dataclasses para métricas
├── config.py                   # Configurações e validação de ambiente
├── requirements.txt            # Dependências do projeto
├── .env.example               # Template de configuração
├── .gitignore                 # Arquivos ignorados pelo git
├── README.md                  # Este arquivo
└── assets/
    └── screenshots/           # Screenshots para documentação
```

### Descrição dos Módulos

- **`app.py`**: Interface principal do Streamlit com layout em 3 colunas (configuração, chat, visualizações)
- **`chat_manager.py`**: Classe `ChatManager` que encapsula a lógica de conversação com Gemini usando LangChain
- **`visualizations.py`**: Classe `ContextWindowVisualizer` com funções para gerar gráficos Plotly
- **`metrics.py`**: Dataclass `MessageMetrics` para estruturar dados de tokens por mensagem
- **`config.py`**: Validação de ambiente, modelos disponíveis e cálculo de custos

## 💡 Como Usar

### Interface do Dashboard

O dashboard está dividido em 3 colunas:

#### Coluna Esquerda - Configuração
- **Modelo Gemini**: Escolha entre Flash (rápido/barato) ou Pro (mais capaz/caro)
- **Limite de Tokens**: Defina um limite para receber alertas
- **Limpar Histórico**: Reseta a conversa e todas as métricas
- **Métricas**: Cards com total de mensagens, tokens, média e custo estimado

#### Coluna Central - Chat
- **Interface de chat**: Estilo ChatGPT para conversar com o modelo
- **Badge de tokens**: Cada mensagem mostra quantos tokens consumiu
- **Histórico completo**: Rolagem para ver toda a conversa

#### Coluna Direita - Análise
- **Aba Crescimento**: Gráfico de linha mostrando tokens acumulados
- **Aba Por Mensagem**: Gráfico de barras comparando tokens por mensagem
- **Aba Detalhes**: Tabela completa com timestamp, preview e estatísticas

### Fluxo de Uso

1. **Inicie uma conversa**: Digite uma mensagem simples como "Olá!"
2. **Observe as métricas**: Veja os gráficos atualizarem automaticamente
3. **Experimente diferentes tipos de mensagens**:
   - Mensagem curta: "Oi"
   - Mensagem longa: "Explique em detalhes como funciona a inteligência artificial"
   - Mensagem com código: "Escreva um exemplo de função Python"
4. **Compare os consumos**: Veja como mensagens diferentes afetam os tokens
5. **Teste o limite**: Configure um limite baixo e veja o alerta aparecer

## 🧪 Experimentos Sugeridos

### Experimento 1: Mensagens Curtas vs Longas
- Envie 3 mensagens curtas (1-5 palavras)
- Envie 3 mensagens longas (50+ palavras)
- Compare o crescimento no gráfico de linha

### Experimento 2: Resumo de Conversas
- Converse por 5-10 mensagens
- Peça: "Resuma toda nossa conversa até agora"
- Observe o consumo de tokens da resposta

### Experimento 3: Código vs Texto Natural
- Peça uma explicação teórica (ex: "O que é machine learning?")
- Peça código (ex: "Escreva uma função para calcular fibonacci")
- Compare quantos tokens cada tipo de resposta consome

### Experimento 4: Comparação de Modelos
- Faça uma conversa com gemini-3-flash-preview
- Limpe o histórico
- Repita a MESMA conversa com gemini-3-pro-preview
- Compare custos estimados entre os modelos

## 📚 Conceitos Principais

### Janela de Contexto (Context Window)

A janela de contexto é o histórico completo de mensagens que o modelo "lembra" durante uma conversa. Cada modelo tem um limite máximo:

- **Gemini 3 Flash**: ~1M tokens
- **Gemini 3 Pro**: ~2M tokens

Quando o limite é atingido, as mensagens mais antigas precisam ser removidas.

### Tokens de Entrada vs Saída

- **Input tokens**: Tokens enviados ao modelo (sua pergunta + histórico)
- **Output tokens**: Tokens gerados pelo modelo (resposta)
- **Total tokens**: Input + Output

⚠️ **Importante**: O histórico completo é enviado a cada mensagem! Se você tem 10 mensagens no histórico, todas são reprocessadas.

### Crescimento Acumulado

A cada nova mensagem, o total de tokens cresce:
```
Mensagem 1: 50 tokens (acumulado: 50)
Mensagem 2: 80 tokens (acumulado: 130)
Mensagem 3: 120 tokens (acumulado: 250)
```

Este crescimento é **exponencial** em conversas longas, pois o histórico é sempre incluído.

### Custos por Token

Os modelos Gemini cobram por milhão de tokens:

| Modelo | Input ($/1M) | Output ($/1M) |
|--------|-------------|--------------|
| Flash  | $0.10       | $0.30        |
| Pro    | $0.50       | $1.50        |

**Exemplo**: 10.000 tokens output no Flash = $0.003

## 🔍 Detalhes Técnicos

### LangChain 1.x - usage_metadata

Este projeto usa a API nativa do LangChain 1.x para capturar métricas:

```python
result = model.invoke(messages)
usage = result.usage_metadata  # Dict com input_tokens, output_tokens, total_tokens
```

### Estrutura de MessageMetrics

```python
@dataclass
class MessageMetrics:
    role: str                    # 'user' ou 'assistant'
    content: str                 # Conteúdo da mensagem
    input_tokens: int           # Tokens de entrada
    output_tokens: int          # Tokens de saída
    total_tokens: int           # Total (input + output)
    cumulative_tokens: int      # Acumulado até este ponto
    timestamp: datetime         # Quando foi criada
```

### Persistência de Estado

O Streamlit usa `st.session_state` para manter o estado entre recargas:

- `chat_manager`: Instância do ChatManager
- `messages`: Lista de mensagens para exibição na UI

## 🐛 Troubleshooting

### Erro: "GOOGLE_API_KEY não configurada"

**Solução**:
1. Verifique se o arquivo `.env` existe
2. Confirme que contém `GOOGLE_API_KEY=sua-chave-aqui`
3. A chave não pode começar com `your-` (placeholder)

### Erro: "Port 8501 is already in use"

**Solução**:
```bash
# Encontre e mate o processo usando a porta
lsof -ti:8501 | xargs kill -9

# Ou use outra porta
streamlit run app.py --server.port 8502
```

### Erro: "Rate limit exceeded"

**Solução**:
- Você excedeu o limite gratuito da API
- Aguarde alguns minutos antes de tentar novamente
- Considere upgrade para um plano pago

### Dashboard não atualiza automaticamente

**Solução**:
- Pressione `R` para recarregar
- Limpe o cache do Streamlit: pressione `C` no dashboard
- Reinicie o servidor Streamlit

### Gráficos não aparecem

**Solução**:
- Certifique-se de que enviou pelo menos 1 mensagem
- Verifique se o Plotly foi instalado: `pip install plotly`
- Atualize o navegador (Ctrl+F5)

## 🎓 Para Instrutores

### Sugestões de Atividades

1. **Análise Comparativa**: Peça aos alunos para comparar consumo entre modelos
2. **Otimização de Prompts**: Desafie a obter a mesma resposta com menos tokens
3. **Cálculo de Custos**: Simule um chatbot com 1000 usuários/dia e calcule custos mensais
4. **Estratégias de Compressão**: Discuta técnicas para reduzir o tamanho da janela de contexto

### Pontos de Discussão

- Por que o histórico completo é enviado a cada mensagem?
- Como implementar "esquecimento" de mensagens antigas?
- Qual a diferença entre janela de contexto e memória de longo prazo?
- Como balancear custo vs qualidade de resposta?

## 📈 Próximas Melhorias

- [ ] Exportação de histórico (CSV/JSON)
- [ ] Comparação lado-a-lado de modelos
- [ ] Alertas sonoros quando limite atingido
- [ ] Integração com Claude e GPT
- [ ] Modo "demo" com conversas pré-programadas
- [ ] Análise de sentimento das mensagens
- [ ] Gráfico de velocidade de resposta (latência)

## 📝 Licença

Este projeto faz parte do material didático da disciplina de **AIOps e Inteligência Artificial com Engenharia Cloud**.

## 🤝 Contribuições

Sugestões e melhorias são bem-vindas! Abra uma issue ou pull request no repositório.

---

**Desenvolvido para fins educacionais** | Disciplina de Pós-Graduação em AIOps
