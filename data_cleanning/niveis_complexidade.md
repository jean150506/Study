# Níveis de Complexidade do Pipeline de Limpeza

Este documento define três níveis de complexidade para o pipeline de dados em `Study/data_cleanning`, ajudando a explicar a evolução do projeto em um portfólio de engenharia de dados.

## Nível 1 — Limpeza Básica

Características:
- Leitura do CSV com `pd.read_csv(...)`.
- Normalização de cabeçalhos (remoção de espaços, padronização para maiúsculas).
- Limpeza de espaços e conversão de strings.
- Conversão de colunas em tipos básicos:
  - `AGE` para inteiro.
  - `BMI` e `TOTAL_CHARGES` para float.
- Substituição direta de valores simples, como `Y` → `YES` e `N` → `NO`.

Benefícios:
- Implementação rápida e fácil de entender.
- Garante consistência mínima para análises exploratórias.

## Nível 2 — Validação e Imputação

Características:
- Validação de esquema de entrada para verificar colunas esperadas.
- Tratamento robusto de valores inválidos com `pd.to_numeric(errors='coerce')`.
- Imputação consciente de valores ausentes ou criação de flags de falta de dado.
- Mapeamento explícito de categorias em dicionários.
- Registro de métricas de qualidade:
  - contagem de valores ausentes;
  - contagem de valores não mapeados;
  - detecção de outliers e valores anômalos.
- Uso de funções auxiliares para torná-las testáveis.

Benefícios:
- Reduz o risco de erros silenciosos.
- Permite explicar decisões de tratamento em entrevistas.
- Melhora a confiabilidade para ingestão posterior.

## Nível 3 — Automação, Testes e Observabilidade

Características:
- Pipeline modular com validação antes e depois de cada etapa.
- Testes unitários para cada transformação de coluna.
- Relatórios de qualidade de dados em arquivos ou logs estruturados.
- Monitoramento de falhas de ingestão e métricas de desempenho.
- Uso de padrões de engenharia de dados como Data Contracts e Data Quality Checks.
- Integração com CI/CD para rodar testes a cada alteração de código.

Benefícios:
- Torna o projeto escalável e confiável em produção.
- Facilita o compartilhamento do projeto como portfólio técnico.
- Demonstra maturidade em práticas de engenharia de dados.

## Como usar esses níveis no portfólio

- Mostrar o progresso do código do nível 1 ao nível 3.
- Explicar quais problemas cada nível resolve.
- Destacar que o projeto evolui de um MVP de limpeza para uma solução de dados governada.
