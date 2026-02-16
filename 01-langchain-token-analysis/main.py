import os
import streamlit as st
import plotly.graph_objects as go
from dotenv import load_dotenv
from prompts import PromptManager
from llms import LLMFactory, execute_prompt, TokenResult
from typing import List

load_dotenv()

ANTHROPIC_MODELS = ["claude-sonnet-4-5-20250929", "claude-haiku-4-5-20251001"]
GOOGLE_MODELS = ["gemini-3-pro-preview", "gemini-3-flash-preview"]

LANG_LABELS = {"pt": "Português", "en": "Inglês"}


def run_models(provider: str, models: List[str], languages: List[str],
               prompt_manager: PromptManager, factory_method) -> List[TokenResult]:
    results = []
    for model_name in models:
        model = factory_method(model_name)
        for lang in languages:
            for prompt in prompt_manager.get_prompts(lang):
                result = execute_prompt(model, prompt.text, provider, model_name, lang, prompt.id)
                if result:
                    results.append(result)
    return results


def build_comparison_chart(results: List[TokenResult]) -> go.Figure:
    models = []
    input_tokens = []
    output_tokens = []
    for r in results:
        label = f"{r.model} ({LANG_LABELS[r.language]})"
        models.append(label)
        input_tokens.append(r.input_tokens)
        output_tokens.append(r.output_tokens)

    fig = go.Figure(data=[
        go.Bar(name="Input Tokens", x=models, y=input_tokens, marker_color="#636EFA"),
        go.Bar(name="Output Tokens", x=models, y=output_tokens, marker_color="#EF553B"),
    ])
    fig.update_layout(
        barmode="group",
        title="Comparação de Tokens por Modelo e Idioma",
        xaxis_title="Modelo",
        yaxis_title="Tokens",
        xaxis_tickangle=-30,
    )
    return fig


def calculate_language_diff(results: List[TokenResult], provider: str) -> float:
    pt_totals = [r.total_tokens for r in results if r.provider == provider and r.language == "pt"]
    en_totals = [r.total_tokens for r in results if r.provider == provider and r.language == "en"]
    if not pt_totals or not en_totals:
        return 0.0
    pt_avg = sum(pt_totals) / len(pt_totals)
    en_avg = sum(en_totals) / len(en_totals)
    if en_avg == 0:
        return 0.0
    return ((pt_avg - en_avg) / en_avg) * 100


def main():
    st.set_page_config(page_title="Análise de Tokens - LangChain", layout="wide")
    st.title("Análise de Tokens com LangChain")

    # --- Sidebar ---
    st.sidebar.header("Configuração")

    providers = st.sidebar.multiselect(
        "Providers",
        ["Anthropic", "Google"],
        default=["Anthropic", "Google"],
    )

    selected_anthropic = []
    selected_google = []

    if "Anthropic" in providers:
        selected_anthropic = st.sidebar.multiselect(
            "Modelos Anthropic",
            ANTHROPIC_MODELS,
            default=ANTHROPIC_MODELS,
        )

    if "Google" in providers:
        selected_google = st.sidebar.multiselect(
            "Modelos Google",
            GOOGLE_MODELS,
            default=GOOGLE_MODELS,
        )

    languages = st.sidebar.multiselect(
        "Idiomas",
        ["pt", "en"],
        default=["pt", "en"],
        format_func=lambda x: LANG_LABELS[x],
    )

    run_button = st.sidebar.button("Executar Análise", type="primary", use_container_width=True)

    # --- Validações ---
    if run_button:
        errors = []
        if "Anthropic" in providers and not os.getenv("ANTHROPIC_API_KEY"):
            errors.append("ANTHROPIC_API_KEY não configurada no .env")
        if "Google" in providers and not os.getenv("GOOGLE_API_KEY"):
            errors.append("GOOGLE_API_KEY não configurada no .env")
        if not providers:
            errors.append("Selecione ao menos um provider")
        if not languages:
            errors.append("Selecione ao menos um idioma")
        if "Anthropic" in providers and not selected_anthropic:
            errors.append("Selecione ao menos um modelo Anthropic")
        if "Google" in providers and not selected_google:
            errors.append("Selecione ao menos um modelo Google")

        if errors:
            for e in errors:
                st.error(e)
        else:
            prompt_manager = PromptManager()
            results: List[TokenResult] = []

            with st.spinner("Executando modelos..."):
                if "Anthropic" in providers and selected_anthropic:
                    results.extend(run_models(
                        "Anthropic", selected_anthropic, languages,
                        prompt_manager, LLMFactory.create_anthropic_model,
                    ))
                if "Google" in providers and selected_google:
                    results.extend(run_models(
                        "Google", selected_google, languages,
                        prompt_manager, LLMFactory.create_google_model,
                    ))

            st.session_state["results"] = results

    # --- Resultados ---
    results = st.session_state.get("results")
    if not results:
        st.info("Configure os parâmetros na barra lateral e clique em **Executar Análise**.")
        return

    # Métricas resumo
    total_tokens = sum(r.total_tokens for r in results)
    models_tested = len({r.model for r in results})
    col1, col2, col3 = st.columns(3)
    col1.metric("Total de Tokens", f"{total_tokens:,}")
    col2.metric("Modelos Testados", models_tested)
    col3.metric("Execuções", len(results))

    st.divider()

    # Tabela comparativa
    st.subheader("Comparação por Modelo e Idioma")
    table_data = []
    for r in results:
        table_data.append({
            "Provider": r.provider,
            "Modelo": r.model,
            "Idioma": LANG_LABELS[r.language],
            "Input Tokens": r.input_tokens,
            "Output Tokens": r.output_tokens,
            "Total Tokens": r.total_tokens,
        })
    st.dataframe(table_data, use_container_width=True)

    # Gráfico
    st.subheader("Gráfico Comparativo")
    fig = build_comparison_chart(results)
    st.plotly_chart(fig, use_container_width=True)

    # Comparação de idiomas
    providers_in_results = sorted({r.provider for r in results})
    langs_in_results = {r.language for r in results}

    if "pt" in langs_in_results and "en" in langs_in_results:
        st.subheader("Comparação entre Idiomas")
        cols = st.columns(len(providers_in_results))
        for col, provider in zip(cols, providers_in_results):
            diff = calculate_language_diff(results, provider)
            direction = "mais" if diff > 0 else "menos"
            col.metric(
                provider,
                f"{abs(diff):.1f}%",
                delta=f"PT usa {abs(diff):.1f}% {direction} tokens que EN",
                delta_color="inverse" if diff > 0 else "normal",
            )

    # Respostas completas
    st.subheader("Respostas Completas")
    for r in results:
        label = f"{r.provider} / {r.model} — {LANG_LABELS[r.language]}"
        with st.expander(label):
            st.markdown(r.response_text)


if __name__ == "__main__":
    main()
