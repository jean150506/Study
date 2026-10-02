import io # pra que serve essa lib ?
import logging 
import sys 
import json 
import time 
from argparse import ArgumentParser 
from dataclasses import dataclass
import dataclasses 
from datetime import date, datetime, timedelta, timezone 
from typing import List, Tuple, Dict, Any, Optional, Set 

import boto3
import pyarrow as pa 
import pyarrow.parquet as pq 
from botocore.config import Config as BotoConfig # pra que serve essa lib ?
from botocore.exceptions import ClientError # imagino que essa lib seja para pegar os logs de erro de Cliente ?

logger = logging.getLogger()
logger.setLevel(logging.INFO)
handler = logging.StreamHandler(sys.stdout) # não sei o que essa linha faz 
handler.setLevel(logging.INFO)
formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# bom, pelo o que entendi esse bloco de código é para configurar o sistema de logs para podermos acompanhar a execução do job 
# handler a gente configura para poder apagar os logs gerados originais, para não termos infromações duplicadas com os logs originais 
# e os que agente tá tentando criar.
# formatter é para a gente definir a estrutura dos logs

logging.info("=" * 70 )
# destacar que o job está começando
logging.info("MODULO CARREGADO  - IMPORTS CONCLUÍDOS COM SUCESSO")
logging.info("=" * 70)

BRT = timezone(timedelta(hours=-3))
# contante para conseguirmos definir o fuso mais a frente
UTC = timezone.utc

BOTO_CONFIG = BotoConfig(retries={"max_attemps": 10, "mode": "adaptive"})

_ADDRESS_TYPE = pa.struct([
    ("Address1", pa.string()),
    ("Address2", pa.string()),
    ("Address3", pa.string()),
    ("Address4", pa.string()),
    ("City", pa.string()),
    ("County", pa.string()),
    ("State", pa.string()),
    ("Provincy", pa.string()),
    ("Country", pa.string()),
    ("PostalCode", pa.string()),
])

_CONTACT_PREFERENCE_TYPE = pa.list_(pa.struct([
    ("KeyName", pa.string()),
    ("KeyValue", pa.string()),
    ("ProfileId", pa.string()),
    ("ContactType", pa.string()),
]))

PROFILE_SCHEMA = pa.schema([
    ("ProfileId", pa.string()),
    ("AccountNumber", pa.string()),
    ("AdditionalInformation", pa.string()),
    ("PartyType", pa.string()),
    ("PartyTypeString", pa.string()),
    ("ProfileType", pa.string()),
    ("BusinessName", pa.string()),
    ("FirstName", pa.string()),
    ("MiddleName", pa.string()),
    ("LastName", pa.string()),
    ("BirthDate", pa.string()),
    ("Gender", pa.string()),
    ("GenderString", pa.string()),
    ("PhoneNumber", pa.string()),
    ("MobilePhoneNumber", pa.string()),
    ("HomePhoneNumber", pa.string()),
    ("BusinessPhoneNumber", pa.string()),
    ("EmailAddress", pa.string()),
    ("PersonalEmailAddress", pa.string()),
    ("BusinesEmailAddress", pa.string()),
    ("Address", _ADDRESS_TYPE),
    ("ShippingAddress", _ADDRESS_TYPE),
    ("MaillingAddress", _ADDRESS_TYPE),
    ("BillingAddress", pa.string()),
    ("Attributes", pa.map_(pa.string(), pa.string())),
    ("FoundByItems", pa.list_(pa.struct([
        ("KeyName", pa.string()),
        ("Values", pa.list_(pa.string())),

    ]))),
    ("EngagementPreferences", pa.struct([
        ("Phone", _CONTACT_PREFERENCE_TYPE),
        ("Email", _CONTACT_PREFERENCE_TYPE),
    ])),
    ("raw_payload", pa.string())
    
])

# Esse bloco de cima para que estamos só definindo todas as colunas que o amazon connect pode entregar de profiles, mas pq usar o Pyarrow ?

