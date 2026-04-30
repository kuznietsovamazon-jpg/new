import pandas as pd
import os

def process_attribution_report(file_path):
    """
    Processes the Amazon Attribution Promoted Product Report.

    Args:
        file_path (str): The path to the Excel report file.
    """
    try:
        # Suppress the UserWarning about default style
        import warnings
        with warnings.catch_warnings():
            warnings.simplefilter("ignore", UserWarning)
            df = pd.read_excel(file_path)
    except FileNotFoundError:
        print(f"Error: File not found at {file_path}")
        return
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return

    # Assuming 'Date' column exists.
    date_column = 'Date'
    if date_column not in df.columns:
        print(f"Error: '{date_column}' column not found in the report. Available columns: {df.columns.tolist()}")
        return

    df[date_column] = pd.to_datetime(df[date_column]).dt.date

    # Group campaigns
    df['Grouped_Campaign_Name'] = df['Campaign Name'].apply(
        lambda x: 'Adv Campaigns' if str(x).lower().startswith('adv') else x
    )

    # Determine the sales column to use
    sales_column = '14 Day Product Sales'
    if sales_column not in df.columns:
        print(f"Error: '{sales_column}' column not found. Available columns: {df.columns.tolist()}")
        return

    # Clean sales column
    if df[sales_column].dtype == 'object':
        df[sales_column] = df[sales_column].replace({r'\$': ''}, regex=True).astype(float)


    # Create pivot table
    pivot = pd.pivot_table(
        df,
        index=['Advertised ASIN', 'Grouped_Campaign_Name'],
        columns=date_column,
        values=sales_column,
        aggfunc='sum',
        fill_value=0
    )

    # --- Save the main pivot table ---
    directory = os.path.dirname(file_path)
    base_name = os.path.splitext(os.path.basename(file_path))[0]
    output_filename = os.path.join(directory, f'{base_name}_by_asin_and_campaign.csv')
    pivot.to_csv(output_filename)
    print(f"Successfully created pivot table: {output_filename}")


if __name__ == "__main__":
    # The user provided the file path in the prompt.
    input_file = r'C:\Users\User\Downloads\Amazon_Attribution_Promoted_product_report (13).xlsx'
    process_attribution_report(input_file)