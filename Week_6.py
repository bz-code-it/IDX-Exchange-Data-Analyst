import pandas as pd
import os
import geopandas as gpd

data = pd.read_csv('/Users/brianzhao/py/sold_residential_cleaned.csv', low_memory=False)

# Converting date fields to datetime
date_cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']

# Checking date column types before conversion
print(data[date_cols].dtypes)

for col in date_cols:
    data[col] = pd.to_datetime(data[col], errors='coerce')

# Checking date column types after conversion
print(data[date_cols].dtypes)

# Price Ratio Metric 
data['PriceRatio'] = (
    data['ClosePrice'].where(~data['invalid_ClosePrice_flag']) 
    / data['ListPrice'].where(data['ListPrice'] > 0)
)

# Numeric distribution of PriceRatio
print(data['PriceRatio'].describe())

# Close to Original List Ratio Metric
data['CloseToOriginalListRatio'] = (
    data['ClosePrice'].where(~data['invalid_ClosePrice_flag']) 
    / data['OriginalListPrice'].where(data['OriginalListPrice'] > 0)
)

# Numeric distribution of CloseToOriginalListRatio
print(data['CloseToOriginalListRatio'].describe())

# Checking for extremely low house prices
print((data['ClosePrice'] < 1000).sum())
print((data['ListPrice'] < 1000).sum())
print((data['OriginalListPrice'] < 1000).sum())

# Looking at the top 5 PriceRatio values to identify potential outliers
print(data['PriceRatio'].nlargest(5))

# Price Per Sq Ft Metric
data['PricePerSqFt'] = (
    data['ClosePrice'].where(~data['invalid_ClosePrice_flag']) 
    / data['LivingArea'].where(data['LivingArea'] > 0)
)

# Numeric distribution of PricePerSqFt
print(data['PricePerSqFt'].describe())  

# Year Metric
data['Year'] = data['CloseDate'].dt.year

# Month Metric
data['Month'] = data['CloseDate'].dt.month

# YrMo Metric
data['YrMo'] = data['CloseDate'].dt.to_period('M')

# Listing to Contract Date Metric
data['ListingToContractDays'] = (data['PurchaseContractDate'] - data['ListingContractDate']).dt.days

# Numeric distribution of ListingToContractDays
print(data['ListingToContractDays'].describe())

# Contract to Close Date Metric
data['ContractToCloseDays'] = (data['CloseDate'] - data['PurchaseContractDate']).dt.days

# Numeric distribution of ContractToCloseDays
print(data['ContractToCloseDays'].describe())

# School Districts
districts = gpd.read_file('/Users/brianzhao/py/DistrictAreas2425/DistrictAreas2425.shp')

# Repair the few invalid polygon shapes so the join doesn't fail
districts['geometry'] = districts.geometry.make_valid()

# Polygon size, used later to pick the most specific district
districts['poly_area'] = districts.geometry.area
districts = districts[['DistrictNa', 'DistrictTy', 'poly_area', 'geometry']]

# Only rows with usable coordinates get a district (excludes geo_issue_flag rows)
geo_ok = data[~data['geo_issue_flag']]

# Turn Longitude/Latitude into points, then convert the
# points to the polygons' coordinate system so the two line up
points = gpd.GeoDataFrame(
    geometry=gpd.points_from_xy(geo_ok['Longitude'], geo_ok['Latitude']),
    index=geo_ok.index,
    crs='EPSG:4326'
).to_crs(districts.crs)

def assign_district(points, polygons, new_col):
    # Find which polygon each point falls inside
    joined = gpd.sjoin(points, polygons, how='inner', predicate='within')
    # A home can fall inside overlapping polygons
    # Keep the smallest (most specific) one so each home ends up with exactly one district
    joined = joined.sort_values('poly_area')
    joined = joined[~joined.index.duplicated(keep='first')]
    return joined['DistrictNa'].rename(new_col)

# Elementary + Unified districts cover every home
# This is the main column
data['SchoolDistrict'] = assign_district(
    points, districts[districts['DistrictTy'] != 'High'], 'SchoolDistrict')

# High school district (blank for homes in unified districts)
data['HighSchoolDistrictGeo'] = assign_district(
    points, districts[districts['DistrictTy'] == 'High'], 'HighSchoolDistrictGeo')

# Checking row count
print(data.shape[0])                

# Checking the number of homes with valid coordinates matched to a school district
print(data['SchoolDistrict'].notnull().sum(), 'of', len(geo_ok), 'homes with valid coordinates matched')

# Looking at the top 10 school districts by number of homes
print(data['SchoolDistrict'].value_counts().head(10))

# Output Table
print(
    data[[
        'PriceRatio', 'CloseToOriginalListRatio', 'PricePerSqFt', 'DaysOnMarket',
        'Year', 'Month', 'YrMo', 'ListingToContractDays', 'ContractToCloseDays', 'SchoolDistrict'
    ]].head()
)

# Segment Analysis
analysis = data[~data['invalid_ClosePrice_flag']
            & ~data['invalid_LivingArea_flag']
            & ~data['invalid_DaysOnMarket_flag']].copy()

table = analysis.groupby('CountyOrParish').agg(
    Row_Count=('ClosePrice', 'count'),
    Med_ClosePrice = ('ClosePrice', 'median'),
    Med_PPSF = ('PricePerSqFt', 'median'),
    Med_DaysOnMarket = ('DaysOnMarket', 'median'),
    Med_CloseToOriginalListRatio = ('CloseToOriginalListRatio', 'median')
).round(2)

print(table.sort_values(by='Med_ClosePrice', ascending=False).head())

table2 = analysis.groupby('PropertySubType').agg(
    Row_Count=('ClosePrice', 'count'),
    Med_ClosePrice = ('ClosePrice', 'median'),
    Med_PPSF = ('PricePerSqFt', 'median'),
    Med_DaysOnMarket = ('DaysOnMarket', 'median'),
    Med_CloseToOriginalListRatio = ('CloseToOriginalListRatio', 'median')
).round(2)

print(table2.sort_values(by='Med_ClosePrice', ascending=False))

table3 = analysis.groupby('ListOfficeName').agg(
    Sales_Count=('ClosePrice', 'count'),
    Total_Sold=('ClosePrice', 'sum')
).nlargest(10, 'Total_Sold')

print(table3)

data.to_csv(os.path.join("/Users/brianzhao/py", "sold_residential_engineered.csv"), index=False)

