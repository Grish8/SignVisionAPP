# SignVision AR Sign Language Interpreter

A comprehensive AR-powered sign language interpretation system with React authentication frontend, Node.js backend, and Flask AI/AR application.

## ✅ **UNIFIED APPLICATION - SINGLE COMMAND SETUP**

### 🚀 **One Command to Rule Them All**
```bash
npm run dev
```

**This single command simultaneously:**
- 🎆 **Starts all 3 services** (React, Node.js, Flask)
- 🌐 **Opens browser automatically** to http://localhost:5173
- 🔐 **Shows login page first** - the correct entry point
- ✨ **Handles the complete flow** from login to AR application

### 🔄 **Seamless Application Flow**
```
User Access → React Login (5173) → Authentication → Flask AR App (5000)
             ↓                    ↓
        Modern UI          Node.js API (3001)
                              ↓
                        MySQL Database
```

### ⚡ **Prerequisites**
- **Python 3.8+** with pip
- **Node.js 16+** with npm
- **MySQL Server** (for authentication database)

## 🎆 **SETUP RESULTS - WHAT YOU GET**

After running `npm run dev`, you'll see:

```
🌐 React Frontend: http://localhost:5173  ✅ Authentication & Modern UI
🔧 Node.js Backend: http://localhost:3001   ✅ API & Database Ready
🤖 Flask AR App: http://localhost:5000      ✅ AI Sign Language Ready
```

### 🎯 **Quick Start Guide**

1. **Install Dependencies (First Time Only):**
   ```bash
   npm run setup
   ```

2. **Start Everything:**
   ```bash
   npm run dev
   ```

3. **Access Your Application:**
   - 🎆 **Browser opens automatically** to `http://localhost:5173`
   - 🔐 **Login** with demo credentials: `demo@example.com` / `password123`
   - 🤖 **Get redirected** automatically to Flask AR app at `http://localhost:5000`

### 🛠️ **Alternative Setup Methods**

#### PowerShell Script (Windows)
```powershell
.\start-app.ps1  # Includes system checks and port conflict detection
```

#### Manual Individual Services
```bash
npm run frontend   # Start only React app (5173)
npm run backend    # Start only Node.js API (3001)  
npm run flask      # Start only Flask app (5000)
```

## 🏧 **UNIFIED SYSTEM ARCHITECTURE**

### 🔍 **How It All Works Together**

```
👥 User
  ↓
🌐 React Frontend (5173)
  │  • Modern authentication UI
  │  • Login/Register forms
  │  • Responsive design
  ↓ (Login Request)
🔧 Node.js Backend (3001)
  │  • JWT authentication
  │  • Password encryption
  │  • MySQL database
  ↓ (Success Redirect)
🤖 Flask AR Application (5000)
  • Sign-to-voice conversion
  • Text-to-sign conversion  
  • Voice-to-sign conversion
  • AR display capabilities
  • AI-powered recognition
```

### 💻 **Component Details**

**1. React Frontend (Port 5173)**
- ✅ Modern, responsive authentication interface
- ✅ Real-time form validation
- ✅ Demo credentials support
- ✅ Automatic redirect after login
- ✅ Error handling and user feedback

**2. Node.js Backend (Port 3001)**
- ✅ RESTful API with Express.js
- ✅ MySQL database integration
- ✅ JWT token-based authentication
- ✅ Bcrypt password hashing
- ✅ CORS configuration
- ✅ Automatic database setup

**3. Flask AR Application (Port 5000)**
- ✅ Machine learning for sign language recognition
- ✅ Real-time video processing
- ✅ Text-to-speech conversion
- ✅ AR overlay capabilities
- ✅ Multi-modal interaction
- ✅ Settings and user preferences

## 🚀 **COMPLETE INSTALLATION GUIDE**

### ⚡ **Super Quick Setup (3 Commands)**

```bash
# 1. Clone the repository
git clone <your-repo>
cd SignVision_App

# 2. Install ALL dependencies (Node.js + Python)
npm run setup
pip install -r requirements.txt

# 3. Start EVERYTHING with one command
npm run dev
```

**That's it! 🎉 All three services are now running!**

### 📝 **Detailed Step-by-Step Setup**

#### **Step 1: Clone and Navigate**
```bash
git clone <your-repo>
cd SignVision_App
```

#### **Step 2: Install All Dependencies**
```bash
npm run setup          # Installs ALL Node.js dependencies
pip install -r requirements.txt  # Install Python dependencies
```

