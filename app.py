from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import io

# Import database functions
from database import save_project, init_db, get_marketplace_listings

app = FastAPI(title="GloCarbon AI Engine", version="2.0.0")

# PERMISSION SLIP (CORS) - Allows your Netlify app to talk to this server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 🧠 THE AI VISION LOGIC ---
def analyze_green_index(image_bytes):
    """
    Reads the raw image, looks at pixels, and calculates 'Greenness'.
    """
    try:
        # 1. Open image from bytes
        img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
        img = img.resize((224, 224)) # Resize for consistency
        
        # 2. Convert to numbers (Matrix)
        data = np.array(img)
        
        # 3. Separate Color Channels
        red = data[:,:,0].astype(float)
        green = data[:,:,1].astype(float)
        blue = data[:,:,2].astype(float)
        
        # 4. Calculate "Excess Green Index" (2*G - R - B)
        # If a pixel is very green, this number is high.
        excess_green = 2 * green - red - blue
        
        # 5. Count Healthy Pixels
        green_pixels = np.sum(excess_green > 0)
        total_pixels = excess_green.size
        
        # 6. Generate Score (0.0 to 1.0)
        ratio = green_pixels / total_pixels
        
        # Boost score slightly for demo (so standard grass looks good)
        health_score = min(max(ratio * 1.5, 0.1), 0.99)
        
        return round(health_score, 2)
        
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

@app.get("/market")
def view_market():
    rows = get_marketplace_listings()
    results = []
    for item in rows:
        results.append({
            "id": item[0], "project_name": item[1], 
            "type": item[2], "credits": item[3], "status": item[4]
        })
    return {"count": len(results), "projects": results}

# --- THE NEW AI ENDPOINT ---
@app.post("/scan_plot")
async def scan_plot(file: UploadFile = File(...)):
    print(f"📸 Receiving Image: {file.filename}")
    
    # 1. READ IMAGE
    contents = await file.read()
    
    # 2. RUN AI ANALYSIS
    health_score = analyze_green_index(contents)
    print(f"🧠 AI Analysis Complete. Health Score: {health_score}")
    
    # 3. CALCULATE CREDITS
    # We assume a standard 50 Hectare plot for this demo
    area = 50
    base_rate = 3.5 # Grassland rate
    
    total_credits = area * base_rate * health_score
    value = total_credits * 15
    
    return {
        "status": "Scanned",
        "file_name": file.filename,
        "ai_health_index": health_score,
        "total_credits": round(total_credits, 2),
        "value_estimate": round(value, 2)
    }