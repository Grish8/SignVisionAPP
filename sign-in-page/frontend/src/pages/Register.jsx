import React, { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import axios from 'axios'
import './Register.css'

const Register = () => {
  const [values, setValues] = useState({
    username: '',
    email: '',
    password: ''
  })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)
  const [passwordStrength, setPasswordStrength] = useState('')
  const navigate = useNavigate()

  const checkPasswordStrength = (password) => {
    if (password.length === 0) return ''
    if (password.length < 6) return 'weak'
    if (password.length < 8) return 'medium'
    if (/[A-Z]/.test(password) && /[0-9]/.test(password) && /[!@#$%^&*]/.test(password)) {
      return 'strong'
    }
    return 'medium'
  }

  const handleChanges = (e) => {
    const newValues = {...values, [e.target.name]: e.target.value}
    setValues(newValues)
    
    if (error) setError('')
    
    // Check password strength
    if (e.target.name === 'password') {
      const strength = checkPasswordStrength(e.target.value)
      setPasswordStrength(strength)
    }
  }

  const getPasswordStrengthText = () => {
    switch (passwordStrength) {
      case 'weak': return 'Password strength: Weak'
      case 'medium': return 'Password strength: Medium'
      case 'strong': return 'Password strength: Strong'
      default: return ''
    }
  }

  const getPasswordStrengthColor = () => {
    switch (passwordStrength) {
      case 'weak': return '#ff4444'
      case 'medium': return '#ffaa00'
      case 'strong': return '#00aa00'
      default: return '#666'
    }
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    setError('')
    setMessage('')
    setLoading(true)

    // Validation
    if (!values.username || !values.email || !values.password) {
      setError('Please fill in all fields')
      setLoading(false)
      return
    }

    if (!/\S+@\S+\.\S+/.test(values.email)) {
      setError('Please enter a valid email address')
      setLoading(false)
      return
    }

    if (values.password.length < 6) {
      setError('Password must be at least 6 characters long')
      setLoading(false)
      return
    }

    if (values.username.length < 3 || values.username.length > 30) {
      setError('Username must be between 3 and 30 characters')
      setLoading(false)
      return
    }

    if (!/^[a-zA-Z0-9_]+$/.test(values.username)) {
      setError('Username can only contain letters, numbers, and underscores')
      setLoading(false)
      return
    }

    try {
      const response = await axios.post('http://localhost:3001/auth/register', values, {
        headers: {
          'Content-Type': 'application/json'
        },
        timeout: 10000 // 10 second timeout
      })
      
      if(response.status === 201){
        setMessage(response.data.message || 'Registration successful! Redirecting to login...')
        setTimeout(() => navigate('/login'), 2000)
      }
    } catch(err) {
      console.log('Registration error:', err)
      if (err.response && err.response.data && err.response.data.message) {
        setError(err.response.data.message)
      } else if (err.code === 'ECONNREFUSED' || err.message.includes('Network Error')) {
        setError('Cannot connect to server. Make sure your backend is running on port 3001.')
      } else if (err.code === 'ECONNABORTED') {
        setError('Request timeout. Please try again.')
      } else {
        setError('Registration failed. Please try again.')
      }
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="register-page">
      <div className="register-container">
        <div className="register-header">
          <h2>Create Your Account</h2>
          <p>Join our AR Sign Language Interpreter community</p>
        </div>

        {message && <div className="success-message">✅ {message}</div>}
        {error && <div className="error-message">⚠️ {error}</div>}

        <form onSubmit={handleSubmit} className="register-form">
          <div className="form-group">
            <label htmlFor="username">Username</label>
            <input 
              type="text" 
              id="username"
              placeholder="Enter your username (3-30 characters)" 
              className="form-input"
              name="username" 
              value={values.username}
              onChange={handleChanges}
              disabled={loading}
              required
              minLength="3"
              maxLength="30"
              pattern="[a-zA-Z0-9_]+"
              title="Username can only contain letters, numbers, and underscores"
            />
          </div>

          <div className="form-group">
            <label htmlFor="email">Email Address</label>
            <input 
              type="email" 
              id="email"
              placeholder="Enter your email" 
              className="form-input"
              name="email" 
              value={values.email}
              onChange={handleChanges}
              disabled={loading}
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input 
              type="password" 
              id="password"
              placeholder="Enter your password (min. 6 characters)" 
              className="form-input"
              name="password" 
              value={values.password}
              onChange={handleChanges}
              disabled={loading}
              required
              minLength="6"
            />
            {passwordStrength && (
              <div 
                className="password-strength" 
                style={{ color: getPasswordStrengthColor() }}
              >
                {getPasswordStrengthText()}
              </div>
            )}
          </div>

          <button 
            type="submit" 
            className={`register-button ${loading ? 'loading' : ''}`}
            disabled={loading}
          >
            {loading ? (
              <>
                <span className="spinner"></span>
                Creating Account...
              </>
            ) : (
              'Create Account'
            )}
          </button>
        </form>

        <div className="register-footer">
          <p>Already have an account? <Link to="/login" className="login-link">Login here</Link></p>
          <p><Link to="/" className="back-link">← Back to Home</Link></p>
        </div>
      </div>
    </div>
  )
}

export default Register