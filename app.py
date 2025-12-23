from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# --- IMPORTS FROM YOUR FILES ---
# We use ProjectRequest because that is what your models.py uses!
from models import ProjectRequest, GrasslandSpecs, WetlandSpecs, ForestSpecs
from database import add_project, get_all_projects

# 1. INITIALIZE THE APP
app = FastAPI(title="GloCarbon Engine API", version="1.0.0")

# 2. ADD THE PERMISSION SLIP (CORS)
# This allows your mobile app to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ALL origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MATH LOGIC (Internal Helpers) ---

def _calculate_grassland_credits(raw_specs):
    # Convert the dictionary (raw_specs) into the Pydantic model
    specs = GrasslandSpecs(**raw_specs) 
    
    # Logic: Cows reduce credits (methane), Health increases them
    methane_penalty = specs.livestock_density * 0.5
    base_rate = 3.5
    gross = specs.area_hectares * base_rate * specs.health_index
    net = max(0, gross - (specs.area_hectares * methane_penalty))
    return round(net, 2)

def _calculate_wetland_credits(raw_specs):
    specs = WetlandSpecs(**raw_specs)
    # Logic: Wetlands generate high credits (8.0 base)
    base_rate = 8.0
    return round(specs.area_hectares * base_rate, 2)

def _calculate_forest_credits(raw_specs):
    specs = ForestSpecs(**raw_specs)
    # Logic: Tree density matters
    biomass_per_tree = 0.02
    return round(specs.area_hectares * specs.tree_density * biomass_per_tree, 2)

# --- API ENDPOINTS ---

@app.on_event("startup")
def startup_event():
    print("🚀 GloCarbon API is listening...")

@app.get("/")
def home():
    return {"status": "online", "message": "GloCarbon AI Engine is Ready 🌍"}

@app.get("/market")
def view_market():
    listings = get_all_projects()
    return {"count": len(listings), "projects": listings}

@app.post("/verify_project")
def submit_project(submission: ProjectRequest):
    """
    Accepts ProjectRequest (from your models.py), validates it, calculates credits.
    """
    print(f"📥 Received project: {submission.project_name}")
    
    total_credits = 0.0
    details = []

    try:
        # Analyze each zone
        for zone in submission.ecosystems:
            credits = 0.0
            
            # Select the right math formula based on type
            if zone.type == 'grassland':
                # Handle optional livestock if missing
                if 'livestock_density' not in zone.specs: zone.specs['livestock_density'] = 0.0
                credits = _calculate_grassland_credits(zone.specs)
                
            elif zone.type == 'wetland':
                credits = _calculate_wetland_credits(zone.specs)
                
            elif zone.type == 'forest':
                credits = _calculate_forest_credits(zone.specs)
            
            total_credits += credits
            details.append({"type": zone.type, "generated_credits": credits})

        # Prepare data for Database
        project_data = submission.model_dump()
        project_data["total_credits"] = round(total_credits, 2)
        project_data["breakdown"] = details
        project_data["status"] = "Verified"

        # Save to DB
        add_project(project_data)

        return {
            "status": "Verified",
            "project_name": submission.project_name,
            "total_credits": round(total_credits, 2),
            "breakdown": details,
            "value_estimate": round(total_credits * 15, 2)
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))