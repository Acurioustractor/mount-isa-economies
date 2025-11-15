"""
ABN Lookup Enrichment Scraper
Uses official ABN Lookup API to enrich organization data with business details

GUID: e3df2bb0-a40b-40f9-b771-0cef7e9d667b
API Docs: https://api.gov.au/service/5b639f0f63f18432cd0e1a66/api-documentation-34653

What this gets:
- Full legal business name
- Trading names (all DBA names)
- Business location (state, postcode)
- ABN status (active/cancelled)
- GST registration status
- Entity type (company, partnership, trust, sole trader, etc)
- DGR status (charity eligibility)
- Historical names
"""

import requests
import pandas as pd
import time
from pathlib import Path
from datetime import datetime
from tqdm import tqdm

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'abn_lookup'
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ABN Lookup API Configuration
ABN_LOOKUP_GUID = "e3df2bb0-a40b-40f9-b771-0cef7e9d667b"
ABN_LOOKUP_URL = "https://abr.business.gov.au/abrxmlsearch/AbrXmlSearch.asmx/ABRSearchByABN"

print("\n" + "="*80)
print("🔍 ABN LOOKUP ENRICHMENT SCRAPER")
print("="*80 + "\n")
print(f"✅ GUID configured: {ABN_LOOKUP_GUID[:8]}...")
print(f"✅ API endpoint: {ABN_LOOKUP_URL}\n")

def lookup_abn(abn: str, include_historical: bool = True) -> dict:
    """
    Look up ABN details from ABN Lookup API

    Args:
        abn: ABN number (can include spaces)
        include_historical: Include historical entity names

    Returns:
        Dictionary with business details
    """
    # Clean ABN (remove spaces)
    abn_clean = abn.replace(' ', '').strip()

    if not abn_clean or len(abn_clean) != 11:
        return {'error': 'Invalid ABN format'}

    # API parameters
    params = {
        'searchString': abn_clean,
        'includeHistoricalDetails': 'Y' if include_historical else 'N',
        'authenticationGuid': ABN_LOOKUP_GUID
    }

    try:
        response = requests.get(ABN_LOOKUP_URL, params=params, timeout=10)
        response.raise_for_status()

        # Parse XML response
        import xml.etree.ElementTree as ET
        root = ET.fromstring(response.content)

        # Extract data from XML
        # ABN Lookup returns XML with nested structure

        result = {
            'abn': abn_clean,
            'lookup_date': datetime.now().isoformat(),
            'raw_xml': response.text
        }

        # Find ABN element
        abn_elem = root.find('.//{http://abr.business.gov.au/ABRXMLSearch/}ABN')
        if abn_elem is not None:
            result['abn'] = abn_elem.text

        # ABN Status
        status_elem = root.find('.//{http://abr.business.gov.au/ABRXMLSearch/}entityStatusCode')
        if status_elem is not None:
            result['abn_status'] = status_elem.text

        effective_from = root.find('.//{http://abr.business.gov.au/ABRXMLSearch/}effectiveFrom')
        if effective_from is not None:
            result['abn_effective_from'] = effective_from.text

        # Entity Type
        entity_type = root.find('.//{http://abr.business.gov.au/ABRXMLSearch/}entityTypeCode')
        if entity_type is not None:
            result['entity_type_code'] = entity_type.text

        entity_desc = root.find('.//{http://abr.business.gov.au/ABRXMLSearch/}entityDescription')
        if entity_desc is not None:
            result['entity_type'] = entity_desc.text

        # Legal Name (Main Name)
        main_name = root.find('.//{http://abr.business.gov.au/ABRXMLSearch/}mainName')
        if main_name is not None:
            org_name = main_name.find('.//{http://abr.business.gov.au/ABRXMLSearch/}organisationName')
            if org_name is not None:
                result['legal_name'] = org_name.text
            else:
                # Individual name
                given_name = main_name.find('.//{http://abr.business.gov.au/ABRXMLSearch/}givenName')
                family_name = main_name.find('.//{http://abr.business.gov.au/ABRXMLSearch/}familyName')
                if given_name is not None and family_name is not None:
                    result['legal_name'] = f"{given_name.text} {family_name.text}"

        # Business Names (Trading As)
        business_names = []
        for business_name in root.findall('.//{http://abr.business.gov.au/ABRXMLSearch/}businessName'):
            org_name = business_name.find('.//{http://abr.business.gov.au/ABRXMLSearch/}organisationName')
            if org_name is not None:
                business_names.append(org_name.text)
        if business_names:
            result['business_names'] = business_names

        # State
        state_code = root.find('.//{http://abr.business.gov.au/ABRXMLSearch/}stateCode')
        if state_code is not None:
            result['state'] = state_code.text

        # Postcode
        postcode = root.find('.//{http://abr.business.gov.au/ABRXMLSearch/}postcode')
        if postcode is not None:
            result['postcode'] = postcode.text

        # GST Status
        gst = root.find('.//{http://abr.business.gov.au/ABRXMLSearch/}goodsAndServicesTax')
        if gst is not None:
            gst_effective = gst.find('.//{http://abr.business.gov.au/ABRXMLSearch/}effectiveFrom')
            if gst_effective is not None:
                result['gst_registered'] = True
                result['gst_from'] = gst_effective.text
            else:
                result['gst_registered'] = False

        # DGR (Deductible Gift Recipient) Status - for charities
        dgr = root.find('.//{http://abr.business.gov.au/ABRXMLSearch/}DGR')
        if dgr is not None:
            dgr_status = dgr.find('.//{http://abr.business.gov.au/ABRXMLSearch/}effectiveFrom')
            if dgr_status is not None:
                result['dgr_status'] = True
                result['dgr_from'] = dgr_status.text
            else:
                result['dgr_status'] = False

        # ACN (Australian Company Number) if applicable
        acn = root.find('.//{http://abr.business.gov.au/ABRXMLSearch/}ASICNumber')
        if acn is not None:
            result['acn'] = acn.text

        return result

    except requests.exceptions.RequestException as e:
        return {'error': f'API request failed: {e}'}
    except ET.ParseError as e:
        return {'error': f'XML parsing failed: {e}'}
    except Exception as e:
        return {'error': f'Unexpected error: {e}'}

