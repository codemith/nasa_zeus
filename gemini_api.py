"""
FastAPI endpoint for Gemini Weather Agent
Provides atmospheric data via AI-powered web search
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, Any
import os
from datetime import datetime
from dotenv import load_dotenv
from gemini_weather_agent import fetch_atmospheric_data, get_parameter_summary
from o3_predictor import O3Predictor

# Load environment variables from .env file
load_dotenv()

app = FastAPI(title="Gemini Weather Agent API")

# Initialize O3 predictor
o3_predictor = O3Predictor(model_type='xgboost')

# Configure CORS for frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Response model
class AtmosphericDataResponse(BaseModel):
    success: bool
    data: Optional[Dict[str, Any]] = None
    summary: Optional[str] = None
    error: Optional[str] = None

@app.get("/")
async def root():
    """API root endpoint"""
    return {
        "service": "Gemini Weather Agent API",
        "version": "1.0.0",
        "endpoints": {
            "/atmospheric-data": "Fetch atmospheric parameters for a location",
            "/predict-o3": "Predict O3 levels from atmospheric data",
            "/health": "Health check"
        }
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "service": "Gemini Weather Agent"
    }

@app.get("/atmospheric-data", response_model=AtmosphericDataResponse)
async def get_atmospheric_data(
    location: str = Query(default="New York City", description="Location to fetch data for"),
    api_key: Optional[str] = Query(default=None, description="Optional Gemini API key override")
):
    """
    Fetch atmospheric data using Gemini AI
    
    Parameters:
    - location: City name (e.g., "New York City", "Los Angeles")
    - api_key: Optional API key (uses environment variable if not provided)
    
    Returns:
    - Atmospheric parameters with sources and timestamps
    """
    
    try:
        # Use environment variable if no API key provided
        if not api_key:
            api_key = os.getenv("GEMINI_API_KEY")
            
        if not api_key:
            raise HTTPException(
                status_code=500,
                detail="GEMINI_API_KEY not configured. Please set it in environment variables."
            )
        
        # Fetch data using Gemini agent
        data = fetch_atmospheric_data(location=location, api_key=api_key)
        
        if not data.get("success"):
            return AtmosphericDataResponse(
                success=False,
                error=data.get("error", "Unknown error occurred"),
                data=data
            )
        
        # Generate summary
        summary = get_parameter_summary(data)
        
        return AtmosphericDataResponse(
            success=True,
            data=data,
            summary=summary
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error fetching atmospheric data: {str(e)}"
        )

@app.post("/atmospheric-data")
async def post_atmospheric_data(
    location: str,
    api_key: Optional[str] = None
):
    """
    POST endpoint for atmospheric data (alternative to GET)
    """
    return await get_atmospheric_data(location=location, api_key=api_key)

@app.get("/predict-o3")
async def predict_o3(
    location: str = Query(default="New York City", description="Location to predict O3 for"),
    api_key: Optional[str] = Query(default=None, description="Optional Gemini API key override")
):
    """
    Fetch atmospheric data and predict O3 levels
    
    This endpoint:
    1. Fetches atmospheric parameters using Gemini AI
    2. Uses trained XGBoost model to predict O3
    3. Returns prediction with confidence level
    
    Parameters:
    - location: City name (e.g., "New York City")
    - api_key: Optional API key (uses environment variable if not provided)
    
    Returns:
    - O3 prediction with atmospheric data and confidence
    """
    try:
        # First, fetch atmospheric data
        atm_response = await get_atmospheric_data(location=location, api_key=api_key)
        
        if not atm_response.success:
            return {
                "success": False,
                "error": "Failed to fetch atmospheric data",
                "details": atm_response.error
            }
        
        # Make O3 prediction
        prediction_result = o3_predictor.predict_o3(atm_response.data)
        
        # Combine atmospheric data and prediction
        return {
            "success": prediction_result.get('success', False),
            "location": location,
            "o3_prediction": prediction_result.get('o3_prediction'),
            "unit": prediction_result.get('unit', 'ppb'),
            "confidence": prediction_result.get('confidence', 'unknown'),
            "model_type": prediction_result.get('model_type', 'xgboost'),
            "atmospheric_data": atm_response.data,
            "error": prediction_result.get('error'),
            "message": prediction_result.get('message')
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error predicting O3: {str(e)}"
        )

if __name__ == "__main__":
    import uvicorn
    
    # Check for API key
    if not os.getenv("GEMINI_API_KEY"):
        print("⚠️  WARNING: GEMINI_API_KEY environment variable not set!")
        print("Set it with: export GEMINI_API_KEY='your-api-key-here'")
    
    print("🚀 Starting Gemini Weather Agent API...")
    print("📍 API will be available at: http://localhost:8001")
    print("📚 Docs available at: http://localhost:8001/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=8001, reload=False)
