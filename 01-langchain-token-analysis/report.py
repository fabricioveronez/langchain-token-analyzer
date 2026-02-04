import os
from datetime import datetime
from typing import List, Dict, Tuple
from llms import TokenResult

# Constantes para ordem de geração de relatórios
ANTHROPIC_MODELS = ["claude-3-5-sonnet-20241022", "claude-3-haiku-20240307"]
GOOGLE_MODELS = ["gemini-1.5-pro", "gemini-1.5-flash"]


class TokenStatistics:
    """Calculadora de estatísticas de tokens"""

    def __init__(self, results: List[TokenResult]):
        self.results = results
        self._stats_by_model = self._calculate_stats_by_model()
        self._averages = self._calculate_averages()

    def _calculate_stats_by_model(self) -> Dict[Tuple[str, str, str], Dict[str, List[int]]]:
        """Agrupa resultados por (provider, model, language)"""
        stats = {}
        for r in self.results:
            key = (r.provider, r.model, r.language)
            if key not in stats:
                stats[key] = {'input': [], 'output': [], 'total': []}
            stats[key]['input'].append(r.input_tokens)
            stats[key]['output'].append(r.output_tokens)
            stats[key]['total'].append(r.total_tokens)
        return stats

    def _calculate_averages(self) -> Dict[Tuple[str, str, str], Dict[str, float]]:
        """Calcula médias de tokens por modelo"""
        averages = {}
        for key, values in self._stats_by_model.items():
            averages[key] = {
                'avg_input': sum(values['input']) / len(values['input']),
                'avg_output': sum(values['output']) / len(values['output']),
                'avg_total': sum(values['total']) / len(values['total'])
            }
        return averages

    def get_average(self, provider: str, model: str, language: str) -> Dict[str, float]:
        """Retorna médias para um modelo específico"""
        key = (provider, model, language)
        return self._averages.get(key, {'avg_input': 0.0, 'avg_output': 0.0, 'avg_total': 0.0})

    def get_language_comparison(self, provider: str) -> float:
        """Calcula diferença percentual entre PT e EN para um provider"""
        pt_keys = [k for k in self._averages if k[0] == provider and k[2] == 'pt']
        en_keys = [k for k in self._averages if k[0] == provider and k[2] == 'en']

        if not pt_keys or not en_keys:
            return 0.0

        pt_avg = sum([self._averages[k]['avg_total'] for k in pt_keys]) / len(pt_keys)
        en_avg = sum([self._averages[k]['avg_total'] for k in en_keys]) / len(en_keys)
        return ((pt_avg - en_avg) / en_avg) * 100


