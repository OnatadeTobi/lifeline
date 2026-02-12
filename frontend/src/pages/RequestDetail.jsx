import { useState, useEffect, useCallback } from 'react';
import { useParams, useNavigate, useLocation, Link } from 'react-router-dom';
import { Phone, FileText, Calendar, MapPin, Building, Check, X, AlertCircle, RefreshCw, Users } from 'lucide-react';
import api from '../utils/api';
import { getUserRole } from '../utils/auth';
import { useNotification } from '../components/NotificationContext';
import { useConfirmModal } from '../components/ConfirmModal';
import Navbar from '../components/Navbar';
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
    const userRole = getUserRole();
    const isDonor = userRole === 'DONOR';
    const isHospital = userRole === 'HOSPITAL';
    const { success, error: notifyError } = useNotification();
    const { confirm, ConfirmModal } = useConfirmModal();

    useEffect(() => {
        if (location.state?.message) {
            success(location.state.message);
            window.history.replaceState({}, document.title);
        }
        fetchRequestDetail();
    }, [id]);

    const fetchRequestDetail = useCallback(async (silent = false) => {
        try {
            if (!silent) setLoading(true);
            const response = await api.get(`/requests/${id}/`);
            setRequest(response.data);

            if (!isDonor) {
                try {
                    const respRes = await api.get(`/requests/${id}/responses/`);
                    const respData = respRes.data.results || respRes.data;
                    setResponses(Array.isArray(respData) ? respData : []);
                } catch {
                    // Not critical
                }
            }
        } catch (err) {
            console.error('Failed to fetch request:', err);
            if (!silent) setError('Failed to load request details.');
        } finally {
            if (!silent) setLoading(false);
        }
    }, [id, isDonor]);

    // Auto-refresh every 30 seconds for hospitals to see new donor responses
    useEffect(() => {
        if (!isHospital) return;
        const interval = setInterval(() => fetchRequestDetail(true), 30000);
        return () => clearInterval(interval);
    }, [isHospital, fetchRequestDetail]);

    const handleAcceptRequest = async () => {
        const ok = await confirm(
            'Accept Blood Request?',
            'You will be committing to donate blood. The hospital will receive your contact information.',
            { confirmText: 'Accept Request', variant: 'info' }
        );
        if (!ok) return;
        try {
            setActionLoading(true);
            setError('');
            await api.post(`/requests/${id}/accept/`);
            success('Request accepted! The hospital will contact you soon.');
            fetchRequestDetail();
        } catch (err) {
            const errorData = err.response?.data;
            const msg = typeof errorData === 'object'
                ? (Array.isArray(Object.values(errorData)[0]) ? Object.values(errorData)[0][0] : String(Object.values(errorData)[0]))
                : 'Failed to accept request.';
            setError(msg);
            notifyError(msg);
        } finally {
            setActionLoading(false);
        }
    };

    const handleFulfillRequest = async () => {
        const ok = await confirm(
            'Mark as Fulfilled?',
            'This confirms you have received the blood donation and the request is complete.',
            { confirmText: 'Mark Fulfilled', variant: 'info' }
        );
        if (!ok) return;
        try {
            setActionLoading(true);
            setError('');
            await api.post(`/requests/${id}/fulfill/`);
            success('Request marked as fulfilled!');
            fetchRequestDetail();
        } catch (err) {
            notifyError('Failed to fulfill request.');
        } finally {
            setActionLoading(false);
        }
    };

    const formatDate = (dateString) => {
        const date = new Date(dateString);
        return date.toLocaleDateString('en-US', {
            year: 'numeric', month: 'long', day: 'numeric',
            hour: '2-digit', minute: '2-digit',
        });
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50">
                <Navbar />
                <div className="flex items-center justify-center py-32">
                    <div className="text-center">
                        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-lifeline-crimson"></div>
                        <p className="mt-4 text-lifeline-gray">Loading request details...</p>
                    </div>
                </div>
            </div>
        );
    }

    if (error && !request) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50">
                <Navbar />
                <div className="flex items-center justify-center py-32">
                    <div className="card max-w-md text-center">
                        <p className="text-lifeline-crimson mb-4">{error}</p>
                        <button onClick={() => navigate('/requests')} className="btn-primary">Back to Requests</button>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50">
            <Navbar />
            {ConfirmModal}

            <main className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                {error && (
                    <div className="mb-6 bg-blood-50 border border-lifeline-crimson text-lifeline-crimson px-4 py-3 rounded-lg flex items-start animate-fade-in">
                        <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
                        <span>{error}</span>
                    </div>
                )}

                <div className="card animate-fade-in">
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
                            <div className="flex items-center text-lifeline-gray">
                                <Phone className="w-4 h-4 mr-2" />
                                <a href={`tel:${request.contact_phone}`} className="hover:text-lifeline-crimson transition-colors">
                                    {request.contact_phone}
                                </a>
                            </div>
                        </div>
                    </div>

                    <div className="mb-6 flex items-center text-lifeline-gray">
                        <Calendar className="w-4 h-4 mr-2" />
                        <span>Posted on {formatDate(request.created_at)}</span>
                    </div>

                    {request.matched_donors_count !== undefined && (
                        <div className="mb-6 p-3 bg-blue-50 border border-blue-200 rounded-lg">
                            <span className="text-blue-800 font-semibold">
                                {request.matched_donors_count} donor response{request.matched_donors_count !== 1 ? 's' : ''}
                            </span>
                        </div>
                    )}

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
                                <button onClick={handleAcceptRequest} disabled={actionLoading} className="btn-primary disabled:opacity-50">
                                    {actionLoading ? 'Accepting...' : 'Accept Request'}
                                </button>
                                <Link to="/requests" className="btn-secondary">Back to Requests</Link>
                            </div>
                        )}

                        {isHospital && (request.status === 'OPEN' || request.status === 'MATCHED') && (
                            <div className="flex space-x-4">
                                <button onClick={handleFulfillRequest} disabled={actionLoading} className="btn-primary disabled:opacity-50">
                                    {actionLoading ? 'Updating...' : 'Mark as Fulfilled'}
                                </button>
                                <Link to="/requests" className="btn-secondary">Back to My Requests</Link>
                            </div>
                        )}

                        {request.status === 'FULFILLED' && (
                            <div className="bg-green-50 border border-green-200 text-green-800 px-4 py-3 rounded-lg">
                                <p className="font-semibold flex items-center"><Check className="w-5 h-5 mr-2" />This request has been fulfilled</p>
                            </div>
                        )}

                        {request.status === 'CANCELLED' && (
                            <div className="bg-gray-50 border border-gray-200 text-gray-800 px-4 py-3 rounded-lg">
                                <p className="font-semibold">This request has been cancelled</p>
                            </div>
                        )}
                    </div>

                    {/* Donor Responses (for hospitals) */}
                    {isHospital && (
                        <div className="mt-6 border-t pt-6">
                            <div className="flex items-center justify-between mb-4">
                                <h3 className="font-semibold text-lifeline-dark flex items-center">
                                    <Users className="w-5 h-5 mr-2" />
                                    Donor Responses ({responses.length})
                                </h3>
                                <button
                                    onClick={() => fetchRequestDetail(true)}
                                    className="flex items-center space-x-1 text-sm text-lifeline-gray hover:text-lifeline-crimson transition-colors"
                                >
                                    <RefreshCw className="w-4 h-4" />
                                    <span>Refresh</span>
                                </button>
                            </div>
                            {responses.length > 0 ? (
                                <div className="space-y-3">
                                    {responses.map((resp) => (
                                        <div key={resp.id} className="bg-gray-50 p-4 rounded-lg hover:bg-gray-100 transition-colors">
                                            <div className="flex items-center justify-between">
                                                <div>
                                                    <p className="font-semibold text-lifeline-dark">{resp.donor_name || 'Donor'}</p>
                                                    <p className="text-sm text-lifeline-gray">Blood Type: {resp.donor_blood_type}</p>
                                                    {resp.donor_phone && (
                                                        <p className="text-sm text-lifeline-gray">
                                                            Phone: <a href={`tel:${resp.donor_phone}`} className="hover:text-lifeline-crimson">{resp.donor_phone}</a>
                                                        </p>
                                                    )}
                                                </div>
                                                <div className="text-sm text-lifeline-gray">{formatDate(resp.accepted_at)}</div>
                                            </div>
                                        </div>
                                    ))}
                                </div>
                            ) : (
                                <div className="text-center py-8 text-lifeline-gray">
                                    <Users className="w-10 h-10 mx-auto mb-2 opacity-40" />
                                    <p>No donor responses yet</p>
                                    <p className="text-xs mt-1">Auto-refreshes every 30 seconds</p>
                                </div>
                            )}
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
