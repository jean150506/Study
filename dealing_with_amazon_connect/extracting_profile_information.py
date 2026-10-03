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

    def log_config(self) -> None:
        logging.info("=" * 70)
        logging.info("[CONFIG] configuraçoes carregadas")
        logging.info("=" * 70)

    @staticmethod
    def discover_customer_profile_domain(region: str) -> List[Dict[str, Any]]:
        # Aqui faremos uma requisição à api da aws ( boto3 ) para pegarmos o nome do domínio que estão as info de 
        # profiles. Como resposta, essa api fornece uma lista de dicionário de chaves str e valores diversos 
        logging.info("=" * 70)
        logging.info("[DISCOVER] procurando por domínios")
        logging.info("=" * 70)

        start_time = time.time() # aqui vamos contar o tempo de processamento
        client = boto3.client("customer-profiles", region_name = region, verify=False, config=BOTO_CONFIG)
        logging.info("[CLIENT] iniciado o client de customer-profiles")

        all_domains: List[Dict[str, Any]] = []
        next_token = None
        page_count = 0 

        while True:
            page_count += 1
            params: Dict[str, Any] = {"MaxResults": 100}
            if next_token:
                params["NextToken"] = next_token

            try:
                logging.info (f"[DISCOVERY] requisitando página {page_count}...")
                response = client.list_domains(**params)
                logging.info("[DISCOVERY] domain encontrado")
                # os argumentos de list_domains são "NextToken" e "MaxResults". usando o **params 
                # descompactamos o dicionário params como argumentos que preenchem o list domain.
                # ou seja, se params está assim: params={"MaxResults":100, "NextToken": 1}
                # depois do ** params é como se virasse MaxResults=100, NextToken=1
                # Sendo assim, dentro do list domains ficaria:
                # client.list_domains(MaxResults=100, NextToken=1)
                # como aqui não tivemos que especificar Region ou qualquer identificador único da nossa conta aws,
                # imagino que isso aqui só funcione se você estiver com as variáveis de ambiente da aws configuradas no seu pc 
                # ou se você rodar isso dentro do teu ambiente aws 
            except ClientError as e: # não sei pra que serve esse ClientError. Acho que é uma lib específica pra relatar
                # problema de conexão com cliente aws
                logging.error("[DISCOVERY] erro ao listar os domínios: {e}")
                raise 
                # keyword raises an exception and immediately stops the normal execution of the program.

            items = response.get("Items", [])
            all_domains.extend(items)
            # all_domains.extend(items) adiciona à lista todos os itens completos retornados 
            # em Items. É equivalente a: for item in items: all_domains.append(item)
            #Ou seja, a resposta que o list_domain dá é a seguinte:
            """
            {
                'Items': [
                    {
                        'DomainName': 'string',
                        'CreatedAt': datetime(2015, 1, 1),
                        'LastUpdatedAt': datetime(2015, 1, 1),
                        'Tags': {
                            'string': 'string'
                        }
                    },
                ],
                'NextToken': 'string'
            }

            com o all_domains.extend(items) pegamos uma lista que está criada já, nesse caso a list_domains é uma lista vazia
            com isso, pegamos cada um dos itens retornados pela API e adicionamos à lista no seguinte formato:
            all_domains=[
                {"DomainName1":"nome do dominio", "createdAt": data de criação do domínio,"LastUpdate":data, "Tags":se tiver},
                {"DomainName2":"nome do dominio", "createdAt": data de criação do domínio,"LastUpdate":data, "Tags":se tiver}
                ]
            Lógicamente, o segundo domain só é adicionado depois da execução completa do bloco. Digo isso porque a chave NextToken
            do primeiro domínio entra depois de registrar os items do primeiro domínio no list_domains
            """
            next_token = response.get("NextToken")
            if not next_token:
                logging.info("[DISCOVERY] ultima pagina processada")
                break
            """
            Resumo de como esse loop While funciona:
            depois do client de customer-profiles ser criado e das variáveis all_domains( lista de dicionários ), next_token e page_count serem declaradas
            aí entramos no loop while
            aqui, verificamos se já tem um valor de NextToken. Na primeira execução o NextToken é None, então não entramos nesse if 
            a partir daí entramos no try. Aqui chamos a api de list_domains e descompactamos o dicionário params que definimos lá encima
            fazemos isso porque a funçãi list_domain precisa dos argumentos de Número máximo de registros e NextToken.
            Se tivermos sucesso nesse try caímos para fora desse esquema de tentativa e excessão e vamos para o items. no Items nós fazemos 
            uma requisição ( metodo get) para a resposta que o list domain nos deu. A estrutura de resposta dele é uma dicionário de listas e esse
            dicionário tem duas chaves principais: Items e NextToken.  na linha items=response.get("Items",[]) nós pegamos tudo que estiver
            dentro da chave Items. Se ela não estiver ali é retornada uma lista vazia. Depois disso, adicionamos à lista all_domains todas as chaves presentes dentro de Items 
            porque a chave Items de reposta da função list_domains tem como valor{"key":"value"} uma lista de dicionários.
            dessa forma, a lista all_domains, pelo metodo extend, passa ter o dict dentro daquela key Items que estamos rodando.
            depois de fazer essa atribuição à all_domains, vamos para o next_token. Aqui verificamos, através do metodo get se há uma key
            dentro da resposta do list_domains chamada "NextToke". Se tiver, nós sobrescrevemos aquele None com o novo valor de next_token.
            aí recomeçamos o loop. Porém, agora quando chegarmos na parte "if next_toke: params["NextToken"] = next_token ", aqui o next_token não 
            é mais None. Agora ele possui um valor. Com ele tendo um valor, digamos que o valor seja 2, quando entramos no "try" novamente, o response vai ser diferente.
            Antes o response seria o seguinte:
            response = client.list_domains(MaxResults=100, NextToken=None)
            agora o response é :
            response = client.list_domains(MaxResults=100, NextToken=2)
            Isso quer dizer que vai ser varrida uma nova página, não a mesma que já foi.
            """

        elapsed = time.time() - start_time
        logging.info(f"tempo de execução: {elapsed}")
        for i, domain in enumerate(all_domains,1):
            # Aqui retornamos  o núemero do registro ( i ) e o registro( domain )
            # para cada posição ( i ) e dominio dentro de all_domains
            logging.info(f"{i}. {domain.get("DomainName", "N/A")}")

        return all_domains

