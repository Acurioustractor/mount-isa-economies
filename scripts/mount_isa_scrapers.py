"""
Mount Isa-specific scrapers to increase coverage for LGA35300

This module contains scrapers specifically targeting Mount Isa-related documents
to address the low document count (currently only 4 documents).
"""
import requests
from bs4 import BeautifulSoup
from typing import List, Dict, Any
import time
from integrated_scraper_example import IntegratedScraper


class MountIsaCouncilScraper(IntegratedScraper):
    """
    Scraper specifically for Mount Isa City Council website
    Targets: Grants, procurement, budget documents, meeting agendas
    """

    BASE_URL = "https://www.mountisa.qld.gov.au"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_system = "mount_isa_council_scraper"

    def scrape_council_news(self) -> List[Dict[str, Any]]:
        """Scrape council news and announcements"""
        urls_to_scrape = [
            f"{self.BASE_URL}/news",
            f"{self.BASE_URL}/announcements",
            f"{self.BASE_URL}/grants",
            # Add more specific URLs as you discover them
        ]

        results = []
        for url in urls_to_scrape:
            print(f"\n📰 Scraping council news from: {url}")
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find article links (this will need to be customized based on actual site structure)
                    articles = soup.find_all(['article', 'div'], class_=['news-item', 'article', 'post'])

                    for article in articles:
                        link = article.find('a', href=True)
                        if link:
                            article_url = link['href']
                            if not article_url.startswith('http'):
                                article_url = f"{self.BASE_URL}{article_url}"

                            # Scrape individual article
                            doc = self.scrape_url(article_url, self.source_system)
                            if doc:
                                results.append(doc)

                            # Be polite - rate limit
                            time.sleep(2)

            except Exception as e:
                print(f"❌ Error scraping {url}: {str(e)}")

        return results

    def scrape_budget_documents(self) -> List[Dict[str, Any]]:
        """Scrape budget and financial documents"""
        urls_to_scrape = [
            f"{self.BASE_URL}/budget",
            f"{self.BASE_URL}/financial-reports",
            f"{self.BASE_URL}/annual-report",
            # PDF documents are especially important for budget data
        ]

        results = []
        for url in urls_to_scrape:
            print(f"\n💵 Scraping budget documents from: {url}")
            doc = self.scrape_url(url, self.source_system)
            if doc:
                results.append(doc)
            time.sleep(2)

        return results

    def scrape_procurement(self) -> List[Dict[str, Any]]:
        """Scrape procurement and tender documents"""
        urls_to_scrape = [
            f"{self.BASE_URL}/tenders",
            f"{self.BASE_URL}/procurement",
            f"{self.BASE_URL}/suppliers",
        ]

        results = []
        for url in urls_to_scrape:
            print(f"\n📋 Scraping procurement from: {url}")
            doc = self.scrape_url(url, self.source_system)
            if doc:
                results.append(doc)
            time.sleep(2)

        return results


class QueenslandGrantsScraper(IntegratedScraper):
    """
    Scraper for Queensland Government grants specifically mentioning Mount Isa
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_system = "qld_grants_scraper"

    def scrape_grants_for_mount_isa(self) -> List[Dict[str, Any]]:
        """
        Scrape Queensland grants database for Mount Isa specific grants
        """
        # Queensland Government grants portal
        base_urls = [
            "https://www.qld.gov.au/community/grants",
            "https://grants.services.qld.gov.au/",
        ]

        results = []

        # Strategy 1: Direct search for Mount Isa grants
        search_terms = [
            "mount+isa",
            "north+west+queensland",
            "remote+communities",
        ]

        for search_term in search_terms:
            print(f"\n🔍 Searching for grants with term: {search_term}")
            # Note: You'll need to customize this based on the actual search functionality
            search_url = f"https://www.qld.gov.au/search?q={search_term}&collection=grants"

            try:
                response = requests.get(search_url, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Find grant result links
                    grant_links = soup.find_all('a', class_=['grant-link', 'result-link'])

                    for link in grant_links[:10]:  # Limit to first 10 results per search
                        grant_url = link.get('href')
                        if grant_url and 'grant' in grant_url.lower():
                            if not grant_url.startswith('http'):
                                grant_url = f"https://www.qld.gov.au{grant_url}"

                            doc = self.scrape_url(grant_url, self.source_system)
                            if doc and doc.get('location') == 'Mount Isa':
                                results.append(doc)

                            time.sleep(2)

            except Exception as e:
                print(f"❌ Error searching for {search_term}: {str(e)}")

        return results


class RegionalDevelopmentScraper(IntegratedScraper):
    """
    Scraper for regional development organizations covering Mount Isa
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.source_system = "regional_dev_scraper"

    def scrape_nwq_sources(self) -> List[Dict[str, Any]]:
        """
        Scrape North West Queensland regional development sources
        """
        # Outback Queensland Tourism Association
        # North West Queensland Resource Centre
        # Regional Development Australia - North West Queensland

        urls = [
            # You would add specific URLs here for:
            # - RDA North West Queensland
            # - Mount Isa Chamber of Commerce
            # - Outback Queensland regional development
        ]

        results = []
        for url in urls:
            doc = self.scrape_url(url, self.source_system)
            if doc:
                results.append(doc)
            time.sleep(2)

        return results


