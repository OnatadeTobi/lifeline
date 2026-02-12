/**
 * BloodTypeBadge - Displays blood type with color coding
 */
function BloodTypeBadge({ bloodType, size = 'md' }) {
    const sizeClasses = {
        sm: 'text-xs px-2 py-1',
        md: 'text-sm px-3 py-1.5',
        lg: 'text-base px-4 py-2',
    };

    return (
        <span
            className={`inline-flex items-center font-bold rounded-full bg-lifeline-crimson text-white ${sizeClasses[size]}`}
        >
            {bloodType}
        </span>
    );
}

export default BloodTypeBadge;
