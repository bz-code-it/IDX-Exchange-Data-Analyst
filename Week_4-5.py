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

for col in cols:
    sold[col] = pd.to_datetime(sold[col])

print(sold[cols].dtypes)
# CloseDate                   datetime64[ns]
# PurchaseContractDate        datetime64[ns]
# ListingContractDate         datetime64[ns]
# ContractStatusChangeDate    datetime64[ns]

# Remove unnecessary or redundant columns
cols_to_drop = ['AboveGradeFinishedArea', 'CoveredSpaces', 'TaxAnnualAmount', 'TaxYear', 
                'ElementarySchoolDistrict', 'FireplacesTotal', 'MiddleOrJuniorSchoolDistrict', 'BusinessType']
## All these columns have a null percentage of 100

print(sold.shape[1])
# Column count before: 86

sold = sold.drop(columns=cols_to_drop)

print(sold.shape[1])
# Column count after: 78

# Handling missing values
null_counts = sold.isnull().sum()
pd.set_option('display.max_rows', None)
print(null_counts[null_counts > 0])
pd.reset_option('display.max_rows')
print(sold[['latfilled', 'lonfilled', 'Latitude', 'Longitude']])

# Decision: missing values are left as Na across the dataset rather
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
    'StreetNumberNumeric', 'MainLevelBedrooms', 'BuildingAreaTotal',
    'BelowGradeFinishedArea', 'ListingKeyNumeric'
]

# Checking column type
print(sold[numeric_cols].dtypes)
# ClosePrice                float64
# ListPrice                 float64
# OriginalListPrice         float64
# LivingArea                float64
# LotSizeAcres              float64
# LotSizeArea               float64
# LotSizeSquareFeet         float64
# BedroomsTotal             float64
# BathroomsTotalInteger     float64
# YearBuilt                 float64
# DaysOnMarket                int64
# GarageSpaces              float64
# ParkingTotal              float64
# Stories                   float64
# AssociationFee            float64
# Latitude                  float64
# Longitude                 float64
# StreetNumberNumeric       float64
# MainLevelBedrooms         float64
# BuildingAreaTotal         float64
# BelowGradeFinishedArea    float64
# ListingKeyNumeric           int64

# Confirmed: all 22 expected numeric fields are already correctly typed
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
# Bathroms: 0



 