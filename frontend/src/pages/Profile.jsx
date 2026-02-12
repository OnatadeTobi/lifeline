import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    Droplet, Phone, Mail, MapPin, Calendar, Shield, Building,
    Heart, ToggleLeft, ToggleRight, Clock, CheckCircle, AlertCircle
} from 'lucide-react';
import api from '../utils/api';
import { getUserRole, getAccessToken } from '../utils/auth';
import { useNotification } from '../components/NotificationContext';
import Navbar from '../components/Navbar';
import BloodTypeBadge from '../components/BloodTypeBadge';

function Profile() {
    const [profile, setProfile] = useState(null);
    const [loading, setLoading] = useState(true);
    const [toggling, setToggling] = useState(false);
    const navigate = useNavigate();
    const userRole = getUserRole();
    const isHospital = userRole === 'HOSPITAL';
    const { success, error } = useNotification();

    useEffect(() => {
        if (!getAccessToken()) {
            navigate('/login');
            return;
        }
        fetchProfile();
    }, [navigate]);

    const fetchProfile = async () => {
        try {
            const endpoint = isHospital ? '/hospitals/profile/' : '/donors/profile/';
            const response = await api.get(endpoint);
            setProfile(response.data);
        } catch (err) {
            console.error('Failed to load profile:', err);
            error('Failed to load profile');
        } finally {
            setLoading(false);
        }
    };

    const handleToggleAvailability = async () => {
        try {
            setToggling(true);
            const response = await api.post('/donors/toggle-availability/');
            setProfile((prev) => ({ ...prev, is_available: response.data.is_available }));
            success(response.data.message || 'Availability updated!');
        } catch (err) {
            error('Failed to toggle availability');
        } finally {
            setToggling(false);
        }
    };

    const formatDate = (dateString) => {
        if (!dateString) return 'N/A';
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric',
        });
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-lifeline-cream">
                <Navbar />
                <div className="flex items-center justify-center py-32">
                    <div className="text-center">
                        <Droplet className="w-12 h-12 text-lifeline-crimson mx-auto mb-4 animate-pulse" fill="currentColor" />
                        <p className="text-lifeline-gray">Loading profile...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50">
            <Navbar />

            <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {/* Profile Header */}
                <div className="card mb-6 animate-fade-in">
                    <div className="flex items-center space-x-4">
                        <div className="w-16 h-16 rounded-full bg-gradient-to-br from-lifeline-crimson to-blood-700 flex items-center justify-center text-white text-2xl font-bold shadow-lg">
                            {isHospital
                                ? (profile?.name?.charAt(0) || 'H')
                                : (profile?.email?.charAt(0)?.toUpperCase() || 'D')}
                        </div>
                        <div>
                            <h2 className="text-2xl font-bold text-lifeline-dark">
                                {isHospital ? profile?.name : profile?.email}
                            </h2>
                            <div className="flex items-center space-x-2 mt-1">
                                <span className={`inline-flex items-center text-xs font-semibold px-2.5 py-0.5 rounded-full ${isHospital
                                        ? 'bg-blue-100 text-blue-800'
                                        : 'bg-green-100 text-green-800'
                                    }`}>
                                    {isHospital ? 'Hospital' : 'Donor'}
                                </span>
                                {!isHospital && profile?.blood_type && (
                                    <BloodTypeBadge bloodType={profile.blood_type} />
                                )}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Donor: Availability Toggle */}
                {!isHospital && (
                    <div className="card mb-6 animate-fade-in" style={{ animationDelay: '0.1s' }}>
                        <div className="flex items-center justify-between">
                            <div>
                                <h3 className="text-lg font-bold text-lifeline-dark">Donation Availability</h3>
                                <p className="text-sm text-lifeline-gray mt-1">
                                    {profile?.is_available
                                        ? 'You are visible to hospitals looking for donors'
                                        : 'You will not appear in donor searches'}
                                </p>
                            </div>
                            <button
                                onClick={handleToggleAvailability}
                                disabled={toggling}
                                className="flex items-center space-x-2 transition-all disabled:opacity-50"
                            >
                                {profile?.is_available ? (
                                    <ToggleRight className="w-10 h-10 text-green-500 hover:scale-110 transition-transform" />
                                ) : (
                                    <ToggleLeft className="w-10 h-10 text-gray-400 hover:scale-110 transition-transform" />
                                )}
                            </button>
                        </div>

                        {/* Eligibility */}
                        <div className="mt-4 pt-4 border-t border-gray-100">
                            <div className="flex items-center space-x-2">
                                {profile?.is_eligible ? (
                                    <>
                                        <CheckCircle className="w-5 h-5 text-green-500" />
                                        <span className="text-green-700 font-medium">Eligible to donate</span>
                                    </>
                                ) : (
                                    <>
                                        <AlertCircle className="w-5 h-5 text-yellow-500" />
                                        <span className="text-yellow-700 font-medium">Not yet eligible</span>
                                    </>
                                )}
                            </div>
                            {profile?.available_from && (
                                <p className="text-sm text-lifeline-gray mt-1 ml-7">
                                    Next eligible date: {formatDate(profile.available_from)}
                                </p>
                            )}
                        </div>
                    </div>
                )}

                {/* Profile Details */}
                <div className="card mb-6 animate-fade-in" style={{ animationDelay: '0.15s' }}>
                    <h3 className="text-lg font-bold text-lifeline-dark mb-4">
                        {isHospital ? 'Hospital Information' : 'Personal Information'}
                    </h3>
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        <InfoItem icon={Mail} label="Email" value={profile?.email} />
                        <InfoItem icon={Phone} label="Phone" value={profile?.phone || 'Not set'} />

                        {isHospital && (
                            <>
                                <InfoItem icon={Building} label="Hospital Name" value={profile?.name} />
                                <InfoItem icon={MapPin} label="Address" value={profile?.address || 'Not set'} />
                                <InfoItem
                                    icon={MapPin}
                                    label="Primary Location"
                                    value={profile?.primary_location_detail?.name || 'Not set'}
                                />
                                <InfoItem
                                    icon={Shield}
                                    label="Verification"
                                    value={profile?.is_verified ? 'Verified ✓' : 'Unverified'}
                                />
                            </>
                        )}

                        {!isHospital && (
                            <>
                                <InfoItem
                                    icon={Droplet}
                                    label="Blood Type"
                                    value={profile?.blood_type || 'Not set'}
                                />
                                <InfoItem
                                    icon={Heart}
                                    label="Last Donation"
                                    value={profile?.last_donation_date ? formatDate(profile.last_donation_date) : 'No records'}
                                />
                                <InfoItem
                                    icon={Clock}
                                    label="Member Since"
                                    value={formatDate(profile?.created_at)}
                                />
                            </>
                        )}
                    </div>
                </div>

                {/* Service Locations */}
                <div className="card animate-fade-in" style={{ animationDelay: '0.2s' }}>
                    <h3 className="text-lg font-bold text-lifeline-dark mb-4">
                        <MapPin className="inline w-5 h-5 mr-1" />
                        Service Locations
                    </h3>
                    {profile?.service_locations?.length > 0 ? (
                        <div className="flex flex-wrap gap-2">
                            {profile.service_locations.map((loc) => (
                                <span
                                    key={loc.id}
                                    className="inline-flex items-center px-3 py-1.5 bg-blue-50 text-blue-700 text-sm font-medium rounded-full"
                                >
                                    <MapPin className="w-3.5 h-3.5 mr-1" />
                                    {loc.name}
                                </span>
                            ))}
                        </div>
                    ) : (
                        <p className="text-lifeline-gray">No service locations set</p>
                    )}
                </div>

                {/* Member since (hospital) */}
                {isHospital && (
                    <div className="text-center mt-6 text-sm text-lifeline-gray animate-fade-in" style={{ animationDelay: '0.25s' }}>
                        <Calendar className="inline w-4 h-4 mr-1" />
                        Member since {formatDate(profile?.created_at)}
                    </div>
                )}
            </main>
        </div>
    );
}

function InfoItem({ icon: Icon, label, value }) {
    return (
        <div className="flex items-start space-x-3 p-3 bg-gray-50 rounded-lg">
            <Icon className="w-5 h-5 text-lifeline-crimson mt-0.5 flex-shrink-0" />
            <div>
                <p className="text-xs text-lifeline-gray uppercase tracking-wider">{label}</p>
                <p className="text-lifeline-dark font-medium">{value}</p>
            </div>
        </div>
    );
}

export default Profile;
