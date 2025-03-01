import React from 'react';
import '../styles/loading-overlay.css';

const LoadingOverlay: React.FC = () => {
    return (
        <div className="loading-overlay">
            <div className="spinner"></div>
        </div>
    );
};

export default LoadingOverlay;
