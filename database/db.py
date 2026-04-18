from pymongo import MongoClient
from pymongo.server_api import ServerApi

uri = "mongodb+srv://employee_db:Boopathi%401307@employee-management.1qkhbku.mongodb.net/?retryWrites=true&w=majority"

client = MongoClient(uri)
db = client["employee_db"]
users = db["users"]
attendance = db["attendance"]
leave_s = db["leave"]


