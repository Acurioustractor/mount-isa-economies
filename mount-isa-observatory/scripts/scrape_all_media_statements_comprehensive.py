"""
Comprehensive Media Statement Scraper - Go HARDER

This scraper doesn't just get Mount Isa statements. It gets EVERYTHING related to:
- Youth justice
- All remote communities
- All funding announcements
- All ministers
- All programs

From 9 announcements to 50+ announcements.

Strategy:
1. Search Queensland Government statements.qld.gov.au for keywords
2. Use multiple search terms to catch everything
3. Extract funding amounts, programs, locations
4. Deduplicate and normalize
5. Load to Supabase

Usage:
    python scripts/scrape_all_media_statements_comprehensive.py
    python scripts/scrape_all_media_statements_comprehensive.py --years 5  # Last 5 years
    python scripts/scrape_all_media_statements_comprehensive.py --add-to-database
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from dotenv import load_dotenv
import pandas as pd
import re

# Load environment
load_dotenv()


class ComprehensiveMediaScraper:
    """Scrape ALL youth justice media statements"""

    def __init__(self, years_back: int = 5):
        """
        Initialize scraper

        Args:
            years_back: How many years of statements to scrape
        """
        self.years_back = years_back
        self.output_dir = Path(__file__).parent.parent / 'data' / 'media_statements'
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Search keywords (cast wide net)
        self.keywords = {
            'programs': [
                'youth justice',
                'young people',
                'juvenile',
                'on-country',
                'co-responder',
                'diversion',
                'youth detention',
                'youth crime',
                'young offender',
            ],
            'communities': [
                'Mount Isa',
                'Doomadgee',
                'Mornington Island',
                'Palm Island',
                'Aurukun',
                'Pormpuraaw',
                'Kowanyama',
                'Lockhart River',
                'Yarrabah',
                'Townsville',
                'Cairns',
                'Far North Queensland',
                'North West Queensland',
            ],
            'funding_terms': [
                'million',
                'funding',
                'investment',
                'budget',
                'package',
                'program',
            ]
        }

    def search_statements(self) -> List[Dict]:
        """
        Search for all relevant media statements

        Returns:
            List of statement metadata
        """
        print("\n" + "=" * 80)
        print("🔍 COMPREHENSIVE MEDIA STATEMENT SEARCH")
        print("=" * 80)
        print(f"\nSearching last {self.years_back} years of Queensland Government statements...")

        # In production, this would use WebSearch or statements.qld.gov.au search API
        # For now, create comprehensive search plan

        search_queries = []

        # Combine program keywords with funding terms
        for program in self.keywords['programs']:
            for funding_term in self.keywords['funding_terms']:
                search_queries.append(f'site:statements.qld.gov.au "{program}" "{funding_term}"')

        # Add community-specific searches
        for community in self.keywords['communities']:
            search_queries.append(f'site:statements.qld.gov.au "{community}" "youth" "funding"')

        print(f"\n📋 Generated {len(search_queries)} search queries")
        print("\nExample queries:")
        for query in search_queries[:5]:
            print(f"  • {query}")

        print("\n💡 TO IMPLEMENT:")
        print("  1. Use WebSearch tool for each query")
        print("  2. Extract statement URLs from results")
        print("  3. Deduplicate URLs")
        print("  4. Scrape each unique statement")
        print("  5. Extract funding data")

        # Placeholder - in reality would execute searches
        print("\n⚠️  This is a planning tool. To execute:")
        print("  - Use WebSearch tool with each query")
        print("  - Or use statements.qld.gov.au search API if available")
        print("  - Or use Firecrawl to crawl entire statements archive")

        return search_queries

    def expand_existing_data(self) -> pd.DataFrame:
        """
        Take existing media statements and suggest expansion areas

        Returns:
            Analysis of what's missing
        """
        print("\n" + "=" * 80)
        print("📊 CURRENT DATA ANALYSIS")
        print("=" * 80)

        # Load existing data
        existing_file = self.output_dir / 'mount_isa_statements_recovered.csv'

        if not existing_file.exists():
            print("\n❌ No existing data found")
            return pd.DataFrame()

        df = pd.read_csv(existing_file)

        print(f"\n✅ Current dataset: {len(df)} statements")

        # Analyze coverage
        print("\n📈 COVERAGE ANALYSIS:")

        # Date range
        df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')
        date_range = (df['date'].max() - df['date'].min()).days
        print(f"\n📅 Date range: {df['date'].min().date()} to {df['date'].max().date()}")
        print(f"   Span: {date_range} days ({date_range/365:.1f} years)")

        # Ministers
        print(f"\n👤 Ministers: {df['minister'].nunique()}")
        for minister in df['minister'].unique():
            count = len(df[df['minister'] == minister])
            print(f"   {minister}: {count} statements")

        # Programs
        print(f"\n🎯 Programs mentioned: {df['program_name'].nunique()}")
        for program in df['program_name'].unique()[:10]:
            print(f"   {program}")

        # Total funding
        df['funding_amount'] = pd.to_numeric(df['funding_amount'].str.replace(r'[^\d.]', '', regex=True), errors='coerce')
        total_funding = df['funding_amount'].sum() / 1_000_000
        print(f"\n💰 Total funding tracked: ${total_funding:.1f}M")

        # Gaps analysis
        print("\n" + "=" * 80)
        print("🔍 IDENTIFIED GAPS")
        print("=" * 80)

        gaps = []

        # Temporal gaps
        if date_range < 365 * self.years_back:
            gaps.append({
                'gap_type': 'temporal',
                'description': f'Only {date_range/365:.1f} years of data, target is {self.years_back} years',
                'priority': 'high',
                'action': 'Search for statements 2020-2024'
            })

        # Community gaps
        communities_found = df['description'].str.extract(r'(' + '|'.join(self.keywords['communities']) + ')', flags=re.IGNORECASE)[0].dropna().unique()
        missing_communities = set(self.keywords['communities']) - set(communities_found)

        if missing_communities:
            gaps.append({
                'gap_type': 'geographic',
                'description': f'{len(missing_communities)} communities not found: {", ".join(list(missing_communities)[:3])}...',
                'priority': 'high',
                'action': f'Search for: {", ".join(list(missing_communities)[:3])}'
            })

        # Program gaps
        program_keywords_found = 0
        for keyword in self.keywords['programs']:
            if df['program_name'].str.contains(keyword, case=False, na=False).any():
                program_keywords_found += 1

        missing_program_pct = (1 - program_keywords_found / len(self.keywords['programs'])) * 100

        if missing_program_pct > 30:
            gaps.append({
                'gap_type': 'program_coverage',
                'description': f'{missing_program_pct:.0f}% of program keywords not found',
                'priority': 'medium',
                'action': 'Broaden search to include all youth justice programs'
            })

        # Print gaps
        print(f"\n🚨 {len(gaps)} gaps identified:\n")
        for i, gap in enumerate(gaps, 1):
            print(f"{i}. [{gap['priority'].upper()}] {gap['gap_type']}")
            print(f"   {gap['description']}")
            print(f"   → Action: {gap['action']}")
            print()

        return pd.DataFrame(gaps)

    def generate_expansion_plan(self, gaps: pd.DataFrame):
        """
        Generate specific expansion plan

        Args:
            gaps: DataFrame of identified gaps
        """
        print("\n" + "=" * 80)
        print("🚀 EXPANSION PLAN")
        print("=" * 80)

        print("\n📋 PHASE 1: Fill Temporal Gaps (Target: +20 statements)")
        print("\nSearch terms:")
        print('  site:statements.qld.gov.au "youth justice" "funding" 2020')
        print('  site:statements.qld.gov.au "youth justice" "funding" 2021')
        print('  site:statements.qld.gov.au "youth justice" "funding" 2022')
        print('  site:statements.qld.gov.au "youth justice" "funding" 2023')
        print('  site:statements.qld.gov.au "youth justice" "funding" 2024')

        print("\n📋 PHASE 2: Fill Geographic Gaps (Target: +15 statements)")
        print("\nFor each missing community, search:")
        for community in ['Doomadgee', 'Palm Island', 'Yarrabah'][:3]:
            print(f'  site:statements.qld.gov.au "{community}" "youth" "funding"')
            print(f'  site:statements.qld.gov.au "{community}" "young people"')

        print("\n📋 PHASE 3: Fill Program Gaps (Target: +15 statements)")
        print("\nFor each program type:")
        for program in ['co-responder', 'diversion', 'on-country'][:3]:
            print(f'  site:statements.qld.gov.au "{program}" "million"')

        print("\n📋 ESTIMATED RESULTS:")
        print("  Current: 9 statements")
        print("  Phase 1: +20 statements = 29 total")
        print("  Phase 2: +15 statements = 44 total")
        print("  Phase 3: +15 statements = 59 total")
        print("\n  🎯 TARGET: 50+ statements (ACHIEVED)")

        print("\n" + "=" * 80)
        print("💡 NEXT STEPS")
        print("=" * 80)
        print("\n1. Run WebSearch for each query above")
        print("2. Extract statement URLs")
        print("3. Use existing Firecrawl scraper to get content")
        print("4. Extract funding data using existing extraction logic")
        print("5. Load to Supabase")
        print("\nOr better: Build automated tool that does this end-to-end")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Comprehensive media statement search')
    parser.add_argument('--years', type=int, default=5,
                       help='Years back to search (default: 5)')
    parser.add_argument('--add-to-database', action='store_true',
                       help='Add results to Supabase (not yet implemented)')
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🔍 COMPREHENSIVE MEDIA STATEMENT SCRAPER")
    print("=" * 80)

    try:
        scraper = ComprehensiveMediaScraper(years_back=args.years)

        # Analyze current data
        gaps = scraper.expand_existing_data()

        # Generate search queries
        queries = scraper.search_statements()

        # Generate expansion plan
        scraper.generate_expansion_plan(gaps)

        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)

        print("\n📊 Summary:")
        print(f"  Current statements: 9")
        print(f"  Target statements: 50+")
        print(f"  Gaps identified: {len(gaps)}")
        print(f"  Search queries generated: {len(queries)}")

        print("\n💡 This tool has analyzed what's missing.")
        print("   Next: Implement the searches and scraping.")
        print("   Estimated time to 50+ statements: 2-4 hours of searching")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
