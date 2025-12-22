# File: view_market.py
from database import get_marketplace_listings

def show_marketplace():
    print("\n--- 🛒 GloCarbon Marketplace: Available Projects ---")
    print(f"{'ID':<5} | {'Project Name':<30} | {'Type':<15} | {'Credits (VCU)':<15} | {'Status'}")
    print("-" * 90)
    
    # 1. Fetch data from the "Vault" (Database)
    listings = get_marketplace_listings()
    
    if not listings:
        print("   (No projects listed yet)")
    
    # 2. Display each project nicely
    for item in listings:
        # item is a tuple: (id, name, type, credits, status)
        p_id, name, p_type, credits, status = item
        print(f"{p_id:<5} | {name:<30} | {p_type:<15} | {credits:<15} | {status}")

    print("-" * 90)
    print("--- End of Listings ---\n")

if __name__ == "__main__":
    show_marketplace()