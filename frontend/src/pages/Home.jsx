import { Link } from 'react-router-dom';
import { Heart, Droplet, Users, Hospital } from 'lucide-react';

function Home() {
    return (
        <div className="min-h-screen bg-gradient-to-br from-lifeline-cream via-white to-blood-50">
            {/* Header/Navbar */}
            <header className="bg-white shadow-sm border-b border-blood-100">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-4">
                    <div className="flex justify-between items-center">
                        <div className="flex items-center space-x-2">
                            <Droplet className="w-8 h-8 text-lifeline-crimson" fill="currentColor" />
                            <h1 className="text-2xl font-bold text-lifeline-crimson">Lifeline</h1>
                        </div>
                        <nav className="flex items-center space-x-4">
                            <Link to="/login" className="text-lifeline-gray hover:text-lifeline-crimson transition-colors">
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
                <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 md:py-24">
                    <div className="text-center">
                        <div className="flex justify-center mb-6">
                            <div className="relative">
                                <div className="absolute inset-0 bg-lifeline-crimson blur-2xl opacity-20 rounded-full"></div>
                                <Heart className="w-20 h-20 text-lifeline-crimson relative z-10" fill="currentColor" />
                            </div>
                        </div>

                        <h2 className="text-4xl md:text-6xl font-bold text-lifeline-dark mb-6">
                            Connecting Life, <span className="text-lifeline-crimson">One Drop</span> at a Time
                        </h2>

                        <p className="text-xl text-lifeline-gray max-w-2xl mx-auto mb-8">
                            Join Nigeria's premier blood donation network. Connect with hospitals in urgent need
                            and become a lifesaver in your community.
                        </p>

                        <div className="flex flex-col sm:flex-row justify-center gap-4">
                            <Link to="/register" className="btn-primary text-lg px-8 py-3">
                                Become a Donor
                            </Link>
                            <Link to="/register" className="btn-secondary text-lg px-8 py-3">
                                Register Hospital
                            </Link>
                        </div>
                    </div>
                </section>

                {/* Features Section */}
                <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 bg-white rounded-2xl shadow-xl my-12">
                    <div className="text-center mb-12">
                        <h3 className="text-3xl font-bold text-lifeline-dark mb-4">How Lifeline Works</h3>
                        <p className="text-lifeline-gray">Simple, fast, and saves lives</p>
                    </div>

                    <div className="grid md:grid-cols-3 gap-8">
                        {/* Feature 1 */}
                        <div className="text-center p-6">
                            <div className="flex justify-center mb-4">
                                <div className="bg-blood-50 p-4 rounded-full">
                                    <Hospital className="w-10 h-10 text-lifeline-crimson" />
                                </div>
                            </div>
                            <h4 className="text-xl font-semibold mb-2 text-lifeline-dark">Hospitals Post Needs</h4>
                            <p className="text-lifeline-gray">
                                Hospitals create urgent blood requests with specific blood types and contact details.
                            </p>
                        </div>

                        {/* Feature 2 */}
                        <div className="text-center p-6">
                            <div className="flex justify-center mb-4">
                                <div className="bg-medical-50 p-4 rounded-full">
                                    <Users className="w-10 h-10 text-medical-600" />
                                </div>
                            </div>
                            <h4 className="text-xl font-semibold mb-2 text-lifeline-dark">Smart Donor Matching</h4>
                            <p className="text-lifeline-gray">
                                Compatible donors in the same location are instantly notified via email.
                            </p>
                        </div>

                        {/* Feature 3 */}
                        <div className="text-center p-6">
                            <div className="flex justify-center mb-4">
                                <div className="bg-blood-50 p-4 rounded-full">
                                    <Droplet className="w-10 h-10 text-lifeline-crimson" fill="currentColor" />
                                </div>
                            </div>
                            <h4 className="text-xl font-semibold mb-2 text-lifeline-dark">Lives Saved</h4>
                            <p className="text-lifeline-gray">
                                Donors respond quickly, and lives are saved through timely blood donations.
                            </p>
                        </div>
                    </div>
                </section>

                {/* Stats Section */}
                <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
                    <div className="grid md:grid-cols-3 gap-8 text-center">
                        <div className="card">
                            <p className="text-5xl font-bold text-lifeline-crimson mb-2">500+</p>
                            <p className="text-lifeline-gray">Active Donors</p>
                        </div>
                        <div className="card">
                            <p className="text-5xl font-bold text-medical-600 mb-2">50+</p>
                            <p className="text-lifeline-gray">Partner Hospitals</p>
                        </div>
                        <div className="card">
                            <p className="text-5xl font-bold text-lifeline-crimson mb-2">200+</p>
                            <p className="text-lifeline-gray">Lives Saved</p>
                        </div>
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

export default Home;
