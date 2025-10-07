// Gemini Weather Data Widget for Dashboard
'use client';

import { useState } from 'react';

export default function GeminiWeatherWidget({ location = "New York City" }) {
  const [loading, setLoading] = useState(false);
  const [data, setData] = useState(null);
  const [error, setError] = useState(null);
  const [showDetails, setShowDetails] = useState(false);
  const [o3Prediction, setO3Prediction] = useState(null);
  const [o3Loading, setO3Loading] = useState(false);
  const [o3Error, setO3Error] = useState(null);

  const fetchWeatherData = async () => {
    setLoading(true);
    setError(null);

    try {
      console.log('🔵 Fetching atmospheric data...');
      const GEMINI_URL = process.env.NEXT_PUBLIC_GEMINI_URL || 'http://localhost:8001';
      const response = await fetch(
        `${GEMINI_URL}/atmospheric-data?location=${encodeURIComponent(location)}`
      );

      console.log('🔵 Response status:', response.status);
      
      if (!response.ok) {
        throw new Error(`Failed to fetch: ${response.status} ${response.statusText}`);
      }

      const result = await response.json();
      console.log('🔵 Raw API response:', result);
      console.log('🔵 Has parameters?', !!result.parameters);
      console.log('🔵 Success field:', result.success);

      // Check if API returned success or if it has parameters (the actual data structure)
      if (result.success && result.parameters) {
        console.log('✅ Setting data with parameters:', Object.keys(result.parameters));
        setData(result);
      } else if (result.error) {
        console.error('❌ API returned error:', result.error);
        setError(result.error || result.message || 'Unknown error');
      } else {
        console.error('❌ No valid data in response');
        setError('No data received from API');
      }
    } catch (err) {
      console.error('❌ Fetch error:', err);
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const predictO3 = async () => {
    setO3Loading(true);
    setO3Error(null);

    try {
      console.log('🟣 Predicting O3...');
      const GEMINI_URL = process.env.NEXT_PUBLIC_GEMINI_URL || 'http://localhost:8001';
      const response = await fetch(
        `${GEMINI_URL}/predict-o3?location=${encodeURIComponent(location)}`
      );

      console.log('🟣 O3 Response status:', response.status);

      if (!response.ok) {
        throw new Error(`Failed to predict O3: ${response.status}`);
      }

      const result = await response.json();
      console.log('🟣 O3 Raw response:', result);
      console.log('🟣 Has o3_prediction?', !!result.o3_prediction);
      console.log('🟣 o3_prediction.success:', result.o3_prediction?.success);

      // Check for o3_prediction in the response
      if (result.o3_prediction && result.o3_prediction.success) {
        console.log('✅ Setting O3 prediction:', result.o3_prediction);
        setO3Prediction(result.o3_prediction);
        // Also update atmospheric data if available
        if (result.atmospheric_data) {
          console.log('✅ Also updating atmospheric data');
          setData(result.atmospheric_data);
        }
      } else if (result.error) {
        console.error('❌ O3 API returned error:', result.error);
        setO3Error(result.error || result.message || 'Prediction failed');
      } else {
        console.error('❌ Invalid O3 response structure:', result);
        setO3Error('No prediction data received');
      }
    } catch (err) {
      console.error('❌ O3 Fetch error:', err);
      setO3Error(err.message);
    } finally {
      setO3Loading(false);
    }
  };

  const getConfidenceEmoji = (confidence) => {
    switch (confidence) {
      case 'high': return '✅';
      case 'medium': return '⚠️';
      case 'low': return '❓';
      default: return '❔';
    }
  };

  const formatValue = (param) => {
    if (!param || param.value === 'unavailable') {
      return 'Not available';
    }
    return `${param.value} ${param.unit}`;
  };

  const getO3Color = (confidence) => {
    switch (confidence) {
      case 'high': return 'from-green-500/80 to-emerald-600/80';
      case 'medium': return 'from-yellow-500/80 to-orange-600/80';
      case 'low': return 'from-red-500/80 to-pink-600/80';
      default: return 'from-gray-500/80 to-gray-600/80';
    }
  };

  const getO3Label = (ppb) => {
    if (ppb < 55) return { level: 'Good', emoji: '😊', color: 'text-green-400' };
    if (ppb < 71) return { level: 'Moderate', emoji: '😐', color: 'text-yellow-400' };
    if (ppb < 86) return { level: 'Unhealthy for Sensitive', emoji: '😷', color: 'text-orange-400' };
    if (ppb < 106) return { level: 'Unhealthy', emoji: '😨', color: 'text-red-400' };
    if (ppb < 200) return { level: 'Very Unhealthy', emoji: '🤢', color: 'text-purple-400' };
    return { level: 'Hazardous', emoji: '☠️', color: 'text-red-600' };
  };

  return (
    <div className="bg-gray-900/20 backdrop-blur-sm border border-white/10 rounded-lg shadow-lg flex flex-col max-h-[calc(100vh-180px)]">
      {/* Fixed Header */}
      <div className="flex items-center justify-between p-4 border-b border-white/10 flex-shrink-0">
        <h3 className="text-lg font-semibold text-white flex items-center gap-2">
          <span>AI Weather Agent</span>
        </h3>
        <div className="flex gap-2">
          <button
            onClick={fetchWeatherData}
            disabled={loading}
            className="px-3 py-2 bg-blue-600/90 hover:bg-blue-700 text-white rounded-lg 
                       disabled:bg-gray-600 disabled:cursor-not-allowed transition-all
                       text-sm font-medium"
          >
            {loading ? 'Loading...' : 'Fetch Data'}
          </button>
          <button
            onClick={predictO3}
            disabled={o3Loading}
            className="px-3 py-2 bg-gradient-to-r from-purple-600/90 to-pink-600/90 
                       hover:from-purple-700 hover:to-pink-700 text-white rounded-lg 
                       disabled:bg-gray-600 disabled:cursor-not-allowed transition-all
                       text-sm font-medium shadow-lg"
          >
            {o3Loading ? 'Loading...' : 'Predict O3'}
          </button>
        </div>
      </div>

      {/* Scrollable Content */}
      <div className="overflow-y-auto overflow-x-hidden p-4 flex-1 custom-scrollbar">
        {/* Debug Info */}
        <div className="mb-2 text-xs text-white/50">
          Data state: {data ? '✅ Has data' : '❌ No data'} | 
          O3: {o3Prediction ? '✅ Has prediction' : '❌ No prediction'} |
          Error: {error || o3Error || 'None'}
        </div>

        {/* O3 Prediction Display */}
        {o3Prediction && o3Prediction.success && (
          <div className={`bg-gradient-to-r ${getO3Color(o3Prediction.confidence)} rounded-lg p-4 shadow-lg border border-white/20`}>
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-white font-bold text-lg flex items-center gap-2">
                O3 Prediction
              </h4>
              <span className="text-xs text-white/80 bg-black/20 px-2 py-1 rounded">
                {o3Prediction.model_type}
              </span>
            </div>
            
            <div className="text-center py-3">
              {(() => {
                const o3Label = getO3Label(o3Prediction.o3_prediction);
                return (
                  <>
                    <div className="text-5xl font-bold text-white mb-2">
                      {Math.round(o3Prediction.o3_prediction)}
                      <span className="text-2xl ml-2">{o3Prediction.unit}</span>
                    </div>
                    <div className={`text-xl font-semibold ${o3Label.color} flex items-center justify-center gap-2`}>
                      <span>{o3Label.level}</span>
                    </div>
                    <div className="text-white/70 text-sm mt-2">
                      Confidence: {o3Prediction.confidence.toUpperCase()}
                    </div>
                  </>
                );
              })()}
            </div>
          </div>
        )}

        {o3Error && (
          <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3">
            <p className="text-white text-sm">O3 Prediction Error: {o3Error}</p>
          </div>
        )}

        {error && (
          <div className="bg-red-500/20 border border-red-500/50 rounded-lg p-3">
            <p className="text-white text-sm">{error}</p>
          </div>
        )}

        {data && (
          <div className="space-y-3">
          {/* Location and Timestamp */}
          <div className="bg-black/20 rounded-lg p-3">
            <p className="text-white text-sm">
              <span className="font-medium">{data.location}</span>
            </p>
            <p className="text-white text-xs mt-1">
              {new Date(data.query_timestamp).toLocaleString()}
            </p>
          </div>

          {/* Parameters Grid */}
          <div className="grid grid-cols-2 gap-2">
            {data.parameters && Object.entries(data.parameters).map(([key, param]) => (
              <div
                key={key}
                className="bg-black/20 rounded-lg p-3 hover:bg-black/30 transition-all cursor-pointer"
                onClick={() => setShowDetails(!showDetails)}
              >
                <div className="flex items-center gap-2 mb-1">
                  <span>{getConfidenceEmoji(param.confidence)}</span>
                  <span className="text-white font-medium text-sm">{key}</span>
                </div>
                <p className="text-white text-xs">
                  {formatValue(param)}
                </p>
              </div>
            ))}
          </div>

          {/* Detailed View */}
          {showDetails && (
            <div className="bg-white/10 backdrop-blur-md rounded-lg overflow-hidden">
              <h3 className="text-lg font-semibold p-4 pb-2 text-white bg-white/5 sticky top-0 z-10 backdrop-blur-md border-b border-white/10">
                Detailed Information
              </h3>
              <div className="max-h-[400px] overflow-y-auto custom-scrollbar p-4 pt-2">
                <div className="space-y-3">
                  {data.parameters && Object.entries(data.parameters).map(([key, param]) => (
                    <div key={key} className="text-xs space-y-1">
                      <p className="text-white font-medium">
                        {getConfidenceEmoji(param.confidence)} {key}
                      </p>
                      <p className="text-white pl-5">
                        Value: {formatValue(param)}
                      </p>
                      {param.source && (
                        <p className="text-white pl-5">
                          Source: {param.source}
                        </p>
                      )}
                      {param.time && (
                        <p className="text-white pl-5">
                          Time: {param.time}
                        </p>
                      )}
                    </div>
                  ))}
                  
                  {data.sources && data.sources.length > 0 && (
                    <div className="pt-2 border-t border-white/10">
                      <p className="text-white text-xs">
                        <strong>Sources:</strong> {data.sources.join(', ')}
                      </p>
                    </div>
                  )}
                  
                  {data.notes && (
                    <div className="pt-2 border-t border-white/10">
                      <p className="text-white text-xs">
                        <strong>Notes:</strong> {data.notes}
                      </p>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}

            {/* Agent Info */}
            <div className="text-center text-white text-xs">
              Powered by {data.agent || 'Gemini AI'} with Web Search
            </div>
          </div>
        )}

        {!data && !loading && !error && (
          <div className="text-center py-8">
            <p className="text-white text-sm mb-2">
              Click "Fetch Data" to retrieve atmospheric parameters
            </p>
            <p className="text-white text-xs">
              Using AI to search reliable meteorological sources
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
