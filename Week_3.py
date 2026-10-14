import pandas as pd
import os

# Fetch mortgage data from FRED
url = "https://fred.stlouisfed.org/graph/fredgraph.csv?id=MORTGAGE30US"
mortgage = pd.read_csv(url, parse_dates=['observation_date'])
mortgage.columns = ['date', 'rate_30yr_fixed']

# Resample weekly rates to monthly averages
mortgage['year_month'] = mortgage['date'].dt.to_period('M')
mortgage_monthly = (
    mortgage.groupby('year_month')['rate_30yr_fixed']
    .mean()
    .reset_index()
)

# Create matching year_month key on MLS datasets
sold = pd.read_csv('/Users/brianzhao/py/combined_sold_residential.csv', low_memory=False)
listings = pd.read_csv('/Users/brianzhao/py/combined_listing_residential.csv', low_memory=False)

sold['year_month'] = pd.to_datetime(sold['CloseDate']).dt.to_period('M')
listings['year_month'] = pd.to_datetime(
    listings['ListingContractDate']
).dt.to_period('M')

# Merge datasets
sold_with_rates = sold.merge(mortgage_monthly, on='year_month', how='left')
listings_with_rates = listings.merge(mortgage_monthly, on='year_month', how='left')

# Null check
print(sold_with_rates['rate_30yr_fixed'].isnull().sum())
print(listings_with_rates['rate_30yr_fixed'].isnull().sum())

# Preview
print(
    sold_with_rates[
        ['CloseDate', 'year_month', 'ClosePrice', 'rate_30yr_fixed']
    ].head()
)

sold_with_rates.to_csv(os.path.join("/Users/brianzhao/py", "sold_residential_with_rates.csv"), index=False)
listings_with_rates.to_csv(os.path.join("/Users/brianzhao/py", "listing_residential_with_rates.csv"), index=False)