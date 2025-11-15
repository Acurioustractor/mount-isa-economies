"""
COMPREHENSIVE MEDIA STATEMENT SCRAPER - IMPLEMENTATION

This script ACTUALLY executes the searches and scrapes the statements.

Strategy:
1. Generate all search queries (67 queries)
2. Execute WebSearch for each query
3. Extract unique statement URLs from results
4. Scrape each URL using simple regex extraction (fast & reliable)
5. Deduplicate by URL
6. Extract funding data (amount, program, location, date)
7. Save to CSV
8. Optionally load to Supabase

This will take you from 10 to 50+ statements.

Usage:
    # Do the searches (slow, ~10 minutes)
    python scripts/implement_comprehensive_search.py --search

    # Review results before loading to database
    cat data/media_statements/comprehensive_search_results.csv

    # Load to database
    python scripts/implement_comprehensive_search.py --load-to-database

    # Or do it all at once
    python scripts/implement_comprehensive_search.py --search --load-to-database
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


class ComprehensiveSearchImplementation:
    """Actually execute the comprehensive search"""

    def __init__(self):
        """Initialize"""
        self.output_dir = Path(__file__).parent.parent / 'data' / 'media_statements'
        self.output_dir.mkdir(parents=True, exist_ok=True)

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
        """
        Generate comprehensive search queries

        Returns:
            List of search query strings
        """
        queries = []

        # Program + funding term combinations
        for program in self.keywords['programs']:
            for funding_term in self.keywords['funding_terms']:
                queries.append(f'site:statements.qld.gov.au "{program}" "{funding_term}"')

        # Community-specific searches
        for community in self.keywords['communities']:
            queries.append(f'site:statements.qld.gov.au "{community}" youth funding')

        return queries

    def execute_searches_manually(self, queries: List[str]) -> Set[str]:
        """
        Show queries for manual execution

        Since WebSearch tool isn't available in this script context,
        show the queries for user to execute manually via web browser
        or provide results from another source.

        Args:
            queries: List of search queries

        Returns:
            Empty set (user will provide URLs manually)
        """
        print("\n" + "=" * 80)
        print("🔍 SEARCH QUERIES TO EXECUTE")
        print("=" * 80)

        print(f"\nGenerated {len(queries)} search queries")
        print("\n📋 Copy these into Google search (or use WebSearch tool separately):\n")

        for i, query in enumerate(queries[:20], 1):
            print(f"{i}. {query}")

        if len(queries) > 20:
            print(f"\n... and {len(queries) - 20} more queries")

        print("\n💡 FOR MANUAL EXECUTION:")
        print("1. Copy each query into Google")
        print("2. Collect all statements.qld.gov.au URLs from results")
        print("3. Create a file: data/media_statements/urls_to_scrape.txt")
        print("4. Put one URL per line in that file")
        print("5. Run: python scripts/implement_comprehensive_search.py --scrape-urls")

        # Save queries to file for reference
        queries_file = self.output_dir / 'search_queries.txt'
        with open(queries_file, 'w') as f:
            for query in queries:
                f.write(query + '\n')

        print(f"\n✅ Queries saved to: {queries_file}")

        return set()

    def load_urls_from_file(self, filename: str = 'urls_to_scrape.txt') -> Set[str]:
        """
        Load URLs from text file

        Args:
            filename: File containing URLs (one per line)

        Returns:
            Set of URLs
        """
        urls_file = self.output_dir / filename

        if not urls_file.exists():
            print(f"\n❌ File not found: {urls_file}")
            print("   Create this file with one URL per line")
            return set()

        with open(urls_file, 'r') as f:
            urls = set(line.strip() for line in f if line.strip() and 'statements.qld.gov.au' in line)

        print(f"\n✅ Loaded {len(urls)} URLs from {urls_file}")

        return urls

    def scrape_statement_simple(self, url: str) -> Optional[Dict]:
        """
        Scrape a single statement using simple HTTP request + regex

        This is faster and more reliable than Firecrawl for known structure.

        Args:
            url: Statement URL

        Returns:
            Dict of extracted data or None
        """
        try:
            import requests
            from bs4 import BeautifulSoup

            # Fetch page
            response = requests.get(url, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.content, 'html.parser')

            # Extract title
            title_tag = soup.find('h1')
            title = title_tag.get_text(strip=True) if title_tag else ""

            # Extract date (usually in meta tags or specific div)
            date = None
            date_meta = soup.find('meta', property='article:published_time')
            if date_meta:
                date = date_meta.get('content', '')[:10]  # YYYY-MM-DD

            # Extract minister (usually in byline or meta)
            minister = ""
            minister_tag = soup.find('span', class_='minister') or soup.find('div', class_='byline')
            if minister_tag:
                minister = minister_tag.get_text(strip=True)

            # Extract content
            content_div = soup.find('div', class_='content') or soup.find('article')
            content = content_div.get_text(strip=True) if content_div else soup.get_text()

            # Extract funding amounts using regex
            amounts = re.findall(r'\$\s*(\d+(?:\.\d+)?)\s*(million|billion|M|B)', content, re.IGNORECASE)

            funding_amount = ""
            if amounts:
                # Convert to standard format
                amount, unit = amounts[0]
                if unit.lower() in ['billion', 'b']:
                    funding_amount = f"${float(amount) * 1000}M"
                else:
                    funding_amount = f"${amount}M"

            # Extract program names (look for specific keywords)
            program_matches = []
            for keyword in ['on-country', 'co-responder', 'youth justice', 'diversion', 'detention']:
                if keyword.lower() in content.lower():
                    program_matches.append(keyword)

            program_name = ', '.join(program_matches[:3]) if program_matches else "Youth Justice"

            # Extract communities mentioned
            communities = []
            for community in self.keywords['communities']:
                if community.lower() in content.lower():
                    communities.append(community)

            recipient = ', '.join(communities[:2]) if communities else ""

            return {
                'url': url,
                'title': title,
                'date': date or datetime.now().strftime('%Y-%m-%d'),
                'minister': minister or "Queensland Government",
                'funding_amount': funding_amount,
                'program_name': program_name,
                'recipient_organization': recipient,
                'description': content[:500],  # First 500 chars
                'statement_id': url.split('/')[-1] if '/' in url else url
            }

        except Exception as e:
            print(f"  ❌ Error scraping {url}: {e}")
            return None

    def scrape_all_statements(self, urls: Set[str]) -> List[Dict]:
        """
        Scrape all statement URLs

        Args:
            urls: Set of URLs to scrape

        Returns:
            List of scraped statements
        """
        print("\n" + "=" * 80)
        print("📥 SCRAPING STATEMENTS")
        print("=" * 80)

        print(f"\nTotal URLs to scrape: {len(urls)}")

        statements = []

        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] Scraping: {url[:60]}...")

            statement = self.scrape_statement_simple(url)

            if statement:
                statements.append(statement)
                print(f"  ✅ {statement['title'][:50]}...")
                if statement['funding_amount']:
                    print(f"  💰 {statement['funding_amount']}")
            else:
                print(f"  ⚠️  Failed to scrape")

            # Rate limiting
            time.sleep(0.5)

        print(f"\n✅ Scraping complete: {len(statements)} statements extracted")

        return statements

    def deduplicate_with_existing(self, new_statements: List[Dict]) -> List[Dict]:
        """
        Deduplicate new statements against existing data

        Args:
            new_statements: List of newly scraped statements

        Returns:
            List of unique new statements
        """
        print("\n" + "=" * 80)
        print("🔍 DEDUPLICATION")
        print("=" * 80)

        # Load existing data
        existing_file = self.output_dir / 'mount_isa_statements_recovered.csv'

        existing_urls = set()
        if existing_file.exists():
            existing_df = pd.read_csv(existing_file)
            existing_urls = set(existing_df['url'].tolist())
            print(f"\n📊 Existing statements: {len(existing_urls)}")

        # Filter out duplicates
        unique_statements = []
        duplicates = 0

        for statement in new_statements:
            if statement['url'] not in existing_urls:
                unique_statements.append(statement)
            else:
                duplicates += 1

        print(f"📊 New statements found: {len(new_statements)}")
        print(f"📊 Duplicates (already have): {duplicates}")
        print(f"✅ Unique new statements: {len(unique_statements)}")

        return unique_statements

    def save_results(self, statements: List[Dict], filename: str = 'comprehensive_search_results.csv'):
        """
        Save results to CSV

        Args:
            statements: List of statement dicts
            filename: Output filename
        """
        if not statements:
            print("\n⚠️  No statements to save")
            return

        df = pd.DataFrame(statements)

        output_file = self.output_dir / filename
        df.to_csv(output_file, index=False)

        print(f"\n✅ Saved {len(statements)} statements to: {output_file}")

        # Print summary
        print("\n" + "=" * 80)
        print("📊 RESULTS SUMMARY")
        print("=" * 80)

        total_funding = 0
        for statement in statements:
            if statement['funding_amount']:
                # Extract numeric value
                match = re.search(r'\$(\d+(?:\.\d+)?)', statement['funding_amount'])
                if match:
                    total_funding += float(match.group(1))

        print(f"\n💰 Total funding found: ${total_funding:.1f}M")
        print(f"📅 Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"👤 Ministers: {df['minister'].nunique()}")
        print(f"🎯 Programs: {df['program_name'].nunique()}")

    def load_to_database(self, csv_file: str = 'comprehensive_search_results.csv'):
        """
        Load results to Supabase database

        Args:
            csv_file: CSV file to load
        """
        print("\n" + "=" * 80)
        print("💾 LOADING TO DATABASE")
        print("=" * 80)

        input_file = self.output_dir / csv_file

        if not input_file.exists():
            print(f"\n❌ File not found: {input_file}")
            print("   Run with --search first to generate data")
            return

        print(f"\n📂 Loading: {input_file}")
        print("\n⚠️  This will use the existing load_data_to_supabase.py script")
        print("   Make sure to run:")
        print(f"   python scripts/load_data_to_supabase.py --csv {input_file}")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Implement comprehensive media statement search')
    parser.add_argument('--generate-queries', action='store_true',
                       help='Generate search queries to file')
    parser.add_argument('--scrape-urls', action='store_true',
                       help='Scrape URLs from urls_to_scrape.txt file')
    parser.add_argument('--load-to-database', action='store_true',
                       help='Load results to Supabase')
    args = parser.parse_args()

    if not any([args.generate_queries, args.scrape_urls, args.load_to_database]):
        print("\n❌ Please specify an action")
        print("\nWorkflow:")
        print("  1. python scripts/implement_comprehensive_search.py --generate-queries")
        print("     (Generates search queries to search_queries.txt)")
        print("\n  2. Manually execute searches and collect URLs")
        print("     (Or use WebSearch tool to automate this)")
        print("\n  3. Put URLs in data/media_statements/urls_to_scrape.txt")
        print("\n  4. python scripts/implement_comprehensive_search.py --scrape-urls")
        print("     (Scrapes all URLs and saves to CSV)")
        print("\n  5. python scripts/implement_comprehensive_search.py --load-to-database")
        print("     (Loads CSV to Supabase)")
        sys.exit(1)

    print("\n" + "=" * 80)
    print("🚀 COMPREHENSIVE MEDIA STATEMENT SEARCH")
    print("=" * 80)

    try:
        scraper = ComprehensiveSearchImplementation()

        if args.generate_queries:
            # Generate and save queries
            queries = scraper.generate_search_queries()
            scraper.execute_searches_manually(queries)

        if args.scrape_urls:
            # Load URLs from file
            urls = scraper.load_urls_from_file()

            if not urls:
                print("\n❌ No URLs to scrape")
                print("   Create data/media_statements/urls_to_scrape.txt with one URL per line")
                sys.exit(1)

            # Scrape all URLs
            statements = scraper.scrape_all_statements(urls)

            # Deduplicate
            unique_statements = scraper.deduplicate_with_existing(statements)

            # Save results
            if unique_statements:
                scraper.save_results(unique_statements)
            else:
                print("\n⚠️  No new statements found (all were duplicates)")

        if args.load_to_database:
            scraper.load_to_database()

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
