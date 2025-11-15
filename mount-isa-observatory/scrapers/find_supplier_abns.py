"""
Find ABNs for contract suppliers by searching ABN Lookup by name
"""
import requests
import pandas as pd
import xml.etree.ElementTree as ET
from pathlib import Path
from datetime import datetime
from tqdm import tqdm
import time

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'abn_lookup'
DATA_DIR.mkdir(parents=True, exist_ok=True)

ABN_LOOKUP_GUID = "e3df2bb0-a40b-40f9-b771-0cef7e9d667b"
ABN_SEARCH_BY_NAME_URL = "https://abr.business.gov.au/abrxmlsearch/AbrXmlSearch.asmx/ABRSearchByName"

print("\n" + "="*80)
print("🔍 FIND ABNs FOR CONTRACT SUPPLIERS")
print("="*80 + "\n")

def search_abn_by_name(business_name: str, state: str = None) -> list:
    """
    Search for ABNs by business name

    Args:
        business_name: Name to search for
        state: Optional state filter (QLD, NSW, etc)

    Returns:
        List of matching ABNs with details
    """
    if not business_name or len(business_name) < 3:
        return []

    params = {
        'name': business_name,
        'authenticationGuid': ABN_LOOKUP_GUID,
        'searchWidth': 'typical',  # typical, narrow, wide
        'minimumScore': '50'  # 0-100, higher = stricter matching
    }

    if state:
        params['stateCode'] = state

    try:
        response = requests.get(ABN_SEARCH_BY_NAME_URL, params=params, timeout=10)
        response.raise_for_status()

        root = ET.fromstring(response.content)

        results = []

        # Find all search result items
        for item in root.findall('.//{http://abr.business.gov.au/ABRXMLSearch/}searchResultsRecord'):
            result = {}

            # ABN
            abn_elem = item.find('.//{http://abr.business.gov.au/ABRXMLSearch/}ABN')
            if abn_elem is not None:
                abn_text = abn_elem.find('.//{http://abr.business.gov.au/ABRXMLSearch/}identifierValue')
                if abn_text is not None:
                    result['abn'] = abn_text.text

            # Business name
            main_name = item.find('.//{http://abr.business.gov.au/ABRXMLSearch/}mainName')
            if main_name is not None:
                org_name = main_name.find('.//{http://abr.business.gov.au/ABRXMLSearch/}organisationName')
                if org_name is not None:
                    result['business_name'] = org_name.text

            # Trading names
            trading_names = []
            for name_elem in item.findall('.//{http://abr.business.gov.au/ABRXMLSearch/}mainTradingName'):
                org_name = name_elem.find('.//{http://abr.business.gov.au/ABRXMLSearch/}organisationName')
                if org_name is not None:
                    trading_names.append(org_name.text)
            if trading_names:
                result['trading_names'] = trading_names

            # State
            state_elem = item.find('.//{http://abr.business.gov.au/ABRXMLSearch/}stateCode')
            if state_elem is not None:
                result['state'] = state_elem.text

            # Postcode
            postcode_elem = item.find('.//{http://abr.business.gov.au/ABRXMLSearch/}postcode')
            if postcode_elem is not None:
                result['postcode'] = postcode_elem.text

            # ABN Status
            status_elem = item.find('.//{http://abr.business.gov.au/ABRXMLSearch/}ABNStatusCode')
            if status_elem is not None:
                result['abn_status'] = status_elem.text

            # Score
            score_elem = item.find('.//{http://abr.business.gov.au/ABRXMLSearch/}score')
            if score_elem is not None:
                result['match_score'] = score_elem.text

            if 'abn' in result:
                results.append(result)

        return results

    except Exception as e:
        print(f"Error searching for '{business_name}': {e}")
        return []

