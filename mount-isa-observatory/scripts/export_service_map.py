"""
Export services from existing mount-isa-service-map PostgreSQL database
Connects to your current service map DB and exports to CSV for import
"""
import psycopg2
import pandas as pd
import os
from pathlib import Path

print("\n" + "="*80)
print("📤 EXPORTING SERVICES FROM SERVICE MAP DATABASE")
print("="*80 + "\n")

# You'll need to provide your service map database credentials
# Default PostgreSQL connection for service map
SERVICE_MAP_DB = {
    'host': input("Service map database host (default: localhost): ").strip() or 'localhost',
    'port': input("Service map database port (default: 5432): ").strip() or '5432',
    'database': input("Service map database name: ").strip(),
    'user': input("Service map database user (default: postgres): ").strip() or 'postgres',
    'password': input("Service map database password: ").strip()
}

try:
    # Connect to service map database
    conn = psycopg2.connect(**SERVICE_MAP_DB)
    print(f"✅ Connected to service map database: {SERVICE_MAP_DB['database']}\n")

    # First, let's see what tables exist
    query = """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """
    tables = pd.read_sql(query, conn)
    print(f"📋 Available tables in database:\n")
    for table in tables['table_name']:
        print(f"   • {table}")
    print()

    # Ask which table contains the services
    service_table = input("Which table contains the services? ").strip()

    # Get sample of that table to see structure
    sample_query = f"SELECT * FROM {service_table} LIMIT 5;"
    sample = pd.read_sql(sample_query, conn)
    print(f"\n📊 Sample data from {service_table}:\n")
    print(sample.to_string())
    print()

    # Get all columns
    print(f"Columns available: {', '.join(sample.columns)}\n")

    # Export all services
    confirm = input(f"Export all records from {service_table}? (yes/no): ").strip().lower()

    if confirm == 'yes':
        export_query = f"SELECT * FROM {service_table};"
        services_df = pd.read_sql(export_query, conn)

        # Save to CSV
        output_dir = Path(__file__).parent.parent / 'data' / 'exports'
        output_dir.mkdir(parents=True, exist_ok=True)
        output_file = output_dir / 'service_map_export.csv'

        services_df.to_csv(output_file, index=False)

        print(f"\n✅ Exported {len(services_df)} services to:")
        print(f"   {output_file}\n")

        # Show summary
        print("="*80)
        print("EXPORT SUMMARY")
        print("="*80)
        print(f"Total services: {len(services_df)}")
        print(f"Columns exported: {len(services_df.columns)}")
        print(f"\nColumn names:")
        for col in services_df.columns:
            non_null = services_df[col].notna().sum()
            print(f"   • {col}: {non_null}/{len(services_df)} populated")
        print()

    conn.close()

except Exception as e:
    print(f"❌ Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure your service map PostgreSQL database is running")
    print("2. Check your database credentials")
    print("3. Verify the database name is correct")
    print("4. Ensure you can connect with: psql -h host -U user -d database")
