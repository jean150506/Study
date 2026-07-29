module "data_source" {
    source = "caminho do source "

    knowledge_base_id = "o ID da knowledge_base que seu source vai ser associado "
    name = " nome do source"
    data_source_type = "s3 ou outro tipo de datasource type, como web crawler "

    s3_configuration = {
        bucket_ar = "o identificador do seu pucket que será usado como data source"
        inclusion_prefixes = [
            "aqui você adiciona o prefixo (path depois do nome do bucket ) caso não queira interagir diretamente com o bucket"
            # ponto de atenção aqui: só é aceito um prefixo por bucket. Sendo assim, se você precisar de mais de uma data source
            # é preciso criar outro módulo.
        ]
    }
    # como esse documento só faz sentido ser criado tendo uma Knowledge_base, aqui faz sentido ter um depends_on
    depends_on = [
        module.knowledge_base
    ]
}