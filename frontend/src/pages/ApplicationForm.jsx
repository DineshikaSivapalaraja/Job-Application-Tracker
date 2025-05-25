import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

export default function ApplicationForm() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [mobile, setMobile] = useState('');
  const [job, setJob] = useState('none');
  const [cv, setCv] = useState(null);
  const [existingCv, setExistingCv] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();
  const location = useLocation();

  // fetch user profile to get registered email
  useEffect(() => {
    const fetchProfile = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
      try {
        const response = await fetch('http://127.0.0.1:8000/profile', {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) {
          throw new Error('Failed to fetch profile');
        }
        const data = await response.json();
        setEmail(data.email); // set registered email in application form
      } catch (err) {
        console.error('Fetch profile error:', err);
        setError('Failed to load profile data. Please try again.');
      }
    };
    fetchProfile();
  }, [navigate]);

  // fetch application data for edit
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
          // const response = await fetch(`http://127.0.0.1:8000/applications/${appId}`, {
          const response = await fetch(`http://127.0.0.1:8000/applications`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (!response.ok) {
            throw new Error(`Failed to fetch application (Status: ${response.status})`);
          }
          const data = await response.json();
          setName(data.name);
          setEmail(data.email);
          setMobile(data.mobile);
          setJob(data.job);
          setExistingCv(data.cv_path.split('\\').pop());
        } catch (err) {
          console.error('Fetch application error:', err);
          setError('Error fetching application data. Ensure the application exists.');
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

    if (!name || !email || !mobile || job === 'none' || (!cv && !existingCv)) {
      setError('Please fill all required fields, select a job, and upload a CV');
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
    if (cv) {
      formData.append('file', cv);
    }

    console.log('FormData:', Object.fromEntries(formData));

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

      console.log('Response status:', response.status, 'Response ok:', response.ok, 'Headers:', response.headers);

      if (response.ok) {
        navigate('/profile');
      } else {
        const data = await response.json();
        console.log('Error response:', data);
        setError(data.detail || `Submission failed (Status: ${response.status})`);
      }
    } catch (err) {
      console.error('Network error:', err);
      setError('Network error occurred. Please try again.');
    }
  };

  return (
    <>
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
            readOnly
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
          {existingCv && <span>Current: {existingCv}</span>}
          <input
            type="file"
            accept=".pdf"
            name="cv"
            onChange={(e) => setCv(e.target.files[0])}
            required={!existingCv}
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
    </>
  );
}
