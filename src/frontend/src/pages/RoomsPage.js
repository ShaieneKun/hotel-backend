import React, { useState, useEffect } from 'react';
import { useParams, useNavigate, Link } from 'react-router-dom';
import roomService from '../api/roomService';
import reservationService from '../api/reservationService';
import authService from '../api/authService';
import './RoomPages.css';

function RoomsPage() {
    const [rooms, setRooms] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState('');
    const [filterStatus, setFilterStatus] = useState('all');
    const user = authService.getCurrentUser();

    useEffect(() => {
        loadRooms();
    }, []);

    const loadRooms = async () => {
        setLoading(true);
        try {
            const data = await roomService.getAllRooms();
            setRooms(data);
        } catch (err) {
            setError('Failed to load rooms');
        } finally {
            setLoading(false);
        }
    };

    const filteredRooms = filterStatus === 'all'
        ? rooms
        : rooms.filter(room => room.status === filterStatus);

    return (
        <div className="rooms-page">
            <div className="container">
                <div className="page-header">
                    <h1>Rooms</h1>
                    {user?.role === 'admin' && (
                        <Link to="/rooms/create" className="btn btn-primary">
                            + Create Room
                        </Link>
                    )}
                </div>

                {error && <div className="alert alert-error">{error}</div>}

                <div className="rooms-filter">
                    <label>Filter by Status:</label>
                    <select value={filterStatus} onChange={(e) => setFilterStatus(e.target.value)}>
                        <option value="all">All Rooms</option>
                        <option value="available">Available</option>
                        <option value="occupied">Occupied</option>
                        <option value="cleaning">Cleaning</option>
                        <option value="blocked">Blocked</option>
                    </select>
                </div>

                {loading ? (
                    <div className="loading"><span className="spinner"></span> Loading rooms...</div>
                ) : (
                    <div className="rooms-grid grid grid-3">
                        {filteredRooms.map(room => (
                            <Link to={`/rooms/${room.id}`} key={room.id} className="room-card">
                                <div className="room-header">
                                    <h3>Room {room.number}</h3>
                                    <span className={`room-status badge badge-${getStatusBadgeColor(room.status)}`}>
                                        {room.status}
                                    </span>
                                </div>
                                <div className="room-details">
                                    <p><strong>Type:</strong> {room.room_type}</p>
                                    <p><strong>Capacity:</strong> {room.capacity} guests</p>
                                    <p><strong>Price:</strong> ${room.price}/night</p>
                                </div>
                            </Link>
                        ))}
                    </div>
                )}
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

export default RoomsPage;
