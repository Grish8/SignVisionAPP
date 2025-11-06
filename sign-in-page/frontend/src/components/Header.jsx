import React from 'react';
import { Link } from 'react-router-dom';
import './Header.css';

function Header() {
  const handleLinkClick = (path) => {
    console.log('Header link clicked:', path);
  };

  return (
    <header className="header">
      <div className="header-container">
        {/* Logo and Brand */}
        <div className="header-brand">
          <Link to="/" className="brand-link">
            <div className="logo">
              <span className="logo-icon">👋</span>
            </div>
            <div className="brand-text">
              <h1 className="brand-name">SignVision</h1>
              <p className="brand-tagline">AR Sign Language Interpreter</p>
            </div>
          </Link>
        </div>

        {/* Navigation */}
        <nav className="header-nav">
          <ul className="nav-list">
            <li className="nav-item">
              <Link to="/" className="nav-link" onClick={() => handleLinkClick('/')}>Home</Link>
            </li>
            <li className="nav-item">
              <Link to="/login" className="nav-link" onClick={() => handleLinkClick('/login')}>Sign In</Link>
            </li>
            <li className="nav-item">
              <Link to="/register" className="nav-link register-btn" onClick={() => handleLinkClick('/register')}>Get Started</Link>
            </li>
          </ul>
        </nav>
      </div>
    </header>
  );
}

export default Header;