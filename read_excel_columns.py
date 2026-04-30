import pandas as pd

try:
    df = pd.read_excel(r'C:\Users\User\Downloads\data (18).xlsx')
    print(df.columns.tolist())
except Exception as e:
    print(f"Error reading Excel file: {e}")