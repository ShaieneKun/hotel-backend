import React from 'react';
import { Link, useNavigate } from 'react-router-dom';
import authService from '../api/authService';
import './Navigation.css';

function Navigation() {
    const navigate = useNavigate();
    const user = authService.getCurrentUser();
    const isAuthenticated = authService.isAuthenticated();

    const handleLogout = () => {
        authService.logout();
        navigate('/login');
    };

    const getNavLinks = () => {
        if (!isAuthenticated) {
            return null;
        }

        const role = user?.role;
        const baseLinks = (
            <>
                {role === 'client' && (
                    <>
                        <Link to="/dashboard/client" className="nav-link">Dashboard</Link>
                        <Link to="/rooms" className="nav-link">Browse Rooms</Link>
                        <Link to="/my-reservations" className="nav-link">My Reservations</Link>
                    </>
                )}
                {role === 'staff' && (
                    <>
                        <Link to="/dashboard/staff" className="nav-link">Dashboard</Link>
                        <Link to="/reservations" className="nav-link">All Reservations</Link>
                        <Link to="/rooms" className="nav-link">Rooms</Link>
                    </>
                )}
                {role === 'admin' && (
                    <>
                        <Link to="/dashboard/admin" className="nav-link">Dashboard</Link>
                        <Link to="/reservations" className="nav-link">Reservations</Link>
                        <Link to="/rooms" className="nav-link">Rooms</Link>
                        <Link to="/rooms/create" className="nav-link">Create Room</Link>
                    </>
                )}
            </>
        );

        return baseLinks;
    };

    return (
        <nav className="navbar">
            <div className="navbar-container">
                <Link to="/" className="navbar-brand">
                    🏨 Hotel Reservations
                </Link>

                <div className="navbar-links">
                    {getNavLinks()}
                </div>

                {isAuthenticated && (
                    <div className="navbar-user">
                        <span className="user-info">
                            {user?.username}
                            <span className="user-role">{user?.role}</span>
                        </span>
                        <button onClick={handleLogout} className="btn btn-secondary btn-small">
                            Logout
                        </button>
                    </div>
                )}
            </div>
        </nav>
    );
}

export default Navigation;
