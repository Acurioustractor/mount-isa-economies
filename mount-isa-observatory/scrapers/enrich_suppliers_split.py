"""
Enhanced Smart Supplier Enrichment - Splits Multiple Suppliers
Handles the " / " separated supplier format in QLD contracts
"""
import pandas as pd
import re
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'

print("\n" + "="*80)
print("🎯 SMART SUPPLIER ENRICHMENT (SPLIT VERSION)")
print("="*80 + "\n")

def extract_abn_acn_from_text(text: str) -> dict:
    """Extract ABN or ACN numbers embedded in supplier names"""
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

def split_suppliers(supplier_text: str) -> list:
    """Split supplier column that contains multiple suppliers"""
    if not supplier_text or not isinstance(supplier_text, str):
        return []
    
    # Split on " / " or newlines
    suppliers = re.split(r'\s*/\s*|\n', supplier_text)
    
    # Clean and filter
    suppliers = [s.strip() for s in suppliers if s.strip()]
    
    return suppliers

def enrich_contracts(contracts_file: Path) -> tuple:
    """Enrich contract suppliers using multiple strategies"""
    print(f"📄 Loading contracts: {contracts_file.name}\n")
    
    df = pd.read_csv(contracts_file, low_memory=False)
    print(f"✅ Loaded {len(df):,} contracts\n")
    
    # Find supplier column
    supplier_cols = [col for col in df.columns if 'supplier' in col.lower()]
    if not supplier_cols:
        print("❌ No supplier column found")
        print(f"Available columns: {df.columns.tolist()}")
        return df, pd.DataFrame()
    
    supplier_col = supplier_cols[0]
    print(f"📋 Using supplier column: {supplier_col}\n")
    
    # Split and collect all unique suppliers
    all_suppliers = []
    for supplier_text in df[supplier_col].dropna():
        suppliers = split_suppliers(str(supplier_text))
        all_suppliers.extend(suppliers)
    
    unique_suppliers = list(set(all_suppliers))
    print(f"🔍 Found {len(unique_suppliers):,} unique suppliers (after splitting)\n")
    
    # Enrich each supplier
    enrichment_data = []
    
    print("🔧 Enriching suppliers using text extraction...\n")
    
    for supplier in tqdm(unique_suppliers, desc="Processing"):
        result = {
            'supplier_name_original': supplier,
            'abn': None,
            'acn': None,
            'match_method': None
        }
        
        # Extract from supplier name
        extracted = extract_abn_acn_from_text(str(supplier))
        if extracted:
            result.update(extracted)
            result['match_method'] = 'extracted_from_name'
        
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
    
    print(f"Total unique suppliers: {total:,}")
    print(f"With ABN: {with_abn:,} ({with_abn/total*100:.1f}%)")
    print(f"With ACN: {with_acn:,} ({with_acn/total*100:.1f}%)")
    print(f"With ABN or ACN: {with_either:,} ({with_either/total*100:.1f}%)\n")
    
    # Save mapping
    mapping_file = DATA_DIR / 'abn_lookup' / f'supplier_enrichment_split_{datetime.now().strftime("%Y%m%d")}.csv'
    mapping_file.parent.mkdir(parents=True, exist_ok=True)
    enrichment_df.to_csv(mapping_file, index=False)
    print(f"💾 Saved enrichment mapping: {mapping_file}\n")
    
    # Filter for Mount Isa suppliers
    mount_isa_keywords = ['mount isa', 'mount-isa', 'kalkadoon', '4825', 'miwb']
    
    mount_isa_suppliers = enrichment_df[
        enrichment_df['supplier_name_original'].str.contains(
            '|'.join(mount_isa_keywords), 
            case=False, 
            na=False
        )
    ]
    
    print(f"🏔️  Found {len(mount_isa_suppliers)} Mount Isa suppliers:\n")
    for _, supplier in mount_isa_suppliers.iterrows():
        print(f"  • {supplier['supplier_name_original']}")
        if supplier['abn']:
            print(f"    ABN: {supplier['abn']}")
        if supplier['acn']:
            print(f"    ACN: {supplier['acn']}")
    print()
    
    return enrichment_df

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python3 enrich_suppliers_split.py path/to/contracts.csv")
        sys.exit(1)
    
    contracts_file = Path(sys.argv[1])
    
    if not contracts_file.exists():
        print(f"❌ File not found: {contracts_file}")
        sys.exit(1)
    
    enrichment_df = enrich_contracts(contracts_file)
    
    print("="*80)
    print("✅ COMPLETE")
    print("="*80 + "\n")
