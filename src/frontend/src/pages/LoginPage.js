import React, { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import authService from '../api/authService';
import './AuthPages.css';

function LoginPage() {
    const navigate = useNavigate();
    const [username, setUsername] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [loading, setLoading] = useState(false);

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        setLoading(true);

        try {
            await authService.login(username, password);
            const user = authService.getCurrentUser();

            // Redirect based on role
            if (user?.role === 'admin') {
                navigate('/dashboard/admin');
            } else if (user?.role === 'staff') {
                navigate('/dashboard/staff');
            } else {
                navigate('/dashboard/client');
            }
        } catch (err) {
            setError(err.response?.data?.detail || 'Invalid credentials. Please try again.');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="auth-page">
            <div className="auth-container">
                <div className="auth-card">
                    <h1 className="auth-title">🏨 Hotel Reservations</h1>
                    <p className="auth-subtitle">Sign in to your account</p>

                    {error && <div className="alert alert-error">{error}</div>}

                    <form onSubmit={handleSubmit}>
                        <div className="form-group">
                            <label htmlFor="username">Username</label>
                            <input
                                id="username"
                                type="text"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                placeholder="Enter your username"
                                required
                                disabled={loading}
                            />
                        </div>

                        <div className="form-group">
                            <label htmlFor="password">Password</label>
                            <input
                                id="password"
                                type="password"
                                value={password}
                                onChange={(e) => setPassword(e.target.value)}
                                placeholder="Enter your password"
                                required
                                disabled={loading}
                            />
                        </div>

                        <button type="submit" className="btn btn-primary btn-block" disabled={loading}>
                            {loading ? <span className="spinner"></span> : 'Sign In'}
                        </button>
                    </form>

                    <div className="auth-footer">
                        <p>Don't have an account? <Link to="/register">Sign up here</Link></p>
                    </div>

                    <div className="demo-credentials">
                        <p>Demo Credentials:</p>
                        <small>Client: client1 / password123</small>
                        <small>Staff: staff1 / password123</small>
                        <small>Admin: admin / password123</small>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default LoginPage;
