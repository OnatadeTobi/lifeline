import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Droplet, Mail, Lock, User, Phone, MapPin, Building } from 'lucide-react';
import axios from 'axios';

function Register() {
    const [formData, setFormData] = useState({
        email: '',
        password: '',
        password2: '',
        first_name: '',
        last_name: '',
        role: 'DONOR',
    });

    const [donorData, setDonorData] = useState({
        phone: '',
        blood_type: 'O+',
        service_locations: [], // Multiple LGAs
    });

    const [hospitalData, setHospitalData] = useState({
        name: '',
        phone: '',
        address: '',
        primary_location: '',
        service_locations: [], // Multiple LGAs
    });

    const [locations, setLocations] = useState([]);
    const [loadingLocations, setLoadingLocations] = useState(true);
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const navigate = useNavigate();

    // Fetch locations on component mount
    useEffect(() => {
        const fetchLocations = async () => {
            try {
                console.log('Fetching locations from API...');
                const response = await axios.get('/api/v1/locations/lgas/');
                console.log('API Response:', response);
                console.log('Response data:', response.data);

                // API returns paginated response: {count, next, previous, results}
                const locationData = response.data.results || response.data;
                console.log('Location data:', locationData);
                console.log('Is array?', Array.isArray(locationData));

                setLocations(Array.isArray(locationData) ? locationData : []);
                console.log('Locations set:', Array.isArray(locationData) ? locationData.length : 0, 'items');
            } catch (err) {
                console.error('Failed to fetch locations:', err);
                console.error('Error response:', err.response);
                setError('Failed to load locations. Please refresh the page.');
                setLocations([]); // Ensure locations is always an array
            } finally {
                setLoadingLocations(false);
            }
        };

        fetchLocations();
    }, []);

    const handleInputChange = (e) => {
        setFormData({ ...formData, [e.target.name]: e.target.value });
    };

    const handleDonorChange = (e) => {
        const { name, value, selectedOptions } = e.target;

        if (name === 'service_locations') {
            // Handle multi-select
            const selectedValues = Array.from(selectedOptions).map(option => parseInt(option.value));
            setDonorData({ ...donorData, service_locations: selectedValues });
        } else {
            setDonorData({ ...donorData, [name]: value });
        }
    };

    const handleHospitalChange = (e) => {
        const { name, value, selectedOptions } = e.target;

        if (name === 'service_locations') {
            // Handle multi-select
            const selectedValues = Array.from(selectedOptions).map(option => parseInt(option.value));
            setHospitalData({ ...hospitalData, service_locations: selectedValues });
        } else {
            setHospitalData({ ...hospitalData, [name]: value });
        }
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');

        if (formData.password !== formData.password2) {
            setError('Passwords do not match');
            return;
        }

        // Validate location selection
        if (formData.role === 'DONOR' && donorData.service_locations.length === 0) {
            setError('Please select at least one service location');
            return;
        }

        if (formData.role === 'HOSPITAL') {
            if (!hospitalData.primary_location) {
                setError('Please select a primary location');
                return;
            }
            if (hospitalData.service_locations.length === 0) {
                setError('Please select at least one service location');
                return;
            }
        }

        setLoading(true);

        try {
            const endpoint = formData.role === 'DONOR'
                ? '/api/v1/donors/register/'
                : '/api/v1/hospitals/register/';

            let payload;
            if (formData.role === 'DONOR') {
                payload = {
                    email: formData.email,
                    first_name: formData.first_name,
                    last_name: formData.last_name,
                    password: formData.password,
                    password2: formData.password2,
                    phone: donorData.phone,
                    blood_type: donorData.blood_type,
                    service_locations: donorData.service_locations
                };
            } else {
                payload = {
                    email: formData.email,
                    password: formData.password,
                    password2: formData.password2,
                    name: hospitalData.name,
                    phone: hospitalData.phone,
                    address: hospitalData.address,
                    primary_location: parseInt(hospitalData.primary_location),
                    service_locations: hospitalData.service_locations
                };
            }

            await axios.post(endpoint, payload);

            navigate('/verify-email', { state: { email: formData.email } });
        } catch (err) {
            const errorData = err.response?.data;
            if (typeof errorData === 'object') {
                const firstError = Object.values(errorData)[0];
                setError(Array.isArray(firstError) ? firstError[0] : firstError);
            } else {
                setError('Registration failed. Please try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50 py-12 px-4">
            <div className="w-full max-w-2xl mx-auto">
                <div className="text-center mb-8">
                    <Link to="/" className="inline-flex items-center space-x-2">
                        <Droplet className="w-10 h-10 text-lifeline-crimson" fill="currentColor" />
                        <h1 className="text-3xl font-bold text-lifeline-crimson">Lifeline</h1>
                    </Link>
                    <p className="mt-2 text-lifeline-gray">Create your account and start saving lives</p>
                </div>

                <div className="card">
                    <form onSubmit={handleSubmit} className="space-y-6">
                        {error && (
                            <div className="bg-blood-50 border border-lifeline-crimson text-lifeline-crimson px-4 py-3 rounded-lg">
                                {error}
                            </div>
                        )}

                        {/* Role Selection */}
                        <div>
                            <label className="block text-sm font-medium text-lifeline-dark mb-2">I am a</label>
                            <div className="grid grid-cols-2 gap-4">
                                <button
                                    type="button"
                                    onClick={() => setFormData({ ...formData, role: 'DONOR' })}
                                    className={`p-4 border-2 rounded-lg transition-colors ${formData.role === 'DONOR'
                                        ? 'border-lifeline-crimson bg-blood-50'
                                        : 'border-gray-200 hover:border-lifeline-crimson'
                                        }`}
                                >
                                    <div className="text-center">
                                        <User className="w-8 h-8 mx-auto mb-2 text-lifeline-crimson" />
                                        <p className="font-semibold">Donor</p>
                                    </div>
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setFormData({ ...formData, role: 'HOSPITAL' })}
                                    className={`p-4 border-2 rounded-lg transition-colors ${formData.role === 'HOSPITAL'
                                        ? 'border-medical-600 bg-medical-50'
                                        : 'border-gray-200 hover:border-medical-600'
                                        }`}
                                >
                                    <div className="text-center">
                                        <Building className="w-8 h-8 mx-auto mb-2 text-medical-600" />
                                        <p className="font-semibold">Hospital</p>
                                    </div>
                                </button>
                            </div>
                        </div>

                        {/* Email */}
                        <div>
                            <label className="block text-sm font-medium text-lifeline-dark mb-2">Email Address</label>
                            <div className="relative">
                                <Mail className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-lifeline-gray" />
                                <input
                                    type="email"
                                    name="email"
                                    value={formData.email}
                                    onChange={handleInputChange}
                                    className="input-field pl-10"
                                    required
                                />
                            </div>
                        </div>

                        {/* Conditional Fields */}
                        {formData.role === 'DONOR' ? (
                            <>
                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-lifeline-dark mb-2">First Name</label>
                                        <input
                                            type="text"
                                            name="first_name"
                                            value={formData.first_name}
                                            onChange={handleInputChange}
                                            className="input-field"
                                            required
                                        />
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-lifeline-dark mb-2">Last Name</label>
                                        <input
                                            type="text"
                                            name="last_name"
                                            value={formData.last_name}
                                            onChange={handleInputChange}
                                            className="input-field"
                                            required
                                        />
                                    </div>
                                </div>

                                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                                    <div>
                                        <label className="block text-sm font-medium text-lifeline-dark mb-2">Phone Number</label>
                                        <div className="relative">
                                            <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-lifeline-gray" />
                                            <input
                                                type="tel"
                                                name="phone"
                                                value={donorData.phone}
                                                onChange={handleDonorChange}
                                                className="input-field pl-10"
                                                placeholder="+234..."
                                                required
                                            />
                                        </div>
                                    </div>
                                    <div>
                                        <label className="block text-sm font-medium text-lifeline-dark mb-2">Blood Type</label>
                                        <select
                                            name="blood_type"
                                            value={donorData.blood_type}
                                            onChange={handleDonorChange}
                                            className="input-field"
                                            required
                                        >
                                            <option value="O+">O+</option>
                                            <option value="O-">O-</option>
                                            <option value="A+">A+</option>
                                            <option value="A-">A-</option>
                                            <option value="B+">B+</option>
                                            <option value="B-">B-</option>
                                            <option value="AB+">AB+</option>
                                            <option value="AB-">AB-</option>
                                        </select>
                                    </div>
                                </div>

                                {/* Donor Service Locations */}
                                <div>
                                    <label className="block text-sm font-medium text-lifeline-dark mb-2">
                                        <MapPin className="inline w-4 h-4 mr-1" />
                                        Service Locations (Select all areas you can serve)
                                    </label>
                                    {loadingLocations ? (
                                        <p className="text-sm text-lifeline-gray">Loading locations...</p>
                                    ) : (
                                        <select
                                            name="service_locations"
                                            multiple
                                            size="6"
                                            value={donorData.service_locations}
                                            onChange={handleDonorChange}
                                            className="input-field"
                                            required
                                        >
                                            {locations.map(lga => (
                                                <option key={lga.id} value={lga.id}>
                                                    {lga.name}
                                                </option>
                                            ))}
                                        </select>
                                    )}
                                    <p className="text-xs text-lifeline-gray mt-1">Hold Ctrl (Cmd on Mac) to select multiple locations</p>
                                </div>
                            </>
                        ) : (
                            <>
                                <div>
                                    <label className="block text-sm font-medium text-lifeline-dark mb-2">Hospital Name</label>
                                    <input
                                        type="text"
                                        name="name"
                                        value={hospitalData.name}
                                        onChange={handleHospitalChange}
                                        className="input-field"
                                        required
                                    />
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-lifeline-dark mb-2">Phone Number</label>
                                    <div className="relative">
                                        <Phone className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-lifeline-gray" />
                                        <input
                                            type="tel"
                                            name="phone"
                                            value={hospitalData.phone}
                                            onChange={handleHospitalChange}
                                            className="input-field pl-10"
                                            placeholder="+234..."
                                            required
                                        />
                                    </div>
                                </div>
                                <div>
                                    <label className="block text-sm font-medium text-lifeline-dark mb-2">Address</label>
                                    <textarea
                                        name="address"
                                        value={hospitalData.address}
                                        onChange={handleHospitalChange}
                                        className="input-field"
                                        rows="3"
                                        required
                                    />
                                </div>

                                {/* Hospital Primary Location */}
                                <div>
                                    <label className="block text-sm font-medium text-lifeline-dark mb-2">
                                        <MapPin className="inline w-4 h-4 mr-1" />
                                        Primary Location
                                    </label>
                                    {loadingLocations ? (
                                        <p className="text-sm text-lifeline-gray">Loading locations...</p>
                                    ) : (
                                        <select
                                            name="primary_location"
                                            value={hospitalData.primary_location}
                                            onChange={handleHospitalChange}
                                            className="input-field"
                                            required
                                        >
                                            <option value="">Select your primary location</option>
                                            {locations.map(lga => (
                                                <option key={lga.id} value={lga.id}>
                                                    {lga.name}
                                                </option>
                                            ))}
                                        </select>
                                    )}
                                </div>

                                {/* Hospital Service Locations */}
                                <div>
                                    <label className="block text-sm font-medium text-lifeline-dark mb-2">
                                        <MapPin className="inline w-4 h-4 mr-1" />
                                        Service Locations (Select all areas you serve)
                                    </label>
                                    {loadingLocations ? (
                                        <p className="text-sm text-lifeline-gray">Loading locations...</p>
                                    ) : (
                                        <select
                                            name="service_locations"
                                            multiple
                                            size="6"
                                            value={hospitalData.service_locations}
                                            onChange={handleHospitalChange}
                                            className="input-field"
                                            required
                                        >
                                            {locations.map(lga => (
                                                <option key={lga.id} value={lga.id}>
                                                    {lga.name}
                                                </option>
                                            ))}
                                        </select>
                                    )}
                                    <p className="text-xs text-lifeline-gray mt-1">Hold Ctrl (Cmd on Mac) to select multiple locations</p>
                                </div>
                            </>
                        )}

                        {/* Password Fields */}
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                            <div>
                                <label className="block text-sm font-medium text-lifeline-dark mb-2">Password</label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-lifeline-gray" />
                                    <input
                                        type="password"
                                        name="password"
                                        value={formData.password}
                                        onChange={handleInputChange}
                                        className="input-field pl-10"
                                        required
                                        minLength="8"
                                    />
                                </div>
                            </div>
                            <div>
                                <label className="block text-sm font-medium text-lifeline-dark mb-2">Confirm Password</label>
                                <div className="relative">
                                    <Lock className="absolute left-3 top-1/2 transform -translate-y-1/2 w-5 h-5 text-lifeline-gray" />
                                    <input
                                        type="password"
                                        name="password2"
                                        value={formData.password2}
                                        onChange={handleInputChange}
                                        className="input-field pl-10"
                                        required
                                        minLength="8"
                                    />
                                </div>
                            </div>
                        </div>

                        <button
                            type="submit"
                            disabled={loading || loadingLocations}
                            className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Creating Account...' : 'Create Account'}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-lifeline-gray">
                            Already have an account?{' '}
                            <Link to="/login" className="text-lifeline-crimson hover:underline font-semibold">
                                Sign in
                            </Link>
                        </p>
                    </div>
                </div>

                <div className="text-center mt-6">
                    <Link to="/" className="text-lifeline-gray hover:text-lifeline-crimson transition-colors">
                        ← Back to Home
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default Register;
