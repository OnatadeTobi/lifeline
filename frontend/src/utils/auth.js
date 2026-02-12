// Authentication helper functions

/**
 * Check if user is authenticated
 */
export const isAuthenticated = () => {
    const accessToken = localStorage.getItem('accessToken');
    return !!accessToken;
};

/**
 * Get current user's access token
 */
export const getAccessToken = () => {
    return localStorage.getItem('accessToken');
};

/**
 * Get current user's refresh token
 */
export const getRefreshToken = () => {
    return localStorage.getItem('refreshToken');
};

/**
 * Set authentication tokens
 */
export const setTokens = (accessToken, refreshToken) => {
    localStorage.setItem('accessToken', accessToken);
    localStorage.setItem('refreshToken', refreshToken);
};

/**
 * Clear authentication tokens
 */
export const clearTokens = () => {
    localStorage.removeItem('accessToken');
    localStorage.removeItem('refreshToken');
    localStorage.removeItem('userRole');
};

/**
 * Logout user and redirect to login
 */
export const logout = () => {
    clearTokens();
    window.location.href = '/login';
};

/**
 * Decode JWT token to get user info
 * Note: This is a simple implementation. For production, consider using jwt-decode library
 */
export const parseJwt = (token) => {
    try {
        const base64Url = token.split('.')[1];
        const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
        const jsonPayload = decodeURIComponent(
            atob(base64)
                .split('')
                .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
                .join('')
        );
        return JSON.parse(jsonPayload);
    } catch (error) {
        return null;
    }
};

/**
 * Get user role from token
 */
export const getUserRole = () => {
    // Role is stored in localStorage at login time (from the login response)
    return localStorage.getItem('userRole') || null;
};

/**
 * Get user ID from token
 */
export const getUserId = () => {
    const token = getAccessToken();
    if (!token) return null;

    const payload = parseJwt(token);
    return payload?.user_id || null;
};

/**
 * Check if token is expired
 */
export const isTokenExpired = (token) => {
    if (!token) return true;

    const payload = parseJwt(token);
    if (!payload || !payload.exp) return true;

    const currentTime = Date.now() / 1000;
    return payload.exp < currentTime;
};
