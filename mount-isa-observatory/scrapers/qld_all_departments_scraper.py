"""
Queensland ALL Departments Data Scraper
Systematically downloads data from ALL QLD government departments via CKAN API

Focus: Health, Education, Transport, Resources, Regional Development
"""
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'departments'
DATA_DIR.mkdir(parents=True, exist_ok=True)

CKAN_URL = "https://data.qld.gov.au/api/3/action"

print("\n" + "="*80)
print("🏛️  QUEENSLAND ALL DEPARTMENTS DATA SCRAPER")
print("="*80 + "\n")

# High-value search terms for Mount Isa region
SEARCH_TERMS = [
    # Regional terms
    'north west queensland',
    'north west region',
    'mount isa',
    'regional queensland',
    'remote queensland',

    # Service areas
    'health services',
    'education',
    'hospital',
    'school',
    'infrastructure',
    'transport',
    'mining',
    'resources',

    # Funding
    'grants',
    'funding',
    'budget',
    'expenditure',
    'spending',

    # Indigenous
    'indigenous',
    'aboriginal',
    'torres strait islander',
    'first nations',
]

def search_datasets(query, rows=100):
    """Search CKAN for datasets"""
    url = f"{CKAN_URL}/package_search"
    params = {'q': query, 'rows': rows}

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()['result']['results']
    except Exception as e:
        print(f"   ❌ Error searching '{query}': {e}")
        return []

def get_dataset_resources(dataset_id):
    """Get resources for a dataset"""
    url = f"{CKAN_URL}/package_show"
    params = {'id': dataset_id}

    try:
        response = requests.get(url, params=params, timeout=30)
        response.raise_for_status()
        return response.json()['result']['resources']
    except Exception as e:
        print(f"   ❌ Error getting resources: {e}")
        return []

def download_csv_resource(resource_url, output_file):
    """Download CSV resource"""
    try:
        response = requests.get(resource_url, timeout=120)
        response.raise_for_status()

        # Try to read as CSV
        df = pd.read_csv(resource_url, low_memory=False)
        df.to_csv(output_file, index=False)

        return len(df)
    except Exception as e:
        print(f"      ⚠️  Error downloading: {e}")
        return 0

# Collect all unique datasets
all_datasets = {}

print("🔍 Phase 1: Discovering datasets...\n")

for term in SEARCH_TERMS:
    print(f"Searching: {term}")
    datasets = search_datasets(term, rows=50)

    for dataset in datasets:
        dataset_id = dataset['name']
        if dataset_id not in all_datasets:
            all_datasets[dataset_id] = dataset

    print(f"   Found: {len(datasets)} datasets")
    time.sleep(0.5)  # Rate limiting

print(f"\n✅ Discovered {len(all_datasets)} unique datasets\n")

# Filter for high-priority datasets
print("🎯 Phase 2: Filtering for high-priority datasets...\n")

priority_keywords = [
    'health', 'hospital', 'medical',
    'education', 'school', 'tafe',
    'transport', 'road', 'infrastructure',
    'mining', 'resources', 'royalties',
    'grant', 'funding', 'expenditure', 'budget',
    'contract', 'procurement', 'supplier',
    'indigenous', 'aboriginal',
    'regional', 'remote', 'north west',
]

priority_datasets = []

for dataset_id, dataset in all_datasets.items():
    title = dataset.get('title', '').lower()
    notes = dataset.get('notes', '').lower()

    # Check if contains priority keywords
    if any(keyword in title or keyword in notes for keyword in priority_keywords):
        priority_datasets.append(dataset)

print(f"✅ {len(priority_datasets)} priority datasets identified\n")

# Show dataset categories
orgs = {}
for dataset in priority_datasets:
    org = dataset.get('organization', {}).get('title', 'Unknown')
    orgs[org] = orgs.get(org, 0) + 1

print("📊 Datasets by department:\n")
for org, count in sorted(orgs.items(), key=lambda x: x[1], reverse=True)[:20]:
    print(f"   {org}: {count} datasets")

print()

# Download phase
print("="*80)
print("📥 Phase 3: Downloading high-value datasets")
print("="*80 + "\n")

downloaded = []
total_records = 0

for idx, dataset in enumerate(priority_datasets[:50], 1):  # Limit to top 50
    title = dataset['title']
    dataset_id = dataset['name']
    org = dataset.get('organization', {}).get('title', 'Unknown')

    print(f"{idx}. {title[:60]}...")
    print(f"   Organization: {org}")

    try:
        resources = get_dataset_resources(dataset_id)
        csv_resources = [r for r in resources if r.get('format', '').upper() == 'CSV']

        if not csv_resources:
            print(f"   ⏭️  No CSV resources")
            continue

        print(f"   Found {len(csv_resources)} CSV files")

        # Download first CSV (usually the main one)
        resource = csv_resources[0]
        resource_name = resource.get('name', 'data')

        # Clean filename
        safe_name = "".join(c for c in resource_name if c.isalnum() or c in (' ', '-', '_'))
        safe_org = "".join(c for c in org if c.isalnum() or c in (' ', '-', '_'))

        output_file = DATA_DIR / f"{safe_org}_{safe_name}_{datetime.now().strftime('%Y%m%d')}.csv"

        print(f"   Downloading: {resource_name}")
        records = download_csv_resource(resource['url'], output_file)

        if records > 0:
            print(f"   ✅ {records:,} records saved")
            downloaded.append({
                'dataset': title,
                'organization': org,
                'records': records,
                'file': output_file.name
            })
            total_records += records

    except Exception as e:
        print(f"   ❌ Error: {e}")

    print()

    # Rate limiting and progress
    if idx % 5 == 0:
        print(f"   Progress: {idx}/{len(priority_datasets[:50])}, pausing...\n")
        time.sleep(2)

# Summary
print("="*80)
print("📊 DOWNLOAD SUMMARY")
print("="*80 + "\n")

print(f"Datasets downloaded: {len(downloaded)}")
print(f"Total records: {total_records:,}")
print()

if downloaded:
    print("✅ Downloaded datasets:\n")
    for item in downloaded:
        print(f"   • {item['dataset'][:50]}...")
        print(f"     {item['organization']}")
        print(f"     {item['records']:,} records")
        print()

    # Save manifest
    manifest_df = pd.DataFrame(downloaded)
    manifest_file = DATA_DIR / f'download_manifest_{datetime.now().strftime("%Y%m%d")}.csv'
    manifest_df.to_csv(manifest_file, index=False)

    print(f"💾 Manifest saved: {manifest_file}\n")

print("="*80)
print("✅ DEPARTMENT DATA SCRAPE COMPLETE")
print("="*80 + "\n")

print("🎯 Next steps:")
print("  1. Analyze downloaded data for Mount Isa mentions")
print("  2. Extract financial and service data")
print("  3. Link to existing service records")
print()
