import os
from dotenv import load_dotenv
from prompts import PromptManager
from llms import LLMFactory, execute_prompt, TokenResult
from report import generate_markdown_report
from typing import List

load_dotenv()

ANTHROPIC_MODELS = ["claude-sonnet-4-5-20250929", "claude-haiku-4-5-20251001"]
GOOGLE_MODELS = ["gemini-3-pro-preview", "gemini-3-flash-preview"]


def validate_environment() -> bool:
    """Valida se as API keys estão configuradas

    Returns:
        True se ambiente está válido, False caso contrário
    """
    if not os.getenv('ANTHROPIC_API_KEY'):
        print("ERRO: ANTHROPIC_API_KEY não configurada no .env")
        return False
    if not os.getenv('GOOGLE_API_KEY'):
        print("ERRO: GOOGLE_API_KEY não configurada no .env")
        return False
    return True


def test_anthropic_models(prompt_manager: PromptManager) -> List[TokenResult]:
    """Executa testes com modelos Anthropic

    Args:
        prompt_manager: Gerenciador de prompts

    Returns:
        Lista de resultados de execução
    """
    results = []
    print("\n--- Testando modelos Anthropic ---")

    for model_name in ANTHROPIC_MODELS:
        print(f"\nModelo: {model_name}")
        model = LLMFactory.create_anthropic_model(model_name)

        for lang in ['pt', 'en']:
            print(f"  - Executando em {'português' if lang == 'pt' else 'inglês'}...")
            for prompt in prompt_manager.get_prompts(lang):
                result = execute_prompt(model, prompt.text, 'Anthropic', model_name, lang, prompt.id)
                if result:
                    results.append(result)
                    print(f"    ✓ Input: {result.input_tokens}, Output: {result.output_tokens}, Total: {result.total_tokens}")

    return results


def test_google_models(prompt_manager: PromptManager) -> List[TokenResult]:
    """Executa testes com modelos Google

    Args:
        prompt_manager: Gerenciador de prompts

    Returns:
        Lista de resultados de execução
    """
    results = []
    print("\n--- Testando modelos Google ---")

    for model_name in GOOGLE_MODELS:
        print(f"\nModelo: {model_name}")
        model = LLMFactory.create_google_model(model_name)

        for lang in ['pt', 'en']:
            print(f"  - Executando em {'português' if lang == 'pt' else 'inglês'}...")
            for prompt in prompt_manager.get_prompts(lang):
                result = execute_prompt(model, prompt.text, 'Google', model_name, lang, prompt.id)
                if result:
                    results.append(result)
                    print(f"    ✓ Input: {result.input_tokens}, Output: {result.output_tokens}, Total: {result.total_tokens}")

    return results


def main():
    """Função principal de orquestração"""
    print("=== Análise de Tokens com LangChain ===\n")

    if not validate_environment():
        return

    print("Carregando prompts...")
    prompt_manager = PromptManager()

    results = []
    results.extend(test_anthropic_models(prompt_manager))
    results.extend(test_google_models(prompt_manager))

    print("\n--- Gerando relatório ---")
    generate_markdown_report(results)

    print("\n✅ Análise concluída com sucesso!")


if __name__ == "__main__":
    main()
