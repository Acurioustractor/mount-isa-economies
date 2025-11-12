"""
Migrate existing CSV data to Supabase
Reads all your collected data and uploads it to the economic observatory database
"""

import os
import pandas as pd
from pathlib import Path
from supabase import create_client, Client
from tqdm import tqdm
import time

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')  # Use service role for admin access

if not SUPABASE_URL or not SUPABASE_KEY:
    print("❌ Error: Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY environment variables")
    print("\nExample:")
    print("export SUPABASE_URL='https://your-project.supabase.co'")
    print("export SUPABASE_SERVICE_ROLE_KEY='your-service-role-key'")
    exit(1)

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

print("\n" + "="*80)
print("📊 MIGRATING DATA TO SUPABASE")
print("="*80 + "\n")

def clean_numeric(value):
    """Clean numeric values for database insertion"""
    if pd.isna(value):
        return None
    if isinstance(value, str):
        # Remove $ and commas
        value = value.replace('$', '').replace(',', '').strip()
        if value == '' or value == '-':
            return None
    try:
        return float(value)
    except:
        return None

def clean_text(value):
    """Clean text values"""
    if pd.isna(value):
        return None
    return str(value).strip() if value else None

def migrate_contracts():
    """Migrate QLD contracts data"""
    print("📄 Migrating contracts...")

    contracts_dir = DATA_DIR / 'qld_contracts'
    if not contracts_dir.exists():
        print("   No contracts data found")
        return

    csv_files = list(contracts_dir.glob('*.csv'))
    print(f"   Found {len(csv_files)} contract files\n")

    total_inserted = 0

    for csv_file in tqdm(csv_files, desc="   Processing"):
        try:
            df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)

            # Transform to database schema
            records = []
            for _, row in df.iterrows():
                record = {
                    'agency': clean_text(row.get('Agency') or row.get('agency')),
                    'supplier_name': clean_text(row.get('Supplier') or row.get('supplier_name')),
                    'supplier_abn': clean_text(row.get('SupplierABN') or row.get('supplier_abn')),
                    'contract_title': clean_text(row.get('Title') or row.get('contract_title')),
                    'contract_description': clean_text(row.get('Description') or row.get('description')),
                    'value': clean_numeric(row.get('Value') or row.get('value')),
                    'start_date': clean_text(row.get('StartDate') or row.get('start_date')),
                    'end_date': clean_text(row.get('EndDate') or row.get('end_date')),
                    'category': clean_text(row.get('Category') or row.get('category')),
                    'source': 'qld_contracts',
                    'source_file': csv_file.name,
                    'raw_data': row.to_dict()
                }

                # Check Mount Isa relevance
                text_to_search = ' '.join([
                    str(record.get('contract_title', '')),
                    str(record.get('contract_description', '')),
                    str(record.get('supplier_name', ''))
                ]).lower()

                keywords = ['mount isa', 'kalkadoon', '4825', '4823', '4824', '4828']
                record['mount_isa_relevance'] = any(kw in text_to_search for kw in keywords)
                if record['mount_isa_relevance']:
                    record['relevance_keywords'] = [kw for kw in keywords if kw in text_to_search]

                records.append(record)

            # Batch insert (Supabase handles up to 1000 rows per request)
            batch_size = 500
            for i in range(0, len(records), batch_size):
                batch = records[i:i+batch_size]
                supabase.table('contracts').insert(batch).execute()
                total_inserted += len(batch)
                time.sleep(0.1)  # Rate limiting

        except Exception as e:
            print(f"\n   ⚠️  Error processing {csv_file.name}: {e}")

    print(f"\n   ✅ Inserted {total_inserted:,} contracts\n")

def migrate_grants():
    """Migrate grants data"""
    print("💰 Migrating grants...")

    grants_dir = DATA_DIR / 'grants'
    if not grants_dir.exists():
        print("   No grants data found\n")
        return

    csv_files = list(grants_dir.glob('*.csv'))
    total_inserted = 0

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)

            records = []
            for _, row in df.iterrows():
                record = {
                    'title': clean_text(row.get('Title') or row.get('title')),
                    'description': clean_text(row.get('Description') or row.get('description')),
                    'funding_agency': clean_text(row.get('Agency') or row.get('funding_agency')),
                    'amount': clean_numeric(row.get('Amount') or row.get('amount')),
                    'status': clean_text(row.get('Status') or row.get('status', 'awarded')),
                    'source': 'grants_scraper',
                    'source_file': csv_file.name,
                    'raw_data': row.to_dict()
                }

                records.append(record)

            if records:
                supabase.table('grants').insert(records).execute()
                total_inserted += len(records)

        except Exception as e:
            print(f"   ⚠️  Error processing {csv_file.name}: {e}")

    print(f"   ✅ Inserted {total_inserted:,} grants\n")

