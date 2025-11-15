"""
Queensland Government Contracts Scraper
Gets ALL QLD government contracts with suppliers in Mount Isa region

Data source: https://data.qld.gov.au/dataset/qld-government-contracts
Real government spending data: contracts, suppliers, amounts
"""
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'contracts'
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*80)
print("📑 QUEENSLAND GOVERNMENT CONTRACTS SCRAPER")
print("="*80 + "\n")

# Queensland Open Data Portal CKAN API
CKAN_URL = "https://data.qld.gov.au/api/3/action"

def search_datasets(query):
    """Search for datasets in QLD open data portal"""
    url = f"{CKAN_URL}/package_search"
    params = {
        'q': query,
        'rows': 10
    }

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    return response.json()

def get_dataset_resources(dataset_id):
    """Get all resources (files) for a dataset"""
    url = f"{CKAN_URL}/package_show"
    params = {'id': dataset_id}

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data['result']['resources']

def download_resource(resource_url):
    """Download a CSV resource"""
    response = requests.get(resource_url, timeout=120)
    response.raise_for_status()

    return pd.read_csv(response.url if hasattr(response, 'url') else resource_url)

# Search for contracts datasets
print("🔍 Searching for Queensland contracts datasets...\n")

search_queries = [
    'government contracts',
    'procurement',
    'tenders',
    'contracts register'
]

all_datasets = []

for query in search_queries:
    print(f"   Searching: {query}")
    try:
        result = search_datasets(query)
        datasets = result['result']['results']
        all_datasets.extend(datasets)
        print(f"   Found: {len(datasets)} datasets")
    except Exception as e:
        print(f"   Error: {e}")

print(f"\n✅ Found {len(all_datasets)} total datasets\n")

# Look for contracts-specific datasets
contracts_datasets = []

for dataset in all_datasets:
    title = dataset.get('title', '').lower()
    name = dataset.get('name', '').lower()

    if any(term in title or term in name for term in ['contract', 'procurement', 'supplier']):
        contracts_datasets.append(dataset)
        print(f"📋 {dataset['title']}")
        print(f"   ID: {dataset['name']}")
        print(f"   Organization: {dataset.get('organization', {}).get('title', 'Unknown')}")
        print()

