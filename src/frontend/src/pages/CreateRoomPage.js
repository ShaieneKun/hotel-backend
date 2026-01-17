import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import roomService from '../api/roomService';
import './RoomPages.css';

function CreateRoomPage() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        number: '',
        room_type: '',
        capacity: 1,
        price: '',
        is_active: true,
    });
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

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
            const roomData = {
                ...formData,
                capacity: parseInt(formData.capacity),
                price: parseFloat(formData.price),
            };
            await roomService.createRoom(roomData);
            navigate('/rooms');
        } catch (err) {
            setError(err.response?.data?.non_field_errors?.[0] || 'Failed to create room');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="create-room-page">
            <div className="container">
                <h1>Create New Room</h1>

                {error && <div className="alert alert-error">{error}</div>}

                <div className="create-room-card">
                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="number">Room Number *</label>
                            <input
                                id="number"
                                type="text"
                                name="number"
                                value={formData.number}
                                onChange={handleChange}
                                placeholder="e.g., 301"
                                required
                                disabled={loading}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="room_type">Room Type *</label>
                            <input
                                id="room_type"
                                type="text"
                                name="room_type"
                                value={formData.room_type}
                                onChange={handleChange}
                                placeholder="e.g., Deluxe, Standard"
                                required
                                disabled={loading}
                            />
                        </div>

                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="capacity">Capacity *</label>
                                <input
                                    id="capacity"
                                    type="number"
                                    name="capacity"
                                    value={formData.capacity}
                                    onChange={handleChange}
                                    min="1"
                                    required
                                    disabled={loading}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="price">Price per Night *</label>
                                <input
                                    id="price"
                                    type="number"
                                    name="price"
                                    value={formData.price}
                                    onChange={handleChange}
                                    step="0.01"
                                    min="0"
                                    required
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label>
                                <input
                                    type="checkbox"
                                    name="is_active"
                                    checked={formData.is_active}
                                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                    disabled={loading}
                                />
                                Active
                            </label>
                        </div>

                        <div className="form-actions">
                            <button type="submit" className="btn btn-primary" disabled={loading}>
                                {loading ? <span className="spinner"></span> : 'Create Room'}
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
            </div>
        </div>
    );
}

export default CreateRoomPage;
