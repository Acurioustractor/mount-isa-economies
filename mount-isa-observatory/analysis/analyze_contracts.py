"""
Contract Analyzer - Find Mount Isa in 530,960 QLD Government Contracts
Analyzes downloaded contracts to find Mount Isa suppliers, locations, and spending
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
import re

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'contracts'
OUTPUT_DIR = BASE_DIR / 'data' / 'analysis'
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*80)
print("🔍 ANALYZING 530K+ QLD CONTRACTS FOR MOUNT ISA")
print("="*80 + "\n")

# Find all contract CSV files
contract_files = list(DATA_DIR.glob('*.csv'))

print(f"📁 Found {len(contract_files)} contract files\n")

all_contracts = []

for file in contract_files:
    print(f"Loading: {file.name}")
    try:
        df = pd.read_csv(file, low_memory=False)
        df['source_file'] = file.name
        all_contracts.append(df)
        print(f"   ✅ Loaded {len(df):,} contracts")
    except Exception as e:
        print(f"   ❌ Error: {e}")

if not all_contracts:
    print("\n❌ No contract files found")
    print("Run qld_contracts_scraper.py first")
    exit(1)

# Combine all contracts
combined = pd.concat(all_contracts, ignore_index=True)

print(f"\n✅ Total contracts loaded: {len(combined):,}\n")

# Show available columns
print("📋 Available columns:")
for col in combined.columns:
    print(f"   • {col}")
print()

# Search for Mount Isa in all text columns
print("🔍 Searching for Mount Isa mentions...\n")

mount_isa_keywords = [
    'mount isa',
    'mount-isa',
    'mt isa',
    'kalkadoon',
    '4825',  # Postcode
    '4823', '4824', '4828',  # Surrounding postcodes
]

# Search across all text columns
mount_isa_contracts = pd.DataFrame()

for col in combined.columns:
    if combined[col].dtype == 'object':  # Text column
        print(f"   Searching column: {col}...")

        for keyword in mount_isa_keywords:
            matches = combined[
                combined[col].astype(str).str.contains(keyword, case=False, na=False)
            ]

            if len(matches) > 0:
                print(f"      ✅ Found {len(matches)} matches for '{keyword}'")
                mount_isa_contracts = pd.concat([mount_isa_contracts, matches])

mount_isa_contracts = mount_isa_contracts.drop_duplicates()

print(f"\n✅ Found {len(mount_isa_contracts):,} Mount Isa contracts\n")

if len(mount_isa_contracts) > 0:
    print("="*80)
    print("📊 MOUNT ISA CONTRACTS ANALYSIS")
    print("="*80 + "\n")

    # Find value/amount columns
    value_cols = [col for col in mount_isa_contracts.columns
                 if any(term in col.lower() for term in ['value', 'amount', 'price', 'cost', 'total'])]

    print(f"💰 Financial columns found: {value_cols}\n")

    # Calculate totals
    for col in value_cols:
        if col in mount_isa_contracts.columns:
            # Try to convert to numeric
            try:
                numeric_vals = pd.to_numeric(
                    mount_isa_contracts[col].astype(str).str.replace('$', '').str.replace(',', ''),
                    errors='coerce'
                )

                total = numeric_vals.sum()
                count = numeric_vals.notna().sum()

                if total > 0:
                    print(f"   {col}:")
                    print(f"      Total: ${total:,.0f}")
                    print(f"      Contracts: {count}")
                    print(f"      Average: ${total/count:,.0f}")
                    print()

            except Exception as e:
                print(f"   ⚠️  Could not calculate {col}: {e}")

    # Show top contracts
    print("\n" + "="*80)
    print("📋 TOP MOUNT ISA CONTRACTS")
    print("="*80 + "\n")

    # Find supplier/contractor columns
    supplier_cols = [col for col in mount_isa_contracts.columns
                    if any(term in col.lower() for term in ['supplier', 'contractor', 'vendor', 'company', 'name'])]

    # Find description columns
    desc_cols = [col for col in mount_isa_contracts.columns
                if any(term in col.lower() for term in ['description', 'details', 'purpose', 'subject'])]

    # Sort by value if possible
    display_df = mount_isa_contracts.copy()

    if value_cols:
        # Try to sort by first value column
        try:
            val_col = value_cols[0]
            display_df['_sort_value'] = pd.to_numeric(
                display_df[val_col].astype(str).str.replace('$', '').str.replace(',', ''),
                errors='coerce'
            )
            display_df = display_df.sort_values('_sort_value', ascending=False)
        except:
            pass

    # Display top 30 contracts
    for idx, contract in display_df.head(30).iterrows():
        print(f"{idx + 1}.")

        # Show supplier
        for col in supplier_cols:
            if col in contract.index and pd.notna(contract[col]):
                print(f"   Supplier: {contract[col]}")
                break

        # Show value
        for col in value_cols:
            if col in contract.index and pd.notna(contract[col]):
                print(f"   Value: {contract[col]}")
                break

        # Show description
        for col in desc_cols:
            if col in contract.index and pd.notna(contract[col]):
                desc = str(contract[col])[:150]
                print(f"   Description: {desc}...")
                break

        # Show date if available
        date_cols = [col for col in contract.index if 'date' in col.lower()]
        for col in date_cols:
            if pd.notna(contract[col]):
                print(f"   Date: {contract[col]}")
                break

        print()

    # Analyze by supplier
    print("="*80)
    print("🏢 TOP SUPPLIERS TO MOUNT ISA")
    print("="*80 + "\n")

    if supplier_cols:
        supplier_col = supplier_cols[0]
        supplier_counts = mount_isa_contracts[supplier_col].value_counts()

        print(f"Top 20 suppliers by number of contracts:\n")
        for supplier, count in supplier_counts.head(20).items():
            print(f"   {supplier}: {count} contracts")

        print()

    # Analyze by department/organization
    org_cols = [col for col in mount_isa_contracts.columns
               if any(term in col.lower() for term in ['department', 'agency', 'organization', 'org'])]

    if org_cols:
        print("="*80)
        print("🏛️  CONTRACTING DEPARTMENTS")
        print("="*80 + "\n")

        org_col = org_cols[0]
        dept_counts = mount_isa_contracts[org_col].value_counts()

        print(f"Top 15 departments contracting in Mount Isa:\n")
        for dept, count in dept_counts.head(15).items():
            print(f"   {dept}: {count} contracts")

        print()

    # Save Mount Isa contracts
    output_file = OUTPUT_DIR / f'mount_isa_contracts_analysis_{datetime.now().strftime("%Y%m%d")}.csv'
    mount_isa_contracts.to_csv(output_file, index=False)

    print(f"💾 Saved Mount Isa contracts: {output_file}\n")

    # Create summary report
    summary = {
        'total_contracts': len(combined),
        'mount_isa_contracts': len(mount_isa_contracts),
        'percentage': len(mount_isa_contracts) / len(combined) * 100,
        'analysis_date': datetime.now().isoformat()
    }

    if value_cols and total > 0:
        summary['total_value'] = float(total)
        summary['average_value'] = float(total / count)

    import json
    summary_file = OUTPUT_DIR / f'mount_isa_contracts_summary_{datetime.now().strftime("%Y%m%d")}.json'
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    print(f"💾 Saved summary: {summary_file}\n")

else:
    print("⚠️  No Mount Isa contracts found in dataset")
    print("\nThis could mean:")
    print("  • Contracts don't include location/supplier details")
    print("  • Mount Isa suppliers use different naming")
    print("  • Need to search by ABN or different identifiers")
    print()

print("="*80)
print("✅ CONTRACT ANALYSIS COMPLETE")
print("="*80 + "\n")

print("🎯 Key findings will be in:")
print(f"   {OUTPUT_DIR}")
print()
