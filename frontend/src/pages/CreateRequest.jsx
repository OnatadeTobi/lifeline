import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import { Droplet, Phone, FileText, AlertCircle } from 'lucide-react';
import api from '../utils/api';
import { useNotification } from '../components/NotificationContext';
import Navbar from '../components/Navbar';

function CreateRequest() {
    const [formData, setFormData] = useState({
        blood_type: 'O+',
        contact_phone: '',
        notes: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();
    const { success, error: notifyError } = useNotification();

    const bloodTypes = ['O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'];

    const handleChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const response = await api.post('/requests/create/', formData);
            success('Blood request created successfully!');
            navigate(`/requests/${response.data.id}`, {
                state: { message: 'Request created successfully!' }
            });
        } catch (err) {
            const errorData = err.response?.data;
            if (typeof errorData === 'object') {
                const messages = [];
                for (const [key, value] of Object.entries(errorData)) {
                    const msg = Array.isArray(value) ? value[0] : value;
                    messages.push(msg);
                }
                const combined = messages.join(' ');
                setError(combined);
                notifyError(combined);
            } else {
                setError('Failed to create request. Please try again.');
                notifyError('Failed to create request.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50">
            <Navbar />

            <main className="max-w-2xl mx-auto px-4 py-8">
                <div className="card animate-fade-in">
                    <div className="mb-6">
                        <h2 className="text-2xl font-bold text-lifeline-dark">New Blood Request</h2>
                        <p className="text-lifeline-gray mt-1">Fill in the details below to find compatible donors</p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {error && (
                            <div className="bg-blood-50 border border-lifeline-crimson text-lifeline-crimson px-4 py-3 rounded-lg flex items-start animate-fade-in">
                                <AlertCircle className="w-5 h-5 mr-2 flex-shrink-0 mt-0.5" />
                                <span>{error}</span>
                            </div>
                        )}

                        {/* Blood Type */}
                        <div>
                            <label className="block text-sm font-medium text-lifeline-dark mb-2">
                                <Droplet className="inline w-4 h-4 mr-1" />
                                Blood Type Needed *
                            </label>
                            <select
                                name="blood_type"
                                value={formData.blood_type}
                                onChange={handleChange}
                                className="input-field"
                                required
                            >
                                {bloodTypes.map(type => (
                                    <option key={type} value={type}>{type}</option>
                                ))}
                            </select>
                            <p className="text-xs text-lifeline-gray mt-1">
                                Compatible donors will be automatically matched based on your service area
                            </p>
                        </div>

                        {/* Contact Phone */}
                        <div>
                            <label className="block text-sm font-medium text-lifeline-dark mb-2">
                                <Phone className="inline w-4 h-4 mr-1" />
                                Contact Phone *
                            </label>
                            <input
                                type="tel"
                                name="contact_phone"
                                value={formData.contact_phone}
                                onChange={handleChange}
                                className="input-field"
                                placeholder="+234..."
                                required
                            />
                        </div>

                        {/* Notes */}
                        <div>
                            <label className="block text-sm font-medium text-lifeline-dark mb-2">
                                <FileText className="inline w-4 h-4 mr-1" />
                                Additional Notes
                            </label>
                            <textarea
                                name="notes"
                                value={formData.notes}
                                onChange={handleChange}
                                className="input-field"
                                rows="4"
                                placeholder="Any additional information (e.g., urgency, special requirements)..."
                            />
                        </div>

                        {/* Submit Button */}
                        <div className="flex space-x-4">
                            <button
                                type="submit"
                                disabled={loading}
                                className="flex-1 btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                            >
                                {loading ? 'Creating Request...' : 'Create Request & Find Donors'}
                            </button>
                            <Link to="/dashboard" className="btn-secondary px-6">
                                Cancel
                            </Link>
                        </div>
                    </form>

                    <div className="mt-6 p-4 bg-blue-50 border border-blue-200 rounded-lg">
                        <h3 className="font-semibold text-blue-900 mb-2">How it works</h3>
                        <ul className="text-sm text-blue-800 space-y-1">
                            <li>• We'll find compatible donors in your service area</li>
                            <li>• Donors will be notified via email</li>
                            <li>• Track responses in real-time on your dashboard</li>
                            <li>• Mark the request as fulfilled once you receive blood</li>
                        </ul>
                    </div>
                </div>

                <div className="text-center mt-6">
                    <Link to="/dashboard" className="text-lifeline-gray hover:text-lifeline-crimson transition-colors">
                        ← Back to Dashboard
                    </Link>
                </div>
            </main>
        </div>
    );
}

export default CreateRequest;
