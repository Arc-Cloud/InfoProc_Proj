import boto3

def create_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.create_table(
        TableName='Leaderboard',
        KeySchema=[
            {
                'AttributeName': 'SessionId',
                'KeyType': 'HASH'  # Partition key
            },
            {
                'AttributeName': 'PlayerId',
                'KeyType': 'RANGE'  # Sort key
            }
        ],
        AttributeDefinitions=[
            {
                'AttributeName': 'SessionId',
                'AttributeType': 'N'
            },
            {
                'AttributeName': 'PlayerId',
                'AttributeType': 'N'
            }
        ],
        ProvisionedThroughput={
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    )
    return table

def EntryPoint(SessionId, PlayerId):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('Leaderboard')
    try:
        response = table.put_item(
            Item={
                'SessionId': SessionId,
                'PlayerId': PlayerId
            }
        )
        return response
    except Exception as e:
        print(f"Error updating leaderboard: {e}")
        # Handle exception appropriately

def update_player_stats(SessionId, PlayerId, ScoreIncrement=0, KillsIncrement=0, DeathsIncrement=0, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('Leaderboard')

    try:
        response = table.update_item(
            Key={
                'SessionId': SessionId,
                'PlayerId': PlayerId
            },
            # increments the stats for each stats the if not exists basically check if the stats exist or not if its not then it will isntantiate it first
            UpdateExpression="SET Score = if_not_exists(Score, :start) + :score, Kills = if_not_exists(Kills, :start) + :kills, Deaths = if_not_exists(Deaths, :start) + :deaths",
            ExpressionAttributeValues={
                ':score': ScoreIncrement,
                ':kills': KillsIncrement,
                ':deaths': DeathsIncrement,
                ':start': 0  # Start value if the attribute does not exist
            },
            ReturnValues="UPDATED_NEW"
        )
        return response
    except ClientError as e:
        print(f"Error updating player stats: {e}")
        # Handle the exception appropriately
        return None

def get_player_stats(SessionId, PlayerId, dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('Leaderboard')

    try:
        response = table.get_item(
            Key={
                'SessionId': SessionId,
                'PlayerId': PlayerId
            }
        )
        # Check if 'Item' key exists in the response to handle non-existent entries
        # this thing returns a dictionary
        if 'Item' in response:
            return response['Item']
        else:
            print("Player stats not found.")
            return None
    except ClientError as e:
        print(f"Error retrieving player stats: {e}")
        # Handle the exception appropriately
        return None


# for deleting stff duh
def delete_leaderboard_table(dynamodb=None):
    if not dynamodb:
        dynamodb = boto3.resource('dynamodb', region_name='us-east-1')

    table = dynamodb.Table('Leaderboard')

    try:
        response = table.delete()
        print("Table deletion initiated successfully.")
        return response
    except ClientError as e:
        print(f"Error deleting table: {e}")
        # Handle the exception appropriately
        return None
