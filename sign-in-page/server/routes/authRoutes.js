import express from 'express'
import mysql from 'mysql2/promise'
import { connectToDatabase } from '../lib/db.js'
import bcrypt from 'bcrypt'
import jwt from 'jsonwebtoken'
import dotenv from 'dotenv'

// Load environment variables
dotenv.config()

const router = express.Router()

// Add middleware to parse JSON bodies
router.use(express.json())

// Add CORS middleware for development
router.use((req, res, next) => {
    res.header('Access-Control-Allow-Origin', process.env.CLIENT_URL || 'http://localhost:5173');
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization');
    res.header('Access-Control-Allow-Credentials', 'true');
    
    // Handle preflight requests
    if (req.method === 'OPTIONS') {
        return res.status(200).end();
    }
    next();
});

// Add request logging middleware
router.use((req, res, next) => {
    console.log(`${new Date().toISOString()} - ${req.method} ${req.originalUrl}`);
    next();
});

// Enhanced register endpoint with XAMPP optimizations
router.post('/register', async (req, res) => {
    console.log('📝 Register request body:', req.body);

    const { username, email, password } = req.body;

    // Validate request body
    if (!req.body || Object.keys(req.body).length === 0) {
        return res.status(400).json({ 
            message: "Request body is empty",
            hint: "Ensure you're sending JSON with Content-Type: application/json"
        });
    }

    // Trim and normalize inputs
    const trimmedUsername = username?.toString().trim();
    const trimmedEmail = email?.toString().toLowerCase().trim();

    // Enhanced validation for required fields
    if (!trimmedUsername || !trimmedEmail || !password) {
        return res.status(400).json({
            message: "All fields are required",
            received: { 
                username: !!trimmedUsername, 
                email: !!trimmedEmail, 
                password: !!password 
            }
        });
    }

    // Validate username length and format
    if (trimmedUsername.length < 3 || trimmedUsername.length > 30) {
        return res.status(400).json({ 
            message: "Username must be between 3 and 30 characters" 
        });
    }

    if (!/^[a-zA-Z0-9_]+$/.test(trimmedUsername)) {
        return res.status(400).json({ 
            message: "Username can only contain letters, numbers, and underscores" 
        });
    }

    // Validate email format
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(trimmedEmail)) {
        return res.status(400).json({ message: "Invalid email format" });
    }

    // Validate password strength
    if (password.length < 6) {
        return res.status(400).json({ 
            message: "Password must be at least 6 characters long" 
        });
    }

    if (password.length > 100) {
        return res.status(400).json({ 
            message: "Password is too long" 
        });
    }

    let db;
    try {
        console.log('🔗 Attempting to connect to XAMPP database...');
        db = await connectToDatabase();
        console.log('✅ XAMPP database connected successfully');

        // Check if username already exists
        const [usernameRows] = await db.execute(
            'SELECT id FROM users WHERE username = ?', 
            [trimmedUsername]
        );
        
        if (usernameRows.length > 0) {
            return res.status(409).json({ 
                message: "Username already exists. Please choose a different username." 
            });
        }

        // Check if email already exists
        const [emailRows] = await db.execute(
            'SELECT id FROM users WHERE email = ?', 
            [trimmedEmail]
        );
        
        if (emailRows.length > 0) {
            return res.status(409).json({ 
                message: "Email already registered. Please use a different email or login." 
            });
        }

        // Hash password with bcrypt
        const saltRounds = 12;
        const hashPassword = await bcrypt.hash(password, saltRounds);
        
        console.log('💾 Inserting new user into XAMPP database:', { 
            username: trimmedUsername, 
            email: trimmedEmail 
        });

        // Insert user into XAMPP database
        const [result] = await db.execute(
            "INSERT INTO users (username, email, password, created_at) VALUES (?, ?, ?, NOW())",
            [trimmedUsername, trimmedEmail, hashPassword]
        );

        console.log('✅ User created successfully in XAMPP database with ID:', result.insertId);
        
        // Return success response
        return res.status(201).json({ 
            message: "User registered successfully in XAMPP database",
            userId: result.insertId,
            username: trimmedUsername,
            email: trimmedEmail,
            timestamp: new Date().toISOString()
        });

    } catch (err) {
        console.error('❌ XAMPP Database registration error:', err);
        
        // MySQL/XAMPP specific error handling
        if (err.code === 'ER_DUP_ENTRY') {
            if (err.sqlMessage.includes('username')) {
                return res.status(409).json({ message: "Username already exists" });
            }
            if (err.sqlMessage.includes('email')) {
                return res.status(409).json({ message: "Email already registered" });
            }
            return res.status(409).json({ message: "User already exists" });
        }
        
        if (err.code === 'ER_ACCESS_DENIED_ERROR') {
            return res.status(500).json({ 
                message: "XAMPP database access denied. Check your MySQL credentials." 
            });
        }
        
        if (err.code === 'ER_BAD_DB_ERROR') {
            return res.status(500).json({ 
                message: "Database not found. Please create the database in XAMPP phpMyAdmin." 
            });
        }
        
        if (err.code === 'ECONNREFUSED') {
            return res.status(500).json({ 
                message: "Cannot connect to XAMPP MySQL. Ensure MySQL is running in XAMPP Control Panel." 
            });
        }
        
        if (err.code === 'ER_NO_SUCH_TABLE') {
            return res.status(500).json({ 
                message: "Users table does not exist. Please run the SQL setup script." 
            });
        }
        
        // Generic error response
        res.status(500).json({ 
            message: "Registration failed. Please try again.",
            ...(process.env.NODE_ENV === 'development' && { 
                error: err.message,
                code: err.code 
            })
        });
    } finally {
        // Ensure database connection is closed
        if (db && db.end) {
            try {
                await db.end();
                console.log('🔒 XAMPP database connection closed');
            } catch (closeErr) {
                console.error('❌ Error closing XAMPP connection:', closeErr);
            }
        }
    }
});

