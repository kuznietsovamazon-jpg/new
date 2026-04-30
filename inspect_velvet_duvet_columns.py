import pandas as pd
import os

file_path = r"C:\Users\User\Desktop\Description\Velvet-Pinsonic-DuvetSet Decsription.xlsx"

if os.path.exists(file_path):
    try:
        df = pd.read_excel(file_path)
        print(f"Columns in {os.path.basename(file_path)}:")
        for col in df.columns:
            print(f"- {col}")
        if not df.empty:
            print("\nFirst 5 rows:")
            print(df.head())
        else:
            print("\nDataFrame is empty.")
    except Exception as e:
        print(f"Error reading {os.path.basename(file_path)}: {e}")
else:
    print(f"File not found: {file_path}")