#### **Step 3: Database Setup (Auto-configured)**
```sql
-- MySQL database is created automatically!
-- Just ensure MySQL server is running
CREATE DATABASE IF NOT EXISTS signvision;
```

#### **Step 4: Environment Configuration**

Create `sign-in-page/server/.env`:
```env
DB_HOST=localhost
DB_USER=your_mysql_user
DB_PASSWORD=your_mysql_password
DB_NAME=signvision
JWT_SECRET=your_jwt_secret_key
CLIENT_URL=http://localhost:5173
PORT=3001
```

#### **Step 5: Launch Unified Application**
```bash
npm run dev  # Starts all 3 services simultaneously
```

### 🎆 **What Happens When You Run `npm run dev`:**

1. 🔄 **Concurrently starts 3 processes:**
   - React Frontend (Vite dev server)
   - Node.js Backend (Express + MySQL)
   - Flask AR Application (Python + AI models)

2. 🔍 **Automatic checks:**
   - Port availability (3001, 5000, 5173)
   - Database connection
   - Dependency verification

3. 🎯 **Ready-to-use URLs:**
   - Authentication: `http://localhost:5173`
   - API Health Check: `http://localhost:3001/health`
   - AR Application: `http://localhost:5000`

## 🎯 Usage

### First Time Setup
1. Run `npm run dev`
2. Navigate to http://localhost:5173
3. Register a new account or use demo credentials:
   - Email: demo@example.com
   - Password: password123
4. After login, you'll be redirected to the AR application

### Features Available
- **Sign-to-Voice**: Convert sign language to spoken words
- **Text-to-Sign**: Convert text input to sign language videos
- **Voice-to-Sign**: Convert speech to sign language
- **AR Display**: Augmented reality sign language overlay

## 📦 **ALL AVAILABLE COMMANDS**

### ⭐ **Main Unified Commands**
```bash
npm run dev          # 🚀 START ALL 3 SERVICES (Main command!)
npm run start        # 🎯 Production version of above
npm run setup        # 📎 Install ALL dependencies everywhere
```

### 🔧 **Individual Service Commands**
```bash
npm run frontend     # 🌐 Start only React app (5173)
npm run backend      # 🔧 Start only Node.js API (3001)  
npm run flask        # 🤖 Start only Flask AR app (5000)
```

### 🛠️ **Utility Commands**
```bash
npm run install-all  # 📎 Install all dependencies (alias for setup)
npm run build        # 🏠 Build React frontend for production
npm run preview      # 🔍 Preview built React app
npm run clean        # 🧹 Clean all node_modules folders
npm test            # ⚙️ Run tests for all components
```

### 🔍 **Alternative Startup Methods**
```bash
# PowerShell script (Windows) - includes system checks
.\start-app.ps1

# Manual service-by-service startup
cd sign-in-page/server && npm start    # Backend first
cd sign-in-page/frontend && npm run dev # Frontend second  
python app.py                           # Flask third
```

## 🔧 Configuration

### Port Configuration
- **React**: 5173 (configurable in vite.config.js)
- **Node.js**: 3001 (configurable in .env)
- **Flask**: 5000 (configurable via PORT environment variable)

### Environment Variables

#### Flask App
```bash
PORT=5000                    # Flask application port
HOST=127.0.0.1              # Flask application host
```

#### Node.js Backend
```bash
DB_HOST=localhost            # MySQL host
DB_USER=root                 # MySQL username
DB_PASSWORD=password         # MySQL password
DB_NAME=signvision          # Database name
JWT_SECRET=secret            # JWT secret key
PORT=3001                    # Backend port
```

## 🚨 **TROUBLESHOOTING UNIFIED APPLICATION**

### ⚠️ **Common Issues & Quick Fixes**

#### 🔌 **Port Conflicts (Most Common)**
```bash
# Check which processes are using our ports
netstat -ano | findstr ":5000"   # Flask AR App
netstat -ano | findstr ":3001"   # Node.js Backend
netstat -ano | findstr ":5173"   # React Frontend

# Kill conflicting processes
taskkill /PID <PID_NUMBER> /F

# Or use our PowerShell script that checks automatically
.\start-app.ps1
```

#### 📊 **Services Not Starting Together**
```bash
# Try individual startup to isolate the issue
npm run backend    # Test Node.js API first
npm run frontend   # Test React app second
npm run flask      # Test Flask app third

# Check logs for specific errors
npm run dev        # Watch all service logs together
```

#### Database Connection Issues
1. Ensure MySQL server is running
2. Check database credentials in `.env`
3. Verify database exists or will be created automatically

