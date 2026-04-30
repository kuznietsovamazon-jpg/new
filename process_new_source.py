

import pandas as pd

def process_and_convert_source():
    """
    Reads the new source Excel file, converts currency for Sales and Spend,
    creates a pivoted report, and saves it.
    """
    source_path = r'C:\Users\User\Downloads\data (15).xlsx'
    output_path = r'C:\Users\User\final_converted_report.csv'
    fixed_rate = 0.71

    try:
        # --- Step 1: Load and Clean Data ---
        df = pd.read_excel(source_path, sheet_name=0)

        # Clean and convert data types
        # First, filter out summary rows based on the 'Date' column before converting to datetime
        df['Date'] = df['Date'].astype(str)
        df = df[~df['Date'].str.contains("Total", na=False, case=False)]

        # Remove rows where 'Child ASIN' is empty, which are also likely part of summary/header sections
        df.dropna(subset=['Child ASIN'], inplace=True)
        
        # Now, safely convert 'Date' column to datetime
        df['Date'] = pd.to_datetime(df['Date'])
        numeric_cols = ['Impressions', 'Clicks', 'Orders', 'Sales', 'Spend']
        for col in numeric_cols:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

        print("Исходный файл успешно загружен и очищен.")

        # --- Step 2: Convert Currency ---
        df['Sales'] = df['Sales'] * fixed_rate
        df['Spend'] = df['Spend'] * fixed_rate
        print(f"Конвертация Sales и Spend в USD по курсу {fixed_rate} выполнена.")

        # --- Step 3: Create Pivot Table ---
        # Select only the columns we need for the final report
        metrics_to_pivot = ['Clicks', 'Orders', 'Sales', 'Spend']
        df_subset = df[['Child ASIN', 'Date'] + metrics_to_pivot]

        # Unpivot the dataframe (melt)
        melted_df = df_subset.melt(
            id_vars=['Child ASIN', 'Date'],
            value_vars=metrics_to_pivot,
            var_name='Metric',
            value_name='Value'
        )

        # Create the final pivot table
        pivot_df = melted_df.pivot_table(
            index=['Child ASIN', 'Metric'],
            columns='Date',
            values='Value',
            aggfunc='sum' # Use sum to handle any potential duplicates
        )
        
        # Sort the metrics in the desired order
        pivot_df = pivot_df.reindex(['Clicks', 'Orders', 'Sales', 'Spend'], level='Metric')
        
        print("Сводная таблица успешно создана.")

        # --- Step 4: Save the Report ---
        pivot_df.to_csv(output_path, float_format='%.2f')
        print(f"Итоговый отчет сохранен в: {output_path}")

        # --- Step 5: Verification (as requested by user) ---
        print("\n--- Проверка контрольного значения ---")
        # Filter for the specific ASIN and Metric
        verification_row = pivot_df.loc[('B0DD7KW73M', 'Sales')]
        # Get the value for the specific date
        # The date columns are datetime objects, so we create one for lookup
        verification_date = pd.to_datetime('2025-11-01')
        
        if verification_date in verification_row.index:
            final_value = verification_row[verification_date]
            print(f"ASIN: B0DD7KW73M, Метрика: Sales, Дата: 2025-11-01")
            print(f"Ожидаемое значение: 402.48")
            print(f"Фактическое значение в файле: {final_value:.2f}")
            if abs(final_value - 402.48) < 0.01:
                print("Контрольное значение совпадает!")
            else:
                print("ВНИМАНИЕ: Контрольное значение НЕ СОВПАДАЕТ!")
        else:
            print("Не удалось найти дату 2025-11-01 для ASIN B0DD7KW73M в итоговом файле.")

    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")

if __name__ == "__main__":
    process_and_convert_source()
