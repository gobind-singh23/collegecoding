from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient('mongodb://localhost:27017/')
db = client['collegecoding']

# Create users collection with validation
db.create_collection("users", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["userHandle", "organization", "rating", "college", "lastSubmissionTime", "maxRating"],
        "properties": {
            "userHandle": {"bsonType": "string"},
            "organization": {"bsonType": "string"},
            "rating": {"bsonType": "int"},
            "college": {"bsonType": "string"},
            "lastSubmissionTime": {"bsonType": "date"},
            "maxRating": {"bsonType": "int"}
        }
    }
})

# Create contests collection
db.create_collection("contests", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["contestID", "name", "div", "time"],
        "properties": {
            "contestID": {"bsonType": "string"},
            "name": {"bsonType": "string"},
            "div": {"bsonType": "string"},
            "time": {"bsonType": "date"}
        }
    }
})

# Create problems collection
db.create_collection("problems", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["problemID", "tag", "organization", "solves"],
        "properties": {
            "problemID": {"bsonType": "string"},
            "tag": {"bsonType": "string"},
            "organization": {"bsonType": "string"},
            "solves": {"bsonType": "int"}
        }
    }
})

# Create tags collection
db.create_collection("tags", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["userHandle", "div", "dp", "greedy", "graph", "sorting", "maths"],
        "properties": {
            "userHandle": {"bsonType": "string"},
            "div": {"bsonType": "string"},
            "dp": {"bsonType": "int"},
            "greedy": {"bsonType": "int"},
            "graph": {"bsonType": "int"},
            "sorting": {"bsonType": "int"},
            "maths": {"bsonType": "int"}
        }
    }
})

# Create rating collection
db.create_collection("rating", validator={
    "$jsonSchema": {
        "bsonType": "object",
        "required": ["userID", "contestID", "div", "oldRating", "newRating"],
        "properties": {
            "userID": {"bsonType": "string"},
            "contestID": {"bsonType": "string"},
            "div": {"bsonType": "string"},
            "oldRating": {"bsonType": "int"},
            "newRating": {"bsonType": "int"}
        }
    }
})

print("Database and collections created successfully!")
