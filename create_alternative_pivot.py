import pandas as pd
import sys

def create_alternative_pivot_report(file_path, output_path):
    """
    Reads an Excel file, converts sales to USD, melts it to a long format, 
    and then creates a pivot table with a multi-level index (ASIN, Metric) 
    and dates as columns.
    """
    try:
        # Hardcoding the file path as per user's context
        file_path = r'C:\Users\User\Downloads\data (14).xlsx'
        
        # Read the specified sheet
        df = pd.read_excel(file_path, sheet_name='Export')
        
        # --- Data Cleaning and Preparation ---
        
        # Convert 'Date' column to datetime and format it, handling potential errors
        df['Date'] = pd.to_datetime(df['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        
        # Drop rows where essential identifiers are missing
        df.dropna(subset=['Date', 'Child ASIN'], inplace=True)

        # Define the metrics to be processed
        metrics = ['Sales', 'Spend', 'Orders', 'Clicks']
        
        # Clean numeric columns
        for col in metrics:
            if df[col].dtype == 'object':
                df[col] = df[col].astype(str).str.replace(r'[$,]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Fill any resulting NaN values in metrics with 0
        df[metrics] = df[metrics].fillna(0)

        # --- Currency Conversion ---
        # Using the rate 1 CAD = 0.72 USD from 2026-01-14
        cad_to_usd_rate = 0.72 
        df['Sales'] = df['Sales'] * cad_to_usd_rate

        # --- Melting ---
        
        # Before melting, aggregate data to ensure one row per ASIN per day
        df_agg = df.groupby(['Child ASIN', 'Date'])[metrics].sum().reset_index()

        # Unpivot the dataframe from wide to long format
        melted_df = df_agg.melt(
            id_vars=['Child ASIN', 'Date'],
            value_vars=metrics,
            var_name='Metric', # This new column will hold 'Sales', 'Spend', etc.
            value_name='Value'
        )

        # --- Pivoting ---
        
        # Create the final pivot table from the long-format data
        final_pivot = melted_df.pivot_table(
            index=['Child ASIN', 'Metric'], # Create a multi-level index
            columns='Date',
            values='Value',
            aggfunc='sum' # Use sum to handle any aggregation needs
        )
        
        # Sort the index to keep metrics grouped under each ASIN
        final_pivot.sort_index(inplace=True)

        # Save the final pivot table to the specified output CSV file
        final_pivot.to_csv(output_path)
        
        print(f"Successfully created the alternative pivot report at: {output_path}")

    except FileNotFoundError:
        print(f"Error: File not found at {file_path}", file=sys.stderr)
        sys.exit(1)
    except KeyError as e:
        print(f"Error: A required column is missing from the Excel file: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    # Define the output path for the new report
    output_csv_path = r'C:\Users\User\pivoted_report_alternative.csv'
    # Execute the function
    create_alternative_pivot_report(None, output_csv_path)
