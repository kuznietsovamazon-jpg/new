import pandas as pd
import os
import datetime

file_path = r'C:\Users\User\Downloads\data (5).xlsx'
output_path = r'C:\Users\User\pivoted_data_5.csv'

try:
    # --- Step 1: Read with multi-level header ---
    df = pd.read_excel(file_path, header=[0, 1])

    # --- Step 2: Separate the Identifier column ---
    identifier_col_tuple = df.columns[0]
    identifier_series = df[identifier_col_tuple]
    df_metrics = df.drop(columns=[identifier_col_tuple])

    # --- Step 3: Restructure the metric data ---
    # Stack the 'Metric' level (level 1 of the column index) into the row index.
    stacked_df = df_metrics.stack(level=1)

    # Reset the index to turn the original row numbers and 'Metric' into columns.
    stacked_df = stacked_df.reset_index()
    stacked_df = stacked_df.rename(columns={'level_0': 'original_index', 'level_1': 'Metric'})

    # --- Step 4: Join the Identifier back ---
    # Map the identifier back using the original row index.
    stacked_df['Identifier'] = stacked_df['original_index'].map(identifier_series)
    
    # --- Step 5: Melt the date columns ---
    # Now, the dates are the columns. We melt them into a 'Date' and 'Value' column.
    final_melted = stacked_df.melt(
        id_vars=['Identifier', 'Metric'], 
        var_name='Date', 
        value_name='Value'
    )

    # --- Step 6: Clean up the data ---
    # Convert Date column and handle any parsing errors
    final_melted['Date'] = pd.to_datetime(final_melted['Date'], errors='coerce').dt.date
    
    # Drop rows where essential data is missing
    final_melted = final_melted.dropna(subset=['Identifier', 'Value', 'Date', 'Metric'])
    
    # Remove summary rows and unnamed metric columns
    final_melted = final_melted[~final_melted['Identifier'].astype(str).str.contains('Total', na=False, case=False)]
    final_melted = final_melted[~final_melted['Metric'].astype(str).str.contains('Unnamed:', na=False)]

    # --- Step 7: Create the final pivot table ---
    final_pivot = final_melted.pivot_table(
        index=['Identifier', 'Metric'], 
        columns='Date', 
        values='Value', 
        aggfunc='sum'
    )

    # --- Step 8: Sort and Save ---
    metric_level = final_pivot.index.get_level_values('Metric')
    unique_metrics = metric_level.unique()
    
    # Try to find a 'Sales' column, case-insensitive
    sales_col_name = next((m for m in unique_metrics if 'sales' in str(m).lower()), None)

    if sales_col_name:
        metrics_order = [sales_col_name] + [m for m in unique_metrics if m != sales_col_name]
        final_pivot = final_pivot.reindex(metrics_order, level='Metric')

    final_pivot.to_csv(output_path)
    print(f"Processing complete. The restructured data has been saved to: {output_path}")

except Exception as e:
    print(f"An error occurred: {e}")
    print("\nThis is a complex file. The automatic processing failed. It might be necessary to inspect the file manually in Excel to understand its exact structure.")
