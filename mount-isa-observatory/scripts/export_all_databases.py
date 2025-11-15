"""
Export ALL data from existing Mount Isa databases
Extracts services, interviews, gaps, locations from mount_isa_services
Also checks youth_justice_services database
"""
import psycopg2
import pandas as pd
from pathlib import Path
import sys

print("\n" + "="*80)
print("📤 EXPORTING ALL DATA FROM MOUNT ISA DATABASES")
print("="*80 + "\n")

# Database credentials
DB_USER = 'benknight'
DB_HOST = 'localhost'
DB_PORT = '5432'

output_dir = Path(__file__).parent.parent / 'data' / 'exports'
output_dir.mkdir(parents=True, exist_ok=True)

exported_data = {}

# ============================================================================
# DATABASE 1: mount_isa_services
# ============================================================================

print("="*80)
print("DATABASE 1: mount_isa_services")
print("="*80 + "\n")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database='mount_isa_services',
        user=DB_USER,
        password=''
    )

    print("✅ Connected to mount_isa_services\n")

    # Export tables
    tables_to_export = [
        'services',
        'community_interviews',
        'identified_gaps',
        'locations',
        'service_categories',
        'service_contacts',
        'interview_participants',
        'interview_themes',
        'data_sources'
    ]

    for table in tables_to_export:
        try:
            df = pd.read_sql(f"SELECT * FROM {table}", conn)
            output_file = output_dir / f'{table}_export.csv'
            df.to_csv(output_file, index=False)
            exported_data[f'mount_isa_services.{table}'] = len(df)
            print(f"✅ {table}: {len(df)} records → {output_file.name}")
        except Exception as e:
            print(f"⚠️  {table}: Could not export ({e})")

    conn.close()
    print()

except Exception as e:
    print(f"❌ Could not connect to mount_isa_services: {e}\n")

# ============================================================================
# DATABASE 2: youth_justice_services
# ============================================================================

print("="*80)
print("DATABASE 2: youth_justice_services")
print("="*80 + "\n")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database='youth_justice_services',
        user=DB_USER,
        password=''
    )

    print("✅ Connected to youth_justice_services\n")

    # First, see what tables exist
    tables_query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """
    tables = pd.read_sql(tables_query, conn)

    if len(tables) > 0:
        print("Available tables:")
        for table in tables['table_name']:
            print(f"   • {table}")
        print()

        # Export all tables
        for table_name in tables['table_name']:
            try:
                df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                output_file = output_dir / f'youth_justice_{table_name}_export.csv'
                df.to_csv(output_file, index=False)
                exported_data[f'youth_justice_services.{table_name}'] = len(df)
                print(f"✅ {table_name}: {len(df)} records → {output_file.name}")
            except Exception as e:
                print(f"⚠️  {table_name}: Could not export ({e})")
    else:
        print("⚠️  No tables found in youth_justice_services database")

    conn.close()
    print()

except Exception as e:
    print(f"❌ Could not connect to youth_justice_services: {e}\n")

# ============================================================================
# DATABASE 3: mount_isa_platform (if different from above)
# ============================================================================

print("="*80)
print("DATABASE 3: mount_isa_platform")
print("="*80 + "\n")

try:
    conn = psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        database='mount_isa_platform',
        user=DB_USER,
        password=''
    )

    print("✅ Connected to mount_isa_platform\n")

    # See what tables exist
    tables_query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """
    tables = pd.read_sql(tables_query, conn)

    if len(tables) > 0:
        print("Available tables:")
        for table in tables['table_name']:
            print(f"   • {table}")
        print()

        # Export all tables
        for table_name in tables['table_name']:
            try:
                df = pd.read_sql(f"SELECT * FROM {table_name}", conn)
                output_file = output_dir / f'platform_{table_name}_export.csv'
                df.to_csv(output_file, index=False)
                exported_data[f'mount_isa_platform.{table_name}'] = len(df)
                print(f"✅ {table_name}: {len(df)} records → {output_file.name}")
            except Exception as e:
                print(f"⚠️  {table_name}: Could not export ({e})")
    else:
        print("⚠️  No tables found in mount_isa_platform database")

    conn.close()
    print()

except Exception as e:
    print(f"❌ Could not connect to mount_isa_platform: {e}\n")

# ============================================================================
# SUMMARY
# ============================================================================

print("="*80)
print("📊 EXPORT SUMMARY")
print("="*80 + "\n")

if exported_data:
    total_records = 0

    for source, count in sorted(exported_data.items()):
        print(f"✅ {source:50s}: {count:>6,} records")
        total_records += count

    print(f"\n{'TOTAL RECORDS EXPORTED':50s}: {total_records:>6,}")
    print(f"\n📁 All files saved to: {output_dir}\n")

    # Key highlights
    print("="*80)
    print("🎯 KEY DATA AVAILABLE")
    print("="*80 + "\n")

    if 'mount_isa_services.services' in exported_data:
        print(f"✅ Services: {exported_data['mount_isa_services.services']} services mapped")

    if 'mount_isa_services.community_interviews' in exported_data:
        interviews_count = exported_data['mount_isa_services.community_interviews']
        if interviews_count > 0:
            print(f"✅ Community Interviews: {interviews_count} interviews recorded")

    if 'mount_isa_services.identified_gaps' in exported_data:
        gaps_count = exported_data['mount_isa_services.identified_gaps']
        if gaps_count > 0:
            print(f"✅ Service Gaps: {gaps_count} gaps identified")

    if 'mount_isa_services.locations' in exported_data:
        locations_count = exported_data['mount_isa_services.locations']
        if locations_count > 0:
            print(f"✅ Locations: {locations_count} locations mapped")

    print()

else:
    print("⚠️  No data exported. Check database connections.\n")

print("="*80)
print("✅ EXPORT COMPLETE")
print("="*80 + "\n")

print("🎯 Next steps:")
print("1. Run scrapers: python3 scripts/scrape_acnc_charities.py")
print("2. Run scrapers: python3 scripts/scrape_grantconnect.py")
print("3. Build v1: python3 scripts/build_v1.py")
print()
