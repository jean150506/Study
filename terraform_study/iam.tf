module "s3_policy" {
    source = 

    name = " the name of your policy "
    description = " the description of your policy"
    
    policy = jsonencode({
        "Version" : "2012-10-17",
        "Statement" : [
            {
                "Sid" : "S3Actions",
                "Effect": "Allow",
                "Action" : [
                    "s3 : ListBucket",
                    "s3: ListBucketMultipartUploads",
                    "s3: GetObjects",
                    "s3: GetObjectVersion",
                    "s3: PutObject",
                    "s3: AbortMultipartUpload
                ],
                "Resource" : [
                    "your s3 bucket path that you what to have all those permissions"
                ]
            },
            {
                "Sid" : "KMSDecrypt",
                "Effect" : "Allow",
                "Action" : [
                    "kms: Decrypt",
                    "kms: GenerateDataKey"
                
                ],
                "Resource" : "your kms path with key"
            }
        ]
    })
}

module "glue_policy" {
    source = 
    name = "your glue policy name"
    description = "your glue policy description "

    policy = jsonencode ({
        "Version" : "2012-10-17",
        "Statement" : [
            {
                "Action" : [
                    "glue: Get*",
                    "glue: Create*",
                    "glue: Update*",
                    "glue: Start*",
                    "glue: Stop*",
                    "glue: List*",
                    "glue: Search*",
                    "glue: BatchGetPartition",
                    "glue: BatchCreatePartition",
                    "logs: CreateLogGroup",
                    "logs: CreateLogStream",
                    "logs: GetLogEvents",
                    "logs: PutLogEvents",
                    "logs: DescribeLogStreams",
                    "cloudwatch: PutMetricData"
                ],
                "Effect" : "Allow"
                "Resource":[
                    "your path:crawler*",
                    "your path:catalog*",
                    "your path:database*",
                    "your path:table*"
                ]
            },
            {
                "Action" : [
                    "iam: PassRole",
                    "iam: ListRoles"
                ],
                "Resource" : "*",
                "Effect" : "Allow",
                "Condition" : {
                    "StringEqualsIfExists" : {
                        "iam: PassedToService" : [
                            "glue.amazonaws.com"
                        ]
                    }
                }
            }
        ]
    })
}