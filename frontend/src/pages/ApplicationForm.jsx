export default function ApplicationForm() {
    return(
        <>
        <div>
        <form className="form-box">
            <h2>Application Form</h2>
            <p>
                <label htmlFor="name">Name:</label>
                <input type="text" name="name" /> 
            </p>

            <p>
                <label htmlFor="email">Email:</label>
                <input type="email" name="email" /> 
            </p>

            <p>
                <label htmlFor="mobile">Mobile no:</label>
                <input type="tel" name="mobile" />
            </p>

            <p>
                <label htmlFor="file">CV:</label>
                <input type="file" accept=".pdf" name="file" /> 
            </p>

            <p>
                <label htmlFor="jobs">Job Title:</label>
                <select id="job" name="job">
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
