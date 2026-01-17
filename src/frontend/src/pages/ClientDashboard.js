import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import reservationService from '../api/reservationService';
import roomService from '../api/roomService';
import './DashboardPages.css';

function ClientDashboard() {
    const [reservations, setReservations] = useState([]);
    const [stats, setStats] = useState({ total: 0, active: 0, completed: 0 });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const data = await reservationService.getAllReservations();
            setReservations(data);

            // Calculate stats
            const total = data.length;
            const active = data.filter(r => r.status === 'confirmed' || r.status === 'checked_in').length;
            const completed = data.filter(r => r.status === 'checked_out').length;
            setStats({ total, active, completed });
        } catch (err) {
            setError('Failed to load reservations');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard">
            <div className="container">
                <h1>Client Dashboard</h1>

                {error && <div className="alert alert-error">{error}</div>}

                <div className="dashboard-stats grid grid-3">
                    <div className="stat-card">
                        <div className="stat-number">{stats.total}</div>
                        <div className="stat-label">Total Reservations</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{stats.active}</div>
                        <div className="stat-label">Active Bookings</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{stats.completed}</div>
                        <div className="stat-label">Completed Stays</div>
                    </div>
                </div>

                <div className="dashboard-actions">
                    <Link to="/rooms" className="btn btn-primary">
                        Browse Rooms
                    </Link>
                    <Link to="/my-reservations" className="btn btn-secondary">
                        View All Reservations
                    </Link>
                </div>

                {loading ? (
                    <div className="loading"><span className="spinner"></span> Loading...</div>
                ) : (
                    <div className="card">
                        <div className="card-header">Recent Reservations</div>
                        {reservations.length === 0 ? (
                            <p style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                                No reservations yet. <Link to="/rooms">Browse rooms</Link> to make a reservation.
                            </p>
                        ) : (
                            <table>
                                <thead>
                                    <tr>
                                        <th>Room</th>
                                        <th>Check-in</th>
                                        <th>Check-out</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {reservations.slice(0, 5).map(reservation => (
                                        <tr key={reservation.id}>
                                            <td>{reservation.room.number} ({reservation.room.room_type})</td>
                                            <td>{new Date(reservation.check_in).toLocaleDateString()}</td>
                                            <td>{new Date(reservation.check_out).toLocaleDateString()}</td>
                                            <td>
                                                <span className={`badge badge-${getStatusColor(reservation.status)}`}>
                                                    {reservation.status}
                                                </span>
                                            </td>
                                            <td>
                                                <Link to={`/reservations/${reservation.id}`} className="btn btn-small">
                                                    View
                                                </Link>
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
}

function getStatusColor(status) {
    const colors = {
        'confirmed': 'primary',
        'checked_in': 'success',
        'checked_out': 'success',
        'cancelled': 'danger',
        'no_show': 'warning',
    };
    return colors[status] || 'primary';
}

export default ClientDashboard;
