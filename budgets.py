import boto3
import os
import json
import datetime
from json import JSONEncoder
import logging
from botocore.client import Config

# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()

def lambda_handler(event, context):
    ROLE_ARN = os.environ['ROLE_ARN']

    sts_connection = boto3.client('sts')
    acct_b = sts_connection.assume_role(
            RoleArn=ROLE_ARN,
            RoleSessionName="cross_acct_lambda"
    )
                
    ACCESS_KEY = acct_b['Credentials']['AccessKeyId']
    SECRET_KEY = acct_b['Credentials']['SecretAccessKey']
    SESSION_TOKEN = acct_b['Credentials']['SessionToken']

    # # create service client using the assumed role credentials
    client = boto3.client(
            "budgets",
            aws_access_key_id=ACCESS_KEY,
            aws_secret_access_key=SECRET_KEY,
            aws_session_token=SESSION_TOKEN,
    )

    account_id = os.environ['ACCOUNT_ID']
    paginator = client.get_paginator("describe_budgets") #Paginator for a large list of accounts
    response_iterator = paginator.paginate(AccountId=account_id)

    with open("data.json", "w") as f:
        for budgets in response_iterator:
            for budget in budgets['Budgets']:
                print(budget)
                if len(budget['CostFilters']) == 0:# IF null then add a none value for Crawler
                    budget.update({'CostFilters': {'Filter': ['None']}})
                dataJSONData = json.dumps(budget, cls=DateTimeEncoder)
                f.write(dataJSONData)
                f.write("\n")
    s3_upload()
    start_crawler()

def s3_upload():

    d = datetime.datetime.now()
    month = d.strftime("%m")
    year = d.strftime("%Y")
    dt_string = d.strftime("%d%m%Y-%H%M%S")

    today = datetime.date.today()
    year = today.year
    month = today.month
    try:
        S3BucketName = os.environ["BUCKET_NAME"]
        DestinationPrefix = os.environ["PATH"]
        s3 = boto3.client('s3', 
                            config=Config(s3={'addressing_style': 'path'}))
        s3.upload_file(f'/tmp/data.json', S3BucketName, f"{DestinationPrefix}/year={year}/month={month}/budgets-{dt_string}.json")
        print(f"Budget data in s3 {S3BucketName}")
    except Exception as e:
        # Send some context about this error to Lambda Logs
        logging.warning("%s" % e)

def start_crawler():
    glue_client = boto3.client("glue")
    Crawler_Name = os.environ["CRAWLER_NAME"]
    try:
        glue_client.start_crawler(Name=Crawler_Name)
        print(f"{Crawler_Name} has been started")
    except Exception as e:
        # Send some context about this error to Lambda Logs
        logging.warning("%s" % e)
