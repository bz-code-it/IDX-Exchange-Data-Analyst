import pandas as pd
import os

sold = pd.read_csv('/Users/brianzhao/py/sold_residential_with_rates.csv', low_memory=False)

print(sold.shape[0])
# Row count before : 495407

# Converting date fields to datetime
cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']

print(sold[cols].dtypes)
# CloseDate                   object
# PurchaseContractDate        object
# ListingContractDate         object
# ContractStatusChangeDate    object

# Checking for nulls in date fields before conversion
print("Null counts before datetime conversion:")
print(sold[cols].isnull().sum())
# CloseDate                     0
# PurchaseContractDate        197
# ListingContractDate           1
# ContractStatusChangeDate    594

for col in cols:
    sold[col] = pd.to_datetime(sold[col], errors='coerce')

# Checking for nulls in date fields after conversion
print("Null counts after datetime conversion:")
print(sold[cols].isnull().sum())
# CloseDate                     0
# PurchaseContractDate        197
# ListingContractDate           1
# ContractStatusChangeDate    594

# Null counts are identical before and after conversion, so no dates were
# lost or corrupted during conversion.

print(sold[cols].dtypes)
# CloseDate                   datetime64[ns]
# PurchaseContractDate        datetime64[ns]
# ListingContractDate         datetime64[ns]
# ContractStatusChangeDate    datetime64[ns]

# Remove unnecessary or redundant columns
cols_to_drop = ['AboveGradeFinishedArea', 'CoveredSpaces', 'TaxAnnualAmount', 'TaxYear', 
                'ElementarySchoolDistrict', 'FireplacesTotal', 'MiddleOrJuniorSchoolDistrict', 'BusinessType',
                'WaterfrontYN', 'BelowGradeFinishedArea', 'BasementYN', 'BuilderName',
                'LotSizeDimensions', 'BuildingAreaTotal', 'CoBuyerAgentFirstName'
]
## All these columns have a null percentage > 90 and are not core fields

print(sold.shape[1])
# Column count before: 86

sold = sold.drop(columns=cols_to_drop)

print(sold.shape[1])
# Column count after: 71

# Handling missing values
null_counts = sold.isnull().sum()
pd.set_option('display.max_rows', None)
print(null_counts[null_counts > 0])
pd.reset_option('display.max_rows')

# Decision: missing values are left as NaN across the dataset rather
# than filled with guessed defaults, since filling would fabricate 
# data and distort calculations later on.
#
# Exception: Latitude/Longitude missingness is handled separately via
# dedicated flag columns in the Geographic Data Checks task below.
#

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
# ClosePrice               float64
# ListPrice                float64
# OriginalListPrice        float64
# LivingArea               float64
# LotSizeAcres             float64
# LotSizeArea              float64
# LotSizeSquareFeet        float64
# BedroomsTotal            float64
# BathroomsTotalInteger    float64
# YearBuilt                float64
# DaysOnMarket               int64
# GarageSpaces             float64
# ParkingTotal             float64
# Stories                  float64
# AssociationFee           float64
# Latitude                 float64
# Longitude                float64
# StreetNumberNumeric      float64
# MainLevelBedrooms        float64
# ListingKeyNumeric          int64

# Confirmed: all 20 expected numeric fields are already correctly typed
# as float64 or int64 therefore no conversion needed. Fields with any missing
# values show as float64 rather than int64. DaysOnMarket is int64 type which
# means it doesn't have any missing values. 
#

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
# ClosePrice: 1
# LivingArea: 177
# DaysOnMarket: 56
# Bedrooms: 0
# Bathrooms: 0

# Decision: flag invalid rows with boolean columns instead of deleting them,
# so the full dataset is preserved and anyone using it can decide whether to
# exclude them. Missing values are not flagged, since NaN comparisons
# evaluate to False.
#
# Note: the 56 negative DaysOnMarket rows are fewer than the 77 rows where
# CloseDate is before ListingContractDate, so the two issues overlap but
# are not identical. 
#

# Date Consistency Checks
sold['listing_after_close_flag'] = sold['ListingContractDate'] > sold['CloseDate']
sold['purchase_after_close_flag'] = sold['PurchaseContractDate'] > sold['CloseDate']
sold['listing_after_purchase_flag'] = sold['ListingContractDate'] > sold['PurchaseContractDate']

# The handbook suggested 'negative_timeline_flag' but I chose the 
# name 'listing_after_purchase_flag' to be accurate to the code.
#

# Checking for date consistency issues
print(sold['listing_after_close_flag'].sum())
print(sold['purchase_after_close_flag'].sum())
print(sold['listing_after_purchase_flag'].sum())
# listing_after_close_flag: 77
# purchase_after_close_flag: 243
# listing_after_purchase_flag: 318

# Rows can appear in more than one flag, so the counts are not additive.
# Flagged rows are kept in the dataset rather than deleted.
#

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
# missing_coordinates_flag: 4801
# zero_coordinate_flag: 46
# positive_Longitude_flag: 35
# out_of_California_flag: 118

# Geographic data quality summary
sold['geo_issue_flag'] = (
    sold['missing_coordinates_flag'] |
    sold['zero_coordinate_flag'] |
    sold['positive_Longitude_flag'] |
    sold['out_of_California_flag']
)
print(sold['geo_issue_flag'].sum())
# geo_issue_flag: 4919

# The zero and positive-longitude rows are a subset of the 118 out-of-California
# rows, so the individual counts are not additive. 
# Flagged rows are kept in the dataset.
#

print(sold.shape[0])
# Row count after: 495407
# Row count is unchanged, since no rows were deleted, only flagged.

print(sold.shape[1])
# Column count after new flag columns: 84

# Cleaned dataset
sold.to_csv(os.path.join("/Users/brianzhao/py", "sold_residential_cleaned.csv"), index=False)