module "crawler_1"{
    source = "s3 bucket path whi the default information of how to build crawlers "

    name = " the name of your crawler"
    description = " the description of your crawler"
    database_name = "where your crawler will show your data "
    role = " the role with the permissions that your crawler needs" / module.role.arn
    recrawl_behavior = " the behavior of your crawler when you recrawl some data" / example: CRAW_EVERYTHING
    update_behavior = "the update behavior expected" / example: UPDATE_IN_DATABASE
    delete_behavior = " the delete behavior expected" / example: DEPRECATE_IN_DATABASE 
    s3_target_path = " the path on s3 where the data that you wanna crawl are "
    tags = local.tags / this we use to refer to other document. Not necessary all the time 
}