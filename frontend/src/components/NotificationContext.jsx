import { createContext, useContext, useState, useCallback } from 'react';
import { X, CheckCircle, AlertCircle, Info } from 'lucide-react';

const NotificationContext = createContext(null);

let toastId = 0;

export function NotificationProvider({ children }) {
    const [toasts, setToasts] = useState([]);

    const removeToast = useCallback((id) => {
        setToasts((prev) => prev.filter((t) => t.id !== id));
    }, []);

    const addToast = useCallback((message, type = 'info', duration = 4000) => {
        const id = ++toastId;
        setToasts((prev) => [...prev, { id, message, type }]);
        if (duration > 0) {
            setTimeout(() => removeToast(id), duration);
        }
        return id;
    }, [removeToast]);

    const success = useCallback((msg) => addToast(msg, 'success'), [addToast]);
    const error = useCallback((msg) => addToast(msg, 'error', 6000), [addToast]);
    const info = useCallback((msg) => addToast(msg, 'info'), [addToast]);

    return (
        <NotificationContext.Provider value={{ success, error, info, removeToast }}>
            {children}
            {/* Toast Container */}
            <div className="fixed top-4 right-4 z-50 flex flex-col gap-3 pointer-events-none" style={{ maxWidth: '400px' }}>
                {toasts.map((toast) => (
                    <Toast key={toast.id} toast={toast} onClose={() => removeToast(toast.id)} />
                ))}
            </div>
        </NotificationContext.Provider>
    );
}

function Toast({ toast, onClose }) {
    const config = {
        success: {
            bg: 'bg-green-50 border-green-400',
            text: 'text-green-800',
            icon: <CheckCircle className="w-5 h-5 text-green-500" />,
        },
        error: {
            bg: 'bg-red-50 border-red-400',
            text: 'text-red-800',
            icon: <AlertCircle className="w-5 h-5 text-red-500" />,
        },
        info: {
            bg: 'bg-blue-50 border-blue-400',
            text: 'text-blue-800',
            icon: <Info className="w-5 h-5 text-blue-500" />,
        },
    };

    const c = config[toast.type] || config.info;

    return (
        <div
            className={`pointer-events-auto flex items-start gap-3 px-4 py-3 rounded-lg border shadow-lg ${c.bg} animate-slide-in`}
        >
            <div className="flex-shrink-0 mt-0.5">{c.icon}</div>
            <p className={`flex-1 text-sm font-medium ${c.text}`}>{toast.message}</p>
            <button
                onClick={onClose}
                className={`flex-shrink-0 ${c.text} opacity-60 hover:opacity-100 transition-opacity`}
            >
                <X className="w-4 h-4" />
            </button>
        </div>
    );
}

export function useNotification() {
    const ctx = useContext(NotificationContext);
    if (!ctx) throw new Error('useNotification must be used inside NotificationProvider');
    return ctx;
}

export default NotificationContext;
