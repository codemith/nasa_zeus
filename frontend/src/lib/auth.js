// Use environment variable or fallback to localhost for development
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Token management
export const getToken = () => {
    if (typeof window !== 'undefined') {
        return localStorage.getItem('access_token');
    }
    return null;
};

export const setToken = (token) => {
    if (typeof window !== 'undefined') {
        localStorage.setItem('access_token', token);
    }
};

export const removeToken = () => {
    if (typeof window !== 'undefined') {
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
    }
};

export const getUser = () => {
    if (typeof window !== 'undefined') {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }
    return null;
};

export const setUser = (user) => {
    if (typeof window !== 'undefined') {
        localStorage.setItem('user', JSON.stringify(user));
    }
};

// API helper functions
const apiRequest = async (endpoint, options = {}) => {
    const url = `${API_BASE_URL}${endpoint}`;
    const token = getToken();

    const headers = {
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        ...options.headers,
    };

    if (token) {
        headers.Authorization = `Bearer ${token}`;
    }

    console.log('Making API request to:', url);
    console.log('Request headers:', headers);
    console.log('Request options:', options);

    try {
        const response = await fetch(url, {
            ...options,
            headers,
            mode: 'cors', // Explicitly set CORS mode
            credentials: 'omit', // Don't send credentials unless needed
        });

        console.log('Response status:', response.status);
        console.log('Response headers:', response.headers);

        if (!response.ok) {
            let errorMessage = 'Something went wrong';
            try {
                const errorData = await response.json();
                errorMessage = errorData.detail || errorData.message || errorMessage;
            } catch (e) {
                // If response is not JSON, use status text
                errorMessage = response.statusText || `HTTP ${response.status}`;
            }
            throw new Error(errorMessage);
        }

        return response.json();
    } catch (error) {
        console.error('API request failed:', error);
        throw error;
    }
};

// Authentication functions
export const register = async (userData) => {
    try {
        console.log('Attempting registration with:', userData);
        console.log('API URL:', `${API_BASE_URL}/auth/register`);

        const response = await apiRequest('/auth/register', {
            method: 'POST',
            body: JSON.stringify(userData),
        });

        if (response.access_token) {
            setToken(response.access_token);
            setUser(response.user);
        }

        console.log('Registration successful');
        return response;
    } catch (error) {
        console.error('Registration error:', error);
        throw error;
    }
};

export const login = async (credentials) => {
    const response = await apiRequest('/auth/login', {
        method: 'POST',
        body: JSON.stringify(credentials),
    });

    if (response.access_token) {
        setToken(response.access_token);
        setUser(response.user);
    }

    return response;
};

export const logout = () => {
    removeToken();
    window.location.href = '/auth/login';
};

export const getCurrentUser = async () => {
    try {
        const user = await apiRequest('/auth/me');
        setUser(user);
        return user;
    } catch (error) {
        removeToken();
        throw error;
    }
};

// User preferences
export const getUserPreferences = async () => {
    return apiRequest('/api/user/preferences');
};

export const updateUserPreferences = async (preferences) => {
    return apiRequest('/api/user/preferences', {
        method: 'PUT',
        body: JSON.stringify(preferences),
    });
};

// User alerts
export const getUserAlerts = async () => {
    return apiRequest('/api/user/alerts');
};

// Current air quality
export const getCurrentAQI = async () => {
    try {
        console.log('Fetching current AQI...');
        const result = await apiRequest('/api/user/current-aqi');
        console.log('Current AQI result:', result);
        return result;
    } catch (error) {
        console.error('getCurrentAQI error:', error);
        // Return a fallback object instead of throwing
        return {
            aqi: null,
            source: "Error",
            location: "Atlanta, GA",
            description: "Unable to load air quality data",
            error: error.message
        };
    }
};

export const isAuthenticated = () => {
    const token = getToken();
    if (!token) return false;

    try {
        const payload = JSON.parse(atob(token.split('.')[1]));
        return payload.exp > Date.now() / 1000;
    } catch {
        return false;
    }
};