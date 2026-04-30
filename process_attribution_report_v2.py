import pandas as pd
import numpy as np
import os

# Define the file path
file_path = r'C:\Users\User\Downloads\Amazon_Attribution_Promoted_product_report (7).xlsx'

# Check if the file exists
if not os.path.exists(file_path):
    print(f"Error: File not found at {file_path}")
else:
    # Read the Excel file
    df = pd.read_excel(file_path)

    # Convert 'Date' column to datetime objects
    df['Date'] = pd.to_datetime(df['Date'])

    # --- Grouping Logic ---
    # Create the 'Grouped_Campaign_Name' column
    df['Grouped_Campaign_Name'] = np.where(
        df['Campaign Name'].str.lower().str.startswith('adv'),
        'Adv Campaigns',
        df['Campaign Name']
    )

    # Define the metric
    sales_metric = '14 Day Product Sales'

    # --- Create Main Pivot Table ---
    pivot_table = pd.pivot_table(
        df,
        values=sales_metric,
        index=['Advertised ASIN', 'Grouped_Campaign_Name'],
        columns=['Date'],
        aggfunc='sum',
        fill_value=0
    )

    # Save the main pivot table
    output_path_main = 'attribution_sales_by_campaign_and_asin_v2.csv'
    pivot_table.to_csv(output_path_main)
    print(f"Successfully created main report: {output_path_main}")

    # --- Filter for 'Adv Campaigns' and Create Second Report ---
    adv_pivot_table = pivot_table[pivot_table.index.get_level_values('Grouped_Campaign_Name') == 'Adv Campaigns']

    # Save the 'Adv Campaigns' filtered report
    output_path_adv = 'attribution_sales_by_adv_campaign_v2.csv'
    adv_pivot_table.to_csv(output_path_adv)
    print(f"Successfully created 'Adv Campaigns' report: {output_path_adv}")
