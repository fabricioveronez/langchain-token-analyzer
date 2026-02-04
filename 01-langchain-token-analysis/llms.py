import os
from typing import Any, Optional
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.callbacks import BaseCallbackHandler
from dataclasses import dataclass


@dataclass
class TokenResult:
    """Resultado da execução de um prompt com métricas de tokens"""
    provider: str
    model: str
    language: str
    prompt_id: str
    input_tokens: int
    output_tokens: int
    response_text: str

    @property
    def total_tokens(self) -> int:
        """Retorna total de tokens (input + output)"""
        return self.input_tokens + self.output_tokens


class TokenCounterCallback(BaseCallbackHandler):
    """Callback customizado para capturar métricas de tokens"""

    def __init__(self):
        self.input_tokens = 0
        self.output_tokens = 0

    def on_llm_end(self, response, **kwargs: Any) -> None:
        """Captura tokens quando a LLM termina a execução"""
        # Formato Anthropic (llm_output)
        if hasattr(response, 'llm_output') and response.llm_output:
            usage = response.llm_output.get('token_usage', {})
            self.input_tokens = usage.get('prompt_tokens', 0)
            self.output_tokens = usage.get('completion_tokens', 0)

        # Formato Google (usage_metadata)
        for generation in response.generations:
            if generation and len(generation) > 0:
                msg = generation[0].message
                if hasattr(msg, 'usage_metadata') and msg.usage_metadata:
                    self.input_tokens = msg.usage_metadata.get('input_tokens', 0)
                    self.output_tokens = msg.usage_metadata.get('output_tokens', 0)


class LLMFactory:
    """Factory para criação de modelos LLM"""

    @staticmethod
    def create_anthropic_model(model_name: str) -> ChatAnthropic:
        """Cria instância de modelo Anthropic Claude

        Args:
            model_name: Nome do modelo Claude

        Returns:
            Instância configurada do ChatAnthropic

        Raises:
            ValueError: Se ANTHROPIC_API_KEY não estiver configurada
        """
        api_key = os.getenv('ANTHROPIC_API_KEY')
        if not api_key:
            raise ValueError("ANTHROPIC_API_KEY não configurada")
        return ChatAnthropic(model=model_name, api_key=api_key)

    @staticmethod
    def create_google_model(model_name: str) -> ChatGoogleGenerativeAI:
        """Cria instância de modelo Google Gemini

        Args:
            model_name: Nome do modelo Gemini

        Returns:
            Instância configurada do ChatGoogleGenerativeAI

        Raises:
            ValueError: Se GOOGLE_API_KEY não estiver configurada
        """
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY não configurada")
        return ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key)


def execute_prompt(
    model,
    prompt_text: str,
    provider: str,
    model_name: str,
    language: str,
    prompt_id: str
) -> Optional[TokenResult]:
    """Executa prompt e captura métricas de tokens

    Args:
        model: Instância do modelo LLM
        prompt_text: Texto do prompt a ser executado
        provider: Nome do provider (ex: 'Anthropic', 'Google')
        model_name: Nome do modelo
        language: Código do idioma ('pt' ou 'en')
        prompt_id: Identificador do prompt

    Returns:
        TokenResult com métricas capturadas ou None em caso de erro
    """
    callback = TokenCounterCallback()

    try:
        result = model.invoke(prompt_text, config={"callbacks": [callback]})

        return TokenResult(
            provider=provider,
            model=model_name,
            language=language,
            prompt_id=prompt_id,
            input_tokens=callback.input_tokens,
            output_tokens=callback.output_tokens,
            response_text=result.content
        )
    except Exception as e:
        print(f"Erro ao executar {provider} {model_name} ({language}): {str(e)}")
        return None
