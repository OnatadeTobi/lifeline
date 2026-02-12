import { Link, useLocation } from 'react-router-dom';
import { Droplet, LogOut, LayoutDashboard, List, User } from 'lucide-react';
import { logout, getUserRole } from '../utils/auth';

function Navbar() {
    const location = useLocation();
    const userRole = getUserRole();
    const isHospital = userRole === 'HOSPITAL';

    const navLinks = [
        { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
        { to: '/requests', label: isHospital ? 'My Requests' : 'Requests', icon: List },
        { to: '/profile', label: 'Profile', icon: User },
    ];

    const isActive = (path) => location.pathname === path;

    return (
        <header className="bg-white shadow-sm border-b border-blood-100 sticky top-0 z-40">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-3">
                <div className="flex justify-between items-center">
                    {/* Logo */}
                    <Link to="/dashboard" className="flex items-center space-x-2 group">
                        <Droplet
                            className="w-8 h-8 text-lifeline-crimson group-hover:scale-110 transition-transform"
                            fill="currentColor"
                        />
                        <h1 className="text-2xl font-bold text-lifeline-crimson">Lifeline</h1>
                    </Link>

                    {/* Navigation */}
                    <nav className="hidden sm:flex items-center space-x-1">
                        {navLinks.map(({ to, label, icon: Icon }) => (
                            <Link
                                key={to}
                                to={to}
                                className={`flex items-center space-x-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${isActive(to)
                                        ? 'bg-blood-50 text-lifeline-crimson'
                                        : 'text-lifeline-gray hover:text-lifeline-crimson hover:bg-gray-50'
                                    }`}
                            >
                                <Icon className="w-4 h-4" />
                                <span>{label}</span>
                            </Link>
                        ))}
                    </nav>

                    {/* Actions */}
                    <div className="flex items-center space-x-3">
                        <button
                            onClick={logout}
                            className="flex items-center space-x-1.5 text-lifeline-gray hover:text-lifeline-crimson transition-colors text-sm"
                        >
                            <LogOut className="w-4 h-4" />
                            <span className="hidden sm:inline">Logout</span>
                        </button>
                    </div>
                </div>

                {/* Mobile nav */}
                <nav className="sm:hidden flex items-center justify-center space-x-1 mt-2 pt-2 border-t border-gray-100">
                    {navLinks.map(({ to, label, icon: Icon }) => (
                        <Link
                            key={to}
                            to={to}
                            className={`flex items-center space-x-1 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${isActive(to)
                                    ? 'bg-blood-50 text-lifeline-crimson'
                                    : 'text-lifeline-gray hover:text-lifeline-crimson'
                                }`}
                        >
                            <Icon className="w-3.5 h-3.5" />
                            <span>{label}</span>
                        </Link>
                    ))}
                </nav>
            </div>
        </header>
    );
}

export default Navbar;
