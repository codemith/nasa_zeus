'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { login } from '../../lib/auth';
import { useAuth } from '../../contexts/AuthContext';

export default function LoginForm() {
    const [formData, setFormData] = useState({
        email: '',
        password: ''
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

        try {
            const response = await login(formData);
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
            <div className="relative z-20 flex items-center justify-center h-full px-4 sm:px-6 lg:px-8">
                <div className="max-w-md w-full space-y-8">
                    <div>
                        <h2 className="mt-6 text-center text-3xl font-extrabold text-white">
                            Sign in to Zeus Air Quality
                        </h2>
                        <p className="mt-2 text-center text-sm text-gray-200">
                            Get personalized air quality alerts for New York City   
                        </p>
                    </div>
                    <form className="mt-8 space-y-6 bg-white/10 backdrop-blur-md rounded-lg shadow-lg p-8 border border-white/20" onSubmit={handleSubmit}>
                    {error && (
                        <div className="bg-red-500/20 border border-red-400/50 text-red-100 px-4 py-3 rounded backdrop-blur-sm">
                            {error}
                        </div>
                    )}
                    <div className="rounded-md shadow-sm -space-y-px">
                        <div>
                            <label htmlFor="email" className="sr-only">
                                Email address
                            </label>
                            <input
                                id="email"
                                name="email"
                                type="email"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-white/30 placeholder-gray-300 text-white bg-white/10 rounded-t-md focus:outline-none focus:ring-indigo-400 focus:border-indigo-400 focus:z-10 sm:text-sm backdrop-blur-sm"
                                placeholder="Email address"
                                value={formData.email}
                                onChange={handleChange}
                            />
                        </div>
                        <div>
                            <label htmlFor="password" className="sr-only">
                                Password
                            </label>
                            <input
                                id="password"
                                name="password"
                                type="password"
                                required
                                className="appearance-none rounded-none relative block w-full px-3 py-2 border border-white/30 placeholder-gray-300 text-white bg-white/10 rounded-b-md focus:outline-none focus:ring-indigo-400 focus:border-indigo-400 focus:z-10 sm:text-sm backdrop-blur-sm"
                                placeholder="Password"
                                value={formData.password}
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
                            {loading ? 'Signing in...' : 'Sign in'}
                        </button>
                    </div>

                    <div className="text-center">
                        <span className="text-sm text-gray-200">
                            Don't have an account?{' '}
                            <a href="/auth/register" className="font-medium text-indigo-400 hover:text-indigo-300">
                                Register here
                            </a>
                        </span>
                    </div>
                </form>
            </div>
        </div>
        </div>
    );
}