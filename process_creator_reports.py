

import pandas as pd
import numpy as np
import os

# Define the file paths
file_paths = [
    r'C:\Users\User\Downloads\reportId=amzn1.report.2L4V9IDAOHRSJ.csv',
    r'C:\Users\User\Downloads\reportId=amzn1.report.26L1T6BKYMQ65.csv'
]
output_dir = r'C:\Users\User'

all_data = []

for file_path in file_paths:
    try:
        # Read the CSV file, handling potential encoding issues
        df = pd.read_csv(file_path, encoding='utf-8-sig')
        all_data.append(df)
    except FileNotFoundError:
        print(f"File not found: {file_path}")
    except Exception as e:
        print(f"Error reading {file_path}: {e}")

if not all_data:
    print("No data to process. Exiting.")
    exit()

# Concatenate all dataframes
combined_df = pd.concat(all_data, ignore_index=True)

# Clean column names (strip whitespace)
combined_df.columns = combined_df.columns.str.strip()

# Ensure required columns exist
required_columns = ['Date', 'ASIN', 'Spend', 'Clicks', 'Orders', 'Sales', 'Commission Rate']
for col in required_columns:
    if col not in combined_df.columns:
        print(f"Error: Required column '{col}' not found in the combined report.")
        exit()

# Convert 'Date' to datetime, handling '%d-%b-%Y' format
combined_df['Date'] = pd.to_datetime(combined_df['Date'], format='%d-%b-%Y', errors='coerce')

# Drop rows where 'Date' could not be parsed
combined_df.dropna(subset=['Date'], inplace=True)

# Clean and convert numeric columns
numeric_cols = ['Spend', 'Clicks', 'Orders', 'Sales', 'Commission Rate']
for col in numeric_cols:
    if combined_df[col].dtype == 'object':
        combined_df[col] = combined_df[col].astype(str).str.replace(r'[$,]', '', regex=True)
    combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').fillna(0)

# Calculate 'Commission Amount'
combined_df['Commission Amount'] = combined_df['Sales'] * (combined_df['Commission Rate'] / 100)

# Define metrics to pivot
metrics = {
    'Sales': 'Total_Creator_Sales_by_ASIN.csv',
    'Orders': 'Total_Creator_Orders_by_ASIN.csv',
    'Clicks': 'Total_Creator_Clicks_by_ASIN.csv',
    'Spend': 'Total_Creator_Spend_by_ASIN.csv',
    'Commission Amount': 'Total_Creator_Commission_by_ASIN.csv'
}

# Generate and save pivot tables
for metric, output_filename in metrics.items():
    pivot_table = pd.pivot_table(
        combined_df,
        values=metric,
        index='ASIN',
        columns='Date',
        aggfunc=np.sum,
        fill_value=0
    )
    # Sort columns by date
    pivot_table = pivot_table.reindex(columns=sorted(pivot_table.columns))

    output_path = os.path.join(output_dir, output_filename)
    pivot_table.to_csv(output_path)
    print(f"Successfully created pivot table for {metric} at: {output_path}")

