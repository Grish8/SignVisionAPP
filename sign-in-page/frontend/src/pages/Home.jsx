import React from 'react';
import { Link } from 'react-router-dom';
import './Home.css';

function Home() {
  return (
    <div className="home-container">
      {/* Hero Section */}
      <div className="hero-section">
        <div className="hero-content">
          <h1 className="main-title">
            The Augmented Reality Sign Language Interpreter
          </h1>
          <p className="subtitle">
            Bridge the communication gap with real-time AR sign language interpretation. 
            Experience seamless communication through cutting-edge technology.
          </p>
          
          <div className="cta-buttons">
            <Link to="/login" className="cta-button primary">
              Sign In
            </Link>
            <Link to="/register" className="cta-button secondary">
              Create Account
            </Link>
          </div>
        </div>
        
        <div className="hero-visual">
          <div className="ar-preview">
            <div className="hand-gesture-animation">
              <div className="hand-container">
                <div className="hand"></div>
                <div className="finger finger-1"></div>
                <div className="finger finger-2"></div>
                <div className="finger finger-3"></div>
                <div className="finger finger-4"></div>
                <div className="finger finger-5"></div>
              </div>
              <div className="ar-effects">
                <div className="pulse-ring ring-1"></div>
                <div className="pulse-ring ring-2"></div>
                <div className="pulse-ring ring-3"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Section */}
      <div className="stats-section">
        <div className="stats-container">
          <div className="stat-item">
            <div className="stat-number">10K+</div>
            <div className="stat-label">Users Worldwide</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">95%</div>
            <div className="stat-label">Accuracy Rate</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">50+</div>
            <div className="stat-label">Languages Supported</div>
          </div>
          <div className="stat-item">
            <div className="stat-number">24/7</div>
            <div className="stat-label">Available</div>
          </div>
        </div>
      </div>

      {/* Features Section */}
      <div className="features-section">
        <h2>Key Features</h2>
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">👋</div>
            <h3>Real-time Interpretation</h3>
            <p>Instant sign language to text/speech conversion using augmented reality</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">📱</div>
            <h3>Mobile Friendly</h3>
            <p>Accessible on all devices with camera capabilities</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">🌍</div>
            <h3>Multiple Languages</h3>
            <p>Support for various sign language systems worldwide</p>
          </div>
        </div>
      </div>

      {/* How It Works Section */}
      <div className="how-it-works-section">
        <div className="section-header">
          <h2>How It Works</h2>
          <p>Three simple steps to bridge communication gaps</p>
        </div>
        <div className="steps-container">
          <div className="step-card">
            <div className="step-number">01</div>
            <div className="step-icon">🎥</div>
            <h3>Capture</h3>
            <p>Use your device's camera to capture sign language gestures in real-time</p>
          </div>
          <div className="step-card">
            <div className="step-number">02</div>
            <div className="step-icon">🤖</div>
            <h3>Process</h3>
            <p>Our AI analyzes and interprets the gestures with advanced computer vision</p>
          </div>
          <div className="step-card">
            <div className="step-number">03</div>
            <div className="step-icon">💬</div>
            <h3>Communicate</h3>
            <p>Get instant text or speech translation for seamless conversation</p>
          </div>
        </div>
      </div>

      {/* Testimonials Section */}
      <div className="testimonials-section">
        <div className="section-header">
          <h2>What Our Users Say</h2>
          <p>Join thousands of satisfied users worldwide</p>
        </div>
        <div className="testimonials-grid">
          <div className="testimonial-card">
            <div className="testimonial-content">
              <p>"This app has revolutionized how I communicate with my hearing-impaired students. The AR features are incredible!"</p>
            </div>
            <div className="testimonial-author">
              <div className="author-avatar">👩‍🏫</div>
              <div className="author-info">
                <h4>Sarah Johnson</h4>
                <p>Special Education Teacher</p>
              </div>
            </div>
          </div>
          <div className="testimonial-card">
            <div className="testimonial-content">
              <p>"As someone who uses sign language daily, this interpreter has made conversations with hearing friends so much easier."</p>
            </div>
            <div className="testimonial-author">
              <div className="author-avatar">👨‍💼</div>
              <div className="author-info">
                <h4>Michael Chen</h4>
                <p>Software Developer</p>
              </div>
            </div>
          </div>
          <div className="testimonial-card">
            <div className="testimonial-content">
              <p>"The accuracy and speed of translation are impressive. It feels like having a personal interpreter always available."</p>
            </div>
            <div className="testimonial-author">
              <div className="author-avatar">👵</div>
              <div className="author-info">
                <h4>Maria Rodriguez</h4>
                <p>Grandparent</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Technology Section */}
      <div className="technology-section">
        <div className="tech-content">
          <div className="tech-info">
            <h2>Powered by Advanced AI</h2>
            <p>Our platform leverages cutting-edge technology to deliver accurate and reliable sign language interpretation</p>
            <div className="tech-features">
              <div className="tech-feature">
                <span className="tech-icon">🧠</span>
                <span>Machine Learning Algorithms</span>
              </div>
              <div className="tech-feature">
                <span className="tech-icon">👁️</span>
                <span>Computer Vision</span>
              </div>
              <div className="tech-feature">
                <span className="tech-icon">🔊</span>
                <span>Real-time Audio Processing</span>
              </div>
              <div className="tech-feature">
                <span className="tech-icon">📊</span>
                <span>Continuous Improvement</span>
              </div>
            </div>
          </div>
          <div className="tech-visual">
            <div className="ai-animation">
              <div className="neural-network">
                <div className="node node-1"></div>
                <div className="node node-2"></div>
                <div className="node node-3"></div>
                <div className="node node-4"></div>
                <div className="node node-5"></div>
                <div className="connection"></div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* CTA Section */}
      <div className="cta-section">
        <div className="cta-content">
          <h2>Ready to Start Communicating?</h2>
          <p>Join our community today and experience the future of sign language interpretation</p>
          <div className="cta-buttons">
            <Link to="/register" className="cta-button primary large">
              Get Started Free
            </Link>
            <Link to="/demo" className="cta-button secondary large">
              Watch Demo
            </Link>
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="home-footer">
        <div className="footer-content">
          <div className="footer-section">
            <h3>Sign Language Interpreter</h3>
            <p>Bridging communication gaps through technology</p>
          </div>
          <div className="footer-section">
            <h4>Quick Links</h4>
            <ul>
              <li><Link to="/about">About Us</Link></li>
              <li><Link to="/features">Features</Link></li>
              <li><Link to="/pricing">Pricing</Link></li>
              <li><Link to="/contact">Contact</Link></li>
            </ul>
          </div>
          <div className="footer-section">
            <h4>Legal</h4>
            <ul>
              <li><Link to="/privacy">Privacy Policy</Link></li>
              <li><Link to="/terms">Terms of Service</Link></li>
              <li><Link to="/cookies">Cookie Policy</Link></li>
            </ul>
          </div>
        </div>
        <div className="footer-bottom">
          <p>&copy; 2025. All rights reserved by. Enos Grisham Odhiambo.</p>
        </div>
      </footer>
    </div>
  );
}

export default Home;