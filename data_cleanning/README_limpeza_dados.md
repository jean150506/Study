README de Limpeza de Dados - Estudo de Caso

1. Objetivo do Script
---------------------
Este script tem como propósito executar um pipeline de limpeza e normalização de um conjunto de dados tabulares carregado a partir de um arquivo CSV. O foco é preparar um dataframe para análise ou consumo por etapas posteriores de um processo de engenharia de dados.

2. Ingestão do Dataset
----------------------
- O arquivo de origem é `Dados_trash.csv`.
- O leitor utiliza `pd.read_csv(..., sep=';')`, o que indica que o arquivo CSV utiliza ponto e vírgula como delimitador.
- A função `reading_file` resolve o caminho de forma relativa ao local do script, o que é uma boa prática para portabilidade local.

3. Normalização de Metadados de Coluna
---------------------------------------
- `treating_spaces` remove espaços em branco antes e depois dos nomes das colunas e também elimina espaços internos do nome da coluna.
- `treating_uppercase` converte todos os nomes de coluna para caixa alta, garantindo uniformidade e facilitando validação de esquema.

4. Regras de Transformação por Coluna
--------------------------------------
4.1 `GENDER_ID`
- Normaliza valores de gênero usando string processing do pandas.
- Substitui `M` por `male` e `f` por `Female`.
- Converte tudo para lowercase ao final.
- Corrige o erro de digitação `femaleale ` para `female`.
- Isso busca uniformizar variações como `M`, `f`, `male` e `FEMALE`.

4.2 `AGE`
- Valores faltantes (`NaN`) são preenchidos com `0`.
- Depois, valores `float` são convertidos para `int`.
- Isso assume que idades ausentes devem ser tratadas como zero, o que é uma decisão de imputação forte e vale comentar no contexto de uso.

4.3 `BMI`
- Substitui o valor textual `UNKNOWN` por `0`.
- Converte a coluna para `float` e faz arredondamento com duas casas decimais.
- Este tratamento transforma um campo misto (texto + numérico) em um campo numérico consistente.

4.4 `IS_SMOKER`
- Converte os valores para uppercase e remove espaços em branco.
- Normaliza as respostas de fumante: `Y` vira `YES`, `N` vira `NO`.
- Essa etapa melhora a qualidade dos dados categóricos, reduzindo ruído causado por variações de caixa e formatação.

4.5 `REGION_NAME`
- Remove espaços em branco de borda, garantindo que valores de região estejam limpos.
- Não faz outras normalizações geoespaciais, mas já evita duplicações por espaços extras.

4.6 `TOTAL_CHARGES`
- Remove o prefixo de moeda `$ ` dos valores.
- Converte o campo para `float` e faz arredondamento para duas casas decimais.
- Preenche valores ausentes com `0`.
- Essa transformação converte uma coluna de faturamento aparentemente textual em uma variável numérica pronta para análise financeira.

5. Observações de Qualidade de Dados
------------------------------------
- O dataset apresenta inconsistências de espaços em nomes de coluna e valores, como ` FEMALE ` e `SOUTHWEST   `.
- Há variações de texto em `IS_SMOKER` (`Y`, `N`, ` NO`, `yes `) que exigem normalização.
- Existem valores `UNKNOWN` na coluna `BMI`, o que representa dados não informados.
- Em `AGE`, há células vazias que foram convertidas para `0`, o que pode ser apropriado para alguns casos, mas deve ser documentado como uma imputação específica.
- O uso de `0` para valores faltantes em `TOTAL_CHARGES` também é uma escolha de tratamento que deve ser ponderada no contexto de negócio.

6. Análise de Engenharia de Dados
---------------------------------
Pontos positivos:
- O pipeline usa funções modulares e nomeadas, facilitando a leitura e reutilização.
- O tratamento é organizado por coluna, o que ajuda a rastrear transformações específicas.
- A conversão de cabeçalhos para caixa alta promove consistência entre etapas.

Riscos e pontos de atenção:
- A imputação com `0` pode ocultar dados missing e impactar análises de média, soma e regressão.
- As regras de normalização em `GENDER_ID` não cobrem todas as variantes possíveis (`FEMALE`, `female`, `F`, etc.).
- `IS_SMOKER` pode conter outros valores além de `Y`, `N` e `yes`, e o script atual não valida valores inesperados.
- `TOTAL_CHARGES` remove apenas `$ `, mas não cobre outros formatos possíveis de moeda ou símbolos.
- Não há validação de esquema ni checkpoints de qualidade antes/depois das transformações.

7. Recomendações para Produção
------------------------------
- Adicionar validação de esquema: verificar presença e tipos esperados das colunas.
- Registrar métricas de qualidade de dados: contagem de valores ausentes, valores únicos e valores anômalos antes e depois.
- Tratar valores ausentes de forma explícita: usar imputation documentada ou flag de ausência em vez de zero quando apropriado.
- Centralizar padrões de normalização em funções reutilizáveis e testáveis.
- Incluir testes unitários para cada transformação, especialmente para `GENDER_ID`, `BMI`, `IS_SMOKER` e `TOTAL_CHARGES`.
- Adicionar logging em vez de `print`, para uso em ambientes de produção.

8. Conclusão
-------------
O script demonstra um pipeline inicial de limpeza de dados com foco em:
- normalização de metadados de coluna,
- correção de formatos em colunas categóricas,
- tratamento de valores ausentes e tipos incorretos,
- preparação de variáveis numéricas para análise.

Para um portfólio de engenharia de dados, vale destacar que o trabalho mostra habilidade em identificar e corrigir problemas comuns de qualidade de dados, além de fornecer um ponto de partida sólido para ampliar o pipeline com validação e governança.

9. Sugestões de evolução
------------------------
- Criar um processo de validação de dados de entrada com esquema definido.
- Usar artefatos como `requirements.txt` ou ambiente virtual documentado.
- Adicionar um fluxo de processamento mais robusto, onde cada transformação gera um relatório de alteração de dados.
- Documentar decisões de imputação e normalização no README do projeto para contextos de entrevista.
