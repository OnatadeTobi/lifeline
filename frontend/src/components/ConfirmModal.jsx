import { useState, useCallback } from 'react';
import { AlertTriangle, X } from 'lucide-react';

/**
 * Custom confirmation modal to replace window.confirm()
 * Usage:
 *   const { confirm, ConfirmModal } = useConfirmModal();
 *   const ok = await confirm('Are you sure?', 'This cannot be undone.');
 */
export function useConfirmModal() {
    const [state, setState] = useState({
        open: false,
        title: '',
        message: '',
        confirmText: 'Confirm',
        cancelText: 'Cancel',
        variant: 'danger', // 'danger' | 'info'
        resolve: null,
    });

    const confirm = useCallback(
        (title, message, options = {}) =>
            new Promise((resolve) => {
                setState({
                    open: true,
                    title,
                    message,
                    confirmText: options.confirmText || 'Confirm',
                    cancelText: options.cancelText || 'Cancel',
                    variant: options.variant || 'danger',
                    resolve,
                });
            }),
        []
    );

    const handleClose = (result) => {
        state.resolve?.(result);
        setState((prev) => ({ ...prev, open: false }));
    };

    const ConfirmModal = state.open ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4">
            {/* Backdrop */}
            <div
                className="absolute inset-0 bg-black/40 backdrop-blur-sm animate-fade-in"
                onClick={() => handleClose(false)}
            />

            {/* Modal */}
            <div className="relative bg-white rounded-2xl shadow-2xl max-w-md w-full p-6 animate-fade-in" style={{ animationDuration: '0.2s' }}>
                {/* Close button */}
                <button
                    onClick={() => handleClose(false)}
                    className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 transition-colors"
                >
                    <X className="w-5 h-5" />
                </button>

                {/* Icon */}
                <div className="flex justify-center mb-4">
                    <div
                        className={`p-3 rounded-full ${state.variant === 'danger'
                                ? 'bg-blood-50'
                                : 'bg-blue-50'
                            }`}
                    >
                        <AlertTriangle
                            className={`w-8 h-8 ${state.variant === 'danger'
                                    ? 'text-lifeline-crimson'
                                    : 'text-blue-500'
                                }`}
                        />
                    </div>
                </div>

                {/* Text */}
                <h3 className="text-xl font-bold text-lifeline-dark text-center mb-2">
                    {state.title}
                </h3>
                <p className="text-lifeline-gray text-center mb-6">
                    {state.message}
                </p>

                {/* Buttons */}
                <div className="flex space-x-3">
                    <button
                        onClick={() => handleClose(false)}
                        className="flex-1 px-4 py-2.5 bg-gray-100 text-lifeline-dark font-semibold rounded-lg hover:bg-gray-200 transition-colors"
                    >
                        {state.cancelText}
                    </button>
                    <button
                        onClick={() => handleClose(true)}
                        className={`flex-1 px-4 py-2.5 font-semibold rounded-lg transition-all ${state.variant === 'danger'
                                ? 'btn-primary'
                                : 'btn-secondary'
                            }`}
                    >
                        {state.confirmText}
                    </button>
                </div>
            </div>
        </div>
    ) : null;

    return { confirm, ConfirmModal };
}
