"""
ACNC Financial Data Scraper
Gets REAL financial data for charities: revenue, expenses, assets, employees

Data source: https://data.gov.au/dataset/acnc-register
Direct CSV download of ALL Australian charities with full financials
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

# Direct download URL for ACNC register (updated regularly)
ACNC_REGISTER_URL = "https://data.gov.au/data/dataset/b050b242-4487-4306-abf5-07ca073e5594/resource/1c50ad70-2f7e-4dd4-b835-2d91d5f60e3f/download/datadotgov_main.csv"

print(f"📥 Downloading ACNC charity register...")
print(f"   Source: {ACNC_REGISTER_URL}\n")

try:
    # Download with proper headers
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
        'Accept': 'text/csv,application/csv'
    }

    response = requests.get(ACNC_REGISTER_URL, headers=headers, timeout=120, stream=True)
    response.raise_for_status()

    # Save raw file
    raw_file = DATA_DIR / f'acnc_register_{datetime.now().strftime("%Y%m%d")}.csv'

    with open(raw_file, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    print(f"✅ Downloaded to: {raw_file}")
    print(f"   File size: {raw_file.stat().st_size / 1024 / 1024:.1f} MB\n")

    # Load and analyze
    print("🔍 Loading and analyzing data...\n")

    # Try different encodings
    try:
        df = pd.read_csv(raw_file, encoding='utf-8', low_memory=False)
    except:
        try:
            df = pd.read_csv(raw_file, encoding='latin-1', low_memory=False)
        except:
            df = pd.read_csv(raw_file, encoding='iso-8859-1', low_memory=False)

    print(f"✅ Loaded {len(df):,} charities\n")

    print("📋 Available columns:")
    for col in df.columns:
        print(f"   • {col}")
    print()

    # Filter for Queensland
    qld_charities = df[df['State'].str.contains('QLD', case=False, na=False)]
    print(f"🗺️  Queensland charities: {len(qld_charities):,}\n")

    # Filter for Mount Isa region
    mount_isa_postcodes = ['4825', '4823', '4824', '4828']

    # Try different postcode column names
    postcode_cols = [col for col in df.columns if 'post' in col.lower() and 'code' in col.lower()]

    mount_isa_charities = pd.DataFrame()

    if postcode_cols:
        postcode_col = postcode_cols[0]
        print(f"📮 Using postcode column: {postcode_col}")
        mount_isa_charities = df[df[postcode_col].astype(str).isin(mount_isa_postcodes)]

    # Also search by name/location
    name_cols = [col for col in df.columns if 'name' in col.lower() or 'charity' in col.lower()]

    for col in name_cols:
        matches = df[df[col].astype(str).str.contains('Mount Isa|Kalkadoon', case=False, na=False)]
        mount_isa_charities = pd.concat([mount_isa_charities, matches]).drop_duplicates()

    print(f"\n✅ Found {len(mount_isa_charities)} Mount Isa charities\n")

    if len(mount_isa_charities) > 0:
        print("📊 Mount Isa Charities:\n")

        # Show financial data if available
        financial_cols = [col for col in mount_isa_charities.columns
                         if any(term in col.lower() for term in ['revenue', 'income', 'expense', 'asset', 'employee'])]

        for idx, charity in mount_isa_charities.head(20).iterrows():
            # Find name column
            name = None
            for col in ['Charity_Legal_Name', 'Organisation_Name', 'Name']:
                if col in charity.index and pd.notna(charity[col]):
                    name = charity[col]
                    break

            if not name:
                name = str(charity[name_cols[0]]) if name_cols else "Unknown"

            print(f"  • {name}")

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
        output_file = DATA_DIR / f'qld_charities_{datetime.now().strftime("%Y%m%d")}.csv'
        qld_charities.to_csv(output_file, index=False)
        print(f"💾 Saved {len(qld_charities):,} QLD charities for review: {output_file}\n")

    print("="*80)
    print("✅ ACNC SCRAPE COMPLETE")
    print("="*80 + "\n")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    print("\nFallback: Download manually from https://data.gov.au/dataset/acnc-register")