def migrate_acnc_financials():
    """Migrate ACNC charity financial data"""
    print("💵 Migrating ACNC financials...")

    acnc_dir = DATA_DIR / 'acnc_financials'
    if not acnc_dir.exists():
        print("   No ACNC data found\n")
        return

    csv_files = list(acnc_dir.glob('*.csv'))
    total_orgs = 0
    total_financials = 0

    for csv_file in csv_files:
        try:
            df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)

            # Insert organizations
            org_records = []
            fin_records = []

            for _, row in df.iterrows():
                # Organization
                org = {
                    'name': clean_text(row.get('Charity_Legal_Name') or row.get('Organisation_Name')),
                    'abn': clean_text(row.get('ABN')),
                    'entity_type': 'charity',
                    'postcode': clean_text(row.get('Postcode')),
                    'state': clean_text(row.get('State')),
                    'source': 'acnc',
                    'raw_data': row.to_dict()
                }

                if org['name']:
                    result = supabase.table('organizations').insert(org).execute()
                    if result.data:
                        org_id = result.data[0]['id']
                        total_orgs += 1

                        # Financial record if available
                        revenue = clean_numeric(row.get('Revenue') or row.get('Total_Gross_Income'))
                        if revenue:
                            fin = {
                                'organization_id': org_id,
                                'revenue': revenue,
                                'expenses': clean_numeric(row.get('Expenses') or row.get('Total_Expenses')),
                                'assets': clean_numeric(row.get('Total_Assets')),
                                'employees_fte': clean_numeric(row.get('Employees_FTE')),
                                'volunteers_count': clean_numeric(row.get('Number_Of_Volunteers')),
                                'financial_year': int(row.get('Financial_Year')) if pd.notna(row.get('Financial_Year')) else 2023,
                                'source': 'acnc_ais'
                            }
                            supabase.table('financial_records').insert(fin).execute()
                            total_financials += 1

                time.sleep(0.05)  # Rate limiting

        except Exception as e:
            print(f"   ⚠️  Error processing {csv_file.name}: {e}")

    print(f"   ✅ Inserted {total_orgs:,} organizations, {total_financials:,} financial records\n")

def migrate_services():
    """Migrate existing services from PostgreSQL export"""
    print("🏢 Migrating services...")

    services_file = DATA_DIR / 'services_export.csv'
    if not services_file.exists():
        print("   No services export found\n")
        return

    try:
        df = pd.read_csv(services_file, encoding='utf-8')

        records = []
        for _, row in df.iterrows():
            record = {
                'name': clean_text(row.get('name')),
                'entity_type': clean_text(row.get('type', 'service_provider')),
                'phone': clean_text(row.get('phone')),
                'email': clean_text(row.get('email')),
                'website': clean_text(row.get('website')),
                'address': clean_text(row.get('address')),
                'postcode': '4825',  # Mount Isa default
                'service_types': [clean_text(row.get('category'))] if row.get('category') else [],
                'source': 'manual_export',
                'raw_data': row.to_dict()
            }

            # Set location if coordinates available
            if pd.notna(row.get('latitude')) and pd.notna(row.get('longitude')):
                record['location'] = f"POINT({row['longitude']} {row['latitude']})"

            records.append(record)

        if records:
            supabase.table('organizations').insert(records).execute()
            print(f"   ✅ Inserted {len(records):,} services\n")

    except Exception as e:
        print(f"   ⚠️  Error: {e}\n")

def verify_migration():
    """Verify data was migrated successfully"""
    print("="*80)
    print("✅ VERIFYING MIGRATION")
    print("="*80 + "\n")

    tables = ['organizations', 'contracts', 'grants', 'financial_records']

    for table in tables:
        try:
            result = supabase.table(table).select('id', count='exact').limit(1).execute()
            count = result.count
            print(f"   {table:25} {count:>10,} records")
        except Exception as e:
            print(f"   {table:25} ERROR: {e}")

    print()

# Run migrations
if __name__ == '__main__':
    migrate_services()
    migrate_contracts()
    migrate_grants()
    migrate_acnc_financials()
    verify_migration()

    print("="*80)
    print("✅ MIGRATION COMPLETE")
    print("="*80 + "\n")

    print("Next steps:")
    print("  1. Generate embeddings: python3 scripts/generate_embeddings.py")
    print("  2. Test LLM chat: python3 scripts/chat_with_data.py")
    print("  3. Deploy Edge Functions for automated updates\n")
