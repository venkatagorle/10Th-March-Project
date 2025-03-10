import sqlite3
import pandas as pd

# Connect to SQLite database
db_path = "sqlite_database.db"
conn = sqlite3.connect(db_path)

# Function to print table data
def display_table(table_name, limit=5):
    query = f"SELECT * FROM {table_name} LIMIT {limit};"
    df = pd.read_sql_query(query, conn)
    print(f"\nTable: {table_name} (showing {limit} rows)\n", df)

# Verify Customers Table
display_table("Customers")

# Verify Products Table
display_table("Products")

# Verify Sales Table
display_table("Sales")

# Close connection
conn.close()
