import React from 'react';
import { Link } from 'react-router-dom';
import './ErrorPages.css';

function UnauthorizedPage() {
    return (
        <div className="error-page">
            <div className="error-container">
                <div className="error-code">403</div>
                <h1 className="error-title">Unauthorized</h1>
                <p className="error-description">
                    You don't have permission to access this resource.
                </p>
                <Link to="/" className="btn btn-primary">
                    Go to Home
                </Link>
            </div>
        </div>
    );
}

export default UnauthorizedPage;
