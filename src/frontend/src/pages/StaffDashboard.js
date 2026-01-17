import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import reservationService from '../api/reservationService';
import roomService from '../api/roomService';
import './DashboardPages.css';

function StaffDashboard() {
    const [reservations, setReservations] = useState([]);
    const [rooms, setRooms] = useState([]);
    const [stats, setStats] = useState({
        totalReservations: 0,
        checkedIn: 0,
        pendingCheckIn: 0,
        availableRooms: 0,
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
            const totalReservations = reservationsData.length;
            const checkedIn = reservationsData.filter(r => r.status === 'checked_in').length;
            const pendingCheckIn = reservationsData.filter(r => r.status === 'confirmed').length;
            const availableRooms = roomsData.filter(r => r.status === 'available').length;

            setStats({ totalReservations, checkedIn, pendingCheckIn, availableRooms });
        } catch (err) {
            setError('Failed to load data');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="dashboard">
            <div className="container">
                <h1>Staff Dashboard</h1>

                {error && <div className="alert alert-error">{error}</div>}

                <div className="dashboard-stats grid grid-3">
                    <div className="stat-card">
                        <div className="stat-number">{stats.totalReservations}</div>
                        <div className="stat-label">Total Reservations</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{stats.checkedIn}</div>
                        <div className="stat-label">Checked In</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{stats.pendingCheckIn}</div>
                        <div className="stat-label">Pending Check-in</div>
                    </div>
                    <div className="stat-card">
                        <div className="stat-number">{stats.availableRooms}</div>
                        <div className="stat-label">Available Rooms</div>
                    </div>
                </div>

                <div className="dashboard-actions">
                    <Link to="/reservations" className="btn btn-primary">
                        View All Reservations
                    </Link>
                    <Link to="/rooms" className="btn btn-secondary">
                        View Rooms
                    </Link>
                </div>

                {loading ? (
                    <div className="loading"><span className="spinner"></span> Loading...</div>
                ) : (
                    <>
                        <div className="card">
                            <div className="card-header">Pending Check-ins</div>
                            {reservations.filter(r => r.status === 'confirmed').length === 0 ? (
                                <p style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                                    No pending check-ins
                                </p>
                            ) : (
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Guest</th>
                                            <th>Room</th>
                                            <th>Check-in</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {reservations.filter(r => r.status === 'confirmed').map(reservation => (
                                            <tr key={reservation.id}>
                                                <td>{reservation.guest.first_name} {reservation.guest.last_name}</td>
                                                <td>{reservation.room.number}</td>
                                                <td>{new Date(reservation.check_in).toLocaleDateString()}</td>
                                                <td>
                                                    <Link to={`/reservations/${reservation.id}`} className="btn btn-small btn-primary">
                                                        Check-in
                                                    </Link>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>

                        <div className="card">
                            <div className="card-header">Currently Checked In</div>
                            {reservations.filter(r => r.status === 'checked_in').length === 0 ? (
                                <p style={{ padding: '20px', textAlign: 'center', color: '#999' }}>
                                    No guests currently checked in
                                </p>
                            ) : (
                                <table>
                                    <thead>
                                        <tr>
                                            <th>Guest</th>
                                            <th>Room</th>
                                            <th>Check-out</th>
                                            <th>Actions</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        {reservations.filter(r => r.status === 'checked_in').map(reservation => (
                                            <tr key={reservation.id}>
                                                <td>{reservation.guest.first_name} {reservation.guest.last_name}</td>
                                                <td>{reservation.room.number}</td>
                                                <td>{new Date(reservation.check_out).toLocaleDateString()}</td>
                                                <td>
                                                    <Link to={`/reservations/${reservation.id}`} className="btn btn-small btn-success">
                                                        Check-out
                                                    </Link>
                                                </td>
                                            </tr>
                                        ))}
                                    </tbody>
                                </table>
                            )}
                        </div>
                    </>
                )}
            </div>
        </div>
    );
}

export default StaffDashboard;
