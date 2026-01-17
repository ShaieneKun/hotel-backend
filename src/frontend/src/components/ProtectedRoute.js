import React from 'react';
import { Navigate } from 'react-router-dom';
import authService from '../api/authService';

function ProtectedRoute({ children, requiredRole = null }) {
    const isAuthenticated = authService.isAuthenticated();
    const user = authService.getCurrentUser();

    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }

    if (requiredRole && user?.role !== requiredRole) {
        return <Navigate to="/unauthorized" />;
    }

    return children;
}

export default ProtectedRoute;
