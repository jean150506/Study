import json
import boto3 # lib para interagir com a aws 
import pandas as pd # para lidar com os arquivos 
import urllib.parse 
import os 
import uuid
from datetime import datetime, timezone
import re


REGION_NAME = "sua region"
DESTINATION_PREFIX = "bucket onde serão descarregados os dados após a execução do programa"
AGENT_ID = "id do agente do bedrock criado. Ele precisa pré existir antes desse script"
AGENT_ALIAS_ID = "ID do alias do agent. O Alias é como se fosse a versão do agente que você está usando."
ENABLE_COMPREHEND = "true. O Comprehend é o serviço de IA da AWS para detecção de dados pessoais e sensíveis."
FOLDER_LAST_LAYER = "último nível de folder antes dos seus particionamentos ou dados começarem. exemplo: bucket/folder1/folder2/partition1.../data.paquet"
source_bucket = "bucket de onde você vai pegar seus dados"
source_key = "todo o path que vem os seus dados."
# OBJETIVO DO CÓDIGO:
# estudar o processo de conversão dos arquivos e o mascaramento de informações sensíveis através de regex e comprehend

# Inicialiazando os clienetes para poder interagir com os serviços da AWS
s3_client = boto3.client("s3")
bedrock_agent_runtime = boto3.client("bedrock-agente-runtime", region_name=REGION_NAME)
comprehend_client = boto3.client("comprehend", region_name="REGION_NAME")

DESTINATION_PREFIX = os.environ("DESTINATION_PREFIX")
AGENT_ID = os.environ("AGENT_ID")
AGENT_ALIAS_ID = os.environ("AGENT_ALIAS_ID")
ENABLE_COMPREHEND = os.environ.get("ENABLE_COMPREHEND", "true").lower() == "true"
# DEFININDO OS PADRÕES REGEX:
PLACA_PATTERN = re.compile(r'\b[A-Z]{3}[0-9][A-Z0-9][0-9]{2}\b')
CPF_PATTERN  =  re.compile(r'\b\d{3}\.?\d{3}\.?\d{3}\-?\d{2}\b')
CNPJ_PATTERN = re.compile(r'\b\d{2}\.?\d{3}\.?\d{3}/?\d{4}-?\d{2}\b')
PHONE_PATTERN = re.compile(
    r'\b(?:\+55\s?)?(?:\d{2}\)?\s?)?\d{4,5}[-\s]?\d{4}\b'
)
EMAIL_PATTERN = re.compile(
    r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
)
ADDRESS_PATTERN = re.compile(
    r'(?:Rod|Rua|Av|Avenida|Alameda|Travessa|Pra[cç]a|Estrada)\s?\.?\s'
    r'[^,\n]{5,80}(?:,\s?(?:N[º]?\s?\d+|S/?N))?'
    r'(?:,\s?[^,\n]{3,50})?'
    r'(?:\s?[--]\s?[A-Z]{2})?',
    re.IGNORECASE
)

def converter(source_bucket, source_key):
    # aqui definimos a função que converte arquivos ".parquet" para ".json"
    if FOLDER_LAST_LAYER in source_key:
        if not source_key.endswith(".paquet"):
            return {"statusCode": 200, "body":"Not a parquet file, skipping"}
            # aqui, definimos esse condicional porque, caso entre outro arquivo dentro do path, não queremos que essa função pegue esse
            # arquivo.
        if source_key.startswith(DESTINATION_PREFIX):
            return {"statusCode": 200, "body":"File already exist, skipping"}
            # Aqui pulamos o reprocessamento dos arquivos.
        tmp_parquet = "/tmp/input.parquet"
        s3_client.download_file(source_bucket, source_key, tmp_parquet)
        df = pd.read_parquet(tmp_parquet)
        if "transcript" in df.columns:
            df["transcript"] = df["transcript"].apply(
                lambda x: json.loads(x) if isinstance(x, str) else x 
                # aqui pegamos o que está dentro de trasncript. se o que estiver dentro de transcript uma string (isisntance(x,str))
                # então usamos o json.loads() para deserializar convertendo um objeto json em objeto python.
                # se transcript for uma lista de strings, aqui vamos pegar essas strings e transformar elas em um objeto python. Exemplo prático:
                # "transcript" antes desse bloco = ['{"key1":"value1","key2":"value2"...},{...},{...}']
                # isso acima é uma lista de variáveis. Dessa forma não conseguimos acessar, por exemlo, somente key1
                # "transcript depois desse bloco" = [{"key1":"value1","key2":"value2"...},{...},{...}]
                # depois do bloco, tudo o que era uma string foi convertido para um dict, que era o objeto python
                # que a estrutura dos dados estava.
                # o json.loads() não transforma sempre para um dicionário. ele identifica e converte para a estrutura de dados
                # que está presente no json. [README]
            )
        records = json.loads(df.to_json(orient="records", force_ascii=False))
        return records
        # aqui termina a função de conversão para json.
