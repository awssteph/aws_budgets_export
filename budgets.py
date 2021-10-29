import boto3
import os
from lambda_base import generate_csv

client = boto3.client('budgets')

account_id = os.environ['account_id']
paginator = client.get_paginator("describe_budgets") #Paginator for a large list of accounts
response_iterator = paginator.paginate(AccountId=account_id)
for budgets in response_iterator:
    #import pdb; pdb.set_trace()
    csv = generate_csv(budgets['Budgets'])
file = open("budget.csv", "w")
file.write(csv)
file.close()

# for budgets in response_iterator:
#     for budget in budgets['Budgets']:
#         print(budget)
#         budget['BudgetName']
#         budget['BudgetLimit']['Amount']
