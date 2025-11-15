"""
Smart Supplier Enrichment - Multiple Strategies
Uses 3 approaches for high success rate:
1. Extract ACNs/ABNs from supplier names
2. Match supplier names to ASIC company data
3. Focus on Mount Isa Water Board contracts specifically
"""
import pandas as pd
import re
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import requests

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

print("\n" + "="*80)
print("🎯 SMART SUPPLIER ENRICHMENT")
print("="*80 + "\n")

def extract_abn_acn_from_text(text: str) -> dict:
    """
    Extract ABN or ACN numbers embedded in supplier names

    Examples:
    - "COMPANY NAME ABN 12345678901"
    - "COMPANY NAME ACN 123456789"
    - "COMPANY NAME - ABN: 12 345 678 901"
    """
    if not text or not isinstance(text, str):
        return {}

    result = {}

    # ABN pattern: 11 digits, may have spaces
    abn_patterns = [
        r'ABN[:\s]+(\d{2}\s?\d{3}\s?\d{3}\s?\d{3})',
        r'ABN[:\s]+(\d{11})',
    ]

    for pattern in abn_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            abn = match.group(1).replace(' ', '')
            if len(abn) == 11:
                result['abn'] = abn
                break

    # ACN pattern: 9 digits, may have spaces
    acn_patterns = [
        r'ACN[:\s]+(\d{3}\s?\d{3}\s?\d{3})',
        r'ACN[:\s]+(\d{9})',
    ]

    for pattern in acn_patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            acn = match.group(1).replace(' ', '')
            if len(acn) == 9:
                result['acn'] = acn
                break

    return result

def load_asic_companies() -> pd.DataFrame:
    """
    Download and load ASIC company data for Queensland
    """
    print("📥 Downloading ASIC company data...\n")

    asic_url = "https://data.gov.au/data/dataset/5e59f5a0-1560-4f11-a4bc-61c3b3830af7/resource/eb1e6be4-5b13-4feb-b28e-388bf7c26f93/download/2025_01_asic_companies.csv"

    try:
        # Try to download
        df = pd.read_csv(asic_url, low_memory=False, nrows=100000)  # First 100k for speed
        print(f"✅ Loaded {len(df):,} ASIC company records\n")

        # Filter for Queensland
        if 'State' in df.columns:
            qld_df = df[df['State'].str.contains('QLD', case=False, na=False)]
            print(f"✅ Filtered to {len(qld_df):,} Queensland companies\n")
            return qld_df

        return df

    except Exception as e:
        print(f"⚠️  Could not download ASIC data: {e}")
        print("   Continuing without ASIC matching...\n")
        return pd.DataFrame()

def match_supplier_to_company(supplier_name: str, companies_df: pd.DataFrame) -> dict:
    """
    Try to match supplier name to ASIC company
    """
    if companies_df.empty or not supplier_name:
        return {}

    # Clean supplier name
    supplier_clean = supplier_name.upper().strip()

    # Remove common suffixes
    for suffix in [' PTY LTD', ' PTY. LTD.', ' LIMITED', ' LTD', ' PROPRIETARY']:
        supplier_clean = supplier_clean.replace(suffix, '')

    # Try exact match on company name
    if 'CompanyName' in companies_df.columns:
        matches = companies_df[companies_df['CompanyName'].str.upper().str.contains(supplier_clean, na=False, regex=False)]

        if len(matches) == 1:
            # Exact unique match
            return {
                'abn': matches.iloc[0].get('ABN'),
                'acn': matches.iloc[0].get('ACN'),
                'company_name': matches.iloc[0].get('CompanyName'),
                'match_method': 'asic_exact'
            }
        elif len(matches) > 1:
            # Multiple matches - take first active one
            if 'Status' in matches.columns:
                active = matches[matches['Status'] == 'Registered']
                if len(active) > 0:
                    return {
                        'abn': active.iloc[0].get('ABN'),
                        'acn': active.iloc[0].get('ACN'),
                        'company_name': active.iloc[0].get('CompanyName'),
                        'match_method': 'asic_active'
                    }

    return {}

