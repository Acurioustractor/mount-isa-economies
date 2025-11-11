"""
ONE-COMMAND DATA COLLECTION
Exports all local databases + scrapes all government sources
"""
import subprocess
import sys
from pathlib import Path
import json
from datetime import datetime

print("\n" + "="*80)
print("🚀 MOUNT ISA ECONOMIC OBSERVATORY - COMPLETE DATA COLLECTION")
print("="*80 + "\n")

scripts_dir = Path(__file__).parent
results = {}

# ============================================================================
# STEP 1: Export existing databases
# ============================================================================

print("="*80)
print("STEP 1: EXPORT EXISTING DATABASES")
print("="*80 + "\n")

try:
    subprocess.run([sys.executable, str(scripts_dir / 'export_all_databases.py')], check=True)
    results['database_export'] = 'success'
except subprocess.CalledProcessError:
    results['database_export'] = 'failed'
    print("\n⚠️  Database export had issues, but continuing...\n")
except Exception as e:
    results['database_export'] = 'failed'
    print(f"\n⚠️  Could not run database export: {e}\n")

# ============================================================================
# STEP 2: Scrape ACNC charities
# ============================================================================

print("\n" + "="*80)
print("STEP 2: SCRAPE ACNC CHARITY REGISTER")
print("="*80 + "\n")

try:
    subprocess.run([sys.executable, str(scripts_dir / 'scrape_acnc_charities.py')], check=True)
    results['acnc_scrape'] = 'success'
except subprocess.CalledProcessError:
    results['acnc_scrape'] = 'failed'
    print("\n⚠️  ACNC scrape had issues, but continuing...\n")
except Exception as e:
    results['acnc_scrape'] = 'failed'
    print(f"\n⚠️  Could not run ACNC scraper: {e}\n")

# ============================================================================
# STEP 3: Scrape GrantConnect
# ============================================================================

print("\n" + "="*80)
print("STEP 3: SCRAPE GRANTCONNECT")
print("="*80 + "\n")

try:
    subprocess.run([sys.executable, str(scripts_dir / 'scrape_grantconnect.py')], check=True)
    results['grantconnect_scrape'] = 'success'
except subprocess.CalledProcessError:
    results['grantconnect_scrape'] = 'failed'
    print("\n⚠️  GrantConnect scrape had issues, but continuing...\n")
except Exception as e:
    results['grantconnect_scrape'] = 'failed'
    print(f"\n⚠️  Could not run GrantConnect scraper: {e}\n")

# ============================================================================
# STEP 4: Generate comprehensive report
# ============================================================================

print("\n" + "="*80)
print("STEP 4: GENERATING COMPREHENSIVE DATA REPORT")
print("="*80 + "\n")

data_dir = scripts_dir.parent / 'data'
exports_dir = data_dir / 'exports'
raw_dir = data_dir / 'raw'

# Count files and records
import pandas as pd

total_records = 0
data_summary = {}

# Check exports
if exports_dir.exists():
    for csv_file in exports_dir.glob('*.csv'):
        try:
            df = pd.read_csv(csv_file)
            data_summary[csv_file.name] = {
                'records': len(df),
                'columns': len(df.columns),
                'source': 'local_database'
            }
            total_records += len(df)
        except Exception as e:
            print(f"⚠️  Could not read {csv_file.name}: {e}")

# Check raw scraped data
if raw_dir.exists():
    for csv_file in raw_dir.glob('*.csv'):
        try:
            df = pd.read_csv(csv_file, on_bad_lines='skip')
            data_summary[csv_file.name] = {
                'records': len(df),
                'columns': len(df.columns),
                'source': 'government_scrape'
            }
            total_records += len(df)
        except Exception as e:
            print(f"⚠️  Could not read {csv_file.name}: {e}")

# Generate report
report = {
    'collection_date': datetime.now().isoformat(),
    'version': 'v1.0',
    'collection_results': results,
    'data_summary': data_summary,
    'totals': {
        'total_records': total_records,
        'total_files': len(data_summary),
        'local_database_files': sum(1 for d in data_summary.values() if d['source'] == 'local_database'),
        'government_scrape_files': sum(1 for d in data_summary.values() if d['source'] == 'government_scrape'),
    }
}

# Save report
report_file = data_dir / 'collection_report.json'
with open(report_file, 'w') as f:
    json.dump(report, f, indent=2)

# Print summary
print("="*80)
print("📊 COMPREHENSIVE DATA COLLECTION REPORT")
print("="*80 + "\n")

print("Collection Results:\n")
for step, status in results.items():
    icon = "✅" if status == "success" else "⚠️"
    print(f"  {icon} {step}: {status}")

print(f"\nData Collected:\n")
print(f"  Total files: {report['totals']['total_files']}")
print(f"  Total records: {report['totals']['total_records']:,}")
print(f"  From local databases: {report['totals']['local_database_files']} files")
print(f"  From government sources: {report['totals']['government_scrape_files']} files")

print(f"\nFiles by source:\n")

# Group by source
local_files = [(k, v) for k, v in data_summary.items() if v['source'] == 'local_database']
govt_files = [(k, v) for k, v in data_summary.items() if v['source'] == 'government_scrape']

if local_files:
    print("  📁 Local Database Exports:")
    for filename, info in sorted(local_files, key=lambda x: x[1]['records'], reverse=True):
        print(f"     • {filename:50s}: {info['records']:>6,} records")

if govt_files:
    print("\n  🏛️  Government Data Scrapes:")
    for filename, info in sorted(govt_files, key=lambda x: x[1]['records'], reverse=True):
        print(f"     • {filename:50s}: {info['records']:>6,} records")

print(f"\n💾 Full report saved to: {report_file}\n")

print("="*80)
print("✅ DATA COLLECTION COMPLETE")
print("="*80 + "\n")

# Key insights
print("🎯 WHAT YOU NOW HAVE:\n")

services_count = 0
interviews_count = 0
gaps_count = 0
charities_count = 0
grants_count = 0

for filename, info in data_summary.items():
    if 'services_export' in filename:
        services_count = info['records']
    elif 'community_interviews' in filename:
        interviews_count = info['records']
    elif 'gaps' in filename:
        gaps_count = info['records']
    elif 'charities' in filename:
        charities_count = info['records']
    elif 'grants' in filename:
        grants_count = info['records']

if services_count > 0:
    print(f"  ✅ {services_count} services mapped")
if interviews_count > 0:
    print(f"  ✅ {interviews_count} community interviews")
if gaps_count > 0:
    print(f"  ✅ {gaps_count} service gaps identified")
if charities_count > 0:
    print(f"  ✅ {charities_count} registered charities (ACNC)")
if grants_count > 0:
    print(f"  ✅ {grants_count} government grants (GrantConnect)")

print("\n🚀 NEXT STEPS:\n")
print("  1. Review data in: data/exports/ and data/raw/")
print("  2. Import into economic observatory database")
print("  3. Run economic flow analysis")
print("  4. View interactive map dashboard")
print()
