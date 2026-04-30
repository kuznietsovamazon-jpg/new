import pandas as pd
import os

def process_combined_daily_returns(file_path):
    """
    Processes the Amazon FBA Returns report to create a combined daily summary
    for a specific date range.

    - Reads the returns CSV file.
    - Filters for dates between Feb 9 and Feb 15, 2026.
    - Creates a pivot table with ASIN as index, dates as columns,
      and sum of quantity as values (combining sellable/unsellable).
    """
    try:
        # Try reading with different encodings
        try:
            df = pd.read_csv(file_path, encoding='utf-8')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp1251')

        # Convert 'return-date' to datetime objects
        df['return-date'] = pd.to_datetime(df['return-date']).dt.date

        # Filter for the specified date range
        start_date = pd.to_datetime('2026-02-09').date()
        end_date = pd.to_datetime('2026-02-15').date()
        df = df[(df['return-date'] >= start_date) & (df['return-date'] <= end_date)]

        if df.empty:
            print("No data found in the specified date range (Feb 9 to Feb 15, 2026).")
            return

        # Ensure quantity is numeric
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)

        # Create pivot table (combined returns per ASIN)
        pivot_table = pd.pivot_table(
            df,
            values='quantity',
            index='asin',
            columns='return-date',
            aggfunc='sum',
            fill_value=0
        )

        # Save the pivot table
        output_filename = 'daily_returns_summary_combined_filtered.csv'
        pivot_table.to_csv(output_filename)
        print(f"Successfully created combined and filtered daily returns summary and saved as '{output_filename}'")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == '__main__':
    file_to_process = r"C:\Users\User\Downloads\367357020500.csv"
    process_combined_daily_returns(file_to_process)
