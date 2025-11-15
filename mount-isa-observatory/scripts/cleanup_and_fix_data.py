"""
CLEANUP AND FIX DATA

Fixes common issues:
1. Remove error pages and 404s
2. Fix dates that defaulted to today
3. Re-extract data from CSV with better parsing

Usage:
    python scripts/cleanup_and_fix_data.py --remove-errors
    python scripts/cleanup_and_fix_data.py --fix-dates --csv /path/to/csv
"""

import os
import sys
import argparse
from pathlib import Path
from datetime import datetime
import pandas as pd
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


class DataCleaner:
    """Clean and fix database data"""

    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not self.supabase_url or not self.supabase_key:
            print("\n❌ Missing Supabase credentials")
            sys.exit(1)

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        print("✅ Connected to Supabase")

    def remove_error_documents(self):
        """Remove error pages and 404s"""
        print("\n" + "=" * 80)
        print("🧹 REMOVING ERROR DOCUMENTS")
        print("=" * 80)

        # Find error documents
        error_patterns = [
            'Error - Ministerial Media Statements',
            '404 Error',
            'Page not found',
            '\n\tError'
        ]

        deleted = 0
        for pattern in error_patterns:
            result = self.supabase.table('documents').delete().ilike('title', f'%{pattern}%').execute()
            if result.data:
                count = len(result.data)
                deleted += count
                print(f"  ✅ Removed {count} documents matching '{pattern}'")

        # Also remove documents with null funding and error in title
        result = self.supabase.table('documents').delete().is_('funding_amount_extracted', 'null').ilike('title', '%error%').execute()
        if result.data:
            count = len(result.data)
            deleted += count
            print(f"  ✅ Removed {count} error documents with no funding")

        print(f"\n✅ Total removed: {deleted} documents")

        # Show what's left
        remaining = self.supabase.table('documents').select('id', count='exact').execute()
        print(f"✅ Remaining documents: {remaining.count}")

    def fix_dates_from_csv(self, csv_path: str):
        """Re-import dates from CSV"""
        print("\n" + "=" * 80)
        print("📅 FIXING DATES FROM CSV")
        print("=" * 80)

        if not Path(csv_path).exists():
            print(f"\n❌ CSV not found: {csv_path}")
            return

        df = pd.read_csv(csv_path)
        print(f"\n✅ Loaded {len(df)} rows from CSV")

        # Parse dates properly
        df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')

        # Remove rows with invalid dates
        df = df.dropna(subset=['date'])
        print(f"✅ {len(df)} rows have valid dates")

        # Update each document
        updated = 0
        errors = 0

        for _, row in df.iterrows():
            try:
                url = row['url']
                date_str = row['date'].strftime('%Y-%m-%d')

                # Update by URL
                result = self.supabase.table('documents').update({
                    'published_date': date_str
                }).eq('url', url).execute()

                if result.data:
                    updated += 1
                    if updated % 10 == 0:
                        print(f"  Updated {updated}/{len(df)}...")

            except Exception as e:
                errors += 1
                if errors < 5:
                    print(f"  ⚠️ Error updating {row.get('url', 'unknown')}: {e}")

        print(f"\n✅ Updated {updated} documents")
        if errors > 0:
            print(f"⚠️  {errors} errors (likely documents not in database)")

    def show_stats(self):
        """Show database statistics"""
        print("\n" + "=" * 80)
        print("📊 DATABASE STATISTICS")
        print("=" * 80)

        # Total documents
        total = self.supabase.table('documents').select('id', count='exact').execute()
        print(f"\nTotal documents: {total.count}")

        # Documents with funding
        with_funding = self.supabase.table('documents').select('id', count='exact').not_.is_('funding_amount_extracted', 'null').execute()
        print(f"With funding amounts: {with_funding.count}")

        # Date range
        dates_result = self.supabase.table('documents').select('published_date').execute()
        if dates_result.data:
            dates = [d['published_date'] for d in dates_result.data]
            unique_dates = set(dates)
            print(f"Unique dates: {len(unique_dates)}")

            # Check if too many have today's date
            today = datetime.now().strftime('%Y-%m-%d')
            today_count = dates.count(today)
            if today_count > 0:
                print(f"⚠️  Documents with today's date: {today_count} (likely missing real dates)")

        # By location
        print("\nDocuments by location (top 10):")
        docs = self.supabase.table('documents').select('locations_mentioned').execute()
        from collections import Counter
        all_locations = []
        for doc in docs.data:
            if doc.get('locations_mentioned'):
                all_locations.extend(doc['locations_mentioned'])

        location_counts = Counter(all_locations)
        for location, count in location_counts.most_common(10):
            print(f"  {location}: {count}")


def main():
    parser = argparse.ArgumentParser(description='Clean and fix database data')
    parser.add_argument('--remove-errors', action='store_true', help='Remove error pages and 404s')
    parser.add_argument('--fix-dates', action='store_true', help='Fix dates from CSV')
    parser.add_argument('--csv', help='Path to CSV file for date fixing')
    parser.add_argument('--stats', action='store_true', help='Show database statistics')
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🔧 DATA CLEANUP & FIX")
    print("=" * 80)

    cleaner = DataCleaner()

    if args.remove_errors:
        cleaner.remove_error_documents()

    if args.fix_dates:
        if not args.csv:
            print("\n❌ --csv required for --fix-dates")
            sys.exit(1)
        cleaner.fix_dates_from_csv(args.csv)

    if args.stats or (not args.remove_errors and not args.fix_dates):
        cleaner.show_stats()

    print("\n" + "=" * 80)
    print("✅ COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
