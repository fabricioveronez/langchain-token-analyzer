"""
Gerenciamento de conversação com LangChain e captura de métricas.
"""
import os
from datetime import datetime
from typing import List, Dict
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from metrics import MessageMetrics


class ChatManager:
    """Gerencia conversação com LangChain e captura métricas de tokens"""

    def __init__(self, model_name: str):
        """
        Inicializa o gerenciador de chat.

        Args:
            model_name: Nome do modelo Gemini a ser usado
        """
        self.model_name = model_name
        self.model = self._create_gemini_model(model_name)
        self.history: List[MessageMetrics] = []
        self.cumulative_tokens = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0

    def _create_gemini_model(self, model_name: str) -> ChatGoogleGenerativeAI:
        """
        Cria instância do modelo Gemini usando LangChain.

        Args:
            model_name: Nome do modelo

        Returns:
            ChatGoogleGenerativeAI: Instância configurada do modelo
        """
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=os.getenv('GOOGLE_API_KEY'),
            temperature=0.7
        )

    def _create_user_metrics(self, message: str) -> MessageMetrics:
        """
        Cria métricas para uma mensagem do usuário.

        Args:
            message: Conteúdo da mensagem

        Returns:
            MessageMetrics: Métricas da mensagem do usuário
        """
        # Mensagens do usuário não têm tokens de saída
        tokens = len(message.split())  # Estimativa simples

        return MessageMetrics(
            role='user',
            content=message,
            input_tokens=tokens,
            output_tokens=0,
            total_tokens=tokens,
            cumulative_tokens=self.cumulative_tokens + tokens,
            timestamp=datetime.now()
        )

    def _build_message_history(self) -> List:
        """
        Constrói histórico de mensagens no formato LangChain.

        Returns:
            List: Lista de mensagens LangChain
        """
        messages = []
        for msg in self.history:
            if msg.role == 'user':
                messages.append(HumanMessage(content=msg.content))
            elif msg.role == 'assistant':
                messages.append(AIMessage(content=msg.content))

        return messages

    def send_message(self, user_message: str) -> MessageMetrics:
        """
        Envia mensagem ao modelo e captura métricas usando usage_metadata.

        Args:
            user_message: Mensagem do usuário

        Returns:
            MessageMetrics: Métricas da resposta do assistente
        """
        # 1. Criar métricas da mensagem do usuário
        user_metrics = self._create_user_metrics(user_message)
        self.cumulative_tokens += user_metrics.total_tokens
        self.history.append(user_metrics)

        # 2. Construir histórico completo e invocar modelo
        messages = self._build_message_history()
        result = self.model.invoke(messages)

        # 3. Extrair métricas da resposta (LangChain 1.x)
        usage = result.usage_metadata

        assistant_metrics = MessageMetrics(
            role='assistant',
            content=result.content,
            input_tokens=usage['input_tokens'],
            output_tokens=usage['output_tokens'],
            total_tokens=usage['total_tokens'],
            cumulative_tokens=self.cumulative_tokens + usage['total_tokens'],
            timestamp=datetime.now()
        )

        # 4. Atualizar totais
        self.cumulative_tokens += usage['total_tokens']
        self.total_input_tokens += usage['input_tokens']
        self.total_output_tokens += usage['output_tokens']
        self.history.append(assistant_metrics)

        return assistant_metrics

    def get_statistics(self) -> Dict:
        """
        Calcula estatísticas agregadas da conversação.

        Returns:
            Dict: Estatísticas da conversa
        """
        user_messages = [m for m in self.history if m.role == 'user']
        assistant_messages = [m for m in self.history if m.role == 'assistant']

        return {
            'total_messages': len(self.history),
            'total_tokens': self.cumulative_tokens,
            'total_input_tokens': self.total_input_tokens,
            'total_output_tokens': self.total_output_tokens,
            'avg_tokens_per_message': self.cumulative_tokens / max(len(self.history), 1),
            'user_messages': len(user_messages),
            'assistant_messages': len(assistant_messages),
            'model_name': self.model_name
        }

    def clear_history(self):
        """Limpa o histórico de conversação e reseta contadores"""
        self.history = []
        self.cumulative_tokens = 0
        self.total_input_tokens = 0
        self.total_output_tokens = 0
