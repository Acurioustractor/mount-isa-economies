"""
Scrape GrantConnect for grants to Mount Isa organizations
GrantConnect is the Australian Government's grants information system
FREE and publicly available
"""
import requests
import pandas as pd
from pathlib import Path
import json
from datetime import datetime
from bs4 import BeautifulSoup
import time

print("\n" + "="*80)
print("💰 SCRAPING GRANTCONNECT FOR MOUNT ISA GRANTS")
print("="*80 + "\n")

# GrantConnect provides a public API
# https://www.grants.gov.au/

output_dir = Path(__file__).parent.parent / 'data' / 'raw'
output_dir.mkdir(parents=True, exist_ok=True)

# Method 1: Search GrantConnect website for Mount Isa
GRANTCONNECT_SEARCH_URL = "https://www.grants.gov.au/"

print("🔍 Searching GrantConnect for Mount Isa grants...\n")

# Search terms that might find Mount Isa grants
search_terms = [
    "Mount Isa",
    "Kalkadoon",
    "North West Queensland",
    "4825",  # Mount Isa postcode
]

all_grants = []

try:
    # Method 2: Use GrantConnect's data.gov.au dataset
    # This is the actual public dataset
    GRANTS_DATA_URL = "https://data.gov.au/data/api/3/action/datastore_search"

    print("📥 Accessing GrantConnect open data via data.gov.au API...\n")

    # Search for grants in Queensland/North West region
    params = {
        'resource_id': 'c7e26722-f79a-4e66-b27d-6e63a13a5d31',  # GrantConnect dataset ID
        'limit': 1000,
        'q': 'Queensland'  # Start with Queensland, then filter
    }

    response = requests.get(GRANTS_DATA_URL, params=params, timeout=30)

    if response.status_code == 200:
        data = response.json()

        if data.get('success'):
            records = data.get('result', {}).get('records', [])
            print(f"✅ Retrieved {len(records)} Queensland grants from GrantConnect\n")

            # Filter for Mount Isa region
            mount_isa_grants = []

            for record in records:
                # Check if grant mentions Mount Isa, Kalkadoon, or relevant areas
                record_text = json.dumps(record).lower()

                if any(term.lower() in record_text for term in search_terms):
                    mount_isa_grants.append(record)

            print(f"✅ Found {len(mount_isa_grants)} grants mentioning Mount Isa region\n")

            if len(mount_isa_grants) > 0:
                # Convert to DataFrame
                df = pd.DataFrame(mount_isa_grants)

                # Save
                output_file = output_dir / 'mount_isa_grants_grantconnect.csv'
                df.to_csv(output_file, index=False)

                print(f"💾 Saved to: {output_file}\n")

                # Show summary
                print("="*80)
                print("GRANT SUMMARY")
                print("="*80 + "\n")

                print("Sample grants:\n")
                for idx, grant in enumerate(mount_isa_grants[:10], 1):
                    print(f"{idx}. {grant.get('title', 'Untitled grant')}")
                    if 'amount' in grant:
                        print(f"   Amount: ${grant['amount']:,}")
                    if 'recipient' in grant:
                        print(f"   Recipient: {grant['recipient']}")
                    if 'year' in grant:
                        print(f"   Year: {grant['year']}")
                    print()

                # Calculate total if amounts available
                if 'amount' in df.columns:
                    total = df['amount'].sum()
                    print(f"💰 Total grant funding: ${total:,.0f}\n")

            else:
                print("⚠️  No grants found with direct Mount Isa mentions")
                print("This might mean we need to:")
                print("  • Search by program name instead of location")
                print("  • Look at Queensland government grants separately")
                print("  • Check state-level funding databases\n")

        else:
            print("❌ API returned unsuccessful response")

    else:
        print(f"❌ API request failed: {response.status_code}")

except requests.exceptions.RequestException as e:
    print(f"❌ Error accessing GrantConnect API: {e}")
    print("\n📝 Alternative approaches:")
    print("1. Visit https://www.grants.gov.au/ and search manually")
    print("2. Download quarterly GrantConnect CSV files")
    print("3. Use Queensland Government grants portal: https://www.qld.gov.au/grants")

except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

# Method 3: Scrape Queensland Government grants page
print("\n" + "="*80)
print("🏛️  CHECKING QUEENSLAND GOVERNMENT GRANTS")
print("="*80 + "\n")

try:
    QLD_GRANTS_URL = "https://www.qld.gov.au/grants-awards/grants"

    print(f"Fetching: {QLD_GRANTS_URL}\n")
    response = requests.get(QLD_GRANTS_URL, timeout=30)

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')

        print("✅ Successfully accessed Queensland grants page")
        print("📋 This page lists current grant opportunities\n")
        print("💡 Recommendation:")
        print("   Visit the page manually and search for:")
        print("   • Regional development grants")
        print("   • North West Queensland programs")
        print("   • Indigenous economic development")
        print("   • Community infrastructure")
        print()

except Exception as e:
    print(f"Note: {e}\n")

print("="*80)
print("✅ GRANTCONNECT SCRAPE COMPLETE")
print("="*80 + "\n")

print("📝 Next steps:")
print("1. Review the exported CSV files in data/raw/")
print("2. Manually search GrantConnect for specific programs")
print("3. Check Queensland Government budget papers for regional allocations")
print("4. Contact North West Queensland councils for grant recipient data")
