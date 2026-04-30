

import pandas as pd

def inspect_excel_file():
    """
    Reads an Excel file and prints its columns and the first 5 rows
    to understand its structure.
    """
    file_path = r'C:\Users\User\Downloads\data (15).xlsx'
    try:
        # Read the first sheet of the Excel file
        df = pd.read_excel(file_path, sheet_name=0)
        
        print("--- Структура файла ---")
        print("Столбцы:", df.columns.tolist())
        print("\n--- Первые 5 строк ---")
        print(df.head())
        print("\n----------------------")
        
    except Exception as e:
        print(f"Произошла ошибка при чтении файла: {e}")

if __name__ == "__main__":
    inspect_excel_file()

