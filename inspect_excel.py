import pandas as pd

def inspect_excel_columns(file_path):
    try:
        df = pd.read_excel(file_path, nrows=5)
        print("First 5 rows:")
        print(df)
        print("\nColumns:")
        print(df.columns.tolist())
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
    except Exception as e:
        print(f"Error reading Excel file: {e}")

if __name__ == "__main__":
    input_file = r'C:\Users\User\Downloads\Amazon_Attribution_Promoted_product_report (12).xlsx'
    inspect_excel_columns(input_file)

