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

## Unique Property Types:
# 'Residential' 
# 'CommercialLease' 
# 'Land' 
# 'ResidentialLease'
# 'ManufacturedInPark' 
# 'ResidentialIncome' 
# 'CommercialSale'
# 'BusinessOpportunity'

# Q1: What is the Residential vs. other property type share?
property_type_share = sold['PropertyType'].value_counts(normalize=True) * 100
print("Residential vs. other property type share:", property_type_share)

## Residential            67.24%
## ResidentialLease       23.01%
## Land                    3.17%
## ResidentialIncome       2.69%
## ManufacturedInPark      2.68%
## CommercialSale          0.62%
## CommercialLease         0.52%
## BusinessOpportunity     0.06%

# Q2: What are the median and average close prices?
print("Median Close Prices:", sold['ClosePrice'].median())
print("Average Close Price:", sold['ClosePrice'].mean())

## Median Close Price: $630000
## Average Close Price: $873,371.29

# Q3: What does the Days on Market distribution look like?
print("Days on Market Summary:", sold['DaysOnMarket'].describe())

# Days on Market Summary: 
# count    736770.000000
# mean         43.419014
# std          69.560371
# min        -288.000000
# 25%           9.000000
# 50%          22.000000
# 75%          54.000000
# max       12430.000000
## The min value being -288 isn't logically possible. Likely a data quality issue.

# Q4: What percentage of homes sold above vs. below list price?
above_list = sold['ClosePrice'] > sold['ListPrice']
above = above_list.mean() * 100
print('Percentage of Homes Sold Above List Price:', above)

## 30.39% of homes sold above list price

below_list = sold['ClosePrice'] < sold['ListPrice']
below = below_list.mean() * 100
print('Percentage of Homes Sold Below List Price:', below)

## 38.56% of homes solve below list price

## Roughly 31% of Homes were Sold at List Price

# Q5: Are there any apparent date consistency issues (e.g., close date before listing date)?
close = pd.to_datetime(sold['CloseDate'], errors='coerce')
listing = pd.to_datetime(sold['ListingContractDate'], errors='coerce')
inconsistent_rows = close < listing
print("Number of rows with date inconsistencies:", inconsistent_rows.sum())

## 140 rows where the close date was before listing date

# Q6: Which counties have the highest median prices?
print(sold.groupby('CountyOrParish')['ClosePrice'].median().nlargest(5))

# Top 5 Counties with highest median prices:
# Santa Clara      $1,483,000.0
# San Mateo        $1,462,000.0
# San Francisco    $1,110,000.0
# Alpine           $1,100,000.0
# Marin            $1,070,000.0

print("Rows before Residential Filter:", len(sold))
sold_Residential = sold[sold['PropertyType'] == 'Residential']
print("Rows after Residential Filter:", len(sold_Residential))

# Rows before Residential Filter: 736770
# Rows after Residential Filter: 495407

null_counts = sold_Residential.isnull().sum()
print("Null Counts:", null_counts)

null_val_percent = (null_counts / len(sold_Residential)) * 100
summary_table = pd.DataFrame({'Null Counts': null_counts, 'Null Percentage': null_val_percent})

summary_table = summary_table.sort_values(by='Null Percentage', ascending=False)
print(summary_table)

high_null_percent = summary_table[summary_table['Null Percentage'] > 90]
print(high_null_percent)

#                               Null Counts  Null Percentage
# AboveGradeFinishedArea             495407       100.000000
# CoveredSpaces                      495407       100.000000
# TaxAnnualAmount                    495407       100.000000
# TaxYear                            495407       100.000000
# ElementarySchoolDistrict           495407       100.000000
# FireplacesTotal                    495407       100.000000
# MiddleOrJuniorSchoolDistrict       495407       100.000000
# BusinessType                       495407       100.000000
# WaterfrontYN                       495096        99.937223
# BelowGradeFinishedArea             492390        99.391006
# BasementYN                         485685        98.037573
# BuilderName                        471305        95.134909
# LotSizeDimensions                  471226        95.118963
# BuildingAreaTotal                  460636        92.981326
# CoBuyerAgentFirstName              449759        90.785758

numeric_distribution_summary = sold_Residential[['ClosePrice', 'LivingArea', 'DaysOnMarket']].describe()
print(numeric_distribution_summary)

#          ClosePrice    LivingArea   DaysOnMarket
# count  4.954030e+05  4.951330e+05  495407.000000
# mean   1.183647e+06  1.902510e+03      37.648233
# std    5.483324e+06  2.420818e+04      53.603875
# min    0.000000e+00  0.000000e+00    -288.000000
# 25%    5.750000e+05  1.250000e+03       8.000000
# 50%    8.250000e+05  1.648000e+03      19.000000
# 75%    1.300000e+06  2.227000e+03      49.000000
# max    9.895000e+08  1.702132e+07   12430.000000

## ClosePrice max seems too large; the min being 0 is also likely a data error
## LivingArea max seems too large; the min begin 0 is also likely a data error
## DaysOnMarket min was caught in the Q5 above

sold_Residential.to_csv(os.path.join("/Users/brianzhao/py", "combined_sold_residential_EDA.csv"), index=False)
