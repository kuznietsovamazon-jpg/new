import pandas as pd
import os

def process_file(file_path, output_filename):
    """
    Processes a sales data file and returns a flattened DataFrame.
    """
    try:
        # 1. Read header rows
        header_df = pd.read_excel(file_path, header=None, nrows=2)

        # 2. Construct column mapping
        base_metrics = header_df.iloc[1, 2:14].tolist() 
        
        dates_raw = header_df.iloc[0, 2:].dropna()
        
        new_columns = ['Image', 'ASIN']
        date_columns_to_process = []

        current_date = None
        # ffill dates
        header_df.iloc[0] = header_df.iloc[0].ffill()

        for i in range(2, len(header_df.columns)):
            current_date = header_df.iloc[0, i]
            
            if isinstance(current_date, pd.Timestamp):
                date_str = current_date.strftime('%Y-%m-%d')
                metric = str(header_df.iloc[1, i])
                if 'Unnamed' not in metric:
                    col_name = f"{date_str}_{metric}"
                    new_columns.append(col_name)
                    date_columns_to_process.append(col_name)

        # Read the data, skipping the header rows
        df = pd.read_excel(file_path, header=None, skiprows=2)
        
        # We'll only use the columns we've constructed names for.
        df = df.iloc[:, :len(new_columns)]
        df.columns = new_columns

        # Melt the dataframe
        id_vars = ['Image', 'ASIN']
        
        df_melted = pd.melt(df, id_vars=id_vars, value_vars=date_columns_to_process, var_name='Date_Metric', value_name='Value')

        # Split 'Date_Metric' into 'Date' and 'Metric'
        df_melted[['Date', 'Metric']] = df_melted['Date_Metric'].str.split('_', n=1, expand=True)
        df_melted = df_melted.drop(columns=['Date_Metric', 'Image'])

        # Strip whitespace from the 'Metric' column
        df_melted['Metric'] = df_melted['Metric'].str.strip()

        # Filter for the desired metrics
        metrics_to_keep = ['Total Sales', 'Units Sold', 'Orders']
        df_filtered = df_melted[df_melted['Metric'].isin(metrics_to_keep)]

        # Pivot the table
        pivot_table = df_filtered.pivot_table(index=['ASIN', 'Metric'], columns='Date', values='Value', aggfunc='first')

        # Save the pivot table
        output_path = os.path.join(os.path.expanduser("~"), "Downloads", output_filename)
        pivot_table.to_excel(output_path)
        
        print(f"Обработанный файл сохранен в {output_path}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

# Process data (10).xlsx
file_path_10 = os.path.join('C:', os.sep, 'Users', 'User', 'Downloads', 'data (10).xlsx')
process_file(file_path_10, 'data_10_processed.xlsx')
