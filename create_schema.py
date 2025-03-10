import sqlite3

# Connect to SQLite database (Creates the file if it doesn't exist)
db_path = "sqlite_database.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# SQL Queries to Create Tables
create_tables_query = """
CREATE TABLE IF NOT EXISTS Customers (
    customer_id INTEGER PRIMARY KEY AUTOINCREMENT,
    customer_name TEXT NOT NULL,
    gender TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Products (
    product_id INTEGER PRIMARY KEY AUTOINCREMENT,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS Sales (
    sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
    date DATE NOT NULL,
    customer_id INTEGER,
    product_id INTEGER,
    total_price REAL NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES Customers(customer_id),
    FOREIGN KEY (product_id) REFERENCES Products(product_id)
);
"""

# Execute SQL Queries
cursor.executescript(create_tables_query)

print("Database schema created successfully.")

# Commit and close connection
conn.commit()
conn.close()
