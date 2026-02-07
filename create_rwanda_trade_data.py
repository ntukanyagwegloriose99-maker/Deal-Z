import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Set random seed for reproducibility
np.random.seed(42)

# ============================================================================
# RWANDA MERCHANDISE TRADE INTELLIGENCE - SAMPLE DATASET
# ============================================================================

# Time periods
years = [2021, 2022, 2023, 2024]
months = range(1, 13)
quarters = {1: 'Q1', 2: 'Q1', 3: 'Q1', 4: 'Q2', 5: 'Q2', 6: 'Q2',
           7: 'Q3', 8: 'Q3', 9: 'Q3', 10: 'Q4', 11: 'Q4', 12: 'Q4'}

# Trade flows
flows = ['Export', 'Import', 'Re-export']

# Partner countries (realistic for Rwanda)
export_partners = [
    'Uganda', 'Kenya', 'Tanzania', 'Burundi', 'DRC',
    'United States', 'United Kingdom', 'Germany', 'Belgium', 'Netherlands',
    'China', 'India', 'UAE', 'South Africa', 'Switzerland',
    'France', 'Italy', 'Canada', 'Japan', 'Singapore',
    'Egypt', 'Ghana', 'Nigeria', 'Zambia', 'Zimbabwe'
]

import_partners = [
    'China', 'India', 'UAE', 'Kenya', 'Uganda',
    'Tanzania', 'United States', 'South Africa', 'Germany', 'Japan',
    'United Kingdom', 'Belgium', 'France', 'Netherlands', 'Italy',
    'Saudi Arabia', 'Turkey', 'Thailand', 'Indonesia', 'Brazil',
    'Egypt', 'Morocco', 'Nigeria', 'Zambia', 'Burundi'
]

# Continents
continent_map = {
    'Uganda': 'Africa', 'Kenya': 'Africa', 'Tanzania': 'Africa', 'Burundi': 'Africa', 'DRC': 'Africa',
    'South Africa': 'Africa', 'Egypt': 'Africa', 'Ghana': 'Africa', 'Nigeria': 'Africa',
    'Zambia': 'Africa', 'Zimbabwe': 'Africa', 'Morocco': 'Africa',
    'United States': 'North America', 'Canada': 'North America',
    'China': 'Asia', 'India': 'Asia', 'UAE': 'Asia', 'Japan': 'Asia', 'Singapore': 'Asia',
    'Saudi Arabia': 'Asia', 'Turkey': 'Asia', 'Thailand': 'Asia', 'Indonesia': 'Asia',
    'United Kingdom': 'Europe', 'Germany': 'Europe', 'Belgium': 'Europe', 'Netherlands': 'Europe',
    'Switzerland': 'Europe', 'France': 'Europe', 'Italy': 'Europe',
    'Brazil': 'South America'
}

# Regional blocks
regional_block_map = {
    'Uganda': 'EAC', 'Kenya': 'EAC', 'Tanzania': 'EAC', 'Burundi': 'EAC',
    'DRC': 'COMESA', 'Egypt': 'COMESA', 'Zambia': 'COMESA', 'Zimbabwe': 'COMESA',
    'South Africa': 'SADC', 'Zambia': 'SADC', 'Zimbabwe': 'SADC', 'Tanzania': 'SADC',
    'Nigeria': 'ECOWAS', 'Ghana': 'ECOWAS',
    'China': 'Other', 'India': 'Other', 'UAE': 'Other', 'United States': 'Other',
    'United Kingdom': 'Other', 'Germany': 'EU', 'Belgium': 'EU', 'Netherlands': 'EU',
    'France': 'EU', 'Italy': 'EU', 'Japan': 'Other', 'Singapore': 'Other',
    'Saudi Arabia': 'Other', 'Turkey': 'Other', 'Thailand': 'Other',
    'Indonesia': 'Other', 'Brazil': 'Other', 'Canada': 'Other', 'Switzerland': 'Other',
    'Morocco': 'Other'
}

# HS Codes and Descriptions (Rwanda's main products)
hs_products = {
    # Exports
    'Export': [
        ('0901', 'Coffee (not roasted)'),
        ('0902', 'Tea'),
        ('2608', 'Tin ores and concentrates'),
        ('2613', 'Tantalum ores and concentrates'),
        ('7102', 'Diamonds'),
        ('0709', 'Vegetables (fresh/chilled)'),
        ('0804', 'Dates, figs, pineapples, avocados'),
        ('6109', 'T-shirts, singlets (knitted)'),
        ('6110', 'Jerseys, pullovers (knitted)'),
        ('2710', 'Petroleum oils (refined)'),
        ('8517', 'Telephones/mobile phones'),
        ('2523', 'Cement'),
        ('7326', 'Iron/steel articles'),
        ('8471', 'Data processing equipment'),
        ('0713', 'Dried legumes'),
    ],
    # Imports
    'Import': [
        ('2710', 'Petroleum oils'),
        ('8703', 'Motor cars'),
        ('8704', 'Motor vehicles (goods transport)'),
        ('1001', 'Wheat'),
        ('1006', 'Rice'),
        ('8517', 'Telephones/mobile phones'),
        ('8471', 'Computers/data processing'),
        ('3004', 'Medicaments (packaged)'),
        ('8528', 'Television receivers'),
        ('6203', 'Suits, ensembles (men)'),
        ('6204', 'Suits, ensembles (women)'),
        ('2523', 'Cement'),
        ('7213', 'Iron/steel bars'),
        ('8415', 'Air conditioning machines'),
        ('8716', 'Trailers and semi-trailers'),
    ]
}

