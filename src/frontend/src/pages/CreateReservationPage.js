import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import roomService from '../api/roomService';
import reservationService from '../api/reservationService';
import './ReservationPages.css';

function CreateReservationPage() {
    const navigate = useNavigate();
    const [rooms, setRooms] = useState([]);
    const [formData, setFormData] = useState({
        room_id: '',
        check_in: '',
        check_out: '',
        notes: '',
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);
    const [loadingRooms, setLoadingRooms] = useState(true);

    useEffect(() => {
        loadRooms();
    }, []);

    const loadRooms = async () => {
        try {
            const data = await roomService.getAllRooms();
            setRooms(data.filter(room => room.status === 'available'));
        } catch (err) {
            setError('Failed to load rooms');
        } finally {
            setLoadingRooms(false);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            const data = {
                room_id: parseInt(formData.room_id),
                check_in: formData.check_in,
                check_out: formData.check_out,
                notes: formData.notes,
            };
            const result = await reservationService.createReservation(data);
            navigate(`/reservations/${result.id}`);
        } catch (err) {
            const errorMessage = err.response?.data?.non_field_errors?.[0] ||
                err.response?.data?.detail ||
                'Failed to create reservation';
            setError(errorMessage);
        } finally {
            setLoading(false);
        }
    };

    // Calculate minimum checkout date (must be at least 1 day after check-in)
    const minCheckout = formData.check_in
        ? new Date(new Date(formData.check_in).getTime() + 24 * 60 * 60 * 1000)
            .toISOString()
            .slice(0, 16)
        : '';

    if (loadingRooms) return <div className="loading"><span className="spinner"></span> Loading rooms...</div>;

    return (
        <div className="create-reservation-page">
            <div className="container">
                <h1>New Reservation</h1>

                {error && <div className="alert alert-error">{error}</div>}

                {rooms.length === 0 ? (
                    <div className="alert alert-info">
                        No available rooms at the moment. Please try again later.
                    </div>
                ) : (
                    <div className="create-reservation-card">
                        <form onSubmit={handleSubmit}>
                            <div className="form-group">
                                <label htmlFor="room_id">Select Room *</label>
                                <select
                                    id="room_id"
                                    name="room_id"
                                    value={formData.room_id}
                                    onChange={handleChange}
                                    required
                                    disabled={loading}
                                >
                                    <option value="">-- Choose a room --</option>
                                    {rooms.map(room => (
                                        <option key={room.id} value={room.id}>
                                            Room {room.number} - {room.room_type} (${room.price}/night, capacity: {room.capacity})
                                        </option>
                                    ))}
                                </select>
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label htmlFor="check_in">Check-in *</label>
                                    <input
                                        id="check_in"
                                        type="datetime-local"
                                        name="check_in"
                                        value={formData.check_in}
                                        onChange={handleChange}
                                        required
                                        disabled={loading}
                                    />
                                </div>

                                <div className="form-group">
                                    <label htmlFor="check_out">Check-out *</label>
                                    <input
                                        id="check_out"
                                        type="datetime-local"
                                        name="check_out"
                                        value={formData.check_out}
                                        onChange={handleChange}
                                        min={minCheckout}
                                        required
                                        disabled={loading}
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label htmlFor="notes">Notes (optional)</label>
                                <textarea
                                    id="notes"
                                    name="notes"
                                    value={formData.notes}
                                    onChange={handleChange}
                                    placeholder="Any special requests or notes..."
                                    rows="4"
                                    disabled={loading}
                                />
                            </div>

                            <div className="form-actions">
                                <button type="submit" className="btn btn-primary" disabled={loading}>
                                    {loading ? <span className="spinner"></span> : 'Create Reservation'}
                                </button>
                                <button
                                    type="button"
                                    className="btn btn-secondary"
                                    onClick={() => navigate('/rooms')}
                                    disabled={loading}
                                >
                                    Cancel
                                </button>
                            </div>
                        </form>
                    </div>
                )}
            </div>
        </div>
    );
}

export default CreateReservationPage;
