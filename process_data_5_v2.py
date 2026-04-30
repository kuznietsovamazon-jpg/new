import pandas as pd
import os

file_path = r'C:\Users\User\Downloads\data (5).xlsx'
output_path = r'C:\Users\User\pivoted_data_5.csv'

try:
    # --- Step 1: Try reading with multi-level header ---
    # This assumes the first row contains dates and the second contains the metric names.
    df = pd.read_excel(file_path, header=[0, 1])
    
    # --- Step 2: Clean up the column names and set the identifier ---
    # The first column in the Excel file is the identifier (ASIN/SKU).
    # Pandas reads its header as a tuple, e.g., ('Day', 'Unnamed: 1_level_1').
    # We'll grab the actual data column and rename its header for melting.
    identifier_header = df.columns[0] 
    df = df.rename(columns={identifier_header: 'Identifier'})
    
    # The columns are now a MultiIndex, plus the 'Identifier' column.
    
    # --- Step 3: Melt the DataFrame ---
    # This transforms the wide data into a long format.
    melted_df = df.melt(id_vars=['Identifier'], var_name=['Date', 'Metric'], value_name='Value')
    
    # --- Step 4: Clean up the melted data ---
    # The 'Date' column might contain junk from merged cells, let's forward-fill the dates.
    # First, convert actual dates to datetime objects, marking others as Not a Time (NaT).
    melted_df['Date'] = pd.to_datetime(melted_df['Date'], errors='coerce')
    # Now forward-fill the valid dates.
    melted_df['Date'].fillna(method='ffill', inplace=True)
    # Keep only the date part.
    melted_df['Date'] = melted_df['Date'].dt.date
    
    # Drop rows with no valid data.
    melted_df = melted_df.dropna(subset=['Identifier', 'Value', 'Date', 'Metric'])
    # Remove any summary rows that might exist in the identifier column.
    melted_df = melted_df[~melted_df['Identifier'].astype(str).str.contains('Total', na=False, case=False)]
    # Remove junk metrics that pandas might create like 'Unnamed: ...'
    melted_df = melted_df[~melted_df['Metric'].astype(str).str.contains('Unnamed:', na=False)]

    # --- Step 5: Create the final pivot table as requested ---
    # Index: Identifier (ASIN) and Metric
    # Columns: Date
    # Values: Value
    final_pivot = melted_df.pivot_table(index=['Identifier', 'Metric'], columns='Date', values='Value', aggfunc='sum')
    
    # --- Step 6: Sort the metrics to have 'Sales' first if it exists ---
    metric_level = final_pivot.index.get_level_values('Metric')
    if 'Sales' in metric_level:
        # Create a sorted list of metrics
        metrics_order = ['Sales'] + [m for m in metric_level.unique() if m != 'Sales']
        # Reindex the dataframe based on the desired metric order
        final_pivot = final_pivot.reindex(metrics_order, level='Metric')

    # --- Step 7: Save the result ---
    final_pivot.to_csv(output_path)
    print(f"Processing complete. The restructured data has been saved to: {output_path}")

except Exception as e:
    print(f"An error occurred: {e}")
    print("\nCould not process the file automatically. The Excel file's header structure might be non-standard. Please ensure the first row contains dates and the second row contains metric names (e.g., Sales, Units).")
