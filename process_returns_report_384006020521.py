import pandas as pd
import os

def process_returns_report(file_path):
    """
    Processes the Amazon returns report to create a pivoted summary.

    Args:
        file_path (str): The path to the returns report CSV file.
    """
    try:
        # Try reading with utf-8-sig first
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except UnicodeDecodeError:
        # Fallback to cp1251 if utf-8-sig fails
        df = pd.read_csv(file_path, encoding='cp1251')

    # Convert 'return-date' to datetime and extract the date part
    df['return-date'] = pd.to_datetime(df['return-date']).dt.date

    # Create 'return_category'
    df['return_category'] = df['detailed-disposition'].apply(lambda x: 'SELLABLE' if x == 'SELLABLE' else 'UNSELLABLE')

    # Group by asin, return_category, and date, and sum the quantity
    daily_returns = df.groupby(['asin', 'return_category', 'return-date'])['quantity'].sum().reset_index()

    # Create the pivot table
    pivot_table = daily_returns.pivot_table(
        index=['asin', 'return_category'],
        columns='return-date',
        values='quantity',
        fill_value=0
    )

    # Get the directory and base name of the input file
    directory = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    file_name_without_ext = os.path.splitext(base_name)[0]

    # Create the output file path
    output_filename = f"daily_returns_summary_{file_name_without_ext}.csv"
    output_path = os.path.join(directory, output_filename)

    # Save the pivot table to a CSV file
    pivot_table.to_csv(output_path)
    print(f"Successfully created pivoted returns report: {output_path}")

if __name__ == "__main__":
    # The user provided this file path.
    file_to_process = r"C:\Users\User\Downloads\384006020521.csv"
    process_returns_report(file_to_process)
