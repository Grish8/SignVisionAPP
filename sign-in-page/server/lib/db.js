import mysql from 'mysql2/promise'

export const connectToDatabase = async () => {
    console.log('Creating new database connection...');
    console.log('Database config:', {
        host: process.env.DB_HOST,
        user: process.env.DB_USER,
        database: process.env.DB_NAME,
        hasPassword: !!process.env.DB_PASSWORD
    });

    try {
        const connection = await mysql.createConnection({
            host: process.env.DB_HOST,
            user: process.env.DB_USER,
            password: process.env.DB_PASSWORD,
            database: process.env.DB_NAME
        });
        console.log('✅ Database connection established successfully');
        return connection;
    } catch (error) {
        console.error('❌ Database connection failed:', error);
        throw error;
    }
}