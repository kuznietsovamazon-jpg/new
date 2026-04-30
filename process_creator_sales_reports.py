import pandas as pd
import glob

# Define the file paths from the user's request
file_paths = [
    r'C:\Users\User\Downloads\reportId=amzn1.report.OKKN0G216EK1.csv',
    r'C:\Users\User\Downloads\reportId=amzn1.report.1JJT8MYK77BPC.csv'
]

output_file = 'creator_report_sales_summary.csv'

try:
    # Read and combine all specified CSV files
    df_list = [pd.read_csv(file) for file in file_paths]
    combined_df = pd.concat(df_list, ignore_index=True)

    # --- Data Cleaning and Preparation ---

    # Convert 'Date' column to datetime objects, handling the specific format like '19-Feb-2026'
    combined_df['Date'] = pd.to_datetime(combined_df['Date'], format='%d-%b-%Y')

    # Ensure 'Sales' is a numeric column, coercing errors
    combined_df['Sales'] = pd.to_numeric(combined_df['Sales'], errors='coerce').fillna(0)
    
    # Ensure 'ASIN' is a string to avoid any formatting issues
    combined_df['ASIN'] = combined_df['ASIN'].astype(str)

    # --- Pivot Table Creation ---

    # Group by ASIN and Date, summing the Sales
    # This is more robust than pivot_table if there are multiple entries that need summing before pivoting
    daily_sales = combined_df.groupby(['ASIN', 'Date'])['Sales'].sum().reset_index()

    # Create the pivot table for the final report
    sales_pivot = daily_sales.pivot_table(
        index='ASIN',
        columns='Date',
        values='Sales',
        aggfunc='sum',
        fill_value=0
    )

    # --- Save Output ---
    sales_pivot.to_csv(output_file)

    print(f"Successfully combined {len(file_paths)} files and created the sales summary pivot table.")
    print(f"Output saved to: {output_file}")

except FileNotFoundError as e:
    print(f"Error: File not found - {e.filename}")
except Exception as e:
    print(f"An error occurred: {e}")