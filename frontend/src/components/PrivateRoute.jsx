import { Navigate } from 'react-router-dom';
import { isAuthenticated } from '../utils/auth';

/**
 * PrivateRoute component - protects routes that require authentication
 * Usage: <PrivateRoute><Dashboard /></PrivateRoute>
 */
function PrivateRoute({ children }) {
    if (!isAuthenticated()) {
        // Redirect to login if not authenticated
        return <Navigate to="/login" replace />;
    }

    return children;
}

export default PrivateRoute;
