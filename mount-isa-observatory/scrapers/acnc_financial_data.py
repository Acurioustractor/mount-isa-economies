"""
ACNC Financial Data Scraper
Gets REAL financial data for charities: revenue, expenses, assets, employees

Data source: https://data.gov.au/dataset/acnc-register
Uses CKAN API to reliably download ACNC charity register
"""
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'acnc_financials'
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*80)
print("💰 ACNC FINANCIAL DATA SCRAPER")
print("="*80 + "\n")

# data.gov.au CKAN API (same approach that worked for QLD contracts)
CKAN_URL = "https://data.gov.au/api/3/action"
ACNC_DATASET_ID = "acnc-register"

def get_dataset_resources(dataset_id):
    """Get all resources (files) for a dataset"""
    url = f"{CKAN_URL}/package_show"
    params = {'id': dataset_id}

    response = requests.get(url, params=params, timeout=30)
    response.raise_for_status()

    data = response.json()
    return data['result']['resources']

def download_csv(resource_url, output_file):
    """Download a CSV resource"""
    print(f"📥 Downloading: {resource_url}")

    response = requests.get(resource_url, timeout=120, stream=True)
    response.raise_for_status()

    with open(output_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Downloaded: {output_file.name}")
    print(f"   File size: {output_file.stat().st_size / 1024 / 1024:.1f} MB\n")

    return output_file

try:
    # 1. Get ACNC dataset resources
    print("🔍 Finding ACNC charity register dataset...\n")

    resources = get_dataset_resources(ACNC_DATASET_ID)
    print(f"✅ Found {len(resources)} resources in ACNC dataset\n")

    # 2. Find the main charity register CSV
    charity_register = None

    for resource in resources:
        name = resource.get('name', '').lower()
        format = resource.get('format', '').upper()

        print(f"   • {resource['name']} ({format})")

        # Look for main register CSV
        if format == 'CSV' and any(term in name for term in ['register', 'charity', 'main']):
            if not any(skip in name for skip in ['notes', 'guide', 'metadata', 'user']):
                charity_register = resource
                print(f"     ⭐ This looks like the main register!\n")

    if not charity_register:
        print("\n⚠️  Couldn't identify main register, using first CSV resource")
        charity_register = next((r for r in resources if r.get('format', '').upper() == 'CSV'), None)

    if not charity_register:
        raise Exception("No CSV resources found in ACNC dataset")

    print(f"\n📋 Using resource: {charity_register['name']}")
    print(f"   Format: {charity_register.get('format')}")
    print(f"   Last modified: {charity_register.get('last_modified', 'Unknown')}\n")

    # 3. Download the CSV
    raw_file = DATA_DIR / f'acnc_register_{datetime.now().strftime("%Y%m%d")}.csv'
    download_csv(charity_register['url'], raw_file)

    # 4. Load and analyze
    print("🔍 Loading and analyzing data...\n")

    # Try different encodings
    df = None
    for encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']:
        try:
            df = pd.read_csv(raw_file, encoding=encoding, low_memory=False)
            print(f"✅ Loaded with {encoding} encoding\n")
            break
        except Exception as e:
            continue

    if df is None:
        raise Exception("Could not load CSV with any encoding")

    print(f"✅ Loaded {len(df):,} charities\n")

    print("📋 Available columns:")
    for col in df.columns:
        print(f"   • {col}")
    print()

    # 5. Filter for Queensland
    state_cols = [col for col in df.columns if 'state' in col.lower()]

    qld_charities = pd.DataFrame()
    if state_cols:
        state_col = state_cols[0]
        print(f"🗺️  Using state column: {state_col}")
        qld_charities = df[df[state_col].astype(str).str.contains('QLD|Queensland', case=False, na=False)]
        print(f"   Found {len(qld_charities):,} Queensland charities\n")

    # 6. Filter for Mount Isa region
    print("🔍 Searching for Mount Isa charities...\n")

    mount_isa_postcodes = ['4825', '4823', '4824', '4828']
    mount_isa_charities = pd.DataFrame()

    # Try different postcode column names
    postcode_cols = [col for col in df.columns if 'post' in col.lower() and 'code' in col.lower()]

    if postcode_cols:
        postcode_col = postcode_cols[0]
        print(f"📮 Using postcode column: {postcode_col}")
        mount_isa_charities = df[df[postcode_col].astype(str).isin(mount_isa_postcodes)]

    # Also search by name/location
    text_cols = [col for col in df.columns
                 if any(term in col.lower() for term in ['name', 'charity', 'address', 'suburb', 'town'])]

    for col in text_cols:
        matches = df[df[col].astype(str).str.contains('Mount Isa|Kalkadoon', case=False, na=False)]
        mount_isa_charities = pd.concat([mount_isa_charities, matches]).drop_duplicates()

    print(f"✅ Found {len(mount_isa_charities)} Mount Isa charities\n")

    # 7. Display and save results
    if len(mount_isa_charities) > 0:
        print("="*80)
        print("📊 MOUNT ISA CHARITIES")
        print("="*80 + "\n")

        # Find name column
        name_cols = [col for col in mount_isa_charities.columns
                    if 'name' in col.lower() and 'charity' in col.lower()]
        if not name_cols:
            name_cols = [col for col in mount_isa_charities.columns if 'name' in col.lower()]

        name_col = name_cols[0] if name_cols else mount_isa_charities.columns[0]

        # Show financial data if available
        financial_cols = [col for col in mount_isa_charities.columns
                         if any(term in col.lower() for term in ['revenue', 'income', 'expense', 'asset', 'employee', 'staff', 'volunteer'])]

        for idx, charity in mount_isa_charities.head(20).iterrows():
            name = str(charity[name_col]) if pd.notna(charity[name_col]) else "Unknown"
            print(f"  • {name}")

            # Show address/postcode
            if postcode_cols and pd.notna(charity[postcode_cols[0]]):
                print(f"    Postcode: {charity[postcode_cols[0]]}")

            # Show financial data if available
            for col in financial_cols[:5]:  # Show first 5 financial columns
                if pd.notna(charity[col]) and charity[col] != 0:
                    print(f"    {col}: {charity[col]}")
            print()

        # Save Mount Isa charities
        output_file = DATA_DIR / f'mount_isa_charities_{datetime.now().strftime("%Y%m%d")}.csv'
        mount_isa_charities.to_csv(output_file, index=False)
        print(f"💾 Saved Mount Isa charities: {output_file}\n")

        # Calculate statistics
        if financial_cols:
            print("="*80)
            print("📈 FINANCIAL SUMMARY")
            print("="*80 + "\n")

            for col in financial_cols:
                if mount_isa_charities[col].dtype in ['int64', 'float64']:
                    total = mount_isa_charities[col].sum()
                    avg = mount_isa_charities[col].mean()
                    count = mount_isa_charities[col].notna().sum()

                    if total > 0:
                        print(f"{col}:")
                        print(f"  Total: ${total:,.0f}")
                        print(f"  Average: ${avg:,.0f}")
                        print(f"  Charities reporting: {count}")
                        print()

    else:
        print("⚠️  No Mount Isa charities found in ACNC register")
        print("\nPossible reasons:")
        print("  • Charities registered in other locations but operate in Mount Isa")
        print("  • Need to search by service area rather than postal address")
        print("  • Column names different than expected\n")

        # Save full QLD data for manual review
        if len(qld_charities) > 0:
            output_file = DATA_DIR / f'qld_charities_{datetime.now().strftime("%Y%m%d")}.csv'
            qld_charities.to_csv(output_file, index=False)
            print(f"💾 Saved {len(qld_charities):,} QLD charities for review: {output_file}\n")

    print("="*80)
    print("✅ ACNC SCRAPE COMPLETE")
    print("="*80 + "\n")

    print("💡 Next steps:")
    print("  1. Review Mount Isa charities for financial data")
    print("  2. Cross-reference with existing services database")
    print("  3. Download Annual Information Statement data for detailed financials")
    print("  4. Track charity programs and service delivery areas\n")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\n💡 Manual fallback:")
    print("  1. Visit: https://data.gov.au/dataset/acnc-register")
    print("  2. Download CSV files manually")
    print("  3. Place in mount-isa-observatory/data/acnc_financials/\n")
