import boto3
import os

client = boto3.client('budgets')

account_id = os.environ['account_id']
paginator = client.get_paginator("describe_budgets") #Paginator for a large list of accounts
response_iterator = paginator.paginate(AccountId=account_id)

for account in response_iterator:
    print(account)