# Generate dataset
data = []

for year in years:
    for month in months:
        quarter = quarters[month]
        
        for flow in flows:
            # Select appropriate partners
            if flow == 'Export':
                partners = export_partners
                products = hs_products['Export']
            else:
                partners = import_partners
                products = hs_products['Import']
            
            # Generate records for each partner
            for partner in partners[:20]:  # Top 20 partners per flow
                # Select 3-5 random products per partner
                num_products = np.random.randint(3, 6)
                selected_products = np.random.choice(len(products), num_products, replace=False)
                
                for prod_idx in selected_products:
                    hs_code, hs_desc = products[prod_idx]
                    
                    # Generate realistic trade value
                    base_value = np.random.uniform(50000, 5000000)
                    
                    # Adjust by flow type
                    if flow == 'Export':
                        value_multiplier = 1.0
                    elif flow == 'Import':
                        value_multiplier = 1.3  # Rwanda imports more than exports
                    else:  # Re-export
                        value_multiplier = 0.3  # Smaller re-export flows
                        base_value = np.random.uniform(10000, 500000)
                    
                    # Year-over-year growth
                    year_factor = 1 + (year - 2021) * 0.08  # 8% annual growth
                    
                    # Seasonal variation
                    seasonal_factor = 1 + 0.1 * np.sin(month * np.pi / 6)
                    
                    trade_value = base_value * value_multiplier * year_factor * seasonal_factor
                    
                    # Quantity (in kg)
                    quantity = trade_value / np.random.uniform(2, 20)  # Price per kg varies
                    
                    # Get continent and regional block
                    continent = continent_map.get(partner, 'Other')
                    regional_block = regional_block_map.get(partner, 'Other')
                    
                    data.append({
                        'Year': year,
                        'Month': month,
                        'Quarter': quarter,
                        'Flow': flow,
                        'Partner_Country': partner,
                        'Partner_Continent': continent,
                        'Regional_Block': regional_block,
                        'HS_Code': hs_code,
                        'HS_Description': hs_desc,
                        'Trade_Value_USD': round(trade_value, 2),
                        'Quantity_KG': round(quantity, 2)
                    })

# Create DataFrame
df = pd.DataFrame(data)

# Add month names
month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 5: 'May', 6: 'June',
               7: 'July', 8: 'August', 9: 'September', 10: 'October', 11: 'November', 12: 'December'}
df['Month_Name'] = df['Month'].map(month_names)

# Add date column
df['Date'] = pd.to_datetime(df[['Year', 'Month']].assign(Day=1))

# Sort by date and flow
df = df.sort_values(['Date', 'Flow', 'Partner_Country', 'HS_Code']).reset_index(drop=True)

# Save to Excel and CSV
df.to_excel('rwanda_trade_data.xlsx', index=False)
df.to_csv('rwanda_trade_data.csv', index=False)

# Display summary
print("="*70)
print("RWANDA MERCHANDISE TRADE INTELLIGENCE - SAMPLE DATASET CREATED")
print("="*70)
print(f"\nTotal Records: {len(df):,}")
print(f"Time Period: {df['Year'].min()} - {df['Year'].max()}")
print(f"Months Covered: {df['Month'].nunique()} months per year")
print(f"\nTrade Flows: {df['Flow'].unique().tolist()}")
print(f"Partner Countries: {df['Partner_Country'].nunique()}")
print(f"Continents: {df['Partner_Continent'].nunique()}")
print(f"Regional Blocks: {df['Regional_Block'].nunique()}")
print(f"HS Codes: {df['HS_Code'].nunique()}")
print(f"\nTotal Trade Value: ${df['Trade_Value_USD'].sum():,.2f}")
print(f"Average Monthly Trade: ${df.groupby(['Year', 'Month'])['Trade_Value_USD'].sum().mean():,.2f}")

print("\n" + "="*70)
print("FILES CREATED:")
print("  - rwanda_trade_data.xlsx")
print("  - rwanda_trade_data.csv")
print("="*70)

# Show sample data
print("\nSAMPLE DATA (First 10 rows):")
print(df.head(10).to_string())

print("\n\nTRADE SUMMARY BY FLOW:")
print(df.groupby('Flow')['Trade_Value_USD'].sum().sort_values(ascending=False))

print("\n\nTOP 10 EXPORT DESTINATIONS:")
exports = df[df['Flow'] == 'Export'].groupby('Partner_Country')['Trade_Value_USD'].sum().sort_values(ascending=False).head(10)
print(exports)

print("\n\nTOP 10 IMPORT ORIGINS:")
imports = df[df['Flow'] == 'Import'].groupby('Partner_Country')['Trade_Value_USD'].sum().sort_values(ascending=False).head(10)
print(imports)
