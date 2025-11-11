"""
CovetPy Configuration Example

Database configuration for the migration system.
"""

# Database Configuration
DATABASE = {
    "engine": "sqlite",  # Options: "sqlite", "postgresql", "mysql"
    "database": "example.db",  # For SQLite: path to database file
    # For PostgreSQL/MySQL:
    # "host": "localhost",
    # "port": 5432,  # or 3306 for MySQL
    # "username": "your_username",
    # "password": "your_password",
}

# For PostgreSQL example:
# DATABASE = {
#     "engine": "postgresql",
#     "database": "myapp_db",
#     "host": "localhost",
#     "port": 5432,
#     "username": "postgres",
#     "password": "password",
# }

# For MySQL example:
# DATABASE = {
#     "engine": "mysql",
#     "database": "myapp_db",
#     "host": "localhost",
#     "port": 3306,
#     "username": "root",
#     "password": "password",
# }
