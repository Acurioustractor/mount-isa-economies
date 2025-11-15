"""
Integrated scraper example showing how to use all the extraction and validation components
"""
import os
from datetime import datetime
from decimal import Decimal
from typing import Dict, Any, Optional
import requests
from bs4 import BeautifulSoup
from supabase import create_client, Client

# Import our custom modules
from date_extractor import extract_date
from funding_extractor import extract_funding_amount
from validators import validate_document


class IntegratedScraper:
    """
    Example scraper that integrates:
    - Multi-strategy date extraction
    - Multi-strategy funding amount extraction
    - Confidence scoring
    - Data validation
    - Supabase storage
    """

    def __init__(self, supabase_url: str = None, supabase_key: str = None):
        """Initialize scraper with Supabase connection"""
        # Load from environment if not provided
        self.supabase_url = supabase_url or os.getenv('SUPABASE_URL')
        self.supabase_key = supabase_key or os.getenv('SUPABASE_KEY')

        if self.supabase_url and self.supabase_key:
            self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        else:
            self.supabase = None
            print("⚠️  Warning: Supabase credentials not provided. Documents won't be saved to database.")

    def scrape_url(self, url: str, source_system: str = "integrated_scraper") -> Optional[Dict[str, Any]]:
        """
        Scrape a single URL and extract all relevant information

        Args:
            url: URL to scrape
            source_system: Identifier for this scraper

        Returns:
            Dictionary with extracted and validated document data
        """
        print(f"\n{'='*80}")
        print(f"Scraping: {url}")
        print(f"{'='*80}")

        try:
            # Fetch the page
            response = requests.get(url, timeout=30, headers={
                'User-Agent': 'Mozilla/5.0 (Queensland Government Data Observatory Bot)'
            })
            response.raise_for_status()

            html = response.text
            soup = BeautifulSoup(html, 'html.parser')

            # Extract plain text
            content = soup.get_text(separator='\n', strip=True)

            # Extract title
            title_tag = soup.find('title')
            title = title_tag.get_text(strip=True) if title_tag else soup.find('h1')
            if title and hasattr(title, 'get_text'):
                title = title.get_text(strip=True)
            title = str(title) if title else "Untitled Document"

            # Extract metadata
            metadata = self._extract_metadata(soup)

            print(f"\n📄 Title: {title}")

            # === MULTI-STRATEGY DATE EXTRACTION ===
            print(f"\n📅 Extracting date...")
            date, date_confidence, date_method = extract_date(
                text=content,
                html=html,
                metadata=metadata
            )

            if date:
                print(f"   ✓ Date: {date.strftime('%Y-%m-%d')}")
                print(f"   ✓ Confidence: {date_confidence:.2f}")
                print(f"   ✓ Method: {date_method}")
            else:
                print(f"   ✗ No date found")

            # === MULTI-STRATEGY FUNDING EXTRACTION ===
            print(f"\n💰 Extracting funding amount...")
            amount, funding_confidence, funding_method = extract_funding_amount(
                text=content,
                html=html,
                metadata=metadata
            )

            if amount:
                print(f"   ✓ Amount: ${amount:,.2f}")
                print(f"   ✓ Confidence: {funding_confidence:.2f}")
                print(f"   ✓ Method: {funding_method}")
            else:
                print(f"   ✗ No funding amount found")

            # === LOCATION EXTRACTION (simplified example) ===
            print(f"\n📍 Extracting location...")
            location, location_confidence = self._extract_location(content)

            if location:
                print(f"   ✓ Location: {location}")
                print(f"   ✓ Confidence: {location_confidence:.2f}")
            else:
                print(f"   ✗ No location found")

            # Build document object
            document = {
                'title': title,
                'url': url,
                'content': content,
                'html': html,
                'date': date,
                'date_confidence': float(date_confidence) if date_confidence else None,
                'date_extraction_method': date_method,
                'funding_amount': float(amount) if amount else None,
                'funding_confidence': float(funding_confidence) if funding_confidence else None,
                'funding_extraction_method': funding_method,
                'location': location,
                'location_confidence': float(location_confidence) if location_confidence else None,
                'source_system': source_system,
                'source_url': url,
                'scraped_at': datetime.now().isoformat(),
                'metadata': metadata
            }

            # === VALIDATION ===
            print(f"\n✅ Validating document...")
            warnings, needs_review = validate_document(document)

            print(f"   Validation warnings: {len(warnings)}")
            print(f"   Needs review: {needs_review}")

            if warnings:
                print(f"\n   Warnings:")
                for warning in warnings:
                    icon = "🔴" if warning.severity == "error" else "🟡" if warning.severity == "warning" else "ℹ️"
                    print(f"   {icon} [{warning.severity}] {warning.field}: {warning.message}")

            # === SAVE TO DATABASE ===
            if self.supabase:
                print(f"\n💾 Saving to database...")
                saved = self._save_to_supabase(document)
                if saved:
                    print(f"   ✓ Saved successfully")
                else:
                    print(f"   ✗ Failed to save")

            return document

        except Exception as e:
            print(f"\n❌ Error scraping {url}: {str(e)}")
            import traceback
            traceback.print_exc()
            return None

    def _extract_metadata(self, soup: BeautifulSoup) -> Dict[str, Any]:
        """Extract metadata from HTML meta tags"""
        metadata = {}

        # Common meta tags
        meta_tags = soup.find_all('meta')
        for tag in meta_tags:
            # property meta tags (Open Graph, etc.)
            if tag.get('property'):
                metadata[tag['property']] = tag.get('content', '')

            # name meta tags
            if tag.get('name'):
                metadata[tag['name']] = tag.get('content', '')

        return metadata

    def _extract_location(self, text: str) -> tuple[Optional[str], float]:
        """
        Simple location extraction (you can enhance this with NLP/LLM)

        Returns:
            Tuple of (location, confidence_score)
        """
        # Known Queensland locations
        locations = {
            'Mount Isa': ['mount isa', 'mount-isa', 'mt isa'],
            'Townsville': ['townsville'],
            'Torres Strait': ['torres strait'],
            'Palm Island': ['palm island'],
            'Cairns': ['cairns'],
            'Doomadgee': ['doomadgee'],
            'Burketown': ['burketown'],
            'Brisbane': ['brisbane'],
            'Gold Coast': ['gold coast'],
            'Logan': ['logan'],
            'Ipswich': ['ipswich'],
            'North Queensland': ['north queensland', 'northern queensland'],
            'Central Queensland': ['central queensland'],
        }

        text_lower = text.lower()

        for location, variations in locations.items():
            for variation in variations:
                if variation in text_lower:
                    # Higher confidence if mentioned multiple times
                    count = text_lower.count(variation)
                    confidence = min(0.7 + (count * 0.05), 0.95)
                    return location, confidence

        return None, 0.0

    def _save_to_supabase(self, document: Dict[str, Any]) -> bool:
        """Save document to Supabase"""
        try:
            # Remove HTML field for storage (too large, can be stored separately if needed)
            doc_to_save = document.copy()
            if 'html' in doc_to_save:
                del doc_to_save['html']

            # Check for duplicate by checksum
            checksum = doc_to_save.get('checksum')
            if checksum:
                existing = self.supabase.table('documents')\
                    .select('id')\
                    .eq('checksum', checksum)\
                    .execute()

                if existing.data:
                    print(f"   ℹ️  Document already exists (checksum: {checksum})")
                    return False

            # Insert document
            result = self.supabase.table('documents').insert(doc_to_save).execute()
            return bool(result.data)

        except Exception as e:
            print(f"   ❌ Database error: {str(e)}")
            return False


