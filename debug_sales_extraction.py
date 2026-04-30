import pandas as pd
import numpy as np

def debug_sales_extraction(file_path):
    """
    Inspects the raw header of the report and debugs the sales data extraction
    for a single ASIN to verify the calculation.
    """
    try:
        # --- Part 1: Inspect raw headers ---
        print("--- Raw Header Rows ---")
        raw_df_head = pd.read_excel(file_path, header=None, nrows=5)
        print(raw_df_head)
        print("-" * 25)

        # --- Part 2: Process data to debug sales ---
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
        
        # --- Part 3: Filter and display debug info ---
        # Find the first valid ASIN to use for debugging
        first_asin = melted_df['ASIN'].dropna().iloc[0]
        
        print(f"\n--- Debugging for ASIN: {first_asin} ---")
        
        # Filter for this ASIN and any metric containing 'Sales'
        debug_subset = melted_df[
            (melted_df['ASIN'] == first_asin) & 
            (melted_df['Metric'].str.contains('Sales', case=False, na=False))
        ]
        
        print("\nFound data for metrics containing 'Sales':")
        # To make it readable, let's pivot this small subset
        debug_pivot = debug_subset.pivot_table(index='Metric', columns='Date', values='value', aggfunc='sum')
        print(debug_pivot.head(20))

    except FileNotFoundError:
        print(f"Error: The file '{file_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    file_to_debug = r'C:\Users\User\Downloads\data (13).xlsx'
    debug_sales_extraction(file_to_debug)
