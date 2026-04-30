import pandas as pd
import re
import os

def process_returns_report_daily(file_path):
    """
    Processes a returns report CSV file to create a daily summary pivoted by ASIN and return category.

    Args:
        file_path (str): The absolute path to the returns report CSV file.

    Returns:
        pd.DataFrame: A pivot table with dates as columns and (ASIN, return_category) as multi-index rows.
    """
    try:
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except UnicodeDecodeError:
        df = pd.read_csv(file_path, encoding='cp1251')

    # Convert 'return-date' to datetime and extract date only
    df['return-date'] = pd.to_datetime(df['return-date']).dt.date

    # Categorize returns as 'SELLABLE' or 'UNSELLABLE'
    df['return_category'] = df['detailed-disposition'].apply(
        lambda x: 'SELLABLE' if x == 'SELLABLE' else 'UNSELLABLE'
    )

    # Group by ASIN, return category, and date, then sum quantities
    grouped_df = df.groupby(['asin', 'return_category', 'return-date'])['quantity'].sum().reset_index()

    # Create a pivot table
    pivot_table = grouped_df.pivot_table(
        index=['asin', 'return_category'],
        columns='return-date',
        values='quantity',
        fill_value=0
    )

    # Flatten the MultiIndex columns for better readability if needed, or keep as is
    # pivot_table.columns = [col.strftime('%Y-%m-%d') for col in pivot_table.columns]

    return pivot_table

if __name__ == "__main__":
    # Define the path to the input file
    input_file = r"C:\Users\User\Downloads\378442020514.csv"
    output_file = r"C:\Users\User\daily_returns_summary_by_asin_and_category_378442020514.csv"

    # Process the report
    daily_returns_pivot = process_returns_report_daily(input_file)

    # Save the output to a CSV file
    daily_returns_pivot.to_csv(output_file)

    print(f"Daily returns summary saved to {output_file}")