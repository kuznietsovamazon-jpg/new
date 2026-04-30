import pandas as pd
import os

def process_creator_report(file_path):
    """
    Processes a creator report to create a daily sales summary by ASIN.

    Args:
        file_path (str): The path to the creator report CSV file.
    """
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return
    except Exception as e:
        print(f"Error reading CSV file: {e}")
        return

    # Convert 'Date' to datetime and extract the date part
    try:
        df['Date'] = pd.to_datetime(df['Date'], format='%d-%b-%Y').dt.date
    except ValueError:
        try:
            df['Date'] = pd.to_datetime(df['Date']).dt.date
        except Exception as e:
            print(f"Error converting date column: {e}")
            return


    # Check if 'Sales' and 'ASIN' columns exist
    if 'Sales' not in df.columns or 'ASIN' not in df.columns:
        print("Error: 'Sales' or 'ASIN' column not found in the file.")
        return

    # Create pivot table for Sales
    sales_pivot = pd.pivot_table(
        df,
        index='ASIN',
        columns='Date',
        values='Sales',
        aggfunc='sum',
        fill_value=0
    )

    # Save the pivot table
    directory = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_filename = os.path.join(directory, f'{base_name}_sales_summary.csv')
    sales_pivot.to_csv(output_filename)
    print(f"Successfully created sales summary: {output_filename}")

    # Also create pivot for Orders
    if 'Orders' in df.columns:
        orders_pivot = pd.pivot_table(
            df,
            index='ASIN',
            columns='Date',
            values='Orders',
            aggfunc='sum',
            fill_value=0
        )
        output_filename_orders = os.path.join(directory, f'{base_name}_orders_summary.csv')
        orders_pivot.to_csv(output_filename_orders)
        print(f"Successfully created orders summary: {output_filename_orders}")



if __name__ == "__main__":
    input_file = r'C:\Users\User\Downloads\reportId=amzn1.report.53DP7YXE8SUU.csv'
    process_creator_report(input_file)