router.post('/login', async (req, res) => {
    console.log('🔑 Login request body:', req.body);

    const { email, password } = req.body;

    // Trim and normalize email
    const trimmedEmail = email?.toLowerCase().trim();

    // Add validation for required fields
    if (!trimmedEmail || !password) {
        return res.status(400).json({
            message: "Email and password are required",
            received: { email: !!trimmedEmail, password: !!password }
        });
    }

    let db;
    try {
        db = await connectToDatabase();
        
        // Use execute for prepared statements
        const [rows] = await db.execute(
            'SELECT id, username, email, password FROM users WHERE email = ?',
            [trimmedEmail]
        );
        
        if (rows.length === 0) {
            return res.status(401).json({ message: "Invalid credentials" });
        }

        const user = rows[0];
        const isMatch = await bcrypt.compare(password, user.password);
        
        if (!isMatch) {
            return res.status(401).json({ message: "Invalid credentials" });
        }

        // Verify JWT_KEY is available
        if (!process.env.JWT_KEY) {
            console.error('❌ JWT_KEY is not defined in environment variables');
            return res.status(500).json({ message: "Server configuration error" });
        }

        const token = jwt.sign(
            { 
                id: user.id,
                email: user.email 
            }, 
            process.env.JWT_KEY, 
            { expiresIn: '3h' }
        );

        console.log('✅ Login successful for user:', user.email);
        
        return res.status(200).json({ 
            token: token, 
            message: "Login successful",
            user: { 
                id: user.id, 
                username: user.username, 
                email: user.email 
            }
        });

    } catch (err) {
        console.error('❌ Login error:', err);
        
        if (err.message.includes('JWT_KEY')) {
            return res.status(500).json({ message: "Server configuration error" });
        }
        
        // Database errors
        if (err.code === 'ER_ACCESS_DENIED_ERROR' || err.code === 'ECONNREFUSED') {
            return res.status(500).json({ message: "Database connection error" });
        }
        
        res.status(500).json({ 
            message: "Internal server error",
            ...(process.env.NODE_ENV === 'development' && { error: err.message })
        });
    } finally {
        if (db && db.end) {
            try {
                await db.end();
            } catch (closeErr) {
                console.error('❌ Error closing connection:', closeErr);
            }
        }
    }
});

