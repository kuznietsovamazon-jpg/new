import pandas as pd
import numpy as np

def convert_currency_fixed_rate():
    """
    Converts sales and spend data from CAD to USD in a pivoted report
    using a fixed exchange rate.
    """
    try:
        # --- Step 1: Define constants ---
        cad_report_path = r'C:\Users\User\pivoted_report_cad.csv'
        usd_report_path = r'C:\Users\User\pivoted_report_usd.csv'
        fixed_rate = 0.72

        print(f"Использую фиксированный курс конвертации CAD в USD: {fixed_rate}")
        print("-" * 50)

        # --- Step 2: Load the CAD report ---
        try:
            cad_df = pd.read_csv(cad_report_path)
        except Exception as e:
            print(f"Ошибка при чтении файла отчета CAD: {e}")
            return

        # --- Step 3: Perform the conversion ---
        usd_df = cad_df.copy()
        metrics_to_convert = ['Sales', 'Spend']
        
        # Identify all date columns
        date_columns = [col for col in usd_df.columns if col not in ['Child ASIN', 'Metric']]
        
        for date_col in date_columns:
            # Ensure the column is numeric before multiplication
            # This will turn non-numeric values (like empty strings) into NaN
            usd_df[date_col] = pd.to_numeric(usd_df[date_col], errors='coerce')

            # Apply conversion only to the specified metrics
            for metric in metrics_to_convert:
                mask = usd_df['Metric'] == metric
                # Multiply the values for the metric rows by the fixed rate
                usd_df.loc[mask, date_col] *= fixed_rate

        # --- Step 4: Save the new report ---
        try:
            # Round the results to 2 decimal places for currency
            usd_df.to_csv(usd_report_path, index=False, float_format='%.2f')
            print(f"Конвертация завершена. Файл сохранен как: {usd_report_path}")
        except Exception as e:
            print(f"Ошибка при сохранении файла USD отчета: {e}")

    except Exception as e:
        print(f"Произошла непредвиденная ошибка: {e}")

if __name__ == "__main__":
    convert_currency_fixed_rate()