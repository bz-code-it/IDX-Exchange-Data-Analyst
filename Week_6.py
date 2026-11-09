import pandas as pd
import os
import geopandas as gpd

data = pd.read_csv('/Users/brianzhao/py/sold_residential_cleaned.csv', low_memory=False)

# Converting date fields to datetime
date_cols = ['CloseDate', 'PurchaseContractDate', 'ListingContractDate', 'ContractStatusChangeDate']

print(data[date_cols].dtypes)
# CloseDate                   object
# PurchaseContractDate        object
# ListingContractDate         object
# ContractStatusChangeDate    object

for col in date_cols:
    data[col] = pd.to_datetime(data[col], errors='coerce')

print(data[date_cols].dtypes)
# CloseDate                   datetime64[ns]
# PurchaseContractDate        datetime64[ns]
# ListingContractDate         datetime64[ns]
# ContractStatusChangeDate    datetime64[ns]

# Price Ratio Metric 
data['PriceRatio'] = (
    data['ClosePrice'].where(~data['invalid_ClosePrice_flag']) 
    / data['ListPrice'].where(data['ListPrice'] > 0)
)

print(data['PriceRatio'].describe())
# count    4.954020e+05
# mean     1.471028e+00
# std      2.845414e+02
# min      9.591326e-07
# 25%      9.761905e-01
# 50%      1.000000e+00
# 75%      1.018846e+00
# max      2.002000e+05

# Close to Original List Ratio Metric
data['CloseToOriginalListRatio'] = (
    data['ClosePrice'].where(~data['invalid_ClosePrice_flag']) 
    / data['OriginalListPrice'].where(data['OriginalListPrice'] > 0)
)

print(data['CloseToOriginalListRatio'].describe())
# count    4.944930e+05
# mean     5.060218e+01
# std      1.418660e+04
# min      9.207366e-07
# 25%      9.529302e-01
# 50%      9.944444e-01
# 75%      1.018519e+00
# max      9.118000e+06

# Checking for extremely low house prices
print((data['ClosePrice'] < 1000).sum())
print((data['ListPrice'] < 1000).sum())
print((data['OriginalListPrice'] < 1000).sum())
# ClosePrice: 9
# ListPrice: 3
# OriginalListPrice: 159

print(data['PriceRatio'].nlargest(5))
# 476480    200200.000000
# 112197      1153.846154
# 302006      1074.981402
# 164640      1055.555556
# 96391       1022.044088

# Price Per Sq Ft Metric
data['PricePerSqFt'] = (
    data['ClosePrice'].where(~data['invalid_ClosePrice_flag']) 
    / data['LivingArea'].where(data['LivingArea'] > 0)
)

print(data['PricePerSqFt'].describe())  
# count    4.949510e+05
# mean     6.379901e+02
# std      4.631398e+03
# min      4.981497e-04
# 25%      3.672670e+02
# 50%      5.359435e+02
# 75%      7.309547e+02
# max      1.164067e+06

# Days on Market Metric is the DaysOnMarket column we already have in the dataset

# Year Metric
data['Year'] = data['CloseDate'].dt.year

# Month Metric
data['Month'] = data['CloseDate'].dt.month

# YrMo Metric
data['YrMo'] = data['CloseDate'].dt.to_period('M')

# Listing to Contract Date Metric
data['ListingToContractDays'] = (data['PurchaseContractDate'] - data['ListingContractDate']).dt.days

print(data['ListingToContractDays'].describe())
# count    495209.000000
# mean         45.537834
# std          84.370632
# min      -36407.000000
# 25%          10.000000
# 50%          25.000000
# 75%          59.000000
# max       14657.000000

# Contract to Close Date Metric
data['ContractToCloseDays'] = (data['CloseDate'] - data['PurchaseContractDate']).dt.days

print(data['ContractToCloseDays'].describe())
# count    495210.000000
# mean         31.623814
# std          57.978104
# min        -331.000000
# 25%          21.000000
# 50%          29.000000
# 75%          36.000000
# max       36629.000000

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

print(data.shape[0])                
# 495407

print(data['SchoolDistrict'].notnull().sum(), 'of', len(geo_ok), 'homes with valid coordinates matched')
# 490349 of 490488 homes with valid coordinates matched

print(data['SchoolDistrict'].value_counts().head(10))
# SchoolDistrict
# Los Angeles Unified          50338
# San Diego Unified            17963
# Capistrano Unified           10331
# Desert Sands Unified          9490
# Palm Springs Unified          9009
# Long Beach Unified            6940
# Saddleback Valley Unified     6858
# Oakland Unified               5796
# Hemet Unified                 5667
# Corona-Norco Unified          5563

