import pandas as pd
import numpy as np
import json
from dataclasses import dataclass
import pathlib
import os

@staticmethod
def creating_parquet():
    np.random.seed(42)

    # Gerando dados aleatórios
    quantidade = 100
    dados = {
        'id': range(1, quantidade + 1),
        'nome': [f'Usuario_{i}' for i in range(1, quantidade + 1)],
        'idade': np.random.randint(18, 65, size=quantidade),
        'salario': np.round(np.random.uniform(3000, 15000, size=quantidade), 2),
        'ativo': np.random.choice([True, False], size=quantidade)
    }

    df = pd.DataFrame(dados)
    return df

@dataclass
class Config:
    raw_path: str = str(pathlib.Path.cwd().parent / "raw")
    context_path: str = str(pathlib.Path.cwd().parent / "context")
    
@staticmethod
def create_directory(raw_path, context_path):
    try:
        os.mkdir(raw_path)
    except FileExistsError:
        os.rmdir(raw_path)
        os.mkdir(raw_path)
    try:
        os.mkdir(context_path)
    except FileExistsError:
        os.rmdir(context_path)
        os.mkdir(context_path)



@staticmethod
def loading_raw(raw_path, df):
    df = creating_parquet()
    df.to_parquet(raw_path, index=False)
    return df

if __name__=="__main__":
    create_directory(Config.raw_path, Config.context_path)
    df = creating_parquet()
    loading_raw(Config.raw_path, df)
    
    