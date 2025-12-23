from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image
import numpy as np
import io
import joblib # The tool to load the brain
import os

# Import database functions
from database import save_project, init_db, get_marketplace_listings

app = FastAPI(title="GloCarbon AI Engine", version="3.0.0")

# PERMISSION SLIP (CORS)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- 🧠 LOAD THE TRAINED BRAIN ---
MODEL_FILE = "glocarbon_brain.pkl"
ai_model = None

@app.on_event("startup")
def startup_event():
    global ai_model
    init_db()
    
    # Try to load the brain file
    if os.path.exists(MODEL_FILE):
        try:
            ai_model = joblib.load(MODEL_FILE)
            print("🧠 AI Brain Loaded Successfully!")
        except Exception as e:
            print(f"⚠️ Failed to load AI Brain: {e}")
    else:
        print("⚠️ Warning: glocarbon_brain.pkl not found. Running in fallback mode.")

# --- AI HELPER FUNCTION ---
def extract_features(image_bytes):
    """
    Must match the EXACT logic used in training!
    """
    img = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    img = img.resize((100, 100)) # Same size as training
    data = np.array(img)
    
    avg_r = np.mean(data[:,:,0])
    avg_g = np.mean(data[:,:,1])
    avg_b = np.mean(data[:,:,2])
    green_ratio = avg_g / (avg_r + avg_b + 1.0)
    
    # Reshape for the model (1 row, 4 columns)
    return np.array([[avg_r, avg_g, avg_b, green_ratio]])

# --- API ENDPOINTS ---

@app.get("/")
def home():
    status = "Online 🟢"
    brain_status = "Active 🧠" if ai_model else "Missing ⚪"
    return {"status": status, "ai_engine": brain_status}

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

@app.post("/scan_plot")
async def scan_plot(file: UploadFile = File(...)):
    print(f"📸 Receiving Image: {file.filename}")
    
    # 1. READ IMAGE
    contents = await file.read()
    
    # 2. ASK THE AI
    health_score = 0.5 # Default neutral
    
    if ai_model:
        try:
            # Extract features (Red, Green, Blue, Ratio)
            features = extract_features(contents)
            
            # Predict Probability (How confident is the AI that this is Healthy?)
            # Returns [[prob_degraded, prob_healthy]]
            prediction = ai_model.predict_proba(features)
            
            # Get the "Healthy" score (0.0 to 1.0)
            health_score = round(prediction[0][1], 2)
            print(f"🧠 AI Prediction: {health_score * 100}% Healthy")
            
        except Exception as e:
            print(f"AI Prediction Error: {e}")
            health_score = 0.5
    else:
        # Fallback if brain is missing (Old logic)
        print("⚠️ Using fallback math (No Brain found)")
        # Simple green index logic here as backup...
        
    # 3. CALCULATE CREDITS
    area = 50
    base_rate = 3.5 
    
    # If AI says it's healthy (> 50%), give full credits scaled by confidence
    # If AI says degraded (< 50%), give low credits
    total_credits = area * base_rate * health_score
    value = total_credits * 15
    
    return {
        "status": "Scanned",
        "file_name": file.filename,
        "ai_health_index": health_score,
        "total_credits": round(total_credits, 2),
        "value_estimate": round(value, 2)
    }