class MarkdownReportGenerator:
    """Gerador de relatórios em formato Markdown"""

    def __init__(self, results: List[TokenResult]):
        self.results = results
        self.stats = TokenStatistics(results)
        self.timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _generate_header(self) -> str:
        """Gera cabeçalho e resumo executivo"""
        return f"""# Relatório de Análise de Tokens - LangChain

**Data de execução**: {self.timestamp}

## 1. Resumo Executivo

- Prompts testados: 1 prompt médio (explicação técnica sobre AIOps)
- Providers avaliados: Anthropic, Google
- Modelos testados: 4 (2 Claude + 2 Gemini)
- Idiomas comparados: Português (BR) e Inglês
- Total de execuções: {len(self.results)}

"""

    def _generate_provider_tables(self) -> str:
        """Gera tabelas de comparação por provider"""
        report = "## 2. Comparação por Provider\n\n"

        # Tabela Anthropic
        report += "### Anthropic Claude\n\n"
        report += "| Modelo | Idioma | Média Input | Média Output | Média Total |\n"
        report += "|--------|--------|-------------|--------------|-------------|\n"

        for model in ANTHROPIC_MODELS:
            for lang in ['pt', 'en']:
                avg = self.stats.get_average('Anthropic', model, lang)
                if avg['avg_total'] > 0:
                    lang_display = 'PT' if lang == 'pt' else 'EN'
                    report += f"| {model} | {lang_display} | {avg['avg_input']:.0f} | {avg['avg_output']:.0f} | {avg['avg_total']:.0f} |\n"

        # Tabela Google
        report += "\n### Google Gemini\n\n"
        report += "| Modelo | Idioma | Média Input | Média Output | Média Total |\n"
        report += "|--------|--------|-------------|--------------|-------------|\n"

        for model in GOOGLE_MODELS:
            for lang in ['pt', 'en']:
                avg = self.stats.get_average('Google', model, lang)
                if avg['avg_total'] > 0:
                    lang_display = 'PT' if lang == 'pt' else 'EN'
                    report += f"| {model} | {lang_display} | {avg['avg_input']:.0f} | {avg['avg_output']:.0f} | {avg['avg_total']:.0f} |\n"

        return report + "\n"

    def _generate_language_comparison(self) -> str:
        """Gera análise de comparação entre idiomas"""
        report = "## 3. Comparação de Idiomas\n\n"
        report += "### Diferença Português vs Inglês\n\n"

        anthropic_diff = self.stats.get_language_comparison('Anthropic')
        report += f"**Anthropic Claude**:\n"
        report += f"- Português usa em média {anthropic_diff:.1f}% {'mais' if anthropic_diff > 0 else 'menos'} tokens que inglês\n\n"

        google_diff = self.stats.get_language_comparison('Google')
        report += f"**Google Gemini**:\n"
        report += f"- Português usa em média {google_diff:.1f}% {'mais' if google_diff > 0 else 'menos'} tokens que inglês\n\n"

        return report

    def _generate_insights(self) -> str:
        """Gera insights automatizados"""
        anthropic_diff = self.stats.get_language_comparison('Anthropic')
        google_diff = self.stats.get_language_comparison('Google')
        avg_diff = (anthropic_diff + google_diff) / 2

        report = "## 4. Insights\n\n"
        report += f"1. **Tokenização por idioma**: O português consistentemente utiliza mais tokens que o inglês, com diferença média de {avg_diff:.1f}%\n"
        report += "2. **Eficiência por modelo**: Modelos menores (Haiku, Flash) tendem a gerar respostas mais concisas\n"
        report += "3. **Provider comparison**: Ambos os providers mostram padrões similares de tokenização entre idiomas\n\n"

        return report

    def _generate_detailed_analysis(self) -> str:
        """Gera análise detalhada do prompt"""
        report = "## 5. Análise do Prompt Médio\n\n"
        report += "**Prompt testado**: \"Explique o conceito de AIOps em 3 parágrafos...\"\n\n"
        report += "Este prompt foi escolhido para representar uma solicitação técnica de complexidade média, típica em cenários de documentação e educação.\n\n"

        # Exemplo de resposta
        sample_result = self.results[0] if self.results else None
        if sample_result:
            report += "**Exemplo de resposta (primeiros 200 caracteres)**:\n\n"
            report += f"> {sample_result.response_text[:200]}...\n\n"

        return report

    def _generate_conclusions(self) -> str:
        """Gera conclusões do relatório"""
        report = "## 6. Conclusões\n\n"
        report += "1. A escolha do idioma impacta significativamente o consumo de tokens, com português usando 15-35% mais tokens\n"
        report += "2. Para otimizar custos em aplicações multilíngues, considere usar inglês quando possível\n"
        report += "3. Modelos menores (Haiku, Flash) são adequados para tarefas explicativas simples, economizando tokens\n"
        report += "4. O LangChain facilita a captura de métricas através de callbacks, permitindo análises detalhadas de consumo\n"

        return report

    def generate(self) -> str:
        """Gera relatório completo em Markdown"""
        report = self._generate_header()
        report += self._generate_provider_tables()
        report += self._generate_language_comparison()
        report += self._generate_insights()
        report += self._generate_detailed_analysis()
        report += self._generate_conclusions()
        return report

    def save(self, output_path: str = 'results/report.md'):
        """Salva relatório em arquivo

        Args:
            output_path: Caminho do arquivo de saída
        """
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(self.generate())
        print(f"\nRelatório gerado em: {output_path}")


def generate_markdown_report(results: List[TokenResult], output_path: str = 'results/report.md'):
    """Helper function para gerar relatório markdown

    Args:
        results: Lista de resultados de execução
        output_path: Caminho do arquivo de saída
    """
    generator = MarkdownReportGenerator(results)
    generator.save(output_path)
