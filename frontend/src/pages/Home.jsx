import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL;

export default function Home() {
    const [user, setUser] = useState(null);

    useEffect(() => {
        const fetchUser = async () => {
            const token = localStorage.getItem('token');
            if (!token) return;
            try {
                const response = await fetch(`${API_URL}/profile`, {
                    headers: { Authorization: `Bearer ${token}` },
                });
                if (response.ok) {
                    const data = await response.json();
                    setUser(data);
                } else {
                    localStorage.removeItem('token');
                }
            } catch (err) {
                console.error('Fetch user error:', err);
                localStorage.removeItem('token');
            }
        };
        fetchUser();
    }, []);

    return (
        <div className="home-container">
            <h1>Welcome to Job Application Tracker</h1>
            <p>
                Manage your job applications efficiently. Applicants can submit and track applications, while admins can review and manage all submissions.
            </p>
            {!user ? (
                <div className="auth-links">
                    <Link to="/login" className="link">Log In</Link> |{' '}
                    <Link to="/signup" className="link">Sign Up as Applicant</Link> |{' '}
                    <Link to="/admin-signup" className="link">Sign Up as Admin</Link>
                </div>
            ) : (
                <div className="auth-links">
                    {user.role === 'admin' ? (
                        <Link to="/admin" className="link">Go to Admin Dashboard</Link>
                    ) 
                    : (
                        <Link to="/profile" className="link">Go to Profile</Link>
                    )
                    }
                    <Link to="/logout" className="link">Log Out</Link>
                </div>
            )}
        </div>
    );
}