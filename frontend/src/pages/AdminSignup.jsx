import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function AdminSignup() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [cpassword, setCpassword] = useState('');
    const [adminCode, setAdminCode] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        if (password !== cpassword) {
        setError('Passwords do not match');
        return;
        }
        try {
        const response = await fetch('http://127.0.0.1:8000/admin-signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password, cpassword, admin_code: adminCode }),
        });
        const data = await response.json();
        if (response.ok) {
            navigate('/success', { state: { message: 'Admin account created successfully! Please log in.' } });
        } else {
            setError(data.detail || 'Admin registration failed');
        }
        } catch (err) {
        setError('An error occurred');
        }
    };

    return (
        <div>
        <form className="form-box" onSubmit={handleSubmit}>
            <h2>Admin Registration</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <p>
            <label htmlFor="name">Full Name:</label>
            <input type="text" name="name" value={name} onChange={(e) => setName(e.target.value)} required />
            </p>
            <p>
            <label htmlFor="email">Email:</label>
            <input type="email" name="email" value={email} onChange={(e) => setEmail(e.target.value)} required />
            </p>
            <p>
            <label htmlFor="password">Password:</label>
            <input type="password" name="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
            </p>
            <p>
            <label htmlFor="cpassword">Confirm Password:</label>
            <input type="password" name="cpassword" value={cpassword} onChange={(e) => setCpassword(e.target.value)} required />
            </p>
            <p>
            <label htmlFor="adminCode">Admin Code:</label>
            <input type="text" name="adminCode" value={adminCode} onChange={(e) => setAdminCode(e.target.value)} required />
            </p>
            <button type="submit">Register as Admin</button>
            <p className="btn">
                Already have an account? <br />
                <Link to="/login" className="link">Log In</Link>
            </p>
        </form>
        </div>
    );
}