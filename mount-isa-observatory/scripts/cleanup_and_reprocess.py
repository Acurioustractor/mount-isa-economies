"""
ENHANCED CLEANUP WITH CONFIDENCE SCORING

Re-processes documents using multi-strategy extraction to fix:
- 94% of documents with wrong dates
- 70% missing funding amounts

Usage:
    python scripts/cleanup_and_reprocess.py --reprocess
    python scripts/cleanup_and_reprocess.py --stats
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Add scripts directory to path to import extractors
# Go up 3 levels: cleanup_and_reprocess.py -> scripts/ -> mount-isa-observatory/ -> mount-isa/ (repo root)
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))

from date_extractor import extract_date
from funding_extractor import extract_funding_amount
from validators import validate_document

load_dotenv()


class EnhancedDataCleaner:
    """Clean and fix database data with confidence scoring"""

    def __init__(self):
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not self.supabase_url or not self.supabase_key:
            print("\n❌ Missing Supabase credentials")
            print("Make sure SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are in your .env file")
            sys.exit(1)

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        print("✅ Connected to Supabase")

    def reprocess_with_confidence_scores(self):
        """
        Re-process all documents to add confidence scores
        This fixes the 94% date problem and 70% funding problem!
        """
        print("\n" + "=" * 80)
        print("🔄 RE-PROCESSING DOCUMENTS WITH CONFIDENCE SCORING")
        print("=" * 80)

        # Get all documents
        result = self.supabase.table('documents').select('*').execute()
        documents = result.data

        print(f"\nProcessing {len(documents)} documents...")

        stats = {
            'processed': 0,
            'dates_improved': 0,
            'funding_improved': 0,
            'high_confidence_dates': 0,
            'high_confidence_funding': 0,
            'needs_review': 0,
            'errors': 0
        }

        for i, doc in enumerate(documents, 1):
            try:
                # Extract content fields (use full_text or markdown_text)
                content = doc.get('full_text') or doc.get('markdown_text') or ''

                # === EXTRACT DATE WITH CONFIDENCE ===
                date, date_conf, date_method = extract_date(
                    text=content,
                    html=None,  # We don't have HTML stored
                    metadata=doc
                )

                # === EXTRACT FUNDING WITH CONFIDENCE ===
                amount, funding_conf, funding_method = extract_funding_amount(
                    text=content,
                    html=None,
                    metadata=doc
                )

                # === VALIDATE ===
                validation_doc = {
                    **doc,
                    'date': date,
                    'date_confidence': date_conf,
                    'funding_amount': float(amount) if amount else None,
                    'funding_confidence': funding_conf,
                }

                warnings, needs_review = validate_document(validation_doc)

                # === UPDATE DATABASE ===
                updates = {
                    'published_date_confidence': float(date_conf) if date_conf else None,
                    'published_date_extraction_method': date_method,
                    'funding_confidence': float(funding_conf) if funding_conf else None,
                    'funding_extraction_method': funding_method,
                    'needs_review': needs_review,
                }

                # Update date if we found one with good confidence
                current_date = doc.get('published_date')
                if date and date_conf and date_conf >= 0.7:
                    # Check if current date is today (likely wrong)
                    # Convert to string for comparison since DB returns string
                    today_str = datetime.now().strftime('%Y-%m-%d')
                    is_today = str(current_date) == today_str if current_date else False

                    if is_today or not current_date:
                        updates['published_date'] = date.strftime('%Y-%m-%d')
                        stats['dates_improved'] += 1

                    if date_conf >= 0.8:
                        stats['high_confidence_dates'] += 1

                # Update funding if we found one with good confidence
                current_funding = doc.get('funding_amount_extracted')
                if amount and funding_conf and funding_conf >= 0.7:
                    if not current_funding:
                        updates['funding_amount_extracted'] = float(amount)
                        stats['funding_improved'] += 1

                    if funding_conf >= 0.8:
                        stats['high_confidence_funding'] += 1

                # Add Mount Isa LGA code if mentioned
                locations = doc.get('locations_mentioned') or []
                if 'Mount Isa' in locations:
                    updates['lga_code'] = 'LGA35300'

                # Add validation warnings
                if warnings:
                    updates['validation_warnings'] = [w.to_dict() for w in warnings]

                if needs_review:
                    stats['needs_review'] += 1

                # Save to database
                self.supabase.table('documents').update(updates).eq('id', doc['id']).execute()

                stats['processed'] += 1
                if stats['processed'] % 10 == 0:
                    print(f"  Processed {stats['processed']}/{len(documents)}...")

            except Exception as e:
                stats['errors'] += 1
                print(f"  ⚠️  Error processing document {doc.get('id', 'unknown')}: {e}")
                if stats['errors'] <= 3:  # Show first 3 errors in detail
                    import traceback
                    traceback.print_exc()

        # === SUMMARY ===
        print("\n" + "=" * 80)
        print("📊 RE-PROCESSING SUMMARY")
        print("=" * 80)
        print(f"Documents processed: {stats['processed']}")
        print(f"Errors: {stats['errors']}")

        print(f"\n📅 Date Extraction:")
        print(f"  Dates improved: {stats['dates_improved']}")
        print(f"  High confidence (≥0.8): {stats['high_confidence_dates']}")

        print(f"\n💰 Funding Extraction:")
        print(f"  Amounts improved: {stats['funding_improved']}")
        print(f"  High confidence (≥0.8): {stats['high_confidence_funding']}")

        print(f"\n🔍 Quality:")
        print(f"  Documents needing review: {stats['needs_review']}")

        return stats

    def show_enhanced_stats(self):
        """Show enhanced database statistics with confidence scores"""
        print("\n" + "=" * 80)
        print("📊 DATABASE STATISTICS (ENHANCED)")
        print("=" * 80)

        # Use the new view we created
        result = self.supabase.table('document_statistics').select('*').execute()

        if result.data and len(result.data) > 0:
            stats = result.data[0]

            print(f"\nTotal documents: {stats.get('total_documents', 0)}")
            print(f"With funding amounts: {stats.get('documents_with_funding', 0)}")
            print(f"Unique dates: {stats.get('unique_dates', 0)}")

            today_count = stats.get('documents_with_today_date', 0)
            total = stats.get('total_documents', 1)
            if today_count > 0:
                print(f"⚠️  Documents with today's date: {today_count} ({today_count/total*100:.1f}%)")

            # Confidence scores
            date_conf = stats.get('avg_date_confidence')
            funding_conf = stats.get('avg_funding_confidence')

            print(f"\n📊 Average Confidence Scores:")
            if date_conf:
                print(f"  Date extraction: {date_conf:.2f}")
            if funding_conf:
                print(f"  Funding extraction: {funding_conf:.2f}")

            # Documents needing review
            review_count = stats.get('documents_needing_review', 0)
            if review_count > 0:
                print(f"\n🔍 Documents flagged for review: {review_count}")

        # Location stats
        print(f"\n📍 Documents by location (top 10):")
        loc_result = self.supabase.table('location_statistics').select('*').limit(10).execute()

        if loc_result.data:
            for loc in loc_result.data:
                location = loc.get('location', 'Unknown')
                count = loc.get('document_count', 0)
                funding = loc.get('total_funding')

                if funding:
                    print(f"  {location}: {count} docs (${funding:,.0f})")
                else:
                    print(f"  {location}: {count} docs")


def main():
    import argparse

    parser = argparse.ArgumentParser(description='Enhanced data cleaning with confidence scoring')
    parser.add_argument('--reprocess', action='store_true',
                       help='Re-process all documents with confidence scoring (FIXES DATE & FUNDING ISSUES!)')
    parser.add_argument('--stats', action='store_true',
                       help='Show enhanced database statistics')
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🔧 ENHANCED DATA CLEANUP & FIX")
    print("=" * 80)

    cleaner = EnhancedDataCleaner()

    if args.reprocess:
        stats = cleaner.reprocess_with_confidence_scores()

        # Show comparison
        print("\n" + "=" * 80)
        print("📈 BEFORE vs AFTER")
        print("=" * 80)
        print("Before:")
        print("  Dates: 3/56 (6%) - 94% using today's date")
        print("  Funding: 17/56 (30%)")
        print("\nAfter:")
        print(f"  Dates: Improved {stats['dates_improved']} documents")
        print(f"  Funding: Improved {stats['funding_improved']} documents")

    if args.stats or not args.reprocess:
        cleaner.show_enhanced_stats()

    print("\n" + "=" * 80)
    print("✅ COMPLETE")
    print("=" * 80)


if __name__ == '__main__':
    main()
