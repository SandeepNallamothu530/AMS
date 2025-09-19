"""
Simple authentication module for AMS app - Azure SQL Database
"""

import pyodbc
import os
from typing import Tuple, Dict, Any

# List of possible drivers to try
POSSIBLE_DRIVERS = [
    "ODBC Driver 18 for SQL Server",
    "ODBC Driver 17 for SQL Server", 
    "ODBC Driver 13 for SQL Server",
    "SQL Server Native Client 11.0",
    "SQL Server"
]

def get_available_driver():
    """Find the first available SQL Server driver"""
    drivers = pyodbc.drivers()
    for driver in POSSIBLE_DRIVERS:
        if driver in drivers:
            return driver
    return None

def get_connection_string():
    """Build connection string with available driver"""
    driver = get_available_driver()
    if not driver:
        raise Exception("No SQL Server ODBC driver found. Please install Microsoft ODBC Driver for SQL Server.")
    
    # Azure SQL Database connection string - fixed format
    return f"Driver={{{driver}}};Server=tcp:amsdbserer.database.windows.net,1433;Database=amsdb;UID=ams-admin;PWD={{password_placeholder}};Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"

def get_connection_string_alternative():
    """Alternative connection string format for Azure SQL"""
    driver = get_available_driver()
    if not driver:
        raise Exception("No SQL Server ODBC driver found.")
    
    # Alternative format - sometimes works better with Azure SQL
    return f"DRIVER={{{driver}}};SERVER=amsdbserer.database.windows.net;PORT=1433;DATABASE=amsdb;UID=ams-admin;PWD={{password_placeholder}};Encrypt=yes;TrustServerCertificate=no;"

def get_connection():
    """Get database connection"""
    try:
        # Get password from environment variable for security
        password = os.environ.get('AMS_DB_PASSWORD', '01@bs.nttdata.com')
        
        # Debug: Print connection details (remove in production)
        driver = get_available_driver()
        print(f"Using driver: {driver}")
        print(f"Server: amsdbserer.database.windows.net")
        print(f"Database: amsdb")
        print(f"Username: ams-admin")
        
        # Try primary connection string first
        try:
            conn_str = get_connection_string().replace('{password_placeholder}', password)
            print(f"Trying primary connection string...")
            conn = pyodbc.connect(conn_str)
            return conn
        except pyodbc.Error as e1:
            print(f"Primary connection failed: {e1}")
            
            # Try alternative connection string
            print(f"Trying alternative connection string...")
            conn_str_alt = get_connection_string_alternative().replace('{password_placeholder}', password)
            conn = pyodbc.connect(conn_str_alt)
            return conn
            
    except pyodbc.Error as e:
        print(f"Database connection error: {e}")
        print("Available drivers:", pyodbc.drivers())
        print("\nTroubleshooting steps:")
        print("1. Verify server name: amsdbserver.database.windows.net")
        print("2. Check if user 'ams-admin' exists in Azure SQL")
        print("3. Verify password is correct")
        print("4. Check Azure SQL firewall rules")
        print("5. Ensure database 'amsdb' exists")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def init_auth_db() -> None:
    """Initialize the database with users table if it doesn't exist"""
    conn = get_connection()
    if not conn:
        return
    
    try:
        cursor = conn.cursor()
        
        # Create users table if it doesn't exist
        cursor.execute('''
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='users' AND xtype='U')
            CREATE TABLE users (
                id INT IDENTITY(1,1),
                email NVARCHAR(255) PRIMARY KEY NOT NULL,
                password NVARCHAR(255) NOT NULL,
                created_at DATETIME2 DEFAULT GETDATE()
            )
        ''')
        
        conn.commit()
        print("Database initialized successfully")
        
    except pyodbc.Error as e:
        print(f"Error initializing database: {e}")
    finally:
        conn.close()

def create_user(email: str, password: str) -> Tuple[bool, str]:
    """Create a new user account with email and password"""
    # TODO: Add password hashing for security
    init_auth_db()
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
        conn.commit()
        return True, "Account created successfully"
        
    except pyodbc.IntegrityError:
        return False, "Email already exists"
    except pyodbc.Error as e:
        return False, f"Database error: {e}"
    finally:
        conn.close()

def get_user_by_email(email: str) -> Tuple[bool, Any]:
    """Fetch user by email"""
    init_auth_db()
    conn = get_connection()
    if not conn:
        return False, "Database connection failed"
    
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, email, password FROM users WHERE email = ?", (email,))
        row = cursor.fetchone()
        
        if row:
            return True, {"id": row[0], "email": row[1], "password": row[2]}
        return False, "Email not found"
        
    except pyodbc.Error as e:
        return False, f"Database error: {e}"
    finally:
        conn.close()

def authenticate_user(email: str, password: str) -> Tuple[bool, str]:
    """Authenticate user login with email and password"""
    ok, user = get_user_by_email(email)
    if not ok:
        return False, "Invalid email or password"
    
    # TODO: Use proper password hashing (bcrypt, scrypt, etc.)
    # Direct password comparison (NOT SECURE for production)
    if password == user["password"]:
        return True, "Login successful"
    else:
        return False, "Invalid email or password"

def get_password_by_email(email: str) -> Tuple[bool, str]:
    """Get password for forgot password functionality"""
    # WARNING: This is a security risk - passwords should never be retrievable
    ok, user = get_user_by_email(email)
    if not ok:
        return False, "Email not found"
    
    return True, user["password"]

def test_connection():
    """Test database connection"""
    try:
        print(f"Available drivers: {pyodbc.drivers()}")
        driver = get_available_driver()
        if driver:
            print(f"Using driver: {driver}")
        else:
            return False, "No suitable SQL Server driver found"
            
        conn = get_connection()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
                conn.close()
                return True, "Connection successful"
            except pyodbc.Error as e:
                conn.close()
                return False, f"Connection test failed: {e}"
        else:
            return False, "Could not establish connection"
    except Exception as e:
        return False, f"Error: {e}"

# Test the connection when module is imported
if __name__ == "__main__":
    success, message = test_connection()
    print(f"Connection test: {message}")
