import sqlite3
import pandas as pd
import os
import matplotlib.pyplot as plt
from fpdf import FPDF

# Define working directory
working_dir = r"C:\10 March 66 Project"
output_dir = os.path.join(working_dir, "output_reports")

# Ensure output directory exists
os.makedirs(output_dir, exist_ok=True)

# Path to SQLite database
db_path = os.path.join(working_dir, "sqlite_database.db")

# Connect to SQLite database
conn = sqlite3.connect(db_path)

# Define SQL query for report generation
report_query = """
SELECT 
    c.customer_name, 
    p.product_name, 
    SUM(s.total_price) AS total_spent,
    RANK() OVER (ORDER BY SUM(s.total_price) DESC) AS customer_rank
FROM Sales s
JOIN Customers c ON s.customer_id = c.customer_id
JOIN Products p ON s.product_id = p.product_id
GROUP BY c.customer_name, p.product_name
ORDER BY total_spent DESC;
"""

# Execute query and store results in DataFrame
report_df = pd.read_sql_query(report_query, conn)

# Close database connection
conn.close()

# Save the report as CSV
csv_output_path = os.path.join(output_dir, "sales_report.csv")
report_df.to_csv(csv_output_path, index=False)

# ------------------ Generate Charts ------------------

# Pie Chart: Sales Distribution by Product
plt.figure(figsize=(6, 6))
product_sales = report_df.groupby("product_name")["total_spent"].sum()
plt.pie(product_sales, labels=product_sales.index, autopct='%1.1f%%', startangle=140, colors=["#ff9999", "#66b3ff", "#99ff99", "#ffcc99"])
plt.title("Total Sales Distribution by Product")
pie_chart_path = os.path.join(output_dir, "pie_chart.png")
plt.savefig(pie_chart_path)
plt.close()

# Bar Chart: Top Customers by Spending
plt.figure(figsize=(8, 5))
top_customers = report_df.groupby("customer_name")["total_spent"].sum().nlargest(5)
top_customers.plot(kind='bar', color="#4285F4")
plt.title("Top 5 Customers by Total Spending")
plt.xlabel("Customer Name")
plt.ylabel("Total Spending")
plt.xticks(rotation=45)
bar_chart_path = os.path.join(output_dir, "bar_chart.png")
plt.savefig(bar_chart_path)
plt.close()

# ------------------ Generate PDF Report ------------------

class PDFReport(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(200, 10, "Sales Report", ln=True, align="C")

    def footer(self):
        self.set_y(-15)
        self.set_font("Arial", "I", 10)
        self.cell(0, 10, f"Page {self.page_no()}", align="C")

# Create PDF instance
pdf = PDFReport()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Arial", "", 12)

# Add Summary Table
pdf.cell(200, 10, "Top Customers by Spending", ln=True, align="C")
pdf.ln(5)

# Add Table Headers
pdf.set_font("Arial", "B", 10)
pdf.cell(60, 10, "Customer Name", 1)
pdf.cell(60, 10, "Product Name", 1)
pdf.cell(40, 10, "Total Spent", 1, ln=True)

# Add Table Data
pdf.set_font("Arial", "", 10)
for _, row in report_df.head(10).iterrows():
    pdf.cell(60, 10, row["customer_name"], 1)
    pdf.cell(60, 10, row["product_name"], 1)
    pdf.cell(40, 10, f"${row['total_spent']:.2f}", 1, ln=True)

# Add Pie Chart to PDF
pdf.ln(10)
pdf.cell(200, 10, "Sales Distribution by Product", ln=True, align="C")
pdf.image(pie_chart_path, x=30, w=150)

# Add Bar Chart to PDF
pdf.add_page()
pdf.cell(200, 10, "Top 5 Customers by Spending", ln=True, align="C")
pdf.image(bar_chart_path, x=30, w=150)

# Save the PDF Report
pdf_output_path = os.path.join(output_dir, "sales_report.pdf")
pdf.output(pdf_output_path)

print(f"\nReport saved successfully at: {pdf_output_path}")
