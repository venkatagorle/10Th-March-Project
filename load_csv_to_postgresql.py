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
df.columns = df.columns.str.strip().str.lower()  # Standardize column names

# Rename columns to match SQL-friendly format
df.rename(columns={
    "customer type": "customer_type",  
    "gender": "gender",
    "product line": "product_line",
    "date": "date",
    "total": "total_price"
}, inplace=True)

# Connect to PostgreSQL
conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

# ---------------------- Drop Existing Tables ----------------------
drop_query = """
DO $$ 
DECLARE 
    r RECORD;
BEGIN
    FOR r IN (SELECT tablename FROM pg_tables WHERE schemaname = 'public') LOOP
        EXECUTE 'DROP TABLE IF EXISTS ' || r.tablename || ' CASCADE';
    END LOOP;
END $$;
"""
cursor.execute(drop_query)

# ---------------------- Create Tables Dynamically ----------------------
table_definitions = {
    "customers": {
        "columns": {
            "customer_type": "TEXT",
            "gender": "TEXT"
        },
        "primary_key": "customer_id SERIAL PRIMARY KEY"
    },
    "products": {
        "columns": {
            "product_line": "TEXT"
        },
        "primary_key": "product_id SERIAL PRIMARY KEY"
    },
    "sales": {
        "columns": {
            "date": "DATE",
            "total_price": "REAL"
        },
        "primary_key": "sale_id SERIAL PRIMARY KEY",
        "foreign_keys": [
            "customer_id INTEGER REFERENCES customers(customer_id) ON DELETE CASCADE",
            "product_id INTEGER REFERENCES products(product_id) ON DELETE CASCADE"
        ]
    }
}

# Create Tables
for table, details in table_definitions.items():
    columns_sql = [details["primary_key"]]  # Add primary key
    
    for column, dtype in details["columns"].items():
        columns_sql.append(f"{column} {dtype}")

    if "foreign_keys" in details:
        columns_sql.extend(details["foreign_keys"])

    create_table_query = f"CREATE TABLE {table} ({', '.join(columns_sql)});"
    cursor.execute(create_table_query)

# Commit schema creation
conn.commit()

# ---------------------- Load Data ----------------------
# Load Customers
customers_df = df[['customer_type', 'gender']].drop_duplicates().reset_index(drop=True)
for _, row in customers_df.iterrows():
    cursor.execute(
        "INSERT INTO customers (customer_type, gender) VALUES (%s, %s) RETURNING customer_id",
        (row["customer_type"], row["gender"])
    )
    row["customer_id"] = cursor.fetchone()[0]

# Load Products
products_df = df[['product_line']].drop_duplicates().reset_index(drop=True)
for _, row in products_df.iterrows():
    cursor.execute(
        "INSERT INTO products (product_line) VALUES (%s) RETURNING product_id",
        (row["product_line"],)
    )
    row["product_id"] = cursor.fetchone()[0]

# Load Sales Data
sales_df = df[['date', 'customer_type', 'product_line', 'total_price']]
for _, row in sales_df.iterrows():
    cursor.execute(
        """
        INSERT INTO sales (date, customer_id, product_id, total_price) 
        VALUES (
            %s, 
            (SELECT customer_id FROM customers WHERE customer_type = %s LIMIT 1),
            (SELECT product_id FROM products WHERE product_line = %s LIMIT 1),
            %s
        )
        """,
        (row["date"], row["customer_type"], row["product_line"], row["total_price"])
    )

# Commit and Close Connection
conn.commit()
cursor.close()
conn.close()

print("✅ Database setup complete, and data uploaded successfully!")
