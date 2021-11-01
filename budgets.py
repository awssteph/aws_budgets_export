import boto3
import os
import json#
import datetime
from json import JSONEncoder

# subclass JSONEncoder
class DateTimeEncoder(JSONEncoder):
    # Override the default method
    def default(self, obj):
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()

def lambda_handler(event, context):
    client = boto3.client('budgets')

    account_id = os.environ['account_id']
    paginator = client.get_paginator("describe_budgets") #Paginator for a large list of accounts
    response_iterator = paginator.paginate(AccountId=account_id)

    #import pdb; pdb.set_trace()
    with open("data.json", "w") as f:
        for budgets in response_iterator:
            for budget in budgets['Budgets']:
                print(budget)
                dataJSONData = json.dumps(budget, cls=DateTimeEncoder)
                f.write(dataJSONData)
                f.write("\n")
