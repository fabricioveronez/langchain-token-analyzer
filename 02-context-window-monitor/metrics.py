"""
Dataclasses para métricas de mensagens e tokens.
"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class MessageMetrics:
    """Métricas de uma mensagem individual na conversa"""
    role: str  # 'user' ou 'assistant'
    content: str
    input_tokens: int
    output_tokens: int
    total_tokens: int
    cumulative_tokens: int  # Acumulado até este ponto
    timestamp: datetime
