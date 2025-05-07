// import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css'
import SignUp from './pages/Signup.jsx'
import LogIn from './pages/LogIn.jsx'
//import ApplicationForm from './pages/ApplicationForm.jsx'

function App() {

  return (
    <>
    <div>
      <Router>
        <Routes>
          <Route path="/login" element={<LogIn />} />
          <Route path="/signup" element={<SignUp />} />
          {/* <Route path="/application" element={<ApplicationForm />} /> */}
        </Routes>
      </Router>
      {/* <ApplicationForm /> */}
    </div>
    </>
  )
}

export default App
