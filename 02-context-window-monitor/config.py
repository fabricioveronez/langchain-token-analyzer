"""
Configurações e validação de ambiente.
"""
import os
from dotenv import load_dotenv

# Carregar .env
load_dotenv()

# Modelos disponíveis
AVAILABLE_MODELS = [
    'gemini-3-flash-preview',
    'gemini-3-pro-preview'
]

# Preços (USD por 1M tokens)
PRICING = {
    'gemini-3-flash-preview': {'input': 0.10, 'output': 0.30},
    'gemini-3-pro-preview': {'input': 0.50, 'output': 1.50}
}


def validate_environment() -> bool:
    """
    Valida se a API key do Google está configurada.

    Returns:
        bool: True se a API key está válida, False caso contrário
    """
    google_key = os.getenv('GOOGLE_API_KEY')

    if not google_key:
        return False

    if google_key.startswith('your-'):
        return False

    return True


def calculate_cost(input_tokens: int, output_tokens: int, model: str) -> float:
    """
    Calcula o custo estimado baseado no uso de tokens.

    Args:
        input_tokens: Número de tokens de entrada
        output_tokens: Número de tokens de saída
        model: Nome do modelo usado

    Returns:
        float: Custo estimado em USD
    """
    if model not in PRICING:
        # Usar média se modelo não encontrado
        return ((input_tokens + output_tokens) / 1_000_000) * 0.20

    prices = PRICING[model]
    input_cost = (input_tokens / 1_000_000) * prices['input']
    output_cost = (output_tokens / 1_000_000) * prices['output']

    return input_cost + output_cost
