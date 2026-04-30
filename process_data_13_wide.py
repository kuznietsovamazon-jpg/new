import pandas as pd
import numpy as np

def process_wide_report(file_path, suffix=''):
    """
    Processes a complex wide-format Excel report into multiple pivoted CSV files.
    Handles non-date columns and specifically uses 'Total Sales' for the sales metric.
    """
    try:
        df = pd.read_excel(file_path, header=[0, 1])

        new_cols = []
        valid_columns_map = {}

        for i, col in enumerate(df.columns):
            original_col_name = col
            try:
                date_part = pd.to_datetime(col[0]).strftime('%Y-%m-%d')
                metric_part = col[1]
                new_col_name = f"{date_part}_{metric_part}"
                new_cols.append(new_col_name)
                valid_columns_map[new_col_name] = original_col_name
            except (ValueError, TypeError):
                if i < 2:
                     new_cols.append(col[1] if pd.notna(col[1]) else col[0])
                     valid_columns_map[new_cols[-1]] = original_col_name

        df = df[[valid_columns_map[c] for c in new_cols]]
        df.columns = new_cols
        df.rename(columns={df.columns[0]: 'Item', df.columns[1]: 'ASIN'}, inplace=True)
        
        id_vars = ['ASIN', 'Item']
        value_vars = [c for c in df.columns if c not in id_vars]
        melted_df = df.melt(id_vars=id_vars, value_vars=value_vars, var_name='variable', value_name='value')

        melted_df[['Date', 'Metric']] = melted_df['variable'].str.split('_', n=1, expand=True)
        
        melted_df.drop(columns=['variable', 'Item'], inplace=True)
        melted_df.dropna(subset=['ASIN', 'value', 'Metric'], inplace=True)
        
        melted_df['value'] = pd.to_numeric(melted_df['value'], errors='coerce')
        melted_df.dropna(subset=['value'], inplace=True)

        metrics_to_pivot = ['Sales', 'Units', 'Orders', 'Sessions']
        
        for metric in metrics_to_pivot:
            
            # --- CORRECTED LOGIC ---
            if metric == 'Sales':
                # Use exact match for 'Total Sales' to avoid including profit.
                metric_df = melted_df[melted_df['Metric'] == 'Total Sales']
            else:
                # Use contains for other metrics for flexibility.
                metric_df = melted_df[melted_df['Metric'].str.contains(metric, case=False, na=False)]
            # --- END OF CORRECTION ---

            if not metric_df.empty:
                pivot_df = metric_df.pivot_table(
                    index='ASIN', 
                    columns='Date', 
                    values='value',
                    aggfunc='sum'
                )
                # Overwrite the existing file with the corrected data
                output_filename = f'pivoted_{metric.lower()}_report{suffix}.csv'
                pivot_df.to_csv(output_filename)
                print(f"Successfully created/updated '{output_filename}' with corrected data.")
            else:
                print(f"No data found for metric: '{metric}'")

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    file_to_process = r'C:\Users\User\Downloads\data (13).xlsx'
    process_wide_report(file_to_process, suffix='_13')