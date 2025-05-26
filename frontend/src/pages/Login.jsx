import { useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';

export default function LogIn() {
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    try {
        const response = await fetch(`http://127.0.0.1:8000/login`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ email, password }),
        });
        const data = await response.json();
        if (response.ok) {
            localStorage.setItem('token', data.access_token);
            navigate('/profile');
        } else {
            setError(data.detail || 'Login failed');
        }
        } catch (err) {
        setError('An error occurred');
        }
    };

    return(
        <>
        <div className='form-wrapper'>
        <form className="form-box" onSubmit={handleSubmit}>
            <h2> Log In </h2>
            {error && <p style={{ color: 'red' }}>{error}</p>}
            <p>
                <label htmlFor="email">Email:</label>
                <input type="email" name="email" value={email} onChange={(e) => setEmail(e.target.value) } /> 
            </p>
            
            <p>
                <label htmlFor="password">Password:</label>
                <input type="password" name="password" value={password} onChange={(e) => setPassword(e.target.value)} /> 
            </p>
            
            <button type="submit">Log In</button>
            {/* <button type="submit"><Link to="/application" className='link1'>Log In</Link></button> */}

            <p className='btn'>Don't have an account? <br></br> 
                <Link to="/signup" className='link'>Register Now</Link>
            </p> 
        </form>
        </div>
        </>
    );
}