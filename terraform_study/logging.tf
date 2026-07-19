module "cloudwatch_log_group"{
    source

    name = " the path that will be created name"
    retention_in_day = 
    
}

module "job_alarm"{
    resource =

    depends_on = [
        if we are monitoring a job, we need first that the job exist
        module.job
    ]

    cw_event_rule_name = "the job name"
    cw_event_rule_description = "description of the rule"
    state = "ENABLE"

    event_pattern = jsonencode({
        "detail-type" : ["Glue Job State Change"],
        "source" : ["aws.glue"],
        "detail" : {
            "jobName": [module.job.name]
            "state" : ["FAILED", "TIMEOUT", "ERROR"]
        }
    })

    alarm_name = " the name of the alarm that you want to create "
    alarm_description = "alarm desciption "
    comparison_operator = "comparison operator that you wanna use " / example: GreaterThanthreshold
    evaluation_periods = "1"
    period = "120"
    statistic = "Sum"
    metric_name = "TriggeredRules"
    namespace = "AWS/Events"

    dimensions = {
        RuleName = "the name of the rule "
    }
    threshold = 0 
    treat_missing_data = "how should treat the missing data " /example:  notBreaching"
    alarm_actions = "here you put your sns arn "
    ok_actions = "here you also put your sns arn "
    
}