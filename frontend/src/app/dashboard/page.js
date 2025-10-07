'use client';

import { useState, useEffect } from 'react';
import { getUserAlerts, getUserPreferences, updateUserPreferences, logout } from '../../lib/auth';
import { useAuth } from '../../contexts/AuthContext';
import AuthGuard from '../../components/auth/AuthGuard';
import dynamic from 'next/dynamic';
import GeminiWeatherWidget from '../components/GeminiWeatherWidget';
import ForecastChart from '../components/ForecastChart';

// Dynamically import the Map component
const Map = dynamic(() => import('../components/Map'), {
    ssr: false,
    loading: () => (
        <div style={{
            height: '400px',
            width: '100%',
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
            backgroundColor: '#f0f0f0'
        }}>
            <p>Loading map...</p>
        </div>
    )
});

export default function Dashboard() {
    const { user } = useAuth();
    const [alerts, setAlerts] = useState([]);
    const [preferences, setPreferences] = useState(null);
    const [loading, setLoading] = useState(true);
    const [showPreferences, setShowPreferences] = useState(false);
    const [showReport, setShowReport] = useState(false);

    useEffect(() => {
        const fetchData = async () => {
            try {
                console.log('🔷 Dashboard: Fetching user data...');
                const [alertsData, prefsData] = await Promise.all([
                    getUserAlerts(),
                    getUserPreferences()
                ]);
                console.log('🔷 Dashboard: Alerts data received:', alertsData);
                console.log('🔷 Dashboard: Preferences data received:', prefsData);
                console.log('🔷 Dashboard: Alerts array:', alertsData.alerts);
                console.log('🔷 Dashboard: Alerts array length:', alertsData.alerts?.length || 0);
                console.log('🔷 Dashboard: Current AQI from API:', alertsData.current_aqi);
                
                setAlerts(alertsData.alerts || []);
                
                // Merge current_aqi into preferences so we can access it in the widget
                setPreferences({
                    ...prefsData,
                    current_aqi: alertsData.current_aqi,
                    current_conditions: alertsData.current_conditions
                });
            } catch (error) {
                console.error('❌ Dashboard: Error fetching data:', error);
            } finally {
                setLoading(false);
            }
        };

        fetchData();
    }, []);

    const handleUpdatePreferences = async (newPrefs) => {
        try {
            await updateUserPreferences(newPrefs);
            setPreferences(newPrefs);
            setShowPreferences(false);
            // Refresh alerts after updating preferences
            const alertsData = await getUserAlerts();
            setAlerts(alertsData.alerts || []);
        } catch (error) {
            console.error('Error updating preferences:', error);
        }
    };

    const getAlertIcon = (severity) => {
        switch (severity) {
            case 'danger':
                return '🚨';
            case 'warning':
                return '⚠️';
            case 'info':
                return 'ℹ️';
            default:
                return '📊';
        }
    };

    const getAlertColor = (severity) => {
        switch (severity) {
            case 'danger':
                return 'bg-red-50 border-red-200 text-red-800';
            case 'warning':
                return 'bg-yellow-50 border-yellow-200 text-yellow-800';
            case 'info':
                return 'bg-blue-50 border-blue-200 text-blue-800';
            default:
                return 'bg-gray-50 border-gray-200 text-gray-800';
        }
    };

    if (loading) {
        return (
            <AuthGuard>
                <div className="min-h-screen flex items-center justify-center">
                    <div className="animate-spin rounded-full h-32 w-32 border-b-2 border-indigo-600"></div>
                </div>
            </AuthGuard>
        );
    }

    return (
        <AuthGuard>
            {/* Full-screen container */}
            <main className="relative h-screen w-screen overflow-hidden">
                {/* Full-screen Map as Background */}
                <div className="absolute inset-0 w-full h-full">
                    <Map />
                </div>

                {/* Floating Header Bar - Top */}
                <div className="absolute top-4 left-1/2 transform -translate-x-1/2 z-[1001]">
                    <div className="bg-gray-900/1 backdrop-blur-sm rounded-lg shadow-2xl border border-white/20 px-6 py-3">
                        <div className="flex items-center space-x-6">
                            <div>
                                <h1 className="text-xl font-bold text-white">Zeus Air Quality</h1>
                                <p className="text-xs text-white">Welcome, {user?.name}</p>
                            </div>
                            <div className="flex items-center space-x-3">
                                <button
                                    onClick={() => setShowReport(!showReport)}
                                    className="bg-blue-600/90 hover:bg-blue-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-all"
                                >
                                    Report
                                </button>
                                <button
                                    onClick={() => setShowPreferences(!showPreferences)}
                                    className="bg-indigo-600/90 hover:bg-indigo-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-all"
                                >
                                    Settings
                                </button>
                                <button
                                    onClick={logout}
                                    className="bg-gray-600/90 hover:bg-gray-700 text-white px-4 py-2 rounded-md text-sm font-medium transition-all"
                                >
                                    Logout
                                </button>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Floating Alerts Panel - Top Left */}
                {alerts.length > 0 && (
                    <div className="absolute top-24 left-4 z-[1001] w-[400px] max-h-[60vh] overflow-y-auto">
                        <div className="bg-gray-900/20 backdrop-blur-sm rounded-lg shadow-2xl border border-white/20 p-5">
                            <h2 className="text-lg font-semibold text-white mb-4 flex items-center">
                                <span className="mr-2">🚨</span>
                                Active Alerts ({alerts.length})
                            </h2>
                            <div className="space-y-3">
                                {alerts.map((alert, index) => (
                                    <div
                                        key={index}
                                        className={`border rounded-lg p-4 ${
                                            alert.severity === 'danger'
                                                ? 'bg-red-900/40 border-red-500/50'
                                                : alert.severity === 'warning'
                                                ? 'bg-yellow-900/40 border-yellow-500/50'
                                                : 'bg-blue-900/40 border-blue-500/50'
                                        }`}
                                    >
                                        <div className="flex items-start">
                                            <span className="text-2xl mr-3">{getAlertIcon(alert.severity)}</span>
                                            <div className="flex-1">
                                                <h3 className="font-semibold text-sm uppercase tracking-wide text-white">
                                                    {alert.severity} Alert
                                                </h3>
                                                <p className="mt-1 text-sm text-white">{alert.message}</p>

                                                {alert.recommendations && (
                                                    <div className="mt-3">
                                                        <p className="text-xs font-medium mb-1 text-white">Recommendations:</p>
                                                        <ul className="text-xs space-y-1 text-white">
                                                            {alert.recommendations.map((rec, i) => (
                                                                <li key={i} className="flex items-start">
                                                                    <span className="mr-2">•</span>
                                                                    <span>{rec}</span>
                                                                </li>
                                                            ))}
                                                        </ul>
                                                    </div>
                                                )}

                                                {alert.timestamp && (
                                                    <p className="text-xs mt-2 text-white/80">
                                                        {new Date(alert.timestamp).toLocaleString()}
                                                    </p>
                                                )}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Floating Location & AQI Panel - Left Side Below Alerts */}
                <div className="absolute bottom-4 left-4 z-[1002] w-[400px]">
                    <div className="bg-gray-900/20 backdrop-blur-md rounded-lg shadow-2xl border-2 border-blue-400/60 p-5">
                        {/* Location Info */}
                        <div className="mb-4 pb-4 border-b border-white/20">
                            <h2 className="text-lg font-semibold text-white mb-2 flex items-center">
                                <span className="mr-2">📍</span>
                                Current Location
                            </h2>
                            <p className="text-sm text-white">
                                New York City, NY
                            </p>
                            <p className="text-xs text-white mt-1">
                                {preferences?.location_lat?.toFixed(4)}, {preferences?.location_lon?.toFixed(4)}
                            </p>
                            <p className="text-xs text-white mt-2">
                                <span className="font-medium">Profile:</span> <span className="capitalize">{preferences?.health_profile}</span> | 
                                <span className="font-medium ml-2">Threshold:</span> AQI {preferences?.alert_threshold}
                            </p>
                        </div>

                        {/* Current AQI Display */}
                        <div>
                            <h2 className="text-lg font-semibold text-white mb-3 flex items-center">
                                <span className="mr-2">🌬️</span>
                                Current Air Quality
                            </h2>

                            {/* Display current AQI from alerts[0].aqi_current OR from preferences state if available */}
                            {((alerts.length > 0 && alerts[0].aqi_current) || preferences?.current_aqi) ? (
                                <div className="text-center">
                                    <div className="text-5xl font-bold text-white mb-2">
                                        {alerts[0]?.aqi_current || preferences?.current_aqi || 'N/A'}
                                    </div>
                                    <div className="text-sm text-white mb-4">
                                        AQI Level
                                    </div>

                                    {/* AQI Scale */}
                                    <div className="w-full bg-gradient-to-r from-green-400 via-yellow-400 via-orange-400 via-red-400 to-purple-600 h-3 rounded-full mb-2">
                                        <div
                                            className="h-3 bg-black rounded-full opacity-50"
                                            style={{
                                                width: `${((alerts[0]?.aqi_current || preferences?.current_aqi || 1) / 5) * 100}%`,
                                                maxWidth: '100%'
                                            }}
                                        ></div>
                                    </div>
                                    <div className="flex justify-between text-[10px] text-white">
                                        <span>Good</span>
                                        <span>Unhealthy</span>
                                    </div>
                                </div>
                            ) : (
                                <div className="text-center py-4 text-gray-400 text-sm">
                                    <p>✓ Air quality is good</p>
                                    <p className="text-xs mt-1">No alerts at this time</p>
                                </div>
                            )}
                        </div>
                    </div>
                </div>

                {/* Gemini Weather Agent Widget - Right Side */}
                <div className="absolute bottom-4 right-4 z-[1002] w-[420px]">
                    <div className="bg-gray-900/95 backdrop-blur-md rounded-lg shadow-2xl border-2 border-purple-400/60 p-1">
                        <GeminiWeatherWidget location="New York City" />
                    </div>
                </div>

                {/* Preferences Modal */}
                {showPreferences && preferences && (
                    <PreferencesPanel
                        preferences={preferences}
                        onUpdate={handleUpdatePreferences}
                        onClose={() => setShowPreferences(false)}
                    />
                )}

                {/* Report Modal */}
                {showReport && (
                    <ReportModal
                        alerts={alerts}
                        preferences={preferences}
                        onClose={() => setShowReport(false)}
                    />
                )}
            </main>
        </AuthGuard>
    );
}

// Preferences Panel Component
function PreferencesPanel({ preferences, onUpdate, onClose }) {
    const [formData, setFormData] = useState(preferences);

    const handleSubmit = (e) => {
        e.preventDefault();
        onUpdate(formData);
    };

    return (
        <div className="fixed inset-0 bg-black/60 backdrop-blur-sm flex items-center justify-center z-[1100]">
            <div className="bg-gray-900/20 backdrop-blur-sm border border-white/20 rounded-lg shadow-2xl p-6 w-full max-w-md">
                <h2 className="text-xl font-semibold text-white mb-4">⚙️ Alert Preferences</h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-200">Health Profile</label>
                        <select
                            value={formData.health_profile}
                            onChange={(e) => setFormData({ ...formData, health_profile: e.target.value })}
                            className="mt-1 block w-full bg-gray-700/50 border border-white/20 text-white rounded-md px-3 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
                        >
                            <option value="general">General Population</option>
                            <option value="sensitive">Sensitive to Air Pollution</option>
                            <option value="high_risk">High Risk (Asthma, Heart Conditions)</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-gray-200">
                            Alert Threshold (AQI Level: {formData.alert_threshold})
                        </label>
                        <input
                            type="range"
                            min="1"
                            max="5"
                            value={formData.alert_threshold}
                            onChange={(e) => setFormData({ ...formData, alert_threshold: parseInt(e.target.value) })}
                            className="mt-2 w-full"
                        />
                        <div className="flex justify-between text-xs text-gray-400 mt-1">
                            <span>1 (Good)</span>
                            <span>5 (Very Unhealthy)</span>
                        </div>
                    </div>

                    <div className="flex items-center">
                        <input
                            type="checkbox"
                            checked={formData.email_notifications}
                            onChange={(e) => setFormData({ ...formData, email_notifications: e.target.checked })}
                            className="mr-2 w-4 h-4"
                        />
                        <label className="text-sm text-gray-200">Enable email notifications</label>
                    </div>

                    <div className="flex space-x-3 pt-4">
                        <button
                            type="submit"
                            className="flex-1 bg-indigo-600 hover:bg-indigo-700 text-white py-2 px-4 rounded-md font-medium transition-all"
                        >
                            💾 Save Changes
                        </button>
                                                <button
                            type="button"
                            onClick={onClose}
                            className="flex-1 bg-gray-600 hover:bg-gray-700 text-white py-2 px-4 rounded-md font-medium transition-all"
                        >
                            ✕ Cancel
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}

// Report Modal Component
function ReportModal({ alerts, preferences, onClose }) {
    const [activeTab, setActiveTab] = useState('summary'); // 'summary' or 'stations'
    
    // Debug logging
    console.log('📋 ReportModal: Received alerts:', alerts);
    console.log('📋 ReportModal: Alerts length:', alerts?.length || 0);
    console.log('📋 ReportModal: Received preferences:', preferences);
    
    const currentDate = new Date().toLocaleString('en-US', {
        weekday: 'long',
        year: 'numeric',
        month: 'long',
        day: 'numeric',
        hour: '2-digit',
        minute: '2-digit'
    });

    // Calculate AQI statistics
    const currentAQI = alerts.length > 0 && alerts[0].aqi_current ? alerts[0].aqi_current : 0;
    console.log('📋 ReportModal: Current AQI:', currentAQI);
    
    const getAQIStatus = (aqi) => {
        if (aqi === 0) return { text: 'No Data', color: '#9CA3AF' };
        if (aqi === 1) return { text: 'Good', color: '#10B981' };
        if (aqi === 2) return { text: 'Moderate', color: '#FBBF24' };
        if (aqi === 3) return { text: 'Unhealthy for Sensitive Groups', color: '#F97316' };
        if (aqi === 4) return { text: 'Unhealthy', color: '#EF4444' };
        if (aqi === 5) return { text: 'Very Unhealthy', color: '#A855F7' };
        return { text: 'Unknown', color: '#9CA3AF' };
    };

    const aqiStatus = getAQIStatus(currentAQI);

    return (
        <div 
            className="fixed inset-0 bg-black/40 backdrop-blur-sm flex items-center justify-center z-[1100]"
            onClick={onClose}>
            <div 
                className="bg-gray-900/10 backdrop-blur-sm rounded-lg shadow-2xl border border-white/20 p-8 w-full max-w-4xl max-h-[90vh] overflow-y-auto mx-4"
                onClick={(e) => e.stopPropagation()}>
                
                {/* Header */}
                <div className="flex justify-between items-center mb-6 pb-4 border-b border-white/20">
                    <h2 className="text-3xl font-bold text-white flex items-center">
                        📋 Air Quality Report
                    </h2>
                    <button
                        onClick={onClose}
                        className="bg-red-600/20 hover:bg-red-600/40 border border-red-500/50 text-red-100 px-4 py-2 rounded-md font-medium transition-all">
                        ✕ Close
                    </button>
                </div>

                {/* Tab Navigation */}
                <div className="mb-6 flex space-x-2 border-b border-white/20">
                    <button
                        onClick={() => setActiveTab('summary')}
                        className={`px-6 py-3 font-semibold transition-all ${
                            activeTab === 'summary'
                                ? 'text-white border-b-2 border-blue-500 bg-blue-500/10'
                                : 'text-gray-400 hover:text-gray-200'
                        }`}>
                        Summary
                    </button>
                    <button
                        onClick={() => setActiveTab('stations')}
                        className={`px-6 py-3 font-semibold transition-all ${
                            activeTab === 'stations'
                                ? 'text-white border-b-2 border-blue-500 bg-blue-500/10'
                                : 'text-gray-400 hover:text-gray-200'
                        }`}>
                        NYC Area Air Quality
                    </button>
                    <button
                        onClick={() => setActiveTab('forecast')}
                        className={`px-6 py-3 font-semibold transition-all ${
                            activeTab === 'forecast'
                                ? 'text-white border-b-2 border-blue-500 bg-blue-500/10'
                                : 'text-gray-400 hover:text-gray-200'
                        }`}>
                        24-Hour Forecast
                    </button>
                    <button
                        onClick={() => setActiveTab('legends')}
                        className={`px-6 py-3 font-semibold transition-all ${
                            activeTab === 'legends'
                                ? 'text-white border-b-2 border-blue-500 bg-blue-500/10'
                                : 'text-gray-400 hover:text-gray-200'
                        }`}>
                        Data Sources & Legends
                    </button>
                </div>

                {/* Tab Content */}
                {activeTab === 'summary' ? (
                    <>
                {/* Report Timestamp */}
                <div className="mb-6 p-4 bg-gray-900/10 border border-blue-500/30 rounded-lg backdrop-blur-sm">
                    <p className="text-sm text-gray-200">
                        <span className="font-semibold text-white">Report Generated:</span> {currentDate}
                    </p>
                    <p className="text-sm text-gray-300 mt-1">
                        <span className="font-semibold text-white">Location:</span> New York City, NY
                    </p>
                </div>

                {/* Current Status Section */}
                <div className="mb-6 p-6 bg-gray-900/10 backdrop-blur-sm rounded-lg border-l-4" style={{ borderLeftColor: aqiStatus.color }}>
                    <h3 className="text-xl font-semibold text-white mb-4">🌍 Current Air Quality Status</h3>
                    <div className="grid grid-cols-2 gap-6">
                        <div>
                            <p className="text-xs text-gray-400 uppercase font-semibold mb-2 tracking-wide">Status</p>
                            <p className="text-4xl font-bold" style={{ color: aqiStatus.color }}>
                                {aqiStatus.text}
                            </p>
                        </div>
                        <div>
                            <p className="text-xs text-gray-400 uppercase font-semibold mb-2 tracking-wide">AQI Level</p>
                            <p className="text-4xl font-bold text-white">
                                {currentAQI > 0 ? currentAQI : 'N/A'}
                            </p>
                        </div>
                    </div>
                </div>

                {/* Active Alerts Summary */}
                <div className="mb-6 p-6 bg-gray-900/10 backdrop-blur-sm rounded-lg">
                    <h3 className="text-xl font-semibold text-white mb-4">🚨 Active Alerts Summary</h3>
                    {alerts.length > 0 ? (
                        <div className="space-y-3">
                            <div className="flex justify-between items-center p-3 bg-gray-900/15 rounded-lg">
                                <span className="text-gray-200">Total Active Alerts:</span>
                                <span className="text-2xl font-bold text-white">{alerts.length}</span>
                            </div>
                            <div className="grid grid-cols-3 gap-3">
                                <div className="p-3 bg-red-900/20 border border-red-500/30 rounded-lg text-center">
                                    <p className="text-xs text-gray-300 mb-1">Danger</p>
                                    <p className="text-xl font-bold text-red-400">
                                        {alerts.filter(a => a.severity === 'danger').length}
                                    </p>
                                </div>
                                <div className="p-3 bg-yellow-900/20 border border-yellow-500/30 rounded-lg text-center">
                                    <p className="text-xs text-gray-300 mb-1">Warning</p>
                                    <p className="text-xl font-bold text-yellow-400">
                                        {alerts.filter(a => a.severity === 'warning').length}
                                    </p>
                                </div>
                                <div className="p-3 bg-blue-900/20 border border-blue-500/30 rounded-lg text-center">
                                    <p className="text-xs text-gray-300 mb-1">Info</p>
                                    <p className="text-xl font-bold text-blue-400">
                                        {alerts.filter(a => a.severity === 'info').length}
                                    </p>
                                </div>
                            </div>
                        </div>
                    ) : (
                        <div className="p-4 bg-green-900/20 border border-green-500/30 rounded-lg text-center">
                            <p className="text-green-300 font-medium">✓ No active alerts at this time</p>
                            <p className="text-sm text-gray-400 mt-1">Air quality is within acceptable levels</p>
                        </div>
                    )}
                </div>

                {/* User Profile Section */}
                {preferences && (
                    <div className="mb-6 p-6 bg-gray-900/10 backdrop-blur-sm rounded-lg">
                        <h3 className="text-xl font-semibold text-white mb-4">👤 Your Health Profile</h3>
                        <div className="grid grid-cols-2 gap-4">
                            <div className="p-3 bg-gray-900/15 rounded-lg">
                                <p className="text-xs text-gray-400 uppercase mb-1">Health Profile</p>
                                <p className="text-lg font-medium text-white capitalize">{preferences.health_profile?.replace('_', ' ')}</p>
                            </div>
                            <div className="p-3 bg-gray-900/15 rounded-lg">
                                <p className="text-xs text-gray-400 uppercase mb-1">Alert Threshold</p>
                                <p className="text-lg font-medium text-white">AQI {preferences.alert_threshold}</p>
                            </div>
                        </div>
                        <div className="mt-3 p-3 bg-indigo-900/20 border border-indigo-500/30 rounded-lg">
                            <p className="text-sm text-gray-300">
                                📧 Email Notifications: 
                                <span className="ml-2 font-semibold text-white">
                                    {preferences.email_notifications ? 'Enabled' : 'Disabled'}
                                </span>
                            </p>
                        </div>
                    </div>
                )}

                {/* Recommendations */}
                {alerts.length > 0 && (
                    <div className="p-6 bg-gray-900/10 backdrop-blur-sm rounded-lg">
                        <h3 className="text-xl font-semibold text-white mb-4">💡 Recommendations</h3>
                        <div className="space-y-2">
                            {alerts[0].recommendations?.map((rec, index) => (
                                <div key={index} className="flex items-start p-3 bg-gray-900/15 rounded-lg">
                                    <span className="text-blue-400 mr-3">•</span>
                                    <span className="text-gray-200">{rec}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Footer */}
                <div className="mt-6 pt-4 border-t border-white/20 text-center">
                    <p className="text-xs text-gray-400">
                        This report is generated from real-time air quality monitoring data.
                        <br />
                        For medical advice, please consult with a healthcare professional.
                    </p>
                </div>
                </>
                ) : activeTab === 'stations' ? (
                    <NYCStationsTab />
                ) : activeTab === 'forecast' ? (
                    <ForecastTab preferences={preferences} />
                ) : (
                    <DataSourcesLegendsTab />
                )}
            </div>
        </div>
    );
}

// 24-Hour Forecast Tab Component
function ForecastTab({ preferences }) {
    const lat = preferences?.latitude || 40.7128;
    const lon = preferences?.longitude || -74.0060;

    return (
        <div className="space-y-6">
            <div className="p-6 bg-gray-900/10 backdrop-blur-sm rounded-lg border border-blue-500/30">
                <h3 className="text-xl font-semibold text-white mb-4">📈 24-Hour Air Quality Forecast</h3>
                <p className="text-sm text-gray-300 mb-6">
                    This forecast shows predicted air quality levels for the next 24 hours based on current atmospheric conditions,
                    pollutant dispersion models, and weather patterns. The Air Quality Index (AQI) scale ranges from 1 (Good) to 5 (Very Unhealthy).
                </p>
                
                <div className="bg-gray-900/20 p-4 rounded-lg">
                    <ForecastChart lat={lat} lon={lon} />
                </div>

                <div className="mt-6 p-4 bg-blue-900/20 border border-blue-500/30 rounded-lg">
                    <h4 className="text-md font-semibold text-white mb-3">📊 AQI Scale Reference</h4>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                        <div className="flex items-center space-x-3 p-3 bg-green-900/20 border border-green-500/30 rounded">
                            <div className="text-2xl font-bold text-green-400">1</div>
                            <div>
                                <p className="font-semibold text-green-300">Good</p>
                                <p className="text-xs text-gray-400">Air quality is satisfactory</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-3 p-3 bg-yellow-900/20 border border-yellow-500/30 rounded">
                            <div className="text-2xl font-bold text-yellow-400">2</div>
                            <div>
                                <p className="font-semibold text-yellow-300">Moderate</p>
                                <p className="text-xs text-gray-400">Acceptable for most people</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-3 p-3 bg-orange-900/20 border border-orange-500/30 rounded">
                            <div className="text-2xl font-bold text-orange-400">3</div>
                            <div>
                                <p className="font-semibold text-orange-300">Unhealthy for Sensitive</p>
                                <p className="text-xs text-gray-400">May affect sensitive groups</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-3 p-3 bg-red-900/20 border border-red-500/30 rounded">
                            <div className="text-2xl font-bold text-red-400">4</div>
                            <div>
                                <p className="font-semibold text-red-300">Unhealthy</p>
                                <p className="text-xs text-gray-400">Everyone may experience effects</p>
                            </div>
                        </div>
                        <div className="flex items-center space-x-3 p-3 bg-purple-900/20 border border-purple-500/30 rounded">
                            <div className="text-2xl font-bold text-purple-400">5</div>
                            <div>
                                <p className="font-semibold text-purple-300">Very Unhealthy</p>
                                <p className="text-xs text-gray-400">Health alert conditions</p>
                            </div>
                        </div>
                    </div>
                </div>

                <div className="mt-4 p-4 bg-gray-900/20 rounded-lg">
                    <p className="text-xs text-gray-400">
                        <span className="font-semibold text-gray-300">Data Source:</span> OpenWeatherMap Air Pollution API
                    </p>
                    <p className="text-xs text-gray-500 mt-1">
                        Forecast data is updated every hour and based on atmospheric models. Actual conditions may vary.
                    </p>
                </div>
            </div>
        </div>
    );
}

// NYC Stations Tab Component
function NYCStationsTab() {
    const stations = [
        { name: "Division Street", distance: 0.94, measuring: "PM2.5", active: false },
        { name: "E Houston St between Clinton St & Attorney St", distance: 2.12, measuring: "PM1", active: true },
        { name: "PS 19", distance: 2.64, measuring: "PM2.5", active: false },
        { name: "Jersey City Newport", distance: 3.04, measuring: "PM1", active: true },
        { name: "7th Ave and W 16th St", distance: 3.09, measuring: "PM1", active: true },
        { name: "Hamilton Park, Jersey City", distance: 3.84, measuring: "PM1", active: true },
        { name: "Jersey City FH", distance: 4.15, measuring: "PM2.5", active: true },
        { name: "Jersey City Heights", distance: 5.21, measuring: "PM1", active: false },
        { name: "Win Son", distance: 5.25, measuring: "PM1", active: true },
        { name: "Jersey City", distance: 5.52, measuring: "CO", active: true },
        { name: "Franklin Avenue", distance: 5.90, measuring: "PM2.5", active: false },
        { name: "NJBAM Test Weehawken", distance: 6.03, measuring: "PM1", active: true },
        { name: "Bklyn - PS274", distance: 6.84, measuring: "PM2.5", active: true },
        { name: "Union City High Scho", distance: 6.94, measuring: "PM2.5", active: true },
        { name: "DropHome", distance: 7.37, measuring: "PM1", active: true },
        { name: "54th St & Grand Ave [NYC Testbed Pilot]", distance: 7.72, measuring: "PM2.5", active: false },
        { name: "Caton Ave and Ocean Pkwy, Brooklyn", distance: 7.74, measuring: "PM1", active: true },
        { name: "54th St & Flushing [NYC Testbed Pilot]", distance: 7.77, measuring: "PM2.5", active: false },
        { name: "56th St & Grand Ave [NYC Testbed Pilot]", distance: 7.87, measuring: "PM2.5", active: false },
        { name: "56th St & Flushing [NYC Testbed Pilot]", distance: 7.88, measuring: "PM2.5", active: false },
        { name: "Metal fence on PS9 back campus [NYC Testbed Pilot]", distance: 7.88, measuring: "PM2.5", active: false },
        { name: "Closest to SA unit on PS9 campus", distance: 7.89, measuring: "PM2.5", active: false },
        { name: "57th St/Front of School [NYC Testbed Pilot]", distance: 7.94, measuring: "PM2.5", active: false },
        { name: "Bklyn - PS 314", distance: 7.97, measuring: "PM2.5", active: true },
        { name: "Maspeth", distance: 9.63, measuring: "PM2.5", active: true },
        { name: "Bayonne", distance: 11.18, measuring: "NO", active: true },
        { name: "CCNY", distance: 12.85, measuring: "O₃", active: true },
        { name: "Near Bay 50 St", distance: 13.92, measuring: "PM1", active: true },
        { name: "Port Richmond", distance: 14.18, measuring: "PM2.5", active: true },
        { name: "Bronx - IS52", distance: 14.43, measuring: "O₃", active: true },
        { name: "Bronx - IS74", distance: 15.14, measuring: "PM2.5", active: true },
        { name: "Morrisania", distance: 15.51, measuring: "PM2.5", active: true },
        { name: "Queens", distance: 15.55, measuring: "O₃", active: true },
        { name: "Newark Firehouse", distance: 15.78, measuring: "CO", active: false },
        { name: "State Dept of Environmental Conservation", distance: 15.88, measuring: "PM1", active: false },
        { name: "State Dept of Environmental Conservation", distance: 15.91, measuring: "PM1", active: false },
        { name: "State Dept of Environmental Conservation", distance: 15.91, measuring: "PM1", active: false },
        { name: "Fort Lee Near Road", distance: 16.01, measuring: "CO", active: true },
        { name: "Queens Near-road", distance: 16.14, measuring: "PM2.5", active: false },
        { name: "Manhattan/IS143", distance: 16.40, measuring: "PM2.5", active: true },
        { name: "Susan Wagner", distance: 16.41, measuring: "O₃", active: false },
        { name: "East Orange", distance: 17.13, measuring: "CO", active: false },
        { name: "Hillcrest, NY", distance: 17.23, measuring: "PM1", active: true },
        { name: "Leonia", distance: 17.57, measuring: "O₃", active: true },
        { name: "Elizabeth", distance: 18.48, measuring: "CO", active: false },
        { name: "Elizabeth Trailer", distance: 18.82, measuring: "CO", active: true },
        { name: "Pfizer Lab", distance: 20.34, measuring: "O₃", active: true },
        { name: "Bayside, NY 11361", distance: 20.99, measuring: "PM1", active: true },
        { name: "Bayside, NY", distance: 20.99, measuring: "PM1", active: false },
        { name: "Bayside, NY", distance: 20.99, measuring: "PM2.5", active: false },
        { name: "Downtown Montclair", distance: 21.10, measuring: "PM1", active: true },
        { name: "Montclair, NJ", distance: 22.59, measuring: "PM1", active: true },
        { name: "West Clinton Avenue Tenafly New Jersey", distance: 23.73, measuring: "PM1", active: true },
        { name: "West Clinton Avenue, Tenafly, NJ", distance: 23.73, measuring: "PM1", active: true },
        { name: "Carteret, NJ", distance: 24.19, measuring: "PM1", active: true },
        { name: "Rahway PM", distance: 25.81, measuring: "PM2.5", active: true },
        { name: "Paterson", distance: 26.62, measuring: "PM2.5", active: true },
        { name: "Springfield, NJ", distance: 27.15, measuring: "PM1", active: true },
        { name: "Larchmont, NY", distance: 32.88, measuring: "PM1", active: false },
        { name: "Ocean roof 1", distance: 33.50, measuring: "PM1", active: true },
        { name: "Madison NJ", distance: 35.06, measuring: "PM1", active: true },
        { name: "Eisenhower Park", distance: 35.49, measuring: "PM2.5", active: false },
        { name: "White Plains", distance: 42.87, measuring: "O₃", active: true },
        { name: "Ramapo", distance: 43.80, measuring: "O₃", active: true },
        { name: "Monmouth University", distance: 48.39, measuring: "O₃", active: true },
        { name: "Babylon", distance: 50.62, measuring: "O₃", active: true },
        { name: "Rockland Cty", distance: 52.21, measuring: "O₃", active: true },
        { name: "Chester", distance: 57.07, measuring: "NO", active: true }
    ];

    const totalStations = 68;
    const activeStations = stations.filter(s => s.active).length;
    const allPollutants = "PM2.5, PM1, RH, Temperature (C), PM0.3 count, PM10, CO, NO, NO₂, NOx, SO₂, O₃";

    return (
        <div className="space-y-6">
            {/* At-a-Glance Section */}
            <div className="p-6 bg-gray-900/10 backdrop-blur-sm rounded-lg border border-white/20">
                <h3 className="text-2xl font-bold text-white mb-6">📊 At-a-Glance</h3>
                
                <div className="grid grid-cols-3 gap-4 mb-6">
                    <div className="p-4 bg-gray-800/40 rounded-lg border border-green-500/30">
                        <p className="text-xs text-gray-400 uppercase mb-2">Network Status</p>
                        <p className="text-2xl font-bold text-green-400 flex items-center">
                            <span className="mr-2">✅</span> Active
                        </p>
                    </div>
                    <div className="p-4 bg-gray-800/40 rounded-lg border border-blue-500/30">
                        <p className="text-xs text-gray-400 uppercase mb-2">Monitoring Stations Online</p>
                        <p className="text-3xl font-bold text-white">
                            {activeStations} <span className="text-lg text-gray-400">of {totalStations}</span>
                        </p>
                    </div>
                    <div className="p-4 bg-gray-800/40 rounded-lg border border-purple-500/30 col-span-1">
                        <p className="text-xs text-gray-400 uppercase mb-2">Measuring</p>
                        <p className="text-sm text-gray-200 leading-relaxed">
                            {allPollutants}
                        </p>
                    </div>
                </div>
            </div>

            {/* Monitoring Stations Section */}
            <div className="p-6 bg-gray-900/10 backdrop-blur-sm rounded-lg border border-white/20">
                <h3 className="text-2xl font-bold text-white mb-4">📡 Monitoring Stations</h3>
                
                <div className="grid grid-cols-2 gap-4 mb-6">
                    <div className="p-4 bg-gray-800/40 rounded-lg">
                        <p className="text-xs text-gray-400 uppercase mb-1">Total Stations:</p>
                        <p className="text-3xl font-bold text-white">{totalStations}</p>
                    </div>
                    <div className="p-4 bg-gray-800/40 rounded-lg">
                        <p className="text-xs text-gray-400 uppercase mb-1">Active Stations:</p>
                        <p className="text-3xl font-bold text-green-400">{activeStations}</p>
                    </div>
                </div>

                <h4 className="text-lg font-semibold text-white mb-4">Nearby Stations</h4>
                <div className="max-h-[400px] overflow-y-auto space-y-3 pr-2">
                    {stations.map((station, index) => (
                        <div 
                            key={index}
                            className={`p-4 rounded-lg border ${
                                station.active 
                                    ? 'bg-gray-800/40 border-green-500/30' 
                                    : 'bg-gray-800/20 border-gray-500/30'
                            }`}>
                            <div className="flex justify-between items-start mb-2">
                                <h5 className="font-semibold text-white text-sm">{station.name}</h5>
                                <span className={`px-2 py-1 rounded text-xs font-bold ${
                                    station.active 
                                        ? 'bg-green-500/20 text-green-400' 
                                        : 'bg-gray-500/20 text-gray-400'
                                }`}>
                                    {station.active ? 'ACTIVE' : 'INACTIVE'}
                                </span>
                            </div>
                            <p className="text-xs text-gray-400 mb-1">
                                📍 {station.distance.toFixed(2)} km away
                            </p>
                            <p className="text-xs text-gray-300">
                                <span className="font-medium">Measuring:</span> {station.measuring}
                            </p>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

// Data Sources & Legends Tab Component
function DataSourcesLegendsTab() {
    return (
        <div className="space-y-6">
            {/* TEMPO NO₂ Legend */}
            <div className="p-6 bg-gray-900/10 backdrop-blur-sm rounded-lg border border-white/20">
                <h3 className="text-2xl font-bold text-white mb-6">🛰️ TEMPO NO₂ Legend</h3>
                
                <div className="space-y-4">
                    <div className="flex items-center space-x-4 p-4 bg-gray-800/40 rounded-lg">
                        <div className="w-8 h-8 rounded-full bg-red-500 flex-shrink-0"></div>
                        <div>
                            <p className="text-white font-semibold">NO₂ Measurement Point</p>
                            <p className="text-sm text-gray-400">Nitrogen Dioxide concentration data</p>
                        </div>
                    </div>
                    
                    <div className="p-4 bg-gray-800/40 rounded-lg">
                        <div className="mb-3">
                            <p className="text-sm text-gray-400 uppercase font-semibold mb-1">Units:</p>
                            <p className="text-lg text-white">molecules/cm²</p>
                        </div>
                        
                        <div className="mb-3">
                            <p className="text-sm text-gray-400 uppercase font-semibold mb-1">Scale:</p>
                            <p className="text-white">Values shown in scientific notation</p>
                            <p className="text-sm text-gray-300 mt-1">Example: 2.72e+14</p>
                        </div>
                        
                        <div className="mt-4 pt-4 border-t border-white/10">
                            <p className="text-xs text-gray-400">
                                <span className="font-semibold text-gray-300">Data source:</span> NASA TEMPO satellite
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                                Tropospheric Emissions: Monitoring of Pollution
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Surface Pressure Legend */}
            <div className="p-6 bg-gray-900/10 backdrop-blur-sm rounded-lg border border-white/20">
                <h3 className="text-2xl font-bold text-white mb-6">🌡️ Surface Pressure Legend</h3>
                
                <div className="space-y-4">
                    <div className="flex items-center space-x-4 p-4 bg-gray-800/40 rounded-lg">
                        <div className="w-8 h-8 rounded-full bg-blue-500 flex-shrink-0"></div>
                        <div>
                            <p className="text-white font-semibold">NOAA Station Data</p>
                            <p className="text-sm text-gray-400">Surface atmospheric pressure measurements</p>
                        </div>
                    </div>
                    
                    <div className="p-4 bg-gray-800/40 rounded-lg">
                        <div className="mb-3">
                            <p className="text-sm text-gray-400 uppercase font-semibold mb-1">Units:</p>
                            <p className="text-lg text-white">Pascals (Pa) / Hectopascals (hPa)</p>
                        </div>
                        
                        <div className="mb-3">
                            <p className="text-sm text-gray-400 uppercase font-semibold mb-1">Measurement:</p>
                            <p className="text-white">Atmospheric pressure at ground level</p>
                            <p className="text-sm text-gray-300 mt-1">Standard pressure: ~1013 hPa (sea level)</p>
                        </div>
                        
                        <div className="mt-4 pt-4 border-t border-white/10">
                            <p className="text-xs text-gray-400">
                                <span className="font-semibold text-gray-300">Data source:</span> NOAA Weather Stations
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                                National Oceanic and Atmospheric Administration
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Current Location Info */}
            <div className="p-6 bg-gray-900/10 backdrop-blur-sm rounded-lg border border-white/20">
                <h3 className="text-2xl font-bold text-white mb-6">📍 Current Location</h3>
                
                <div className="space-y-3">
                    <div className="p-4 bg-gray-800/40 rounded-lg">
                        <p className="text-sm text-gray-400 uppercase font-semibold mb-2">Location</p>
                        <p className="text-2xl text-white font-semibold">New York City, NY</p>
                    </div>
                    
                    <div className="p-4 bg-gray-800/40 rounded-lg">
                        <p className="text-sm text-gray-400 uppercase font-semibold mb-2">Coordinates</p>
                        <p className="text-lg text-white font-mono">40.7128, -74.0060</p>
                        <p className="text-xs text-gray-400 mt-1">Latitude, Longitude</p>
                    </div>
                </div>
            </div>

            {/* Wind Information Legend */}
            <div className="p-6 bg-gray-900/10 backdrop-blur-sm rounded-lg border border-white/20">
                <h3 className="text-2xl font-bold text-white mb-6">💨 Wind Information</h3>
                
                <div className="space-y-4">
                    <div className="flex items-center space-x-4 p-4 bg-gray-800/40 rounded-lg">
                        <div className="w-8 h-8 rounded-full bg-cyan-500 flex-shrink-0 flex items-center justify-center">
                            <span className="text-white text-lg">➜</span>
                        </div>
                        <div>
                            <p className="text-white font-semibold">Wind Data Indicators</p>
                            <p className="text-sm text-gray-400">Real-time wind speed and direction measurements</p>
                        </div>
                    </div>
                    
                    <div className="p-4 bg-gray-800/40 rounded-lg">
                        <div className="mb-4">
                            <p className="text-sm text-gray-400 uppercase font-semibold mb-2">Wind Speed</p>
                            <div className="space-y-2">
                                <div className="flex items-center justify-between p-2 bg-gray-700/30 rounded">
                                    <span className="text-gray-300">Units:</span>
                                    <span className="text-white font-semibold">m/s (meters per second) or mph</span>
                                </div>
                                <div className="flex items-center justify-between p-2 bg-gray-700/30 rounded">
                                    <span className="text-gray-300">Typical Range:</span>
                                    <span className="text-white font-semibold">0 - 30+ m/s</span>
                                </div>
                            </div>
                        </div>
                        
                        <div className="mb-4">
                            <p className="text-sm text-gray-400 uppercase font-semibold mb-2">Wind Direction</p>
                            <div className="space-y-2">
                                <div className="flex items-center justify-between p-2 bg-gray-700/30 rounded">
                                    <span className="text-gray-300">Units:</span>
                                    <span className="text-white font-semibold">Degrees (°) or Cardinal Direction</span>
                                </div>
                                <div className="grid grid-cols-2 gap-2 mt-2">
                                    <div className="p-2 bg-gray-700/30 rounded text-center">
                                        <p className="text-xs text-gray-400">N</p>
                                        <p className="text-sm text-white">0° / 360°</p>
                                    </div>
                                    <div className="p-2 bg-gray-700/30 rounded text-center">
                                        <p className="text-xs text-gray-400">E</p>
                                        <p className="text-sm text-white">90°</p>
                                    </div>
                                    <div className="p-2 bg-gray-700/30 rounded text-center">
                                        <p className="text-xs text-gray-400">S</p>
                                        <p className="text-sm text-white">180°</p>
                                    </div>
                                    <div className="p-2 bg-gray-700/30 rounded text-center">
                                        <p className="text-xs text-gray-400">W</p>
                                        <p className="text-sm text-white">270°</p>
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div className="mb-3">
                            <p className="text-sm text-gray-400 uppercase font-semibold mb-2">Wind Classification</p>
                            <div className="space-y-1 text-sm">
                                <div className="flex justify-between p-2 bg-green-900/20 border border-green-500/30 rounded">
                                    <span className="text-gray-300">Calm</span>
                                    <span className="text-green-400 font-semibold">0-2 m/s (0-4.5 mph)</span>
                                </div>
                                <div className="flex justify-between p-2 bg-blue-900/20 border border-blue-500/30 rounded">
                                    <span className="text-gray-300">Light Breeze</span>
                                    <span className="text-blue-400 font-semibold">2-5 m/s (4.5-11 mph)</span>
                                </div>
                                <div className="flex justify-between p-2 bg-yellow-900/20 border border-yellow-500/30 rounded">
                                    <span className="text-gray-300">Moderate Wind</span>
                                    <span className="text-yellow-400 font-semibold">5-10 m/s (11-22 mph)</span>
                                </div>
                                <div className="flex justify-between p-2 bg-orange-900/20 border border-orange-500/30 rounded">
                                    <span className="text-gray-300">Strong Wind</span>
                                    <span className="text-orange-400 font-semibold">10-17 m/s (22-38 mph)</span>
                                </div>
                                <div className="flex justify-between p-2 bg-red-900/20 border border-red-500/30 rounded">
                                    <span className="text-gray-300">Gale/Storm</span>
                                    <span className="text-red-400 font-semibold">17+ m/s (38+ mph)</span>
                                </div>
                            </div>
                        </div>
                        
                        <div className="mt-4 pt-4 border-t border-white/10">
                            <p className="text-xs text-gray-400">
                                <span className="font-semibold text-gray-300">Data sources:</span> NOAA Weather Stations & Weather APIs
                            </p>
                            <p className="text-xs text-gray-500 mt-1">
                                Wind data influences air pollutant dispersion and distribution patterns
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            {/* Additional Information */}
            <div className="p-6 bg-blue-900/20 border border-blue-500/30 rounded-lg backdrop-blur-sm">
                <h4 className="text-lg font-semibold text-white mb-3">ℹ️ About the Data</h4>
                <div className="space-y-2 text-sm text-gray-300">
                    <p>
                        <span className="font-semibold text-white">TEMPO:</span> NASA's first space-based instrument to monitor air pollutants hourly during daytime across North America.
                    </p>
                    <p>
                        <span className="font-semibold text-white">NOAA:</span> Provides real-time surface weather observations including atmospheric pressure, wind, and temperature from ground stations.
                    </p>
                    <p>
                        <span className="font-semibold text-white">Wind Data:</span> Critical for understanding air quality patterns as wind disperses pollutants and affects concentration levels.
                    </p>
                    <p className="text-xs text-gray-400 mt-3">
                        Data is updated in near real-time and may be subject to quality control adjustments.
                    </p>
                </div>
            </div>
        </div>
    );
}
