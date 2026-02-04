from dataclasses import dataclass
from typing import List


@dataclass
class Prompt:
    """Representa um prompt com seus metadados"""
    id: str
    category: str
    text: str
    description: str


class PromptManager:
    """Gerenciador de prompts em múltiplos idiomas"""

    def __init__(self):
        self._prompts_pt = [
            Prompt(
                id="medium_1",
                category="medium",
                text="Explique o conceito de AIOps em 3 parágrafos, incluindo suas principais características e benefícios.",
                description="Explicação técnica média"
            )
        ]

        self._prompts_en = [
            Prompt(
                id="medium_1",
                category="medium",
                text="Explain the concept of AIOps in 3 paragraphs, including its main characteristics and benefits.",
                description="Medium technical explanation"
            )
        ]

    def get_prompts(self, language: str) -> List[Prompt]:
        """Retorna prompts para o idioma especificado

        Args:
            language: Código do idioma ('pt' ou 'en')

        Returns:
            Lista de prompts

        Raises:
            ValueError: Se o idioma não for suportado
        """
        if language == 'pt':
            return self._prompts_pt
        elif language == 'en':
            return self._prompts_en
        raise ValueError(f"Idioma não suportado: {language}")

    def get_supported_languages(self) -> List[str]:
        """Retorna lista de idiomas suportados"""
        return ['pt', 'en']
