import { useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

export default function Logout() {
  const navigate = useNavigate();

  useEffect(() => {
    const logout = async () => {
      const token = localStorage.getItem('token');
      if (token) {
        await fetch(`http://127.0.0.1:8000/logout`, {
          method: 'POST',
          headers: { Authorization: `Bearer ${token}` },
        });
        localStorage.removeItem('token');
      }
      navigate('/login');
    };
    logout();
  }, [navigate]);

  return null; 
}