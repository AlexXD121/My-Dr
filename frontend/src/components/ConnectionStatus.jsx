import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import apiService from '../services/api';

const ConnectionStatus = () => {
    const [status, setStatus] = useState('checking');
    const [showStatus, setShowStatus] = useState(false);
    const [statusChangeTime, setStatusChangeTime] = useState(null);

    const checkConnection = async () => {
        const previousStatus = status;
        try {
            setStatus('checking');
            await apiService.healthCheck();
            if (previousStatus !== 'connected') {
                setStatus('connected');
                setShowStatus(true);
                setStatusChangeTime(Date.now());
            } else {
                setStatus('connected');
            }
        } catch (error) {
            console.error('Connection check failed:', error);
            if (previousStatus !== 'disconnected') {
                setStatus('disconnected');
                setShowStatus(true);
                setStatusChangeTime(Date.now());
            } else {
                setStatus('disconnected');
            }
        }
    };

    useEffect(() => {
        checkConnection();
        const interval = setInterval(checkConnection, 30000); // Check every 30s
        return () => clearInterval(interval);
    }, []);

    // Hide status after 5 seconds
    useEffect(() => {
        if (showStatus && statusChangeTime) {
            const timer = setTimeout(() => {
                setShowStatus(false);
            }, 5000);
            return () => clearTimeout(timer);
        }
    }, [showStatus, statusChangeTime]);

    const getStatusColor = () => {
        switch (status) {
            case 'checking': return 'bg-yellow-500';
            case 'connected': return 'bg-green-500';
            case 'disconnected': return 'bg-red-500';
            default: return 'bg-gray-500';
        }
    };

    const getStatusText = () => {
        switch (status) {
            case 'checking': return 'Checking...';
            case 'connected': return 'Connected';
            case 'disconnected': return 'Connection lost';
            default: return 'Unknown';
        }
    };

    const getStatusIcon = () => {
        switch (status) {
            case 'checking': return '⏳';
            case 'connected': return '✅';
            case 'disconnected': return '❌';
            default: return '❓';
        }
    };

    return (
        <AnimatePresence>
            {showStatus && (
                <motion.div
                    initial={{ opacity: 0, x: -100 }}
                    animate={{ opacity: 1, x: 0 }}
                    exit={{ opacity: 0, x: -100 }}
                    className="fixed bottom-4 left-4 z-50"
                >
                    <div className={`${getStatusColor()} text-white px-3 py-2 rounded-lg shadow-lg backdrop-blur-sm`}>
                        <div className="flex items-center gap-2">
                            <span className="text-sm">{getStatusIcon()}</span>
                            <span className="text-xs font-medium">
                                {getStatusText()}
                            </span>
                        </div>
                    </div>
                </motion.div>
            )}
        </AnimatePresence>
    );
};

export default ConnectionStatus;