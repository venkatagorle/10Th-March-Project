import psycopg2
import pandas as pd
import os

# PostgreSQL connection details
DB_URL = "postgresql://supermarket_fm98_user:TMm5U0YeBBTLmNVYlEJQ3SG69hnXPPS1@dpg-cv643oggph6c73djqm4g-a.oregon-postgres.render.com/supermarket_fm98"

# Define CSV file path
data_dir = r"C:\10 March 66 Project\data"
csv_file = os.path.join(data_dir, "supermarket_sales.csv")

# Read CSV file
df = pd.read_csv(csv_file)

# Standardize column names (trim spaces and lowercase)
df.columns = df.columns.str.strip().str.lower()

# Connect to PostgreSQL
conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

# ---------------------- Identify Schema ----------------------
# Define tables and primary keys
table_definitions = {
    "customers": {
        "columns": {
            "customer type": "TEXT",
            "gender": "TEXT"
        },
        "primary_key": "customer_id SERIAL PRIMARY KEY"
    },
    "products": {
        "columns": {
            "product line": "TEXT"
        },
        "primary_key": "product_id SERIAL PRIMARY KEY"
    },
    "sales": {
        "columns": {
            "date": "DATE",
            "total": "REAL"
        },
        "primary_key": "sale_id SERIAL PRIMARY KEY",
        "foreign_keys": [
            "customer_id INTEGER REFERENCES customers(customer_id) ON DELETE CASCADE",
            "product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE"
        ]
    }
}

# ---------------------- Create Tables Dynamically ----------------------
for table, details in table_definitions.items():
    columns_sql = [details["primary_key"]]  # Add primary key
    
    # Add columns
    for column, dtype in details["columns"].items():
        formatted_col = column.replace(" ", "_")  # PostgreSQL doesn't allow spaces
        columns_sql.append(f"{formatted_col} {dtype}")

    # Add foreign keys if any
    if "foreign_keys" in details:
        columns_sql.extend(details["foreign_keys"])

    # Create table
    create_table_query = f"CREATE TABLE {table} ({', '.join(columns_sql)});"
    cursor.execute(create_table_query)

conn.commit()
print("✅ Schema dynamically created based on CSV!")

# Close connection
cursor.close()
conn.close()
