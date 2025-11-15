"""
AUTOMATED COMPREHENSIVE SEARCH - Using Firecrawl

This script FULLY AUTOMATES the comprehensive search using Firecrawl:
1. Executes all search queries via Google
2. Extracts statement URLs from search results
3. Scrapes each URL with Firecrawl
4. Extracts funding data
5. Deduplicates
6. Saves to CSV

No manual steps required - just run it!

Usage:
    # Full automation (slow but thorough)
    python scripts/automated_comprehensive_search_firecrawl.py

    # Test mode (first 5 queries only)
    python scripts/automated_comprehensive_search_firecrawl.py --test

    # Then load to database
    python scripts/load_data_to_supabase.py --csv data/media_statements/firecrawl_comprehensive_results.csv
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Set
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import re
import time
import json

# Load environment
load_dotenv()


class FirecrawlComprehensiveSearch:
    """Fully automated comprehensive search using Firecrawl"""

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
            print("\n   Or run in manual mode:")
            print("   python scripts/implement_comprehensive_search.py --generate-queries")
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

        # Search keywords
        self.keywords = {
            'programs': [
                'youth justice',
                'young people',
                'juvenile',
                'on-country',
                'co-responder',
                'diversion',
            ],
            'communities': [
                'Mount Isa',
                'Doomadgee',
                'Mornington Island',
                'Palm Island',
                'Aurukun',
                'Yarrabah',
                'Townsville',
            ],
            'funding_terms': [
                'million',
                'funding',
                'investment',
                'budget',
            ]
        }

        self.found_urls = set()
        self.scraped_statements = []

    def generate_search_queries(self) -> List[str]:
        """Generate comprehensive search queries"""
        queries = []

        # Program + funding term combinations
        for program in self.keywords['programs']:
            for funding_term in self.keywords['funding_terms']:
                queries.append(f'site:statements.qld.gov.au "{program}" "{funding_term}"')

        # Community-specific searches
        for community in self.keywords['communities']:
            queries.append(f'site:statements.qld.gov.au "{community}" youth funding')

        return queries

    def search_with_firecrawl(self, query: str) -> List[str]:
        """
        Execute a search using Firecrawl's search API

        Args:
            query: Search query

        Returns:
            List of URLs found
        """
        try:
            print(f"  Searching: {query[:60]}...")

            # Use Firecrawl search API
            result = self.firecrawl.search(
                query,
                limit=10  # Get top 10 results per query
            )

            # Extract URLs from search results
            urls = []
            if hasattr(result, 'data'):
                for item in result.data:
                    if hasattr(item, 'url') and 'statements.qld.gov.au' in item.url:
                        urls.append(item.url)

            # Deduplicate
            urls = list(set(urls))

            print(f"  ✅ Found {len(urls)} URLs")

            return urls

        except Exception as e:
            print(f"  ❌ Search error: {e}")
            return []

    def execute_all_searches(self, queries: List[str], test_mode: bool = False) -> Set[str]:
        """
        Execute all search queries

        Args:
            queries: List of search queries
            test_mode: If True, only run first 5 queries

        Returns:
            Set of unique URLs found
        """
        print("\n" + "=" * 80)
        print("🔍 EXECUTING AUTOMATED SEARCHES")
        print("=" * 80)

        if test_mode:
            queries = queries[:5]
            print(f"\n⚠️  TEST MODE: Running first 5 queries only")

        print(f"\nTotal queries: {len(queries)}")
        print(f"Estimated time: ~{len(queries) * 5} seconds ({len(queries) * 5 / 60:.1f} minutes)\n")

        all_urls = set()

        for i, query in enumerate(queries, 1):
            print(f"\n[{i}/{len(queries)}]", end=" ")

            urls = self.search_with_firecrawl(query)
            all_urls.update(urls)

            print(f"  Total unique URLs so far: {len(all_urls)}")

            # Rate limiting (Firecrawl has limits)
            time.sleep(3)

        print(f"\n✅ Search complete: {len(all_urls)} unique URLs found")

        # Save URLs to file
        urls_file = self.output_dir / 'found_urls.txt'
        with open(urls_file, 'w') as f:
            for url in sorted(all_urls):
                f.write(url + '\n')

        print(f"✅ URLs saved to: {urls_file}")

        return all_urls

    def scrape_statement_firecrawl(self, url: str) -> Optional[Dict]:
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
            communities = []
            for community in self.keywords['communities']:
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
            print(f"  ❌ Error scraping {url}: {e}")
            return None

    def scrape_all_urls(self, urls: Set[str]) -> List[Dict]:
        """
        Scrape all URLs using Firecrawl

        Args:
            urls: Set of URLs to scrape

        Returns:
            List of scraped statements
        """
        print("\n" + "=" * 80)
        print("📥 SCRAPING ALL URLS WITH FIRECRAWL")
        print("=" * 80)

        print(f"\nTotal URLs: {len(urls)}")
        print(f"Estimated time: ~{len(urls) * 2} seconds ({len(urls) * 2 / 60:.1f} minutes)\n")

        statements = []

        for i, url in enumerate(sorted(urls), 1):
            print(f"\n[{i}/{len(urls)}] {url[:60]}...")

            statement = self.scrape_statement_firecrawl(url)

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

    def deduplicate_with_existing(self, new_statements: List[Dict]) -> List[Dict]:
        """
        Deduplicate against existing data

        Args:
            new_statements: List of newly scraped statements

        Returns:
            List of unique new statements
        """
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

        output_file = self.output_dir / 'firecrawl_comprehensive_results.csv'
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
    import argparse

    parser = argparse.ArgumentParser(description='Automated comprehensive search with Firecrawl')
    parser.add_argument('--test', action='store_true',
                       help='Test mode (first 5 queries only)')
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🚀 AUTOMATED COMPREHENSIVE SEARCH - FIRECRAWL")
    print("=" * 80)

    try:
        searcher = FirecrawlComprehensiveSearch()

        # Generate queries
        queries = searcher.generate_search_queries()
        print(f"\n📋 Generated {len(queries)} search queries")

        if args.test:
            print("\n⚠️  TEST MODE: Will run 5 queries only")
            print("   Remove --test flag for full search")

        # Execute searches
        urls = searcher.execute_all_searches(queries, test_mode=args.test)

        if not urls:
            print("\n❌ No URLs found")
            sys.exit(1)

        # Scrape all URLs
        statements = searcher.scrape_all_urls(urls)

        # Deduplicate
        unique_statements = searcher.deduplicate_with_existing(statements)

        # Save
        if unique_statements:
            searcher.save_results(unique_statements)
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
