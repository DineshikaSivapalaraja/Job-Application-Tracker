import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function EditProfile() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const [success, setSuccess] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
        e.preventDefault();
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
            return;
        }

    const updateData = {};
    if (name) updateData.name = name;
    if (email) updateData.email = email;
    if (password) updateData.password = password;

    if (!name && !email && !password) {
        setError('Please provide at least one field to update.');
        return;
        }

        try {
        const response = await fetch(`http://127.0.0.1:8000/profile`, {
            method: 'PUT',
            headers: {
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}`,
            },
            body: JSON.stringify(updateData),
        });
        if (response.ok) {
            const data = await response.json();
            console.log('Update response:', data); 
            setSuccess('Profile updated successfully!');
            setTimeout(() => navigate('/profile'), 1000);
        } else {
            const data = await response.json();
            setError(data.detail || 'Update failed');
        }
        } catch (err) {
        setError('Network error occurred');
        console.error(err);
        }
    };

    return (
        <>
        <div className='form-wrapper'>
        <div className='form-box'>
        <h2>Edit Profile</h2>
        {error && <p style={{ color: 'red' }}>{error}</p>}
        {success && <p style={{ color: 'green' }}>{success}</p>}
        <form onSubmit={handleSubmit}>
            <label>
            Name:
            <input
                type="text"
                value={name}
                onChange={(e) => setName(e.target.value)}
                placeholder="Enter new name (optional)"
            />
            </label><br />
            <label>
            Email:
            <input
                type="email"
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Enter new email (optional)"
            />
            </label><br />
            <label>
            Password:
            <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="Enter new password (optional)"
            />
            </label><br />
            <button type="submit">Save Changes</button>
        </form>
        </div>
        </div>
        </>
    );
}