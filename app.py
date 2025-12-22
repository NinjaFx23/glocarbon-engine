from flask import Flask, request, jsonify
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app)  # This allows your HTML app to talk to this Python server

# 1. THE HEALTH CHECK (To confirm we are alive)
@app.route('/', methods=['GET'])
def home():
    return "GloCarbon AI Engine is Online! 🌍🚀"

# 2. THE SCAN SIMULATION (Replacing the JS timer with Python logic)
# Soon, we will put the REAL MindSpore code here.
@app.route('/analyze', methods=['POST'])
def analyze_image():
    print("Received an image for analysis...")
    
    # Simulate AI processing time (2 seconds)
    time.sleep(2)
    
    # Simulate a result (This is where MindSpore will eventually give real data)
    # We randomize it slightly so every scan feels different
    carbon_density = round(random.uniform(10.5, 15.0), 2)
    est_value = round(carbon_density * 27.50, 2) # Assuming $27.50 per tonne
    
    return jsonify({
        "status": "success",
        "biomass_type": "Grassland/Savannah",
        "carbon_tonnes": carbon_density,
        "market_value": est_value,
        "confidence": "98.4%"
    })

if __name__ == '__main__':
    # Run the server on port 5000
    app.run(debug=True, port=5000)