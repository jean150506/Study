from datetime import date, datetime, timedelta
import json
import boto3 # lib que permite a conexão com aws 
import pandas as pd 
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
    source_path: str = ("caminho s3 do recurso")
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

def iter_objects(bucket: str, prefix: str):
    s3 = boto3.client("s3")
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
        for obj in page.get("Contents", []):
            if obj["Size"] > 0:
                yield obj["Key"]
    # Esse bloco cria um cliente s3 para que possamos acessar os objetos dentro de um s3 bucket
    # inicializamos o paginador. Ele serve pra quando temos uma quantidade massiva de dados que podem ser retornados.
    # ou seja, se nesse bucket tiver uma quantidade muito grande de arquivos, usamos o paginator para a aws divir essa carga em 
    # páginas. Ele gerencia tokens de continuação (NextToken).
    # depois de criado esse paginador, para cada página retornada pelo bucket e pelo prefixo desse bucket ( no caso o path de onde estão nossos arquivos )
    # ele vai pegar tudo o que estiver dentro da key ( do dicionário retornado pela página ) "Content". Se o dicionário não 
    # tiver essa key, então é retornada uma lista vazia. Tendo essa key, ele procura pela key "size" dentro de "Content". Se o objeto 
    # "size" existir e for maior que zero, ou seja, se o dicionário retornado tiver algo dentro, aí utilzamos a função yield
    # yield é usada para definir funções geradoras (generators). Ela funciona de forma parecida com o return, mas com uma diferença fundamental:
    # em vez de encerrar a função e devolver um único valor, o yield pausa a execução da função, entrega um valor e mantém o estado para que ela 
    # possa continuar exatamente de onde parou na próxima vez que for chamada.
    # Ou seja, com esse yield , ele vai retornar cada um dos registros de "key" dentro do objeto retornado dentro do dict "Contents"
    
def read_jsonl_object(bucket:str, key:str):
    s3 = boto3.client("s3")
    resp = s3.get_object(Bucket=bucket, Key=key)
    # aqui fazemos uma requisição ao bucket, na chave ( path ) dos nossos dados
    body = resp["Body"]
    # Aqui pegamos a estrutrua, conteúdo de fato, dentro do arquivo. Aqui acessamos o conteúdo dentro do jsonline
    for raw in body.iter_lines():
        # aqui, depois de acessarmos o body, iteramos sob cada uma das linhas desse arquivo. 
        if not raw:
            continue
        line = raw.decode("utf-8").strip()
        # encontrando a linha, decodificamos ela com utf-8 ( acentuação ) e tiramos espaços nas extremidades
        if not line:
            continue
        yield json.loads(line)
        # aqui o json.loads(str) transforma um objeto str em um objeto python  

def date_range(start: date, end: date) -> "list[date]":
    if not (start <= end):
        return []
    return [start + timedelta(days=i) for i in range ((end - start).days + 1) ]

def job(cfg:Config) -> None:
    path = cfg.source_path # de onde vamos tirar os dados 
    no_schema = path[5:] # tiramos "s3://" 
    bucket, prefix = no_schema.split("/", 1)
    # aqui pegamos o que tem antes da primeira barra, que é o bucket, e o que tem depois da primeira barra que é o path ( prefix )
    records = []
    count_files = 0
    for key in iter_objects(bucket, prefix ):
        count_files += 1 
        for rec in read_jsonl_object(bucket, key):
             records.append(rec)
            #  para cada objeto jsonlin que conseguirmos, vamos chamar a função read_jsonl_object 
            # e o retorno dessa função, que vai ser um objeto pythhon decodificado em utf -8 vai ser adicionádo à lista records 
        logging.info("Read %d file(s), %d record(s)", count_files, len(records))
        if not records:
            logging.warning("No records found for %s", cfg.date)
        df = pd.DataFrame(records)
        # a partir da lista criamos um pandas dataframe 
        output = cfg.raw_target_path + "data.parquet"
        df.to_parquet(path=output, index=False, engine="pyarrow")
        # aqui salvamos nosso arquivo em formato parquet no destino "output" sem indexador 

        logging.info("wrote %d rows to %s ", len(df), output)
        # Aqui retorna o número de linhas do dataframe escrito no nosso bucket/path de output

if __name__=="__main__":
    for h in logging.root.handlers[:]: # não sei o que essa linha faz
        # O que ela faz: O Python (e alguns frameworks ou ambientes como AWS Glue / Jupyter) 
        # costuma configurar handlers de log padrão automaticamente ao iniciar. Se você chamar logging.basicConfig()
        # depois sem limpar os handlers anteriores, os logs podem aparecer duplicados no console
        # (uma mensagem impressa duas vezes). Esse trecho percorre todos os manipuladores de log ativos
        # (root.handlers[:]) e os remove,
        # garantindo que o logging.basicConfig() configure o ambiente do zero de forma limpa.
        logging.root.removeHandler(h)
    logging.basicConfig(
        level= logging.INFO, 
        format="%(asctime)s main %(levelname)s %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    args = Args.parse()
    # parse é a função que passa argumentos para o terminal.
    if args.start_dt ==args.end_dt:
        logging.info("running job for %s", args.start_dt)
        cfg = Config(date=args.start_dt)
        job(cfg=cfg)

        # caso a data de inicio seja a mesma da data de fim da leitura, vai ser chamada a função cfg para a data de inicio 
        # somente
    else:
        logging.info("running job for %s - %s in range", args.start_dt, args.end_dt)

        dates = date_range(start=args.start_dt, end=args.end_dt)
        for dt in dates:
            cfg = Config(date=dt)
            job(cfg=cfg)
        