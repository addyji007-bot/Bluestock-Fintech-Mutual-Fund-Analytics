import requests
import pandas as pd
import os

os.makedirs("data/raw", exist_ok=True)

schemes = {
    "119018": "HDFC_Large_Cap_Direct",
    "119598": "SBI_Large_Cap_Direct",
    "120586": "ICICI_Large_Cap_Direct",
    "118632": "Nippon_Large_Cap_Direct",
    "120465": "Axis_Large_Cap_Direct",
    "120152": "Kotak_Large_Cap_Direct"
}

print("Fetching Live NAV for Key Large Cap Schemes")
print("-" * 60)

for code, name in schemes.items():
    url = f"https://api.mfapi.in/mf/{code}"
    print(f"\nFetching: {name} (Code: {code})")
    
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        meta = data.get("meta", {})
        print(f"  Scheme Name : {meta.get('scheme_name')}")
        print(f"  Fund House  : {meta.get('fund_house')}")
        print(f"  Category    : {meta.get('scheme_category')}")
        
        nav_df = pd.DataFrame(data["data"])
        print(f"  Total records: {len(nav_df)}")
        
        if not nav_df.empty:
            print(f"  Latest NAV  : {nav_df.iloc[0]['nav']} on {nav_df.iloc[0]['date']}")
        
        output_path = f"data/raw/live_{name}_nav.csv"
        nav_df.to_csv(output_path, index=False)
        print(f"  Saved to: {output_path}")
        
    except Exception as e:
        print(f"  Error fetching {name}: {e}")

print("\n" + "-" * 60)
print("All schemes processed.")