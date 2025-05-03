import { Link } from 'react-router-dom';

export default function LogIn() {
    return(
        <>
        <div>
        <form className="form-box">
            <h2> Log In </h2>
            <p>
                <label htmlFor="email">Email:</label>
                <input type="email" name="email" /> 
            </p>
            
            <p>
                <label htmlFor="password">Password:</label>
                <input type="password" name="password"/> 
            </p>
            
            <button type="submit">Log In</button>
            
            <p className='btn'>Don't have an account? <br></br> 
                <Link to="/signup" className='link'>Register Now</Link>
            </p> 
        </form>
        </div>
        </>
    );
}