# Output Table
print(
    data[[
        'PriceRatio', 'CloseToOriginalListRatio', 'PricePerSqFt', 'DaysOnMarket',
        'Year', 'Month', 'YrMo', 'ListingToContractDays', 'ContractToCloseDays', 'SchoolDistrict'
    ]].head()
)
#    PriceRatio  CloseToOriginalListRatio  PricePerSqFt  DaysOnMarket  ...     YrMo  ListingToContractDays ContractToCloseDays            SchoolDistrict
# 0    0.813559                  0.480962    210.526316           777  ...  2024-01                  777.0                65.0     San Mateo-Foster City
# 1    1.072510                  1.072510    412.867275            33  ...  2024-01                  114.0               919.0       National Elementary
# 2    1.051948                  1.094743    410.334347           228  ...  2024-01                  255.0               778.0       National Elementary
# 3    1.000000                  1.000000    562.098501             0  ...  2024-01                    0.0                48.0  San Luis Coastal Unified
# 4    1.000000                  1.000000    928.571429           -36  ...  2024-01                   32.0                34.0        Fort Bragg Unified

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
#                 Row_Count  Med_ClosePrice  Med_PPSF  Med_DaysOnMarket  Med_CloseToOriginalListRatio
# CountyOrParish                                                                                     
# San Mateo            8442       1700000.0   1050.79              12.0                          1.01
# Santa Clara         21035       1590000.0    961.54              10.0                          1.02
# Del Norte               2       1465000.0    349.01             195.5                          0.81
# San Francisco        1123       1200000.0    905.64              16.0                          1.01
# Santa Cruz           3560       1189500.0    728.72              18.0                          0.98

table2 = analysis.groupby('PropertySubType').agg(
    Row_Count=('ClosePrice', 'count'),
    Med_ClosePrice = ('ClosePrice', 'median'),
    Med_PPSF = ('PricePerSqFt', 'median'),
    Med_DaysOnMarket = ('DaysOnMarket', 'median'),
    Med_CloseToOriginalListRatio = ('CloseToOriginalListRatio', 'median')
).round(2)

print(table2.sort_values(by='Med_ClosePrice', ascending=False))
#                        Row_Count  Med_ClosePrice  Med_PPSF  Med_DaysOnMarket  Med_CloseToOriginalListRatio
# PropertySubType                                                                                           
# Farm                          17       1425000.0    763.36              20.0                          0.95
# Quadruplex                   185       1250500.0    374.32              32.0                          0.95
# Triplex                      423       1125000.0    467.44              30.0                          0.97
# Duplex                      2777        910000.0    543.43              22.0                          0.98
# SingleFamilyResidence     371069        896111.0    532.55              17.0                          1.00
# Townhouse                  29042        800000.0    557.69              18.0                          1.00
# MixedUse                     246        657500.0    430.00              53.0                          0.93
# Loft                          33        650000.0    539.22              26.0                          0.99
# Condominium                81189        625000.0    561.75              25.0                          0.98
# DeededParking                  6        577500.0    348.41              12.0                          0.99
# MobileHome                    44        555000.0    656.80              68.0                          0.91
# Timeshare                     18        505000.0    187.64              58.0                          0.98
# CoOwnership                   25        400000.0    396.49              24.0                          0.97
# StockCooperative            1939        362500.0    396.97              21.0                          0.98
# ManufacturedOnLand          6398        321750.0    225.54              30.0                          0.97
# Studio                        14        319000.0    668.78              37.5                          0.94
# ManufacturedHome              65        290000.0    185.30              43.0                          0.94
# OwnYourOwn                    68        278000.0    496.92              39.5                          0.95
# Cabin                        584        250000.0    297.88              46.0                          0.92
# BoatSlip                     104        185000.0   1725.00              28.5                          0.94

table3 = analysis.groupby('ListOfficeName').agg(
    Sales_Count=('ClosePrice', 'count'),
    Total_Sold=('ClosePrice', 'sum')
).nlargest(10, 'Total_Sold')

print(table3)
#                                                     Sales_Count    Total_Sold
# ListOfficeName                                                               
# Compass                                                   35090  6.472824e+10
# Coldwell Banker Realty                                    22242  3.684069e+10
# Keller Williams Realty                                     9668  1.001578e+10
# Berkshire Hathaway HomeServices California Prop...         6254  9.469149e+09
# Intero Real Estate Services                                5175  8.512247e+09
# First Team Real Estate                                     6936  7.804807e+09
# The Agency                                                 3283  7.682219e+09
# Coldwell Banker West                                       3243  6.707868e+09
# Real Broker                                                5773  6.099406e+09
# Pacific Sotheby's Int'l Realty                             1994  6.009327e+09

data.to_csv(os.path.join("/Users/brianzhao/py", "sold_residential_engineered.csv"), index=False)

