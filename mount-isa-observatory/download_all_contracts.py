"""
Download multiple QLD contract disclosure datasets
"""
import requests
import pandas as pd
from pathlib import Path
import time

print("\n🔍 Downloading Queensland Contract Datasets...\n")

# Get datasets
url = "https://www.data.qld.gov.au/api/3/action/package_search"
params = {'q': 'contract disclosure', 'rows': 50}

response = requests.get(url, params=params, timeout=30)
data = response.json()
datasets = data.get('result', {}).get('results', [])

print(f"Found {len(datasets)} datasets\n")

all_contracts = []
download_dir = Path('data/downloads')
download_dir.mkdir(parents=True, exist_ok=True)

for i, ds in enumerate(datasets[:10], 1):  # Download first 10 datasets
    title = ds.get('title', 'Unknown')
    print(f"{i}. {title}")
    
    for resource in ds.get('resources', []):
        if resource.get('format', '').upper() == 'CSV':
            csv_url = resource.get('url', '')
            if csv_url:
                try:
                    print(f"   Downloading: {resource.get('name', 'file')[:50]}...")
                    df = pd.read_csv(csv_url, low_memory=False)
                    
                    # Add source info
                    df['dataset_source'] = title
                    df['resource_name'] = resource.get('name', '')
                    
                    all_contracts.append(df)
                    print(f"   ✅ {len(df):,} rows")
                    
                except Exception as e:
                    print(f"   ⚠️  Error: {str(e)[:50]}")
    
    print()
    time.sleep(0.5)  # Rate limiting

if all_contracts:
    # Combine all
    combined_df = pd.concat(all_contracts, ignore_index=True)
    output_file = download_dir / 'qld_all_contract_disclosures.csv'
    combined_df.to_csv(output_file, index=False)
    
    print(f"\n✅ Combined {len(combined_df):,} total contracts")
    print(f"💾 Saved: {output_file}\n")
    
    # Search for Mount Isa
    mount_isa_rows = combined_df[
        combined_df.astype(str).apply(
            lambda row: row.str.contains('mount isa|mount-isa|kalkadoon|4825', case=False).any(), 
            axis=1
        )
    ]
    
    print(f"🏔️  Found {len(mount_isa_rows)} rows mentioning Mount Isa!\n")
    
    if len(mount_isa_rows) > 0:
        mount_isa_file = download_dir / 'mount_isa_all_contracts.csv'
        mount_isa_rows.to_csv(mount_isa_file, index=False)
        print(f"💾 Saved Mount Isa contracts: {mount_isa_file}\n")

