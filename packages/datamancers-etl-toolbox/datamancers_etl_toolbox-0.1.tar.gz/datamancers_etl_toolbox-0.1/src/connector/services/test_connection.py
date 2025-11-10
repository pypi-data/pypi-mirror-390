import pyodbc
import os
import time
import sys
import ssl
import platform
from dotenv import load_dotenv

load_dotenv()

# Connection parameters
server = os.getenv("MONEY_S4_SERVER")
database = os.getenv("MONEY_S4_DATABASE")
username = os.getenv("MONEY_S4_USERNAME")
password = os.getenv("MONEY_S4_PASSWORD")
port = 1433
print(f"Attempting to connect to: {server}:{port}")
print(f"Python version: {sys.version}")
print(f"PyODBC version: {pyodbc.version}")
print(f"OpenSSL version: {ssl.OPENSSL_VERSION}")
print(f"Operating system: {platform.system()} {platform.version()}")

# List available drivers
print("\nAvailable ODBC drivers:")
for driver in pyodbc.drivers():
    print(f"  - {driver}")

# Try multiple connection methods
connection_methods = []

# Windows-specific connection strings if running on Windows
if platform.system() == 'Windows':
    connection_methods.extend([
        {
            "name": "Windows Authentication",
            "string": (
                f"DRIVER={{ODBC Driver for SQL Server}};"
                f"SERVER={server},{port};"
                f"DATABASE={database};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;"
            )
        },
        {
            "name": "SQL Server Native Client 11.0",
            "string": (
                f"DRIVER={{SQL Server Native Client 11.0}};"
                f"SERVER={server},{port};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
                f"TrustServerCertificate=yes;"
            )
        },
        {
            "name": "SQL Server with older TLS settings",
            "string": (
                f"DRIVER={{SQL Server}};"
                f"SERVER={server},{port};"
                f"DATABASE={database};"
                f"UID={username};"
                f"PWD={password};"
            )
        },
    ])

# Cross-platform connection strings
connection_methods.extend([
    {
        "name": "ODBC Driver 18 with specific TLS 1.2 cipher suites",
        "string": (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server},{port};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"TrustServerCertificate=yes;"
            f"Encrypt=yes;"
            f"TLS_Version=1.2;"  # Force TLS 1.2 specifically
            f"ColumnEncryption=Disabled;"
        )
    },
    {
        "name": "ODBC Driver 17 with older cipher suites",
        "string": (
            f"DRIVER={{ODBC Driver 17 for SQL Server}};"
            f"SERVER={server},{port};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"Encrypt=yes;"
            f"TrustServerCertificate=yes;"
            f"TLS_Version=1.0;"  # Try older TLS version
        )
    },
    {
        "name": "ODBC Driver with encryption disabled",
        "string": (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER={server},{port};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
            f"Encrypt=no;"
            f"TrustServerCertificate=no;"
        )
    },
    {
        "name": "Try with TCP protocol explicitly",
        "string": (
            f"DRIVER={{ODBC Driver 18 for SQL Server}};"
            f"SERVER=tcp:{server},{port};"
            f"DATABASE={database};"
            f"UID={username};"
            f"PWD={password};"
        )
    },
])

success = False

for method in connection_methods:
    try:
        print(f"\nTrying connection method: {method['name']}")
        print(f"Connection string: {method['string']}")
        
        start_time = time.time()
        conn = pyodbc.connect(method['string'], timeout=30)
        end_time = time.time()
        
        print(f"Connection successful! Time taken: {end_time - start_time:.2f} seconds")

        cursor = conn.cursor()
        cursor.execute("SELECT @@VERSION")
        row = cursor.fetchone()
        print(f"SQL Server version: {row[0]}")

        cursor.close()
        conn.close()
        print("Connection closed.")
        
        success = True
        break  # Exit the loop if connection is successful
        
    except pyodbc.Error as e:
        print(f"Connection failed: {e}")
        print(f"Error code: {e.args[0] if e.args else 'No error code'}")
        print(f"Error message: {e.args[1] if len(e.args) > 1 else 'No additional message'}")
    except Exception as ex:
        print(f"Unexpected error: {ex}")
        print(f"Error type: {type(ex).__name__}")
        print(f"Error details: {str(ex)}")

if not success:
    print("\nAll connection methods failed.")
    print("\nBased on the SQL Server error message:")
    print("- Fatal alert error code 40 indicates a handshake failure")
    print("- The server rejected the connection because of cipher suite incompatibility")
    print("- Your client and the SQL Server can't agree on encryption methods")
    print("\nPossible solutions:")
    print("1. Check SQL Server configuration:")
    print("   - Run 'SELECT name, value FROM sys.configurations WHERE name LIKE '%tls%'' on the server")
    print("   - Check if 'Force Encryption' is enabled in SQL Server Configuration Manager")
    print("2. Check Windows registry settings for TLS:")
    print("   - HKEY_LOCAL_MACHINE\\SYSTEM\\CurrentControlSet\\Control\\SecurityProviders\\SCHANNEL\\Protocols")
    print("3. Try updating ODBC drivers on both client and server")
    print("4. Check if a firewall is blocking the connection")
    print("5. Ask the server admin to check SQL Server error logs for more details")
