import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib.pyplot as plt
import seaborn as sns
from scipy import stats

def calculate_paper_statistics(df):
    # Prepare regression variables - using already scaled variables
    X = pd.DataFrame({
        'Temperature': df['Temperature (°C)'],
        'Humidity': df['Relative Humidity (%)'],
        'UV_Exposure': df['Ozone Concentration (ppb)'],
        'Health_Coverage': df['Health_Coverage_Index'],
        'Median_Age': df['Median_Age'],
        'Urban_Population': df['Urban_Population_Share']
    })

    # Clean data and add constant
    X = X.dropna()
    y = df['Cases per Million'][X.index]
    X = sm.add_constant(X)

    # Run main regression
    model = sm.OLS(y, X)
    results = model.fit(cov_type='HC3')

    # Regional analysis
    north_africa = df[df['Region'] == 'North Africa']['Cases per Million'].dropna()
    sub_saharan = df[df['Region'] == 'Sub-Saharan Africa']['Cases per Million'].dropna()
    t_stat, p_value = stats.ttest_ind(north_africa, sub_saharan)

    # Create correlation matrix
    correlation_vars = ['Cases per Million', 'Temperature (°C)', 'Relative Humidity (%)', 
                       'Ozone Concentration (ppb)', 'Health_Coverage_Index', 
                       'Median_Age', 'Urban_Population_Share']
    correlations = df[correlation_vars].corr()

    # Save comprehensive results
    with open('paper_statistics.txt', 'w') as f:
        f.write("COVID-19 Transmission Analysis in African Regions (2020-2023)\n")
        f.write("=" * 80 + "\n\n")

        f.write("1. Model Specification\n")
        f.write("-" * 40 + "\n")
        f.write("Cases_per_million = b0 + b1(Temperature) + b2(Humidity) + b3(UV_Exposure) +\n")
        f.write("                    b4(Health_Coverage) + b5(Median_Age) + b6(Urban_Population) + e\n\n")

        f.write("2. Summary Statistics by Variable\n")
        f.write("-" * 40 + "\n")
        f.write(df[correlation_vars].describe().to_string() + "\n\n")

        f.write("3. Regional Comparison (T-test)\n")
        f.write("-" * 40 + "\n")
        f.write(f"T-statistic: {t_stat:.4f}\n")
        f.write(f"P-value: {p_value:.4f}\n\n")

        f.write("4. Correlation Matrix\n")
        f.write("-" * 40 + "\n")
        f.write(correlations.round(3).to_string() + "\n\n")

        f.write("5. Regression Results\n")
        f.write("-" * 40 + "\n")
        f.write(results.summary().as_text() + "\n\n")

        # Additional regional statistics
        f.write("6. Regional Summary Statistics\n")
        f.write("-" * 40 + "\n")
        f.write(df.groupby('Region')[correlation_vars].agg(['mean', 'std']).round(3).to_string())

    # Create visualization of regression results
    plt.figure(figsize=(12, 8))
    coef_df = pd.DataFrame({
        'Variable': X.columns[1:],  # Exclude constant
        'Coefficient': results.params[1:],
        'CI_Lower': results.conf_int()[0][1:],
        'CI_Upper': results.conf_int()[1][1:]
    })
    
    sns.barplot(data=coef_df, x='Variable', y='Coefficient')
    plt.errorbar(x=range(len(coef_df)), 
                y=coef_df['Coefficient'],
                yerr=[coef_df['Coefficient'] - coef_df['CI_Lower'], 
                      coef_df['CI_Upper'] - coef_df['Coefficient']],
                fmt='none', color='black', capsize=5)
    
    plt.xticks(rotation=45)
    plt.title('Regression Coefficients with 95% Confidence Intervals')
    plt.tight_layout()
    plt.savefig('regression_coefficients.png')
    plt.close()

if __name__ == "__main__":
    print("Loading data...")
    df = pd.read_csv('processed_african_covid_data.csv')
    
    print("Calculating statistics...")
    calculate_paper_statistics(df)
    print("Statistics saved to 'paper_statistics.txt'")
