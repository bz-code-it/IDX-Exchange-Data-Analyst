import pandas as pd
import os

sold = pd.read_csv('/Users/brianzhao/py/sold_residential_with_rates.csv', low_memory=False)

# Checking row count of dataset
print(sold.shape[0])

# Converting date fields to datetime
cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']

# Checking column types before conversion
print(sold[cols].dtypes)

# Checking for nulls in date fields before conversion
print("Null counts before datetime conversion:")
print(sold[cols].isnull().sum())

for col in cols:
    sold[col] = pd.to_datetime(sold[col], errors='coerce')

# Checking for nulls in date fields after conversion
print("Null counts after datetime conversion:")
print(sold[cols].isnull().sum())

# Checking column types after conversion
print(sold[cols].dtypes)

# Remove unnecessary or redundant columns
cols_to_drop = ['AboveGradeFinishedArea', 'CoveredSpaces', 'TaxAnnualAmount', 'TaxYear', 
                'ElementarySchoolDistrict', 'FireplacesTotal', 'MiddleOrJuniorSchoolDistrict', 'BusinessType',
                'WaterfrontYN', 'BelowGradeFinishedArea', 'BasementYN', 'BuilderName',
                'LotSizeDimensions', 'BuildingAreaTotal', 'CoBuyerAgentFirstName'
]
## All these columns have a null percentage > 90 and are not core fields

# Checking column count before dropping columns
print(sold.shape[1])

sold = sold.drop(columns=cols_to_drop)

# Checking column count after dropping columns
print(sold.shape[1])

# Handling missing values
null_counts = sold.isnull().sum()
pd.set_option('display.max_rows', None)
print(null_counts[null_counts > 0])
pd.reset_option('display.max_rows')

# Ensure numeric fields are properly typed
numeric_cols = [
    'ClosePrice', 'ListPrice', 'OriginalListPrice', 'LivingArea', 
    'LotSizeAcres', 'LotSizeArea', 'LotSizeSquareFeet', 'BedroomsTotal', 
    'BathroomsTotalInteger', 'YearBuilt', 'DaysOnMarket', 'GarageSpaces', 
    'ParkingTotal', 'Stories', 'AssociationFee', 'Latitude', 'Longitude',
    'StreetNumberNumeric', 'MainLevelBedrooms', 'ListingKeyNumeric'
]

# Checking column type
print(sold[numeric_cols].dtypes)

# Flag invalid numeric values
sold['invalid_ClosePrice_flag'] = sold['ClosePrice'] <= 0
sold['invalid_LivingArea_flag'] = sold['LivingArea'] <= 0
sold['invalid_DaysOnMarket_flag'] = sold['DaysOnMarket'] < 0
sold['invalid_Bedrooms_flag'] = sold['BedroomsTotal'] < 0
sold['invalid_Bathrooms_flag'] = sold['BathroomsTotalInteger'] < 0

# Checking for invalid numeric values
print(sold['invalid_ClosePrice_flag'].sum())
print(sold['invalid_LivingArea_flag'].sum())
print(sold['invalid_DaysOnMarket_flag'].sum())
print(sold['invalid_Bedrooms_flag'].sum())
print(sold['invalid_Bathrooms_flag'].sum())

# Date Consistency Checks
sold['listing_after_close_flag'] = sold['ListingContractDate'] > sold['CloseDate']
sold['purchase_after_close_flag'] = sold['PurchaseContractDate'] > sold['CloseDate']
sold['listing_after_purchase_flag'] = sold['ListingContractDate'] > sold['PurchaseContractDate']

# Checking for date consistency issues
print(sold['listing_after_close_flag'].sum())
print(sold['purchase_after_close_flag'].sum())
print(sold['listing_after_purchase_flag'].sum())

# Geographic Data Checks
sold['missing_coordinates_flag'] = sold['Latitude'].isnull() | sold['Longitude'].isnull()
sold['zero_coordinate_flag'] = (sold['Latitude'] == 0) | (sold['Longitude'] == 0)
sold['positive_Longitude_flag'] = sold['Longitude'] > 0

has_coordinates = sold['Latitude'].notnull() & sold['Longitude'].notnull()
outside_coordinate_range = (~sold['Latitude'].between(32.5, 42.0)) | (~sold['Longitude'].between(-124.5, -114.1))
sold['out_of_California_flag'] = has_coordinates & outside_coordinate_range

# Checking for geographic data errors
print(sold['missing_coordinates_flag'].sum())
print(sold['zero_coordinate_flag'].sum())
print(sold['positive_Longitude_flag'].sum())
print(sold['out_of_California_flag'].sum())

# Geographic data quality summary
sold['geo_issue_flag'] = (
    sold['missing_coordinates_flag'] |
    sold['zero_coordinate_flag'] |
    sold['positive_Longitude_flag'] |
    sold['out_of_California_flag']
)
print(sold['geo_issue_flag'].sum())

# Checking row count of dataset after cleaning
print(sold.shape[0])

# Checking column count of dataset after cleaning
print(sold.shape[1])

# Cleaned dataset
sold.to_csv(os.path.join("/Users/brianzhao/py", "sold_residential_cleaned.csv"), index=False)