terraform = {
    backend "s3" {
        region = "your region"
        bucket = "bucket name "
        encrypt = "true or false"
        key = "the path to .tfstate"
    }
}