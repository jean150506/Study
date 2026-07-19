module "conditional to craw" {
    source 
    depends_on = [
        job_name,
        crawler_name    
    ]

    name = "the name of the trigger "
    description = " the description of the trigger"
    type = " type of the trigger" / example: CONDITIONAL 
    
}