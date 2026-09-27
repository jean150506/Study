from datetime import date, datetime, timedelta
import json
# import boto3 # lib que permite a conexão com aws 
# import pandas as pd 
from argparse import ArgumentParser # lib para passar argumentos extras do terminal 
from dataclasses import dataclass 
import logging
import sys  
 
@dataclass # usamos esse decorador quando queremos indicar que a classe que será criada 
# é basicamente para guardar variáveis
class Args:
    start_dt    : date 
    end_dt      : date
    _DATE_FORMAT: str = "%Y-%m-%d"

    @staticmethod
    def _read_date(s:str) -> date :
        return datetime.strptime (s, Args._DATE_FORMAT).date()
        # pega o valor de "s", que é esperado ser uma string, e convertee para datetime 
        # padroniza no formato que definimos em _DATE_FORMAT e por fim tira o time, deixando somente
        # a data
    @classmethod
    # quando definimos uma classmethod, 
    # os argumentos definidos dentro da classe são referenciados 
    # diretamente dentro da função que decoramos com o classmethod 
    # nesse caso, "cls" vai receber os argumentos de start_dt e end_dt que 
    # definimos dentro da classe.
    def parse(cls):
        _DM1 = date.today() - timedelta(days=1)
        # definição para pegarmos o dia anterior à rodagem desse job 
        ap = ArgumentParser()
        # definido assim só pra não ter que escrever ArgumentParser().add_argument()
        ap.add_argument("--start-dt", type=Args._read_date, required=False, default=_DM1)
        ap.add_argument("--end-dt", type=Args._read_date, required=False, default=_DM1)
        args, _others = ap.parse_known_args()
        # args recebe os argumentos reconhecidos pelo ArgumentParser ( no caso --start-dt e --end-dt)
        # _others recebe demais argumentos que podem aparecer no terminal sem retornar erro.
        return cls(**vars(args))
        # Converte o Namespace args em um dicionário e usa seus valores
        # para criar e retornar uma instância da classe Args.