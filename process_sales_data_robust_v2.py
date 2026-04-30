import pandas as pd
import os

def process_sales_data_robust(file_path, output_filename, exchange_rate):
    """
    Processes a sales data file, including sessions, converts sales to USD,
    and returns a flattened DataFrame in the requested pivot format.
    """
    try:
        # Read the raw data, skipping the first two header rows
        df_data = pd.read_excel(file_path, header=None, skiprows=2)

        # Read the first two header rows separately
        df_header = pd.read_excel(file_path, header=None, nrows=2)

        # The first two columns are 'Image' and 'ASIN'
        # The rest of the columns are date-metric pairs
        
        # Create a list for the new MultiIndex columns
        multi_cols = [('Image', ''), ('ASIN', '')] # For the first two columns

        current_date = None
        for i in range(2, len(df_header.columns)):
            date_val = df_header.iloc[0, i]
            metric_val = str(df_header.iloc[1, i]).strip()

            if pd.notna(date_val) and isinstance(date_val, pd.Timestamp):
                current_date = date_val.strftime('%Y-%m-%d')
            
            if current_date is not None and 'Unnamed' not in metric_val and metric_val != 'nan':
                multi_cols.append((current_date, metric_val))
            else:
                # Handle columns that are not date-metric pairs (e.g., trailing totals)
                # We'll just use the metric name if it's not 'Unnamed' or 'nan'
                if 'Unnamed' not in metric_val and metric_val != 'nan':
                    multi_cols.append(('Total', metric_val)) # Assign a 'Total' date for these
                else:
                    multi_cols.append((f"col_{i}", "")) # Fallback for truly unhandled columns

        # Assign the new MultiIndex columns to the data DataFrame
        df_data.columns = pd.MultiIndex.from_tuples(multi_cols[:len(df_data.columns)])

        # Rename the first two columns
        df_data = df_data.rename(columns={'Image': 'Image', 'ASIN': 'ASIN'})

        # Melt the DataFrame
        # We need to melt based on the MultiIndex columns that represent dates and metrics
        df_melted = df_data.melt(id_vars=[('Image', ''), ('ASIN', '')], 
                                 var_name='Date_Metric_Tuple', # Use a single string for var_name
                                 value_name='Value')

        # Clean up the melted DataFrame
        df_melted = df_melted.rename(columns={('Image', ''): 'Image', ('ASIN', ''): 'ASIN'})
        df_melted = df_melted.drop(columns=['Image'])
        
        # Split the 'Date_Metric_Tuple' into 'Date' and 'Metric'
        df_melted[['Date', 'Metric']] = pd.DataFrame(df_melted['Date_Metric_Tuple'].tolist(), index=df_melted.index)
        df_melted = df_melted.drop(columns=['Date_Metric_Tuple'])

        # Convert 'Date' to datetime objects
        df_melted['Date'] = pd.to_datetime(df_melted['Date'], errors='coerce').dt.date

        # Strip whitespace from the 'Metric' column
        df_melted['Metric'] = df_melted['Metric'].str.strip()

        # Filter for the desired metrics
        metrics_to_keep = ['Total Sales', 'Units Sold', 'Orders', 'Total Sessions']
        df_filtered = df_melted[df_melted['Metric'].isin(metrics_to_keep)]

        # Convert 'Value' to numeric, coercing errors
        df_filtered['Value'] = pd.to_numeric(df_filtered['Value'], errors='coerce')

        # Convert 'Total Sales' to USD
        df_filtered.loc[df_filtered['Metric'] == 'Total Sales', 'Value'] *= exchange_rate
        df_filtered.loc[df_filtered['Metric'] == 'Total Sales', 'Metric'] = 'Total Sales (USD)'

        # Pivot the table to the desired format
        pivot_table = df_filtered.pivot_table(index=['ASIN', 'Metric'], columns='Date', values='Value', aggfunc='first')

        # Save the pivot table
        output_path = os.path.join(os.path.expanduser("~"), "Downloads", output_filename)
        pivot_table.to_excel(output_path)
        
        print(f"Обработанный файл с сессиями сохранен в {output_path}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Process data (11).xlsx
file_path_11 = os.path.join('C:', os.sep, 'Users', 'User', 'Downloads', 'data (11).xlsx')
exchange_rate = 0.72
process_sales_data_robust(file_path_11, 'data_11_with_sessions_robust.xlsx', exchange_rate)
