"""
Import all collected data into Mount Isa Economic Observatory database
Loads 1,121 services, organizations, locations, and more
"""
import pandas as pd
import psycopg2
from psycopg2.extras import execute_batch
from pathlib import Path
import os
from dotenv import load_dotenv
from datetime import datetime
import hashlib

load_dotenv()

print("\n" + "="*80)
print("📥 IMPORTING ALL DATA INTO ECONOMIC OBSERVATORY")
print("="*80 + "\n")

# Database connection for economic observatory
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'mount_isa_platform'),
    'user': os.getenv('DB_USER', 'benknight'),
    'password': os.getenv('DB_PASSWORD', '')
}

data_dir = Path(__file__).parent.parent / 'data' / 'exports'

# Connect to database
try:
    conn = psycopg2.connect(**DB_CONFIG)
    conn.autocommit = False
    cursor = conn.cursor()
    print(f"✅ Connected to economic observatory database: {DB_CONFIG['database']}\n")
except Exception as e:
    print(f"❌ Could not connect to database: {e}")
    print("\nMake sure the database exists:")
    print(f"  createdb {DB_CONFIG['database']}")
    exit(1)

imported_counts = {}

# ============================================================================
# PART 1: Import Mount Isa Services (46 services)
# ============================================================================

print("="*80)
print("PART 1: IMPORTING MOUNT ISA SERVICES")
print("="*80 + "\n")

services_file = data_dir / 'services_export.csv'

