import { Link } from 'react-router-dom';

export default function SignUp() {
    return(
        <>
        <div>
        <form className="form-box">
            <h2>Register</h2>
            <p>
                <label htmlFor="name"> Full name:</label>
                <input type="text" name="name" /> 
            </p>
            
            <p>
                <label htmlFor="email">Email:</label>
                <input type="email" name="email" /> 
            </p>

            <p>
                <label htmlFor="password">Password:</label>
                <input type="password" name="password" /> 
            </p>

            <p>
                <label htmlFor="cpassword">Confirm Password:</label>
                <input type="password" name="cpassword" /> 
            </p>

            <button type="submit">Register</button>

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