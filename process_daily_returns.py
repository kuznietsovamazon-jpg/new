import pandas as pd
import os

def process_daily_returns_report(file_path):
    """
    Processes the Amazon FBA Returns report to create a daily summary.

    - Reads the returns CSV file.
    - Converts 'return-date' to just the date.
    - Categorizes returns as 'SELLABLE' or 'UNSELLABLE'.
    - Creates a pivot table with ASIN and category as index, dates as columns,
      and sum of quantity as values.
    """
    try:
        # Try reading with different encodings
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp1251')

        # Convert 'return-date' to datetime and extract date part
        df['return-date'] = pd.to_datetime(df['return-date']).dt.date

        # Categorize returns
        df['return_category'] = df['detailed-disposition'].apply(
            lambda x: 'SELLABLE' if x == 'SELLABLE' else 'UNSELLABLE'
        )

        # Ensure quantity is numeric
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)

        # Create pivot table
        pivot_table = pd.pivot_table(
            df,
            values='quantity',
            index=['asin', 'return_category'],
            columns='return-date',
            aggfunc='sum',
            fill_value=0
        )

        # Save the pivot table
        output_filename = 'daily_returns_summary.csv'
        pivot_table.to_csv(output_filename)
        print(f"Successfully created daily returns summary and saved as '{output_filename}'")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    file_to_process = r"C:\Users\User\Downloads\367357020500.csv"
    process_daily_returns_report(file_to_process)
