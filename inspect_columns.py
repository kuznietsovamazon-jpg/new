import pandas as pd

try:
    # Read the Excel file
    df = pd.read_excel(r'C:\Users\User\Downloads\data (15).xlsx')
    
    # Print the columns
    print("Столбцы в файле 'data (15).xlsx':")
    for col in df.columns:
        print(f"- {col}")

except FileNotFoundError:
    print("Ошибка: Файл 'data (15).xlsx' не найден.")
except Exception as e:
    print(f"Произошла ошибка: {e}")