"""
YOUTH JUSTICE FUNDING COMPREHENSIVE SCRAPER

Targets all Queensland Government youth justice funding announcements
Focus: Latest rounds of funding, where it's going, what programs

Data Sources:
1. Youth Justice Department media releases
2. Premier's announcements on youth justice
3. Attorney-General's announcements
4. Budget papers (youth justice allocation)
5. Community safety grants
6. Indigenous youth programs
"""

import os
import sys
from pathlib import Path
from datetime import datetime
import time
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from supabase import create_client, Client

# Add extractors to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))
from date_extractor import extract_date
from funding_extractor import extract_funding_amount
from validators import validate_document

load_dotenv()


class YouthJusticeScraper:
    """Comprehensive youth justice funding scraper for Queensland"""

    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if self.supabase_url and self.supabase_key:
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            print("✅ Connected to Supabase")
        else:
            self.supabase = None
            print("⚠️  No Supabase credentials - will print results only")

        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Queensland Economic Observatory Bot)'
        })

    def search_youth_justice_statements(self):
        """
        Search Queensland Government media statements for youth justice
        """
        print("\n" + "="*80)
        print("🔍 SEARCHING YOUTH JUSTICE MEDIA STATEMENTS")
        print("="*80)

        base_urls = [
            # Youth Justice Department
            "https://www.youthjustice.qld.gov.au/news-media",

            # Premier's office - search for youth justice
            "https://statements.qld.gov.au/search?query=youth+justice",
            "https://statements.qld.gov.au/search?query=youth+crime",
            "https://statements.qld.gov.au/search?query=community+safety",

            # Attorney-General
            "https://statements.qld.gov.au/search?query=youth+detention",
            "https://statements.qld.gov.au/search?query=youth+programs",

            # Specific funding announcements
            "https://statements.qld.gov.au/search?query=youth+justice+funding",
            "https://statements.qld.gov.au/search?query=youth+justice+grants",
        ]

        all_documents = []

        for url in base_urls:
            print(f"\n📍 Searching: {url}")
            try:
                docs = self._scrape_search_results(url)
                all_documents.extend(docs)
                print(f"   Found {len(docs)} documents")
                time.sleep(2)  # Be polite
            except Exception as e:
                print(f"   ❌ Error: {e}")

        return all_documents

    def _scrape_search_results(self, url):
        """Scrape search results page and extract document links"""
        documents = []

        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                return documents

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find all links that look like media statements
            # Queensland Government statements follow pattern: statements.qld.gov.au/statements/XXXXX
            links = soup.find_all('a', href=True)

            for link in links:
                href = link['href']

                # Filter for actual statement pages
                if '/statements/' in href or '/Statement/' in href:
                    full_url = href if href.startswith('http') else f"https://statements.qld.gov.au{href}"

                    # Avoid duplicates
                    if full_url not in [d.get('url') for d in documents]:
                        print(f"   → Found: {link.get_text(strip=True)[:60]}...")
                        doc = self._scrape_individual_statement(full_url)
                        if doc:
                            documents.append(doc)
                        time.sleep(1)  # Rate limit

        except Exception as e:
            print(f"   Error scraping search results: {e}")

        return documents

    def _scrape_individual_statement(self, url):
        """Scrape an individual media statement"""
        try:
            response = self.session.get(url, timeout=30)
            if response.status_code != 200:
                return None

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract title
            title_tag = soup.find('h1') or soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else "Untitled"

            # Extract content
            # Queensland statements usually in article or main content div
            content_div = (soup.find('article') or
                          soup.find('div', class_='content') or
                          soup.find('main'))

            content = content_div.get_text(separator='\n', strip=True) if content_div else soup.get_text()

            # Only process if it mentions youth justice or related keywords
            youth_justice_keywords = [
                'youth justice', 'youth crime', 'youth detention',
                'juvenile justice', 'young offenders', 'youth programs',
                'community safety', 'youth services', 'youth support'
            ]

            if not any(kw in content.lower() for kw in youth_justice_keywords):
                return None  # Not relevant

            print(f"      Processing: {title[:60]}...")

            # === EXTRACT WITH CONFIDENCE SCORING ===
            date, date_conf, date_method = extract_date(
                text=content,
                html=response.text,
                metadata={'url': url}
            )

            amount, funding_conf, funding_method = extract_funding_amount(
                text=content,
                html=response.text,
                metadata={'url': url}
            )

            # Extract locations mentioned
            locations = self._extract_locations(content)

            # Build document
            document = {
                'url': url,
                'title': title,
                'full_text': content,
                'published_date': date.strftime('%Y-%m-%d') if date else None,
                'published_date_confidence': float(date_conf) if date_conf else None,
                'published_date_extraction_method': date_method,
                'funding_amount_extracted': float(amount) if amount else None,
                'funding_confidence': float(funding_conf) if funding_conf else None,
                'funding_extraction_method': funding_method,
                'locations_mentioned': locations,
                'source_type': 'Queensland Government Media Statement',
                'source_organization': 'Youth Justice Department',
                'categories': ['Youth Justice', 'Community Safety'],
                'scraped_date': datetime.now().isoformat(),
            }

            # Validate
            warnings, needs_review = validate_document(document)
            document['needs_review'] = needs_review
            if warnings:
                document['validation_warnings'] = [w.to_dict() for w in warnings]

            # Save to database
            if self.supabase:
                self._save_to_supabase(document)

            print(f"         ✓ Date: {date.strftime('%Y-%m-%d') if date else 'None'} (conf: {date_conf:.2f if date_conf else 0})")
            print(f"         ✓ Funding: ${amount:,.0f} (conf: {funding_conf:.2f if funding_conf else 0})" if amount else "         - No funding found")
            print(f"         ✓ Locations: {', '.join(locations[:3])}" if locations else "         - No locations")

            return document

        except Exception as e:
            print(f"      ❌ Error: {e}")
            return None

    def _extract_locations(self, text):
        """Extract Queensland locations mentioned in text"""
        qld_locations = [
            'Mount Isa', 'Townsville', 'Cairns', 'Brisbane', 'Gold Coast',
            'Torres Strait', 'Palm Island', 'Doomadgee', 'Burketown',
            'Mornington Island', 'Aurukun', 'Kowanyama', 'Pormpuraaw',
            'Yarrabah', 'Cherbourg', 'Woorabinda', 'Hope Vale',
            'Lockhart River', 'Napranum', 'Mapoon', 'Bamaga',
            'Thursday Island', 'Horn Island', 'North Queensland',
            'Far North Queensland', 'North West Queensland',
            'Cape York', 'Gulf Country', 'Central Queensland',
            'Rockhampton', 'Mackay', 'Bundaberg', 'Toowoomba',
            'Ipswich', 'Logan', 'Redland', 'Moreton Bay'
        ]

        found_locations = []
        text_lower = text.lower()

        for location in qld_locations:
            if location.lower() in text_lower:
                if location not in found_locations:
                    found_locations.append(location)

        return found_locations

    def _save_to_supabase(self, document):
        """Save document to Supabase"""
        try:
            # Check for duplicate by URL
            existing = self.supabase.table('documents')\
                .select('id')\
                .eq('url', document['url'])\
                .execute()

            if existing.data:
                print(f"         ℹ️  Already in database")
                return False

            # Insert
            result = self.supabase.table('documents').insert(document).execute()
            print(f"         ✓ Saved to database")
            return True

        except Exception as e:
            print(f"         ❌ Database error: {e}")
            return False

    def search_youth_justice_budget_papers(self):
        """
        Search Queensland Budget Papers for youth justice allocations
        """
        print("\n" + "="*80)
        print("📊 SEARCHING BUDGET PAPERS - YOUTH JUSTICE")
        print("="*80)

        budget_urls = [
            # 2024-25 Budget
            "https://budget.qld.gov.au/files/2024-MYFER-SDS-Youth_Justice.pdf",
            "https://budget.qld.gov.au/2024-25/",

            # 2023-24 Budget
            "https://budget.qld.gov.au/files/2023-SDS-Youth_Justice.pdf",

            # Historical budgets
            "https://budget.qld.gov.au/2022-23/",
        ]

        print("\n⚠️  Budget papers require PDF extraction")
        print("Consider using:")
        print("  - PyPDF2 for text extraction")
        print("  - Tabula for table extraction")
        print("  - Manual review of SDS (Service Delivery Statements)")

    def search_grants_portal(self):
        """
        Search Queensland grants portal for youth justice grants
        """
        print("\n" + "="*80)
        print("💰 SEARCHING GRANTS PORTAL - YOUTH JUSTICE")
        print("="*80)

        grant_search_urls = [
            "https://www.grants.services.qld.gov.au/?keywords=youth+justice",
            "https://www.grants.services.qld.gov.au/?keywords=youth+crime",
            "https://www.grants.services.qld.gov.au/?keywords=community+safety",
            "https://www.grants.services.qld.gov.au/?keywords=youth+services",
        ]

        print("\n📋 Grant search URLs to explore:")
        for url in grant_search_urls:
            print(f"  → {url}")

        print("\n💡 Tip: Many grants require manual application review")
        print("   Consider FOI request for awarded grants list")


