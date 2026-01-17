import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import reservationService from '../api/reservationService';
import authService from '../api/authService';
import './ReservationPages.css';

function ReservationDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [reservation, setReservation] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const [cancelReason, setCancelReason] = useState('');
    const [showCancelForm, setShowCancelForm] = useState(false);
    const user = authService.getCurrentUser();

    useEffect(() => {
        loadReservation();
    }, [id]);

    const loadReservation = async () => {
        try {
            const data = await reservationService.getReservationById(id);
            setReservation(data);
        } catch (err) {
            setError('Failed to load reservation');
        } finally {
            setLoading(false);
        }
    };

    const handleCheckIn = async () => {
        try {
            setError('');
            const updated = await reservationService.checkInReservation(id);
            setReservation(updated);
            setSuccess('Check-in successful!');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to check in');
        }
    };

    const handleCheckOut = async () => {
        try {
            setError('');
            const updated = await reservationService.checkOutReservation(id);
            setReservation(updated);
            setSuccess('Check-out successful!');
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to check out');
        }
    };

    const handleCancel = async (e) => {
        e.preventDefault();
        try {
            setError('');
            const updated = await reservationService.cancelReservation(id, cancelReason);
            setReservation(updated);
            setSuccess('Reservation cancelled successfully');
            setShowCancelForm(false);
        } catch (err) {
            setError(err.response?.data?.detail || 'Failed to cancel reservation');
        }
    };

    const canCheckIn = user?.role === 'staff' && reservation?.status === 'confirmed';
    const canCheckOut = user?.role === 'staff' && reservation?.status === 'checked_in';
    const canCancel = (user?.role === 'client' && reservation?.guest?.id === user?.id) ||
        user?.role === 'staff' ||
        user?.role === 'admin';

    if (loading) return <div className="loading"><span className="spinner"></span> Loading...</div>;
    if (!reservation) return <div className="alert alert-error">{error}</div>;

    const nights = Math.ceil(
        (new Date(reservation.check_out) - new Date(reservation.check_in)) / (1000 * 60 * 60 * 24)
    );

    return (
        <div className="reservation-detail-page">
            <div className="container">
                <Link to="/reservations" className="back-link">← Back to Reservations</Link>

                {error && <div className="alert alert-error">{error}</div>}
                {success && <div className="alert alert-success">{success}</div>}

                <div className="reservation-detail-card">
                    <div className="reservation-detail-header">
                        <div>
                            <h1>Reservation #{reservation.id}</h1>
                            <p className="reservation-guest">
                                {reservation.guest.first_name} {reservation.guest.last_name}
                                <span className="guest-email">{reservation.guest.email}</span>
                            </p>
                        </div>
                        <span className={`badge badge-${getStatusColor(reservation.status)} badge-large`}>
                            {reservation.status}
                        </span>
                    </div>

                    <div className="grid grid-2 reservation-info">
                        <div className="info-section">
                            <h3>Room Details</h3>
                            <div className="info-row">
                                <label>Room Number</label>
                                <span>Room {reservation.room.number}</span>
                            </div>
                            <div className="info-row">
                                <label>Room Type</label>
                                <span>{reservation.room.room_type}</span>
                            </div>
                            <div className="info-row">
                                <label>Capacity</label>
                                <span>{reservation.room.capacity} guests</span>
                            </div>
                            <div className="info-row">
                                <label>Price per Night</label>
                                <span>${reservation.room.price}</span>
                            </div>
                        </div>

                        <div className="info-section">
                            <h3>Reservation Details</h3>
                            <div className="info-row">
                                <label>Check-in</label>
                                <span>{new Date(reservation.check_in).toLocaleString()}</span>
                            </div>
                            <div className="info-row">
                                <label>Check-out</label>
                                <span>{new Date(reservation.check_out).toLocaleString()}</span>
                            </div>
                            <div className="info-row">
                                <label>Number of Nights</label>
                                <span>{nights} {nights === 1 ? 'night' : 'nights'}</span>
                            </div>
                            <div className="info-row">
                                <label>Total Price</label>
                                <span className="total-price">${reservation.total_price}</span>
                            </div>
                        </div>
                    </div>

                    {reservation.notes && (
                        <div className="info-section">
                            <h3>Notes</h3>
                            <p>{reservation.notes}</p>
                        </div>
                    )}

                    <div className="reservation-actions">
                        {canCheckIn && (
                            <button onClick={handleCheckIn} className="btn btn-success">
                                Check-in Guest
                            </button>
                        )}
                        {canCheckOut && (
                            <button onClick={handleCheckOut} className="btn btn-primary">
                                Check-out Guest
                            </button>
                        )}
                        {canCancel && reservation.status !== 'cancelled' && reservation.status !== 'checked_out' && (
                            <button
                                onClick={() => setShowCancelForm(!showCancelForm)}
                                className="btn btn-danger"
                            >
                                {showCancelForm ? 'Cancel Cancel' : 'Cancel Reservation'}
                            </button>
                        )}
                    </div>

                    {showCancelForm && (
                        <form onSubmit={handleCancel} className="cancel-form">
                            <div className="form-group">
                                <label htmlFor="reason">Cancellation Reason (optional)</label>
                                <textarea
                                    id="reason"
                                    value={cancelReason}
                                    onChange={(e) => setCancelReason(e.target.value)}
                                    placeholder="Why are you cancelling this reservation?"
                                    rows="4"
                                />
                            </div>
                            <div className="form-actions">
                                <button type="submit" className="btn btn-danger">
                                    Confirm Cancellation
                                </button>
                                <button
                                    type="button"
                                    onClick={() => setShowCancelForm(false)}
                                    className="btn btn-secondary"
                                >
                                    Keep Reservation
                                </button>
                            </div>
                        </form>
                    )}
                </div>
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

export default ReservationDetailPage;
