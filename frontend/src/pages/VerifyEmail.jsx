import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Droplet, Mail, CheckCircle } from 'lucide-react';
import axios from 'axios';

function VerifyEmail() {
    const [code, setCode] = useState('');
    const [email, setEmail] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState(false);
    const [loading, setLoading] = useState(false);
    const [resending, setResending] = useState(false);
    const navigate = useNavigate();
    const location = useLocation();

    // Get email from navigation state if available
    const emailFromState = location.state?.email || '';

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await axios.post('/api/v1/auth/verify-email/', {
                email: email || emailFromState,
                code
            });

            setSuccess(true);

            // Redirect to login after 2 seconds
            setTimeout(() => {
                navigate('/login', { state: { message: 'Email verified! You can now log in.' } });
            }, 2000);
        } catch (err) {
            const errorData = err.response?.data;
            if (typeof errorData === 'object') {
                const firstError = Object.values(errorData)[0];
                setError(Array.isArray(firstError) ? firstError[0] : firstError);
            } else {
                setError('Verification failed. Please check your code and try again.');
            }
        } finally {
            setLoading(false);
        }
    };

    const handleResend = async () => {
        setError('');
        setResending(true);

        try {
            await axios.post('/api/v1/auth/resend-verification/', {
                email: email || emailFromState
            });

            setError('');
            alert('Verification code sent! Please check your email.');
        } catch (err) {
            setError('Failed to resend code. Please try again.');
        } finally {
            setResending(false);
        }
    };

    if (success) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50 flex items-center justify-center p-4">
                <div className="w-full max-w-md text-center">
                    <div className="card">
                        <CheckCircle className="w-16 h-16 text-green-500 mx-auto mb-4" />
                        <h2 className="text-2xl font-bold text-lifeline-dark mb-2">Email Verified!</h2>
                        <p className="text-lifeline-gray">Redirecting to login...</p>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50 flex items-center justify-center p-4">
            <div className="w-full max-w-md">
                {/* Logo Header */}
                <div className="text-center mb-8">
                    <Link to="/" className="inline-flex items-center space-x-2">
                        <Droplet className="w-10 h-10 text-lifeline-crimson" fill="currentColor" />
                        <h1 className="text-3xl font-bold text-lifeline-crimson">Lifeline</h1>
                    </Link>
                    <p className="mt-2 text-lifeline-gray">Verify your email to continue</p>
                </div>

                {/* Verification Card */}
                <div className="card">
                    <div className="text-center mb-6">
                        <Mail className="w-12 h-12 text-lifeline-crimson mx-auto mb-3" />
                        <h2 className="text-xl font-semibold text-lifeline-dark mb-2">Check Your Email</h2>
                        <p className="text-sm text-lifeline-gray">
                            We've sent a 6-digit verification code to your email address.
                        </p>
                    </div>

                    <form onSubmit={handleSubmit} className="space-y-6">
                        {error && (
                            <div className="bg-blood-50 border border-lifeline-crimson text-lifeline-crimson px-4 py-3 rounded-lg text-sm">
                                {error}
                            </div>
                        )}

                        {!emailFromState && (
                            <div>
                                <label htmlFor="email" className="block text-sm font-medium text-lifeline-dark mb-2">
                                    Email Address
                                </label>
                                <input
                                    id="email"
                                    type="email"
                                    value={email}
                                    onChange={(e) => setEmail(e.target.value)}
                                    className="input-field"
                                    placeholder="your@email.com"
                                    required
                                />
                            </div>
                        )}

                        <div>
                            <label htmlFor="code" className="block text-sm font-medium text-lifeline-dark mb-2">
                                Verification Code
                            </label>
                            <input
                                id="code"
                                type="text"
                                value={code}
                                onChange={(e) => setCode(e.target.value)}
                                className="input-field text-center text-2xl tracking-widest"
                                placeholder="000000"
                                maxLength="6"
                                pattern="[0-9]{6}"
                                required
                            />
                            <p className="text-xs text-lifeline-gray mt-1">Enter the 6-digit code from your email</p>
                        </div>

                        <button
                            type="submit"
                            disabled={loading}
                            className="w-full btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
                        >
                            {loading ? 'Verifying...' : 'Verify Email'}
                        </button>
                    </form>

                    <div className="mt-6 text-center">
                        <p className="text-sm text-lifeline-gray mb-2">
                            Didn't receive the code?
                        </p>
                        <button
                            onClick={handleResend}
                            disabled={resending || !email && !emailFromState}
                            className="text-lifeline-crimson hover:underline font-semibold disabled:opacity-50"
                        >
                            {resending ? 'Sending...' : 'Resend Code'}
                        </button>
                    </div>
                </div>

                {/* Back to Login */}
                <div className="text-center mt-6">
                    <Link to="/login" className="text-lifeline-gray hover:text-lifeline-crimson transition-colors">
                        ← Back to Login
                    </Link>
                </div>
            </div>
        </div>
    );
}

export default VerifyEmail;
