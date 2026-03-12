# Database Setup Guide

## MySQL Database Setup

Your application requires a MySQL database named `har_db` with a `users` table.

### Step 1: Ensure MySQL is Running
- Make sure MySQL server is installed and running on your system
- Default connection settings in `views.py`:
  - Host: `localhost`
  - User: `root`
  - Password: `root`
  - Database: `har_db`

### Step 2: Create the Database and Table

Run these SQL commands in MySQL Workbench or command line:

```sql
CREATE DATABASE IF NOT EXISTS har_db;

USE har_db;

CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(100) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(150) NOT NULL UNIQUE,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
```

### Step 3: Update Database Credentials (if needed)

If your MySQL credentials are different, edit `Medical/views.py` and update:
- `MYSQL_HOST`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DB`

### Step 4: Test the Connection

After setting up the database, try:
1. Sign up a new user at `/signup/`
2. Login with that user at `/login/`

If you see error messages, they will now be more descriptive and help identify the issue.
