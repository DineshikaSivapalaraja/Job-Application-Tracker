import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const API_URL = import.meta.env.VITE_API_URL;

export default function Logout() {
  const navigate = useNavigate();

  useEffect(() => {
    const logout = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        await fetch(`${API_URL}/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
        localStorage.removeItem('token');
      }
      navigate('/login');
    };
    logout();
  }, [navigate]);

  // return null; 
  return (
    <h2>Successfully Logout!</h2>
  );
}