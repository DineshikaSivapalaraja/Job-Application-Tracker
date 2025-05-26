import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Profile() {
    const [user, setUser] = useState(null);
    const [applications, setApplications] = useState([]);
    const [error, setError] = useState(null);
    const [loading, setLoading] = useState(true);
    const navigate = useNavigate();

    useEffect(() => {
        const fetchData = async () => {
        const token = localStorage.getItem('token');
        if (!token) {
            navigate('/login');
            return;
        }
        try {
            const userResponse = await fetch(`http://127.0.0.1:8000/profile`, {
                headers: { Authorization: `Bearer ${token}` },
            });
            //added
            if (!userResponse.ok) {
                throw new Error('Failed to fetch user data');
            }
            const userData = await userResponse.json();
            setUser(userData);

            //added--> fetch application only for applicants
            if (userData.role === 'applicant') {
            const appResponse = await fetch('http://127.0.0.1:8000/applications', {
                headers: { Authorization: `Bearer ${token}` },
            });
            //added
            if (!appResponse.ok) {
                throw new Error('Failed to fetch applications');
            }
            const appData = await appResponse.json();
            setApplications(appData.applications);
            }
        } catch (err) {
            console.error('Error fetching data:', err);
            // setError('Failed to load profile or applications. Please try again or log in.');
        } finally {  //added
            setLoading(false);
        }
        };
        fetchData();
    }, [navigate]);

    const handleDelete = async (appId) => {
        const token = localStorage.getItem('token');
        try {
            const response = await fetch(`http://127.0.0.1:8000/applications/${appId}`, {
                method: 'DELETE',
                headers: { Authorization: `Bearer ${token}` },
            });
            if (response.ok) {
                setApplications(applications.filter(app => app.id !== appId));
            } else {
                throw new Error('Failed to delete application');
            }
        } catch (err) {
            console.error('Error deleting application:', err);
            setError('Failed to delete application. Please try again.');
        }
    };

    const handleEditApplication = (appId) => {
        navigate(`/application?edit=${appId}`); //navigate to edit application
    };

    const handleEditProfile = () => {
        navigate('/edit-profile'); //navigate to edit user profile
    };

    const handleAdminDashboard = () => {
        navigate('/admin'); //navigate to admin dashboard
    };

    return (
        <>
        {/* <div> */}
            <div className='form-box2'>
            
            <h2>Profile</h2>
            {loading && <p>Loading...</p>}
            {error && <p style={{ color: 'red' }}>{error}</p>}
            {user && (
                <>
                <div className='form-box3'>
                <label>Name: {user.name}</label><br />
                <label>Email: {user.email}</label><br />
                <label>Role: {user.role}</label><br />
                {/* <label>Mobile: {user.mobile}</label><br />
                <label>Job: {user.job}</label><br />
                <label>CV: {user.cv}</label><br /> */}
                <br />
                <button onClick={handleEditProfile}>Edit Profile</button>
                <br />
                {user.role === 'admin' && (
                    <button onClick={handleAdminDashboard}>Admin Dashboard</button>
                )}
                </div> 
                </>
            )}
            {user && user.role === 'applicant' && (
                <>
                <h3>Applications List</h3>
                {applications.length > 0 ? (
                    // <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                    <div className='table-container'>
                    <table className='admin-dashboard' style={{ borderCollapse: 'collapse' }}>
                    <thead>
                        <tr>
                        <th>Job</th>
                        <th>Email</th>
                        <th>Mobile</th>
                        <th>CV</th>
                        <th>Status</th>
                        <th>Actions</th>
                        </tr>
                    </thead>
                    <tbody>
                        {applications.map((app) => (
                        <tr key={app.id}>
                            <td>{app.job}</td>
                            <td>{app.email}</td>
                            <td>{app.mobile}</td>
                            <td>{app.cv_path.split('\\').pop()}</td>
                            <td>{app.status}</td>
                            <td>
                                <button onClick={() => handleEditApplication(app.id)}>Edit</button>
                                <button onClick={() => handleDelete(app.id)}>Delete</button>
                            </td>
                        </tr>
                        ))}
                    </tbody>
                    </table>
                    </div>
                ) : (
                    <p>
                        No applications submitted.{' '}
                        <a href="/application" onClick={() => navigate('/application')}>
                            Submit an application
                        </a>
                    </p>
                )}
                <p>
                    {/* <strong>Note:</strong> You must upload a CV for each new application.{' '} */}
                    <a href="/application" onClick={() => navigate('/application')}>
                        Apply for another job
                    </a>
                </p>
                </>
            )}
        </div>
        </>
    );
}