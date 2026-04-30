import pandas as pd
import os

def process_returns_report(file_path):
    """
    Processes the returns report to create a daily summary by ASIN and return category.

    Args:
        file_path (str): The path to the returns CSV file.
    """
    try:
        # Try reading with utf-8-sig first to handle BOM
        df = pd.read_csv(file_path, encoding='utf-8-sig')
    except (UnicodeDecodeError, FileNotFoundError):
        try:
            # Fallback to cp1251 if utf-8 fails
            df = pd.read_csv(file_path, encoding='cp1251')
        except FileNotFoundError:
            print(f"Error: The file was not found at {file_path}")
            return
        except Exception as e:
            print(f"An error occurred while reading the file: {e}")
            return


    # Convert 'return-date' to datetime and extract the date part
    df['return-date'] = pd.to_datetime(df['return-date']).dt.date

    # Categorize returns as 'Sellable' or 'Unsellaable'
    df['return_category'] = df['detailed-disposition'].apply(lambda x: 'SELLABLE' if x == 'SELLABLE' else 'UNSELLABLE')

    # Group by ASIN, date, and return category, then count the quantity
    daily_summary = df.groupby(['asin', 'return-date', 'return_category'])['quantity'].sum().reset_index()

    # Create the pivot table
    pivot_table = daily_summary.pivot_table(
        index=['asin', 'return_category'],
        columns='return-date',
        values='quantity',
        fill_value=0
    )

    # Get the directory and base name of the input file
    directory = os.path.dirname(file_path)
    base_name = os.path.basename(file_path)
    file_name_without_ext = os.path.splitext(base_name)[0]

    # Define the output file path
    output_filename = os.path.join(directory, f'{file_name_without_ext}_daily_returns_summary_by_asin.csv')

    # Save the pivot table to a CSV file
    pivot_table.to_csv(output_filename)
    print(f"Successfully created daily returns summary: {output_filename}")

if __name__ == "__main__":
    # Path to the input file
    input_file = r'C:\Users\User\Downloads\372845020507.csv'
    process_returns_report(input_file)
