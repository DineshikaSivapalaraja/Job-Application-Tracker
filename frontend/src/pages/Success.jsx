import { useNavigate, useLocation } from 'react-router-dom';

export default function Success() {
    const navigate = useNavigate();
    const location = useLocation();
    const message = location.state?.message || 'Action completed successfully!';

    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return (
        <>
        <div className="success-container">
            <h2>Success</h2>
            <p>{message}</p>
            <button onClick={() => navigate('/profile')}>Back to Profile</button>
            <button onClick={handleLogout}>Logout</button>
        </div>
        </>
    );
}