# Implementação de Índices em Estruturas de Dados

## Visão Geral

Este projeto apresenta a implementação de duas estruturas fundamentais de indexação em bancos de dados:

- **Árvore B+**: Estrutura balanceada otimizada para operações sequenciais e por intervalo
- **Hash Linear**: Estrutura dinâmica baseada em hashing, ideal para buscas por igualdade

Desenvolvido como parte integrante da disciplina de **Banco de Dados II**, o trabalho explora os aspectos teóricos e práticos da organização eficiente de dados em memória secundária, com ênfase em registros compostos exclusivamente por campos inteiros. A arquitetura implementada oferece total flexibilidade na configuração de parâmetros críticos de desempenho, permitindo análises comparativas detalhadas entre diferentes configurações.

---

## Índice

- [Pré-requisitos](#pré-requisitos)
- [Estrutura do Projeto](#estrutura-do-projeto)
- [Como Executar](#como-executar)
- [Configuração de Implementação](#configuração-de-implementação)
- [Estruturas Implementadas](#estruturas-implementadas)
- [Experimentos](#experimentos)
- [Qualidade e Organização do Código](#qualidade-e-organização-do-código)

---

## Pré-requisitos

Para executar este projeto, é necessário ter instalado:

- **Python 3.x** (versão mínima recomendada: 3.8)
- **Jupyter Notebook** ou **JupyterLab** (para visualização e execução dos experimentos)
- **(Opcional)** Bibliotecas auxiliares para análise de dados:
  - `numpy` - para operações numéricas
  - `matplotlib` - para visualização de resultados
  - `pandas` - para manipulação de dados tabulares

### Instalação das dependências opcionais:
```bash
pip install numpy matplotlib pandas jupyter
```

---

## Estrutura do Projeto

O repositório está organizado de forma modular e intuitiva:
```
.
├── .gitignore
├── dados_btree.csv                  # Dados sintéticos gerados para validação específica da B+ Tree
├── dados_hash.csv                   # Dados sintéticos gerados para validação específica do Hash Linear
├── implementacao_btree_bd.py        # Implementação completa da classe BPlusTree
├── implementacao_linearhash_bd.py   # Implementação completa da classe LinearHash
├── README.md                        # Documentação do projeto
├── relatorio_experimento_bd2.ipynb  # Notebook com a bateria de testes e geração de gráficos
├── relatorio_experimento_bd2.pdf    # Versão exportada do relatório final
├── teste1.csv                       # Dataset de carga progressiva (Menor volume)
├── teste2.csv                       # Dataset de carga progressiva
├── teste3.csv                       # Dataset de carga progressiva
├── teste4.csv                       # Dataset de carga progressiva
└── teste5.csv                       # Dataset de carga progressiva (Maior volume)

```

### Descrição dos Componentes:

| Arquivo | Descrição |
|---------|-----------|
| `implementacao_btree_bd.py` | Contém a classe `BPlusTree` com toda a lógica de inserção, remoção, busca e gerenciamento de páginas da Árvore B+ |
| `implementacao_linearhash_bd.py` | Contém a classe `LinearHash` com a implementação completa do algoritmo de hash linear dinâmico |
| `relatorio_experimento_bd2.ipynb` | Notebook interativo que importa as estruturas, executa testes comparativos e apresenta resultados com gráficos e análises estatísticas |
| `teste1.csv` a `teste5.csv`	| Conjunto de 5 arquivos sintéticos utilizados para o relatório de escalabilidade. |

---

## Como Executar

### Método 1: Execução via Notebook (Recomendado)

Esta é a forma ideal para visualizar os experimentos completos, incluindo análises comparativas e gráficos de desempenho.

1. **Inicie o Jupyter Notebook:**
```bash
   jupyter notebook
```
   ou
```bash
   jupyter lab
```

2. **Abra o arquivo** `relatorio_experimento_bd2.ipynb`

3. **Execute as células sequencialmente** para:
   - Importar as implementações das estruturas
   - Carregar datasets sintéticos
   - Executar operações de inserção, busca e remoção
   - Visualizar métricas de desempenho (I/Os, tempo de execução)
   - Comparar resultados entre Árvore B+ e Hash Linear

### Método 2: Execução Direta (Testes Rápidos)

Para testes isolados e rápidos de cada estrutura, execute diretamente os arquivos Python:

**Testar a Árvore B+:**
```bash
python implementacao_btree_bd.py
```

**Testar o Hash Linear:**
```bash
python implementacao_linearhash_bd.py
```

> **Nota:** Os arquivos `.py` podem conter funções de teste básicas no bloco `if __name__ == "__main__"`, permitindo verificações rápidas de funcionalidade.

---

## Configuração de Implementação

A arquitetura do projeto foi concebida com **flexibilidade** como princípio fundamental, permitindo ajustes finos nos parâmetros que influenciam diretamente o desempenho das estruturas de indexação.

### Parâmetros Configuráveis:

| Parâmetro | Descrição | Exemplo de Configuração | Impacto |
|-----------|-----------|-------------------------|---------|
| **Número de Campos** | Quantidade de campos inteiros em cada registro | `num_campos = 5` | Define o tamanho do registro e, consequentemente, a capacidade de cada página |
| **Tamanho da Página** | Tamanho físico da página (bloco) em bytes | `tamanho_pagina = 512` | Determina quantos registros/ponteiros cabem em uma página, afetando a altura da árvore e o número de I/Os |

### Consideração Importante sobre Tamanho de Página

Foi adotado o **tamanho mínimo de 256 bytes** para as páginas, em conformidade com as recomendações da literatura especializada. Esta escolha garante que:

- Páginas não-folha da Árvore B+ possam acomodar **no mínimo 3 chaves**
- Haja espaço suficiente para ponteiros e metadados
- A estrutura mantenha suas propriedades de balanceamento

> **Fundamentação Teórica:** Páginas muito pequenas aumentam a altura da árvore e o número de acessos a disco, enquanto páginas muito grandes desperdiçam espaço e aumentam o custo de leitura/escrita. O valor de 256 bytes representa um equilíbrio adequado para registros inteiros.

---

## Estruturas Implementadas

### Árvore B+ (`BPlusTree`)

A Árvore B+ é uma estrutura de dados em árvore balanceada, amplamente utilizada em sistemas de gerenciamento de bancos de dados devido à sua eficiência em operações de I/O em memória secundária.

#### Características Principais:

- **Balanceamento automático**: todas as folhas estão no mesmo nível
- **Encadeamento de folhas**: permite varredura sequencial eficiente
- **Ocupação mínima garantida**: cada nó mantém pelo menos 50% de ocupação
- **Otimização para disco**: minimiza o número de acessos a páginas

#### Operações Suportadas:

| Operação | Sintaxe | Complexidade | Descrição |
|----------|---------|--------------|-----------|
| **Inserção** | `insercao(registro)` | O(log n) | Adiciona um novo registro, realizando splits quando necessário |
| **Remoção** | `remocao(chave)` | O(log n) | Remove um registro, fazendo redistribuição ou merge de nós |
| **Busca por Igualdade** | `busca_igualdade(chave)` | O(log n) | Localiza um registro específico pela chave |
| **Busca por Intervalo** | `busca_intervalo(chave_min, chave_max)` | O(log n + k) | Retorna todos os registros no intervalo [min, max] |

#### Vantagens:
- Excelente para consultas por intervalo (range queries)
- Suporte eficiente a ordenação
- Acesso sequencial otimizado
- Balanceamento automático mantém desempenho previsível

---

### Hash Linear (`LinearHash`)

O Hash Linear é uma técnica de hashing dinâmico que permite o crescimento gradual da tabela hash sem necessidade de rehashing completo, tornando-a particularmente adequada para aplicações com crescimento incremental de dados.

#### Características Principais:

- **Crescimento incremental**: buckets são divididos um de cada vez
- **Sem reorganização global**: evita o custo de rehashing completo
- **Fator de carga controlado**: mantém desempenho previsível
- **Overflow encadeado**: utiliza páginas de overflow quando necessário

#### Operações Suportadas:

| Operação | Sintaxe | Complexidade | Descrição |
|----------|---------|--------------|-----------|
| **Inserção** | `insercao(registro)` | O(1) amortizado | Adiciona registro, disparando split quando necessário |
| **Remoção** | `remocao(chave)` | O(1) esperado | Remove registro pela chave |
| **Busca por Igualdade** | `busca_igualdade(chave)` | O(1) esperado | Localiza registro específico |

#### Restrição Importante:

A operação de **busca por intervalo NÃO é suportada** nesta estrutura. Esta limitação é inerente à natureza do hashing, que não preserva a ordem dos elementos, conforme especificado nos requisitos do projeto.

#### Vantagens:
- Busca por igualdade extremamente rápida
- Crescimento dinâmico sem reorganização total
- Uso eficiente de memória
- Desempenho constante para operações básicas

---

## Experimentos

### Geração de Dados Sintéticos

Para garantir a **reprodutibilidade** e **controle** sobre os experimentos, todos os datasets utilizados foram gerados através da ferramenta **siogen** (Synthetic I/O Generator).

**Ferramenta utilizada:** [siogen - Gerador de Dados Sintéticos](https://ribeiromarcos.github.io/siogen/)

Esta abordagem permite:
- Controle preciso sobre a distribuição dos dados
- Geração de volumes variados para testes de escalabilidade
- Reprodução exata dos experimentos por outros pesquisadores

---

### Metodologia Experimental

Os experimentos foram conduzidos de forma sistemática, variando parâmetros-chave para análise comparativa do desempenho das estruturas. A metodologia seguiu um **design fatorial**, permitindo isolar o efeito de cada variável.

#### Dimensões de Variação:

| Dimensão | Descrição | Valores Testados | Objetivo |
|----------|-----------|------------------|----------|
| **Número de Campos** | Campos inteiros por registro | Variável | Analisar impacto do tamanho do registro |
| **Tamanho da Página** | Tamanho do bloco em bytes | 256, 512, 1024, 2048 | Avaliar trade-off entre I/O e capacidade |
| **Volume de Inserções** | Quantidade de registros inseridos | 1K, 10K, 100K, 1M | Medir escalabilidade |
| **Volume de Buscas** | Operações de consulta (igualdade/intervalo) | Variável | Avaliar eficiência de recuperação |
| **Volume de Remoções** | Quantidade de registros removidos | Variável | Analisar custos de manutenção |

#### Métricas Coletadas:

1. **Número de I/Os** (operações de leitura/escrita em disco)
2. **Tempo de execução** (em milissegundos)
3. **Altura da árvore** (para B+)
4. **Número de buckets/páginas de overflow** (para Hash Linear)
5. **Taxa de ocupação** das páginas

---

### Documentação dos Resultados

A análise completa dos experimentos, incluindo:

- **Gráficos comparativos** de desempenho
- **Análises estatísticas** (média, mediana, desvio padrão)
- **Discussão aprofundada** sobre trade-offs
- **Recomendações** de uso para diferentes cenários

está integralmente documentada no **Relatório Científico** que acompanha esta entrega, disponível no notebook `relatorio_experimento_bd2.ipynb`.

---

## Qualidade e Organização do Código

### Princípios de Desenvolvimento:

O código foi desenvolvido seguindo as melhores práticas de engenharia de software, com ênfase em:

#### 1. Documentação Extensiva
- **Comentários descritivos** em todas as funções e métodos complexos
- **Docstrings** seguindo o padrão PEP 257
- Explicações detalhadas sobre algoritmos não-triviais
- Justificativas para decisões de design

#### 2. Arquitetura Modular
- **Classes bem definidas** com responsabilidades claras
- **Encapsulamento** da lógica de baixo nível (gerenciamento de disco/memória)
- **Separação de concerns**: lógica de índice separada de I/O
- **Reutilização de código** através de métodos auxiliares

#### 3. Legibilidade e Manutenibilidade
- Código formatado seguindo **PEP 8**
- **Nomes significativos** para variáveis e funções
- Funções pequenas e focadas (princípio da responsabilidade única)
- Estrutura preparada para testes unitários

#### 4. Complexidade Gerenciada
- Implementação clara de operações complexas (ex: **split de nós** na B+)
- Lógica de **redistribuição e merge** bem documentada
- Tratamento explícito de casos especiais e bordas

### Destaques da Implementação:

A implementação prioriza clareza conceitual sem sacrificar eficiência. Cada estrutura encapsula completamente sua lógica interna, expondo apenas interfaces bem definidas para operações de alto nível. O gerenciamento de páginas, fundamental para simular o comportamento em disco, foi implementado de forma transparente, permitindo fácil instrumentação para coleta de métricas.

---

## Licença e Autoria

Este projeto foi desenvolvido como trabalho acadêmico para a disciplina de **Banco de Dados II**.

---

## Contribuições

Sugestões, melhorias e discussões sobre a implementação são bem-vindas. Sinta-se à vontade para abrir issues ou enviar pull requests.

---

## Referências

- **Ramakrishnan, R.; Gehrke, J.** - *Database Management Systems*
- **Silberschatz, A.; Korth, H. F.; Sudarshan, S.** - *Database System Concepts*
- **Elmasri, R.; Navathe, S. B.** - *Fundamentals of Database Systems*

---

**Desenvolvido para a compreensão profunda de estruturas de indexação em bancos de dados**
