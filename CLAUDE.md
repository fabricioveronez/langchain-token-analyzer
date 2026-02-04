# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Propósito do Repositório

Repositório de projetos de exemplo para disciplina de pós-graduação em **AIOps e Inteligência Artificial com Engenharia Cloud**. Cada projeto está em uma pasta numerada e inclui código completo + README explicativo.

## Estrutura

```
projetos-auxiliares/
├── README.md (índice principal)
├── 01-nome-projeto/
│   ├── README.md (explicação do projeto)
│   ├── código e arquivos necessários
│   └── ...
├── 02-nome-projeto/
│   └── ...
└── NN-nome-projeto/
```

## Convenções de Desenvolvimento

### Git
- Use **semantic commit** com mensagens de uma linha
- Exemplo: `feat: add monitoring dashboard for 01-project`
- **Nunca assine commits como agente de IA**

### Linguagem
- Documentação e comunicação em **português (Brasil)**
- Códigos-fonte podem ter comentários em inglês quando apropriado

### Projetos Novos
Ao criar um novo projeto numerado:

1. Crie pasta `NN-nome-descritivo`
2. Inclua `README.md` com:
   - Título e descrição
   - Objetivos de aprendizado
   - Requisitos
   - Como executar
   - Estrutura de arquivos explicada
3. Adicione todo código/configuração necessário
4. Atualize o README principal com a nova entrada na tabela de projetos

## Requisitos Comuns

- Python 3.8+
- Docker (para alguns projetos)
- Git

Projetos podem ter requisitos específicos documentados em seus READMEs individuais.

## Comunicação

Sempre interaja usando português Brasil, conforme configurado no CLAUDE.md global do usuário.
