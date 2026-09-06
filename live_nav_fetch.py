import requests
import pandas as pd
import json
from datetime import datetime
import os

# Create raw folder if not exists (safety)
os.makedirs("data/raw", exist_ok=True)

# API endpoint for HDFC Top 100 Direct Growth
url = "https://api.mfapi.in/mf/119018"

print("Fetching live NAV data for HDFC Top 100 Direct (Code: 119018)...")
print(f"URL: {url}")

try:
    response = requests.get(url, timeout=30)
    response.raise_for_status()  # Raise error if request failed
    
    data = response.json()
    
    # Print basic info
    print("\n--- Meta Information ---")
    print(f"Scheme Code : {data['meta']['scheme_code']}")
    print(f"Scheme Name : {data['meta']['scheme_name']}")
    print(f"Fund House  : {data['meta']['fund_house']}")
    print(f"Scheme Type : {data['meta']['scheme_type']}")
    print(f"Scheme Category : {data['meta']['scheme_category']}")
    
    # Convert NAV history to DataFrame
    nav_df = pd.DataFrame(data['data'])
    
    print(f"\nTotal NAV records fetched: {len(nav_df)}")
    print("\nLatest 5 NAV records:")
    print(nav_df.head())
    
    # Save as CSV in data/raw
    output_path = "data/raw/live_hdfc_top100_nav.csv"
    nav_df.to_csv(output_path, index=False)
    
    print(f"\n Successfully saved to: {output_path}")
    
except requests.exceptions.RequestException as e:
    print(f" Network/API Error: {e}")
except Exception as e:
    print(f" Unexpected Error: {e}")