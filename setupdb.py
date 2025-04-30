from pymongo import MongoClient, ASCENDING

# Connect to MongoDB (update with your connection URI)
client = MongoClient("mongodb://localhost:27017/")
db = client['coding_platform']

# 1. Users collection
users = db['users']
users.create_index([('handle', ASCENDING)], unique=True)

# 2. Contests collection
contests = db['contests']
contests.create_index([('contestId', ASCENDING)], unique=True)

# 3. Tags collection
tags = db['tags']
# Composite PK: (handle, division)
tags.create_index([('handle', ASCENDING), ('division', ASCENDING)], unique=True)

# 4. Rating collection
rating = db['rating']
# Composite PK: (handle, contestId)
rating.create_index([('handle', ASCENDING), ('contestId', ASCENDING)], unique=True)

# 5. Problems collection
problems = db['problems']
problems.create_index([('problemID', ASCENDING)], unique=True)

print("MongoDB schema setup completed with indexes.")
