'use client';

import { createContext, useContext, useEffect, useState } from 'react';
import { getUser, getCurrentUser, isAuthenticated, removeToken } from '../lib/auth';

const AuthContext = createContext();

export const useAuth = () => {
    const context = useContext(AuthContext);
    if (!context) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
};

export const AuthProvider = ({ children }) => {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const initializeAuth = async () => {
            try {
                if (isAuthenticated()) {
                    const savedUser = getUser();
                    if (savedUser) {
                        setUser(savedUser);
                    } else {
                        // Verify token with server
                        const currentUser = await getCurrentUser();
                        setUser(currentUser);
                    }
                }
            } catch (error) {
                console.error('Auth initialization error:', error);
                removeToken();
            } finally {
                setLoading(false);
            }
        };

        initializeAuth();
    }, []);

    const value = {
        user,
        setUser,
        loading,
        isAuthenticated: isAuthenticated(),
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
};