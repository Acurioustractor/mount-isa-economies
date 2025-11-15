"""
Use ABN Lookup API to find ABNs for suppliers that don't have them
Uses the approved GUID: e3df2bb0-a40b-40f9-b771-0cef7e9d667b
"""
import pandas as pd
import requests
import xml.etree.ElementTree as ET
from pathlib import Path
from tqdm import tqdm
import time

ABN_LOOKUP_GUID = "e3df2bb0-a40b-40f9-b771-0cef7e9d667b"
ABN_SEARCH_URL = "https://abr.business.gov.au/abrxmlsearch/AbrXmlSearch.asmx/ABRSearchByName"

def search_abn_by_name(name: str) -> dict:
    """Search ABN Lookup by name"""
    params = {
        'name': name,
        'authenticationGuid': ABN_LOOKUP_GUID,
        'searchWidth': 'typical',
        'minimumScore': '60',
        'stateCode': 'QLD'
    }
    
    try:
        response = requests.get(ABN_SEARCH_URL, params=params, timeout=10)
        if response.status_code != 200:
            return None
        
        root = ET.fromstring(response.content)
        
        # Get first result
        for item in root.findall('.//{http://abr.business.gov.au/ABRXMLSearch/}searchResultsRecord'):
            abn_elem = item.find('.//{http://abr.business.gov.au/ABRXMLSearch/}ABN')
            if abn_elem is not None:
                abn_value = abn_elem.find('.//{http://abr.business.gov.au/ABRXMLSearch/}identifierValue')
                if abn_value is not None:
                    return {'abn': abn_value.text}
        
        return None
        
    except Exception as e:
        return None

# Load the enrichment file
enrichment_file = Path('data/abn_lookup/supplier_enrichment_split_20251114.csv')
df = pd.read_csv(enrichment_file)

print(f"\n📊 Total suppliers: {len(df):,}")

# Filter for Mount Isa suppliers without ABNs
mount_isa_suppliers = df[
    df['supplier_name_original'].str.contains('mount isa|kalkadoon|4825', case=False, na=False)
]

print(f"🏔️  Mount Isa suppliers: {len(mount_isa_suppliers)}")

# Get suppliers without ABNs
missing_abns = mount_isa_suppliers[mount_isa_suppliers['abn'].isna()]

print(f"🔍 Mount Isa suppliers needing ABN lookup: {len(missing_abns)}\n")

if len(missing_abns) > 0:
    print("Looking up ABNs...\n")
    
    for idx, row in missing_abns.iterrows():
        supplier_name = row['supplier_name_original']
        print(f"  Searching: {supplier_name}")
        
        result = search_abn_by_name(supplier_name)
        
        if result and result.get('abn'):
            print(f"  ✅ Found ABN: {result['abn']}")
            df.loc[idx, 'abn'] = result['abn']
            df.loc[idx, 'match_method'] = 'abn_lookup_api'
        else:
            print(f"  ⚠️  No ABN found")
        
        time.sleep(1)  # Rate limiting
        print()
    
    # Save updated file
    df.to_csv(enrichment_file, index=False)
    print(f"\n💾 Updated: {enrichment_file}")

print("\n✅ Done!")