class ConnectContactsProfileExtractor:
    def __init__(self, connect_instance_id: str, profiles_domain_name, region:str = "<REGION>", max_profiles: int= 0):
        logging.info("[EXTRACTOR] inicializando extrator ")
        self.connect_instance_id = connect_instance_id
        self.instance_short_id = connect_instance_id.split("/")[-1]
        self.profiles_domain_name = profiles_domain_name
        self.region = region
        self.max_profiles = max_profiles

        logging.info("=" * 70)
        logging.info("inicializando o cliente connect")
        self.connect_client = boto3.client("connect", region_name=region, verify=False, config=BOTO_CONFIG)
        logging.info("=" * 70 )
        logging.info("inicializando o cliente customer-profiles")
        self.profile_client = boto3.client("customer-profiles", region_name = region, verify=False, config=BOTO_CONFIG)
        logging.info("=" * 70 )

        self._processed_contacts: Set[str] = set()
        # metodo set cria uma lista de elementos únicos
        self._processed_profiles_ids: Set[str]=set()
        self._found_profiles: List[Dict[str, Any]]=[]

        # Esse bloco de código acho que não tem muito o que falar. Lembro de ter visto em algum lugar que função __init__
        # ela pré carrega dados que vamos usar. nesse caso, pre carregamos os clientes connect e profile
    def _limit_reached(self) -> bool:
        if self.max_profiles <= 0 :
            return False 
        return len (self._found_profiles) >= self.max_profiles
    

