import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import axios from 'axios';
import './Login.css';

function Login() {
  const [formData, setFormData] = useState({
    email: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
    // Clear error when user starts typing
    if (error) setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    setSuccess(false);

    // Basic validation
    if (!formData.email || !formData.password) {
      setError('Please fill in all fields');
      setLoading(false);
      return;
    }

    if (!/\S+@\S+\.\S+/.test(formData.email)) {
      setError('Please enter a valid email address');
      setLoading(false);
      return;
    }

    try {
      // REAL API call to your backend
      const response = await axios.post('http://localhost:3001/auth/login', {
        email: formData.email,
        password: formData.password
      }, {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 10000
      });

      if (response.status === 200) {
        setSuccess(true);
        
        // Store user session with real data from backend
        const { token, user } = response.data;
        
        localStorage.setItem('authToken', token);
        localStorage.setItem('userEmail', user.email);
        localStorage.setItem('userId', user.id);
        localStorage.setItem('username', user.username);
        localStorage.setItem('isLoggedIn', 'true');
        
        console.log('✅ Login successful for user:', user.email);
        
        // Show success message for 2 seconds before redirecting
        setTimeout(() => {
          // Redirect to the AR application
          window.location.href = 'http://localhost:5000';
        }, 2000);
        
      } else {
        setError('Login failed. Please try again.');
      }
    } catch (err) {
      console.error('Login error:', err);
      
      if (err.response) {
        // Server responded with error status
        switch (err.response.status) {
          case 400:
            setError('Invalid request. Please check your input.');
            break;
          case 401:
            setError('Invalid email or password. Please try again.');
            break;
          case 500:
            setError('Server error. Please try again later.');
            break;
          default:
            setError(err.response.data?.message || 'Login failed. Please try again.');
        }
      } else if (err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        setError('Cannot connect to server. Make sure your backend is running on port 3001.');
      } else if (err.code === 'ECONNABORTED') {
        setError('Request timeout. Please try again.');
      } else {
        setError('Login failed. Please check your connection and try again.');
      }
    } finally {
      setLoading(false);
    }
  };

  // Demo credentials helper
  const fillDemoCredentials = () => {
    setFormData({
      email: 'demo@example.com',
      password: 'password123'
    });
    setError('');
  };

  return (
    <div className="login-page">
      <div className="login-container">
        <div className="login-header">
          <h2>Welcome Back</h2>
          <p>Sign in to access your AR Sign Language Interpreter</p>
        </div>

        {success && (
          <div className="success-message">
            ✅ Login successful! Redirecting to AR application...
          </div>
        )}

        {error && (
          <div className="error-message">
            ⚠️ {error}
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form">
          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input
              type="email"
              id="email"
              name="email"
              value={formData.email}
              onChange={handleChange}
              placeholder="Enter your email"
              required
              disabled={loading || success}
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
              disabled={loading || success}
            />
          </div>

          <button 
            type="submit" 
            className={`login-button ${loading ? 'loading' : ''} ${success ? 'success' : ''}`}
            disabled={loading || success}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Signing In...
              </>
            ) : success ? (
              '✅ Success!'
            ) : (
              'Sign In'
            )}
          </button>
        </form>

        <div className="demo-credentials">
          <button 
            type="button" 
            className="demo-button"
            onClick={fillDemoCredentials}
            disabled={loading || success}
          >
            Try Demo Credentials
          </button>
          <p className="demo-hint">Email: demo@example.com | Password: password123</p>
        </div>

        <div className="login-footer">
          <p>
            Don't have an account?{' '}
            <Link to="/register" className="register-link">
              Create one here
            </Link>
          </p>
          <p>
            <Link to="/" className="back-link">
              ← Back to Home
            </Link>
          </p>
        </div>
      </div>
    </div>
  );
}

export default Login;