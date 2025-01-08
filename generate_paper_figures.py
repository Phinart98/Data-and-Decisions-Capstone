import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os

def create_paper_figures(df):
    os.makedirs('paper_figures', exist_ok=True)
    
    # Data preparation
    df['Year_Month'] = pd.to_datetime(df['Year_Month'].astype(str) + '-01')
    df = df.sort_values('Year_Month')
    
    # Figure 1: Regional Patterns
    plt.figure(figsize=(12, 6))
    sns.boxplot(data=df, x='Region', y='Cases per Million', showfliers=False)
    plt.title('Distribution of COVID-19 Cases Across African Regions (2020-2023)', fontsize=12)
    plt.ylabel('Cases per Million Population')
    plt.tight_layout()
    plt.savefig('paper_figures/figure1_regional_patterns.png')
    plt.close()
    
    # Figure 2: Environmental Effects
    fig, axes = plt.subplots(2, 3, figsize=(18, 12))
    
    # Environmental variables
    for region in df['Region'].unique():
        region_data = df[df['Region'] == region]
        
        # Temperature
        sns.scatterplot(data=region_data, x='Temperature (°C)', y='Cases per Million', 
                       alpha=0.5, label=region, ax=axes[0,0])
        sns.regplot(data=region_data, x='Temperature (°C)', y='Cases per Million',
                   scatter=False, color='red', line_kws={'alpha': 1.0, 'linewidth': 2}, ax=axes[0,0], ci=None)
        
        # Humidity
        sns.scatterplot(data=region_data, x='Relative Humidity (%)', y='Cases per Million',
                       alpha=0.5, label=region, ax=axes[0,1])
        sns.regplot(data=region_data, x='Relative Humidity (%)', y='Cases per Million',
                   scatter=False, color='red', line_kws={'alpha': 1.0, 'linewidth': 2}, ax=axes[0,1], ci=None)
        
        # Ozone
        sns.scatterplot(data=region_data, x='Ozone Concentration (ppb)', y='Cases per Million',
                       alpha=0.5, label=region, ax=axes[0,2])
        sns.regplot(data=region_data, x='Ozone Concentration (ppb)', y='Cases per Million',
                   scatter=False, color='red', line_kws={'alpha': 1.0, 'linewidth': 2}, ax=axes[0,2], ci=None)
        
        # Control variables
        sns.scatterplot(data=region_data, x='Health_Coverage_Index', y='Cases per Million',
                       alpha=0.5, label=region, ax=axes[1,0])
        sns.regplot(data=region_data, x='Health_Coverage_Index', y='Cases per Million',
                   scatter=False, color='red', line_kws={'alpha': 1.0, 'linewidth': 2}, ax=axes[1,0], ci=None)
        
        sns.scatterplot(data=region_data, x='Median_Age', y='Cases per Million',
                       alpha=0.5, label=region, ax=axes[1,1])
        sns.regplot(data=region_data, x='Median_Age', y='Cases per Million',
                   scatter=False, color='red', line_kws={'alpha': 1.0, 'linewidth': 2}, ax=axes[1,1], ci=None)
        
        sns.scatterplot(data=region_data, x='Urban_Population_Share', y='Cases per Million',
                       alpha=0.5, label=region, ax=axes[1,2])
        sns.regplot(data=region_data, x='Urban_Population_Share', y='Cases per Million',
                   scatter=False, color='red', line_kws={'alpha': 1.0, 'linewidth': 2}, ax=axes[1,2], ci=None)
    
    # Update titles for all subplots
    axes[0,0].set_title('Impact of Temperature (°C) on COVID-19 Cases\nNorth vs Sub-Saharan Africa')
    axes[0,1].set_title('Effect of Relative Humidity (%) on COVID-19 Cases\nNorth vs Sub-Saharan Africa')
    axes[0,2].set_title('Relationship between UV Exposure (Ozone ppb)\nand COVID-19 Cases by Region')
    axes[1,0].set_title('Healthcare Coverage Index Impact\non Regional COVID-19 Transmission')
    axes[1,1].set_title('Influence of Population Median Age\non COVID-19 Cases by Region')
    axes[1,2].set_title('Urban Population Share Effect\non COVID-19 Transmission Patterns')
    
    plt.tight_layout()
    plt.savefig('paper_figures/figure2_combined_effects.png')
    plt.close()
    
    # Figure 3: Temporal Trends
    monthly_avg = df.groupby(['Year_Month', 'Region'])[['Cases per Million']].mean().reset_index()
    
    plt.figure(figsize=(15, 8))
    for region in monthly_avg['Region'].unique():
        region_data = monthly_avg[monthly_avg['Region'] == region]
        plt.plot(region_data['Year_Month'], 
                region_data['Cases per Million'].rolling(window=3).mean(),
                label=region, linewidth=2)
    
    plt.title('Evolution of COVID-19 Cases in African Regions (2020-2023)\nThree-Month Moving Average', fontsize=12)
    plt.xlabel('Time Period')
    plt.ylabel('Cases per Million Population')
    plt.legend(title='Region')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('paper_figures/figure3_temporal_trends.png')
    plt.close()
    
    # Figure 4: Seasonal Patterns
    df['Month'] = df['Year_Month'].dt.month
    seasonal = df.groupby(['Region', 'Month'])['Cases per Million'].mean().reset_index()
    
    plt.figure(figsize=(12, 6))
    for region in seasonal['Region'].unique():
        region_data = seasonal[seasonal['Region'] == region]
        plt.plot(region_data['Month'], region_data['Cases per Million'], 
                label=region, marker='o', linewidth=2)
    
    plt.title('Seasonal Patterns in COVID-19 Cases by Region (2020-2023)', fontsize=12)
    plt.xlabel('Month of Year')
    plt.ylabel('Average Cases per Million Population')
    plt.legend(title='Region')
    plt.grid(True, alpha=0.3)
    plt.xticks(range(1,13))
    plt.tight_layout()
    plt.savefig('paper_figures/figure4_seasonal_patterns.png')
    plt.close()

if __name__ == "__main__":
    print("Loading data...")
    df = pd.read_csv('processed_african_covid_data.csv')
    
    print("Generating paper figures...")
    create_paper_figures(df)
    print("Figures generated successfully in 'paper_figures' directory")
