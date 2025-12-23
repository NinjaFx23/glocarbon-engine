from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
from database import add_project, get_all_projects
from models import ProjectSubmission
# 1. IMPORT CORS
from fastapi.middleware.cors import CORSMiddleware 

app = FastAPI()

# 2. ADD THE PERMISSION SLIP (Allow your app to talk to the server)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows ALL origins (Mobile apps, Localhost, etc.)
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods (POST, GET, etc.)
    allow_headers=["*"],
)

# ... The rest of your code (endpoints) stays the same below ...

# 1. Initialize the App
app = FastAPI(title="GloCarbon Engine API", version="1.0.0")

# --- MATH LOGIC (Internal Helpers) ---

def _calculate_grassland_credits(raw_specs):
    specs = GrasslandSpecs(**raw_specs) 
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

# --- API ENDPOINTS (The Public Doors) ---

@app.on_event("startup")
def startup_event():
    """Run this when the server turns on"""
    init_db()
    print("🚀 GloCarbon API is listening...")

@app.get("/")
def home():
    """Simple check to see if we are online"""
    return {"status": "online", "message": "GloCarbon AI Engine is Ready 🌍"}

@app.get("/market")
def view_market():
    """Fetch all listed projects"""
    listings = get_marketplace_listings()
    # Format the data for the web
    results = []
    for item in listings:
        results.append({
            "id": item[0],
            "project_name": item[1],
            "type": item[2],
            "credits": item[3],
            "status": item[4]
        })
    return {"count": len(results), "projects": results}

@app.post("/verify_project")
def submit_project(project: ProjectRequest):
    """
    Accepts JSON data, validates it, calculates credits, and saves it.
    """
    print(f"📥 Received project: {project.project_name}")
    
    total_credits = 0
    details = []

    try:
        # Analyze each zone using the Pydantic models automatically!
        for zone in project.ecosystems:
            credits = 0
            if zone.type == 'grassland':
                credits = _calculate_grassland_credits(zone.specs)
            elif zone.type == 'wetland':
                credits = _calculate_wetland_credits(zone.specs)
            elif zone.type == 'forest':
                credits = _calculate_forest_credits(zone.specs)
            
            total_credits += credits
            details.append({"type": zone.type, "generated_credits": credits})

        # Save to DB
        save_project(project, total_credits)

        return {
            "status": "Verified",
            "project_name": project.project_name,
            "total_credits": total_credits,
            "breakdown": details
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))