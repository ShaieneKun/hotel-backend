import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import reservationService from '../api/reservationService';
import authService from '../api/authService';
import './ReservationPages.css';

function ReservationsPage() {
    const [reservations, setReservations] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const user = authService.getCurrentUser();

    useEffect(() => {
        loadReservations();
    }, []);

    const loadReservations = async () => {
        setLoading(true);
        try {
            const data = await reservationService.getAllReservations();
            setReservations(data);
        } catch (err) {
            setError('Failed to load reservations');
        } finally {
            setLoading(false);
        }
    };

    const filteredReservations = filterStatus === 'all'
        ? reservations
        : reservations.filter(r => r.status === filterStatus);

    return (
        <div className="reservations-page">
            <div className="container">
                <div className="page-header">
                    <h1>Reservations</h1>
                    {user?.role === 'client' && (
                        <Link to="/rooms" className="btn btn-primary">
                            + New Reservation
                        </Link>
                    )}
                </div>

                {error && <div className="alert alert-error">{error}</div>}

                <div className="reservations-filter">
                    <label>Filter by Status:</label>
                    <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
                        <option value="all">All Reservations</option>
                        <option value="confirmed">Confirmed</option>
                        <option value="checked_in">Checked In</option>
                        <option value="checked_out">Checked Out</option>
                        <option value="cancelled">Cancelled</option>
                        <option value="no_show">No Show</option>
                    </select>
                </div>

                {loading ? (
                    <div className="loading"><span className="spinner"></span> Loading reservations...</div>
                ) : filteredReservations.length === 0 ? (
                    <div className="alert alert-info">No reservations found</div>
                ) : (
                    <div className="reservations-table">
                        <table>
                            <thead>
                                <tr>
                                    <th>Guest</th>
                                    <th>Room</th>
                                    <th>Check-in</th>
                                    <th>Check-out</th>
                                    <th>Status</th>
                                    <th>Price</th>
                                    <th>Actions</th>
                                </tr>
                            </thead>
                            <tbody>
                                {filteredReservations.map(reservation => (
                                    <tr key={reservation.id}>
                                        <td>{reservation.guest.first_name} {reservation.guest.last_name}</td>
                                        <td>Room {reservation.room.number}</td>
                                        <td>{new Date(reservation.check_in).toLocaleDateString()}</td>
                                        <td>{new Date(reservation.check_out).toLocaleDateString()}</td>
                                        <td>
                                            <span className={`badge badge-${getStatusColor(reservation.status)}`}>
                                                {reservation.status}
                                            </span>
                                        </td>
                                        <td>${reservation.total_price}</td>
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

export default ReservationsPage;