if not contracts_datasets:
    print("⚠️  No contracts datasets found")
    print("\nTrying direct download URLs...\n")

    # Known QLD contracts data URLs
    known_urls = [
        {
            'name': 'QLD Government Contracts',
            'url': 'https://data.qld.gov.au/dataset/qld-government-contracts',
            'csv_urls': [
                'https://www.hpw.qld.gov.au/__data/assets/file/0026/6227/hpw-contract-disclosure-2023.csv',
                'https://www.hpw.qld.gov.au/__data/assets/file/0025/6226/hpw-contract-disclosure-2022.csv',
            ]
        }
    ]

    all_contracts = []

    for source in known_urls:
        print(f"📥 Downloading: {source['name']}\n")

        for csv_url in source['csv_urls']:
            try:
                print(f"   Downloading: {csv_url}")
                df = pd.read_csv(csv_url)
                print(f"   ✅ Loaded {len(df)} contracts")

                # Add source information
                df['data_source'] = source['name']
                df['download_date'] = datetime.now().isoformat()

                all_contracts.append(df)

            except Exception as e:
                print(f"   ⚠️  Error: {e}")

    if all_contracts:
        # Combine all contract data
        combined_df = pd.concat(all_contracts, ignore_index=True)

        print(f"\n✅ Total contracts loaded: {len(combined_df):,}\n")

        # Show columns
        print("📋 Available columns:")
        for col in combined_df.columns:
            print(f"   • {col}")
        print()

        # Filter for Mount Isa region
        print("🔍 Filtering for Mount Isa region...\n")

        # Search in multiple fields
        mount_isa_contracts = pd.DataFrame()

        search_fields = [col for col in combined_df.columns
                        if any(term in col.lower() for term in ['supplier', 'contractor', 'name', 'location', 'address'])]

        for field in search_fields:
            if field in combined_df.columns:
                matches = combined_df[
                    combined_df[field].astype(str).str.contains(
                        'Mount Isa|4825|Kalkadoon',
                        case=False,
                        na=False
                    )
                ]

                mount_isa_contracts = pd.concat([mount_isa_contracts, matches]).drop_duplicates()

        print(f"✅ Found {len(mount_isa_contracts)} Mount Isa contracts\n")

        if len(mount_isa_contracts) > 0:
            print("="*80)
            print("📊 MOUNT ISA CONTRACTS")
            print("="*80 + "\n")

            # Try to find amount/value columns
            value_cols = [col for col in mount_isa_contracts.columns
                         if any(term in col.lower() for term in ['value', 'amount', 'price', 'cost'])]

            for idx, contract in mount_isa_contracts.head(20).iterrows():
                # Find key fields
                supplier = None
                for col in ['Supplier', 'Contractor', 'Supplier Name', 'Company Name']:
                    if col in contract.index and pd.notna(contract[col]):
                        supplier = contract[col]
                        break

                print(f"  {idx + 1}. {supplier or 'Unknown supplier'}")

                # Show contract value if available
                for col in value_cols:
                    if pd.notna(contract[col]):
                        print(f"     {col}: {contract[col]}")

                # Show other key details
                for col in ['Description', 'Contract Description', 'Purpose']:
                    if col in contract.index and pd.notna(contract[col]):
                        desc = str(contract[col])[:100]
                        print(f"     {col}: {desc}...")
                        break

                print()

            # Calculate totals if possible
            if value_cols:
                for col in value_cols:
                    if mount_isa_contracts[col].dtype in ['int64', 'float64']:
                        total = mount_isa_contracts[col].sum()
                        if total > 0:
                            print(f"💰 Total {col}: ${total:,.0f}\n")

            # Save Mount Isa contracts
            output_file = DATA_DIR / f'mount_isa_contracts_{datetime.now().strftime("%Y%m%d")}.csv'
            mount_isa_contracts.to_csv(output_file, index=False)
            print(f"💾 Saved: {output_file}\n")

        else:
            print("⚠️  No Mount Isa contracts found")
            print("\nThis could mean:")
            print("  • Contracts don't include supplier location")
            print("  • Need to search by different criteria")
            print("  • Mount Isa suppliers use different names/addresses\n")

            # Save all QLD contracts for manual review
            output_file = DATA_DIR / f'qld_all_contracts_{datetime.now().strftime("%Y%m%d")}.csv'
            combined_df.to_csv(output_file, index=False)
            print(f"💾 Saved {len(combined_df):,} QLD contracts: {output_file}\n")

else:
    # Download from found datasets
    print(f"\n📥 Downloading contracts from {len(contracts_datasets)} datasets...\n")

    all_contracts = []

    for dataset in contracts_datasets[:10]:  # Download from first 10 datasets
        print(f"Processing: {dataset['title']}")

        try:
            resources = get_dataset_resources(dataset['name'])
            print(f"   Found {len(resources)} resources")

            for resource in resources:
                if resource.get('format', '').upper() == 'CSV':
                    print(f"   Downloading: {resource['name']}")
                    df = download_resource(resource['url'])
                    all_contracts.append(df)
                    print(f"   ✅ {len(df)} records")

        except Exception as e:
            print(f"   ⚠️  Error: {e}")

        print()

    # Save all downloaded contracts
    if all_contracts:
        combined_df = pd.concat(all_contracts, ignore_index=True)
        output_file = DATA_DIR / f'qld_all_contracts_{datetime.now().strftime("%Y%m%d")}.csv'
        combined_df.to_csv(output_file, index=False)
        print(f"💾 Saved {len(combined_df):,} contracts: {output_file}\n")

print("="*80)
print("✅ QLD CONTRACTS SCRAPE COMPLETE")
print("="*80 + "\n")
