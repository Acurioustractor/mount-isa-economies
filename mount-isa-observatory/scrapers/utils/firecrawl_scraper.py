"""
Firecrawl Utility for Mount Isa Economic Observatory

Bypasses 403 blocks, handles JavaScript rendering, and scrapes protected sites.
Use this when simple requests fail (e.g., Queensland Government sites).

Setup:
1. Get API key from https://firecrawl.dev/ (500 free credits/month)
2. Add to .env: FIRECRAWL_API_KEY=fc-your_key_here
3. Install: pip install firecrawl-py

Usage:
    from utils.firecrawl_scraper import FirecrawlScraper

    scraper = FirecrawlScraper()

    # Simple scrape (returns markdown)
    content = scraper.scrape_url('https://statements.qld.gov.au/statements/100887')

    # Extract structured data
    data = scraper.extract_structured(
        url='https://statements.qld.gov.au/statements/100887',
        schema={
            'title': 'string',
            'date': 'string',
            'funding_amount': 'string',
            'description': 'string'
        }
    )
"""

import os
from typing import Dict, Optional, List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class FirecrawlScraper:
    """
    Wrapper for Firecrawl API - bypasses blocks and handles JavaScript
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Firecrawl scraper

        Args:
            api_key: Firecrawl API key (defaults to FIRECRAWL_API_KEY env var)
        """
        self.api_key = api_key or os.getenv('FIRECRAWL_API_KEY')

        if not self.api_key:
            raise ValueError(
                "❌ FIRECRAWL_API_KEY not set.\n"
                "   Get from: https://firecrawl.dev/\n"
                "   Add to .env: FIRECRAWL_API_KEY=fc-your_key_here"
            )

        try:
            from firecrawl import FirecrawlApp
            self.app = FirecrawlApp(api_key=self.api_key)
            print("✅ Firecrawl initialized")
        except ImportError:
            raise ImportError(
                "❌ firecrawl-py not installed.\n"
                "   Run: pip install firecrawl-py"
            )

    def scrape_url(
        self,
        url: str,
        formats: List[str] = ['markdown', 'html'],
        only_main_content: bool = True
    ) -> Dict:
        """
        Scrape a single URL

        Args:
            url: URL to scrape
            formats: Output formats ('markdown', 'html', 'rawHtml', 'screenshot', 'links')
            only_main_content: Extract only main content (removes nav, footer, etc.)

        Returns:
            Dict with 'markdown', 'html', 'metadata', etc.

        Example:
            result = scraper.scrape_url('https://statements.qld.gov.au/statements/100887')
            content = result['markdown']
            title = result['metadata']['title']
        """
        print(f"🔥 Firecrawl: Scraping {url}")

        try:
            # Firecrawl API: pass parameters as direct kwargs
            result = self.app.scrape(
                url,
                formats=formats,
                only_main_content=only_main_content
            )

            print(f"✅ Scraped successfully: {result.get('metadata', {}).get('title', 'Unknown')}")
            return result

        except Exception as e:
            print(f"❌ Firecrawl error: {e}")
            raise

    def extract_structured(
        self,
        url: str,
        schema: Dict,
        prompt: Optional[str] = None
    ) -> Dict:
        """
        Extract structured data from URL using LLM

        Args:
            url: URL to extract from
            schema: Data structure to extract (e.g., {'title': 'string', 'amount': 'number'})
            prompt: Optional prompt to guide extraction

        Returns:
            Extracted structured data

        Example:
            data = scraper.extract_structured(
                url='https://statements.qld.gov.au/statements/100887',
                schema={
                    'title': 'string',
                    'date': 'string',
                    'funding_amount': 'string',
                    'recipient': 'string',
                    'program_name': 'string'
                },
                prompt='Extract funding information from this ministerial statement'
            )
        """
        print(f"🔥 Firecrawl: Extracting structured data from {url}")

        try:
            # Firecrawl API: pass parameters as direct kwargs
            kwargs = {'schema': schema}
            if prompt:
                kwargs['prompt'] = prompt

            result = self.app.extract(url, **kwargs)

            print(f"✅ Extracted: {result}")
            return result

        except Exception as e:
            print(f"❌ Firecrawl extraction error: {e}")
            raise

    def scrape_multiple(
        self,
        urls: List[str],
        formats: List[str] = ['markdown']
    ) -> List[Dict]:
        """
        Scrape multiple URLs (batch processing)

        Args:
            urls: List of URLs to scrape
            formats: Output formats

        Returns:
            List of scrape results
        """
        print(f"🔥 Firecrawl: Batch scraping {len(urls)} URLs")

        results = []
        for url in urls:
            try:
                result = self.scrape_url(url, formats=formats)
                results.append(result)
            except Exception as e:
                print(f"⚠️  Failed to scrape {url}: {e}")
                results.append({'url': url, 'error': str(e)})

        print(f"✅ Batch complete: {len(results)} results")
        return results

    def search(
        self,
        query: str,
        limit: int = 10
    ) -> List[Dict]:
        """
        Search and scrape (if Firecrawl supports search in your plan)

        Args:
            query: Search query
            limit: Max results

        Returns:
            Search results with scraped content
        """
        # Note: Search feature may require higher-tier plan
        print(f"🔥 Firecrawl: Searching for '{query}'")

        try:
            result = self.app.search(query, params={'limit': limit})
            print(f"✅ Found {len(result)} results")
            return result
        except Exception as e:
            print(f"⚠️  Search not available or error: {e}")
            return []


def test_firecrawl():
    """
    Test Firecrawl with Queensland Government media statement

    Run: python -m scrapers.utils.firecrawl_scraper
    """
    print("\n" + "="*80)
    print("🔥 TESTING FIRECRAWL - Queensland Gov Media Statement")
    print("="*80 + "\n")

    try:
        scraper = FirecrawlScraper()

        # Test URL that was blocked before
        test_url = 'https://statements.qld.gov.au/statements/100887'

        print(f"Testing URL: {test_url}")
        print("(This URL returns 403 Forbidden with simple requests)\n")

        # Scrape
        result = scraper.scrape_url(test_url)

        print("\n" + "="*80)
        print("📄 SCRAPE RESULTS")
        print("="*80 + "\n")

        # Print metadata
        metadata = result.get('metadata', {})
        print(f"Title: {metadata.get('title', 'N/A')}")
        print(f"Description: {metadata.get('description', 'N/A')}")
        print(f"URL: {metadata.get('url', 'N/A')}")
        print()

        # Print first 500 chars of markdown
        markdown = result.get('markdown', '')
        print("Content preview:")
        print(markdown[:500] + "...")
        print()

        # Test structured extraction
        print("\n" + "="*80)
        print("📊 STRUCTURED EXTRACTION TEST")
        print("="*80 + "\n")

        extracted = scraper.extract_structured(
            url=test_url,
            schema={
                'title': 'string',
                'announcement_date': 'string',
                'funding_amount': 'string',
                'recipient_organization': 'string',
                'program_name': 'string',
                'minister': 'string'
            },
            prompt='Extract funding details from this Queensland Government media statement'
        )

        print("Extracted data:")
        for key, value in extracted.items():
            print(f"  {key}: {value}")

        print("\n✅ Firecrawl test successful!")
        print("\nFirecrawl can now bypass 403 blocks on Queensland Gov sites! 🎉")

    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        print("\nTroubleshooting:")
        print("  1. Check FIRECRAWL_API_KEY is set in .env")
        print("  2. Verify you have credits: https://firecrawl.dev/app/usage")
        print("  3. Install: pip install firecrawl-py")


if __name__ == '__main__':
    test_firecrawl()
