import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function ApplicationForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [mobile, setMobile] = useState('');
  const [job, setJob] = useState('none');
  const [cv, setCv] = useState(null);
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const appId = params.get('edit');
    if (appId) {
      const fetchApplication = async () => {
        const token = localStorage.getItem('token');
        if (!token) {
          navigate('/login');
          return;
        }
        try {
          const response = await fetch(`http://127.0.0.1:8000/applications`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          const data = await response.json();
          const app = data.applications.find((a) => a.id === parseInt(appId));
          if (app) {
            setName(app.name);
            setEmail(app.email);
            setMobile(app.mobile);
            setJob(app.job);
          } else {
            setError('Application not found');
          }
        } catch (err) {
          setError('Error fetching application data');
        }
      };
      fetchApplication();
    }
  }, [location, navigate]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const token = localStorage.getItem('token');
    if (!token) {
      setError('Please log in first');
      navigate('/login');
      return;
    }

    if (!name || !email || !mobile || job === 'none') {
      setError('Please fill all required fields and select a job');
      return;
    }

    const params = new URLSearchParams(location.search);
    const appId = params.get('edit');
    const isEditing = !!appId;

    const formData = new FormData();
    formData.append('name', name);
    formData.append('email', email);
    formData.append('mobile', mobile);
    formData.append('job', job);
    if (cv) formData.append('cv', cv);

    try {
      const url = isEditing
        ? `http://127.0.0.1:8000/edit-applications/${appId}`
        : 'http://127.0.0.1:8000/application-submit';
      const method = isEditing ? 'PUT' : 'POST';

      const response = await fetch(url, {
        method,
        headers: {
          Authorization: `Bearer ${token}`
        },
        body: formData,
      });

      if (response.ok) {
        navigate('/profile');
      } else {
        const data = await response.json();
        setError(data.detail || `Submission failed (Status: ${response.status})`);
      }
    } catch (err) {
      setError('Network error occurred. Please try again.');
      console.error('Fetch error:', err);
    }
  };

  return (
    <div>
      <form className="form-box" onSubmit={handleSubmit}>
        <h2>{location.search.includes('edit') ? 'Edit Application' : 'Application Form'}</h2>
        {error && <p style={{ color: 'red' }}>{error}</p>}

        <p>
          <label htmlFor="name">Name:</label>
          <input
            type="text"
            name="name"
            value={name}
            onChange={(e) => setName(e.target.value)}
            required
          />
        </p>

        <p>
          <label htmlFor="email">Email:</label>
          <input
            type="email"
            name="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
          />
        </p>

        <p>
          <label htmlFor="mobile">Mobile no:</label>
          <input
            type="tel"
            name="mobile"
            value={mobile}
            onChange={(e) => setMobile(e.target.value)}
            required
          />
        </p>

        <p>
          <label htmlFor="file">CV (PDF only):</label>
          <input
            type="file"
            accept=".pdf"
            name="cv"
            onChange={(e) => setCv(e.target.files[0])}
            required={!location.search.includes('edit')} // Not required when editing
          />
        </p>

        <p>
          <label htmlFor="job">Job Title:</label>
          <select
            id="job"
            name="job"
            value={job}
            onChange={(e) => setJob(e.target.value)}
            required
          >
            <option value="none" disabled>
              Select a job
            </option>
            <option value="Software Engineer Intern">Software Engineer Intern</option>
            <option value="Associate/Junior Software Engineer">Associate/Junior Software Engineer</option>
            <option value="Software Engineer">Software Engineer</option>
            <option value="AI/ML Intern">AI/ML Intern</option>
            <option value="Associate/Junior AI/ML">Associate/Junior AI/ML</option>
            <option value="ML Engineer">ML Engineer</option>
            <option value="AI Engineer">AI Engineer</option>
            <option value="Data Scientist">Data Scientist</option>
            <option value="DevOps Engineer">DevOps Engineer</option>
            <option value="UI-UX Engineer">UI-UX Engineer</option>
          </select>
        </p>

        <button type="submit">{location.search.includes('edit') ? 'Update' : 'Submit'}</button>
      </form>
    </div>
  );
}