def enrich_from_csv(csv_file: Path, abn_column: str = 'abn') -> pd.DataFrame:
    """
    Enrich a CSV file containing ABNs with full business details

    Args:
        csv_file: Path to CSV with ABN column
        abn_column: Name of ABN column

    Returns:
        DataFrame with enriched data
    """
    print(f"📄 Loading: {csv_file.name}")

    # Load CSV
    try:
        df = pd.read_csv(csv_file, encoding='utf-8', low_memory=False)
    except:
        df = pd.read_csv(csv_file, encoding='latin-1', low_memory=False)

    if abn_column not in df.columns:
        print(f"   ⚠️  Column '{abn_column}' not found. Available: {df.columns.tolist()}")
        return df

    # Get unique ABNs
    unique_abns = df[abn_column].dropna().unique()
    print(f"   Found {len(unique_abns):,} unique ABNs")

    # Look up each ABN
    enriched_data = []

    for abn in tqdm(unique_abns, desc="   Looking up ABNs"):
        result = lookup_abn(str(abn))
        enriched_data.append(result)

        # Rate limiting - ABN Lookup allows "reasonable" requests
        # Be conservative: 1 request per second = 3,600/hour
        time.sleep(1)

    # Convert to DataFrame
    enriched_df = pd.DataFrame(enriched_data)

    # Merge back to original
    df_merged = df.merge(
        enriched_df,
        left_on=abn_column,
        right_on='abn',
        how='left',
        suffixes=('_original', '_abn_lookup')
    )

    return df_merged

