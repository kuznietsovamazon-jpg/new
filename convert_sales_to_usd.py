
import pandas as pd

def convert_sales_to_usd(input_file, output_file, exchange_rate):
    """
    Reads a sales report, converts all monetary values from CAD to USD,
    and saves the result to a new file.
    """
    try:
        # Read the CSV file. The first column (ASIN) is the index.
        df = pd.read_csv(input_file, index_col=0)
        
        # Ensure all data is numeric, coercing errors
        # This handles any non-numeric data that might have slipped in
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce')
            
        # Multiply all sales figures by the exchange rate
        df_usd = df * exchange_rate
        
        # Format the numbers to 2 decimal places
        df_usd = df_usd.round(2)
        
        # Save the converted data to the new CSV file
        df_usd.to_csv(output_file)
        
        print(f"Successfully read '{input_file}'.")
        print(f"Converted sales to USD with an exchange rate of {exchange_rate}.")
        print(f"New report saved as '{output_file}'.")

    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    # Define the conversion parameters
    cad_to_usd_rate = 0.72
    sales_report_cad = 'pivoted_sales_report.csv'
    sales_report_usd = 'pivoted_sales_report_usd.csv'
    
    # Run the conversion function
    convert_sales_to_usd(sales_report_cad, sales_report_usd, cad_to_usd_rate)
