"""
O3 Prediction Service
Uses trained         self.model_type = model_type
        self.model = None
        
        # Get absolute paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_path = os.path.join(base_dir, 'MACHINE_LEARNING', 'merra2_nyc_final_dataset.csv')
        self.model_dir = os.path.join(base_dir, 'MACHINE_LEARNING', 'checkpoints')
        
        # Core atmospheric features (TO3 and TOX not needed for this model)
        self.feature_names = ['PS', 'TS', 'CLDPRS', 'Q250']predict O3 levels from atmospheric parameters
"""

import json
import pandas as pd
import numpy as np
from typing import Dict, Any, Optional
import os

# For XGBoost model
try:
    import xgboost as xgb
    XGBOOST_AVAILABLE = True
except ImportError:
    XGBOOST_AVAILABLE = False
    print("⚠️  XGBoost not installed. Install with: pip install xgboost")

# For PyTorch model
try:
    import torch
    import torch.nn as nn
    PYTORCH_AVAILABLE = True
except ImportError:
    PYTORCH_AVAILABLE = False
    print("⚠️  PyTorch not installed. Install with: pip install torch")


class O3Predictor:
    """O3 prediction using trained model"""
    
    def __init__(self, model_type='xgboost'):
        """
        Initialize O3 predictor
        
        Args:
            model_type: 'xgboost' or 'pytorch'
        """
        self.model_type = model_type
        self.model = None
        
        # Get absolute paths
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.csv_path = os.path.join(base_dir, 'MACHINE_LEARNING', 'merra2_nyc_final_dataset.csv')
        self.model_dir = os.path.join(base_dir, 'MACHINE_LEARNING', 'checkpoints')
        
        self.feature_names = ['PS', 'TS', 'CLDPRS', 'Q250', 'TO3']  # TOX excluded for now
        
        # Load historical data for TOX fallback
        if os.path.exists(self.csv_path):
            self.historical_data = pd.read_csv(self.csv_path)
            print(f"✅ Loaded {len(self.historical_data)} historical records for fallback")
        else:
            self.historical_data = None
            print(f"⚠️  Historical data not found at {self.csv_path}")
        
        # Load model
        self._load_model()
    
    def _load_model(self):
        """Load the trained model"""
        if self.model_type == 'xgboost' and XGBOOST_AVAILABLE:
            model_path = os.path.join(self.model_dir, 'xgboost_o3.json')
            if os.path.exists(model_path):
                self.model = xgb.Booster()
                self.model.load_model(model_path)
                print(f"✅ Loaded XGBoost model from {model_path}")
            else:
                print(f"❌ XGBoost model not found at {model_path}")
        
        elif self.model_type == 'pytorch' and PYTORCH_AVAILABLE:
            model_path = os.path.join(self.model_dir, 'o3_model_epoch10.pt')
            if os.path.exists(model_path):
                # You'll need to define your PyTorch model architecture here
                # self.model = YourModelClass()
                # self.model.load_state_dict(torch.load(model_path))
                # self.model.eval()
                print("✅ PyTorch model loading ready (need architecture definition)")
            else:
                print(f"❌ PyTorch model not found at {model_path}")
    
    def get_parameter_fallback(self, param_name: str, location: str = "New York City") -> Optional[float]:
        """
        Get parameter value from historical CSV data
        Returns the average value for the parameter from historical data
        
        Args:
            param_name: Name of parameter (TOX, CLDPRS, Q250, etc.)
            location: Location name (default: New York City)
        
        Returns:
            Average value from historical data or None
        """
        if self.historical_data is None:
            return None
        
        # For NYC, get average value from dataset
        if param_name in self.historical_data.columns:
            param_mean = self.historical_data[param_name].mean()
            print(f"📊 Using average {param_name} from historical data: {param_mean}")
            return param_mean
        
        return None
    
    def prepare_features(self, atmospheric_data: Dict[str, Any]) -> Optional[np.ndarray]:
        """
        Prepare features from atmospheric data for model input
        Model expects: PS, TS, CLDPRS, Q250, lon, lat, hour, dayofyear, sin_hour, cos_hour, sin_doy, cos_doy
        
        Args:
            atmospheric_data: Dict with parameters from Gemini agent
        
        Returns:
            numpy array of features or None if data incomplete
        """
        try:
            params = atmospheric_data.get('parameters', {})
            
            # Extract atmospheric values
            features = {}
            for param_name in self.feature_names:
                param_data = params.get(param_name, {})
                value = param_data.get('value')
                
                # Check if value is available
                if value == 'unavailable' or value is None:
                    print(f"⚠️  {param_name} is unavailable, using historical fallback")
                    fallback_value = self.get_parameter_fallback(param_name)
                    if fallback_value is None:
                        print(f"❌ No fallback available for {param_name}")
                        return None
                    value = fallback_value
                
                # Convert to float if not already
                if isinstance(value, str):
                    try:
                        value = float(value)
                    except ValueError:
                        print(f"❌ Cannot convert {param_name} value '{value}' to float")
                        return None
                
                features[param_name] = value
            
            # Add location features (NYC coordinates)
            features['lon'] = -73.75  # NYC longitude from your dataset
            features['lat'] = 40.5    # NYC latitude from your dataset
            
            # Add temporal features
            from datetime import datetime
            timestamp_str = atmospheric_data.get('query_timestamp') or atmospheric_data.get('timestamp_utc')
            if timestamp_str:
                try:
                    dt = datetime.fromisoformat(timestamp_str.replace('Z', '+00:00'))
                except Exception:
                    dt = datetime.utcnow()
            else:
                dt = datetime.utcnow()
            
            # Extract time features
            hour = dt.hour
            dayofyear = dt.timetuple().tm_yday
            
            features['hour'] = hour
            features['dayofyear'] = dayofyear
            
            # Add cyclical time encoding (sine/cosine)
            features['sin_hour'] = np.sin(2 * np.pi * hour / 24)
            features['cos_hour'] = np.cos(2 * np.pi * hour / 24)
            features['sin_doy'] = np.sin(2 * np.pi * dayofyear / 365)
            features['cos_doy'] = np.cos(2 * np.pi * dayofyear / 365)
            
            # Create feature array in the EXACT order the model expects
            feature_order = ['PS', 'TS', 'CLDPRS', 'Q250', 'lon', 'lat', 
                           'hour', 'dayofyear', 'sin_hour', 'cos_hour', 'sin_doy', 'cos_doy']
            feature_array = np.array([features[name] for name in feature_order])
            
            print(f"✅ Features prepared: {dict(zip(feature_order, feature_array))}")
            return feature_array.reshape(1, -1)
        
        except Exception as e:
            print(f"❌ Error preparing features: {str(e)}")
            return None
    
    def predict_o3(self, atmospheric_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Predict O3 level from atmospheric data
        
        Args:
            atmospheric_data: Dict with parameters from Gemini agent
        
        Returns:
            Dict with O3 prediction and metadata
        """
        if self.model is None:
            return {
                'success': False,
                'error': 'Model not loaded',
                'message': 'Please ensure the trained model file exists'
            }
        
        # Prepare features
        features = self.prepare_features(atmospheric_data)
        if features is None:
            return {
                'success': False,
                'error': 'Insufficient data',
                'message': 'Could not prepare features from atmospheric data'
            }
        
        try:
            # Make prediction
            if self.model_type == 'xgboost':
                # Create DMatrix with feature names
                feature_names = ['PS', 'TS', 'CLDPRS', 'Q250', 'lon', 'lat', 
                               'hour', 'dayofyear', 'sin_hour', 'cos_hour', 'sin_doy', 'cos_doy']
                dmatrix = xgb.DMatrix(features, feature_names=feature_names)
                o3_prediction = self.model.predict(dmatrix)[0]
            elif self.model_type == 'pytorch':
                with torch.no_grad():
                    features_tensor = torch.FloatTensor(features)
                    o3_prediction = self.model(features_tensor).item()
            else:
                return {
                    'success': False,
                    'error': 'Unknown model type',
                    'message': f'Model type {self.model_type} not supported'
                }
            
            # Get location
            location = atmospheric_data.get('location', 'Unknown')
            timestamp = atmospheric_data.get('query_timestamp', 'Unknown')
            
            return {
                'success': True,
                'o3_prediction': float(o3_prediction),
                'unit': 'ppb',  # or DU, depending on your model
                'location': location,
                'timestamp': timestamp,
                'model_type': self.model_type,
                'features_used': features.tolist(),
                'confidence': self._calculate_confidence(atmospheric_data)
            }
        
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'message': f'Error during prediction: {str(e)}'
            }
    
    def _calculate_confidence(self, atmospheric_data: Dict[str, Any]) -> str:
        """Calculate prediction confidence based on data quality"""
        params = atmospheric_data.get('parameters', {})
        
        # Count high confidence parameters
        high_confidence = sum(
            1 for p in params.values() 
            if isinstance(p, dict) and p.get('confidence') == 'high'
        )
        
        total_params = len([p for p in params.values() if isinstance(p, dict)])
        
        if total_params == 0:
            return 'low'
        
        confidence_ratio = high_confidence / total_params
        
        if confidence_ratio >= 0.7:
            return 'high'
        elif confidence_ratio >= 0.4:
            return 'medium'
        else:
            return 'low'


# Standalone testing
if __name__ == "__main__":
    print("🧪 Testing O3 Predictor\n")
    
    # Initialize predictor
    predictor = O3Predictor(model_type='xgboost')
    
    # Sample atmospheric data (from Gemini)
    sample_data = {
        "location": "New York City",
        "query_timestamp": "2025-10-05T12:00:00Z",
        "parameters": {
            "TS": {"value": 289.15, "unit": "K", "confidence": "high"},
            "PS": {"value": 101500, "unit": "Pa", "confidence": "high"},
            "CLDPRS": {"value": 30000, "unit": "Pa", "confidence": "medium"},
            "Q250": {"value": 0.0000045, "unit": "kg/kg", "confidence": "medium"},
            "TO3": {"value": 318, "unit": "DU", "confidence": "high"},
            "TOX": {"value": "unavailable", "unit": "DU", "confidence": "low"}
        }
    }
    
    # Make prediction
    print("\n🔮 Making O3 prediction...")
    result = predictor.predict_o3(sample_data)
    
    print("\n" + "="*60)
    print("PREDICTION RESULT:")
    print("="*60)
    print(json.dumps(result, indent=2))
