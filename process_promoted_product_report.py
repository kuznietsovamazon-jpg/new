import pandas as pd
import numpy as np

# Define the file path and output file names
file_path = r'C:\Users\User\Downloads\Amazon_Attribution_Promoted_product_report (16).xlsx'
output_pivot_path = 'promoted_product_report_by_asin_and_campaign_16.csv'
output_adv_campaigns_path = 'promoted_product_report_adv_campaigns_16.csv'
output_adv_campaigns_total_path = 'promoted_product_report_adv_campaigns_total_16.csv'

try:
    # Read the Excel file
    df = pd.read_excel(file_path)

    # --- Data Cleaning and Preparation ---

    # Convert 'Date' column to datetime objects
    # The date format is assumed to be standard, if not, a format string is needed
    df['Date'] = pd.to_datetime(df['Date']).dt.date

    # Clean the sales column to handle '$' and ','
    sales_column = '14 Day Product Sales'
    if sales_column in df.columns:
        df[sales_column] = df[sales_column].replace({r'\$': '', ',': ''}, regex=True).astype(float)
    else:
        raise ValueError(f"Sales column '{sales_column}' not found in the file.")

    # --- Grouping Logic ---

    # Create a new column for grouped campaign names
    # If 'Campaign Name' starts with 'adv' (case-insensitive), group it, otherwise keep the original name
    df['Grouped_Campaign_Name'] = np.where(
        df['Campaign Name'].str.lower().str.startswith('adv', na=False),
        'Adv Campaigns',
        df['Campaign Name']
    )

    # --- Main Pivot Table ---

    # Create a pivot table with ASIN and the new grouped campaign name
    pivot_table = df.pivot_table(
        index=['Advertised ASIN', 'Grouped_Campaign_Name'],
        columns='Date',
        values=sales_column,
        aggfunc='sum',
        fill_value=0
    )

    # Save the main pivot table to a CSV file
    pivot_table.to_csv(output_pivot_path)
    print(f"Successfully created pivot table: {output_pivot_path}")

    # --- "Adv Campaigns" Filtered Report ---

    # Filter the DataFrame for "Adv Campaigns"
    adv_campaigns_df = df[df['Grouped_Campaign_Name'] == 'Adv Campaigns']

    if not adv_campaigns_df.empty:
        # Create a pivot table for just "Adv Campaigns"
        adv_pivot = adv_campaigns_df.pivot_table(
            index='Advertised ASIN',
            columns='Date',
            values=sales_column,
            aggfunc='sum',
            fill_value=0
        )

        # Save the "Adv Campaigns" pivot table
        adv_pivot.to_csv(output_adv_campaigns_path)
        print(f"Successfully created 'Adv Campaigns' report: {output_adv_campaigns_path}")

        # --- "Adv Campaigns" Total Report ---

        # Calculate the total for "Adv Campaigns" by summing up the adv_pivot
        adv_total = adv_pivot.sum(axis=0).to_frame().T
        adv_total.index = ['Total Adv Campaigns Sales']

        # Save the total report
        adv_total.to_csv(output_adv_campaigns_total_path)
        print(f"Successfully created 'Adv Campaigns' total report: {output_adv_campaigns_total_path}")
    else:
        print("No 'Adv Campaigns' found to create filtered reports.")

except FileNotFoundError:
    print(f"Error: The file was not found at {file_path}")
except Exception as e:
    print(f"An error occurred: {e}")