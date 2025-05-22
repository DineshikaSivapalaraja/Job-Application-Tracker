// import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css'
import SignUp from './pages/Signup.jsx';
import LogIn from './pages/Login.jsx';
import ApplicationForm from './pages/ApplicationForm.jsx';
import Success from './pages/Success.jsx';
import Profile from './pages/Profile.jsx';
import AdminDashboard from './pages/AdminDashboard.jsx';
import Logout from './pages/Logout.jsx';
import EditProfile from './pages/EditProfile.jsx';

function App() {

  return (
    <>
    <div>
      <Router>
        <Routes>
          <Route path="/login" element={<LogIn />} />
          <Route path="/signup" element={<SignUp />} />
          <Route path="/application" element={<ApplicationForm />} />
          <Route path="/success" element={<Success />} />
          <Route path="/profile" element={<Profile />} />
          <Route path='/edit-profile' element={<EditProfile/>} />
          <Route path="/admin" element={<AdminDashboard />} />
          <Route path="/logout" element={<Logout />} />
        </Routes>
      </Router>
    </div>
    </>
  )
}

export default App;