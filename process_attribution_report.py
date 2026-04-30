
import pandas as pd
import numpy as np
import os

# Define the file path
file_path = r'C:\Users\User\Downloads\Amazon_Attribution_Promoted_product_report (18).xlsx'
output_dir = r'C:\Users\User'

# Read the Excel file
try:
    df = pd.read_excel(file_path)
except FileNotFoundError:
    print(f"File not found: {file_path}")
    exit()

# Rename columns for easier access
df.columns = df.columns.str.strip()

# Ensure the 'Date' column exists
if 'Date' not in df.columns:
    print("Error: 'Date' column not found in the report.")
    exit()

# Convert 'Date' to datetime
df['Date'] = pd.to_datetime(df['Date'])

# Define the sales column to use
sales_column = None
possible_sales_columns = ['14 Day Product Sales', 'Product Sales']
for col in possible_sales_columns:
    if col in df.columns:
        sales_column = col
        break

if sales_column is None:
    print(f"Error: None of the possible sales columns {possible_sales_columns} found in the report.")
    exit()

# Clean and convert sales column to numeric
if df[sales_column].dtype == 'object':
    df[sales_column] = df[sales_column].replace({'\$': '', ',': ''}, regex=True)
df[sales_column] = pd.to_numeric(df[sales_column], errors='coerce')


# Group campaigns
def group_campaigns(campaign_name):
    if isinstance(campaign_name, str) and campaign_name.lower().startswith('adv'):
        return 'Adv Campaigns'
    return campaign_name

df['Grouped_Campaign_Name'] = df['Campaign Name'].apply(group_campaigns)

# Create the main pivot table
pivot_table = pd.pivot_table(
    df,
    values=sales_column,
    index=['Advertised ASIN', 'Grouped_Campaign_Name'],
    columns=['Date'],
    aggfunc=np.sum,
    fill_value=0
)

# Save the main pivot table
output_path = os.path.join(output_dir, 'promoted_product_report_by_asin_and_campaign_18.csv')
pivot_table.to_csv(output_path)
print(f"Successfully created pivot table at: {output_path}")


# Create and save the 'Adv Campaigns' filtered report
adv_campaigns_df = pivot_table.reset_index()
adv_campaigns_df = adv_campaigns_df[adv_campaigns_df['Grouped_Campaign_Name'] == 'Adv Campaigns']

if not adv_campaigns_df.empty:
    adv_output_path = os.path.join(output_dir, 'promoted_product_report_adv_campaigns_18.csv')
    adv_campaigns_df.to_csv(adv_output_path, index=False)
    print(f"Successfully created 'Adv Campaigns' report at: {adv_output_path}")
else:
    print("No 'Adv Campaigns' found to create a separate report.")

