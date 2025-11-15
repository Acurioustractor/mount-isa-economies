"""
SCRAPE DISCOVERED URLs - Using Firecrawl

This script scrapes the 66 URLs we already discovered using WebSearch.
Simpler and faster than the full search - just scrapes known URLs.

Usage:
    python scripts/scrape_discovered_urls_firecrawl.py

    # Then load to database
    python scripts/load_data_to_supabase.py --csv data/media_statements/firecrawl_scraped_results.csv
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import re
import time

# Load environment
load_dotenv()


class FirecrawlURLScraper:
    """Scrape known URLs using Firecrawl"""

    def __init__(self):
        """Initialize with Firecrawl"""
        self.output_dir = Path(__file__).parent.parent / 'data' / 'media_statements'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Check for Firecrawl API key
        self.firecrawl_api_key = os.getenv('FIRECRAWL_API_KEY')

        if not self.firecrawl_api_key:
            print("\n⚠️  FIRECRAWL_API_KEY not found in .env")
            print("   Add your Firecrawl API key to .env file:")
            print("   FIRECRAWL_API_KEY=your_key_here")
            print("\n   Get a free API key at: https://firecrawl.dev")
            sys.exit(1)

        # Initialize Firecrawl
        try:
            from firecrawl import FirecrawlApp
            self.firecrawl = FirecrawlApp(api_key=self.firecrawl_api_key)
            print("✅ Firecrawl initialized")
        except Exception as e:
            print(f"\n❌ Error initializing Firecrawl: {e}")
            print("   Install: pip install firecrawl-py")
            sys.exit(1)

    def load_urls(self) -> List[str]:
        """Load URLs from file"""
        urls_file = self.output_dir / 'urls_to_scrape.txt'

        if not urls_file.exists():
            print(f"\n❌ File not found: {urls_file}")
            print("   Run WebSearch first to generate URLs")
            sys.exit(1)

        with open(urls_file, 'r') as f:
            urls = [line.strip() for line in f if line.strip() and 'statements.qld.gov.au' in line]

        print(f"\n✅ Loaded {len(urls)} URLs to scrape")
        return urls

    def scrape_statement(self, url: str) -> Optional[Dict]:
        """
        Scrape a single statement using Firecrawl

        Args:
            url: Statement URL

        Returns:
            Dict of extracted data or None
        """
        try:
            # Scrape with Firecrawl
            result = self.firecrawl.scrape(
                url,
                formats=['markdown'],
                only_main_content=True
            )

            # Extract data from Document object
            markdown = getattr(result, 'markdown', '') or ''
            metadata = getattr(result, 'metadata', {}) or {}

            # Extract title
            title = metadata.get('title', '') or metadata.get('ogTitle', '')

            # Extract date
            date = metadata.get('publishedTime', '') or metadata.get('modifiedTime', '')
            if date:
                date = date[:10]  # YYYY-MM-DD
            else:
                date = datetime.now().strftime('%Y-%m-%d')

            # Extract minister from content
            minister = "Queensland Government"
            minister_match = re.search(r'(Minister|Hon|Premier)\s+([A-Z][a-z]+\s+[A-Z][a-z]+)', markdown)
            if minister_match:
                minister = minister_match.group(0)

            # Extract funding amounts
            amounts = re.findall(r'\$\s*(\d+(?:\.\d+)?)\s*(million|billion|M|B)', markdown, re.IGNORECASE)

            funding_amount = ""
            if amounts:
                amount, unit = amounts[0]
                if unit.lower() in ['billion', 'b']:
                    funding_amount = f"${float(amount) * 1000}M"
                else:
                    funding_amount = f"${amount}M"

            # Extract program names
            program_matches = []
            for keyword in ['on-country', 'co-responder', 'youth justice', 'diversion', 'detention']:
                if keyword.lower() in markdown.lower():
                    program_matches.append(keyword.title())

            program_name = ', '.join(program_matches[:3]) if program_matches else "Youth Justice"

            # Extract communities
            communities_keywords = ['Mount Isa', 'Doomadgee', 'Mornington Island', 'Palm Island',
                                   'Aurukun', 'Yarrabah', 'Townsville']
            communities = []
            for community in communities_keywords:
                if community.lower() in markdown.lower():
                    communities.append(community)

            recipient = ', '.join(communities[:2]) if communities else ""

            return {
                'url': url,
                'title': title,
                'date': date,
                'minister': minister,
                'funding_amount': funding_amount,
                'program_name': program_name,
                'recipient_organization': recipient,
                'description': markdown[:500],
                'statement_id': url.split('/')[-1] if '/' in url else url
            }

        except Exception as e:
            print(f"  ❌ Error: {e}")
            return None

    def scrape_all(self, urls: List[str]) -> List[Dict]:
        """Scrape all URLs"""
        print("\n" + "=" * 80)
        print("📥 SCRAPING URLS WITH FIRECRAWL")
        print("=" * 80)

        print(f"\nTotal URLs: {len(urls)}")
        print(f"Estimated time: ~{len(urls) * 2} seconds ({len(urls) * 2 / 60:.1f} minutes)\n")

        statements = []

        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] {url[:60]}...")

            statement = self.scrape_statement(url)

            if statement:
                statements.append(statement)
                if statement['title']:
                    print(f"  ✅ {statement['title'][:50]}")
                if statement['funding_amount']:
                    print(f"  💰 {statement['funding_amount']}")
            else:
                print(f"  ⚠️  Failed")

            # Rate limiting
            time.sleep(2)

        print(f"\n✅ Scraping complete: {len(statements)} statements extracted")

        return statements

    def deduplicate(self, new_statements: List[Dict]) -> List[Dict]:
        """Deduplicate against existing data"""
        print("\n" + "=" * 80)
        print("🔍 DEDUPLICATION")
        print("=" * 80)

        existing_file = self.output_dir / 'mount_isa_statements_recovered.csv'

        existing_urls = set()
        if existing_file.exists():
            existing_df = pd.read_csv(existing_file)
            existing_urls = set(existing_df['url'].tolist())
            print(f"\n📊 Existing statements: {len(existing_urls)}")

        unique_statements = []
        duplicates = 0

        for statement in new_statements:
            if statement['url'] not in existing_urls:
                unique_statements.append(statement)
            else:
                duplicates += 1

        print(f"📊 New statements scraped: {len(new_statements)}")
        print(f"📊 Duplicates: {duplicates}")
        print(f"✅ Unique new statements: {len(unique_statements)}")

        return unique_statements

    def save_results(self, statements: List[Dict]):
        """Save results to CSV"""
        if not statements:
            print("\n⚠️  No new statements to save")
            return

        df = pd.DataFrame(statements)

        output_file = self.output_dir / 'firecrawl_scraped_results.csv'
        df.to_csv(output_file, index=False)

        print("\n" + "=" * 80)
        print("💾 RESULTS SAVED")
        print("=" * 80)

        print(f"\n✅ Saved {len(statements)} statements to: {output_file}")

        # Summary stats
        total_funding = 0
        for statement in statements:
            if statement['funding_amount']:
                match = re.search(r'\$(\d+(?:\.\d+)?)', statement['funding_amount'])
                if match:
                    total_funding += float(match.group(1))

        print(f"\n📊 SUMMARY:")
        print(f"  Total new statements: {len(statements)}")
        print(f"  Total funding: ${total_funding:.1f}M")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  Ministers: {df['minister'].nunique()}")
        print(f"  Programs: {df['program_name'].nunique()}")

        print(f"\n💡 NEXT STEP:")
        print(f"  Load to database:")
        print(f"  python scripts/load_data_to_supabase.py --csv {output_file}")


def main():
    """Main execution"""
    print("\n" + "=" * 80)
    print("🚀 SCRAPE DISCOVERED URLS - FIRECRAWL")
    print("=" * 80)

    try:
        scraper = FirecrawlURLScraper()

        # Load URLs
        urls = scraper.load_urls()

        # Scrape all URLs
        statements = scraper.scrape_all(urls)

        # Deduplicate
        unique_statements = scraper.deduplicate(statements)

        # Save
        if unique_statements:
            scraper.save_results(unique_statements)
        else:
            print("\n⚠️  No new statements (all were duplicates)")

        print("\n" + "=" * 80)
        print("✅ COMPLETE")
        print("=" * 80)

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
