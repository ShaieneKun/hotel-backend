import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import reservationService from '../api/reservationService';
import roomService from '../api/roomService';
import './DashboardPages.css';

function AdminDashboard() {
    const [reservations, setReservations] = useState([]);
    const [rooms, setRooms] = useState([]);
    const [stats, setStats] = useState({
        totalRooms: 0,
        totalReservations: 0,
        activeReservations: 0,
        occupancyRate: 0,
    });
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const [reservationsData, roomsData] = await Promise.all([
                reservationService.getAllReservations(),
                roomService.getAllRooms(),
            ]);

            setReservations(reservationsData);
            setRooms(roomsData);

            // Calculate stats
            const totalRooms = roomsData.length;
            const totalReservations = reservationsData.length;
            const activeReservations = reservationsData.filter(
                r => r.status === 'confirmed' || r.status === 'checked_in'
            ).length;
            const occupancyRate = totalRooms > 0 ? Math.round((activeReservations / totalRooms) * 100) : 0;

            setStats({ totalRooms, totalReservations, activeReservations, occupancyRate });
        } catch (err) {
            setError('Failed to load data');
        } finally {
            setLoading(false);
        }
    };

    const roomStatusSummary = rooms.reduce((acc, room) => {
        acc[room.status] = (acc[room.status] || 0) + 1;
        return acc;
    }, {});

    return (
        <div className="dashboard">
            <div className="container">
                <h1>Admin Dashboard</h1>

                {error && <div className="alert alert-error">{error}</div>}

                <div className="dashboard-stats grid grid-3">
                    <div className="stat-card">
                        <div className="stat-number">{stats.totalRooms}</div>
                        <div className="stat-label">Total Rooms</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{stats.totalReservations}</div>
                        <div className="stat-label">Total Reservations</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{stats.occupancyRate}%</div>
                        <div className="stat-label">Occupancy Rate</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{stats.activeReservations}</div>
                        <div className="stat-label">Active Bookings</div>
                    </div>
                </div>

                <div className="dashboard-actions">
                    <Link to="/rooms" className="btn btn-primary">
                        Manage Rooms
                    </Link>
                    <Link to="/rooms/create" className="btn btn-success">
                        + Create Room
                    </Link>
                    <Link to="/reservations" className="btn btn-secondary">
                        Manage Reservations
                    </Link>
                </div>

                {loading ? (
                    <div className="loading"><span className="spinner"></span> Loading...</div>
                ) : (
                    <>
                        <div className="grid grid-2">
                            <div className="card">
                                <div className="card-header">Room Status Summary</div>
                                <div className="status-summary">
                                    {Object.entries(roomStatusSummary).map(([status, count]) => (
                                        <div key={status} className="status-item">
                                            <span className="status-label">{status}</span>
                                            <span className={`status-count badge-${getStatusBadgeColor(status)}`}>
                                                {count}
                                            </span>
                                        </div>
                                    ))}
                                </div>
                            </div>

                            <div className="card">
                                <div className="card-header">Reservation Summary</div>
                                <div className="status-summary">
                                    {['confirmed', 'checked_in', 'checked_out', 'cancelled'].map(status => {
                                        const count = reservations.filter(r => r.status === status).length;
                                        return (
                                            <div key={status} className="status-item">
                                                <span className="status-label">{status}</span>
                                                <span className={`status-count badge-${getStatusBadgeColor(status)}`}>
                                                    {count}
                                                </span>
                                            </div>
                                        );
                                    })}
                                </div>
                            </div>
                        </div>

                        <div className="card">
                            <div className="card-header">Recent Reservations</div>
                            <table>
                                <thead>
                                    <tr>
                                        <th>Guest</th>
                                        <th>Room</th>
                                        <th>Check-in</th>
                                        <th>Check-out</th>
                                        <th>Status</th>
                                        <th>Actions</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {reservations.slice(0, 10).map(reservation => (
                                        <tr key={reservation.id}>
                                            <td>{reservation.guest.first_name} {reservation.guest.last_name}</td>
                                            <td>{reservation.room.number}</td>
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
                        </div>
                    </>
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

function getStatusBadgeColor(status) {
    const colors = {
        'available': 'success',
        'occupied': 'danger',
        'cleaning': 'warning',
        'blocked': 'danger',
    };
    return colors[status] || 'primary';
}

export default AdminDashboard;
