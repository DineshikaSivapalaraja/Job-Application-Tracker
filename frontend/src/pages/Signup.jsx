import { useNavigate, Link } from 'react-router-dom';
import { useState } from 'react';

export default function SignUp() {
    const [name, setName] = useState('');
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [cpassword, setCpassword] = useState('');
    const [error, setError] = useState('');
    const navigate = useNavigate();

    const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');
    if (password !== cpassword) {
        setError('Passwords do not match');
        return;
        }
        try {
        const response = await fetch('http://localhost:8000/signup', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ name, email, password, cpassword }),
        });
        const data = await response.json();
        if (response.ok) {
            navigate('/login');
        } else {
            setError(data.detail || 'Registration failed');
        }
        } catch (err) {
        setError('An error occurred');
        }
    };

    return(
        <>
        <div>
        <form className="form-box" onSubmit={handleSubmit}>
            <h2>Register</h2>
            {error && <p style={{color: 'red'}}>{error}</p>}
            <p>
                <label htmlFor="name"> Full name:</label>
                <input type="text" name="name" value={name} onChange={(e) => setName(e.target.value)}/> 
            </p>
            
            <p>
                <label htmlFor="email">Email:</label>
                <input type="email" name="email" value={email} onChange={(e) => setEmail(e.target.value)}/> 
            </p>

            <p>
                <label htmlFor="password">Password:</label>
                <input type="password" name="password" value={password} onChange={(e) => setPassword(e.target.value)} /> 
            </p>

            <p>
                <label htmlFor="cpassword">Confirm Password:</label>
                <input type="password" name="cpassword" value={cpassword} onChange={(e) => setCpassword(e.target.value)}/> 
            </p>

            <button type="submit">Register</button>
            {/* <button type="submit"><Link to="/application" className='link1'>Register</Link></button> */}

            {/* <p>Already have an account?</p>
            <a href="LogIn.jsx">LogIn</a> */}

            <p className='btn'>Already have an account?<br></br>
                <Link to="/login" className='link'>Log in</Link>
            </p>
    </form>
    </div>
    </>
    );
}