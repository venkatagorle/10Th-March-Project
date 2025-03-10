import psycopg2

# PostgreSQL connection details
DB_URL = "postgresql://supermarket_fm98_user:TMm5U0YeBBTLmNVYlEJQ3SG69hnXPPS1@dpg-cv643oggph6c73djqm4g-a.oregon-postgres.render.com/supermarket_fm98"

# Connect to PostgreSQL
conn = psycopg2.connect(DB_URL)
cursor = conn.cursor()

# Drop existing tables if they exist
drop_query = """
DROP TABLE IF EXISTS Sales CASCADE;
DROP TABLE IF EXISTS Customers CASCADE;
DROP TABLE IF EXISTS Products CASCADE;
"""

cursor.execute(drop_query)
conn.commit()

# Create tables with foreign key relationships
create_query = """
CREATE TABLE Customers (
    customer_id SERIAL PRIMARY KEY,
    customer_name TEXT NOT NULL,
    gender TEXT NOT NULL
);

CREATE TABLE Products (
    product_id SERIAL PRIMARY KEY,
    product_name TEXT NOT NULL,
    category TEXT NOT NULL
);

CREATE TABLE Sales (
    sale_id SERIAL PRIMARY KEY,
    date DATE NOT NULL,
    customer_id INTEGER REFERENCES Customers(customer_id) ON DELETE CASCADE,
    product_id INTEGER REFERENCES Products(product_id) ON DELETE CASCADE,
    total_price REAL NOT NULL
);
"""

cursor.execute(create_query)
conn.commit()

print("PostgreSQL setup complete! Tables created successfully.")

# Close connection
cursor.close()
conn.close()
