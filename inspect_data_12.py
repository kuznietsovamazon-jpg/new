import pandas as pd

def inspect_file(file_path):
    """
    Reads an Excel or CSV file and prints its columns and the first 5 rows.
    """
    try:
        # It's an .xlsx file, so we should primarily try to read it as Excel.
        # The 'openpyxl' engine is required for .xlsx files.
        df = pd.read_excel(file_path, engine='openpyxl')
        print(f"Successfully read as Excel file.")
        
    except Exception as e_excel:
        print(f"Could not read as Excel, attempting to read as CSV. Excel read error: {e_excel}")
        try:
            # Fallback to CSV if Excel reading fails
            df = pd.read_csv(file_path)
            print(f"Successfully read as CSV file.")
        except Exception as e_csv:
            print(f"Failed to read as both Excel and CSV. CSV read error: {e_csv}")
            return

    # Print the column names
    print(f"\n--- Columns in '{file_path}' ---")
    print(df.columns.tolist())
    
    # Print the first 5 rows of the dataframe
    print("\n--- First 5 rows ---")
    print(df.head())

if __name__ == "__main__":
    # Hardcode the file path to avoid command-line argument parsing issues
    file_to_inspect = r'C:\Users\User\Downloads\data (11).xlsx'
    inspect_file(file_to_inspect)