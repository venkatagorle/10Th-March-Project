import kaggle
import pandas as pd

# Download dataset
dataset = "aungpyaeap/supermarket-sales"
kaggle.api.dataset_download_files(dataset, path="./data", unzip=True)

# Load into DataFrame
df = pd.read_csv("./data/supermarket_sales.csv")
print(df.head())  # Preview data
