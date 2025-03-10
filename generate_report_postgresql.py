import psycopg2
import pandas as pd
import os
import matplotlib.pyplot as plt
from fpdf import FPDF
from datetime import datetime

# PostgreSQL connection details
DB_URL = "postgresql://supermarket_fm98_user:TMm5U0YeBBTLmNVYlEJQ3SG69hnXPPS1@dpg-cv643oggph6c73djqm4g-a.oregon-postgres.render.com/supermarket_fm98"

# Output directory
reports_dir = r"C:\10 March 66 Project\reports"
os.makedirs(reports_dir, exist_ok=True)

# PDF Report file path
pdf_file_path = os.path.join(reports_dir, "sales_report.pdf")

# Connect to PostgreSQL
conn = psycopg2.connect(DB_URL)

# Initialize PDF
pdf = FPDF()
pdf.set_auto_page_break(auto=True, margin=15)

# ---------------------- Function to Add Report to PDF ----------------------
def add_chart_to_pdf(title, chart_path):
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, title, ln=True, align="C")
    pdf.image(chart_path, x=10, y=30, w=180)
    pdf.ln(100)  # Space after image

def add_table_to_pdf(title, df):
    pdf.add_page()
    pdf.set_font("Arial", style="B", size=16)
    pdf.cell(200, 10, title, ln=True, align="C")
    pdf.ln(10)

    pdf.set_font("Arial", size=10)
    col_width = pdf.w / (len(df.columns) + 1)

    # Add Table Header
    pdf.set_fill_color(200, 200, 200)
    for col in df.columns:
        pdf.cell(col_width, 10, col, border=1, fill=True, align="C")
    pdf.ln()

    # Add Table Rows
    for _, row in df.iterrows():
        for value in row:
            pdf.cell(col_width, 10, str(value), border=1, align="C")
        pdf.ln()

# ---------------------- 1️⃣ Report: Total Sales Per Product ----------------------
query1 = """
SELECT p.product_line, SUM(s.total_price) AS total_sales
FROM sales s
JOIN products p ON s.product_id = p.product_id
GROUP BY p.product_line
ORDER BY total_sales DESC;
"""
df1 = pd.read_sql(query1, conn)

# Generate Bar Chart
chart1_path = os.path.join(reports_dir, "sales_per_product.png")
plt.figure(figsize=(10, 5))
plt.bar(df1['product_line'], df1['total_sales'], color='skyblue')
plt.xlabel("Product Line")
plt.ylabel("Total Sales")
plt.title("Total Sales Per Product")
plt.xticks(rotation=45)
plt.savefig(chart1_path)
plt.close()

# Add to PDF
add_chart_to_pdf("Total Sales Per Product", chart1_path)
add_table_to_pdf("Total Sales Per Product (Tabular Data)", df1)

# ---------------------- 2️⃣ Report: Total Sales Per Customer Type ----------------------
query2 = """
SELECT c.customer_type, SUM(s.total_price) AS total_sales
FROM sales s
JOIN customers c ON s.customer_id = c.customer_id
GROUP BY c.customer_type
ORDER BY total_sales DESC;
"""
df2 = pd.read_sql(query2, conn)

# Generate Pie Chart
chart2_path = os.path.join(reports_dir, "sales_per_customer_type.png")
plt.figure(figsize=(7, 7))
plt.pie(df2['total_sales'], labels=df2['customer_type'], autopct='%1.1f%%', colors=['lightcoral', 'lightblue'])
plt.title("Total Sales Per Customer Type")
plt.savefig(chart2_path)
plt.close()

# Add to PDF
add_chart_to_pdf("Total Sales Per Customer Type", chart2_path)
add_table_to_pdf("Total Sales Per Customer Type (Tabular Data)", df2)

# ---------------------- 3️⃣ Report: Monthly Sales Trend ----------------------
query3 = """
SELECT DATE_TRUNC('month', s.date) AS sales_month, SUM(s.total_price) AS total_sales
FROM sales s
GROUP BY sales_month
ORDER BY sales_month;
"""
df3 = pd.read_sql(query3, conn)

# Generate Line Chart
chart3_path = os.path.join(reports_dir, "monthly_sales_trend.png")
plt.figure(figsize=(10, 5))
plt.plot(df3['sales_month'], df3['total_sales'], marker='o', color='green', linestyle='-')
plt.xlabel("Month")
plt.ylabel("Total Sales")
plt.title("Monthly Sales Trend")
plt.xticks(rotation=45)
plt.grid()
plt.savefig(chart3_path)
plt.close()

# Add to PDF
add_chart_to_pdf("Monthly Sales Trend", chart3_path)
add_table_to_pdf("Monthly Sales Trend (Tabular Data)", df3)

# ---------------------- Save PDF ----------------------
pdf.output(pdf_file_path)

# Close connection
conn.close()

print(f"✅ Sales report generated successfully: {pdf_file_path}")