def anonymize_with_regex(text: str):
    # aqui substituimos no texto os dados sensíveis por valores específicos.
    # o regex encontra o padrão que definimos no inicio do scirpt e substitui 
    text = PLACA_PATTERN.sub("[PLACA]", text)
    text = CPF_PATTERN.sub("[DOCUMENTO]", text)
    text = CNPJ_PATTERN.sub("[DOCUMENTO]", text)
    text = PHONE_PATTERN.sub("[TELEFONE]", text)
    text = EMAIL_PATTERN.sub("[EMAIL]", text)
    text = ADDRESS_PATTERN.sub("[ENDERECO]", text)

    return text 

def anonymize_with_comprehend(text: str):
    if not ENABLE_COMPREHEND or not text.strip():
        # aqui verificamos se o comprehend está habilitado e se o nosso texto, depois de remover os espaços,
        # está vazio.
        return text
    try:
        response = comprehend_client.detect_pii_entities(
            Text=text[:5000], # aqui temos uma limitação de 5000 caracteres do próprio serviço.
            LanguageCode='pt'
        )
    except Exception as e:
        print(f'comprehend falhou, retornando texto somente com regex : {e}')
        return text
    pii_map = {
        'NAME':['NOME'],
        'ADDRESS':['ENDERECO'],
        'PHONE':['TELEFONE'],
        'EMAIL':['EMAIL'],
        'SSN':['DOCUMENTO'],
        'CREDIT_DEBIT_NUMBER':['CARTAO'],
        'BANK_ACCOUNT_NUMBER':['CONTA_BANCARIA'],
        'DATE_TIME':None,
        'AGE':None
    }

    entities = sorted(
        response.get('Entities',[]),
        key=lambda e: e["BeginOffset"],
        reverse=True
    )
    for entity in entities:
        entity_type = entity['Type']
        replacement = pii_map.get(entity_type)

        if replacement and entity["Score"]>=0.85:
            start = entity["BeginOffset"]
            end = entity["EndOffset"]
            text = text[:start] + replacement + text[end:]
            # o que fazemos aqui: botamos o comprehend para analisar o texto( max de 5000 caracteres). Se dentro do texto
            # o comprehend identificar algum dos padrões que definimos acima no pii_map ( definimos em ingles por que é o padrao
            # do comprehend). O comprehend gera um campo chamado "BeginOffset" que é onde a palavra no padrão se inicia e um 
            # campo "EndOffset" que é onde a palavra se encerra. ele também gera um campo chamado "Score" onde ele diz 
            # o percentual de chance daquela palavra/frase ser um dado sensível. Com base nisso, se ele identificar um padrão
            # ( if replacement) e se ele julgar que a chance de ser um dado sensível for maior ou igual a 85%, ele vai no texto 
            # pega onde essa palavra/frase inicia e onde ela termina e substitui tudo o que estiver ENTRE esse intervalo.
            # O Comprehend analisa o texto, detecta dados pessoais e retorna suas posições
            # Ordenamos em REVERSE para substituir do final → início, preservando os índices
            # Para cada entidade detectada:
            #   - Verificamos se está no pii_map (se deve ser mascarada)
            #   - Verificamos se Score >= 0.85 (alta confiança)
            #   - Substituímos tudo entre BeginOffset e EndOffset pelo rótulo (ex: [NOME])
    return text

def anonymize( text: str):
    text = anonymize_with_regex(text)
    text = anonymize_with_comprehend(text)
    # Aqui é onde de fato aplicamos as anonimizações definidas nas funções ao texto
    return text

SUMMARY_PROMPT_TEMPLATE = """
GERE UM RESUMO DO TEXTO QUE VOCÊ RECEBER RESPEITANDO A SEGUINTE ESTRUTURA:
**TEMA PRINCIPAL DO TEXTO **: [TEMA DO TEXTO]
**RESUMO**: [RESUMO BREVE SOBRE O QUE O TEXTO TRATA]
**PROBLEMA IDENTIFICADO**:[PROBLEMA IDENTIFICADO NO TEXTO CASO TENHA]
**SOLUÇÃO APLICADA**: [COMO A QUESTÃO APRESENTADA NO TEXTO FOI RESOLVIDA]

TEXTO: 
{text}
"""

def extract_conversation(record):
    transcript =  record.get("transcript", [])
    # aqui recebemos um objeto do tipo dicionário, e desse dict procuramos a key "transcript". Se ela existir, 
    # salvamos o resultado dele à variável "trasncript" que seria uma lista, caso contrário retornamos uma lista vazia.
    if not transcript:
        return None
    lines = []
    for msg in transcript:
        role = msg.get("ParticipantRole", "UNKNOWN")
        content = msg.get("Content", "")
        # aqui, dentro da lista "transcript" temos dicionários que possuem os campos/ keys ParticipantRole e Content.
        # Salvamos esses campos nas variáveis
        if content.strip():
            # aqui, de maneira implícita, estamos declarando que, caso depois de tirar o espaço do inicio e do fim
            # content ainda seja True, ou seja, após tirar os espaços, se content ainda existir...
            lines.append(f"[{role}]: [{content}]")
            # adicionamos à lista "lines" a linha de Participante: Content
    return "\n".join(lines) if lines else None
    # aqui unimos todos os registros em lines separando por quebra de linha 