@dataclass
# decorador pra identificar que sua classe basicamente vai ser para guardar variáveis e não ter de usar self nem init 
class Args:
    start_dt: date
    end_dt : date
    _DATE_FORMAT : str  = "%Y-%m-%d"

    @staticmethod
    # decorador para não termos que usar o self na função de sequência
    def _read_date(s: str) -> date:
        return datetime.strptime(s, Args._DATE_FORMAT).date()
        # pegamos a data que for passada dentro dessa função e convertemos ela para o formato datetime e por fim
        # ficamos somente com a data no formato yyyy-mm-dd
    
    @classmethod
    def parse(cls):
        # aqui vamos passar os argumentos de data que vão para o terminal
        logging.info("=" * 70)
        logging.info("Iniciando o parsing de argumentos do terminal ")
        logging.info("=" * 70)

        _DM1 = date.today() - timedelta(days=1)
        ap = ArgumentParser()
        ap.add_argument(
            "--start-dt", required=False, type=Args._read_date, default=_DM1, help="YYYY-MM-DD"
        )
        # aqui definimos que o argumento que PODE ser passado no terminal é o argumento de --start-dt. Ele não é 
        # obrigatório, por isso o required=False, o tipo de dado que esse argumento vai carregar é um tipo de dado 
        # Date, porque é a resposta da função _read_date ( entramos com uma string, formatamos para yyyy-mm-dd, convertemos
        # essa string para datetime e por fim convertemos ela somente para date). Caso esse argument não seja passado 
        # ele é assumido como d-1 
        ap.add_argument(
            "--end-dt", required=False, type=Args._read_date, default=_DM1, help="YYYY-MM-DD"
        )

        args, _others = ap.parse_known_args()
        # isso aqui quer dizer que args vai receber os argumentos conhecidos( --start-dt e --end-dt) e que _others
        # vai receber outros argumentos que não fomos nós que definimos. Argumentos que são executados juntos com o 
        # terminal. 
        # Sua explicação está corretíssima. O parse_known_args() é excelente (e muito usado em engenharia de dados) 
        # porque evita que o script quebre com um erro de argumento desconhecido caso plataformas de execução 
        # (como AWS Glue, Databricks, Airflow ou containers Docker) injetem parâmetros extras automáticos na linha 
        # de comando. O que é conhecido vai para args, e o restante fica guardado em _others de forma segura.

        logging.info("=" * 70)
        logging.info("Fim do parsing")
        logging.info("=" * 70)

        return cls(start_dt=Args.start_dt, end_dt=Args.end_dt)

@dataclass
class Config:
    target_layer: str = "<LAYER>"
    indicator: str = "<PROJECT NAME>"
    squad_tag: str = "<IDENTIFIER OF THE RESPONSIBLE FOR THE INFORMATION>"
    environment: str = "<WHERE THE DATA IS GOING TO>"
    connect_instance_id: str = "<CONNECT INSTANCE ARN>"
    profile_domain_name: str = "<PROFILE DOMAIN NAME>"
    region: str = "<REGION>"
    output: str = dataclasses.field(init=False)

    def __post_init__(self) -> None:
        self.output_bucket=f"<YOUR BUCKET PATH>"

    @property # não sei pra que serve
    def instance_short_id(self) -> str :
        return self.connect_instance_id.split("/")[-1]
        # aqui pegamos o último campo antes da barra 
        xxxxx/xxxxxx/[AQUI]
    def split_output_bucket(self) -> Tuple[str, str]:
        path = self.output_bucket.split("://", 1)[-1]
        # depois dessa linha o caminho do bucket fica algo assim:
        # antes:
        # s3://<BUCKET>/<PREFIX>
        # depois( o que tem antes de :// ele joga fora):
        # <BUCKET>/<PREFIX
        bucket_name,_, prefix = path.partition("/")
        # depois daqui fica:
        # bucket_name = <BUCKET>, _=/, prefix=PREFIX
        # o "_" é um placeholder para sinalizar que ele vai receber um valor que não vai ser utilizado, mas que a função 
        # no caso a função .partition() precisa devolver. Ela, nesse caso, sempre vai retornar 3 valors, o que está antes do 
        # delimitador, o delimitador e o que está depois do delimitador.
        return bucket_name, prefix.rstrip("/")
        # aqui usamos o rstrip para caso o bucket tiver várias subpastas, o prefix vai pegar a / mais a direita 