import sqlite3
import pandas as pd

# Connect to SQLite database
db_path = "sqlite_database.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Load extracted CSV data
df = pd.read_csv("./data/supermarket_sales.csv")

# Transform Customers Table
customers = df[['Customer type', 'Gender']].drop_duplicates().reset_index(drop=True)
customers.insert(0, "customer_id", range(1, len(customers) + 1))
customers.rename(columns={'Customer type': 'customer_name', 'Gender': 'gender'}, inplace=True)

# Insert into Customers table
customers.to_sql("Customers", conn, if_exists="replace", index=False)

# Transform Products Table
products = df[['Product line']].drop_duplicates().reset_index(drop=True)
products.insert(0, "product_id", range(1, len(products) + 1))
products.rename(columns={'Product line': 'product_name'}, inplace=True)
products["category"] = "General"  # Assuming a default category

# Insert into Products table
products.to_sql("Products", conn, if_exists="replace", index=False)

# Transform Sales Table
sales = df[['Date', 'Customer type', 'Product line', 'Total']]
sales = sales.merge(customers, left_on="Customer type", right_on="customer_name", how="left")
sales = sales.merge(products, left_on="Product line", right_on="product_name", how="left")

# Keep relevant columns
sales = sales[['Date', 'customer_id', 'product_id', 'Total']]
sales.rename(columns={'Total': 'total_price', 'Date': 'date'}, inplace=True)

# Insert into Sales table
sales.to_sql("Sales", conn, if_exists="replace", index=False)

print("Data inserted into tables successfully.")

# Commit and close connection
conn.commit()
conn.close()
