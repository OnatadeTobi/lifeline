import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { Droplet, Plus, Filter } from 'lucide-react';
import api from '../utils/api';
import { getUserRole } from '../utils/auth';
import RequestCard from '../components/RequestCard';
import Navbar from '../components/Navbar';

function RequestList() {
    const [requests, setRequests] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const userRole = getUserRole();
    const isHospital = userRole === 'HOSPITAL';

    useEffect(() => {
        fetchRequests();
    }, [filterStatus]);

    const fetchRequests = async () => {
        try {
            setLoading(true);
            const endpoint = '/requests/';
            const params = filterStatus !== 'all' ? { status: filterStatus } : {};

            const response = await api.get(endpoint, { params });
            const data = response.data.results || response.data;
            setRequests(Array.isArray(data) ? data : []);
        } catch (err) {
            console.error('Failed to fetch requests:', err);
            setError('Failed to load requests. Please try again.');
            setRequests([]);
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50">
            <Navbar />

            <main className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
                <div className="flex items-center justify-between mb-6 animate-fade-in">
                    <div>
                        <h2 className="text-3xl font-bold text-lifeline-dark">
                            {isHospital ? 'My Blood Requests' : 'Available Blood Requests'}
                        </h2>
                        <p className="text-lifeline-gray mt-1">
                            {isHospital
                                ? 'Manage your blood requests and view donor responses'
                                : 'Browse and respond to blood requests in your area'}
                        </p>
                    </div>
                    {isHospital && (
                        <Link to="/create-request" className="btn-primary">
                            <Plus className="w-5 h-5 mr-2 inline" />
                            Create Request
                        </Link>
                    )}
                </div>

                {/* Filters */}
                <div className="mb-6 flex items-center space-x-4 animate-fade-in" style={{ animationDelay: '0.05s' }}>
                    <Filter className="w-5 h-5 text-lifeline-gray" />
                    <div className="flex space-x-2">
                        {[
                            { value: 'all', label: 'All' },
                            { value: 'OPEN', label: 'Open' },
                            { value: 'MATCHED', label: 'Matched' },
                            ...(isHospital ? [{ value: 'FULFILLED', label: 'Fulfilled' }] : []),
                        ].map(({ value, label }) => (
                            <button
                                key={value}
                                onClick={() => setFilterStatus(value)}
                                className={`px-4 py-2 rounded-lg transition-all duration-200 ${filterStatus === value
                                    ? 'bg-lifeline-crimson text-white shadow-md'
                                    : 'bg-white text-lifeline-gray hover:bg-gray-50'
                                    }`}
                            >
                                {label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Requests Grid */}
                {loading ? (
                    <div className="text-center py-12">
                        <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-lifeline-crimson"></div>
                        <p className="mt-4 text-lifeline-gray">Loading requests...</p>
                    </div>
                ) : error ? (
                    <div className="card text-center py-12 animate-fade-in">
                        <p className="text-lifeline-crimson">{error}</p>
                        <button onClick={fetchRequests} className="mt-4 btn-primary">
                            Try Again
                        </button>
                    </div>
                ) : requests.length === 0 ? (
                    <div className="card text-center py-12 animate-fade-in">
                        <Droplet className="w-16 h-16 text-lifeline-gray mx-auto mb-4 opacity-50" />
                        <h3 className="text-xl font-semibold text-lifeline-dark mb-2">
                            No requests found
                        </h3>
                        <p className="text-lifeline-gray">
                            {isHospital
                                ? 'Create your first blood request to get started'
                                : 'Check back later for new blood requests in your area'}
                        </p>
                        {isHospital && (
                            <Link to="/create-request" className="btn-primary mt-4 inline-block">
                                Create Request
                            </Link>
                        )}
                    </div>
                ) : (
                    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                        {requests.map((request, index) => (
                            <div key={request.id} className="animate-fade-in" style={{ animationDelay: `${index * 0.05}s` }}>
                                <RequestCard request={request} />
                            </div>
                        ))}
                    </div>
                )}
            </main>
        </div>
    );
}

export default RequestList;
