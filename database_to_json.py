from pymongo import MongoClient
from bson import json_util
import json
from collections import defaultdict

client = MongoClient("mongodb://localhost:27017/")
db = client["coding_platform"]

def infer_bson_type(value):
    if isinstance(value, str):
        return "string"
    elif isinstance(value, bool):
        return "bool"
    elif isinstance(value, int):
        return "int"
    elif isinstance(value, float):
        return "double"
    elif isinstance(value, list):
        item_types = {infer_bson_type(item) for item in value}
        return {"bsonType": "array", "items": {"bsonType": list(item_types)[0] if item_types else "string"}}
    elif isinstance(value, dict):
        return "object"
    else:
        return "string"

schema = {
    "collections": [],
    "version": 1
}

for name in db.list_collection_names():
    coll = db[name]
    sample_doc = coll.find_one()
    
    # Document schema inference
    doc_schema = {"properties": {}}
    if sample_doc:
        for field, value in sample_doc.items():
            doc_schema["properties"][field] = {"bsonType": infer_bson_type(value)}

    # Indexes
    indexes = []
    unique_indexes = []
    for index in coll.list_indexes():
        index_dict = {
            "key": dict(index["key"])
        }
        indexes.append(index_dict)
        if index.get("unique"):
            unique_indexes.append(index_dict)

    schema["collections"].append({
        "name": name,
        "indexes": indexes,
        "uniqueIndexes": unique_indexes,
        "document": doc_schema
    })

with open("db_schema.json", "w") as f:
    json.dump(schema, f, indent=2, default=json_util.default)
