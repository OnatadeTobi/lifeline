import { Link } from 'react-router-dom';
import { Heart, Droplet, Users, Hospital, ArrowRight, Shield, Zap } from 'lucide-react';

function Home() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50">
            {/* Header/Navbar */}
            <header className="bg-white/80 backdrop-blur-md shadow-sm border-b border-blood-100 sticky top-0 z-40">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-2">
                            <Droplet className="w-8 h-8 text-lifeline-crimson animate-float" fill="currentColor" />
                            <h1 className="text-2xl font-bold text-lifeline-crimson">Lifeline</h1>
                        </div>
                        <nav className="flex items-center space-x-4">
                            <Link to="/login" className="text-lifeline-gray hover:text-lifeline-crimson transition-colors font-medium">
                                Login
                            </Link>
                            <Link to="/register" className="btn-primary">
                                Get Started
                            </Link>
                        </nav>
                    </div>
                </div>
            </header>

            {/* Hero Section */}
            <main>
                <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-28">
                    <div className="text-center animate-fade-in">
                        <div className="flex justify-center mb-8">
                            <div className="relative">
                                <div className="absolute inset-0 bg-lifeline-crimson blur-3xl opacity-20 rounded-full scale-150"></div>
                                <Heart className="w-24 h-24 text-lifeline-crimson relative z-10 animate-heartbeat drop-shadow-lg" fill="currentColor" />
                            </div>
                        </div>

                        <h2 className="text-4xl md:text-6xl lg:text-7xl font-bold text-lifeline-dark mb-6 leading-tight">
                            Connecting Life,{' '}
                            <span className="text-transparent bg-clip-text bg-gradient-to-r from-lifeline-crimson to-blood-500">
                                One Drop
                            </span>{' '}
                            at a Time
                        </h2>

                        <p className="text-xl text-lifeline-gray max-w-2xl mx-auto mb-10">
                            Join Nigeria's premier blood donation network. Connect with hospitals in urgent need
                            and become a lifesaver in your community.
                        </p>

                        <div className="flex flex-col sm:flex-row justify-center gap-4">
                            <Link to="/register" className="btn-primary text-lg px-8 py-3 inline-flex items-center justify-center group">
                                Become a Donor
                                <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                            </Link>
                            <Link to="/register" className="btn-secondary text-lg px-8 py-3 inline-flex items-center justify-center">
                                Register Hospital
                            </Link>
                        </div>
                    </div>
                </section>

                {/* Features Section */}
                <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                    <div className="bg-white rounded-3xl shadow-xl p-8 md:p-12 border border-gray-100">
                        <div className="text-center mb-12">
                            <h3 className="text-3xl font-bold text-lifeline-dark mb-4">How Lifeline Works</h3>
                            <p className="text-lifeline-gray max-w-lg mx-auto">Simple, fast, and saves lives. Three steps to make a difference.</p>
                        </div>

                        <div className="grid md:grid-cols-3 gap-8">
                            <FeatureCard
                                icon={Hospital}
                                color="blood"
                                title="Hospitals Post Needs"
                                description="Hospitals create urgent blood requests with specific blood types and contact details."
                                step="01"
                                delay="0.1s"
                            />
                            <FeatureCard
                                icon={Zap}
                                color="medical"
                                title="Smart Donor Matching"
                                description="Compatible donors in the same location are instantly notified via email."
                                step="02"
                                delay="0.2s"
                            />
                            <FeatureCard
                                icon={Heart}
                                color="blood"
                                title="Lives Saved"
                                description="Donors respond quickly, and lives are saved through timely blood donations."
                                step="03"
                                delay="0.3s"
                            />
                        </div>
                    </div>
                </section>

                {/* Stats Section */}
                <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                    <div className="grid md:grid-cols-3 gap-8 text-center">
                        <StatCard number="500+" label="Active Donors" color="text-lifeline-crimson" delay="0.1s" />
                        <StatCard number="50+" label="Partner Hospitals" color="text-medical-600" delay="0.2s" />
                        <StatCard number="200+" label="Lives Saved" color="text-lifeline-crimson" delay="0.3s" />
                    </div>
                </section>

                {/* Trust Section */}
                <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                    <div className="bg-gradient-to-r from-lifeline-crimson to-blood-700 rounded-3xl p-8 md:p-12 text-white text-center shadow-2xl">
                        <Shield className="w-12 h-12 mx-auto mb-4 opacity-90" />
                        <h3 className="text-3xl font-bold mb-4">Safe, Secure & Verified</h3>
                        <p className="text-lg max-w-2xl mx-auto opacity-90 mb-8">
                            Every hospital on our platform is verified. Your data is protected with industry-standard
                            security. Together, we're building a safer blooddonation ecosystem for Nigeria.
                        </p>
                        <Link to="/register" className="inline-flex items-center bg-white text-lifeline-crimson font-semibold px-8 py-3 rounded-lg hover:bg-gray-100 transition-colors group">
                            Join Lifeline Today
                            <ArrowRight className="w-5 h-5 ml-2 group-hover:translate-x-1 transition-transform" />
                        </Link>
                    </div>
                </section>
            </main>

            {/* Footer */}
            <footer className="bg-lifeline-dark text-white py-8 mt-16">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
                    <div className="flex items-center justify-center space-x-2 mb-4">
                        <Droplet className="w-6 h-6 text-lifeline-crimson" fill="currentColor" />
                        <span className="text-xl font-semibold">Lifeline</span>
                    </div>
                    <p className="text-gray-400">
                        Connecting lives through blood donation. © 2026 Lifeline. All rights reserved.
                    </p>
                </div>
            </footer>
        </div>
    );
}

function FeatureCard({ icon: Icon, color, title, description, step, delay }) {
    const bgColor = color === 'blood' ? 'bg-blood-50' : 'bg-medical-50';
    const iconColor = color === 'blood' ? 'text-lifeline-crimson' : 'text-medical-600';
    const stepColor = color === 'blood' ? 'text-blood-200' : 'text-medical-200';

    return (
        <div className="text-center p-6 relative animate-fade-in" style={{ animationDelay: delay }}>
            <div className={`absolute top-2 right-2 text-5xl font-bold ${stepColor} select-none`}>
                {step}
            </div>
            <div className="flex justify-center mb-4">
                <div className={`${bgColor} p-4 rounded-2xl`}>
                    <Icon className={`w-10 h-10 ${iconColor}`} />
                </div>
            </div>
            <h4 className="text-xl font-semibold mb-2 text-lifeline-dark">{title}</h4>
            <p className="text-lifeline-gray">{description}</p>
        </div>
    );
}

function StatCard({ number, label, color, delay }) {
    return (
        <div className="card hover:shadow-xl hover:-translate-y-1 transition-all animate-fade-in" style={{ animationDelay: delay }}>
            <p className={`text-5xl font-bold ${color} mb-2`}>{number}</p>
            <p className="text-lifeline-gray font-medium">{label}</p>
        </div>
    );
}

export default Home;
