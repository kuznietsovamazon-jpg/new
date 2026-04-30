import pandas as pd
import sys

def create_pivot_report(file_path, output_path):
    """
    Reads an Excel file, creates a pivot table with multiple values, 
    and saves it to a CSV file.
    """
    try:
        # The file path is passed as an argument, but we'll use the hardcoded one for now.
        file_path = r'C:\Users\User\Downloads\data (14).xlsx'
        
        # Read the 'Export' sheet from the Excel file
        df = pd.read_excel(file_path, sheet_name='Export')
        
        # --- Data Cleaning and Preparation ---
        
        # Convert 'Date' column to datetime objects, coercing errors to NaT
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
        
        # Drop rows where the date could not be parsed
        df.dropna(subset=['Date'], inplace=True)

        # Format date as YYYY-MM-DD
        df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')

        # Define the columns that should be numeric
        numeric_cols = ['Sales', 'Spend', 'Orders', 'Clicks']
        
        # Clean these numeric columns
        for col in numeric_cols:
            # Check if column is object type, which may indicate non-numeric characters
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(r'[$,]', '', regex=True)
            # Convert to numeric, setting errors to NaN
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Fill any NaN values in these key metrics with 0
        df[numeric_cols] = df[numeric_cols].fillna(0)

        # --- Pivoting ---
        
        # Define the metrics we want in our pivot table
        metrics_to_pivot = ['Sales', 'Spend', 'Orders', 'Clicks']
        
        # Create the pivot table. 
        # Using pivot_table with an aggfunc (like 'sum') handles duplicate entries for the same ASIN and Date.
        pivot_df = pd.pivot_table(df, 
                                  index='Child ASIN', 
                                  columns='Date', 
                                  values=metrics_to_pivot,
                                  aggfunc='sum')
                                  
        # The pivot operation creates multi-level columns, e.g., ('Sales', '2024-01-01'), ('Spend', '2024-01-01').
        # This structure keeps the requested metrics grouped under each date.
        
        # Save the resulting pivot table to a CSV file
        pivot_df.to_csv(output_path)
        
        print(f"Successfully created the pivot report and saved it to: {output_path}")

    except FileNotFoundError:
        print(f"Error: The file was not found at {file_path}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"Error: A required column is missing from the Excel file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Define the path for the output CSV file
    output_csv_path = r'C:\Users\User\pivoted_report.csv'
    # Call the function to create the report
    create_pivot_report(None, output_csv_path)
