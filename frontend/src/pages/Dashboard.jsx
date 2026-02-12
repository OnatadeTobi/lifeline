import { useState, useEffect } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Droplet, Heart, User, Plus, List, Activity, MapPin } from 'lucide-react';
import api from '../utils/api';
import { getUserRole, parseJwt, getAccessToken } from '../utils/auth';
import Navbar from '../components/Navbar';

function Dashboard() {
    const [profile, setProfile] = useState(null);
    const [requestCount, setRequestCount] = useState(0);
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

        const tokenData = parseJwt(token);
        fetchProfile(tokenData);
    }, [navigate]);

    const fetchProfile = async (tokenData) => {
        try {
            const endpoint = isHospital ? '/hospitals/profile/' : '/donors/profile/';
            const response = await api.get(endpoint);
            setProfile(response.data);

            try {
                const reqRes = await api.get('/requests/');
                const reqData = reqRes.data.results || reqRes.data;
                setRequestCount(Array.isArray(reqData) ? reqData.length : 0);
            } catch {
                // Not critical
            }
        } catch (err) {
            console.error('Failed to fetch profile:', err);
            setProfile({
                email: tokenData?.email || 'User',
                role: tokenData?.role || userRole,
            });
        } finally {
            setLoading(false);
        }
    };

    const getDisplayName = () => {
        if (isHospital) return profile?.name || '';
        return '';
    };

    const getPrimaryLocation = () => {
        if (!isHospital || !profile) return 'N/A';
        return profile?.primary_location_detail?.name || 'N/A';
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-lifeline-cream">
                <Navbar />
                <div className="flex items-center justify-center py-32">
                    <div className="text-center">
                        <Droplet className="w-12 h-12 text-lifeline-crimson mx-auto mb-4 animate-pulse" fill="currentColor" />
                        <p className="text-lifeline-gray">Loading...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-lifeline-cream">
            <Navbar />

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="mb-8 animate-fade-in">
                    <h2 className="text-3xl font-bold text-lifeline-dark mb-2">
                        Welcome back{getDisplayName() ? `, ${getDisplayName()}` : ''}! 👋
                    </h2>
                    <p className="text-lifeline-gray">
                        {isHospital
                            ? 'Manage your blood requests and find donors'
                            : 'Ready to save lives today?'}
                    </p>
                </div>

                {/* Quick Stats */}
                <div className="grid md:grid-cols-3 gap-6 mb-8">
                    <div className="card animate-fade-in" style={{ animationDelay: '0.05s' }}>
                        <div className="flex items-center space-x-4">
                            <div className="bg-blood-50 p-3 rounded-full">
                                <Heart className="w-6 h-6 text-lifeline-crimson" fill="currentColor" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold text-lifeline-dark">{requestCount}</p>
                                <p className="text-sm text-lifeline-gray">
                                    {isHospital ? 'Total Requests' : 'Requests Available'}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="card animate-fade-in" style={{ animationDelay: '0.1s' }}>
                        <div className="flex items-center space-x-4">
                            <div className="bg-medical-50 p-3 rounded-full">
                                {isHospital
                                    ? <MapPin className="w-6 h-6 text-medical-600" />
                                    : <Droplet className="w-6 h-6 text-medical-600" fill="currentColor" />
                                }
                            </div>
                            <div>
                                <p className="text-2xl font-bold text-lifeline-dark">
                                    {isHospital ? getPrimaryLocation() : (profile?.blood_type || 'N/A')}
                                </p>
                                <p className="text-sm text-lifeline-gray">
                                    {isHospital ? 'Primary Location' : 'Blood Type'}
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="card animate-fade-in" style={{ animationDelay: '0.15s' }}>
                        <div className="flex items-center space-x-4">
                            <div className="bg-blood-50 p-3 rounded-full">
                                <User className="w-6 h-6 text-lifeline-crimson" />
                            </div>
                            <div>
                                <p className="text-2xl font-bold text-lifeline-dark">
                                    {isHospital
                                        ? (profile?.is_verified ? 'Verified' : 'Unverified')
                                        : (profile?.is_available ? 'Available' : 'Unavailable')}
                                </p>
                                <p className="text-sm text-lifeline-gray">
                                    {isHospital ? 'Verification Status' : 'Donation Status'}
                                </p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="grid md:grid-cols-2 gap-6 mb-8">
                    {isHospital ? (
                        <>
                            <Link to="/create-request" className="card hover:shadow-xl hover:-translate-y-0.5 transition-all group animate-fade-in" style={{ animationDelay: '0.2s' }}>
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
                            <Link to="/requests" className="card hover:shadow-xl hover:-translate-y-0.5 transition-all group animate-fade-in" style={{ animationDelay: '0.25s' }}>
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
                            <Link to="/requests" className="card hover:shadow-xl hover:-translate-y-0.5 transition-all group animate-fade-in" style={{ animationDelay: '0.2s' }}>
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
                            <div className="card animate-fade-in" style={{ animationDelay: '0.25s' }}>
                                <div className="flex items-center space-x-4">
                                    <div className="bg-medical-600 p-3 rounded-full">
                                        <Heart className="w-6 h-6 text-white" />
                                    </div>
                                    <div>
                                        <h3 className="text-lg font-bold text-lifeline-dark">
                                            {profile?.is_available ? 'You are Available' : 'You are Unavailable'}
                                        </h3>
                                        <p className="text-sm text-lifeline-gray">
                                            {profile?.is_eligible
                                                ? 'You are eligible to donate'
                                                : 'Check eligibility requirements'}
                                        </p>
                                    </div>
                                </div>
                            </div>
                        </>
                    )}
                </div>

                {/* Role Badge */}
                <div className="card text-center animate-fade-in" style={{ animationDelay: '0.3s' }}>
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
