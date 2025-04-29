from pymongo import MongoClient, UpdateOne

def get_database(db_name):
    client = MongoClient("mongodb://localhost:27017/")
    return client[db_name]

def store_valid_participants_in_users(valid_participants, db_name, collection_name):
    db = get_database(db_name)
    users_collection = db[collection_name]

    bulk_operations = []

    for participant in valid_participants:
        if not isinstance(participant, dict):
            print(f"Skipping non-dictionary participant: {participant}")
            continue
        if 'userHandle' not in participant:
            print(f"Skipping participant due to missing 'userHandle': {participant}")
            continue

        filter_query = {'userHandle': participant['userHandle']}
        update_query = {'$set': participant}

        # REAL UpdateOne object
        operation = UpdateOne(filter_query, update_query, upsert=True)
        bulk_operations.append(operation)

    if bulk_operations:
        result = users_collection.bulk_write(bulk_operations)
        print(f"Bulk write result: {result.bulk_api_result}")
    else:
        print("No valid participants to update.")

def store_participants_in_temp_collection(valid_participants, db_name, temp_collection_name):
    db = get_database(db_name)
    temp_collection = db[temp_collection_name]

    if valid_participants:
        temp_collection.insert_many(valid_participants)
        print(f"Inserted {len(valid_participants)} participants into temporary collection.")

def delete_temp_collection(db_name, temp_collection_name):
    db = get_database(db_name)
    if temp_collection_name in db.list_collection_names():
        db.drop_collection(temp_collection_name)
        print(f"Temporary collection {temp_collection_name} deleted.")
    else:
        print(f"Temporary collection {temp_collection_name} does not exist.")
