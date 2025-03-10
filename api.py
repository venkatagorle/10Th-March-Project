from fastapi import FastAPI
import psycopg2
import pandas as pd
from fastapi.responses import FileResponse

# PostgreSQL connection details
DB_URL = "postgresql://supermarket_fm98_user:TMm5U0YeBBTLmNVYlEJQ3SG69hnXPPS1@dpg-cv643oggph6c73djqm4g-a.oregon-postgres.render.com/supermarket_fm98"

# API setup
app = FastAPI()

# Endpoint to fetch total sales per product
@app.get("/sales-per-product")
def get_sales_per_product():
    conn = psycopg2.connect(DB_URL)
    query = """
    SELECT p.product_line, SUM(s.total_price) AS total_sales
    FROM sales s
    JOIN products p ON s.product_id = p.product_id
    GROUP BY p.product_line
    ORDER BY total_sales DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_dict(orient="records")

# Endpoint to fetch total sales per customer type
@app.get("/sales-per-customer-type")
def get_sales_per_customer_type():
    conn = psycopg2.connect(DB_URL)
    query = """
    SELECT c.customer_type, SUM(s.total_price) AS total_sales
    FROM sales s
    JOIN customers c ON s.customer_id = c.customer_id
    GROUP BY c.customer_type
    ORDER BY total_sales DESC;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_dict(orient="records")

# Endpoint to fetch monthly sales trend
@app.get("/monthly-sales-trend")
def get_monthly_sales_trend():
    conn = psycopg2.connect(DB_URL)
    query = """
    SELECT DATE_TRUNC('month', s.date) AS sales_month, SUM(s.total_price) AS total_sales
    FROM sales s
    GROUP BY sales_month
    ORDER BY sales_month;
    """
    df = pd.read_sql(query, conn)
    conn.close()
    return df.to_dict(orient="records")

# Endpoint to download the sales report PDF
@app.get("/download-report")
def download_report():
    report_path = r"C:\10 March 66 Project\reports\sales_report.pdf"
    return FileResponse(report_path, filename="sales_report.pdf", media_type="application/pdf")

# Run the API locally (for testing)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
