from fastapi import FastAPI
import psycopg2
import pandas as pd
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import os

# PostgreSQL connection details
DB_URL = "postgresql://supermarket_fm98_user:TMm5U0YeBBTLmNVYlEJQ3SG69hnXPPS1@dpg-cv643oggph6c73djqm4g-a.oregon-postgres.render.com/supermarket_fm98"

# API setup
app = FastAPI()

# Enable CORS (Allows frontend apps to access API)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Root endpoint to verify API is working
@app.get("/")
def home():
    return {"message": "Supermarket Sales API is live 🚀"}

# ✅ Health Check Endpoint (Verify Database Connectivity)
@app.get("/health-check")
def health_check():
    try:
        conn = psycopg2.connect(DB_URL)
        conn.close()
        return JSONResponse(content={"status": "Database connected ✅"}, status_code=200)
    except Exception as e:
        return JSONResponse(content={"status": "Database connection failed ❌", "error": str(e)}, status_code=500)

# ✅ Fetch total sales per product
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

# ✅ Fetch total sales per customer type
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

# ✅ Fetch monthly sales trend
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

# ✅ Download the sales report PDF
@app.get("/download-report")
def download_report():
    report_path = os.path.join(os.getcwd(), "reports", "sales_report.pdf")
    if os.path.exists(report_path):
        return FileResponse(report_path, filename="sales_report.pdf", media_type="application/pdf")
    return JSONResponse(content={"error": "Report not found ❌"}, status_code=404)

# ✅ Run the API on Render
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))  # Get assigned port from Render
    uvicorn.run(app, host="0.0.0.0", port=port)
