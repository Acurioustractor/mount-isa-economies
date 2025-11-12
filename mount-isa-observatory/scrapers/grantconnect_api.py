"""
Australian Government Grants Scraper
Gets grant data from multiple reliable sources:
1. Data.gov.au grant datasets (department-specific)
2. ARC Grants Search API (research grants)

Note: GrantConnect doesn't offer a public API or bulk download, so we use alternative sources
"""
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import json

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'grants'
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*80)
print("💰 AUSTRALIAN GOVERNMENT GRANTS SCRAPER")
print("="*80 + "\n")

# data.gov.au CKAN API
CKAN_URL = "https://data.gov.au/api/3/action"

# ARC Grants API
ARC_API_URL = "https://dataportal.arc.gov.au/NCGP/API/Grant/Search"

class GrantsScraper:
    """Scrape government grants from multiple sources"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def search_datagovau_grants(self, search_terms):
        """Search data.gov.au for grant datasets"""
        print("🔍 Searching data.gov.au for grant datasets...\n")

        all_datasets = []

        for term in search_terms:
            try:
                url = f"{CKAN_URL}/package_search"
                params = {
                    'q': f'grants {term}',
                    'rows': 100
                }

                response = self.session.get(url, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()
                datasets = data['result']['results']

                print(f"   '{term}': Found {len(datasets)} datasets")
                all_datasets.extend(datasets)

                time.sleep(0.5)

            except Exception as e:
                print(f"   Error searching '{term}': {e}")

        # Remove duplicates
        unique_datasets = {d['id']: d for d in all_datasets}.values()
        print(f"\n✅ Found {len(unique_datasets)} unique grant datasets\n")

        return list(unique_datasets)

    def download_grant_dataset(self, dataset):
        """Download CSV resources from a grant dataset"""
        print(f"📥 {dataset['title']}")

        try:
            url = f"{CKAN_URL}/package_show"
            params = {'id': dataset['id']}

            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            resources = response.json()['result']['resources']

            # Find CSV resources
            csv_resources = [r for r in resources if r.get('format', '').upper() == 'CSV']

            if not csv_resources:
                print("   No CSV resources available\n")
                return None

            # Download first CSV
            resource = csv_resources[0]
            print(f"   Downloading: {resource['name']}")

            csv_response = self.session.get(resource['url'], timeout=120)
            csv_response.raise_for_status()

            # Save to file
            filename = f"{dataset['name'][:50]}_{datetime.now().strftime('%Y%m%d')}.csv"
            output_file = DATA_DIR / filename

            with open(output_file, 'wb') as f:
                f.write(csv_response.content)

            print(f"   ✅ Saved: {filename}")
            print(f"   Size: {output_file.stat().st_size / 1024:.1f} KB\n")

            return output_file

        except Exception as e:
            print(f"   ⚠️  Error: {e}\n")
            return None

    def search_arc_grants(self, keywords):
        """Search ARC grants database (research grants)"""
        print("🔍 Searching ARC research grants database...\n")

        grants = []

        for keyword in keywords:
            try:
                params = {
                    'Keywords': keyword,
                    'PageSize': 100,
                    'PageNumber': 1
                }

                response = self.session.get(ARC_API_URL, params=params, timeout=30)
                response.raise_for_status()

                data = response.json()

                if 'Grants' in data:
                    grants.extend(data['Grants'])
                    print(f"   '{keyword}': Found {len(data['Grants'])} ARC grants")

                time.sleep(1)

            except Exception as e:
                print(f"   Error searching ARC for '{keyword}': {e}")

        print(f"\n✅ Found {len(grants)} ARC research grants\n")
        return grants

    def filter_mount_isa_grants(self, grants, search_fields):
        """Filter grants for Mount Isa mentions"""
        mount_isa_keywords = [
            'mount isa', 'kalkadoon', '4825', 'north west queensland',
            'north-west queensland', 'nw qld', 'nwq'
        ]

        mount_isa_grants = []

        for grant in grants:
            for field in search_fields:
                if field in grant:
                    text = str(grant[field]).lower()
                    if any(keyword in text for keyword in mount_isa_keywords):
                        mount_isa_grants.append(grant)
                        break

        return mount_isa_grants


# Main execution
if __name__ == '__main__':
    scraper = GrantsScraper()

    all_grants = []

    # 1. Search data.gov.au for grant datasets
    print("="*80)
    print("PHASE 1: DATA.GOV.AU GRANT DATASETS")
    print("="*80 + "\n")

    search_terms = [
        'Mount Isa',
        'North West Queensland',
        'regional development',
        'remote communities',
        'indigenous grants',
        'Queensland grants'
    ]

    datasets = scraper.search_datagovau_grants(search_terms)

    # Download promising datasets
    if datasets:
        print("📥 Downloading grant datasets...\n")

        for dataset in datasets[:10]:  # Limit to first 10
            file = scraper.download_grant_dataset(dataset)

            if file:
                try:
                    # Try to load and filter for Mount Isa
                    df = pd.read_csv(file, encoding='utf-8', low_memory=False, nrows=10000)

                    # Search all text columns
                    mount_isa_matches = pd.DataFrame()

                    for col in df.columns:
                        if df[col].dtype == 'object':
                            matches = df[df[col].astype(str).str.contains(
                                'mount isa|kalkadoon|4825',
                                case=False,
                                na=False
                            )]
                            mount_isa_matches = pd.concat([mount_isa_matches, matches]).drop_duplicates()

                    if len(mount_isa_matches) > 0:
                        print(f"   🎯 Found {len(mount_isa_matches)} Mount Isa grants in this dataset!")
                        all_grants.extend(mount_isa_matches.to_dict('records'))

                except Exception as e:
                    pass

    # 2. Search ARC research grants
    print("\n" + "="*80)
    print("PHASE 2: ARC RESEARCH GRANTS")
    print("="*80 + "\n")

    arc_keywords = [
        'Mount Isa',
        'Kalkadoon',
        'North West Queensland'
    ]

    arc_grants = scraper.search_arc_grants(arc_keywords)

    if arc_grants:
        # Filter for Mount Isa relevance
        arc_search_fields = ['Title', 'Description', 'PrimaryFORSubject', 'AdministratingInstitution']
        mount_isa_arc_grants = scraper.filter_mount_isa_grants(arc_grants, arc_search_fields)

        if mount_isa_arc_grants:
            print(f"🎯 Found {len(mount_isa_arc_grants)} Mount Isa-related ARC grants\n")

            print("="*80)
            print("📊 ARC RESEARCH GRANTS - MOUNT ISA")
            print("="*80 + "\n")

            for grant in mount_isa_arc_grants[:20]:
                print(f"  • {grant.get('Title', 'Untitled')}")
                if 'FundingAmount' in grant:
                    print(f"    Amount: ${grant['FundingAmount']:,}")
                if 'StartYear' in grant:
                    print(f"    Year: {grant['StartYear']}")
                print()

            all_grants.extend(mount_isa_arc_grants)

    # 3. Save all results
    print("="*80)
    print("💾 SAVING RESULTS")
    print("="*80 + "\n")

    if all_grants:
        df = pd.DataFrame(all_grants)

        output_file = DATA_DIR / f'mount_isa_grants_{datetime.now().strftime("%Y%m%d")}.csv'
        df.to_csv(output_file, index=False)

        print(f"✅ Saved {len(df)} grants: {output_file}\n")

        # Calculate totals if possible
        amount_cols = [col for col in df.columns if any(term in col.lower() for term in ['amount', 'value', 'funding'])]

        for col in amount_cols:
            if df[col].dtype in ['int64', 'float64']:
                total = df[col].sum()
                if total > 0:
                    print(f"💰 Total {col}: ${total:,.0f}")

        print()

    else:
        print("⚠️  No Mount Isa grants found\n")

    print("="*80)
    print("✅ GRANTS SCRAPE COMPLETE")
    print("="*80 + "\n")

    print("💡 Summary:")
    print(f"   Total grants found: {len(all_grants)}")
    print()

    print("💡 Additional grant sources to explore manually:")
    print("  1. GrantConnect: https://www.grants.gov.au/")
    print("     Search for 'Mount Isa' to find current opportunities")
    print()
    print("  2. QLD Government Grants Portal:")
    print("     https://www.qld.gov.au/grants-awards")
    print()
    print("  3. Mount Isa City Council grants listings:")
    print("     https://www.mountisa.qld.gov.au/grants")
    print()
    print("  4. Department-specific grant programs:")
    print("     - Regional Development Australia")
    print("     - National Indigenous Australians Agency")
    print("     - Department of Infrastructure")
    print()
