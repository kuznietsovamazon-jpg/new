import pandas as pd
import re

def process_attribution_report(file_path):
    # Load the Excel file
    df = pd.read_excel(file_path)

    # Clean column names
    df.columns = df.columns.str.strip()

    # Convert 'Date' column to datetime objects
    # Assuming 'Date' column exists and is in a parseable format
    # If the date is part of a range, we need to extract the end date.
    # For attribution reports, 'Date' usually refers to the start date of the attribution window.
    # Let's assume 'Date' is a single date column for now.
    if 'Date' in df.columns:
        df['Date'] = pd.to_datetime(df['Date'])
    else:
        # Attempt to find a date-like column if 'Date' is not present
        date_cols = [col for col in df.columns if 'date' in col.lower()]
        if date_cols:
            df[date_cols[0]] = pd.to_datetime(df[date_cols[0]])
            df = df.rename(columns={date_cols[0]: 'Date'})
        else:
            print("Warning: No 'Date' column found. Date-based pivoting might not work as expected.")
            # If no date column, we might need to infer it or use a placeholder
            df['Date'] = pd.to_datetime('today').normalize() # Placeholder for now

    # Clean and convert '14 Day Product Sales' to numeric
    if '14 Day Product Sales' in df.columns:
        df['14 Day Product Sales'] = df['14 Day Product Sales'].astype(str).str.replace('$', '').str.replace(',', '').astype(float)
    else:
        print("Warning: '14 Day Product Sales' column not found.")
        df['14 Day Product Sales'] = 0.0 # Default to 0 if not found

    # Filter for 'Marketplace == 'US''
    if 'Marketplace' in df.columns:
        df = df[df['Marketplace'] == 'AMAZON.COM']
    else:
        print("Warning: 'Marketplace' column not found. Skipping country filter.")

    # Create 'Grouped_Campaign_Name'
    df['Grouped_Campaign_Name'] = df['Campaign Name'].apply(
        lambda x: 'Adv Campaigns' if isinstance(x, str) and x.lower().startswith('adv') else x
    )

    # Create the main pivot table
    pivot_all_campaigns = pd.pivot_table(
        df,
        values='14 Day Product Sales',
        index=['Advertised ASIN', 'Grouped_Campaign_Name'],
        columns='Date',
        aggfunc='sum'
    )
    
    # Fill NaN values with 0 for better readability in sales reports
    pivot_all_campaigns = pivot_all_campaigns.fillna(0)

    # Create the "Adv Campaigns" specific pivot table
    df_adv_campaigns = df[df['Grouped_Campaign_Name'] == 'Adv Campaigns']
    pivot_adv_campaigns = pd.pivot_table(
        df_adv_campaigns,
        values='14 Day Product Sales',
        index=['Advertised ASIN', 'Grouped_Campaign_Name'],
        columns='Date',
        aggfunc='sum'
    )
    
    # Fill NaN values with 0
    pivot_adv_campaigns = pivot_adv_campaigns.fillna(0)

    # Save the pivot tables to CSV files
    output_base_name = file_path.split('\\')[-1].replace('.xlsx', '')
    output_all_campaigns_path = f"{output_base_name}_by_asin_and_campaign.csv"
    output_adv_campaigns_path = f"{output_base_name}_adv_campaigns.csv"

    pivot_all_campaigns.to_csv(output_all_campaigns_path)
    pivot_adv_campaigns.to_csv(output_adv_campaigns_path)

    print(f"Generated: {output_all_campaigns_path}")
    print(f"Generated: {output_adv_campaigns_path}")

# Example usage:
file_path = r'C:\Users\User\Downloads\Amazon_Attribution_Promoted_product_report (22).xlsx'
process_attribution_report(file_path)