const verifyToken = (req, res, next) => {
    try {
        const authHeader = req.headers['authorization'] || req.headers['Authorization'];
        
        if (!authHeader) {
            return res.status(401).json({ message: "Access denied. No token provided." });
        }

        // Handle both "Bearer token" and just "token" formats
        const token = authHeader.startsWith('Bearer ') 
            ? authHeader.split(' ')[1] 
            : authHeader;

        if (!token) {
            return res.status(401).json({ message: "Access denied. No token provided." });
        }

        if (!process.env.JWT_KEY) {
            console.error('❌ JWT_KEY missing in token verification');
            return res.status(500).json({ message: "Server configuration error" });
        }

        const decoded = jwt.verify(token, process.env.JWT_KEY);
        req.userId = decoded.id;
        req.userEmail = decoded.email;
        
        console.log('✅ Token verified for user:', decoded.email);
        next();

    } catch (err) {
        console.error('❌ Token verification error:', err.name);
        
        if (err.name === 'TokenExpiredError') {
            return res.status(401).json({ message: "Token expired" });
        }
        if (err.name === 'JsonWebTokenError') {
            return res.status(401).json({ message: "Invalid token" });
        }
        if (err.name === 'NotBeforeError') {
            return res.status(401).json({ message: "Token not active" });
        }
        
        return res.status(401).json({ message: "Token verification failed" });
    }
};

router.get('/home', verifyToken, async (req, res) => {
    let db;
    try {
        db = await connectToDatabase();
        
        // Only select necessary fields, exclude password
        const [rows] = await db.execute(
            'SELECT id, username, email, created_at FROM users WHERE id = ?', 
            [req.userId]
        );
        
        if (rows.length === 0) {
            return res.status(404).json({ message: "User not found" });
        }

        const user = rows[0];
        console.log('🏠 Home route accessed by:', user.email);
        
        return res.status(200).json({ 
            user: {
                id: user.id,
                username: user.username,
                email: user.email,
                createdAt: user.created_at
            }
        });

    } catch (err) {
        console.error('❌ Home route error:', err);
        
        if (err.code === 'ER_ACCESS_DENIED_ERROR' || err.code === 'ECONNREFUSED') {
            return res.status(500).json({ message: "Database connection error" });
        }
        
        return res.status(500).json({ 
            message: "Internal server error",
            ...(process.env.NODE_ENV === 'development' && { error: err.message })
        });
    } finally {
        if (db && db.end) {
            try {
                await db.end();
            } catch (closeErr) {
                console.error('❌ Error closing connection:', closeErr);
            }
        }
    }
});

// Add a health check endpoint
router.get('/health', async (req, res) => {
    let db;
    try {
        db = await connectToDatabase();
        await db.execute('SELECT 1');
        res.status(200).json({
            status: 'OK',
            database: 'Connected',
            timestamp: new Date().toISOString()
        });
    } catch (err) {
        res.status(500).json({
            status: 'Error',
            database: 'Disconnected',
            error: err.message
        });
    } finally {
        if (db && db.end) {
            try {
                await db.end();
            } catch (closeErr) {
                console.error('❌ Error closing connection:', closeErr);
            }
        }
    }
});

// Temporary route to list all users (for debugging)
router.get('/users', async (req, res) => {
    let db;
    try {
        db = await connectToDatabase();
        const [rows] = await db.execute('SELECT id, username, email, created_at FROM users');
        res.status(200).json({
            users: rows,
            count: rows.length
        });
    } catch (err) {
        res.status(500).json({
            message: 'Error fetching users',
            error: err.message
        });
    } finally {
        if (db && db.end) {
            try {
                await db.end();
            } catch (closeErr) {
                console.error('❌ Error closing connection:', closeErr);
            }
        }
    }
});

export default router;