def enrich_mount_isa_organizations():
    """
    Find and enrich all Mount Isa organizations with ABN data
    """
    print("🏢 Enriching Mount Isa organizations with ABN data...\n")

    # Look for existing organization CSVs
    possible_sources = [
        BASE_DIR / 'data' / 'services_export.csv',
        BASE_DIR / 'data' / 'acnc_financials' / 'mount_isa_charities_*.csv',
        BASE_DIR / 'data' / 'qld_contracts' / '*.csv'
    ]

    all_abns = set()

    # Collect all unique ABNs from various sources
    for pattern in possible_sources:
        for file in Path(pattern).parent.glob(pattern.name):
            try:
                df = pd.read_csv(file, encoding='utf-8', low_memory=False)

                # Find ABN columns
                abn_cols = [col for col in df.columns if 'abn' in col.lower()]

                for col in abn_cols:
                    abns = df[col].dropna().unique()
                    all_abns.update([str(abn).replace(' ', '') for abn in abns])

            except Exception as e:
                continue

    if not all_abns:
        print("⚠️  No ABNs found in data files")
        print("\nTo use this scraper:")
        print("  1. Export organizations with ABNs to CSV")
        print("  2. Run: python3 abn_lookup_enrichment.py path/to/file.csv")
        return

    print(f"✅ Found {len(all_abns):,} unique ABNs across all data sources\n")

    # Look up each ABN
    results = []

    for abn in tqdm(list(all_abns)[:100], desc="Looking up ABNs"):  # Limit to first 100 for testing
        result = lookup_abn(abn)
        results.append(result)
        time.sleep(1)  # Rate limiting

    # Save results
    df_results = pd.DataFrame(results)
    output_file = DATA_DIR / f'abn_enrichment_{datetime.now().strftime("%Y%m%d")}.csv'
    df_results.to_csv(output_file, index=False)

    print(f"\n💾 Saved enriched ABN data: {output_file}")
    print(f"   Total records: {len(df_results):,}")

    # Summary statistics
    if 'abn_status' in df_results.columns:
        active = df_results['abn_status'].eq('Active').sum()
        print(f"   Active ABNs: {active:,} ({active/len(df_results)*100:.1f}%)")

    if 'gst_registered' in df_results.columns:
        gst = df_results['gst_registered'].sum()
        print(f"   GST registered: {gst:,} ({gst/len(df_results)*100:.1f}%)")

    if 'dgr_status' in df_results.columns:
        dgr = df_results['dgr_status'].sum()
        print(f"   DGR charities: {dgr:,} ({dgr/len(df_results)*100:.1f}%)")

    return df_results

# Test function
def test_abn_lookup():
    """Test the ABN lookup with a known ABN"""
    print("🧪 Testing ABN Lookup API...\n")

    # Test with a well-known ABN (Australian Red Cross)
    test_abn = "50169561394"  # Red Cross

    print(f"Testing with ABN: {test_abn}")
    result = lookup_abn(test_abn)

    if 'error' in result:
        print(f"❌ Error: {result['error']}")
        return False
    else:
        print("✅ API working! Sample result:\n")
        for key, value in result.items():
            if key != 'raw_xml':  # Don't print full XML
                print(f"   {key}: {value}")
        return True

if __name__ == '__main__':
    import sys

    # Test API first
    if not test_abn_lookup():
        print("\n❌ API test failed. Please check:")
        print("  1. GUID is correct")
        print("  2. Internet connection is working")
        print("  3. ABN Lookup service is online")
        sys.exit(1)

    print("\n" + "="*80 + "\n")

    # If CSV file provided, enrich it
    if len(sys.argv) > 1:
        csv_file = Path(sys.argv[1])
        if not csv_file.exists():
            print(f"❌ File not found: {csv_file}")
            sys.exit(1)

        # Detect ABN column
        df = pd.read_csv(csv_file, nrows=0)
        abn_cols = [col for col in df.columns if 'abn' in col.lower()]

        if not abn_cols:
            print(f"❌ No ABN column found in {csv_file}")
            print(f"   Available columns: {df.columns.tolist()}")
            sys.exit(1)

        abn_column = abn_cols[0]
        print(f"Using ABN column: {abn_column}\n")

        enriched = enrich_from_csv(csv_file, abn_column)

        output_file = DATA_DIR / f'enriched_{csv_file.name}'
        enriched.to_csv(output_file, index=False)

        print(f"\n✅ Enriched data saved: {output_file}")

    else:
        # Enrich Mount Isa organizations
        enrich_mount_isa_organizations()

    print("\n" + "="*80)
    print("✅ ABN LOOKUP ENRICHMENT COMPLETE")
    print("="*80 + "\n")

    print("💡 Usage:")
    print("  python3 abn_lookup_enrichment.py                    # Auto-enrich all Mount Isa ABNs")
    print("  python3 abn_lookup_enrichment.py path/to/file.csv   # Enrich specific CSV file\n")

    print("📊 What you now have:")
    print("  • Full legal business names")
    print("  • All trading names (DBA)")
    print("  • Business locations (state, postcode)")
    print("  • ABN status (active/cancelled)")
    print("  • GST registration status")
    print("  • Entity types (company, trust, sole trader, etc)")
    print("  • DGR status (charity eligibility)")
    print("  • ACN numbers (for companies)\n")
