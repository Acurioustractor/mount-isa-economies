"""
Analyze the sample procurement data we just fetched
Shows the power of the Economic Observatory
"""
import pandas as pd
from pathlib import Path
import json

print("\n" + "="*70)
print("🏛️  MOUNT ISA ECONOMIC OBSERVATORY - FULL ANALYSIS")
print("="*70 + "\n")

# Load the latest procurement data
data_dir = Path('data/raw/qld_procurement')
csv_files = sorted(data_dir.glob('qld_procurement_direct_*.csv'))

if not csv_files:
    print("❌ No data files found. Run ingestion first:")
    print("   python ingestion/qld_gov/fetch_procurement_direct.py")
    exit(1)

latest_file = csv_files[-1]
print(f"📂 Loading data from: {latest_file.name}")

df = pd.read_csv(latest_file)
print(f"   Records: {len(df)}")
print(f"   Date range: {df['publish_date'].min()} to {df['publish_date'].max()}")

# Load provenance
provenance_files = sorted(data_dir.glob('provenance_*.json'))
if provenance_files:
    with open(provenance_files[-1]) as f:
        prov = json.load(f)
    print(f"\n🔐 Data Provenance:")
    print(f"   Fetch time: {prov['fetch_timestamp']}")
    print(f"   File hash: {prov['file_hash'][:16]}...")
    print(f"   Licence: {prov.get('licence', 'Unknown')}")

print("\n" + "="*70)
print("💰 FINANCIAL ANALYSIS")
print("="*70 + "\n")

# Total spending
total_value = df['contract_value'].sum()
local_value = df[df['is_local']]['contract_value'].sum()
external_value = total_value - local_value
local_pct = (local_value / total_value * 100) if total_value > 0 else 0

print(f"Total Queensland Government Spending (sample): ${total_value:,.0f}")
print(f"  ✓ Local (Mount Isa 4825): ${local_value:,.0f} ({local_pct:.1f}%)")
print(f"  🚨 External (LEAKAGE): ${external_value:,.0f} ({100-local_pct:.1f}%)")

print("\n" + "-"*70)
print("🎯 10% LOCALIZATION PILOT TARGETS")
print("-"*70 + "\n")

target_amount = external_value * 0.10
jobs_created = target_amount / 100000  # $100k per job estimate
multiplier_effect = target_amount * 1.48  # 48% local multiplier

print(f"If we shift 10% of external spending to local providers:")
print(f"  💵 Direct impact: ${target_amount:,.0f} stays in Mount Isa")
print(f"  👥 Estimated jobs: ~{int(jobs_created)} new local positions")
print(f"  🔄 Total economic impact (with multiplier): ${multiplier_effect:,.0f}")
print(f"  📈 GDP contribution: ${multiplier_effect:,.0f}")

print("\n" + "="*70)
print("📊 CATEGORY BREAKDOWN - WHERE'S THE MONEY GOING?")
print("="*70 + "\n")

category_analysis = df.groupby(['category', 'is_local']).agg({
    'contract_value': ['sum', 'count']
}).round(0)

category_totals = df.groupby('category').agg({
    'contract_value': 'sum',
    'is_local': 'sum'
}).sort_values('contract_value', ascending=False)

print("Top Categories by Total Spending:\n")
for category, row in category_totals.head(10).iterrows():
    total = row['contract_value']
    local_contracts = int(row['is_local'])
    total_contracts = len(df[df['category'] == category])
    local_spend = df[(df['category'] == category) & (df['is_local'])]['contract_value'].sum()
    local_spend_pct = (local_spend / total * 100) if total > 0 else 0

    print(f"{category:.<25} ${total:>12,.0f}")
    print(f"  {'':.<25} Local: {local_contracts}/{total_contracts} contracts ({local_spend_pct:.1f}% of $)")

    # Identify opportunities
    if local_spend_pct < 20 and total > 500000:
        opportunity = total * 0.10
        print(f"  {'':.<25} 🎯 OPPORTUNITY: ${opportunity:,.0f} could be localized")
    print()

