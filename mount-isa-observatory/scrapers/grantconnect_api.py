"""
GrantConnect API Client
Professional client for Australian Government grants data

API: https://www.grants.gov.au/
Gets: Grant programs, recipients, amounts, purposes for Mount Isa region
"""
import requests
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
from bs4 import BeautifulSoup
import json

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'grants'
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*80)
print("💰 GRANTCONNECT GRANTS SCRAPER")
print("="*80 + "\n")

class GrantConnectScraper:
    """Professional GrantConnect scraper with multiple data sources"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def search_grants(self, keywords, max_results=1000):
        """
        Search GrantConnect for grants matching keywords

        Uses the public search interface
        """
        print(f"🔍 Searching for grants with keywords: {keywords}\n")

        grants = []

        # GrantConnect search URL
        search_url = "https://www.grants.gov.au/search"

        params = {
            'query': keywords,
            'size': 100,  # Results per page
            'from': 0
        }

        page = 0
        while len(grants) < max_results:
            params['from'] = page * 100

            try:
                print(f"   Fetching page {page + 1}...")
                response = self.session.get(search_url, params=params, timeout=30)
                response.raise_for_status()

                # Parse HTML response
                soup = BeautifulSoup(response.text, 'html.parser')

                # Find grant results (GrantConnect uses specific HTML structure)
                grant_cards = soup.find_all('div', class_='grant-card')

                if not grant_cards:
                    print(f"   No more results found")
                    break

                for card in grant_cards:
                    grant = self._parse_grant_card(card)
                    if grant:
                        grants.append(grant)

                page += 1
                time.sleep(1)  # Rate limiting

            except Exception as e:
                print(f"   Error fetching page {page + 1}: {e}")
                break

        print(f"\n✅ Found {len(grants)} grants\n")
        return grants

    def _parse_grant_card(self, card):
        """Parse individual grant card HTML"""
        try:
            grant = {}

            # Extract grant details from card
            title_elem = card.find('h3')
            grant['title'] = title_elem.text.strip() if title_elem else None

            # Get grant ID/link
            link_elem = card.find('a', href=True)
            grant['url'] = f"https://www.grants.gov.au{link_elem['href']}" if link_elem else None

            # Extract other details
            details = card.find_all('div', class_='grant-detail')
            for detail in details:
                label = detail.find('span', class_='label')
                value = detail.find('span', class_='value')

                if label and value:
                    key = label.text.strip().lower().replace(' ', '_')
                    grant[key] = value.text.strip()

            return grant

        except Exception as e:
            print(f"   Error parsing grant card: {e}")
            return None

    def get_grant_details(self, grant_url):
        """Get detailed information for a specific grant"""
        try:
            response = self.session.get(grant_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            details = {}

            # Extract all grant details
            detail_sections = soup.find_all('div', class_='grant-detail-section')
            for section in detail_sections:
                label = section.find('dt')
                value = section.find('dd')

                if label and value:
                    key = label.text.strip().lower().replace(' ', '_')
                    details[key] = value.text.strip()

            return details

        except Exception as e:
            print(f"Error getting grant details: {e}")
            return {}


# Alternative: Use published grant datasets
def download_published_grants():
    """
    Download published grant data from data.gov.au

    This is more reliable than scraping
    """
    print("📥 Downloading published grant datasets...\n")

    # data.gov.au maintains published grant data
    datasets = [
        {
            'name': 'Commonwealth Grants',
            'url': 'https://data.gov.au/data/dataset/grants-awarded',
            'description': 'All Commonwealth grants awarded'
        }
    ]

    all_grants = []

    for dataset in datasets:
        print(f"   Downloading: {dataset['name']}")

        try:
            # This would need the actual CSV URL from data.gov.au
            # Placeholder for demonstration
            print(f"   ⚠️  Need to find direct CSV download link")

        except Exception as e:
            print(f"   Error: {e}")

    return all_grants


# Main execution
if __name__ == '__main__':
    scraper = GrantConnectScraper()

    # Search for Mount Isa related grants
    search_terms = [
        "Mount Isa",
        "North West Queensland",
        "Kalkadoon",
        "4825",  # Mount Isa postcode
        "Isaac Regional Council",  # Sometimes covers Mount Isa region
    ]

    all_grants = []

    for term in search_terms:
        grants = scraper.search_grants(term, max_results=100)
        all_grants.extend(grants)

    # Remove duplicates
    df = pd.DataFrame(all_grants)

    if len(df) > 0:
        df = df.drop_duplicates(subset=['title', 'url'])

        print("="*80)
        print(f"📊 GRANTS SUMMARY ({len(df)} unique grants)")
        print("="*80 + "\n")

        for idx, grant in df.head(20).iterrows():
            print(f"{idx + 1}. {grant.get('title', 'Untitled')}")
            if 'amount' in grant and pd.notna(grant['amount']):
                print(f"   Amount: {grant['amount']}")
            if 'recipient' in grant and pd.notna(grant['recipient']):
                print(f"   Recipient: {grant['recipient']}")
            print()

        # Save results
        output_file = DATA_DIR / f'mount_isa_grants_{datetime.now().strftime("%Y%m%d")}.csv'
        df.to_csv(output_file, index=False)

        print(f"💾 Saved grants: {output_file}\n")

    else:
        print("⚠️  No grants found")
        print("\nAlternative approaches:")
        print("1. Contact local council for grant recipient lists")
        print("2. Check Queensland Government grants portal")
        print("3. Review federal budget papers for regional allocations")
        print("4. FOI request to relevant departments\n")

    print("="*80)
    print("✅ GRANTCONNECT SCRAPE COMPLETE")
    print("="*80 + "\n")
