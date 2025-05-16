// import { useState } from 'react'
import { BrowserRouter as Router, Routes, Route } from 'react-router-dom';
import './App.css'
import SignUp from './pages/Signup.jsx'
import LogIn from './pages/LogIn.jsx'

function App() {

  return (
    <>
    <div>
      <Router>
        <Routes>
          <Route path="/login" element={<LogIn />} />
          <Route path="/signup" element={<SignUp />} />
        </Routes>
      </Router>
    </div>
    </>
  )
}

export default App;