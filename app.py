# File: app.py
from models import ProjectRequest, GrasslandSpecs, WetlandSpecs, ForestSpecs
from database import init_db, save_project 

# --- MATH LOGIC ---

def _calculate_grassland_credits(raw_specs):
    # 1. Validate
    specs = GrasslandSpecs(**raw_specs) 
    
    # 2. Calculate
    methane_penalty = specs.livestock_density * 0.5
    base_rate = 3.5
    gross = specs.area_hectares * base_rate * specs.health_index
    net = max(0, gross - (specs.area_hectares * methane_penalty))
    
    return round(net, 2)

def _calculate_wetland_credits(raw_specs):
    specs = WetlandSpecs(**raw_specs)
    base_rate = 8.0
    return round(specs.area_hectares * base_rate, 2)

def _calculate_forest_credits(raw_specs):
    specs = ForestSpecs(**raw_specs)
    biomass_per_tree = 0.02
    return round(specs.area_hectares * specs.tree_density * biomass_per_tree, 2)

# --- MAIN ROUTER ---

def process_project_valuation(json_data):
    """
    Receives raw JSON, validates it against blueprints, calculates credits,
    and saves the result to the database.
    """
    print("\n🛡️  SECURITY: Validating input data...")
    
    try:
        # STEP 1: Check the overall structure
        project = ProjectRequest(**json_data)
        print(f"✅ Data looks good! Analyzing '{project.project_name}'...")
        
        total_credits = 0
        
        # STEP 2: Analyze each zone
        for zone in project.ecosystems:
            credits = 0
            
            if zone.type == 'grassland':
                credits = _calculate_grassland_credits(zone.specs)
            elif zone.type == 'wetland':
                credits = _calculate_wetland_credits(zone.specs)
            elif zone.type == 'forest':
                credits = _calculate_forest_credits(zone.specs)
                
            print(f"   > Found {zone.type}: +{credits} VCUs")
            total_credits += credits
            
        print(f"💎 TOTAL VERIFIED CREDITS: {total_credits}")

        # STEP 3: Save to Database
        save_project(project, total_credits)
        
        return total_credits

    except Exception as e:
        print(f"\n❌ DATA REJECTED: {e}")
        return None

# Entry point
def main():
    # Initialize the DB when the app starts
    init_db()
    print("GloCarbon Multi-Ecosystem Engine is Online! 🌍🔄")

if __name__ == "__main__":
    main()