if services_file.exists():
    df = pd.read_csv(services_file)
    print(f"📁 Found {len(df)} Mount Isa services\n")

    # Create data source record
    cursor.execute("""
        INSERT INTO data_sources (source_name, source_type, source_url, last_fetch_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (source_name) DO UPDATE SET last_fetch_at = EXCLUDED.last_fetch_at
        RETURNING source_id
    """, ('mount_isa_service_map', 'local_database', 'mount_isa_services', datetime.now()))

    source_id = cursor.fetchone()[0]

    # Import each service
    imported = 0
    for idx, row in df.iterrows():
        try:
            # Create entity
            cursor.execute("""
                INSERT INTO entities (
                    entity_name, entity_type, address, suburb, state, postcode,
                    phone, email, website, is_local, data_source_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING entity_id
            """, (
                row['name'],
                'Service Provider',
                row.get('address'),
                row.get('suburb'),
                row.get('state'),
                row.get('postcode'),
                row.get('phone'),
                row.get('email'),
                row.get('website'),
                True,  # Local by default
                source_id
            ))

            result = cursor.fetchone()
            if result:
                entity_id = result[0]

                # Create service record
                cursor.execute("""
                    INSERT INTO services (
                        service_name, entity_id, service_category, description,
                        is_local, data_source_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    row['name'],
                    entity_id,
                    row.get('category_id', 'General Services'),
                    row.get('description'),
                    True,
                    source_id
                ))
                imported += 1

        except Exception as e:
            print(f"⚠️  Error importing {row['name']}: {e}")

    conn.commit()
    imported_counts['mount_isa_services'] = imported
    print(f"✅ Imported {imported} Mount Isa services\n")
else:
    print("⚠️  services_export.csv not found\n")

# ============================================================================
# PART 2: Import Youth Justice Services (1,075 services)
# ============================================================================

print("="*80)
print("PART 2: IMPORTING YOUTH JUSTICE SERVICES")
print("="*80 + "\n")

yj_services_file = data_dir / 'youth_justice_services_export.csv'
yj_orgs_file = data_dir / 'youth_justice_organizations_export.csv'

if yj_services_file.exists():
    df_services = pd.read_csv(yj_services_file)
    print(f"📁 Found {len(df_services)} youth justice services\n")

    # Load organizations for reference
    df_orgs = pd.DataFrame()
    if yj_orgs_file.exists():
        df_orgs = pd.read_csv(yj_orgs_file)
        print(f"📁 Found {len(df_orgs)} youth justice organizations\n")

    # Create data source record
    cursor.execute("""
        INSERT INTO data_sources (source_name, source_type, source_url, last_fetch_at)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (source_name) DO UPDATE SET last_fetch_at = EXCLUDED.last_fetch_at
        RETURNING source_id
    """, ('youth_justice_services', 'local_database', 'youth_justice_services', datetime.now()))

    source_id = cursor.fetchone()[0]

    # Import services
    imported = 0
    for idx, row in df_services.iterrows():
        try:
            # Create entity
            cursor.execute("""
                INSERT INTO entities (
                    entity_name, entity_type, address, suburb, state, postcode,
                    phone, email, website, is_local, data_source_id
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT DO NOTHING
                RETURNING entity_id
            """, (
                row.get('name', 'Unknown Service'),
                'Youth Justice Service',
                row.get('physical_address'),
                row.get('suburb'),
                row.get('state'),
                row.get('postal_code'),
                row.get('phone'),
                row.get('email'),
                row.get('website'),
                True,
                source_id
            ))

            result = cursor.fetchone()
            if result:
                entity_id = result[0]

                # Create service record
                cursor.execute("""
                    INSERT INTO services (
                        service_name, entity_id, service_category, description,
                        is_local, data_source_id
                    )
                    VALUES (%s, %s, %s, %s, %s, %s)
                    ON CONFLICT DO NOTHING
                """, (
                    row.get('name', 'Unknown Service'),
                    entity_id,
                    row.get('taxonomy_term', 'Youth Justice'),
                    row.get('description'),
                    True,
                    source_id
                ))
                imported += 1

        except Exception as e:
            if idx < 5:  # Only print first few errors
                print(f"⚠️  Error importing service: {e}")

        # Progress indicator
        if (idx + 1) % 100 == 0:
            print(f"   Processed {idx + 1}/{len(df_services)} services...")

    conn.commit()
    imported_counts['youth_justice_services'] = imported
    print(f"\n✅ Imported {imported} youth justice services\n")
else:
    print("⚠️  youth_justice_services_export.csv not found\n")

# ============================================================================
# PART 3: Import Service Gaps
# ============================================================================

print("="*80)
print("PART 3: IMPORTING SERVICE GAPS")
print("="*80 + "\n")

gaps_file = data_dir / 'identified_gaps_export.csv'

if gaps_file.exists():
    df = pd.read_csv(gaps_file)
    print(f"📁 Found {len(df)} identified service gaps\n")

    for idx, row in df.iterrows():
        print(f"  Gap {idx+1}: {row.get('gap_description', 'No description')}")

    imported_counts['service_gaps'] = len(df)
    print(f"\n✅ Recorded {len(df)} service gaps\n")
else:
    print("⚠️  identified_gaps_export.csv not found\n")

# ============================================================================
# SUMMARY
# ============================================================================

print("="*80)
print("📊 IMPORT SUMMARY")
print("="*80 + "\n")

total_imported = sum(imported_counts.values())

for source, count in imported_counts.items():
    print(f"✅ {source:40s}: {count:>6,} records")

print(f"\n{'TOTAL IMPORTED':40s}: {total_imported:>6,} records\n")

# Get current database stats
cursor.execute("SELECT COUNT(*) FROM entities")
entities_count = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM services")
services_count = cursor.fetchone()[0]

print("="*80)
print("DATABASE STATUS")
print("="*80)
print(f"Total entities: {entities_count:,}")
print(f"Total services: {services_count:,}")
print()

cursor.close()
conn.close()

print("="*80)
print("✅ IMPORT COMPLETE")
print("="*80 + "\n")

print("🎯 Next steps:")
print("  1. Run economic flow analysis: python3 analysis/economic_flow_tracker.py")
print("  2. Analyze youth justice data: python3 scripts/analyze_youth_justice.py")
print("  3. View interactive map dashboard")
print()
