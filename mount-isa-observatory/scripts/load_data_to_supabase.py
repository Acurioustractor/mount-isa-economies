"""
Load Mount Isa funding data into Supabase

This script loads data from CSV files into the Supabase database following
the schema defined in database/supabase_schema.sql.

It handles:
- Media statements (funding announcements)
- Contracts (actual payments)
- Organization data
- Program categorization
- Data normalization and relationship management

Setup:
1. Run database/supabase_schema.sql in Supabase SQL editor first
2. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env
3. Run: python scripts/load_data_to_supabase.py

Usage:
    python scripts/load_data_to_supabase.py
    python scripts/load_data_to_supabase.py --dry-run  # Preview without loading
"""

import os
import sys
import pandas as pd
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from dotenv import load_dotenv

# Load environment
load_dotenv()

# Supabase imports
try:
    from supabase import create_client, Client
except ImportError:
    print("❌ Supabase not installed. Run: pip install supabase")
    sys.exit(1)


class SupabaseDataLoader:
    """Load Mount Isa economic data into Supabase"""

    def __init__(self, dry_run: bool = False):
        """
        Initialize Supabase connection

        Args:
            dry_run: If True, preview data without loading
        """
        self.dry_run = dry_run

        # Get credentials
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError(
                "❌ SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set in .env\n"
                "   Get from: https://app.supabase.com/project/_/settings/api"
            )

        # Initialize client
        self.supabase: Client = create_client(supabase_url, supabase_key)
        print(f"✅ Connected to Supabase: {supabase_url}")

        if dry_run:
            print("🔍 DRY RUN MODE - No data will be written")

        # Cache for entity IDs (avoid duplicate lookups/inserts)
        self.location_cache: Dict[str, str] = {}
        self.org_cache: Dict[str, str] = {}
        self.program_cache: Dict[str, str] = {}
        self.document_cache: Dict[str, str] = {}

    def get_or_create_location(self, location_name: str, state: str = 'QLD') -> Optional[str]:
        """
        Get or create a location, return UUID

        Args:
            location_name: Location name
            state: State abbreviation

        Returns:
            Location UUID
        """
        cache_key = f"{location_name}_{state}"

        if cache_key in self.location_cache:
            return self.location_cache[cache_key]

        # Check if exists
        result = self.supabase.table('locations').select('id').eq('name', location_name).eq('state', state).execute()

        if result.data and len(result.data) > 0:
            location_id = result.data[0]['id']
            self.location_cache[cache_key] = location_id
            return location_id

        # Create new
        if self.dry_run:
            print(f"  [DRY RUN] Would create location: {location_name}, {state}")
            return None

        new_location = {
            'name': location_name,
            'state': state
        }

        result = self.supabase.table('locations').insert(new_location).execute()

        if result.data and len(result.data) > 0:
            location_id = result.data[0]['id']
            self.location_cache[cache_key] = location_id
            print(f"  ✅ Created location: {location_name}")
            return location_id

        return None

    def get_or_create_organization(
        self,
        org_name: str,
        org_type: str = 'Unknown',
        sector: Optional[str] = None,
        abn: Optional[str] = None
    ) -> Optional[str]:
        """
        Get or create an organization, return UUID

        Args:
            org_name: Organization name
            org_type: Organization type
            sector: Sector
            abn: ABN

        Returns:
            Organization UUID
        """
        if org_name in self.org_cache:
            return self.org_cache[org_name]

        # Check if exists (by name or ABN)
        if abn:
            result = self.supabase.table('organizations').select('id').eq('abn', abn).execute()
        else:
            result = self.supabase.table('organizations').select('id').eq('name', org_name).execute()

        if result.data and len(result.data) > 0:
            org_id = result.data[0]['id']
            self.org_cache[org_name] = org_id
            return org_id

        # Create new
        if self.dry_run:
            print(f"  [DRY RUN] Would create organization: {org_name} ({org_type})")
            return None

        new_org = {
            'name': org_name,
            'organization_type': org_type,
        }

        if sector:
            new_org['sector'] = sector
        if abn:
            new_org['abn'] = abn

        # Detect indigenous organizations
        indigenous_keywords = ['Indigenous', 'Aboriginal', 'Torres Strait', 'Mithangkaya']
        if any(keyword.lower() in org_name.lower() for keyword in indigenous_keywords):
            new_org['indigenous_controlled'] = True

        result = self.supabase.table('organizations').insert(new_org).execute()

        if result.data and len(result.data) > 0:
            org_id = result.data[0]['id']
            self.org_cache[org_name] = org_id
            print(f"  ✅ Created organization: {org_name}")
            return org_id

        return None

    def get_or_create_program(
        self,
        program_name: str,
        program_type: str,
        sector: str = 'Youth Justice'
    ) -> Optional[str]:
        """
        Get or create a program, return UUID

        Args:
            program_name: Program name
            program_type: Program type
            sector: Sector

        Returns:
            Program UUID
        """
        if program_name in self.program_cache:
            return self.program_cache[program_name]

        # Check if exists
        result = self.supabase.table('programs').select('id').eq('name', program_name).execute()

        if result.data and len(result.data) > 0:
            program_id = result.data[0]['id']
            self.program_cache[program_name] = program_id
            return program_id

        # Create new
        if self.dry_run:
            print(f"  [DRY RUN] Would create program: {program_name} ({program_type})")
            return None

        new_program = {
            'name': program_name,
            'program_type': program_type,
            'sector': sector,
            'status': 'active'
        }

        result = self.supabase.table('programs').insert(new_program).execute()

        if result.data and len(result.data) > 0:
            program_id = result.data[0]['id']
            self.program_cache[program_name] = program_id
            print(f"  ✅ Created program: {program_name}")
            return program_id

        return None

    def get_or_create_document(
        self,
        doc_type: str,
        title: str,
        source_url: Optional[str] = None,
        identifier: Optional[str] = None,
        publication_date: Optional[str] = None
    ) -> Optional[str]:
        """
        Get or create a document, return UUID

        Args:
            doc_type: Document type
            title: Document title
            source_url: Source URL
            identifier: Document identifier
            publication_date: Publication date

        Returns:
            Document UUID
        """
        cache_key = f"{doc_type}_{identifier}" if identifier else f"{doc_type}_{title}"

        if cache_key in self.document_cache:
            return self.document_cache[cache_key]

        # Check if exists
        if identifier:
            result = self.supabase.table('documents').select('id').eq('document_type', doc_type).eq('document_identifier', identifier).execute()
        else:
            result = self.supabase.table('documents').select('id').eq('document_type', doc_type).eq('title', title).execute()

        if result.data and len(result.data) > 0:
            doc_id = result.data[0]['id']
            self.document_cache[cache_key] = doc_id
            return doc_id

        # Create new
        if self.dry_run:
            print(f"  [DRY RUN] Would create document: {title}")
            return None

        new_doc = {
            'document_type': doc_type,
            'title': title,
        }

        if source_url:
            new_doc['source_url'] = source_url
        if identifier:
            new_doc['document_identifier'] = identifier
        if publication_date:
            new_doc['publication_date'] = publication_date

        result = self.supabase.table('documents').insert(new_doc).execute()

        if result.data and len(result.data) > 0:
            doc_id = result.data[0]['id']
            self.document_cache[cache_key] = doc_id
            print(f"  ✅ Created document: {title}")
            return doc_id

        return None

    def parse_funding_amount(self, amount_str: str) -> Optional[float]:
        """
        Parse funding amount from string

        Args:
            amount_str: Amount string (e.g., "$24000000", "$24M")

        Returns:
            Amount as float
        """
        if pd.isna(amount_str) or amount_str == 'N/A' or not amount_str:
            return None

        # Remove $, commas, spaces
        amount_str = str(amount_str).replace('$', '').replace(',', '').strip()

        # Handle million/billion
        if 'M' in amount_str.upper() or 'million' in amount_str.lower():
            amount_str = amount_str.upper().replace('M', '').replace('ILLION', '').strip()
            return float(amount_str) * 1_000_000
        elif 'B' in amount_str.upper() or 'billion' in amount_str.lower():
            amount_str = amount_str.upper().replace('B', '').replace('ILLION', '').strip()
            return float(amount_str) * 1_000_000_000

        try:
            return float(amount_str)
        except ValueError:
            return None

    def classify_program_type(self, program_name: str) -> str:
        """
        Classify program type from name

        Args:
            program_name: Program name

        Returns:
            Program type
        """
        program_name_lower = program_name.lower()

        if 'on-country' in program_name_lower or 'on country' in program_name_lower:
            return 'On-Country'
        elif 'co-responder' in program_name_lower:
            return 'Co-Responder'
        elif 'stronger communities' in program_name_lower:
            return 'Community Partnership'
        elif 'diversionary' in program_name_lower or 'diversion' in program_name_lower:
            return 'Diversionary'
        elif 'grant' in program_name_lower:
            return 'Grant Program'
        elif 'budget' in program_name_lower:
            return 'Budget Allocation'
        else:
            return 'Other'

    def load_media_statements(self, csv_path: str):
        """
        Load media statements as funding announcements

        Args:
            csv_path: Path to media statements CSV
        """
        print("\n" + "=" * 80)
        print("📰 LOADING MEDIA STATEMENTS")
        print("=" * 80)

        df = pd.read_csv(csv_path)
        print(f"Found {len(df)} statements to load")

        # Get Queensland Government org (funding body)
        qld_gov_id = self.get_or_create_organization(
            'Queensland Government',
            'Government',
            'Government'
        )

        loaded_count = 0
        skipped_count = 0

        for idx, row in df.iterrows():
            statement_id = row['statement_id']
            print(f"\nProcessing statement {statement_id}: {row['title'][:60]}...")

            # Parse amount
            amount = self.parse_funding_amount(row['funding_amount'])
            if not amount:
                print(f"  ⚠️  Skipping - no valid funding amount")
                skipped_count += 1
                continue

            # Create document
            doc_id = self.get_or_create_document(
                doc_type='Media Statement',
                title=row['title'],
                source_url=row['url'],
                identifier=str(statement_id),
                publication_date=row['date'] if pd.notna(row['date']) else None
            )

            # Create/get program
            program_name = row['program_name'] if pd.notna(row['program_name']) else row['title']
            program_type = self.classify_program_type(program_name)

            program_id = self.get_or_create_program(
                program_name=program_name,
                program_type=program_type,
                sector='Youth Justice'
            )

            # Create/get recipient organization
            recipient_id = None
            if pd.notna(row['recipient_organization']) and row['recipient_organization']:
                recipient_name = row['recipient_organization']
                # Clean up recipient name if it has amounts in it
                if '$' in recipient_name:
                    recipient_name = recipient_name.split('$')[0].strip().rstrip(',')

                recipient_id = self.get_or_create_organization(
                    org_name=recipient_name,
                    org_type='NGO',
                    sector='Youth Justice'
                )

            # Create funding announcement
            if self.dry_run:
                print(f"  [DRY RUN] Would create funding announcement: ${amount:,.0f}")
                loaded_count += 1
                continue

            # Check if already exists
            existing = self.supabase.table('funding_announcements') \
                .select('id') \
                .eq('source_document_id', doc_id) \
                .execute()

            if existing.data and len(existing.data) > 0:
                print(f"  ⚠️  Already exists - skipping")
                skipped_count += 1
                continue

            # Determine if Mount Isa specific
            is_mount_isa_specific = 'mount isa' in row['title'].lower()

            announcement = {
                'program_id': program_id,
                'recipient_org_id': recipient_id,
                'funding_body_id': qld_gov_id,
                'amount_announced': amount,
                'announcement_date': row['date'],
                'funding_period_description': row['funding_period'] if pd.notna(row['funding_period']) else None,
                'announced_by': row['minister'] if pd.notna(row['minister']) else None,
                'source_document_id': doc_id,
                'is_mount_isa_specific': is_mount_isa_specific,
                'confidence_score': 3,  # Media statements = confidence 3
                'verification_status': 'unverified',
                'announcement_context': row['description'] if pd.notna(row['description']) else None
            }

            try:
                result = self.supabase.table('funding_announcements').insert(announcement).execute()
                if result.data:
                    print(f"  ✅ Loaded: ${amount:,.0f} for {program_name[:50]}")
                    loaded_count += 1
                else:
                    print(f"  ❌ Failed to load")
                    skipped_count += 1
            except Exception as e:
                print(f"  ❌ Error: {e}")
                skipped_count += 1

        print("\n" + "=" * 80)
        print(f"✅ Loaded {loaded_count} statements")
        print(f"⚠️  Skipped {skipped_count} statements")
        print("=" * 80)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Load Mount Isa data into Supabase')
    parser.add_argument('--dry-run', action='store_true', help='Preview without loading')
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🚀 MOUNT ISA ECONOMIC OBSERVATORY - DATA LOADER")
    print("=" * 80)

    try:
        # Initialize loader
        loader = SupabaseDataLoader(dry_run=args.dry_run)

        # Data directory
        data_dir = Path(__file__).parent.parent / 'data'

        # Load media statements
        media_statements_path = data_dir / 'media_statements' / 'mount_isa_statements_recovered.csv'
        if media_statements_path.exists():
            loader.load_media_statements(str(media_statements_path))
        else:
            print(f"⚠️  Media statements not found: {media_statements_path}")

        # TODO: Add more data loaders
        # - load_contracts()
        # - load_budget_data()
        # - load_outcomes()

        print("\n" + "=" * 80)
        print("✅ DATA LOADING COMPLETE")
        print("=" * 80)

        if not args.dry_run:
            print("\nNext steps:")
            print("  1. Verify data in Supabase dashboard")
            print("  2. Run visualizations: python scripts/visualize_funding_flows.py")
            print("  3. Check data quality: SELECT * FROM v_funding_flow;")

    except ValueError as e:
        print(f"\n❌ {e}")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
