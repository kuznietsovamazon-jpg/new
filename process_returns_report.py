import pandas as pd
import re

def process_returns_report(file_path):
    """
    Processes an Amazon Returns Report to categorize returns as 'SELLABLE' or 'UNSELLABLE'
    and generates a pivoted table with daily quantities by ASIN and return category.

    Args:
        file_path (str): The absolute path to the returns CSV file.

    Returns:
        pandas.DataFrame: A pivoted DataFrame with dates as columns and
                          (ASIN, return_category) as multi-index rows,
                          showing the sum of quantities.
    """
    try:
        # Read the CSV file with utf-8-sig encoding to handle BOM
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except UnicodeDecodeError:
        # Fallback to cp1251 if utf-8-sig fails
        df = pd.read_csv(file_path, encoding='cp1251')

    # Convert 'return-date' to datetime objects and extract only the date
    df['return-date'] = pd.to_datetime(df['return-date']).dt.date

    # Categorize returns as 'SELLABLE' or 'UNSELLABLE'
    df['return_category'] = df['detailed-disposition'].apply(
        lambda x: 'SELLABLE' if x == 'SELLABLE' else 'UNSELLABLE'
    )

    # Ensure 'quantity' is numeric
    df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)

    # Group by ASIN, return_category, and return-date, then sum quantities
    grouped_df = df.groupby(['asin', 'return_category', 'return-date'])['quantity'].sum().reset_index()

    # Pivot the table to have dates as columns and (ASIN, return_category) as multi-index rows
    pivot_df = grouped_df.pivot_table(
        index=['asin', 'return_category'],
        columns='return-date',
        values='quantity',
        fill_value=0
    )

    # Flatten the MultiIndex columns for better readability if needed, or keep as is
    # For this request, keeping as is for clarity of daily breakdown.
    # pivot_df.columns = [col.strftime('%Y-%m-%d') for col in pivot_df.columns]

    return pivot_df

if __name__ == "__main__":
    # Example usage:
    # Replace with the actual path to your returns report file
    file_path = r"C:\Users\User\Downloads\373557020508.csv"
    output_file_name = "daily_returns_summary_by_asin.csv"

    processed_df = process_returns_report(file_path)

    if processed_df is not None:
        processed_df.to_csv(output_file_name)
        print(f"Processed returns report saved to {output_file_name}")
        print(processed_df.head())