class AustenderMountIsaScraper:
    """
    Scraper for Commonwealth procurement (AusTender) filtered for Mount Isa
    Uses the AusTender API/OCDS feed
    """

    def __init__(self, supabase_url=None, supabase_key=None):
        self.base_scraper = IntegratedScraper(supabase_url, supabase_key)
        self.source_system = "austender_mount_isa"

    def scrape_austender_contracts(self) -> List[Dict[str, Any]]:
        """
        Scrape AusTender for contracts delivered to Mount Isa (postcode 4825)

        Note: AusTender has an API - you should use that instead of scraping HTML
        See: https://www.tenders.gov.au/?event=public.api.show
        """
        # Example API endpoint (you'll need to register for API access)
        api_url = "https://www.tenders.gov.au/api/contracts"

        params = {
            'postcode': '4825',  # Mount Isa postcode
            'status': 'active',
            'format': 'json'
        }

        print(f"\n🏢 Querying AusTender API for Mount Isa contracts...")

        try:
            # Note: You may need authentication for the API
            response = requests.get(api_url, params=params, timeout=30)

            if response.status_code == 200:
                contracts = response.json()

                results = []
                for contract in contracts.get('contracts', []):
                    # Convert contract data to our document format
                    doc = {
                        'title': contract.get('title', 'Untitled Contract'),
                        'url': contract.get('url', ''),
                        'content': contract.get('description', ''),
                        'date': contract.get('publish_date'),
                        'funding_amount': contract.get('value'),
                        'location': 'Mount Isa',
                        'lga_code': 'LGA35300',
                        'location_confidence': 1.0,  # High confidence from postcode match
                        'program_type': 'procurement',
                        'payer_type': 'Commonwealth',
                        'source_system': self.source_system,
                        'source_url': contract.get('url'),
                    }

                    # Validate and save
                    from validators import validate_document
                    warnings, needs_review = validate_document(doc)

                    if self.base_scraper.supabase:
                        self.base_scraper._save_to_supabase(doc)

                    results.append(doc)

                print(f"   ✓ Found {len(results)} AusTender contracts for Mount Isa")
                return results

        except Exception as e:
            print(f"❌ Error querying AusTender: {str(e)}")

        return []


def run_all_mount_isa_scrapers():
    """
    Run all Mount Isa-specific scrapers to build up the document database

    This addresses the issue: "Only 4 documents for Mount Isa"
    """
    print("="*80)
    print("🎯 MOUNT ISA FOCUSED SCRAPING")
    print("="*80)

    all_documents = []

    # 1. Council scraper
    print("\n\n1️⃣  MOUNT ISA CITY COUNCIL")
    print("-" * 80)
    council_scraper = MountIsaCouncilScraper()

    council_news = council_scraper.scrape_council_news()
    all_documents.extend(council_news)

    council_budget = council_scraper.scrape_budget_documents()
    all_documents.extend(council_budget)

    council_procurement = council_scraper.scrape_procurement()
    all_documents.extend(council_procurement)

    # 2. Queensland grants scraper
    print("\n\n2️⃣  QUEENSLAND GOVERNMENT GRANTS")
    print("-" * 80)
    grants_scraper = QueenslandGrantsScraper()
    grants = grants_scraper.scrape_grants_for_mount_isa()
    all_documents.extend(grants)

    # 3. Regional development scraper
    print("\n\n3️⃣  REGIONAL DEVELOPMENT SOURCES")
    print("-" * 80)
    regional_scraper = RegionalDevelopmentScraper()
    regional_docs = regional_scraper.scrape_nwq_sources()
    all_documents.extend(regional_docs)

    # 4. AusTender scraper
    print("\n\n4️⃣  AUSTENDER COMMONWEALTH PROCUREMENT")
    print("-" * 80)
    austender_scraper = AustenderMountIsaScraper()
    contracts = austender_scraper.scrape_austender_contracts()
    all_documents.extend(contracts)

    # Summary
    print("\n\n" + "="*80)
    print("📊 MOUNT ISA SCRAPING SUMMARY")
    print("="*80)
    print(f"Total documents scraped: {len(all_documents)}")
    print(f"  • Council: {len(council_news) + len(council_budget) + len(council_procurement)}")
    print(f"  • Grants: {len(grants)}")
    print(f"  • Regional Dev: {len(regional_docs)}")
    print(f"  • AusTender: {len(contracts)}")

    return all_documents


if __name__ == "__main__":
    from dotenv import load_dotenv
    load_dotenv()

    run_all_mount_isa_scrapers()
