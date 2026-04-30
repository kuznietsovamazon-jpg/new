import pandas as pd
import os

def process_creator_reports(file_paths):
    all_data = []
    for file_path in file_paths:
        try:
            df = pd.read_csv(file_path, encoding='utf-8-sig')
            all_data.append(df)
        except UnicodeDecodeError:
            df = pd.read_csv(file_path, encoding='cp1251')
            all_data.append(df)
        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            continue

    if not all_data:
        print("No data to process.")
        return

    combined_df = pd.concat(all_data, ignore_index=True)

    # Clean and convert 'Date' column
    combined_df['Date'] = pd.to_datetime(combined_df['Date'], format='%d-%b-%Y', errors='coerce')
    combined_df.dropna(subset=['Date'], inplace=True)

    # Clean and convert numeric columns
    numeric_cols = ['Spend', 'Clicks', 'Orders', 'Sales', 'Commission Rate']
    for col in numeric_cols:
        if col in combined_df.columns:
            combined_df[col] = combined_df[col].astype(str).str.replace('$', '', regex=False).str.replace(',', '', regex=False)
            combined_df[col] = pd.to_numeric(combined_df[col], errors='coerce').fillna(0)

    # Calculate 'Commission Amount'
    if 'Sales' in combined_df.columns and 'Commission Rate' in combined_df.columns:
        combined_df['Commission Amount'] = combined_df['Sales'] * (combined_df['Commission Rate'] / 100)
    else:
        combined_df['Commission Amount'] = 0

    # Group by ASIN and Date and sum the metrics
    daily_summary = combined_df.groupby(['ASIN', 'Date']).agg(
        Total_Clicks=('Clicks', 'sum'),
        Total_Orders=('Orders', 'sum'),
        Total_Sales=('Sales', 'sum'),
        Total_Spend=('Spend', 'sum'),
        Total_Commission_Amount=('Commission Amount', 'sum')
    ).reset_index()

    # Create pivot tables for each metric
    metrics_to_pivot = {
        'Total_Clicks': 'Total_Creator_Clicks_by_ASIN_Date.csv',
        'Total_Orders': 'Total_Creator_Orders_by_ASIN_Date.csv',
        'Total_Sales': 'Total_Creator_Sales_by_ASIN_Date.csv',
        'Total_Spend': 'Total_Creator_Spend_by_ASIN_Date.csv',
        'Total_Commission_Amount': 'Total_Creator_Commission_by_ASIN_Date.csv'
    }

    for metric, output_filename in metrics_to_pivot.items():
        pivot_df = daily_summary.pivot_table(index='ASIN', columns='Date', values=metric, aggfunc='sum')
        pivot_df.columns = pivot_df.columns.strftime('%Y-%m-%d') # Format date columns
        output_path = os.path.join(os.getcwd(), output_filename)
        pivot_df.to_csv(output_path)
        print(f"Generated {output_filename}")

if __name__ == "__main__":
    # Example usage with the provided file paths
    file_paths = [
        r'C:\Users\User\Downloads\reportId=amzn1.report.B7D0U55039TF.csv',
        r'C:\Users\User\Downloads\reportId=amzn1.report.7QE49A4F39EL.csv'
    ]
    process_creator_reports(file_paths)
