import pandas as pd
import os

try:
    file_path = os.path.join('C:', os.sep, 'Users', 'User', 'Downloads', 'data_10_pivoted.xlsx')
    if not os.path.exists(file_path):
        print(f"Файл не найден: {file_path}")
    else:
        # Read the Excel file
        df = pd.read_excel(file_path, header=[0, 1], index_col=[0, 1])
        print("Вот предварительный просмотр созданной таблицы:")
        print(df.head(10).to_string())

except Exception as e:
    print(f"Произошла ошибка: {e}")
