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
    df.to_parquet("Data_frame.parquet",index=False)
    return df

@dataclass
class Config:
    raw_path: str = str(pathlib.Path.cwd() / "raw")
    context_path: str = str(pathlib.Path.cwd() / "context")
    
@staticmethod
def create_directory(raw_path, context_path):
    os.mkdir(raw_path)
    os.mkdir(context_path)

if __name__=="__main__":
    create_directory(Config.raw_path, Config.context_path)