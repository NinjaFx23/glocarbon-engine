# File: app.py
import json

# 1. This is the logic function (The "Brain")
def process_carbon_data(data_payload):
    """
    Receives data, calculates carbon footprint, and returns a result.
    """
    print(f"\n⚙️  ENGINE: Processing data from {data_payload.get('source_id')}...")
    
    # Extract metrics from the input data
    metrics = data_payload.get('metrics', {})
    elec = metrics.get('electricity_usage', 0)
    fuel = metrics.get('transport_fuel', 0)
    
    # --- BASIC CALCULATION LOGIC ---
    # Electricity factor: 0.5 kgCO2 per kWh
    # Fuel factor: 2.3 kgCO2 per Liter
    carbon_footprint = (elec * 0.5) + (fuel * 2.3)
    
    # Print the breakdown so we can see it working
    print(f"   ⚡ Electricity Impact: {elec * 0.5} kgCO2")
    print(f"   ⛽ Fuel Impact:       {fuel * 2.3} kgCO2")
    print(f"   📉 TOTAL FOOTPRINT:   {carbon_footprint} kgCO2")
    
    return carbon_footprint

# 2. Main Entry Point
def main():
    print("GloCarbon AI Engine is Online! 🌍🚀")

if __name__ == "__main__":
    main()