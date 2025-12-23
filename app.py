from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import io

# Import database functions
from database import save_project, init_db

app = FastAPI(title="GloCarbon AI Engine", version="2.0.0")

# CORS (Permission Slip)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- THE "REAL" AI LOGIC ---
def analyze_vegetation_health(image_bytes):
    """
    1. Opens the image.
    2. Converts to standard RGB.
    3. Calculates how 'Green' the image is (Greenness Index).
    This is the placeholder where we will plug in the MindSpore model later.
    """
    try:
        # Open image from bytes
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img = img.resize((224, 224)) # Resize for standard AI input
        
        # Convert to math array
        data = np.array(img)
        
        # Simple Algorithm: Calculate Green Ratio vs Red/Blue
        # (Green Channel - Red Channel) + (Green Channel - Blue Channel)
        # This is a basic "Excess Green" index used in agriculture.
        r, g, b = data[:,:,0], data[:,:,1], data[:,:,2]
        
        # Avoid division by zero
        green_score = np.mean(g)
        total_intensity = np.mean(r) + np.mean(g) + np.mean(b)
        
        health_index = 0.0
        if total_intensity > 0:
            health_index = green_score / (total_intensity / 3)
            
        # Normalize to 0.0 - 1.0 range (Simple heuristic)
        # If green is dominant (>1.0), it's healthy.
        normalized_health = min(max((health_index - 0.8) * 2, 0.1), 1.0)
        
        return round(normalized_health, 2)
        
    except Exception as e:
        print(f"AI Error: {e}")
        return 0.5 # Default fallback

# --- API ENDPOINTS ---

@app.on_event("startup")
def startup_event():
    init_db()

@app.get("/")
def home():
    return {"status": "Active", "mode": "Computer Vision 📸"}

@app.post("/scan_plot")
async def scan_plot(file: UploadFile = File(...)):
    """
    Receives an IMAGE file, runs analysis, and returns credits.
    """
    print(f"📸 Receiving Image: {file.filename}")
    
    # 1. READ THE IMAGE
    contents = await file.read()
    
    # 2. RUN AI ANALYSIS
    # (This replaces the random inputs we used before)
    health_score = analyze_vegetation_health(contents)
    
    # 3. CALCULATE CREDITS based on AI finding
    # We assume a standard 50 Hectare plot for the scan prototype
    area_hectares = 50 
    base_rate = 3.5 # Grassland
    
    total_credits = area_hectares * base_rate * health_score
    value = total_credits * 15
    
    # 4. SAVE TO DB (Simplified for the scan)
    # Note: You might want to expand database.py to handle images later
    
    return {
        "status": "Scanned",
        "file_name": file.filename,
        "ai_health_index": health_score,
        "total_credits": round(total_credits, 2),
        "value_estimate": round(value, 2)
    }