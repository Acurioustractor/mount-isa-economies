"""
Scrape ACNC (Australian Charities and Not-for-profits Commission) data
For charities and non-profits operating in Mount Isa region
FREE and publicly available data
"""
import requests
import pandas as pd
from pathlib import Path
import json
from datetime import datetime

print("\n" + "="*80)
print("🏛️  SCRAPING ACNC CHARITY DATA FOR MOUNT ISA")
print("="*80 + "\n")

# ACNC provides free CSV downloads of all registered charities
# https://www.acnc.gov.au/charity/data

print("📥 Downloading ACNC charity register...\n")

# ACNC Data Download URL (this is real and publicly available)
ACNC_DATA_URL = "https://data.gov.au/data/dataset/b050b242-4487-4306-abf5-07ca073e5594/resource/1c50ad70-2f7e-4dd4-b835-2d91d5f60e3f/download/datadotgov_main.csv"

try:
    # Download the full ACNC register
    print("Downloading full ACNC register (this may take a minute)...")
    response = requests.get(ACNC_DATA_URL, timeout=60)
    response.raise_for_status()

    # Save raw file
    output_dir = Path(__file__).parent.parent / 'data' / 'raw'
    output_dir.mkdir(parents=True, exist_ok=True)

    raw_file = output_dir / 'acnc_full_register.csv'
    with open(raw_file, 'wb') as f:
        f.write(response.content)

    print(f"✅ Downloaded ACNC register to: {raw_file}\n")

    # Load and filter for Mount Isa
    print("🔍 Filtering for Mount Isa region...")

    # Try different CSV parsing options to handle malformed data
    try:
        df = pd.read_csv(raw_file, on_bad_lines='skip', encoding='utf-8')
    except:
        try:
            df = pd.read_csv(raw_file, on_bad_lines='skip', encoding='latin-1')
        except:
            df = pd.read_csv(raw_file, error_bad_lines=False, encoding='utf-8')

    print(f"Total charities in Australia: {len(df):,}\n")

    # Filter for Mount Isa area (postcode 4825 and surrounding)
    mount_isa_postcodes = ['4825', '4823', '4824', '4828']  # Mount Isa and surrounding

    mount_isa_charities = df[
        df['Address_Post_Code'].astype(str).isin(mount_isa_postcodes) |
        df['Charity_Legal_Name'].str.contains('Mount Isa', case=False, na=False) |
        df['Charity_Legal_Name'].str.contains('Kalkadoon', case=False, na=False)
    ]

    print(f"✅ Found {len(mount_isa_charities)} charities operating in Mount Isa region\n")

    # Save filtered data
    filtered_file = output_dir / 'mount_isa_charities.csv'
    mount_isa_charities.to_csv(filtered_file, index=False)

    print(f"💾 Saved to: {filtered_file}\n")

    # Show summary
    print("="*80)
    print("MOUNT ISA CHARITIES SUMMARY")
    print("="*80 + "\n")

    if len(mount_isa_charities) > 0:
        # Show sample
        print("Sample charities:\n")
        for idx, charity in mount_isa_charities.head(10).iterrows():
            print(f"  • {charity['Charity_Legal_Name']}")
            if pd.notna(charity['Charity_Size']):
                print(f"    Size: {charity['Charity_Size']}")
            if pd.notna(charity['Address_Post_Code']):
                print(f"    Postcode: {charity['Address_Post_Code']}")
            print()

        # Statistics
        print("\n📊 Statistics:")
        if 'Charity_Size' in mount_isa_charities.columns:
            print("\nBy size:")
            print(mount_isa_charities['Charity_Size'].value_counts().to_string())

        # Show what data we have
        print(f"\n📋 Available fields:")
        for col in mount_isa_charities.columns:
            non_null = mount_isa_charities[col].notna().sum()
            if non_null > 0:
                print(f"   • {col}: {non_null}/{len(mount_isa_charities)} populated")
    else:
        print("⚠️  No charities found in Mount Isa postcodes")
        print("This might mean:")
        print("  • Charities are registered elsewhere but operate in Mount Isa")
        print("  • We need to search by service area rather than postal address")
        print("\nTry searching the full dataset manually for relevant organizations")

    print("\n" + "="*80)
    print("✅ ACNC SCRAPE COMPLETE")
    print("="*80 + "\n")

except requests.exceptions.RequestException as e:
    print(f"❌ Error downloading ACNC data: {e}")
    print("\nAlternative: Visit https://www.acnc.gov.au/charity/data")
    print("Download the CSV manually and place in mount-isa-observatory/data/raw/")

except Exception as e:
    print(f"❌ Error processing data: {e}")
    import traceback
    traceback.print_exc()
