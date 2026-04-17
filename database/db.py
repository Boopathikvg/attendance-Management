from pymongo import MongoClient




client = MongoClient("mongodb://localhost:27017/")
db = client["attendance_db"]
users = db["users"]
attendance = db["attendance"]