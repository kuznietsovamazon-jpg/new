import pandas as pd
import numpy as np
import os

# Define file paths
file_path = r'C:\Users\User\Downloads\Amazon_Attribution_Promoted_product_report (5).xlsx'
output_path = r'C:\Users\User\attribution_sales_by_campaign_and_asin.csv'

try:
    # Load the Excel file
    df = pd.read_excel(file_path)

    # --- Identify Columns ---
    date_col = next((col for col in df.columns if 'date' in col.lower()), None)
    campaign_col = next((col for col in df.columns if 'campaign name' in col.lower()), None)
    sales_col = next((col for col in df.columns if '14 day product sales' in col.lower()), None)
    if not sales_col:
        sales_col = next((col for col in df.columns if 'sales' in col.lower()), None)
    # New: Find the Advertised ASIN column
    asin_col = next((col for col in df.columns if 'advertised asin' in col.lower()), None)

    if not all([date_col, campaign_col, sales_col, asin_col]):
        raise ValueError(f"Could not find all required columns. Found: Date='{date_col}', Campaign='{campaign_col}', Sales='{sales_col}', ASIN='{asin_col}'")

    # --- Data Cleaning and Preparation ---
    if df[sales_col].dtype == 'object':
        df[sales_col] = df[sales_col].replace({r'\$': '', ',': ''}, regex=True)
    df[sales_col] = pd.to_numeric(df[sales_col], errors='coerce')
    df.dropna(subset=[sales_col, asin_col], inplace=True)

    df[date_col] = pd.to_datetime(df[date_col]).dt.date

    # --- Grouping Logic ---
    df['Grouped Campaign'] = np.where(
        df[campaign_col].str.lower().str.startswith('adv', na=False),
        'Adv Campaigns',
        df[campaign_col]
    )

    # --- Pivoting (with new multi-level index) ---
    pivot_df = df.pivot_table(
        index=['Grouped Campaign', asin_col], # Changed index
        columns=date_col,
        values=sales_col,
        aggfunc='sum',
        fill_value=0
    )

    # --- Save the result ---
    pivot_df.to_csv(output_path)

    print(f"Processing complete. The new report with ASIN breakdown has been saved to: {output_path}")

except FileNotFoundError:
    print(f"Error: The file was not found at {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")
