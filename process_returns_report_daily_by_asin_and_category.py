import pandas as pd
import re
from datetime import datetime

def process_returns_report_daily_by_asin_and_category(file_path):
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

    # Group by ASIN, return_category, and return-date, then sum quantity
    grouped_df = df.groupby(['asin', 'return_category', 'return-date'])['quantity'].sum().reset_index()

    # Pivot the table
    pivot_table = grouped_df.pivot_table(
        index=['asin', 'return_category'],
        columns='return-date',
        values='quantity',
        fill_value=0
    )

    # Flatten multi-index columns for better CSV output
    pivot_table.columns = [col.strftime('%Y-%m-%d') for col in pivot_table.columns]

    # Extract filename for output
    file_name_match = re.search(r'(\d+)\.csv$', file_path)
    if file_name_match:
        original_file_id = file_name_match.group(1)
        output_filename = f"daily_returns_summary_by_asin_and_category_{original_file_id}.csv"
    else:
        output_filename = "daily_returns_summary_by_asin_and_category.csv"

    output_path = f"C:/Users/User/{output_filename}"
    pivot_table.to_csv(output_path)
    print(f"Pivoted returns report saved to {output_path}")

# Example usage:
file_path = "C:/Users/User/Downloads/378439020514.csv"
process_returns_report_daily_by_asin_and_category(file_path)