#### Python Dependencies
```bash
pip install -r requirements.txt
# If specific packages fail:
pip install flask opencv-python mediapipe tensorflow
```

#### Node.js Dependencies
```bash
npm run clean        # Clean all node_modules
npm run setup        # Reinstall all dependencies
```

### Service-Specific Issues

#### React App Not Starting
- Check if port 5173 is available
- Run `cd sign-in-page/frontend && npm install`
- Check vite.config.js for proxy settings

#### Node.js Backend Issues  
- Verify MySQL is running and accessible
- Check `.env` file exists and has correct values
- Run `cd sign-in-page/server && npm install`

#### Flask App Issues
- Install Python requirements: `pip install -r requirements.txt`
- Check camera permissions for AR features
- Verify model files exist (model.p, gender_detection.keras)

## 🎮 Demo Credentials

For testing purposes:
- **Email**: demo@example.com
- **Password**: password123

## 🔐 Security Notes

- JWT tokens are used for authentication
- Passwords are hashed using bcrypt
- CORS is configured for cross-origin requests
- Session management handles user state

## 📁 **UNIFIED PROJECT STRUCTURE**

```
SignVision_App/                    # 🏠 Root - Unified Application
├── package.json                   # ⭐ MAIN - Controls all 3 services
├── start-app.ps1                  # 📜 PowerShell alternative startup
├── README.md                      # 📖 This comprehensive guide
│
├── sign-in-page/                  # 🔐 Authentication System
│   ├── frontend/                  # 🌐 React App (Port 5173)
│   │   ├── src/
│   │   │   ├── pages/             # Login/Register components
│   │   │   └── App.jsx            # Main React router
│   │   ├── package.json           # React dependencies
│   │   └── vite.config.js         # ⚙️ Vite config with proxy
│   │
│   └── server/                    # 🔧 Node.js API (Port 3001)
│       ├── routes/                # Authentication routes
│       ├── lib/                   # Database connection
│       ├── .env                   # 📎 Environment variables
│       ├── package.json           # Node.js dependencies
│       └── index.js               # Express server
│
└── Flask AR Application/          # 🤖 AI Sign Language (Port 5000)
    ├── app.py                     # ⭐ Main Flask application
    ├── requirements.txt           # Python dependencies
    ├── static/
    │   ├── assets/                # Sign language video files
    │   └── blank.jpg              # Placeholder image
    ├── templates/                 # HTML templates
    ├── model.p                    # AI model files
    └── gender_detection.keras     # Gender detection model
```

### 🎯 **Key Files Explained**

- **`package.json`** (Root) - 🎆 **The magic file that runs everything**
- **`start-app.ps1`** - 🛡️ Windows PowerShell alternative with checks
- **`vite.config.js`** - ⚙️ Proxy configuration for API calls
- **`.env`** - 🔐 Database and API configuration
- **`app.py`** - 🤖 Flask AI application with AR capabilities

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🎆 **UNIFIED APPLICATION ACHIEVEMENTS**

### ✅ **What We've Accomplished**

✨ **Single Command Startup**: `npm run dev` launches everything  
✨ **Seamless Integration**: React → Node.js → Flask workflow  
✨ **Port Management**: Automatic conflict detection and resolution  
✨ **Cross-Platform**: Works on Windows, macOS, and Linux  
✨ **Developer Experience**: Hot reloading, error handling, logs  
✨ **Production Ready**: Build and deployment scripts included  

### 📊 **Performance Metrics**

- **Startup Time**: ~10-15 seconds for all services
- **Memory Usage**: Optimized for development workflow
- **Port Allocation**: Smart port management (5173, 3001, 5000)
- **Hot Reload**: Instant React updates, Flask debug mode

### 🎯 **User Experience**

1. **Developer**: One command to start everything
2. **End User**: Smooth authentication flow
3. **Deployment**: Unified build and deployment process
4. **Maintenance**: Centralized configuration and logs

---

## 🚀 **QUICK REFERENCE**

```bash
# Start everything (main command)
npm run dev

# First time setup
npm run setup
pip install -r requirements.txt

# Individual services
npm run frontend  # React (5173)
npm run backend   # Node.js (3001)
npm run flask     # Flask (5000)

# Alternative startup
.\start-app.ps1   # Windows PowerShell
```

**URLs after startup:**
- 🌐 Authentication: http://localhost:5173
- 🔧 API Health: http://localhost:3001/health  
- 🤖 AR Application: http://localhost:5000

---

**Made with ❤️ for the sign language community**  
**⚡ Powered by unified application architecture**
