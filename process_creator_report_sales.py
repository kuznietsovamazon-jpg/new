import pandas as pd
import os

# Define the file path
file_path = r'C:\Users\User\Downloads\reportId=amzn1.report.GQS6BM7WGMK7.csv'

# Check if the file exists
if not os.path.exists(file_path):
    print(f"Error: File not found at {file_path}")
else:
    # Read the csv file
    df = pd.read_csv(file_path)

    # Convert 'Date' column to datetime objects
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y')

    # Group by ASIN and Date and sum the Sales
    sales_by_asin = df.groupby(['ASIN', 'Date'])['Sales'].sum().reset_index()

    # Create a pivot table
    pivot_table = sales_by_asin.pivot_table(
        index='ASIN',
        columns='Date',
        values='Sales',
        aggfunc='sum',
        fill_value=0
    )

    # Save the pivot table to a new CSV file
    output_path = 'creator_report_sales_by_asin_daily_v2.csv'
    pivot_table.to_csv(output_path)

    print(f"Successfully created the daily creator sales report by ASIN: {output_path}")
