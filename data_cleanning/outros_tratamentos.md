# Outros Tratamentos Recomendados

## 1. Objetivo

Este documento complementa a limpeza realizada em `cleanning_job.py` com sugestões de tratamentos adicionais e melhorias que fortalecem o pipeline de dados.

## 2. Problemas identificados em `Dados_trash.csv`

- Valores inconsistentes na coluna `IS_SMOKER`: `Y`, `N`, `yes`, ` NO`, `YESES`, espaços extras.
- Valores `UNKNOWN` em `BMI` que obrigam conversão numérica segura.
- Formatos monetários em `TOTAL_CHARGES` com prefixo `$ ` e casas decimais irregulares.
- Cabeçalhos de coluna com espaços extras e texto irregular: `AGE `, `b m i`, `is_SMOKER`.
- Valores de gênero `M`, `f`, `male`, ` FEMALE ` sem padronização clara.
- Espaços em branco no final de `REGION_NAME` e valores regionais não normalizados.
- Ausência de idade em algumas linhas, tratada atualmente como `0`.

## 3. Tratamentos adicionais sugeridos

### 3.1 Normalização segura de `IS_SMOKER`

- Usar mapeamento explícito em vez de substituições parciais:

```python
smoker_map = {
    'Y': 'YES',
    'YES': 'YES',
    'N': 'NO',
    'NO': 'NO'
}

df['IS_SMOKER'] = (
    df['IS_SMOKER']
      .astype('string')
      .str.strip()
      .str.upper()
      .map(smoker_map)
)
```

- Detectar valores não mapeados e gerar uma coluna de flag ou relatório de qualidade.

### 3.2 Padronização de `GENDER_ID`

- Ajustar variantes comuns para uma lista controlada:

```python
gender_map = {
    'M': 'male',
    'MALE': 'male',
    'F': 'female',
    'FEMALE': 'female'
}
```

- Aplicar `.str.strip()` e `.str.upper()` antes do mapeamento.

### 3.3 Conversão robusta de `BMI`

- Usar `pd.to_numeric(errors='coerce')` para transformar valores inválidos em `NaN`.
- Definir abordagem de imputação: `0`, média de grupo, ou deixar como `NaN` e usar sinalizador de valor ausente.

### 3.4 Tratamento de `TOTAL_CHARGES`

- Remover quaisquer símbolos não numéricos com regex:

```python
import re

df['TOTAL_CHARGES'] = (
    df['TOTAL_CHARGES']
      .astype('string')
      .str.replace(r'[^
0-9.,-]', '', regex=True)
      .str.replace(',', '.')
)
```

- Converter para `float` com `pd.to_numeric(errors='coerce')`.
- Manter um campo booleano para indicar valores faltantes ou inválidos.

### 3.5 Validação e registro de qualidade de dados

- Adicionar checagem de esquema antes e depois da limpeza.
- Contabilizar valores ausentes, valores mapeados como `NaN`, e registros rejeitados.
- Criar uma saída de logs ou relatório de métricas de qualidade.

## 4. Exemplos de uso de regex e extração

- Remover espaços e caracteres especiais:

```python
clean_text = df['REGION_NAME'].astype('string').str.strip().str.replace(r'\s+', ' ', regex=True)
```

- Verificação de formatos numéricos:

```python
valid_bmi = df['BMI'].astype('string').str.match(r'^\d+(\.\d+)?$')
```

## 5. Recomendações de projeto

- Documentar todas as decisões de imputação no README do projeto.
- Evitar substituir valores ausentes por `0` sem contexto claro.
- Criar testes automatizados para cada regra de transformação.
- Usar uma etapa de pré-validação antes de transformar os dados para evitar perda silenciosa de qualidade.
