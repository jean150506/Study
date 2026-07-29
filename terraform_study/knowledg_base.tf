module "knowledge_base" {
    source = "sua source"

    knowledge_base_name = " nome da sua knowledge_base"
    description = " descrição da sua knowledge_base "
    execution_role_arn  = " é interessante, olhando para o isolamento, que sua KB tenha uma role só pra ela"

    Knowledge_base_type = "VECTOR"
    """
    sobre os vetores. Declarar o tipo da KB como VECTOR é indicar que ela será usada para buscar semântica e não palavras chaves
    Ps vetores são representações numéricas dos textos inseridos nessa KB.Na prática, cada trecho dos documentos viram 
    um ponto num espaço multidimencional e com isso, textos com significados parecidos ficam próximos nesse espaço. Quando
    uma pergunta é feita ao agente a mesma lógica se aplica.
    Em resumo:
    VECTOR = modo de busca por significado
    vetores = representação matemática dos textos 
    objetivo = encontrar documentos semanticamente relacionados à pergunta.
    """

    vector_embedding_model_arn =  "modelo utilizado para o vetor "

    storage_configuration_type = "exeplo: OPENSEARCH_SERVERLESS"
    storage_configuration_opensearch_serverless_configuration = {
        collection_arn = "arn da collection que você utiliza"
        vector_index_name = "nome do index vector "
        field_mapping = {
            metadata_field = "nome do campo de metadata"
            text_field = "nome do campo de texto "
            vector_field =  "nome do campo de vetor "
        }
    }
}