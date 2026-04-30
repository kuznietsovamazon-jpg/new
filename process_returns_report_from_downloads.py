import pandas as pd
import os

def process_returns_report(file_path):
    """
    Processes the returns report to create a daily summary by ASIN and return category.

    Args:
        file_path (str): The path to the returns report CSV file.
    """
    try:
        df = pd.read_csv(file_path, encoding='utf-8')
    except UnicodeDecodeError:
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp1251')

    # Convert 'return-date' to datetime and extract date
    df['return-date'] = pd.to_datetime(df['return-date']).dt.date

    # Categorize returns
    df['return_category'] = df['detailed-disposition'].apply(lambda x: 'SELLABLE' if x == 'SELLABLE' else 'UNSELLABLE')

    # Group and pivot
    pivot_df = df.pivot_table(
        index=['asin', 'return_category'],
        columns='return-date',
        values='quantity',
        aggfunc='sum',
        fill_value=0
    )

    # Save the output
    output_filename = 'daily_returns_summary_by_asin_and_category.csv'
    pivot_df.to_csv(output_filename)
    print(f"Processed returns report saved to {output_filename}")

if __name__ == "__main__":
    file_to_process = r"C:\Users\User\Downloads\374333020509.csv"
    if os.path.exists(file_to_process):
        process_returns_report(file_to_process)
    else:
        print(f"File not found: {file_to_process}")