def find_abns_for_suppliers(csv_file: Path) -> pd.DataFrame:
    """
    Find ABNs for all suppliers in contracts CSV
    """
    print(f"📄 Loading contracts: {csv_file.name}\n")

    df = pd.read_csv(csv_file, low_memory=False)

    print(f"✅ Loaded {len(df):,} contracts\n")

    # Find supplier name columns
    supplier_cols = [col for col in df.columns if 'supplier' in col.lower() and 'name' in col.lower()]

    if not supplier_cols:
        print("❌ No supplier name column found")
        print(f"Available columns: {df.columns.tolist()}")
        return df

    supplier_col = supplier_cols[0]
    print(f"📋 Using supplier column: {supplier_col}\n")

    # Get unique supplier names
    unique_suppliers = df[supplier_col].dropna().unique()
    print(f"🔍 Found {len(unique_suppliers):,} unique suppliers\n")
    print(f"⏱️  Estimated time: ~{len(unique_suppliers)} seconds (1 request/sec)\n")

    # Search for ABNs
    supplier_abns = {}

    for supplier in tqdm(unique_suppliers[:100], desc="Searching for ABNs"):  # Limit to first 100 for testing
        # Clean supplier name
        supplier_clean = str(supplier).strip()

        # Search (prioritize QLD businesses)
        results = search_abn_by_name(supplier_clean, state='QLD')

        if results:
            # Take the best match (highest score)
            best_match = max(results, key=lambda x: int(x.get('match_score', 0)))
            supplier_abns[supplier] = best_match
        else:
            # Try without state filter
            results = search_abn_by_name(supplier_clean)
            if results:
                best_match = max(results, key=lambda x: int(x.get('match_score', 0)))
                supplier_abns[supplier] = best_match

        time.sleep(1)  # Rate limiting

    print(f"\n✅ Found ABNs for {len(supplier_abns):,} suppliers\n")

    # Create mapping dataframe
    abn_data = []
    for supplier, abn_info in supplier_abns.items():
        abn_data.append({
            'supplier_name_original': supplier,
            'abn': abn_info.get('abn'),
            'business_name': abn_info.get('business_name'),
            'trading_names': ', '.join(abn_info.get('trading_names', [])),
            'state': abn_info.get('state'),
            'postcode': abn_info.get('postcode'),
            'abn_status': abn_info.get('abn_status'),
            'match_score': abn_info.get('match_score')
        })

    supplier_abn_df = pd.DataFrame(abn_data)

    # Save supplier ABN mapping
    mapping_file = DATA_DIR / f'supplier_abn_mapping_{datetime.now().strftime("%Y%m%d")}.csv'
    supplier_abn_df.to_csv(mapping_file, index=False)
    print(f"💾 Saved supplier→ABN mapping: {mapping_file}\n")

    # Merge back to contracts
    df_enriched = df.merge(
        supplier_abn_df,
        left_on=supplier_col,
        right_on='supplier_name_original',
        how='left',
        suffixes=('', '_abn_lookup')
    )

    return df_enriched, supplier_abn_df

if __name__ == '__main__':
    import sys

    if len(sys.argv) < 2:
        print("Usage: python3 find_supplier_abns.py path/to/contracts.csv")
        sys.exit(1)

    csv_file = Path(sys.argv[1])

    if not csv_file.exists():
        print(f"❌ File not found: {csv_file}")
        sys.exit(1)

    enriched_df, mapping_df = find_abns_for_suppliers(csv_file)

    # Save enriched contracts
    output_file = DATA_DIR / f'contracts_with_abns_{datetime.now().strftime("%Y%m%d")}.csv'
    enriched_df.to_csv(output_file, index=False)

    print(f"💾 Saved enriched contracts: {output_file}\n")

    print("="*80)
    print("✅ COMPLETE")
    print("="*80 + "\n")

    print("📊 Summary:")
    print(f"   Total contracts: {len(enriched_df):,}")
    print(f"   Suppliers with ABNs: {mapping_df['abn'].notna().sum():,}")
    print(f"   Match rate: {mapping_df['abn'].notna().sum() / len(mapping_df) * 100:.1f}%\n")

    print("💡 Next steps:")
    print("  1. Review supplier_abn_mapping CSV for accuracy")
    print("  2. Use ABNs to enrich with full business details")
    print("  3. Link contracts to organizations in database\n")
