"""
http://docs.aws.amazon.com/amazondynamodb/latest/gettingstartedguide/GettingStarted.JsShell.html#GettingStarted.JsShell.Prereqs.Download
http://docs.aws.amazon.com/amazondynamodb/latest/gettingstartedguide/GettingStarted.Python.html

"""
import boto3
import json

# - http://boto3.readthedocs.io/en/latest/guide/configuration.html
# - Please change IAM policies first
# - http://stackoverflow.com/questions/34784804/aws-dynamodb-issue-user-is-not-authorized-to-perform-dynamodbputitem-on-resou

if False:
    credentials = json.load(open('../aws/credentials.json'))
    dynamodb = boto3.client('dynamodb', aws_access_key_id=credentials['AWS_ACCESS_KEY_ID'],
                            aws_secret_access_key=credentials['AWS_SECRET_ACCESS_KEY'])
dynamodb = boto3.client('dynamodb')

table = dynamodb.create_table(
    TableName='Movies',
    KeySchema=[
        {
            'AttributeName': 'year',
            'KeyType': 'HASH'  # Partition key
        },
        {
            'AttributeName': 'title',
            'KeyType': 'RANGE'  # Sort key
        }
    ],
    AttributeDefinitions=[
        {
            'AttributeName': 'year',
            'AttributeType': 'N'
        },
        {
            'AttributeName': 'title',
            'AttributeType': 'S'
        },

    ],
    ProvisionedThroughput={
        'ReadCapacityUnits': 10,
        'WriteCapacityUnits': 10
    }
)
