module "knowledge_base" {
    source = "sua source"

    knowledge_base_name = " nome da sua knowledge_base"
    description = " descrição da sua knowledge_base "
    execution_role_arn  = " é interessante, olhando para o isolamento, que sua KB tenha uma role só pra ela"

    Knowledge_base_type = "VECTOR"
}