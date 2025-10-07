'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { register } from '../../lib/auth';
import { useAuth } from '../../contexts/AuthContext';

export default function RegisterForm() {
    const [formData, setFormData] = useState({
        name: '',
        email: '',
        password: '',
        confirmPassword: '',
        health_profile: 'general'
    });
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState('');
    const router = useRouter();
    const { setUser } = useAuth();

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setLoading(true);
        setError('');

        if (formData.password !== formData.confirmPassword) {
            setError('Passwords do not match');
            setLoading(false);
            return;
        }

        if (formData.password.length < 8) {
            setError('Password must be at least 8 characters long');
            setLoading(false);
            return;
        }

        if (formData.password.length > 72) {
            setError('Password is too long (maximum 72 characters)');
            setLoading(false);
            return;
        }

        try {
            const { confirmPassword, ...registrationData } = formData;
            const response = await register(registrationData);
            setUser(response.user);
            router.push('/dashboard');
        } catch (err) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="relative h-screen w-screen overflow-hidden">
            {/* Video Background */}
            <video
                autoPlay
                loop
                muted
                src="/vid/earth.mp4"
                className="absolute top-0 left-0 w-full h-full object-cover z-0"
            />
            
            {/* Dark Overlay */}
            <div className="absolute top-0 left-0 w-full h-full bg-black/50 z-10" />
            
            {/* Centered Form Container */}
            <div className="relative z-20 flex items-center justify-center h-full px-4 sm:px-6 lg:px-8 py-12 overflow-y-auto">
                <div className="max-w-md w-full space-y-8 my-auto">
                    <div>
                        <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
                            Create your Zeus account
                        </h2>
                        <p className="mt-2 text-center text-sm text-gray-200">
                            Get started with personalized air quality monitoring
                        </p>
                    </div>
                    <form className="mt-8 space-y-6 bg-white/10 backdrop-blur-md rounded-lg shadow-lg p-8 border border-white/20" onSubmit={handleSubmit}>
                    {error && (
                        <div className="bg-red-500/20 border border-red-400/50 text-red-100 px-4 py-3 rounded backdrop-blur-sm">
                            {error}
                        </div>
                    )}
                    <div className="space-y-4">
                        <div>
                            <label htmlFor="name" className="block text-sm font-medium text-gray-200">
                                Full Name
                            </label>
                            <input
                                id="name"
                                name="name"
                                type="text"
                                required
                                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-white/30 placeholder-gray-300 text-white bg-white/10 rounded-md focus:outline-none focus:ring-indigo-400 focus:border-indigo-400 sm:text-sm backdrop-blur-sm"
                                placeholder="Enter your full name"
                                value={formData.name}
                                onChange={handleChange}
                            />
                        </div>

                        <div>
                            <label htmlFor="email" className="block text-sm font-medium text-gray-200">
                                Email Address
                            </label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                required
                                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-white/30 placeholder-gray-300 text-white bg-white/10 rounded-md focus:outline-none focus:ring-indigo-400 focus:border-indigo-400 sm:text-sm backdrop-blur-sm"
                                placeholder="Enter your email"
                                value={formData.email}
                                onChange={handleChange}
                            />
                        </div>

                        <div>
                            <label htmlFor="health_profile" className="block text-sm font-medium text-gray-200">
                                Health Profile
                            </label>
                            <select
                                id="health_profile"
                                name="health_profile"
                                className="mt-1 block w-full px-3 py-2 border border-white/30 bg-white/10 text-white rounded-md shadow-sm focus:outline-none focus:ring-indigo-400 focus:border-indigo-400 sm:text-sm backdrop-blur-sm"
                                value={formData.health_profile}
                                onChange={handleChange}
                            >
                                <option value="general" className="bg-gray-800">General Population</option>
                                <option value="sensitive" className="bg-gray-800">Sensitive to Air Pollution</option>
                                <option value="high_risk" className="bg-gray-800">High Risk (Asthma, Heart Conditions)</option>
                            </select>
                            <p className="mt-1 text-xs text-gray-300">
                                This helps us customize alert thresholds for your health needs
                            </p>
                        </div>

                        <div>
                            <label htmlFor="password" className="block text-sm font-medium text-gray-200">
                                Password
                            </label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                required
                                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-white/30 placeholder-gray-300 text-white bg-white/10 rounded-md focus:outline-none focus:ring-indigo-400 focus:border-indigo-400 sm:text-sm backdrop-blur-sm"
                                placeholder="Enter your password (min 8 characters)"
                                value={formData.password}
                                onChange={handleChange}
                            />
                        </div>

                        <div>
                            <label htmlFor="confirmPassword" className="block text-sm font-medium text-gray-200">
                                Confirm Password
                            </label>
                            <input
                                id="confirmPassword"
                                name="confirmPassword"
                                type="password"
                                required
                                className="mt-1 appearance-none relative block w-full px-3 py-2 border border-white/30 placeholder-gray-300 text-white bg-white/10 rounded-md focus:outline-none focus:ring-indigo-400 focus:border-indigo-400 sm:text-sm backdrop-blur-sm"
                                placeholder="Confirm your password"
                                value={formData.confirmPassword}
                                onChange={handleChange}
                            />
                        </div>
                    </div>

                    <div>
                        <button
                            type="submit"
                            disabled={loading}
                            className="group relative w-full flex justify-center py-2 px-4 border border-transparent text-sm font-medium rounded-md text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50"
                        >
                            {loading ? 'Creating account...' : 'Create Account'}
                        </button>
                    </div>

                    <div className="text-center">
                        <span className="text-sm text-gray-200">
                            Already have an account?{' '}
                            <a href="/auth/login" className="font-medium text-indigo-400 hover:text-indigo-300">
                                Sign in here
                            </a>
                        </span>
                    </div>
                </form>
            </div>
        </div>
        </div>
    );
}