import { useState, useEffect } from 'react';
import { useParams, useNavigate, useLocation, Link } from 'react-router-dom';
import { Droplet, Phone, FileText, Calendar, MapPin, Building, Check, X, AlertCircle } from 'lucide-react';
import api from '../utils/api';
import { getUserRole, logout } from '../utils/auth';
import BloodTypeBadge from '../components/BloodTypeBadge';
import StatusBadge from '../components/StatusBadge';

function RequestDetail() {
    const { id } = useParams();
    const navigate = useNavigate();
    const location = useLocation();
    const [request, setRequest] = useState(null);
    const [responses, setResponses] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [actionLoading, setActionLoading] = useState(false);
    const [successMessage, setSuccessMessage] = useState(location.state?.message || '');
    const userRole = getUserRole();
    const isDonor = userRole === 'DONOR';
    const isHospital = userRole === 'HOSPITAL';

    useEffect(() => {
        fetchRequestDetail();
    }, [id]);

    const fetchRequestDetail = async () => {
        try {
            setLoading(true);
            const response = await api.get(`/requests/${id}/`);
            setRequest(response.data);

            // If hospital, also fetch donor responses
            if (!isDonor) {
                try {
                    const respRes = await api.get(`/requests/${id}/responses/`);
                    const respData = respRes.data.results || respRes.data;
                    setResponses(Array.isArray(respData) ? respData : []);
                } catch (respErr) {
                    console.error('Failed to fetch responses:', respErr);
                }
            }
        } catch (err) {
            console.error('Failed to fetch request:', err);
            setError('Failed to load request details. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    const handleAcceptRequest = async () => {
        if (!window.confirm('Are you sure you want to accept this blood request?')) {
            return;
        }

        try {
            setActionLoading(true);
            setError('');
            await api.post(`/requests/${id}/accept/`);
            setSuccessMessage('Request accepted successfully! The hospital will contact you soon.');
            fetchRequestDetail();
        } catch (err) {
            const errorData = err.response?.data;
            if (typeof errorData === 'object') {
                const firstError = Object.values(errorData)[0];
                setError(Array.isArray(firstError) ? firstError[0] : String(firstError));
            } else {
                setError('Failed to accept request. Please try again.');
            }
        } finally {
            setActionLoading(false);
        }
    };

    const handleFulfillRequest = async () => {
        if (!window.confirm('Mark this blood request as fulfilled?')) {
            return;
        }

        try {
            setActionLoading(true);
            setError('');
            await api.post(`/requests/${id}/fulfill/`);
            setSuccessMessage('Request marked as fulfilled!');
            fetchRequestDetail();
        } catch (err) {
            setError('Failed to fulfill request. Please try again.');
        } finally {
            setActionLoading(false);
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'long',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
        });
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50 flex items-center justify-center">
                <div className="text-center">
                    <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-lifeline-crimson"></div>
                    <p className="mt-4 text-lifeline-gray">Loading request details...</p>
                </div>
            </div>
        );
    }

    if (error && !request) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50 flex items-center justify-center">
                <div className="card max-w-md text-center">
                    <p className="text-lifeline-crimson mb-4">{error}</p>
                    <button onClick={() => navigate('/requests')} className="btn-primary">
                        Back to Requests
                    </button>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50">
            {/* Header */}
            <header className="bg-white shadow-sm">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex items-center justify-between">
                        <Link to="/dashboard" className="flex items-center space-x-2">
                            <Droplet className="w-8 h-8 text-lifeline-crimson" fill="currentColor" />
                            <h1 className="text-2xl font-bold text-lifeline-crimson">Lifeline</h1>
                        </Link>
                        <div className="flex items-center space-x-4">
                            <Link to="/requests" className="text-lifeline-gray hover:text-lifeline-crimson">
                                Requests
                            </Link>
                            <Link to="/dashboard" className="text-lifeline-gray hover:text-lifeline-crimson">
                                Dashboard
                            </Link>
                            <button
                                onClick={logout}
                                className="text-lifeline-gray hover:text-lifeline-crimson"
                            >
                                Logout
                            </button>
                        </div>
                    </div>
                </div>
            </header>

            {/* Main Content */}
            <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {successMessage && (
                    <div className="mb-6 bg-green-50 border border-green-500 text-green-700 px-4 py-3 rounded-lg flex items-start">
                        <Check className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
                        <span>{successMessage}</span>
                        <button
                            onClick={() => setSuccessMessage('')}
                            className="ml-auto text-green-700 hover:text-green-900"
                        >
                            <X className="w-5 h-5" />
                        </button>
                    </div>
                )}

                {error && (
                    <div className="mb-6 bg-blood-50 border border-lifeline-crimson text-lifeline-crimson px-4 py-3 rounded-lg flex items-start">
                        <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
                        <span>{error}</span>
                    </div>
                )}

                <div className="card">
                    {/* Header */}
                    <div className="flex items-start justify-between mb-6">
                        <div>
                            <div className="flex items-center space-x-3 mb-2">
                                <BloodTypeBadge bloodType={request.blood_type} size="lg" />
                                <StatusBadge status={request.status} size="lg" />
                            </div>
                            <h2 className="text-2xl font-bold text-lifeline-dark">Blood Request Details</h2>
                        </div>
                    </div>

                    {/* Details Grid */}
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
                        <div>
                            <h3 className="font-semibold text-lifeline-dark mb-3">Hospital Information</h3>
                            <div className="space-y-2">
                                <div className="flex items-center text-lifeline-gray">
                                    <Building className="w-4 h-4 mr-2" />
                                    <span>{request.hospital_name || 'Hospital'}</span>
                                </div>
                                {request.hospital_location && (
                                    <div className="flex items-center text-lifeline-gray">
                                        <MapPin className="w-4 h-4 mr-2" />
                                        <span>{request.hospital_location}</span>
                                    </div>
                                )}
                            </div>
                        </div>

                        <div>
                            <h3 className="font-semibold text-lifeline-dark mb-3">Contact Information</h3>
                            <div className="space-y-2">
                                <div className="flex items-center text-lifeline-gray">
                                    <Phone className="w-4 h-4 mr-2" />
                                    <a href={`tel:${request.contact_phone}`} className="hover:text-lifeline-crimson">
                                        {request.contact_phone}
                                    </a>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Posted Date */}
                    <div className="mb-6">
                        <div className="flex items-center text-lifeline-gray">
                            <Calendar className="w-4 h-4 mr-2" />
                            <span>Posted on {formatDate(request.created_at)}</span>
                        </div>
                    </div>

                    {/* Matched Donors Count */}
                    {request.matched_donors_count !== undefined && (
                        <div className="mb-6 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                            <span className="text-blue-800 font-semibold">
                                {request.matched_donors_count} donor response{request.matched_donors_count !== 1 ? 's' : ''}
                            </span>
                        </div>
                    )}

                    {/* Notes */}
                    {request.notes && (
                        <div className="mb-6">
                            <h3 className="font-semibold text-lifeline-dark mb-2 flex items-center">
                                <FileText className="w-4 h-4 mr-2" />
                                Additional Notes
                            </h3>
                            <p className="text-lifeline-gray whitespace-pre-wrap">{request.notes}</p>
                        </div>
                    )}

                    {/* Actions */}
                    <div className="border-t pt-6">
                        {isDonor && request.status === 'OPEN' && (
                            <div className="flex space-x-4">
                                <button
                                    onClick={handleAcceptRequest}
                                    disabled={actionLoading}
                                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {actionLoading ? 'Accepting...' : 'Accept Request'}
                                </button>
                                <Link to="/requests" className="btn-secondary">
                                    Back to Requests
                                </Link>
                            </div>
                        )}

                        {isHospital && (request.status === 'OPEN' || request.status === 'MATCHED') && (
                            <div className="flex space-x-4">
                                <button
                                    onClick={handleFulfillRequest}
                                    disabled={actionLoading}
                                    className="btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                                >
                                    {actionLoading ? 'Updating...' : 'Mark as Fulfilled'}
                                </button>
                                <Link to="/requests" className="btn-secondary">
                                    Back to My Requests
                                </Link>
                            </div>
                        )}

                        {request.status === 'FULFILLED' && (
                            <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
                                <p className="font-semibold">✓ This request has been fulfilled</p>
                            </div>
                        )}

                        {request.status === 'CANCELLED' && (
                            <div className="bg-gray-50 border border-gray-200 text-gray-800 px-4 py-3 rounded-lg">
                                <p className="font-semibold">This request has been cancelled</p>
                            </div>
                        )}
                    </div>

                    {/* Donor Responses (for hospitals) */}
                    {isHospital && responses.length > 0 && (
                        <div className="mt-6 border-t pt-6">
                            <h3 className="font-semibold text-lifeline-dark mb-4">
                                Donor Responses ({responses.length})
                            </h3>
                            <div className="space-y-3">
                                {responses.map((resp) => (
                                    <div key={resp.id} className="bg-gray-50 p-4 rounded-lg">
                                        <div className="flex items-center justify-between">
                                            <div>
                                                <p className="font-semibold text-lifeline-dark">
                                                    {resp.donor_name || 'Donor'}
                                                </p>
                                                <p className="text-sm text-lifeline-gray">
                                                    Blood Type: {resp.donor_blood_type}
                                                </p>
                                                {resp.donor_phone && (
                                                    <p className="text-sm text-lifeline-gray">
                                                        Phone: <a href={`tel:${resp.donor_phone}`} className="hover:text-lifeline-crimson">
                                                            {resp.donor_phone}
                                                        </a>
                                                    </p>
                                                )}
                                            </div>
                                            <div className="text-sm text-lifeline-gray">
                                                {formatDate(resp.accepted_at)}
                                            </div>
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>
                    )}
                </div>

                <div className="text-center mt-6">
                    <Link to="/requests" className="text-lifeline-gray hover:text-lifeline-crimson transition-colors">
                        ← Back to Requests
                    </Link>
                </div>
            </main>
        </div>
    );
}

export default RequestDetail;