def invoke_agent(conversation_text):
    session_id = str(uuid.uuid4())
    # aqui criamos um identificador único para a sessão e convertemos para uma string 
    prompt = SUMMARY_PROMPT_TEMPLATE.format(conversation_text = conversation_text)
    # declaramos aqui que o agente que vamos invocar deve usar como prompt as infromações que definimos em
    # SUMMARY_PROMPT_TEMPLATE 
    try:
        response = bedrock_agent_runtime.invoke_agent(
            agent_id = AGENT_ID,
            # definimos o id do agente que deve ser invocado 
            agentAliasId = AGENT_ALIAS_ID,
            # definimos a identificação da versão do agente que deve ser invocado 
            sessionId=session_id,
            # o id unico que criamos para a sessão
            inputText=prompt
            # o prompt do agente que definimos acima 
        )
        completion = ""
        for event in response["completion"]:
            if "chunk" in event:
                # com chunk sendo um fragmento de resposta
                chunk_data = event["chunk"].get("bytes", b"")
                # chunk_data sendo bytes desse fragmento
                completion += chunk_data.decode("utf-8")
                # agregamos à completion todos os fragmentos da resposta para gerar uma resposta completa.
        return completion 
    except Exception as e :
        print(f"[ERROR]: {e}")
        # caso tenhamos um erro na tentativa de invocar o agente, retornamos o erro que tivemos 
def parse_summary_response(response_text: str):
    fields ={
        "titulo":"",
        "resumo":"",
        "problema_identificado":"",
        "solucao_aplicada":""
        # aqui criamos um dicionário vazio com keys a serem preenchidas.

    }
    patterns = {
    "titulo": r"\*?\*?T[ií]tulo\s*:\s*\*?\s*(.*?)(?=\n\*?\s*\|\s*$)",
    "resumo": r"\*?\*?Resumo\s*:\s*\*?\s*(.*?)(?=\n\*?\s*\|\s*$)",
    "problema_identificado": r"\*?\*?Problema identificado\s*:\s*\*?\s*(.*?)(?=\n\*?\s*\|\s*$)",
    "solucao_aplicada": r"\*?\*?Solu[cç][aã]o aplicada\s*:\s*\*?\s*(.*?)(?=\n\*?\s*\|\s*$|\Z)"
    # aqui definimos a expressão regular para encontrar esses campos no meio do texto

    }

    for field , pattern in patterns.items():
        match = re.search(pattern, response_text, re.IGNORECASE | re.DOTALL )
        # aqui, para cada campo, procuramos o padrão que estabelecemos dentro de um texto (response_text) ignorando
        # tamanho das letras e pondo o ponto final em cada uma das quebras de linha 
        #  se encontrarmos alguma correspondência com o padrão que definimos....
        if match:
            fields[field] = match.group(1).strip()
            # pegamos o primeiro grupo que pegamos o padrão e trimaos o espaço no inicio e final.
            # exemplo: **titulo**: meu estudo. O re.search encontra esse trecho e o group(1) retorna "meu estudo".
            # se mudassemos, por exemplo, para "group(0)" teríamos como retorno "**titulo**: meu estudo /n"
        
    return fields 

def summary_already_exists(source_bucket, dest_key):
    try:
        s3_client.head_object(Bucket=source_bucket, Key=dest_key)
        return True
    except s3_client.Exceptions.ClientError:
        return False
def lambda_handler(event, context):
    if "Records" in event:
        source_bucket = event["Records"][0]["s3"]["bucket"]["name"]
        source_key = urllib.parse.unquote_plus(
            event["detail"]["object"]["key"], encoding="utf-8"
        )
    else:
        return {"statusCode": 400, "body":"unknown. Error "}
    if not source_key.endswith(".parquet"):
        return "not a paquet file, skipping"
    if source_key.startswith(DESTINATION_PREFIX):
        return "file already exists"
    
    records = converter(source_bucket, source_key)
    if not records:
        return "No records to proccess"
    conversations = records if isinstance(records, list) else [records]

    year_match = re.search(r"year=(\d{4})", source_key)
    month_match = re.search(r"month=(\d{2})", source_key)
    day_match = re.search(r"day=(\d{2})", source_key)

    if year_match and month_match and day_match:
        year = year_match.group(1) 
        # year_match = "year=xxxx"
        # year_match.group(1) = "xxxx"
        # year = year_match(1) = "xxxx"
        month = month_match.group(1)
        day = day_match.group(1)
    else:
        now = datetime.now(timezone.utc)
        year = str(now.year)
        month = f"{now.month:02d}"
        day = f"{now.day:02d}"

    dest_key_default = (
        f"{DESTINATION_PREFIX}/y={year}/m={month}/d={day}/"
        f"summaries_{year}-{month}-{day}"
    )