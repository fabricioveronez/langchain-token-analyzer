# 03 - Explorador de Parâmetros de Sampling (Temperature, Top-K, Top-P)

Dashboard interativo em Streamlit para explorar como os parâmetros de sampling afetam a geração de texto de um LLM (Gemini 3 Pro).

## Objetivos de Aprendizado

- Entender o papel de **temperature**, **top_k** e **top_p** na geração de texto
- Observar na prática como cada parâmetro altera o comportamento do modelo
- Perceber a variabilidade das respostas executando o mesmo prompt múltiplas vezes

## Conceitos

### Temperature

Controla a aleatoriedade da distribuição de probabilidade dos tokens. Valores baixos (ex: 0.1) tornam o modelo mais determinístico — ele tende a sempre escolher os tokens mais prováveis. Valores altos (ex: 1.5+) aumentam a criatividade e imprevisibilidade.

### Top-P (Nucleus Sampling)

Define um limiar de probabilidade acumulada. O modelo considera apenas o menor conjunto de tokens cuja soma de probabilidades atinge o valor de `top_p`. Com `top_p=0.1`, apenas os tokens que representam os 10% de maior probabilidade são candidatos.

### Top-K

Limita a seleção aos K tokens mais prováveis a cada passo de geração. Com `top_k=1`, o modelo sempre escolhe o token mais provável (greedy decoding). Valores maiores permitem mais diversidade nas respostas.

## Requisitos

- Python 3.8+
- Chave de API do Google (Gemini)

## Como Executar

1. Configure a variável de ambiente `GOOGLE_API_KEY` no arquivo `.env` na raiz do repositório:

```
GOOGLE_API_KEY=sua-chave-aqui
```

2. Instale as dependências:

```bash
pip install -r requirements.txt
```

3. Execute o dashboard:

```bash
streamlit run main.py
```

## Estrutura de Arquivos

```
03-temperature-topk-topp/
├── README.md              # Este arquivo
├── requirements.txt       # Dependências Python
└── main.py                # Código completo do dashboard
```

## Experimentos Sugeridos

1. **Temperature baixa vs alta**: Execute o mesmo prompt com temperature=0.1 e depois com temperature=2.0. Compare as respostas.
2. **Top-K restritivo**: Use top_k=1 (greedy) e observe que as respostas ficam praticamente idênticas entre execuções.
3. **Variabilidade**: Com temperature=1.0, execute o mesmo prompt 5 vezes e note as diferenças entre cada resposta.
4. **Top-P baixo**: Use top_p=0.1 com temperature=1.0 e veja como o modelo fica mais focado mesmo com temperature alta.
