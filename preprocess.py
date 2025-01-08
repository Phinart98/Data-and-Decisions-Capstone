import pandas as pd
import numpy as np
from datetime import datetime
from tqdm import tqdm

# Read environmental data files
temp_df = pd.read_csv('Datasets/environmental_data_monthly/t_monthly_country_avg.csv')
humid_df = pd.read_csv('Datasets/environmental_data_monthly/r_monthly_country_avg.csv')
ozone_df = pd.read_csv('Datasets/environmental_data_monthly/o3_monthly_country_avg.csv')

# Create Year_Month columns
temp_df['Date_reported'] = pd.to_datetime(temp_df['Date_reported'])
temp_df['Year_Month'] = temp_df['Date_reported'].dt.to_period('M')

humid_df['Date_reported'] = pd.to_datetime(humid_df['Date_reported'])
humid_df['Year_Month'] = humid_df['Date_reported'].dt.to_period('M')

ozone_df['Date_reported'] = pd.to_datetime(ozone_df['Date_reported'])
ozone_df['Year_Month'] = ozone_df['Date_reported'].dt.to_period('M')

# Read control variable data
health_df = pd.read_csv('Datasets/healthcare-coverage-index/Universal_health_Coverage_Service_Coverage_Index.csv')
median_age_df = pd.read_csv('Datasets/sociodemographic-data/median-age/median-age.csv')
urban_pop_df = pd.read_csv('Datasets/sociodemographic-data/long-term-urban-population-region-full/long-term-urban-population-region.csv')

# Get list of African countries
african_countries = temp_df['Country'].unique()

# Process COVID data
covid_data = pd.read_csv('Datasets/covid-data/WHO-COVID-19-global-data.csv')
covid_data['Date_reported'] = pd.to_datetime(covid_data['Date_reported'])

# Create monthly data
covid_monthly = covid_data[covid_data['Country'].isin(african_countries)].copy()
covid_monthly['Year_Month'] = covid_monthly['Date_reported'].dt.to_period('M')
covid_monthly = covid_monthly.groupby(['Country', 'Year_Month']).agg({
    'New_cases': 'sum',
    'New_deaths': 'sum',
    'Cumulative_cases': 'last',
    'Cumulative_deaths': 'last'
}).reset_index()

# Process control variables
health_coverage = health_df[health_df['GEO_NAME_SHORT'].isin(african_countries)]
health_coverage = health_coverage.groupby('GEO_NAME_SHORT')['INDEX_N'].mean().reset_index()
health_coverage.columns = ['Country', 'Health_Coverage_Index']

median_age = median_age_df[median_age_df['Entity'].isin(african_countries)]
median_age = median_age.groupby('Entity')['Median age - Sex: all - Age: all - Variant: estimates'].mean().reset_index()
median_age.columns = ['Country', 'Median_Age']

urban_pop = urban_pop_df[urban_pop_df['Entity'].isin(african_countries)]
urban_pop = urban_pop.groupby('Entity')['Population share in urban areas'].mean().reset_index()
urban_pop.columns = ['Country', 'Urban_Population_Share']

def scale_variables(df):
    # Create scaled versions
    df['Temperature (°C)'] = (df['t_avg'] - 273.15) * -2.5
    df['Relative Humidity (%)'] = df['r_avg'] * 200000
    df['Ozone Concentration (ppb)'] = df['o3_avg'] * 1e7
    df['Cases per Million'] = df['Cases_per_million']
    
    # Remove original columns
    df = df.drop(['t_avg', 'r_avg', 'o3_avg', 'Cases_per_million'], axis=1)
    
    return df

# Merge all data
merged_df = covid_monthly.merge(temp_df, on=['Country', 'Year_Month'], how='left')
merged_df = merged_df.merge(humid_df, on=['Country', 'Year_Month'], how='left')
merged_df = merged_df.merge(ozone_df, on=['Country', 'Year_Month'], how='left')
merged_df = merged_df.merge(health_coverage, on='Country', how='left')
merged_df = merged_df.merge(median_age, on='Country', how='left')
merged_df = merged_df.merge(urban_pop, on='Country', how='left')

# Define regions
north_africa = ['Morocco', 'Algeria', 'Tunisia', 'Libya', 'Egypt']
merged_df['Region'] = np.where(merged_df['Country'].isin(north_africa), 'North Africa', 'Sub-Saharan Africa')

# Calculate cases per million directly
merged_df['Cases_per_million'] = merged_df['New_cases']

# Scale variables before saving
merged_df = scale_variables(merged_df)

# Save processed data
merged_df.to_csv('processed_african_covid_data.csv', index=False)
