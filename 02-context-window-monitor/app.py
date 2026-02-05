"""
Dashboard Streamlit para visualizar crescimento da janela de contexto.
"""
import streamlit as st
from chat_manager import ChatManager
from visualizations import ContextWindowVisualizer
from config import validate_environment, AVAILABLE_MODELS, calculate_cost


def main():
    """Aplicação principal do dashboard"""
    st.set_page_config(
        page_title="Monitor de Janela de Contexto",
        page_icon="📊",
        layout="wide"
    )

    # Validar ambiente
    if not validate_environment():
        st.error("❌ GOOGLE_API_KEY não configurada!")
        st.info("Configure sua API key no arquivo .env")
        st.info("Copie o arquivo .env.example para .env e adicione sua chave")
        st.stop()

    # Título
    st.title("📊 Monitor de Janela de Contexto - LangChain + Gemini")
    st.markdown(
        "**Objetivo**: Visualizar em tempo real como a janela de contexto cresce durante uma conversa"
    )

    # Inicializar estado
    if 'chat_manager' not in st.session_state:
        st.session_state.chat_manager = ChatManager('gemini-3-flash-preview')
        st.session_state.messages = []

    # Layout em 3 colunas
    col_config, col_chat, col_viz = st.columns([1, 2, 2])

    # === COLUNA 1: CONFIGURAÇÃO ===
    with col_config:
        st.subheader("⚙️ Configuração")

        # Seleção de modelo
        selected_model = st.selectbox(
            "Modelo Gemini",
            options=AVAILABLE_MODELS,
            index=0,
            help="Escolha o modelo Gemini para usar na conversa"
        )

        # Atualizar modelo se mudou
        if selected_model != st.session_state.chat_manager.model_name:
            st.session_state.chat_manager = ChatManager(selected_model)
            st.session_state.messages = []
            st.info(f"Modelo alterado para {selected_model}. Histórico limpo.")

        # Limite de alerta
        token_limit = st.slider(
            "Limite de Tokens (Alerta)",
            min_value=1000,
            max_value=100000,
            value=10000,
            step=1000,
            help="Defina um limite para receber alertas quando o uso se aproximar"
        )

        # Botão limpar
        if st.button("🗑️ Limpar Histórico", use_container_width=True):
            st.session_state.chat_manager.clear_history()
            st.session_state.messages = []
            st.rerun()

        st.divider()

        # Métricas em cards
        stats = st.session_state.chat_manager.get_statistics()

        st.metric("Total de Mensagens", stats['total_messages'])
        st.metric("Total de Tokens", f"{stats['total_tokens']:,}")
        st.metric("Média Tokens/Msg", f"{stats['avg_tokens_per_message']:.1f}")

        # Progress bar do limite
        if stats['total_tokens'] > 0:
            progress = min(stats['total_tokens'] / token_limit, 1.0)
            st.progress(progress, text=f"{progress*100:.1f}% do limite")

            if progress >= 0.8:
                st.warning(f"⚠️ {progress*100:.0f}% do limite atingido!")
            elif progress >= 1.0:
                st.error("🚨 Limite excedido!")

    # === COLUNA 2: CHAT ===
    with col_chat:
        st.subheader("💬 Conversa")

        # Container de mensagens com altura fixa
        chat_container = st.container(height=500)

        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg['role']):
                    # content já é string pura garantida pelo chat_manager
                    st.markdown(msg['content'])
                    st.caption(f"🔢 {msg['tokens']:,} tokens")

        # Input do usuário
        if user_input := st.chat_input("Digite sua mensagem..."):
            # Adicionar mensagem do usuário à interface
            st.session_state.messages.append({
                'role': 'user',
                'content': user_input,
                'tokens': len(user_input.split())  # Estimativa simples
            })

            # Enviar para o modelo e obter resposta
            with st.spinner("🤔 Gemini pensando..."):
                try:
                    response_metrics = st.session_state.chat_manager.send_message(user_input)

                    # Adicionar resposta do assistente à interface
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': response_metrics.content,
                        'tokens': response_metrics.total_tokens
                    })

                except Exception as e:
                    st.error(f"Erro ao processar mensagem: {str(e)}")
                    # Remover mensagem do usuário se falhou
                    st.session_state.messages.pop()

            st.rerun()

    # === COLUNA 3: VISUALIZAÇÕES ===
    with col_viz:
        st.subheader("📈 Análise de Tokens")

        history = st.session_state.chat_manager.history

        if len(history) > 0:
            # Tabs para organizar visualizações
            tab1, tab2, tab3 = st.tabs(["📈 Crescimento", "📊 Por Mensagem", "📋 Detalhes"])

            with tab1:
                # Gráfico de crescimento acumulado
                fig_growth = ContextWindowVisualizer.plot_cumulative_growth(history)
                st.plotly_chart(fig_growth, use_container_width=True)

            with tab2:
                # Gráfico de barras por mensagem
                fig_bars = ContextWindowVisualizer.plot_tokens_per_message(history)
                st.plotly_chart(fig_bars, use_container_width=True)

            with tab3:
                # Tabela detalhada
                df = ContextWindowVisualizer.create_metrics_table(history)
                st.dataframe(
                    df,
                    use_container_width=True,
                    height=400,
                    hide_index=True
                )

                # Estatísticas adicionais
                st.divider()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Mensagens do Usuário", stats['user_messages'])
                    st.metric("Input Tokens", f"{stats['total_input_tokens']:,}")
                with col2:
                    st.metric("Mensagens do Assistente", stats['assistant_messages'])
                    st.metric("Output Tokens", f"{stats['total_output_tokens']:,}")

        else:
            st.info("👋 Envie uma mensagem para começar a análise!")
            st.markdown("""
            **Como usar:**
            1. Digite uma mensagem no chat
            2. Observe os gráficos atualizarem em tempo real
            3. Experimente diferentes tipos de perguntas
            4. Compare o consumo de tokens entre mensagens curtas e longas
            """)

    # Rodapé com informações
    st.divider()
    st.caption(
        f"Projeto 02 - Monitor de Janela de Contexto | "
        f"Modelo: {stats['model_name']} | "
        f"Desenvolvido para disciplina de AIOps e IA com Engenharia Cloud"
    )


if __name__ == "__main__":
    main()
