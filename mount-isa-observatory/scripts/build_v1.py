"""
V1 Data Builder for Mount Isa Economic Observatory
Runs all scrapers, validates data, and creates first working version
"""
import subprocess
import sys
from pathlib import Path
import pandas as pd
from datetime import datetime
import json

print("\n" + "="*80)
print("🚀 BUILDING MOUNT ISA ECONOMIC OBSERVATORY V1")
print("="*80 + "\n")

# Track what data we successfully collect
data_sources = {
    'service_map_export': {'status': 'pending', 'records': 0, 'file': None},
    'acnc_charities': {'status': 'pending', 'records': 0, 'file': None},
    'grantconnect_grants': {'status': 'pending', 'records': 0, 'file': None},
    'qld_open_data': {'status': 'pending', 'records': 0, 'file': None},
}

data_dir = Path(__file__).parent.parent / 'data' / 'raw'
data_dir.mkdir(parents=True, exist_ok=True)

# Step 1: Export service map (if database available)
print("="*80)
print("STEP 1: EXPORT SERVICE MAP DATA")
print("="*80 + "\n")

print("Do you want to export your service map database now?")
print("(You need PostgreSQL credentials for your service map)")
export_now = input("Export now? (yes/no): ").strip().lower()

if export_now == 'yes':
    print("\n▶️  Running service map export...\n")
    try:
        subprocess.run([sys.executable, 'scripts/export_service_map.py'], check=True)

        # Check if export succeeded
        export_file = data_dir / 'service_map_export.csv'
        if export_file.exists():
            df = pd.read_csv(export_file)
            data_sources['service_map_export']['status'] = 'success'
            data_sources['service_map_export']['records'] = len(df)
            data_sources['service_map_export']['file'] = str(export_file)
            print(f"\n✅ Service map: {len(df)} services exported")
        else:
            data_sources['service_map_export']['status'] = 'failed'
            print("\n⚠️  Service map export file not found")
    except subprocess.CalledProcessError:
        data_sources['service_map_export']['status'] = 'failed'
        print("\n⚠️  Service map export failed - continuing with other sources")
else:
    print("⏭️  Skipping service map export for now")
    data_sources['service_map_export']['status'] = 'skipped'

# Step 2: Scrape ACNC charities
print("\n" + "="*80)
print("STEP 2: SCRAPE ACNC CHARITY DATA")
print("="*80 + "\n")

print("▶️  Running ACNC scraper...\n")
try:
    subprocess.run([sys.executable, 'scripts/scrape_acnc_charities.py'], check=True)

    charity_file = data_dir / 'mount_isa_charities.csv'
    if charity_file.exists():
        df = pd.read_csv(charity_file)
        data_sources['acnc_charities']['status'] = 'success'
        data_sources['acnc_charities']['records'] = len(df)
        data_sources['acnc_charities']['file'] = str(charity_file)
        print(f"\n✅ ACNC: {len(df)} charities found")
    else:
        data_sources['acnc_charities']['status'] = 'no_results'
        print("\n⚠️  No Mount Isa charities found in ACNC register")
except Exception as e:
    data_sources['acnc_charities']['status'] = 'failed'
    print(f"\n⚠️  ACNC scrape failed: {e}")

# Step 3: Scrape GrantConnect
print("\n" + "="*80)
print("STEP 3: SCRAPE GRANTCONNECT GRANTS")
print("="*80 + "\n")

print("▶️  Running GrantConnect scraper...\n")
try:
    subprocess.run([sys.executable, 'scripts/scrape_grantconnect.py'], check=True)

    grants_file = data_dir / 'mount_isa_grants_grantconnect.csv'
    if grants_file.exists():
        df = pd.read_csv(grants_file)
        data_sources['grantconnect_grants']['status'] = 'success'
        data_sources['grantconnect_grants']['records'] = len(df)
        data_sources['grantconnect_grants']['file'] = str(grants_file)
        print(f"\n✅ GrantConnect: {len(df)} grants found")
    else:
        data_sources['grantconnect_grants']['status'] = 'no_results'
        print("\n⚠️  No grants found in GrantConnect for Mount Isa")
except Exception as e:
    data_sources['grantconnect_grants']['status'] = 'failed'
    print(f"\n⚠️  GrantConnect scrape failed: {e}")

# Generate V1 Report
print("\n" + "="*80)
print("📊 V1 DATA COLLECTION REPORT")
print("="*80 + "\n")

report = {
    'build_date': datetime.now().isoformat(),
    'version': 'v1.0',
    'data_sources': data_sources,
    'summary': {
        'total_sources': len(data_sources),
        'successful': sum(1 for s in data_sources.values() if s['status'] == 'success'),
        'failed': sum(1 for s in data_sources.values() if s['status'] == 'failed'),
        'skipped': sum(1 for s in data_sources.values() if s['status'] == 'skipped'),
        'total_records': sum(s['records'] for s in data_sources.values()),
    }
}

# Print summary
print("Data Collection Summary:\n")
for source_name, source_data in data_sources.items():
    status_icon = {
        'success': '✅',
        'failed': '❌',
        'skipped': '⏭️',
        'no_results': '⚠️',
        'pending': '⏸️'
    }.get(source_data['status'], '❓')

    print(f"{status_icon} {source_name:30s}: {source_data['status']:12s} ({source_data['records']} records)")
    if source_data['file']:
        print(f"   📁 {source_data['file']}")

print(f"\n{'='*80}")
print(f"Total Records: {report['summary']['total_records']}")
print(f"Successful Sources: {report['summary']['successful']}/{report['summary']['total_sources']}")
print("="*80 + "\n")

# Save report
report_file = Path(__file__).parent.parent / 'data' / 'v1_build_report.json'
with open(report_file, 'w') as f:
    json.dump(report, f, indent=2)

print(f"💾 Report saved to: {report_file}\n")

# Next steps based on what we got
print("="*80)
print("🎯 NEXT STEPS FOR V1")
print("="*80 + "\n")

if report['summary']['total_records'] > 0:
    print("✅ You have data! Next steps:\n")
    print("1. Import data into PostgreSQL database:")
    print("   python scripts/import_to_database.py\n")
    print("2. Run data validation:")
    print("   python scripts/validate_data.py\n")
    print("3. Generate initial economic analysis:")
    print("   python analysis/economic_flow_tracker.py\n")
    print("4. View interactive map:")
    print("   Open visualization/map_dashboard.html\n")
else:
    print("⚠️  No data collected yet. To build v1:\n")

    if data_sources['service_map_export']['status'] in ['skipped', 'failed']:
        print("1. Export your service map database:")
        print("   python scripts/export_service_map.py\n")

    print("2. Manually download these datasets:")
    print("   • ACNC Charity Register: https://www.acnc.gov.au/charity/data")
    print("   • GrantConnect: https://www.grants.gov.au/")
    print("   • QLD Open Data: https://www.data.qld.gov.au/\n")

    print("3. Place CSV files in: mount-isa-observatory/data/raw/\n")

    print("4. Re-run this script: python scripts/build_v1.py\n")

print("="*80)
print("✅ V1 BUILD PROCESS COMPLETE")
print("="*80 + "\n")
