import os

import streamlit as st
from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI

load_dotenv()

SUGGESTED_PROMPTS = [
    "Escreva sua própria pergunta...",
    "Escreva um parágrafo sobre inteligência artificial",
    "Crie uma história curta sobre um robô que aprende a cozinhar",
    "Explique computação quântica para uma criança de 10 anos",
    "Dê 5 nomes criativos para uma startup de tecnologia",
    "Escreva um haiku sobre programação",
]


def validate_environment():
    """Valida se a API key do Google está configurada."""
    google_key = os.getenv("GOOGLE_API_KEY")

    if not google_key:
        return False

    if google_key.startswith("your-"):
        return False

    return True


def create_model(temperature, top_k, top_p):
    """Cria instância do modelo Gemini com os parâmetros de sampling."""
    api_key = os.getenv("GOOGLE_API_KEY")
    return ChatGoogleGenerativeAI(
        model="gemini-3-pro-preview",
        google_api_key=api_key,
        temperature=temperature,
        top_k=top_k,
        top_p=top_p,
    )


def main():
    st.set_page_config(
        page_title="Explorador de Parâmetros de Sampling",
        page_icon="🎛️",
        layout="wide",
    )

    st.title("Explorador de Parâmetros de Sampling")
    st.markdown(
        "Ajuste **temperature**, **top_k** e **top_p** e observe como cada "
        "configuração afeta a geração de texto do modelo."
    )

    if not validate_environment():
        st.error(
            "**GOOGLE_API_KEY** não configurada. "
            "Crie um arquivo `.env` na raiz do repositório com sua chave: "
            "`GOOGLE_API_KEY=sua-chave-aqui`"
        )
        st.stop()

    # --- Sidebar ---
    with st.sidebar:
        st.header("Parâmetros de Sampling")

        temperature = st.slider(
            "Temperature", min_value=0.0, max_value=2.0, value=1.0, step=0.1
        )
        with st.expander("O que é Temperature?"):
            st.markdown(
                "Controla a **aleatoriedade** da geração. Valores baixos (ex: 0.1) "
                "tornam o modelo mais determinístico e focado. Valores altos (ex: 1.5+) "
                "tornam as respostas mais criativas e imprevisíveis."
            )

        top_p = st.slider(
            "Top-P (nucleus sampling)", min_value=0.0, max_value=1.0, value=0.95, step=0.05
        )
        with st.expander("O que é Top-P?"):
            st.markdown(
                "Considera apenas os tokens cuja probabilidade acumulada atinge **P**. "
                "Com top_p=0.1, apenas os tokens mais prováveis que somam 10% de "
                "probabilidade são considerados. Valores menores = respostas mais focadas."
            )

        top_k = st.slider(
            "Top-K", min_value=1, max_value=100, value=40, step=1
        )
        with st.expander("O que é Top-K?"):
            st.markdown(
                "Limita a seleção aos **K tokens mais prováveis** a cada passo. "
                "Com top_k=1 o modelo sempre escolhe o token mais provável (greedy). "
                "Valores maiores permitem mais diversidade."
            )

        st.divider()

        num_executions = st.slider(
            "Número de execuções", min_value=1, max_value=5, value=1, step=1,
            help="Execute o mesmo prompt várias vezes para observar a variabilidade das respostas.",
        )

        st.divider()

        st.subheader("Prompts sugeridos")
        selected_prompt = st.selectbox(
            "Escolha um prompt sugerido:",
            SUGGESTED_PROMPTS,
            label_visibility="collapsed",
        )

    # --- Área principal ---
    prompt = st.text_area(
        "Digite seu prompt:",
        value=selected_prompt if selected_prompt != SUGGESTED_PROMPTS[0] else "",
        height=100,
    )

    if st.button("Executar", type="primary"):
        if not prompt.strip():
            st.warning("Digite um prompt antes de executar.")
            return

        model = create_model(temperature, top_k, top_p)

        st.markdown(
            f"**Parâmetros:** temperature=`{temperature}` | top_p=`{top_p}` | top_k=`{top_k}`"
        )

        for i in range(num_executions):
            if num_executions > 1:
                st.subheader(f"Execução {i + 1}")

            with st.spinner("Gerando resposta..."):
                try:
                    response = model.invoke(prompt)
                    content = response.content
                    if isinstance(content, list):
                        content = "\n".join(
                            block.get("text", "") if isinstance(block, dict) else str(block)
                            for block in content
                        )
                    st.markdown(content)
                except Exception as e:
                    st.error(f"Erro ao gerar resposta: {e}")

            if num_executions > 1 and i < num_executions - 1:
                st.divider()


if __name__ == "__main__":
    main()
