/**
 * StatusBadge - Displays request status with color coding
 * Backend statuses: OPEN, MATCHED, FULFILLED, CANCELLED
 */
function StatusBadge({ status, size = 'md' }) {
    const sizeClasses = {
        sm: 'text-xs px-2 py-1',
        md: 'text-sm px-3 py-1.5',
        lg: 'text-base px-4 py-2',
    };

    const statusConfig = {
        OPEN: {
            bg: 'bg-yellow-100',
            text: 'text-yellow-800',
            label: 'Open',
        },
        MATCHED: {
            bg: 'bg-blue-100',
            text: 'text-blue-800',
            label: 'Matched',
        },
        FULFILLED: {
            bg: 'bg-green-100',
            text: 'text-green-800',
            label: 'Fulfilled',
        },
        CANCELLED: {
            bg: 'bg-gray-100',
            text: 'text-gray-800',
            label: 'Cancelled',
        },
    };

    const config = statusConfig[status] || statusConfig.OPEN;

    return (
        <span
            className={`inline-flex items-center font-medium rounded-full ${config.bg} ${config.text} ${sizeClasses[size]}`}
        >
            {config.label}
        </span>
    );
}

export default StatusBadge;
