# File: db_connect.py
import os
from pymongo import MongoClient
from dotenv import load_dotenv

load_dotenv()

# Connect to MongoDB
# Ensure you have a running MongoDB instance or use the default localhost
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["agentx_db"]

# Collections
telematics_col = db["telematics_logs"]
appointments_col = db["service_appointments"]

def log_telematics(data: dict):
    """Stores raw sensor data stream."""
    # Ensure data is a dictionary
    if isinstance(data, dict):
        return telematics_col.insert_one(data)
    print("Error: Data to log must be a dictionary.")

def create_appointment(booking_data: dict):
    """Stores confirmed service bookings."""
    return appointments_col.insert_one(booking_data)
