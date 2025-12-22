# File: app.py
# GloCarbon Multi-Ecosystem Valuation Engine (Verra Aligned)

def _calculate_grassland_credits(specs):
    """
    Implements logic from Verra VM0042 (Improved Agricultural Land Management).
    Focus: Soil Organic Carbon (SOC) sequestration.
    """
    area = specs.get('area_hectares', 0)
    health = specs.get('health_index', 0)
    
    # Verra Logic: Deduct for leakage (e.g., livestock methane)
    livestock_density = specs.get('livestock_density', 0) # Units per hectare
    methane_penalty = livestock_density * 0.5 # Simplified penalty factor
    
    base_rate = 3.5 # tonnes/ha (Healthy Savannah)
    gross_credits = area * base_rate * health
    
    # Net Credits = Gross Sequestration - Methane Leakage
    net_credits = max(0, gross_credits - (area * methane_penalty))
    
    return {
        "type": "Grassland (VM0042)",
        "credits": round(net_credits, 2),
        "note": f"Penalty applied for {livestock_density} livestock/ha"
    }

def _calculate_wetland_credits(specs):
    """
    Implements logic from Verra VM0033 (Tidal Wetland/Seagrass Restoration).
    Focus: Blue Carbon (very high sequestration).
    """
    area = specs.get('area_hectares', 0)
    
    # Wetlands sequester significantly more carbon than forests/grass
    base_rate = 8.0 # tonnes/ha
    
    total_credits = area * base_rate
    return {
        "type": "Wetland/Blue Carbon (VM0033)",
        "credits": round(total_credits, 2),
        "note": "High-value ecosystem detected"
    }

def _calculate_forest_credits(specs):
    """
    Implements logic from Verra VM0007 (REDD+ / Forestry).
    Focus: Above-ground biomass.
    """
    area = specs.get('area_hectares', 0)
    tree_density = specs.get('tree_density', 0) # Trees per hectare
    
    # Simplified biomass formula
    biomass_per_tree = 0.02 # tonnes CO2
    total_credits = area * tree_density * biomass_per_tree
    
    return {
        "type": "Forestry/Agroforestry (VM0007)",
        "credits": round(total_credits, 2),
        "note": f"Density: {tree_density} trees/ha"
    }

def process_project_valuation(project_data):
    """
    Main Router: Breaks a project down into ecosystems and aggregates value.
    """
    project_name = project_data.get('project_name')
    print(f"\n🌍 ENGINE: Starting Holistic Analysis for '{project_name}'...")
    
    ecosystems = project_data.get('ecosystems', [])
    total_credits = 0
    report = []
    
    for zone in ecosystems:
        land_type = zone.get('type')
        specs = zone.get('specs')
        
        # ROUTING LOGIC: AI decides which standard to apply
        if land_type == 'grassland':
            result = _calculate_grassland_credits(specs)
        elif land_type == 'wetland':
            result = _calculate_wetland_credits(specs)
        elif land_type == 'forest':
            result = _calculate_forest_credits(specs)
        else:
            result = {"type": "Unknown", "credits": 0, "note": "No methodology found"}
            
        # Add to totals
        total_credits += result['credits']
        report.append(result)
        
        print(f"   Detected {result['type']}: +{result['credits']} VCUs ({result['note']})")

    print(f"   💎 GRAND TOTAL: {total_credits:.2f} Verified Carbon Units (VCUs)")
    return total_credits

# Entry point
def main():
    print("GloCarbon Multi-Ecosystem Engine is Online! 🌍🔄")

if __name__ == "__main__":
    main()