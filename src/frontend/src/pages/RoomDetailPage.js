import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import roomService from '../api/roomService';
import authService from '../api/authService';
import './RoomPages.css';

function RoomDetailPage() {
    const { id } = useParams();
    const navigate = useNavigate();
    const [room, setRoom] = useState(null);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [isEditing, setIsEditing] = useState(false);
    const [formData, setFormData] = useState({});
    const user = authService.getCurrentUser();

    useEffect(() => {
        loadRoom();
    }, [id]);

    const loadRoom = async () => {
        try {
            const data = await roomService.getRoomById(id);
            setRoom(data);
            setFormData(data);
        } catch (err) {
            setError('Failed to load room');
        } finally {
            setLoading(false);
        }
    };

    const handleChange = (e) => {
        setFormData({
            ...formData,
            [e.target.name]: e.target.value,
        });
    };

    const handleSave = async () => {
        try {
            await roomService.updateRoom(id, formData);
            setRoom(formData);
            setIsEditing(false);
        } catch (err) {
            setError('Failed to update room');
        }
    };

    const handleDelete = async () => {
        if (window.confirm('Are you sure you want to delete this room?')) {
            try {
                await roomService.deleteRoom(id);
                navigate('/rooms');
            } catch (err) {
                setError('Failed to delete room');
            }
        }
    };

    if (loading) return <div className="loading"><span className="spinner"></span> Loading...</div>;
    if (!room) return <div className="alert alert-error">{error}</div>;

    return (
        <div className="room-detail-page">
            <div className="container">
                <Link to="/rooms" className="back-link">← Back to Rooms</Link>

                {error && <div className="alert alert-error">{error}</div>}

                <div className="room-detail-card">
                    <div className="room-detail-header">
                        <h1>Room {room.number}</h1>
                        <span className={`badge badge-${getStatusBadgeColor(room.status)}`}>
                            {room.status}
                        </span>
                    </div>

                    {!isEditing ? (
                        <div className="room-detail-view">
                            <div className="detail-row">
                                <label>Type</label>
                                <span>{room.room_type}</span>
                            </div>
                            <div className="detail-row">
                                <label>Capacity</label>
                                <span>{room.capacity} guests</span>
                            </div>
                            <div className="detail-row">
                                <label>Price per Night</label>
                                <span>${room.price}</span>
                            </div>
                            <div className="detail-row">
                                <label>Status</label>
                                <span>{room.status}</span>
                            </div>
                            <div className="detail-row">
                                <label>Active</label>
                                <span>{room.is_active ? 'Yes' : 'No'}</span>
                            </div>

                            {user?.role === 'admin' && (
                                <div className="room-detail-actions">
                                    <button onClick={() => setIsEditing(true)} className="btn btn-primary">
                                        Edit Room
                                    </button>
                                    <button onClick={handleDelete} className="btn btn-danger">
                                        Delete Room
                                    </button>
                                </div>
                            )}
                        </div>
                    ) : (
                        <div className="room-detail-edit">
                            <div className="form-group">
                                <label>Room Number</label>
                                <input
                                    type="text"
                                    name="number"
                                    value={formData.number}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="form-group">
                                <label>Room Type</label>
                                <input
                                    type="text"
                                    name="room_type"
                                    value={formData.room_type}
                                    onChange={handleChange}
                                />
                            </div>

                            <div className="form-row">
                                <div className="form-group">
                                    <label>Capacity</label>
                                    <input
                                        type="number"
                                        name="capacity"
                                        value={formData.capacity}
                                        onChange={handleChange}
                                        min="1"
                                    />
                                </div>

                                <div className="form-group">
                                    <label>Price per Night</label>
                                    <input
                                        type="number"
                                        name="price"
                                        value={formData.price}
                                        onChange={handleChange}
                                        step="0.01"
                                    />
                                </div>
                            </div>

                            <div className="form-group">
                                <label>Status</label>
                                <select name="status" value={formData.status} onChange={handleChange}>
                                    <option value="available">Available</option>
                                    <option value="occupied">Occupied</option>
                                    <option value="cleaning">Cleaning</option>
                                    <option value="blocked">Blocked</option>
                                </select>
                            </div>

                            <div className="form-group">
                                <label>
                                    <input
                                        type="checkbox"
                                        name="is_active"
                                        checked={formData.is_active}
                                        onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                    />
                                    Active
                                </label>
                            </div>

                            <div className="room-detail-actions">
                                <button onClick={handleSave} className="btn btn-success">
                                    Save Changes
                                </button>
                                <button onClick={() => setIsEditing(false)} className="btn btn-secondary">
                                    Cancel
                                </button>
                            </div>
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
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

export default RoomDetailPage;
