import { useNavigate } from 'react-router-dom';

export default function Success() {
    const navigate = useNavigate();
    
    const handleLogout = () => {
        localStorage.removeItem('token');
        navigate('/login');
    };

    return(
        <>
        <div>
            <p>Application submitted successfully!</p>
            {/* <a href="Profile.jsx">Back to profile</a> */}
            <a href="#" onClick={() => navigate('/profile')}>Back to profile</a>
            <br />
            <a href="#" onClick={handleLogout}>Logout</a>
            {/* <a href="Logout.jsx">Logout</a> */}
        </div>
        </>
    );
}