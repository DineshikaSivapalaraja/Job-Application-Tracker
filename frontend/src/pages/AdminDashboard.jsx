import { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL;

export default function AdminDashboard() {
    const [applications, setApplications] = useState([]);
    const [status, setStatus] = useState('');

    useEffect(() => {
        const fetchData = async () => {
        const token = localStorage.getItem('token');
        if (!token) return;
        try {
            // const response = await fetch('http://localhost:8000/admin/applications', {
            // const response = await fetch(`http://127.0.0.1:8000/admin/applications`, {
            const response = await fetch(`${API_URL}/admin/applications`, {

            headers: { Authorization: `Bearer ${token}` },
            });
            const data = await response.json();
            setApplications(data.applications);
        } catch (err) {
            console.error('Error fetching applications:', err);
        }
        };
        fetchData();
    }, []);

    const handleStatusUpdate = async (appId) => {
        const token = localStorage.getItem('token');
        const response = await fetch(`${API_URL}/applications/${appId}`, {

        method: 'PUT',
        headers: { 
            'Content-Type': 'application/json',
            Authorization: `Bearer ${token}` 
        },
        body: JSON.stringify({ status }),
        });
        // setApplications(applications.map(app => 
        // app.id === appId ? { ...app, status } : app
        // ));
        // setStatus('');
        if (response.ok) {
            setApplications(
                applications.map((app) =>
                app.id === appId ? { ...app, status } : app
                )
            );
            setStatus('');
            } else {
            const data = await response.json();
            console.error('Failed to update status:', data.detail);
    }
    };

    const handleDownloadCV = async (appId) => {
    const token = localStorage.getItem('token');
    try {
        const response = await fetch(`${API_URL}/applications/${appId}/cv`, {
            headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) {
            throw new Error('Failed to download CV');
        }
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `cv_${appId}.pdf`; 
        document.body.appendChild(a);
        a.click();
        a.remove();
        window.URL.revokeObjectURL(url);
        } catch (err) {
        console.error('Error downloading CV:', err);
        }
    };

    return (
        <>
        <div className='form-box2'>
        <h2>Applicants List</h2>
        <br></br>

        <Link to="/profile" className="link">Go to Profile</Link>
        <br></br>
        <Link to="/logout" className="link">Log Out</Link>

        <div className='table-container'>
        <table className='admin-dashboard'>
            <tr>
            <th>Name</th>
            <th>Email</th>
            <th>Mobile</th>
            <th>Job</th>
            <th>CV</th>
            <th>Status</th>
            </tr>
            {applications.map((app) => (
            <tr key={app.id}>
                <td>{app.name}</td>
                <td>{app.email}</td>
                <td>{app.mobile}</td>
                <td>{app.job}</td>
                <td>
                {/* <a href={`http://127.0.0.1:8000/applications/${app.id}/cv`} download>
                    Download
                </a> */}
                    <button onClick={() => handleDownloadCV(app.id)}>Download</button>
                </td>
                <td>
                {app.status}
                <select value={status} onChange={(e) => setStatus(e.target.value)}>
                    <option value="">Update Status</option>
                    <option value="Applied">Applied</option>
                    <option value="Viewed">Viewed</option>
                    <option value="Resume Downloaded">Resume Downloaded</option>
                    <option value="Interview Scheduled">Interview Scheduled</option>
                    <option value="Rejected">Rejected</option>
                    <option value="Offered">Offered</option>
                </select>
                <button onClick={() => handleStatusUpdate(app.id)}>Update</button>
                </td>
            </tr>
            ))}
        </table>
        </div>
        </div>
        </>
    );
}