"""
Componentes de visualização para análise de tokens.
"""
import pandas as pd
import plotly.graph_objects as go
from typing import List
from metrics import MessageMetrics


class ContextWindowVisualizer:
    """Gera visualizações do crescimento da janela de contexto"""

    @staticmethod
    def plot_cumulative_growth(history: List[MessageMetrics]) -> go.Figure:
        """
        Gráfico de linha: crescimento acumulado de tokens.

        Args:
            history: Lista de métricas de mensagens

        Returns:
            go.Figure: Gráfico Plotly
        """
        if not history:
            # Retornar gráfico vazio se não há dados
            fig = go.Figure()
            fig.update_layout(
                title='Crescimento da Janela de Contexto',
                xaxis_title='Número da Mensagem',
                yaxis_title='Tokens Acumulados'
            )
            return fig

        fig = go.Figure()

        # Adicionar linha de crescimento
        fig.add_trace(go.Scatter(
            x=[i + 1 for i in range(len(history))],
            y=[msg.cumulative_tokens for msg in history],
            mode='lines+markers',
            name='Tokens Acumulados',
            line=dict(color='#1f77b4', width=3),
            marker=dict(size=8),
            hovertemplate='<b>Mensagem %{x}</b><br>Tokens: %{y}<extra></extra>'
        ))

        fig.update_layout(
            title='Crescimento da Janela de Contexto',
            xaxis_title='Número da Mensagem',
            yaxis_title='Tokens Acumulados',
            hovermode='x unified',
            showlegend=False,
            height=400
        )

        return fig

    @staticmethod
    def plot_tokens_per_message(history: List[MessageMetrics]) -> go.Figure:
        """
        Gráfico de barras: tokens por mensagem (input vs output).

        Args:
            history: Lista de métricas de mensagens

        Returns:
            go.Figure: Gráfico Plotly
        """
        if not history:
            # Retornar gráfico vazio se não há dados
            fig = go.Figure()
            fig.update_layout(
                title='Tokens por Mensagem',
                xaxis_title='Mensagem',
                yaxis_title='Tokens'
            )
            return fig

        fig = go.Figure()

        # Separar mensagens por tipo
        user_indices = []
        user_tokens = []
        assistant_indices = []
        assistant_tokens = []

        for i, msg in enumerate(history):
            if msg.role == 'user':
                user_indices.append(i + 1)
                user_tokens.append(msg.total_tokens)
            else:
                assistant_indices.append(i + 1)
                assistant_tokens.append(msg.total_tokens)

        # Barras de usuário
        if user_indices:
            fig.add_trace(go.Bar(
                x=user_indices,
                y=user_tokens,
                name='Usuário',
                marker_color='#2ca02c',
                hovertemplate='<b>Mensagem %{x}</b><br>Tokens: %{y}<extra></extra>'
            ))

        # Barras de assistente
        if assistant_indices:
            fig.add_trace(go.Bar(
                x=assistant_indices,
                y=assistant_tokens,
                name='Assistente',
                marker_color='#ff7f0e',
                hovertemplate='<b>Mensagem %{x}</b><br>Tokens: %{y}<extra></extra>'
            ))

        fig.update_layout(
            title='Tokens por Mensagem',
            xaxis_title='Mensagem',
            yaxis_title='Tokens',
            barmode='group',
            height=400
        )

        return fig

    @staticmethod
    def create_metrics_table(history: List[MessageMetrics]) -> pd.DataFrame:
        """
        Tabela detalhada de todas as mensagens.

        Args:
            history: Lista de métricas de mensagens

        Returns:
            pd.DataFrame: DataFrame com histórico detalhado
        """
        if not history:
            return pd.DataFrame(columns=['ID', 'Tipo', 'Tokens', 'Acumulado', 'Timestamp', 'Preview'])

        data = []
        for i, msg in enumerate(history):
            # content já é string garantida pelo chat_manager
            preview = msg.content[:200] + '...' if len(msg.content) > 200 else msg.content

            data.append({
                'ID': i + 1,
                'Tipo': 'Usuário' if msg.role == 'user' else 'Assistente',
                'Tokens': msg.total_tokens,
                'Acumulado': msg.cumulative_tokens,
                'Timestamp': msg.timestamp.strftime('%H:%M:%S'),
                'Preview': preview
            })

        return pd.DataFrame(data)

    @staticmethod
    def plot_token_distribution(history: List[MessageMetrics]) -> go.Figure:
        """
        Gráfico de pizza: distribuição de tokens input vs output.

        Args:
            history: Lista de métricas de mensagens

        Returns:
            go.Figure: Gráfico Plotly
        """
        if not history:
            fig = go.Figure()
            fig.update_layout(title='Distribuição Input/Output')
            return fig

        total_input = sum(msg.input_tokens for msg in history)
        total_output = sum(msg.output_tokens for msg in history)

        fig = go.Figure(data=[go.Pie(
            labels=['Input', 'Output'],
            values=[total_input, total_output],
            marker_colors=['#2ca02c', '#ff7f0e'],
            hovertemplate='<b>%{label}</b><br>Tokens: %{value}<br>Percentual: %{percent}<extra></extra>'
        )])

        fig.update_layout(
            title='Distribuição Input/Output',
            height=400
        )

        return fig
