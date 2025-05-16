import { useState } from 'react';
import { useNavigate } from 'react-router-dom';

export default function ApplicationForm() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [mobile, setMobile] = useState('');
    const [job, setJob] = useState('none');
    const [cv, setCv] = useState(null);
    const [error, setError] = useState('');
    const navigate = useNavigate();
    
    const handleSubmit = async (e) => {
        e.preventDefault();
        setError('');
        const formData = new FormData();
        formData.append('name', name);
        formData.append('email', email);
        formData.append('mobile', mobile);
        formData.append('job', job);
        if (cv) formData.append('cv', cv);
    
        try {
        const token = localStorage.getItem('token');
        const response = await fetch('http://localhost:8000/application-submit', {
            method: 'POST',
            headers: { Authorization: `Bearer ${token}` },
            body: formData,
        });
        if (response.ok) {
            navigate('/success');
        } else {
            const data = await response.json();
            setError(data.detail || 'Submission failed');
        }
        } catch (err) {
        setError('An error occurred');
        }
    };
    return(
        <>
        <div>
        <form className="form-box" onSubmit={handleSubmit}>
            <h2>Application Form</h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}

            <p>
                <label htmlFor="name">Name:</label>
                <input type="text" name="name"  value={name} onChange={(e) => setName(e.target.value)} /> 
            </p>

            <p>
                <label htmlFor="email">Email:</label>
                <input type="email" name="email"  value={email} onChange={(e) => setEmail(e.target.value)} /> 
            </p>

            <p>
                <label htmlFor="mobile">Mobile no:</label>
                <input type="tel" name="mobile"  value={mobile} onChange={(e) => setMobile(e.target.value)} />
            </p>

            <p>
                <label htmlFor="file">CV:</label>
                <input type="file" accept=".pdf" name="file" onChange={(e) => setCv(e.target.files[0])}/> 
            </p>

            <p>
                <label htmlFor="jobs">Job Title:</label>
                <select id="job" name="job"  value={job} onChange={(e) => setJob(e.target.value)}>
                    <option value="se-intern">Software Engineer Intern</option>
                    <option value="associate-se">Associate/Junior Software Engineer</option>
                    <option value="se">Software Engineer</option>
                    <option value="ai/ml-intern">AI/ML Intern</option>
                    <option value="associate-ai/ml">Associate/Junior AI/ML</option>
                    <option value="ml">ML Engineer</option>
                    <option value="ai">AI Engineer</option>
                    <option value="ds">Data Scientist</option>
                    <option value="devops">DevOps Engineer</option>
                    <option value="ui-ux">UI-UX Engineer</option>
                    <option value="none" selected>None</option>
                </select>
                {/* <input name="job" />  */}
            </p>
            
            <button type="submit">Submit</button>        
        </form>
        </div>
        </>
    );
}
