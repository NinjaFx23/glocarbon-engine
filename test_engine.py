import datetime
from app import process_project_valuation

def generate_complex_land_data():
    return {
        "timestamp": str(datetime.datetime.now()),
        "project_owner": "Mara_North_Conservancy",
        "project_name": "Mara Mixed-Use Conservation Project",
        # The AI now accepts a LIST of ecosystems found on the property
        "ecosystems": [
            {
                "type": "grassland",
                "specs": {
                    "area_hectares": 400.0,
                    "health_index": 0.9,
                    "livestock_density": 1.2 # Cows per hectare (Reduces credits!)
                }
            },
            {
                "type": "wetland",
                "specs": {
                    "area_hectares": 50.0, # Small swamp area
                    "water_level": "stable"
                }
            },
            {
                "type": "forest",
                "specs": {
                    "area_hectares": 50.0, # Patches of Acacia
                    "tree_density": 150 # Trees per hectare
                }
            }
        ]
    }

if __name__ == "__main__":
    print("--- 🧪 Starting GloCarbon Holistic Audit ---")
    
    data = generate_complex_land_data()
    process_project_valuation(data)
    
    print("--- 🏁 Audit Complete ---")