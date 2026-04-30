import pandas as pd
import os

def process_returns_report_daily_by_asin_and_category(file_path):
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='cp1251')

    # Convert 'return-date' to datetime and extract date only
    df['return-date'] = pd.to_datetime(df['return-date']).dt.date

    # Categorize returns
    df['return_category'] = df['detailed-disposition'].apply(
        lambda x: 'SELLABLE' if x == 'SELLABLE' else 'UNSELLABLE'
    )

    # Group by ASIN, return_category, and return-date, then sum quantity
    grouped_df = df.groupby(['asin', 'return_category', 'return-date'])['quantity'].sum().reset_index()

    # Pivot the table
    pivot_df = grouped_df.pivot_table(
        index=['asin', 'return_category'],
        columns='return-date',
        values='quantity',
        fill_value=0
    )

    # Flatten the columns for better readability if needed, or keep as is for multi-index columns
    # For this specific request, multi-index columns (dates) are desired.

    # Create output filename
    base_name = os.path.basename(file_path)
    output_filename = f"daily_returns_summary_by_asin_and_category_{os.path.splitext(base_name)[0]}.csv"
    output_path = os.path.join(os.path.dirname(file_path), output_filename)

    pivot_df.to_csv(output_path)
    print(f"Daily returns summary by ASIN and category saved to: {output_path}")

# Example usage:
file_path = r"C:\Users\User\Downloads\422818020570.csv"
process_returns_report_daily_by_asin_and_category(file_path)