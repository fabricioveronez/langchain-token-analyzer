import os
from typing import Optional
from langchain_anthropic import ChatAnthropic
from langchain_google_genai import ChatGoogleGenerativeAI
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
    try:
        # Invoke sem callbacks - usage_metadata vem automaticamente
        result = model.invoke(prompt_text)

        # usage_metadata já vem no AIMessage automaticamente
        # Estrutura: {'input_tokens': 8, 'output_tokens': 21, 'total_tokens': 29, ...}
        usage = result.usage_metadata if hasattr(result, 'usage_metadata') and result.usage_metadata else {}

        return TokenResult(
            provider=provider,
            model=model_name,
            language=language,
            prompt_id=prompt_id,
            input_tokens=usage.get('input_tokens', 0),
            output_tokens=usage.get('output_tokens', 0),
            response_text=result.content
        )
    except Exception as e:
        print(f"Erro ao executar {provider} {model_name} ({language}): {str(e)}")
        return None
