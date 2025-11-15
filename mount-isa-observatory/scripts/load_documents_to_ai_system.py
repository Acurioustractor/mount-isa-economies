"""
LOAD DOCUMENTS TO AI-POWERED SYSTEM

Loads scraped media statements into the AI-powered document system with:
1. Document ingestion
2. Entity extraction
3. Auto-queuing for chunking and AI analysis
4. Deduplication

Usage:
    python scripts/load_documents_to_ai_system.py --csv data/media_statements/firecrawl_scraped_results.csv
    python scripts/load_documents_to_ai_system.py --csv data/media_statements/firecrawl_scraped_results.csv --analyze-now
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime
import pandas as pd
import re
from dotenv import load_dotenv
from supabase import create_client, Client

load_dotenv()


class DocumentLoader:
    """Load documents into AI system"""

    def __init__(self):
        """Initialize Supabase client"""
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not self.supabase_url or not self.supabase_key:
            print("\n❌ Missing Supabase credentials in .env")
            print("   Required: SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY")
            sys.exit(1)

        self.supabase: Client = create_client(self.supabase_url, self.supabase_key)
        print("✅ Connected to Supabase")

    def extract_entities(self, text: str, title: str) -> Dict:
        """Extract entities from text using regex patterns"""

        # Extract funding amounts
        funding_amounts = []
        amount_patterns = re.findall(r'\$\s*(\d+(?:\.\d+)?)\s*(million|billion|M|B)', text, re.IGNORECASE)
        for amount, unit in amount_patterns:
            normalized_amount = float(amount)
            if unit.lower() in ['billion', 'b']:
                normalized_amount *= 1000  # Convert to millions
            funding_amounts.append({
                'amount': normalized_amount,
                'unit': 'million',
                'original_text': f'${amount}{unit}'
            })

        # Primary funding amount (first mentioned)
        funding_amount_extracted = funding_amounts[0]['amount'] if funding_amounts else None

        # Extract program keywords
        programs = []
        program_keywords = [
            'on-country', 'on country', 'co-responder', 'youth justice',
            'diversion', 'detention', 'rehabilitation', 'early intervention',
            'staying on track', 'regional reset', 'kickstarter', 'circuit breaker',
            'crime prevention school', 'youth justice school', 'pcyc'
        ]
        text_lower = text.lower()
        title_lower = title.lower()
        for keyword in program_keywords:
            if keyword in text_lower or keyword in title_lower:
                programs.append(keyword.title())

        # Extract locations
        locations = []
        location_keywords = [
            'Mount Isa', 'Townsville', 'Cairns', 'Brisbane', 'Gold Coast',
            'Ipswich', 'Logan', 'Rockhampton', 'Doomadgee', 'Palm Island',
            'Mornington Island', 'Yarrabah', 'Aurukun', 'Moreton Bay',
            'Darling Downs', 'South Burnett', 'Far North Queensland',
            'Central Queensland', 'South West Queensland', 'North Queensland',
            'Cape York', 'Torres Strait'
        ]
        for location in location_keywords:
            if location.lower() in text_lower or location.lower() in title_lower:
                locations.append(location)

        # Extract organizations
        organizations = []
        org_patterns = [
            r'((?:[A-Z][a-z]+ )+(?:Corporation|Foundation|Services|Company|Centre|Inc|Ltd))',
            r'(PCYC)',
            r'(Kokoda Youth Foundation)',
            r'(Life Without Barriers)',
            r'(Ohana for Youth)',
            r'(Men of Business)',
            r'(54 Reasons)',
            r'(Queensland Police)',
        ]
        for pattern in org_patterns:
            matches = re.findall(pattern, text)
            organizations.extend(matches)

        # Extract people (ministers, officials)
        people = []
        minister_pattern = r'((?:Minister|Hon|Premier|MP)\s+[A-Z][a-z]+\s+[A-Z][a-z]+)'
        minister_matches = re.findall(minister_pattern, text)
        for match in minister_matches:
            people.append({
                'name': match,
                'role': 'Minister' if 'Minister' in match else 'Official'
            })

        # Categorize document
        categories = []
        if any(k in text_lower for k in ['early intervention', 'prevention', 'diversion']):
            categories.append('early_intervention')
        if any(k in text_lower for k in ['detention', 'remand', 'youth justice centre']):
            categories.append('detention')
        if any(k in text_lower for k in ['rehabilitation', 'staying on track', 'post-detention']):
            categories.append('rehabilitation')
        if any(k in text_lower for k in ['on-country', 'on country', 'culturally', 'indigenous']):
            categories.append('on_country')
        if 'mount isa' in text_lower or 'mount isa' in title_lower:
            categories.append('mount_isa')

        # Generate keywords
        keywords = list(set(programs + locations[:3] + categories))

        return {
            'funding_amount_extracted': funding_amount_extracted,
            'funding_amounts_all': funding_amounts,
            'programs_mentioned': list(set(programs)),
            'locations_mentioned': list(set(locations)),
            'organizations_mentioned': list(set(organizations)),
            'people_mentioned': people,
            'categories': categories,
            'keywords': keywords
        }

    def load_csv(self, csv_path: str) -> pd.DataFrame:
        """Load and validate CSV"""
        if not Path(csv_path).exists():
            print(f"\n❌ File not found: {csv_path}")
            sys.exit(1)

        df = pd.read_csv(csv_path)
        print(f"\n✅ Loaded {len(df)} rows from CSV")

        # Validate columns
        required_cols = ['url', 'title', 'date']
        missing = [col for col in required_cols if col not in df.columns]
        if missing:
            print(f"\n❌ Missing required columns: {missing}")
            print(f"   Found columns: {df.columns.tolist()}")
            sys.exit(1)

        return df

    def prepare_document(self, row: pd.Series) -> Dict:
        """Prepare document for insertion"""

        # Parse date
        try:
            published_date = pd.to_datetime(row['date']).strftime('%Y-%m-%d')
        except:
            published_date = datetime.now().strftime('%Y-%m-%d')

        # Extract statement ID from URL
        statement_id = None
        if 'statements/' in row['url']:
            statement_id = row['url'].split('statements/')[-1].split('/')[0]

        # Full text (combine title and description)
        full_text = row.get('description', '') or ''
        if pd.isna(full_text):
            full_text = row['title']

        # Extract entities
        entities = self.extract_entities(full_text, row['title'])

        # Build document
        doc = {
            'url': row['url'],
            'statement_id': statement_id,
            'title': row['title'],
            'published_date': published_date,
            'scraped_date': datetime.now().isoformat(),

            'source_type': 'media_statement',
            'source_organization': 'Queensland Government',
            'minister_name': row.get('minister', 'Queensland Government'),

            'full_text': full_text,
            'markdown_text': None,
            'summary': None,  # Will be generated by AI

            **entities,

            'ai_analysis_status': 'pending',
            'embedding_status': 'pending',
            'created_by': 'firecrawl_scraper'
        }

        return doc

    def load_documents(self, df: pd.DataFrame, queue_for_processing: bool = True) -> Dict:
        """Load documents to Supabase"""

        print("\n" + "=" * 80)
        print("📥 LOADING DOCUMENTS TO AI SYSTEM")
        print("=" * 80)

        inserted = 0
        updated = 0
        skipped = 0
        errors = []

        for idx, row in df.iterrows():
            try:
                doc = self.prepare_document(row)

                # Try to insert
                result = self.supabase.table('documents').upsert(
                    doc,
                    on_conflict='url'
                ).execute()

                if result.data:
                    # Check if it was insert or update
                    existing = self.supabase.table('documents').select('id').eq('url', doc['url']).execute()
                    if existing.data and len(existing.data) == 1:
                        doc_id = existing.data[0]['id']

                        # Queue for processing if requested
                        if queue_for_processing:
                            self.queue_document(doc_id)

                        inserted += 1
                        if (inserted + updated) % 10 == 0:
                            print(f"  Processed {inserted + updated}/{len(df)}...")
                    else:
                        updated += 1
                else:
                    skipped += 1

            except Exception as e:
                errors.append({'row': idx, 'error': str(e), 'url': row.get('url', 'unknown')})
                print(f"\n  ❌ Error on row {idx}: {e}")

        print(f"\n✅ Loading complete:")
        print(f"   Inserted: {inserted}")
        print(f"   Updated: {updated}")
        print(f"   Skipped: {skipped}")
        print(f"   Errors: {len(errors)}")

        if errors:
            print(f"\n⚠️  Errors encountered:")
            for err in errors[:5]:
                print(f"   Row {err['row']}: {err['error']}")

        return {
            'inserted': inserted,
            'updated': updated,
            'skipped': skipped,
            'errors': errors
        }

    def queue_document(self, document_id: str):
        """Queue document for AI processing"""
        stages = ['chunking', 'embedding', 'ai_analysis', 'story_generation']

        for stage in stages:
            try:
                self.supabase.table('processing_queue').upsert({
                    'document_id': document_id,
                    'stage': stage,
                    'status': 'pending',
                    'priority': 5
                }, on_conflict='document_id,stage').execute()
            except:
                pass  # Already queued

    def run_immediate_analysis(self, document_ids: List[str]):
        """Trigger immediate analysis for documents"""
        print("\n" + "=" * 80)
        print("🤖 STARTING AI ANALYSIS")
        print("=" * 80)
        print("\n⚠️  This feature requires the AI processing pipeline to be running")
        print("   Run: python scripts/ai_processing_pipeline.py")
        print(f"\n   {len(document_ids)} documents queued for analysis")


def main():
    """Main execution"""
    parser = argparse.ArgumentParser(description='Load documents to AI system')
    parser.add_argument('--csv', required=True, help='Path to CSV file')
    parser.add_argument('--analyze-now', action='store_true', help='Start AI analysis immediately')
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🚀 DOCUMENT LOADER - AI SYSTEM")
    print("=" * 80)

    loader = DocumentLoader()

    # Load CSV
    df = loader.load_csv(args.csv)

    # Load to database
    results = loader.load_documents(df, queue_for_processing=True)

    # Show summary
    print("\n" + "=" * 80)
    print("📊 SUMMARY")
    print("=" * 80)
    print(f"\n✅ {results['inserted']} documents loaded")
    print(f"✅ {results['inserted']} documents queued for AI processing")

    print("\n" + "=" * 80)
    print("📋 NEXT STEPS")
    print("=" * 80)
    print("\n1. View documents in Supabase:")
    print("   SELECT * FROM documents ORDER BY published_date DESC;")
    print("\n2. Check processing queue:")
    print("   SELECT * FROM v_processing_status;")
    print("\n3. Run AI processing pipeline:")
    print("   python scripts/ai_processing_pipeline.py")
    print("\n4. Generate stories:")
    print("   python scripts/generate_stories.py")

    if args.analyze_now:
        # Get all document IDs
        all_docs = loader.supabase.table('documents').select('id').execute()
        doc_ids = [doc['id'] for doc in all_docs.data]
        loader.run_immediate_analysis(doc_ids)


if __name__ == '__main__':
    main()
