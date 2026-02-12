import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Droplet, LogOut, Heart, User, Plus, List, Activity } from 'lucide-react';
import api from '../utils/api';
import { getUserRole, parseJwt, getAccessToken, logout } from '../utils/auth';

function Dashboard() {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();
    const userRole = getUserRole();
    const isHospital = userRole === 'HOSPITAL';

    useEffect(() => {
        const token = getAccessToken();

        if (!token) {
            navigate('/login');
            return;
        }

        // Get basic info from JWT token
        const tokenData = parseJwt(token);

        // Fetch full profile from the appropriate endpoint
        fetchProfile(tokenData);
    }, [navigate]);

    const fetchProfile = async (tokenData) => {
        try {
            const endpoint = isHospital ? '/hospitals/profile/' : '/donors/profile/';
            const response = await api.get(endpoint);
            setProfile(response.data);
        } catch (err) {
            console.error('Failed to fetch profile:', err);
            // Still show dashboard with basic info from token
            setProfile({
                email: tokenData?.email || 'User',
                role: tokenData?.role || userRole,
            });
        } finally {
            setLoading(false);
        }
    };

    const handleLogout = () => {
        logout();
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
                        <div className="flex items-center space-x-4">
                            <Link to="/requests" className="text-lifeline-gray hover:text-lifeline-crimson transition-colors">
                                Requests
                            </Link>
                            <button
                                onClick={handleLogout}
                                className="flex items-center space-x-2 text-lifeline-gray hover:text-lifeline-crimson transition-colors"
                            >
                                <LogOut className="w-5 h-5" />
                                <span>Logout</span>
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-8">
                    <h2 className="text-3xl font-bold text-lifeline-dark mb-2">
                        Welcome back{profile?.first_name ? `, ${profile.first_name}` : profile?.name ? `, ${profile.name}` : ''}! 👋
                    </h2>
                    <p className="text-lifeline-gray">
                        {isHospital
                            ? 'Manage your blood requests and find donors'
                            : 'Ready to save lives today?'}
                    </p>
                </div>

                {/* Quick Stats */}
                <div className="grid md:grid-cols-3 gap-6 mb-8">
                    <div className="card">
                        <div className="flex items-center space-x-4">
                            <div className="bg-blood-50 p-3 rounded-full">
                                <Heart className="w-6 h-6 text-lifeline-crimson" fill="currentColor" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold text-lifeline-dark">
                                    {isHospital ? (profile?.total_requests || 0) : (profile?.total_donations || 0)}
                                </p>
                                <p className="text-sm text-lifeline-gray">
                                    {isHospital ? 'Total Requests' : 'Total Donations'}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <div className="flex items-center space-x-4">
                            <div className="bg-medical-50 p-3 rounded-full">
                                <Droplet className="w-6 h-6 text-medical-600" fill="currentColor" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold text-lifeline-dark">
                                    {isHospital ? (profile?.primary_location_name || 'N/A') : (profile?.blood_type || 'N/A')}
                                </p>
                                <p className="text-sm text-lifeline-gray">
                                    {isHospital ? 'Primary Location' : 'Blood Type'}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="card">
                        <div className="flex items-center space-x-4">
                            <div className="bg-blood-50 p-3 rounded-full">
                                <User className="w-6 h-6 text-lifeline-crimson" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold text-lifeline-dark">
                                    {isHospital ? 'Hospital' : (profile?.is_available ? 'Available' : 'Unavailable')}
                                </p>
                                <p className="text-sm text-lifeline-gray">
                                    {isHospital ? 'Account Type' : 'Status'}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="grid md:grid-cols-2 gap-6 mb-8">
                    {isHospital ? (
                        <>
                            <Link to="/create-request" className="card hover:shadow-lg transition-shadow group">
                                <div className="flex items-center space-x-4">
                                    <div className="bg-lifeline-crimson p-3 rounded-full group-hover:scale-110 transition-transform">
                                        <Plus className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-lifeline-dark">Create Blood Request</h3>
                                        <p className="text-sm text-lifeline-gray">Post a new request and find compatible donors</p>
                                    </div>
                                </div>
                            </Link>
                            <Link to="/requests" className="card hover:shadow-lg transition-shadow group">
                                <div className="flex items-center space-x-4">
                                    <div className="bg-medical-600 p-3 rounded-full group-hover:scale-110 transition-transform">
                                        <List className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-lifeline-dark">My Requests</h3>
                                        <p className="text-sm text-lifeline-gray">View and manage your blood requests</p>
                                    </div>
                                </div>
                            </Link>
                        </>
                    ) : (
                        <>
                            <Link to="/requests" className="card hover:shadow-lg transition-shadow group">
                                <div className="flex items-center space-x-4">
                                    <div className="bg-lifeline-crimson p-3 rounded-full group-hover:scale-110 transition-transform">
                                        <Activity className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-lifeline-dark">Browse Requests</h3>
                                        <p className="text-sm text-lifeline-gray">Find blood requests in your area</p>
                                    </div>
                                </div>
                            </Link>
                            <div className="card">
                                <div className="flex items-center space-x-4">
                                    <div className="bg-medical-600 p-3 rounded-full">
                                        <Heart className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-lifeline-dark">
                                            {profile?.is_available ? 'You are Available' : 'You are Unavailable'}
                                        </h3>
                                        <p className="text-sm text-lifeline-gray">
                                            {profile?.is_available
                                                ? 'Hospitals can find you for donations'
                                                : 'Toggle availability to receive requests'}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </>
                    )}
                </div>

                {/* Role Badge */}
                <div className="card text-center">
                    <div className="inline-flex items-center px-4 py-2 bg-blood-50 rounded-full">
                        <Droplet className="w-4 h-4 text-lifeline-crimson mr-2" fill="currentColor" />
                        <span className="text-sm font-semibold text-lifeline-crimson">
                            {isHospital ? 'Hospital Account' : 'Donor Account'} • {profile?.email || 'User'}
                        </span>
                    </div>
                </div>
            </main>
        </div>
    );
}

export default Dashboard;