def main():
    print("\n" + "="*80)
    print("🚀 YOUTH JUSTICE COMPREHENSIVE DATA COLLECTION")
    print("="*80)
    print("\nFocus: Latest rounds of funding for youth justice programs")
    print("Target: Mount Isa, Palm Island, Torres Strait, and regional Queensland")
    print("="*80)

    scraper = YouthJusticeScraper()

    # 1. Search media statements
    print("\n\n" + "="*80)
    print("PHASE 1: MEDIA STATEMENTS")
    print("="*80)
    documents = scraper.search_youth_justice_statements()

    # 2. Budget papers (guidance only)
    print("\n\n" + "="*80)
    print("PHASE 2: BUDGET PAPERS")
    print("="*80)
    scraper.search_youth_justice_budget_papers()

    # 3. Grants portal (guidance only)
    print("\n\n" + "="*80)
    print("PHASE 3: GRANTS PORTAL")
    print("="*80)
    scraper.search_grants_portal()

    # Summary
    print("\n\n" + "="*80)
    print("📊 SUMMARY")
    print("="*80)
    print(f"Media statements found: {len(documents)}")

    if documents:
        with_funding = sum(1 for d in documents if d.get('funding_amount_extracted'))
        mount_isa_mentions = sum(1 for d in documents if 'Mount Isa' in d.get('locations_mentioned', []))

        print(f"With funding amounts: {with_funding}")
        print(f"Mentioning Mount Isa: {mount_isa_mentions}")

        # Show Mount Isa specific documents
        if mount_isa_mentions > 0:
            print(f"\n🎯 MOUNT ISA YOUTH JUSTICE FUNDING:")
            for doc in documents:
                if 'Mount Isa' in doc.get('locations_mentioned', []):
                    amount = doc.get('funding_amount_extracted')
                    print(f"\n  📄 {doc['title'][:70]}")
                    print(f"     Date: {doc.get('published_date', 'Unknown')}")
                    print(f"     Funding: ${amount:,.0f}" if amount else "     Funding: Not extracted")
                    print(f"     URL: {doc['url']}")

    print("\n" + "="*80)
    print("✅ COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
