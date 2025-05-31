import { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL;

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
  const isEditing = location.search.includes('edit');

  // fetch user profile to get registered email
  useEffect(() => {
    const fetchProfile = async () => {
      const token = localStorage.getItem('token');
      if (!token) {
        navigate('/login');
        return;
      }
      try {
        const response = await fetch(`${API_URL}/profile`, {
          headers: { Authorization: `Bearer ${token}` },
        });
        if (!response.ok) {
          throw new Error('Failed to fetch profile');
        }
        const data = await response.json();
        setEmail(data.email);
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
          const response = await fetch(`${API_URL}/applications?app_id=${appId}`, {
            headers: { Authorization: `Bearer ${token}` },
          });
          if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || `Failed to fetch application (Status: ${response.status})`);
          }
          const data = await response.json();
          console.log('Fetched application data:', data);
          const application = data.applications[0];
          if (application) {
            if (application.status !== 'Applied') {
              setError('Application cannot be edited, it is no longer in "Applied" status.');
              setTimeout(() => navigate('/profile'), 2000);
              return;
            }
            setName(application.name);
            setEmail(application.email);
            setMobile(application.mobile);
            setJob(application.job);
            setExistingCv(application.cv_path.split('\\').pop());
          } else {
              throw new Error('Application not found');
          }
        } catch (err) {
            console.error('Fetch application error:', err);
            setError(err.message || 'Error fetching application data. Ensure the application exists.');
            setTimeout(() => navigate('/profile'), 2000);
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

    // validation for new application-->all fields required
    if (!isEditing && (!name || !email || !mobile || job === 'none' || !cv)) {
      setError('Please fill all required fields, select a job, and upload a CV');
      return;
    }

    // validation for edit--> at least one field must be updated
    if (isEditing && !name && !mobile && job === 'none' && !cv) {
      setError('Please update at least one field or upload a new CV');
      return;
    }

    const formData = new FormData();
    if (name) formData.append('name', name);
    if (email) formData.append('email', email);
    if (mobile) formData.append('mobile', mobile);
    if (job !== 'none') formData.append('job', job);
    if (cv) formData.append('file', cv);

    console.log('FormData:', Object.fromEntries(formData));

    try {
      const params = new URLSearchParams(location.search);
      const appId = params.get('edit');
      const url = isEditing
        ? `${API_URL}/edit-applications/${appId}`
        : `${API_URL}/application-submit`;
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
        // navigate('/profile');
        navigate('/success', {
          state: { message: isEditing ? 'Application updated successfully!' : 'Application submitted successfully!' }
        });
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
      <div className='form-wrapper'>
        <form className="form-box" onSubmit={handleSubmit}>
          <h2>{isEditing ? 'Edit Application' : 'Application Form'}</h2>
          {error && <p style={{ color: 'red' }}>{error}</p>}

          <p>
            <label htmlFor="name">Name:</label>
            <input
              type="text"
              name="name"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required={!isEditing}
            />
          </p>

          <p>
            <label htmlFor="email">Email:</label>
            <input
              type="email"
              name="email"
              value={email}
              readOnly
              required={!isEditing}
            />
          </p>

          <p>
            <label htmlFor="mobile">Mobile no:</label>
            <input
              type="tel"
              name="mobile"
              value={mobile}
              onChange={(e) => setMobile(e.target.value)}
              required={!isEditing}
            />
          </p>

          <p>
            <label htmlFor="file">CV (PDF only):</label>
            {existingCv && isEditing && <span>Current: {existingCv}</span>}
            <input
              type="file"
              accept=".pdf"
              name="cv"
              onChange={(e) => setCv(e.target.files[0])}
              required={!isEditing}
            />
          </p>

          <p>
            <label htmlFor="job">Job Title:</label>
            <select
              id="job"
              name="job"
              value={job}
              onChange={(e) => setJob(e.target.value)}
              required={!isEditing}
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

          <button type="submit">{isEditing ? 'Update' : 'Submit'}</button>
        </form>
      </div>
    </>
  );
}