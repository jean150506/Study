terraform {
    required_providers {
        aws = {
            source = "hashicorp/aws"
            version = "~> 5.93.0"
        }
    }
    required_version = ">= 1.6.1"
}

provider "aws {
    region = " your region "
    
    default_tags {
        tags = module.tag.tags
    }
    
    assume_role {
        role_arn = " your account_destination "
    }
}