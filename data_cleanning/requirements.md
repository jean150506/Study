# Requisitos de Ambiente e Dependências

## 1. Objetivo

Este documento descreve o ambiente mínimo e as dependências necessárias para executar o pipeline de limpeza em `Study/data_cleanning/cleanning_job.py`.

## 2. Ambiente Python

- Versão recomendada: Python 3.11 ou superior.
- O projeto já usa um ambiente virtual localizado em `.venv`.
- Usar ambiente virtual garante isolamento e evita conflitos de pacotes.

## 3. Criação do ambiente virtual

No PowerShell:

```powershell
cd c:\Users\Jean\Desktop\Scripts\study_programs\Study
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
```

## 4. Instalação de dependências

Instale o pacote necessário:

```powershell
python -m pip install pandas
```

### Dependências essenciais

- `pandas` - biblioteca principal para leitura e transformação do CSV.
- `pathlib` - módulo padrão do Python usado para resolver caminhos de arquivos.

## 5. Boas práticas

- Use `python -m pip install ...` dentro do ambiente virtual.
- Não confie em instalações globais do Python quando o projeto estiver em `.venv`.
- Crie um arquivo `requirements.txt` se desejar fixar versões:

```powershell
python -m pip freeze > requirements.txt
```

## 6. Exemplo de `requirements.txt`

```text
pandas==2.2.0
```

> Nota: a versão exata deve ser ajustada de acordo com o ambiente de desenvolvimento. O arquivo `requirements.txt` torna o projeto mais reproduzível para entrevistas e deploy.

## 7. Validação do ambiente

Após instalar as dependências, teste a execução do script:

```powershell
python .\data_cleanning\cleanning_job.py
```

Se o script rodar sem erro, o ambiente está configurado corretamente.
