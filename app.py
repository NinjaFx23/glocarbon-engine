from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List

# --- IMPORTS (Matched to your files) ---
from models import ProjectRequest, GrasslandSpecs, WetlandSpecs, ForestSpecs
from database import save_project, get_marketplace_listings, init_db

# 1. INITIALIZE THE APP
app = FastAPI(title="GloCarbon Engine API", version="1.0.0")

# 2. PERMISSION SLIP (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MATH LOGIC ---

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

# --- API ENDPOINTS ---

@app.on_event("startup")
def startup_event():
    """Initialize the database when the server starts"""
    init_db()
    print("🚀 GloCarbon API is listening...")

@app.get("/")
def home():
    return {"status": "online", "message": "GloCarbon AI Engine is Ready 🌍"}

@app.get("/market")
def view_market():
    # Get raw rows (tuples) from database
    rows = get_marketplace_listings()
    
    # Convert tuples to JSON dictionary
    results = []
    for item in rows:
        results.append({
            "id": item[0],
            "project_name": item[1],
            "type": item[2],
            "credits": item[3],
            "status": item[4]
        })
    return {"count": len(results), "projects": results}

@app.post("/verify_project")
def submit_project(submission: ProjectRequest):
    print(f"📥 Received project: {submission.project_name}")
    
    total_credits = 0.0
    details = []

    try:
        # 1. Calculate Credits
        for zone in submission.ecosystems:
            credits = 0.0
            
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

        final_credits = round(total_credits, 2)

        # 2. Save to DB (Passing the 'submission' object directly as your DB expects)
        save_project(submission, final_credits)

        # 3. Return Success
        return {
            "status": "Verified",
            "project_name": submission.project_name,
            "total_credits": final_credits,
            "breakdown": details,
            "value_estimate": round(final_credits * 15, 2)
        }

    except Exception as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))