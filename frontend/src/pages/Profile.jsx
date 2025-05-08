export default function Profile() {
    return(
        <>
        <div>
            {/* <p>Hello</p> */}
            <h2>Profile</h2>
            <label>Name: </label>
            <label>Email: </label>
            <label>Mobile: </label>
            <label>CV: </label>
            <label>Job: </label>

            <h4>Applications List</h4>
            <table>
                <tr>
                    <th>Job</th>
                    <th>CV</th>
                    <th>Status</th> 
                     {/* <!--reviewed/downloaded/rejected/shortlisted--> */}
                    <th>Action</th> 
                    {/* <!-- applicant can delete/edit the application--> */}
                </tr>
                <tr>

                </tr>
            </table>
        </div>
        </>

    );
}