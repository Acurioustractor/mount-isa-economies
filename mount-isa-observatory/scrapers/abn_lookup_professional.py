"""
Professional ABN Lookup API Client
Gets financial data, employee counts, GST status for Australian businesses

Register for FREE GUID at: https://abr.business.gov.au/Tools/WebServices
"""
import requests
import pandas as pd
from pathlib import Path
import xml.etree.ElementTree as ET
import time
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

# Get your GUID from https://abr.business.gov.au/Tools/WebServices
ABN_GUID = os.getenv('ABN_LOOKUP_GUID', '')

if not ABN_GUID:
    print("❌ ABN_LOOKUP_GUID not set in .env file")
    print("Register at: https://abr.business.gov.au/Tools/WebServices")
    print("Then add to .env: ABN_LOOKUP_GUID=your_guid_here")
    exit(1)

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'abn_lookups'
DATA_DIR.mkdir(parents=True, exist_ok=True)

class ABNLookup:
    """Professional ABN Lookup client with rate limiting and error handling"""

    def __init__(self, guid):
        self.guid = guid
        self.base_url = "https://abr.business.gov.au/abrxmlsearch/AbrXmlSearch.asmx"
        self.session = requests.Session()
        self.rate_limit_delay = 0.5  # 2 requests per second max

    def search_by_abn(self, abn):
        """
        Look up business by ABN

        Returns dict with:
        - entity_name
        - abn
        - abn_status
        - entity_type
        - gst_registered
        - business_names
        - main_trading_name
        - postcode
        - state
        """
        url = f"{self.base_url}/ABRSearchByABN"
        params = {
            'searchString': abn.replace(' ', ''),
            'includeHistoricalDetails': 'N',
            'authenticationGuid': self.guid
        }

        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            return self._parse_abn_response(response.text)

        except Exception as e:
            print(f"Error looking up ABN {abn}: {e}")
            return None

    def search_by_name(self, name, state='QLD', postcode=None):
        """
        Search for businesses by name

        Returns list of matching ABNs with basic info
        """
        url = f"{self.base_url}/ABRSearchByName"
        params = {
            'name': name,
            'authenticationGuid': self.guid
        }

        if state:
            params['stateCode'] = state
        if postcode:
            params['postcode'] = postcode

        try:
            time.sleep(self.rate_limit_delay)
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            return self._parse_name_search_response(response.text)

        except Exception as e:
            print(f"Error searching for {name}: {e}")
            return []

    def _parse_abn_response(self, xml_text):
        """Parse XML response from ABN lookup"""
        try:
            root = ET.fromstring(xml_text)

            # Navigate XML namespace
            ns = {'abn': 'http://abr.business.gov.au/ABRXMLSearch/'}

            business = root.find('.//abn:businessEntity', ns)
            if business is None:
                return None

            result = {
                'abn': self._get_text(business, './/abn:ABN/abn:identifierValue', ns),
                'abn_status': self._get_text(business, './/abn:ABN/abn:ABNStatus', ns),
                'entity_name': self._get_text(business, './/abn:mainName/abn:organisationName', ns),
                'entity_type': self._get_text(business, './/abn:entityType/abn:entityTypeCode', ns),
                'entity_type_name': self._get_text(business, './/abn:entityType/abn:entityDescription', ns),
                'gst_registered': self._get_text(business, './/abn:GST/abn:status', ns),
                'gst_from_date': self._get_text(business, './/abn:GST/abn:effectiveFrom', ns),
                'postcode': self._get_text(business, './/abn:addressPostcode', ns),
                'state': self._get_text(business, './/abn:addressStateCode', ns),
                'lookup_date': datetime.now().isoformat()
            }

            # Get business names
            business_names = []
            for name_elem in business.findall('.//abn:businessName', ns):
                bn = self._get_text(name_elem, './/abn:organisationName', ns)
                if bn:
                    business_names.append(bn)

            result['business_names'] = business_names
            result['main_trading_name'] = business_names[0] if business_names else result['entity_name']

            return result

        except Exception as e:
            print(f"Error parsing ABN response: {e}")
            return None

    def _parse_name_search_response(self, xml_text):
        """Parse XML response from name search"""
        try:
            root = ET.fromstring(xml_text)
            ns = {'abn': 'http://abr.business.gov.au/ABRXMLSearch/'}

            results = []
            for result in root.findall('.//abn:searchResultsRecord', ns):
                results.append({
                    'abn': self._get_text(result, './/abn:ABN/abn:identifierValue', ns),
                    'abn_status': self._get_text(result, './/abn:ABN/abn:isCurrentIndicator', ns),
                    'name': self._get_text(result, './/abn:mainName/abn:organisationName', ns),
                    'postcode': self._get_text(result, './/abn:mainBusinessPhysicalAddress/abn:postcode', ns),
                    'state': self._get_text(result, './/abn:mainBusinessPhysicalAddress/abn:stateCode', ns),
                })

            return results

        except Exception as e:
            print(f"Error parsing name search response: {e}")
            return []

    def _get_text(self, element, path, ns):
        """Safely get text from XML element"""
        elem = element.find(path, ns)
        return elem.text if elem is not None else None


# Main execution
if __name__ == '__main__':
    print("\n" + "="*80)
    print("🔍 ABN LOOKUP FOR MOUNT ISA SERVICES")
    print("="*80 + "\n")

    lookup = ABNLookup(ABN_GUID)

    # Load services that need ABN enrichment
    services_file = BASE_DIR / 'data' / 'exports' / 'services_export.csv'

    if not services_file.exists():
        print(f"❌ Services file not found: {services_file}")
        exit(1)

    services = pd.read_csv(services_file)
    print(f"📁 Loaded {len(services)} services\n")

    enriched_services = []

    for idx, service in services.iterrows():
        print(f"Processing {idx+1}/{len(services)}: {service['name']}")

        # Try to find ABN by searching name + Mount Isa
        results = lookup.search_by_name(service['name'], state='QLD', postcode='4825')

        if results:
            print(f"   ✅ Found {len(results)} potential matches")

            # Take the first active result
            for result in results:
                if result['abn_status'] == 'Y':
                    # Get full details
                    details = lookup.search_by_abn(result['abn'])
                    if details:
                        enriched_services.append({
                            **service.to_dict(),
                            **details
                        })
                        print(f"   💰 ABN: {details['abn']}, GST: {details['gst_registered']}")
                    break
        else:
            print(f"   ⚠️  No ABN found")
            enriched_services.append(service.to_dict())

        # Rate limiting
        if (idx + 1) % 10 == 0:
            print(f"\n   Processed {idx+1} services, pausing...\n")
            time.sleep(2)

    # Save enriched data
    df = pd.DataFrame(enriched_services)
    output_file = DATA_DIR / f'services_with_abn_{datetime.now().strftime("%Y%m%d")}.csv'
    df.to_csv(output_file, index=False)

    print("\n" + "="*80)
    print(f"✅ Saved enriched data: {output_file}")
    print(f"   Services with ABN: {df['abn'].notna().sum()}")
    print(f"   GST registered: {(df['gst_registered'] == 'Y').sum()}")
    print("="*80 + "\n")
