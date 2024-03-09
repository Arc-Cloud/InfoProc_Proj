import boto3
from botocore.exceptions import ClientError
import logging

def create_dynamodb_resource(region_name='us-east-1'):
    """Create a DynamoDB resource."""
    try:
        dynamodb = boto3.resource('dynamodb', region_name=region_name)
        return dynamodb
    except ClientError as e:
        logging.error(e)
        return None

def create_table(dynamodb=None):
    """Create a DynamoDB table."""
    if dynamodb is None:
        dynamodb = create_dynamodb_resource()

    if dynamodb is None:
        logging.error("Could not create DynamoDB resource.")
        return None

    try:
        table = dynamodb.create_table(
            TableName='Leaderboard',
            KeySchema=[
                {
                    'AttributeName': 'PlayerId',
                    'KeyType': 'HASH'  # Partition key
                },
            ],
           AttributeDefinitions=[
                {
                    'AttributeName': 'PlayerId',
                    'AttributeType': 'S'
                },
                {
                    'AttributeName': 'HighScore',
                    'AttributeType': 'N'  # Score as a number
                }
            ],
            ProvisionedThroughput={
                'ReadCapacityUnits': 5,
                'WriteCapacityUnits': 5
            }
        )
        return table
    except ClientError as e:
        logging.error(e)
        return None

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    table = create_table()
    if table is not None:
        logging.info(f"Table status: {table.table_status}")
    else:
        logging.error("Failed to create the table.")