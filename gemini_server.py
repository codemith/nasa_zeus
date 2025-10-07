"""
FastAPI Server for Gemini Weather Agent
Provides web endpoints for atmospheric data and O3 prediction
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from gemini_weather_agent import fetch_atmospheric_data
from o3_predictor import O3Predictor
import os

app = FastAPI(title="Gemini Weather Agent API")

# Initialize O3 predictor (XGBoost model)
o3_predictor = O3Predictor(model_type='xgboost')

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "Gemini Weather Agent API",
        "version": "1.0",
        "endpoints": [
            "/atmospheric-data",
            "/predict-o3",
            "/health"
        ]
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "gemini-weather-agent"}

@app.get("/atmospheric-data")
async def get_atmospheric_data(location: str = "New York City"):
    """
    Fetch atmospheric data for a given location using Gemini AI
    
    Parameters:
    - location: Location name (default: New York City)
    
    Returns:
    - Atmospheric parameters including TS, PS, Q250, TO3, etc.
    """
    try:
        # Check if Gemini API key is set
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your-gemini-api-key-here":
            return {
                "error": "Gemini API key not configured",
                "message": "Please set a valid GEMINI_API_KEY in your environment",
                "location": location,
                "parameters": {},
                "agent": "Gemini AI (API Key Required)"
            }
        
        # Fetch data using the Gemini agent
        data = fetch_atmospheric_data(location, api_key=None)  # Uses env var
        
        if not data:
            raise HTTPException(status_code=500, detail="Failed to fetch atmospheric data")
        
        return data
        
    except ValueError as e:
        # API key error
        return {
            "error": "Configuration Error",
            "message": str(e),
            "location": location,
            "parameters": {},
            "agent": "Gemini AI (Requires Valid API Key)"
        }
    except Exception as e:
        # Other errors
        print(f"Error fetching atmospheric data: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching atmospheric data: {str(e)}"
        )

@app.get("/predict-o3")
async def predict_ozone(location: str = "New York City"):
    """
    Predict O3 concentration for a given location
    
    Parameters:
    - location: Location name (default: New York City)
    
    Returns:
    - O3 prediction and related atmospheric parameters
    """
    try:
        # First fetch atmospheric data
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key or api_key == "your-gemini-api-key-here":
            return {
                "error": "Gemini API key not configured",
                "message": "O3 prediction requires atmospheric data from Gemini AI",
                "location": location
            }
        
        atmospheric_data = fetch_atmospheric_data(location, api_key=None)
        
        if not atmospheric_data or "parameters" not in atmospheric_data:
            raise HTTPException(status_code=500, detail="Failed to fetch atmospheric data for O3 prediction")
        
        # Predict O3 using the ML model
        prediction = o3_predictor.predict_o3(atmospheric_data)
        
        if not prediction or not prediction.get("success"):
            raise HTTPException(
                status_code=500,
                detail=prediction.get("message", "O3 prediction failed")
            )
        
        return {
            "location": location,
            "atmospheric_data": atmospheric_data,
            "o3_prediction": prediction
        }
        
    except ValueError as e:
        return {
            "error": "Configuration Error",
            "message": str(e),
            "location": location
        }
    except Exception as e:
        print(f"Error predicting O3: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error predicting O3: {str(e)}"
        )

if __name__ == "__main__":
    # Run the server
    port = int(os.getenv("PORT", 8001))
    print(f"🚀 Starting Gemini Weather Agent API on port {port}")
    print(f"📍 Endpoints available at http://0.0.0.0:{port}")
    
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