def enrich_contracts(contracts_file: Path) -> pd.DataFrame:
    """
    Enrich contract suppliers using multiple strategies
    """
    print(f"📄 Loading contracts: {contracts_file.name}\n")

    df = pd.read_csv(contracts_file, low_memory=False)
    print(f"✅ Loaded {len(df):,} contracts\n")

    # Find supplier column
    supplier_cols = [col for col in df.columns if 'supplier' in col.lower() and 'name' in col.lower()]
    if not supplier_cols:
        print("❌ No supplier name column found")
        return df

    supplier_col = supplier_cols[0]
    print(f"📋 Using supplier column: {supplier_col}\n")

    # Get unique suppliers
    unique_suppliers = df[supplier_col].dropna().unique()
    print(f"🔍 Found {len(unique_suppliers):,} unique suppliers\n")

    # Load ASIC data
    asic_df = load_asic_companies()

    # Enrich each supplier
    enrichment_data = []

    print("🔧 Enriching suppliers using multiple strategies...\n")

    for supplier in tqdm(unique_suppliers, desc="Processing"):
        result = {
            'supplier_name_original': supplier,
            'abn': None,
            'acn': None,
            'company_name': None,
            'match_method': None
        }

        # Strategy 1: Extract from supplier name
        extracted = extract_abn_acn_from_text(str(supplier))
        if extracted:
            result.update(extracted)
            result['match_method'] = 'extracted_from_name'

        # Strategy 2: Match to ASIC data
        if not result['abn'] and not asic_df.empty:
            matched = match_supplier_to_company(str(supplier), asic_df)
            if matched:
                result.update(matched)

        enrichment_data.append(result)

    # Create enrichment dataframe
    enrichment_df = pd.DataFrame(enrichment_data)

    # Statistics
    print("\n" + "="*80)
    print("📊 ENRICHMENT RESULTS")
    print("="*80 + "\n")

    total = len(enrichment_df)
    with_abn = enrichment_df['abn'].notna().sum()
    with_acn = enrichment_df['acn'].notna().sum()
    with_either = enrichment_df[['abn', 'acn']].notna().any(axis=1).sum()

    print(f"Total suppliers: {total:,}")
    print(f"With ABN: {with_abn:,} ({with_abn/total*100:.1f}%)")
    print(f"With ACN: {with_acn:,} ({with_acn/total*100:.1f}%)")
    print(f"With ABN or ACN: {with_either:,} ({with_either/total*100:.1f}%)\n")

    # Method breakdown
    if 'match_method' in enrichment_df.columns:
        print("Match methods:")
        method_counts = enrichment_df['match_method'].value_counts()
        for method, count in method_counts.items():
            if pd.notna(method):
                print(f"  {method}: {count:,}")
        print()

    # Save mapping
    mapping_file = DATA_DIR / 'abn_lookup' / f'supplier_enrichment_{datetime.now().strftime("%Y%m%d")}.csv'
    mapping_file.parent.mkdir(parents=True, exist_ok=True)
    enrichment_df.to_csv(mapping_file, index=False)
    print(f"💾 Saved enrichment mapping: {mapping_file}\n")

    # Merge back to contracts
    df_enriched = df.merge(
        enrichment_df,
        left_on=supplier_col,
        right_on='supplier_name_original',
        how='left',
        suffixes=('', '_enriched')
    )

    return df_enriched, enrichment_df

def extract_mount_isa_contracts(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract contracts specifically related to Mount Isa
    """
    print("🔍 Filtering for Mount Isa contracts...\n")

    mount_isa_keywords = ['mount isa', 'mount-isa', 'kalkadoon', '4825', 'miwb', 'mount isa water']

    mount_isa_contracts = pd.DataFrame()

    # Search in all text columns
    for col in df.columns:
        if df[col].dtype == 'object':
            for keyword in mount_isa_keywords:
                matches = df[df[col].astype(str).str.contains(keyword, case=False, na=False)]
                mount_isa_contracts = pd.concat([mount_isa_contracts, matches]).drop_duplicates()

    print(f"✅ Found {len(mount_isa_contracts):,} Mount Isa contracts\n")

    return mount_isa_contracts

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 enrich_suppliers_smart.py path/to/contracts.csv")
        sys.exit(1)

    contracts_file = Path(sys.argv[1])

    if not contracts_file.exists():
        print(f"❌ File not found: {contracts_file}")
        sys.exit(1)

    # Enrich all suppliers
    enriched_df, mapping_df = enrich_contracts(contracts_file)

    # Extract Mount Isa specific contracts
    mount_isa_df = extract_mount_isa_contracts(enriched_df)

    # Save results
    output_dir = DATA_DIR / 'contracts'
    output_dir.mkdir(parents=True, exist_ok=True)

    enriched_file = output_dir / f'contracts_enriched_{datetime.now().strftime("%Y%m%d")}.csv'
    enriched_df.to_csv(enriched_file, index=False)
    print(f"💾 Saved enriched contracts: {enriched_file}\n")

    if len(mount_isa_df) > 0:
        mount_isa_file = output_dir / f'mount_isa_contracts_{datetime.now().strftime("%Y%m%d")}.csv'
        mount_isa_df.to_csv(mount_isa_file, index=False)
        print(f"💾 Saved Mount Isa contracts: {mount_isa_file}\n")

        # Show some Mount Isa contracts
        print("="*80)
        print("📊 MOUNT ISA CONTRACT EXAMPLES")
        print("="*80 + "\n")

        for idx, contract in mount_isa_df.head(10).iterrows():
            supplier = contract.get('suppliername', 'Unknown')
            agency = contract.get('agencyname', contract.get('agency', 'Unknown'))
            value = contract.get('Contract value', contract.get('contract value', 'Unknown'))

            print(f"  • {supplier}")
            print(f"    Agency: {agency}")
            print(f"    Value: {value}")
            print()

    print("="*80)
    print("✅ COMPLETE")
    print("="*80 + "\n")

    print("💡 What you have now:")
    print("  1. Supplier enrichment mapping (ABNs/ACNs extracted and matched)")
    print("  2. Full contracts with enriched supplier data")
    print("  3. Mount Isa specific contracts filtered\n")

    print("📈 Success rate:")
    with_id = mapping_df[['abn', 'acn']].notna().any(axis=1).sum()
    total = len(mapping_df)
    print(f"  {with_id:,} of {total:,} suppliers enriched ({with_id/total*100:.1f}%)\n")
