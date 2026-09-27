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
@dataclass
class Config:
    date: date
    source_path: str = ("caminho s3 do recurso"
    )
    raw_target_path: str = ("caminho s3 onde vão ser descarregados os dados ")

    
    def __post_init__(self) -> None:
        # Este método é chamado automaticamente após Config ser inicializado.
        # Nesse momento, self.date já contém a data recebida na criação do objeto.
        # Usamos essa data para montar self.dt com o ano formatado como texto.
    
        self.dt = {
            "year": self.date.strftime("%Y"),
            "month": self.date.strftime("%m"),
            "day" : self.date.strftime("%d")
        }
        # a variável date vai receber um valor em algum momento. com isso 
        # quando a classe Config for inicializada, nós criamos a variável dt onde essa 
        # é um dict com o s campos de year, month e day extraídos da variável date que foi 
        # carregada antes __post_init__
        # Ao criar Config, o valor informado é guardado em self.date.
        # Depois disso, __post_init__ é chamado automaticamente.
        # Aqui montamos self.dt, um dicionário com o ano, o mês e o dia
        # extraídos de self.date.
        source_tail = self._source_partition_suffix()
        self.source_path = self.source_path.rstrip("/") + "/" + source_tail

    def _source_partition_suffix(self):
        return f"{self.dt["year"]}/{self.dt["month"]}/{self.dt["day"]}/"
        # nesse caso estamos lidando com um bucket onde a partição dele não é em hive 
    def _target_partition_suffix(self):
        return f"year={self.dt["year"]}/month={self.dt["month"]}/day={self.dt["day"]}/"
        # aqui os dados vão ser descarregados em hive format 
    
             