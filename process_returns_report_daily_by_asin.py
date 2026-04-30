import pandas as pd
import re
import os

def process_returns_report_daily_by_asin(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='cp1251')

    # Convert 'return-date' to datetime and extract date only
    df['return-date'] = pd.to_datetime(df['return-date']).dt.date

    # Create 'return_category' column
    df['return_category'] = df['detailed-disposition'].apply(
        lambda x: 'SELLABLE' if x == 'SELLABLE' else 'UNSELLABLE'
    )

    # Group by ASIN, return_category, and return-date, then sum quantities
    grouped_df = df.groupby(['asin', 'return_category', 'return-date'])['quantity'].sum().reset_index()

    # Pivot the table
    pivot_df = grouped_df.pivot_table(
        index=['asin', 'return_category'],
        columns='return-date',
        values='quantity',
        fill_value=0
    )

    # Flatten the MultiIndex columns for better readability
    pivot_df.columns = [col.strftime('%Y-%m-%d') for col in pivot_df.columns]

    # Generate output file name
    base_name = os.path.basename(file_path)
    output_filename = f"daily_returns_summary_by_asin_and_category_{os.path.splitext(base_name)[0]}.csv"
    output_path = os.path.join(os.path.dirname(file_path), output_filename)

    pivot_df.to_csv(output_path)
    print(f"Processed returns report saved to: {output_path}")

# Define the path to the input file
input_file = 'C:/Users/User/Downloads/395210020535.csv'

# Process the report
process_returns_report_daily_by_asin(input_file)