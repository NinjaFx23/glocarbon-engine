# File: test_engine.py
from app import process_project_valuation

def generate_bad_data():
    return {
        "project_owner": "Lazy_User",
        "project_name": "Bad", # Too short! (Should fail)
        "ecosystems": [
            {
                "type": "grassland",
                "specs": {
                    "area_hectares": 100, 
                    # MISSING 'health_index' -> Should fail!
                }
            }
        ]
    }

def generate_good_data():
    return {
        "project_owner": "Serious_Rancher",
        "project_name": "Valid Savannah Project",
        "ecosystems": [
            {
                "type": "grassland",
                "specs": {
                    "area_hectares": 100,
                    "health_index": 0.8,
                    "livestock_density": 0.5
                }
            }
        ]
    }

if __name__ == "__main__":
    print("--- 🧪 TEST 1: Sending BAD Data ---")
    process_project_valuation(generate_bad_data())
    
    print("\n--- 🧪 TEST 2: Sending GOOD Data ---")
    process_project_valuation(generate_good_data())