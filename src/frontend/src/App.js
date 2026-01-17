import React from 'react';
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Navigation from './components/Navigation';
import ProtectedRoute from './components/ProtectedRoute';
import authService from './api/authService';

// Auth Pages
import LoginPage from './pages/LoginPage';
import RegisterPage from './pages/RegisterPage';
import UnauthorizedPage from './pages/UnauthorizedPage';

// Dashboard Pages
import ClientDashboard from './pages/ClientDashboard';
import StaffDashboard from './pages/StaffDashboard';
import AdminDashboard from './pages/AdminDashboard';

// Room Pages
import RoomsPage from './pages/RoomsPage';
import RoomDetailPage from './pages/RoomDetailPage';
import CreateRoomPage from './pages/CreateRoomPage';

// Reservation Pages
import ReservationsPage from './pages/ReservationsPage';
import ReservationDetailPage from './pages/ReservationDetailPage';
import CreateReservationPage from './pages/CreateReservationPage';

function HomePage() {
    const isAuthenticated = authService.isAuthenticated();

    if (!isAuthenticated) {
        return <Navigate to="/login" />;
    }

    const user = authService.getCurrentUser();
    if (user?.role === 'admin') {
        return <Navigate to="/dashboard/admin" />;
    } else if (user?.role === 'staff') {
        return <Navigate to="/dashboard/staff" />;
    } else {
        return <Navigate to="/dashboard/client" />;
    }
}

function App() {
    return (
        <BrowserRouter>
            <Navigation />
            <Routes>
                {/* Public Routes */}
                <Route path="/login" element={<LoginPage />} />
                <Route path="/register" element={<RegisterPage />} />
                <Route path="/unauthorized" element={<UnauthorizedPage />} />

                {/* Home Route */}
                <Route path="/" element={<HomePage />} />

                {/* Dashboard Routes */}
                <Route
                    path="/dashboard/client"
                    element={
                        <ProtectedRoute requiredRole="client">
                            <ClientDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/dashboard/staff"
                    element={
                        <ProtectedRoute requiredRole="staff">
                            <StaffDashboard />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/dashboard/admin"
                    element={
                        <ProtectedRoute requiredRole="admin">
                            <AdminDashboard />
                        </ProtectedRoute>
                    }
                />

                {/* Room Routes */}
                <Route
                    path="/rooms"
                    element={
                        <ProtectedRoute>
                            <RoomsPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/rooms/:id"
                    element={
                        <ProtectedRoute>
                            <RoomDetailPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/rooms/create"
                    element={
                        <ProtectedRoute requiredRole="admin">
                            <CreateRoomPage />
                        </ProtectedRoute>
                    }
                />

                {/* Reservation Routes */}
                <Route
                    path="/reservations"
                    element={
                        <ProtectedRoute>
                            <ReservationsPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/reservations/:id"
                    element={
                        <ProtectedRoute>
                            <ReservationDetailPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/reservations/create"
                    element={
                        <ProtectedRoute requiredRole="client">
                            <CreateReservationPage />
                        </ProtectedRoute>
                    }
                />
                <Route
                    path="/rooms/:roomId/reserve"
                    element={
                        <ProtectedRoute requiredRole="client">
                            <CreateReservationPage />
                        </ProtectedRoute>
                    }
                />

                {/* Alias for client my-reservations */}
                <Route
                    path="/my-reservations"
                    element={
                        <ProtectedRoute requiredRole="client">
                            <ReservationsPage />
                        </ProtectedRoute>
                    }
                />

                {/* Catch all */}
                <Route path="*" element={<Navigate to="/" />} />
            </Routes>
        </BrowserRouter>
    );
}

export default App;
