import express from 'express'
import cors from 'cors'
import mysql from 'mysql2/promise'
import authRouter from './routes/authRoutes.js'
import { connectToDatabase } from './lib/db.js'
import dotenv from 'dotenv'

// Load environment variables FIRST
dotenv.config()

const app = express()

// CORS configuration
app.use(cors({
    origin: process.env.CLIENT_URL || 'http://localhost:5173',
    credentials: true
}))

app.use(express.json())

// Test route to verify server is running
app.get('/', (req, res) => {
    res.json({ 
        message: 'Server is running!',
        timestamp: new Date().toISOString()
    })
})

// Health check endpoint
app.get('/health', async (req, res) => {
    let db;
    try {
        db = await connectToDatabase()
        await db.execute('SELECT 1')

        // Check if users table exists and has records
        const [tables] = await db.execute("SHOW TABLES LIKE 'users'")
        const tableExists = tables.length > 0

        let userCount = 0
        if (tableExists) {
            const [countResult] = await db.execute('SELECT COUNT(*) as count FROM users')
            userCount = countResult[0].count
        }

        res.status(200).json({
            status: 'OK',
            database: 'Connected',
            databaseName: process.env.DB_NAME,
            usersTableExists: tableExists,
            userCount: userCount,
            timestamp: new Date().toISOString()
        })
    } catch (error) {
        res.status(500).json({
            status: 'Error',
            database: 'Disconnected',
            error: error.message
        })
    } finally {
        if (db && db.end) {
            try {
                await db.end()
            } catch (closeError) {
                console.error('Error closing connection:', closeError)
            }
        }
    }
})

// Use auth routes
app.use('/auth', authRouter)

const setupDatabase = async () => {
    let tempConnection, db
    
    try {
        console.log('🔧 Setting up database...')
        
        // Check if required environment variables are present
        if (!process.env.DB_HOST || !process.env.DB_USER || !process.env.DB_NAME) {
            throw new Error('Missing required database environment variables')
        }

        console.log('Database configuration:', {
            host: process.env.DB_HOST,
            user: process.env.DB_USER,
            database: process.env.DB_NAME,
            hasPassword: !!process.env.DB_PASSWORD
        })

        // Create database if not exists
        tempConnection = await mysql.createConnection({
            host: process.env.DB_HOST,
            user: process.env.DB_USER,
            password: process.env.DB_PASSWORD
        })
        
        console.log('✅ Temporary connection established')

        await tempConnection.query(`CREATE DATABASE IF NOT EXISTS \`${process.env.DB_NAME}\``)
        console.log('✅ Database created or already exists')
        await tempConnection.end()
        tempConnection = null

        // Connect to the specific database
        db = await connectToDatabase()
        console.log('✅ Connected to database:', process.env.DB_NAME)

        // Create users table
        await db.query(`
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(255) NOT NULL,
                email VARCHAR(255) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `)
        console.log('✅ Users table created or already exists')

        console.log('🎉 Database setup completed successfully')

    } catch (error) {
        console.error('❌ Error setting up database:', error.message)
        
        // More specific error handling
        if (error.code === 'ER_ACCESS_DENIED_ERROR') {
            console.error('Database access denied. Check your username and password.')
        } else if (error.code === 'ECONNREFUSED') {
            console.error('Cannot connect to MySQL server. Make sure MySQL is running.')
        } else if (error.code === 'ER_BAD_DB_ERROR') {
            console.error('Database does not exist and could not be created.')
        }
        
        throw error // Prevent server from starting if DB setup fails
    } finally {
        // Clean up connections
        if (tempConnection) {
            try {
                await tempConnection.end()
                console.log('🔌 Temporary connection closed')
            } catch (closeError) {
                console.error('Error closing temporary connection:', closeError)
            }
        }
        if (db) {
            try {
                await db.end()
                console.log('🔌 Database connection closed')
            } catch (closeError) {
                console.error('Error closing database connection:', closeError)
            }
        }
    }
}

// Async function to start the server
const startServer = async () => {
    try {
        console.log('🚀 Starting server...')
        console.log('📁 Current directory:', process.cwd())
        console.log('🌳 Environment:', process.env.NODE_ENV || 'development')
        
        // Setup database first
        await setupDatabase()
        
        // Start the server
        const PORT = process.env.PORT || 3001
        app.listen(PORT, () => {
            console.log('🌈 Server is running on port', PORT)
            console.log('📍 Health check available at: http://localhost:' + PORT + '/health')
            console.log('📍 Auth routes available at: http://localhost:' + PORT + '/auth')
            console.log('📍 Test route available at: http://localhost:' + PORT)
        })

    } catch (error) {
        console.error('💥 Failed to start server:', error.message)
        console.error('Please check:')
        console.error('1. Is MySQL server running?')
        console.error('2. Are database credentials correct in .env file?')
        console.error('3. Does the database user have permission to create databases?')
        process.exit(1) // Exit with error code
    }
}

// Start the server
startServer()

// Handle graceful shutdown
process.on('SIGINT', async () => {
    console.log('\n🛑 Shutting down server gracefully...')
    process.exit(0)
})

process.on('unhandledRejection', (err) => {
    console.error('Unhandled Promise Rejection:', err)
    process.exit(1)
})