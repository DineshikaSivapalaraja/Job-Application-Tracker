import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Profile() {
    const [user, setUser] = useState(null);
    const [applications, setApplications] = useState([]);
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
        const userData = await userResponse.json();
        setUser(userData);

        const appResponse = await fetch(`http://127.0.0.1:8000/applications`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        const appData = await appResponse.json();
        setApplications(appData.applications);
        } catch (err) {
            console.error('Error fetching data:', err);
        }
    };
    fetchData();
    }, [navigate]);

    const handleDelete = async (appId) => {
    const token = localStorage.getItem('token');
    await fetch(`http://127.0.0.1:8000/applications/${appId}`, {
        method: 'DELETE',
        headers: { Authorization: `Bearer ${token}` },
    });
        setApplications(applications.filter(app => app.id !== appId));
    };

    const handleEdit = (appId) => {
        navigate(`/application?edit=${appId}`);
    };

    return(
        <>
        <div>
            <h2>Profile</h2>
            {/* {/* {/* <label>Name: </label>
            <label>Email: </label>
            <label>Mobile: </label>
            <label>CV: </label>
            <label>Job: </label> */}
            {user && (
            <>
            <label>Name: {user.name}</label><br />
            <label>Email: {user.email}</label><br />
            <label>Mobile: {user.mobile}</label><br />
            <label>Job: {user.job}</label><br />
            <label>CV: {user.cv}</label><br />
            </>
        )}

            <h4>Applications List</h4>
            <table>
                <tr>
                    <th>Job</th>
                    <th>CV</th>
                    <th>Status</th> 
                     {/* <!--reviewed/downloaded/rejected/shortlisted--> */}
                    <th>Action</th> 
                    {/* <!-- applicant can delete/edit the application--> */}
                </tr>
                {applications.map((app) => (
                <tr key={app.id}>
                    <td>{app.job}</td>
                    <td>{app.cv_path.split('\\').pop()}</td>
                    <td>{app.status}</td>
                    <td>
                    <button onClick={() => handleEdit(app.id)}>Edit</button>
                    <button onClick={() => handleDelete(app.id)}>Delete</button>
                    </td>
                </tr>
                ))} 
            </table>
        </div>
        </>
    );
}