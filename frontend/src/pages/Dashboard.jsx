import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Droplet, LogOut, Heart, User } from 'lucide-react';
import axios from 'axios';

function Dashboard() {
    const [user, setUser] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const token = localStorage.getItem('access_token');

        if (!token) {
            navigate('/login');
            return;
        }

        // Set axios default header
        axios.defaults.headers.common['Authorization'] = `Bearer ${token}`;

        // Fetch user profile
        fetchProfile();
    }, [navigate]);

    const fetchProfile = async () => {
        try {
            // This endpoint doesn't exist yet, but shows the pattern
            const response = await axios.get('/api/v1/auth/me/');
            setUser(response.data);
        } catch (err) {
            if (err.response?.status === 401) {
                handleLogout();
            }
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        delete axios.defaults.headers.common['Authorization'];
        navigate('/login');
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-lifeline-cream flex items-center justify-center">
                <div className="text-center">
                    <Droplet className="w-12 h-12 text-lifeline-crimson mx-auto mb-4 animate-pulse" fill="currentColor" />
                    <p className="text-lifeline-gray">Loading...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-lifeline-cream">
            {/* Header */}
            <header className="bg-white shadow-sm border-b border-blood-100">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-2">
                            <Droplet className="w-8 h-8 text-lifeline-crimson" fill="currentColor" />
                            <h1 className="text-2xl font-bold text-lifeline-crimson">Lifeline</h1>
                        </div>
                        <button
                            onClick={handleLogout}
                            className="flex items-center space-x-2 text-lifeline-gray hover:text-lifeline-crimson transition-colors"
                        >
                            <LogOut className="w-5 h-5" />
                            <span>Logout</span>
                        </button>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-8">
                    <h2 className="text-3xl font-bold text-lifeline-dark mb-2">
                        Welcome back! 👋
                    </h2>
                    <p className="text-lifeline-gray">
                        Ready to save lives today?
                    </p>
                </div>

                <div className="grid md:grid-cols-3 gap-6 mb-8">
                    {/* Quick Stats */}
                    <div className="card">
                        <div className="flex items-center space-x-4">
                            <div className="bg-blood-50 p-3 rounded-full">
                                <Heart className="w-6 h-6 text-lifeline-crimson" fill="currentColor" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold text-lifeline-dark">12</p>
                                <p className="text-sm text-lifeline-gray">Total Donations</p>
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <div className="flex items-center space-x-4">
                            <div className="bg-medical-50 p-3 rounded-full">
                                <Droplet className="w-6 h-6 text-medical-600" fill="currentColor" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold text-lifeline-dark">O+</p>
                                <p className="text-sm text-lifeline-gray">Blood Type</p>
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <div className="flex items-center space-x-4">
                            <div className="bg-blood-50 p-3 rounded-full">
                                <User className="w-6 h-6 text-lifeline-crimson" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold text-lifeline-dark">Active</p>
                                <p className="text-sm text-lifeline-gray">Status</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Recent Requests */}
                <div className="card">
                    <h3 className="text-xl font-bold text-lifeline-dark mb-4">Recent Blood Requests</h3>
                    <div className="space-y-4">
                        <div className="p-4 bg-lifeline-cream rounded-lg border border-gray-100">
                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <p className="font-semibold text-lifeline-dark">Lagos University Teaching Hospital</p>
                                    <p className="text-sm text-lifeline-gray">Needs: O+ Blood</p>
                                </div>
                                <span className="px-3 py-1 bg-blood-100 text-lifeline-crimson text-sm font-semibold rounded-full">
                                    Urgent
                                </span>
                            </div>
                            <p className="text-sm text-lifeline-gray mb-3">
                                Emergency surgery patient requires O+ blood immediately.
                            </p>
                            <button className="btn-primary w-full sm:w-auto">
                                Respond to Request
                            </button>
                        </div>

                        <div className="p-4 bg-lifeline-cream rounded-lg border border-gray-100">
                            <div className="flex justify-between items-start mb-2">
                                <div>
                                    <p className="font-semibold text-lifeline-dark">General Hospital Ikeja</p>
                                    <p className="text-sm text-lifeline-gray">Needs: A+ Blood</p>
                                </div>
                                <span className="px-3 py-1 bg-medical-100 text-medical-600 text-sm font-semibold rounded-full">
                                    Open
                                </span>
                            </div>
                            <p className="text-sm text-lifeline-gray mb-3">
                                Multiple patients in need of A+ blood type for scheduled procedures.
                            </p>
                            <button className="btn-secondary w-full sm:w-auto">
                                View Details
                            </button>
                        </div>
                    </div>

                    <div className="mt-6 text-center">
                        <button className="text-lifeline-crimson hover:underline font-semibold">
                            View All Requests →
                        </button>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default Dashboard;
