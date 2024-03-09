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
    
if __name__ == '__main__':
    delete_leaderboard_table()
    print("Leaderboard table deleted.")