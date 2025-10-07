"""
Gemini AI Agent for Atmospheric Data Collection
Fetches real-time atmospheric parameters using Google's Gemini AI with web search
"""

import google.generativeai as genai
import json
import os
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure Gemini API
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")  # Set your API key here or in environment

def initialize_gemini(api_key: str = None):
    """Initialize Gemini API with key"""
    key = api_key or GEMINI_API_KEY
    if not key:
        raise ValueError("GEMINI_API_KEY not found. Please set it in environment or pass as parameter.")
    genai.configure(api_key=key)
    return genai.GenerativeModel('gemini-flash-latest')

def fetch_atmospheric_data(location: str = "New York City", api_key: str = None) -> Dict[str, Any]:
    """
    Use Gemini AI to search web and fetch current atmospheric parameters
    
    Parameters:
    - location: City name (default: "New York City")
    - api_key: Optional Gemini API key
    
    Returns:
    - Dictionary with atmospheric parameters and metadata
    """
    
    model = initialize_gemini(api_key)
    
    prompt = f"""
    Search the web for the MOST RECENT atmospheric and meteorological data for {location}.
    
    Find and extract these specific parameters:
    
    1. **TS (Surface Temperature)**: Current temperature in Kelvin or Celsius
    2. **PS (Surface Pressure)**: Current atmospheric pressure at surface in Pascals or hPa
    3. **CLDPRS (Cloud Top Pressure)**: Cloud top pressure in Pascals or hPa
    4. **Q250 (Specific Humidity at 250 hPa)**: Humidity at 250 hPa pressure level in kg/kg
    5. **TO3 (Total Column Ozone)**: Total ozone column in Dobson Units (DU)
    6. **TOX (Total Odd Oxygen)**: If available, in Dobson Units
    
    For each parameter, provide:
    - The VALUE (with units)
    - The SOURCE (website/service name)
    - The TIMESTAMP (when the measurement was taken)
    - CONFIDENCE (high/medium/low based on source reliability)
    
    If a parameter is not available, mark it as "unavailable" and explain why.
    
    Return the data in this EXACT JSON format:
    {{
        "location": "{location}",
        "timestamp_utc": "ISO 8601 timestamp",
        "parameters": {{
            "TS": {{"value": number, "unit": "K", "source": "source name", "time": "time", "confidence": "high/medium/low"}},
            "PS": {{"value": number, "unit": "Pa", "source": "source name", "time": "time", "confidence": "high/medium/low"}},
            "CLDPRS": {{"value": number or "unavailable", "unit": "Pa", "source": "source name", "time": "time", "confidence": "high/medium/low"}},
            "Q250": {{"value": number or "unavailable", "unit": "kg/kg", "source": "source name", "time": "time", "confidence": "high/medium/low"}},
            "TO3": {{"value": number or "unavailable", "unit": "DU", "source": "source name", "time": "time", "confidence": "high/medium/low"}},
            "TOX": {{"value": number or "unavailable", "unit": "DU", "source": "source name", "time": "time", "confidence": "high/medium/low"}}
        }},
        "sources": ["list of all sources used"],
        "notes": "Any important context or caveats"
    }}
    
    Use ONLY reliable meteorological sources like:
    - NOAA
    - Weather.gov
    - NASA
    - European Space Agency
    - National Weather Services
    - University meteorology departments
    """
    
    try:
        # Generate content with web search enabled
        response = model.generate_content(
            prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.1,  # Low temperature for factual responses
            )
        )
        
        # Extract JSON from response
        response_text = response.text
        
        # Try to parse JSON from response
        # Gemini might wrap JSON in markdown code blocks
        if "```json" in response_text:
            json_start = response_text.find("```json") + 7
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        elif "```" in response_text:
            json_start = response_text.find("```") + 3
            json_end = response_text.find("```", json_start)
            json_text = response_text[json_start:json_end].strip()
        else:
            json_text = response_text.strip()
        
        data = json.loads(json_text)
        
        # Add query metadata
        data["query_timestamp"] = datetime.utcnow().isoformat()
        data["agent"] = "Gemini-1.5-Flash"
        data["success"] = True
        
        return data
        
    except json.JSONDecodeError as e:
        return {
            "success": False,
            "error": "Failed to parse response as JSON",
            "raw_response": response_text[:500],
            "exception": str(e)
        }
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "exception_type": type(e).__name__
        }

def get_parameter_summary(data: Dict[str, Any]) -> str:
    """Generate human-readable summary of fetched data"""
    
    if not data.get("success"):
        return f"❌ Failed to fetch data: {data.get('error', 'Unknown error')}"
    
    summary = f"📍 Location: {data.get('location', 'Unknown')}\n"
    summary += f"🕐 Query Time: {data.get('query_timestamp', 'Unknown')}\n\n"
    summary += "📊 Atmospheric Parameters:\n"
    
    params = data.get("parameters", {})
    for param_name, param_data in params.items():
        if isinstance(param_data, dict):
            value = param_data.get("value", "N/A")
            unit = param_data.get("unit", "")
            source = param_data.get("source", "Unknown")
            confidence = param_data.get("confidence", "unknown")
            
            emoji = "✅" if confidence == "high" else "⚠️" if confidence == "medium" else "❓"
            
            if value == "unavailable" or value == "N/A":
                summary += f"  {emoji} {param_name}: Not available\n"
            else:
                summary += f"  {emoji} {param_name}: {value} {unit} (from {source})\n"
    
    if data.get("sources"):
        summary += f"\n📚 Sources: {', '.join(data['sources'])}\n"
    
    if data.get("notes"):
        summary += f"\n💡 Notes: {data['notes']}\n"
    
    return summary

# Example usage
if __name__ == "__main__":
    print("🤖 Gemini Weather Agent - Atmospheric Data Fetcher\n")
    print("=" * 60)
    
    # Check if running in Docker/non-interactive mode
    import sys
    is_interactive = sys.stdin.isatty()
    
    # Get API key from environment or user input
    if is_interactive:
        api_key = input("Enter your Gemini API key (or press Enter to use environment variable): ").strip()
        if not api_key:
            api_key = None
        location = input("Enter location (default: New York City): ").strip() or "New York City"
    else:
        # Non-interactive mode (Docker) - use environment variables
        api_key = None  # Will use GEMINI_API_KEY from environment
        location = os.getenv("DEFAULT_LOCATION", "New York City")
        print(f"Running in non-interactive mode")
        print(f"Using GEMINI_API_KEY from environment")
    
    print(f"\n🔍 Searching for atmospheric data for {location}...")
    print("This may take 10-15 seconds...\n")
    
    # Fetch data
    try:
        data = fetch_atmospheric_data(location, api_key)
    except ValueError as e:
        print(f"❌ Error: {e}")
        print("Please set GEMINI_API_KEY environment variable")
        sys.exit(1)
    
    # Display results
    print("=" * 60)
    print(get_parameter_summary(data))
    print("=" * 60)
    
    # Save to JSON file
    output_file = f"atmospheric_data_{location.replace(' ', '_')}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w') as f:
        json.dump(data, f, indent=2)
    
    print(f"\n💾 Full data saved to: {output_file}")