print("="*70)
print("🏢 AGENCY ANALYSIS - WHO'S BUYING WHAT?")
print("="*70 + "\n")

agency_analysis = df.groupby('agency').agg({
    'contract_value': 'sum',
    'is_local': lambda x: f"{x.sum()}/{len(x)}"
}).sort_values('contract_value', ascending=False)

print("Top Agencies by Spending:\n")
for agency, row in agency_analysis.head(5).iterrows():
    print(f"{agency}")
    print(f"  Total spending: ${row['contract_value']:,.0f}")
    print(f"  Local contracts: {row['is_local']}")
    print()

print("="*70)
print("🗺️  GEOGRAPHIC LEAKAGE - WHERE IS MONEY FLOWING TO?")
print("="*70 + "\n")

location_analysis = df.groupby('supplier_location').agg({
    'contract_value': 'sum',
    'supplier_name': 'count'
}).sort_values('contract_value', ascending=False)
location_analysis.columns = ['Total Value', 'Contract Count']

print(location_analysis.to_string())

print("\n" + "="*70)
print("🔍 SERVICE GAPS - HIGH PRIORITY OPPORTUNITIES")
print("="*70 + "\n")

# Find categories with high external spending and few/no local providers
service_gaps = []

for category in df['category'].unique():
    cat_data = df[df['category'] == category]
    total_spend = cat_data['contract_value'].sum()
    local_providers = cat_data[cat_data['is_local']]['supplier_name'].nunique()
    external_spend = cat_data[~cat_data['is_local']]['contract_value'].sum()

    if external_spend > 100000 and local_providers < 3:
        service_gaps.append({
            'category': category,
            'external_spending': external_spend,
            'local_providers': local_providers,
            'opportunity_score': external_spend / (local_providers + 1)
        })

service_gaps_df = pd.DataFrame(service_gaps).sort_values('opportunity_score', ascending=False)

if len(service_gaps_df) > 0:
    print("Categories with HIGH external spending & LOW local capacity:\n")
    for idx, row in service_gaps_df.head(5).iterrows():
        print(f"{row['category']}")
        print(f"  External spending: ${row['external_spending']:,.0f}")
        print(f"  Local providers: {row['local_providers']}")
        print(f"  🎯 Opportunity score: {row['opportunity_score']:,.0f}")
        print(f"  → Action: Train local workers or support new business in this area")
        print()

print("="*70)
print("📋 RECOMMENDED ACTIONS FOR MOUNT ISA")
print("="*70 + "\n")

print("1. IMMEDIATE (This Month):")
print(f"   • Present these findings at Council meeting")
print(f"   • Identify 2-3 priority categories from service gaps above")
print(f"   • Connect with TAFE Queensland about training programs")
print()

print("2. SHORT-TERM (Next 3 Months):")
print(f"   • Launch community investment fund for gap categories")
print(f"   • Support {int(jobs_created)} local workers to get certified/trained")
print(f"   • Work with top agencies to preference local suppliers")
print()

print("3. LONG-TERM (12 Month Pilot):")
print(f"   • Track progress monthly (re-run this analysis)")
print(f"   • Aim to shift ${target_amount:,.0f} to local providers")
print(f"   • Measure job creation and community wellbeing impact")
print()

print("="*70)
print("✅ ANALYSIS COMPLETE")
print("="*70)
print(f"\n💡 This is just SAMPLE data. Imagine this with:")
print(f"   • Real Queensland procurement (1000s of contracts)")
print(f"   • Commonwealth AusTender data")
print(f"   • Medicare & PBS health spending")
print(f"   • Local business registry (ABN Lookup)")
print(f"   • Mining company procurement")
print(f"\n   The full picture will be even more powerful! 🚀")
print()
