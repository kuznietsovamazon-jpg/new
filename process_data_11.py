import pandas as pd
import os

def process_data_11(file_path):
    """
    Processes the Excel file to extract and pivot the data as requested.
    """
    try:
        # Read the header rows to get dates and metric names
        header_df = pd.read_excel(file_path, header=None, nrows=2)
        
        # Forward fill the dates in the first row
        dates = header_df.iloc[0].ffill()
        
        # Get the metrics from the second row
        metrics = header_df.iloc[1]
        
        # Create new column names
        new_columns = []
        for i in range(len(dates)):
            # Format the date to a string, if it's a datetime object
            if isinstance(dates[i], pd.Timestamp):
                date_str = dates[i].strftime('%Y-%m-%d')
            else:
                date_str = str(dates[i])
            new_columns.append(f"{date_str}_{metrics[i]}")
            
        # Read the data, skipping the header rows
        df = pd.read_excel(file_path, header=None, skiprows=2)
        df.columns = new_columns
        
        # Rename the first two columns
        df = df.rename(columns={df.columns[0]: 'Image', df.columns[1]: 'ASIN'})
        
        # Melt the dataframe to unpivot
        id_vars = ['Image', 'ASIN']
        value_vars = [col for col in df.columns if col not in id_vars]
        df_melted = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='Date_Metric', value_name='Value')
        
        # Split 'Date_Metric' into 'Date' and 'Metric'
        df_melted[['Date', 'Metric']] = df_melted['Date_Metric'].str.split('_', n=1, expand=True)
        df_melted = df_melted.drop(columns=['Date_Metric'])
        
        # Strip whitespace from the 'Metric' column
        df_melted['Metric'] = df_melted['Metric'].str.strip()
        
        # Filter for the desired metrics
        metrics_to_keep = ['Total Sales', 'Units Sold', 'Orders']
        df_filtered = df_melted[df_melted['Metric'].isin(metrics_to_keep)]
        
        # Create the pivot table
        pivot_table = df_filtered.pivot_table(index=['ASIN', 'Metric'], columns='Date', values='Value', aggfunc='first')
        
        # Save the pivot table
        output_path = os.path.join(os.path.dirname(file_path), 'data_11_pivoted.xlsx')
        pivot_table.to_excel(output_path)
        
        print(f"Сводная таблица сохранена в {output_path}")

    except Exception as e:
        print(f"Произошла ошибка: {e}")

file_path = os.path.join('C:', os.sep, 'Users', 'User', 'Downloads', 'data (11).xlsx')
process_data_11(file_path)
