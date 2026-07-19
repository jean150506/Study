module "job" {
    source = 
    depend_on = [
        here you declare what other structures need to be created first to this file be created and make sense.
        module.crawler_1 / for example
    ]
    name = "the job name"
    description = " the job description" 
    role_arn = "the role that the job will use with the permissions that he need"
    timeout = "time of job running before it broke"
    max_retries = "maximum number of retries"
    glue_version = "the version of glue that you want to use " / example "3.0"
    command_name = "here you put if you using pythonshell or glueetl"
    max_capacity = "here you define the max capacity"
    python_version = "here you define the python version you are using"
    script_location = "here you define the s3 path where the script python that your job will run are"
    max_concurrent_runs = " here you define how many jobs you can run at the same time"

    default_arguments = {
        "--TempDir" = "here you define the s3 path where the temporary files will be loaded"
        "--class" = "GlueApp"
        "--log-group" = "here you define the cloudwatch log group that will be monitoring this job "
        "--enable-continuos-cloudwatch-log" = "true"
        "--job-language" = "python"
        "--additional-python-modules" = "here you define the libs that you use on your script" / example : "boto3==1.34, pandas==2.1"
        "--enable-glue-datacatalog" = "true"
        "--enable-job-insights" = "true"
        "--enable-metrics" = "true"
        "--enable-spark-ui" = "true"
        "--job-bookmark-option" = "job-bookmark-disable"

    }
}