def main():
    """Example usage"""
    # Initialize scraper
    scraper = IntegratedScraper()

    # Example URLs to scrape (you would replace these with real Queensland Gov URLs)
    test_urls = [
        # Queensland Government examples
        "https://www.qld.gov.au/community/grants",
        # Add your specific URLs here
    ]

    print("🚀 Starting integrated scraper")
    print(f"   Supabase: {'Connected' if scraper.supabase else 'Not connected'}")

    results = []
    for url in test_urls:
        result = scraper.scrape_url(url, source_system="qld_gov_scraper")
        if result:
            results.append(result)

    print(f"\n{'='*80}")
    print(f"📊 SCRAPING SUMMARY")
    print(f"{'='*80}")
    print(f"Total URLs: {len(test_urls)}")
    print(f"Successfully scraped: {len(results)}")
    print(f"Failed: {len(test_urls) - len(results)}")

    # Summary statistics
    with_dates = sum(1 for r in results if r.get('date'))
    with_funding = sum(1 for r in results if r.get('funding_amount'))
    needs_review = sum(1 for r in results if r.get('needs_review'))

    print(f"\nExtraction success rates:")
    print(f"  Dates: {with_dates}/{len(results)} ({with_dates/len(results)*100:.1f}%)")
    print(f"  Funding: {with_funding}/{len(results)} ({with_funding/len(results)*100:.1f}%)")
    print(f"  Needs review: {needs_review}")


if __name__ == "__main__":
    # Load environment variables
    from dotenv import load_dotenv
    load_dotenv()

    main()
