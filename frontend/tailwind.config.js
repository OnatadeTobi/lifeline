/** @type {import('tailwindcss').Config} */
export default {
    content: [
        "./index.html",
        "./src/**/*.{js,ts,jsx,tsx}",
    ],
    theme: {
        extend: {
            colors: {
                // Blood/Medical themed palette
                blood: {
                    50: '#fef2f2',   // Very light red/pink
                    100: '#fee2e2',  // Light red
                    200: '#fecaca',  // Lighter red
                    300: '#fca5a5',  // Light red
                    400: '#f87171',  // Medium red
                    500: '#ef4444',  // Standard red
                    600: '#dc2626',  // Dark red (primary blood)
                    700: '#b91c1c',  // Darker red
                    800: '#991b1b',  // Very dark red
                    900: '#7f1d1d',  // Deepest red
                },
                medical: {
                    50: '#f0f9ff',   // Very light blue
                    100: '#e0f2fe',  // Light blue
                    200: '#bae6fd',  // Lighter blue
                    300: '#7dd3fc',  // Light medical blue
                    400: '#38bdf8',  // Medium blue
                    500: '#0ea5e9',  // Standard blue
                    600: '#0284c7',  // Dark blue (medical)
                    700: '#0369a1',  // Darker blue
                    800: '#075985',  // Very dark blue
                    900: '#0c4a6e',  // Deepest blue
                },
                lifeline: {
                    crimson: '#C41E3A',  // Deep blood red
                    white: '#FFFFFF',     // Clean white
                    cream: '#FFF5F0',     // Soft cream background
                    gray: '#6B7280',      // Medical gray for text
                    dark: '#1F2937',      // Dark text
                }
            },
        },
    },
    plugins: [],
}
