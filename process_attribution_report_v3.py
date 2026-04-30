import pandas as pd
import numpy as np
import os

def process_attribution_report(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"Error: File not found at {file_path}")
        return

    # Read the Excel file
    df = pd.read_excel(file_path)

    # Data Cleaning: Remove '$' and ',' from numeric columns and convert to float
    numeric_cols = ['14 Day Product Sales'] # Assuming this is the primary sales metric
    for col in numeric_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Convert 'Date' column to datetime objects
    df['Date'] = pd.to_datetime(df['Date'])

    # Filtering: Advertiser Country == 'US' if column exists
    if 'Advertiser Country' in df.columns:
        df = df[df['Advertiser Country'] == 'US']

    # --- Campaign Grouping Logic ---
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

    # Create output filenames based on the input file
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_path_main = os.path.join(os.path.dirname(file_path), f"{base_name}_by_asin_and_campaign.csv")
    output_path_adv = os.path.join(os.path.dirname(file_path), f"{base_name}_adv_campaigns.csv")

    # Save the main pivot table
    pivot_table.to_csv(output_path_main)
    print(f"Successfully created main report: {output_path_main}")

    # --- Filter for 'Adv Campaigns' and Create Second Report ---
    # Check if 'Adv Campaigns' exists in the index before filtering
    if 'Adv Campaigns' in pivot_table.index.get_level_values('Grouped_Campaign_Name'):
        adv_pivot_table = pivot_table[pivot_table.index.get_level_values('Grouped_Campaign_Name') == 'Adv Campaigns']
        # Save the 'Adv Campaigns' filtered report
        adv_pivot_table.to_csv(output_path_adv)
        print(f"Successfully created 'Adv Campaigns' report: {output_path_adv}")
    else:
        print(f"No 'Adv Campaigns' found in {file_path}. Skipping 'Adv Campaigns' report generation.")

# Example usage:
file_path = r"C:\Users\User\Downloads\Amazon_Attribution_Promoted_product_report (24).xlsx"
process_attribution_report(file_path)
