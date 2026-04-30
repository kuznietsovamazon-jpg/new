import pandas as pd

file_path = r'C:\Users\User\Downloads\data (5).xlsx'

try:
    # Read the file without assuming any header structure to see the raw data
    df = pd.read_excel(file_path, header=None)
    
    print("--- Raw File Content (first 10 rows) ---")
    print(df.head(10).to_string())
    
    # Also try to read with a header to see what pandas identifies as column names
    print("\n--- Identified Column Names (assuming first row is header) ---")
    df_header = pd.read_excel(file_path)
    print(df_header.columns.tolist())

except Exception as e:
    print(f"An error occurred: {e}")
