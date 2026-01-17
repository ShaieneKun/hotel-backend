import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../api/authService';
import './AuthPages.css';

function RegisterPage() {
    const navigate = useNavigate();
    const [formData, setFormData] = useState({
        username: '',
        email: '',
        password: '',
        first_name: '',
        last_name: '',
        role: 'client',
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
            await authService.register(formData);
            // Auto-login after registration
            await authService.login(formData.username, formData.password);
            const user = authService.getCurrentUser();

            if (user?.role === 'admin') {
                navigate('/dashboard/admin');
            } else if (user?.role === 'staff') {
                navigate('/dashboard/staff');
            } else {
                navigate('/dashboard/client');
            }
        } catch (err) {
            setError(err.response?.data?.username?.[0] || err.response?.data?.email?.[0] || 'Registration failed. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-container">
                <div className="auth-card auth-card-large">
                    <h1 className="auth-title">🏨 Hotel Reservations</h1>
                    <p className="auth-subtitle">Create a new account</p>

                    {error && <div className="alert alert-error">{error}</div>}

                    <form onSubmit={handleSubmit}>
                        <div className="form-row">
                            <div className="form-group">
                                <label htmlFor="first_name">First Name</label>
                                <input
                                    id="first_name"
                                    type="text"
                                    name="first_name"
                                    value={formData.first_name}
                                    onChange={handleChange}
                                    placeholder="John"
                                    disabled={loading}
                                />
                            </div>

                            <div className="form-group">
                                <label htmlFor="last_name">Last Name</label>
                                <input
                                    id="last_name"
                                    type="text"
                                    name="last_name"
                                    value={formData.last_name}
                                    onChange={handleChange}
                                    placeholder="Doe"
                                    disabled={loading}
                                />
                            </div>
                        </div>

                        <div className="form-group">
                            <label htmlFor="username">Username</label>
                            <input
                                id="username"
                                type="text"
                                name="username"
                                value={formData.username}
                                onChange={handleChange}
                                placeholder="Enter username"
                                required
                                disabled={loading}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="email">Email</label>
                            <input
                                id="email"
                                type="email"
                                name="email"
                                value={formData.email}
                                onChange={handleChange}
                                placeholder="john@example.com"
                                required
                                disabled={loading}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">Password</label>
                            <input
                                id="password"
                                type="password"
                                name="password"
                                value={formData.password}
                                onChange={handleChange}
                                placeholder="Enter password"
                                required
                                disabled={loading}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="role">Role</label>
                            <select
                                id="role"
                                name="role"
                                value={formData.role}
                                onChange={handleChange}
                                disabled={loading}
                            >
                                <option value="client">Client</option>
                            </select>
                            <small style={{ color: '#666', marginTop: '4px', display: 'block' }}>
                                Only clients can self-register. Staff and admin accounts are created by administrators.
                            </small>
                        </div>

                        <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                            {loading ? <span className="spinner"></span> : 'Create Account'}
                        </button>
                    </form>

                    <div className="auth-footer">
                        <p>Already have an account? <Link to="/login">Sign in here</Link></p>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default RegisterPage;
