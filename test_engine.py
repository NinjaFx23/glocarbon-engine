# File: test_engine.py
import json
import datetime

# 👇 THIS LINE CHANGED: We now import from 'app'
from app import process_carbon_data 

def generate_dummy_data():
    data = {
        "timestamp": str(datetime.datetime.now()),
        "source_id": "factory_01",
        "metrics": {
            "electricity_usage": 150.5, 
            "transport_fuel": 40.0      
        }
    }
    return data

if __name__ == "__main__":
    print("--- 🧪 Starting GloCarbon Interface Test ---")
    
    # 1. Generate Data
    payload = generate_dummy_data()
    print("📦 Payload Generated.")

    # 2. Send to Engine
    print("📡 Sending data to Engine...")
    
    # This calls the function inside app.py
    result = process_carbon_data(payload)
    
    print(f"\n✅ Calculation Received: {result} kgCO2 total.")
    print("--- 🏁 Test Complete ---")