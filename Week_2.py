import pandas as pd
import os

# Load data
sold = pd.read_csv('/Users/brianzhao/py/combined_sold_all_types.csv', low_memory=False)

# Inspect structure
print(sold.columns)
print(sold.head())
print("Number of Rows:", sold.shape[0])
print("Number of Columns:", sold.shape[1])
print(sold.dtypes)

# Check property categories
print("Unique Property Types:", sold['PropertyType'].unique())

# Q1: What is the Residential vs. other property type share?
property_type_share = sold['PropertyType'].value_counts(normalize=True) * 100
print("Residential vs. other property type share:", property_type_share)

# Q2: What are the median and average close prices?
print("Median Close Prices:", sold['ClosePrice'].median())
print("Average Close Price:", sold['ClosePrice'].mean())

# Q3: What does the Days on Market distribution look like?
print("Days on Market Summary:", sold['DaysOnMarket'].describe())

# Q4: What percentage of homes sold above vs. below list price?
above_list = sold['ClosePrice'] > sold['ListPrice']
above = above_list.mean() * 100
print('Percentage of Homes Sold Above List Price:', above)

below_list = sold['ClosePrice'] < sold['ListPrice']
below = below_list.mean() * 100
print('Percentage of Homes Sold Below List Price:', below)

# Q5: Are there any apparent date consistency issues (e.g., close date before listing date)?
close = pd.to_datetime(sold['CloseDate'], errors='coerce')
listing = pd.to_datetime(sold['ListingContractDate'], errors='coerce')
inconsistent_rows = close < listing
print("Number of rows with date inconsistencies:", inconsistent_rows.sum())

# Q6: Which counties have the highest median prices?
print(sold.groupby('CountyOrParish')['ClosePrice'].median().nlargest(5))

# Checking row count before and after filtering
print("Rows before Residential Filter:", len(sold))
sold_Residential = sold[sold['PropertyType'] == 'Residential']
print("Rows after Residential Filter:", len(sold_Residential))

# Checking for null values in the filtered dataset
null_counts = sold_Residential.isnull().sum()
print("Null Counts:", null_counts)

null_val_percent = (null_counts / len(sold_Residential)) * 100
summary_table = pd.DataFrame({'Null Counts': null_counts, 'Null Percentage': null_val_percent})

summary_table = summary_table.sort_values(by='Null Percentage', ascending=False)
print(summary_table)

# Checking for columns with >90% null values
high_null_percent = summary_table[summary_table['Null Percentage'] > 90]
print(high_null_percent)

# Analyzing numeric distributions for key columns
numeric_distribution_summary = sold_Residential[['ClosePrice', 'LivingArea', 'DaysOnMarket']].describe()
print(numeric_distribution_summary)

sold_Residential.to_csv(os.path.join("/Users/brianzhao/py", "combined_sold_residential_EDA.csv"), index=False)
