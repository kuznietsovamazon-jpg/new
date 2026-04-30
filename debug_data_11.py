import pandas as pd
import os

def process_sales_file(file_path):
    """
    Processes a sales data file (like data (10).xlsx or data (11).xlsx)
    and returns a flattened DataFrame.
    """
    header_df = pd.read_excel(file_path, header=None, nrows=2)
    dates = header_df.iloc[0].ffill()
    metrics = header_df.iloc[1]
    
    new_columns = []
    for i in range(len(dates)):
        if isinstance(dates[i], pd.Timestamp):
            date_str = dates[i].strftime('%Y-%m-%d')
            new_columns.append(f"{date_str}_{metrics[i]}")
        else:
            new_columns.append(f"Total_{metrics[i]}")

    df = pd.read_excel(file_path, header=None, skiprows=2)
    
    print(f"File: {file_path}")
    print(f"Length of new_columns: {len(new_columns)}")
    print(f"Length of df.columns: {len(df.columns)}")
    
    # Let's see the columns
    print("new_columns:", new_columns)
    
    # It seems there is an extra column in the excel file.
    # Let's try to use only the number of columns of the dataframe
    df.columns = new_columns[:len(df.columns)]
    
    df = df.rename(columns={df.columns[0]: 'Image', df.columns[1]: 'ASIN'})
    
    id_vars = ['Image', 'ASIN']
    
    # We need to find the actual value columns, which are the ones with dates
    value_vars = [col for col in df.columns if 'Total_' not in col and col not in id_vars and 'nan' not in col]

    df_melted = pd.melt(df, id_vars=id_vars, value_vars=value_vars, var_name='Date_Metric', value_name='Value')
    
    df_melted[['Date', 'Metric']] = df_melted['Date_Metric'].str.split('_', n=1, expand=True)
    df_melted = df_melted.drop(columns=['Date_Metric', 'Image'])
    
    df_melted['Metric'] = df_melted['Metric'].str.strip()
    
    metrics_to_keep = ['Total Sales', 'Units Sold', 'Orders']
    df_filtered = df_melted[df_melted['Metric'].isin(metrics_to_keep)]
    
    flat_table = df_filtered.pivot_table(index=['ASIN', 'Date'], columns='Metric', values='Value', aggfunc='first').reset_index()
    
    return flat_table

file_path_11 = os.path.join('C:', os.sep, 'Users', 'User', 'Downloads', 'data (11).xlsx')
process_sales_file(file_path_11)
