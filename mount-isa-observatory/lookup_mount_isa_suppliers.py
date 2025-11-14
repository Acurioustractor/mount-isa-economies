import requests
import xml.etree.ElementTree as ET

ABN_LOOKUP_GUID = "e3df2bb0-a40b-40f9-b771-0cef7e9d667b"
ABN_SEARCH_URL = "https://abr.business.gov.au/abrxmlsearch/AbrXmlSearch.asmx/ABRSearchByName"

suppliers = [
    "Meteor Car & Truck Rentals",
    "New Nation Enterprise",
    "CNW PTY LTD",
    "HGW Consulting"
]

print("\n🔍 Looking up ABNs for Mount Isa suppliers...\n")

for supplier in suppliers:
    params = {
        'name': supplier,
        'authenticationGuid': ABN_LOOKUP_GUID,
        'searchWidth': 'typical',
        'minimumScore': '50',
        'stateCode': 'QLD'
    }
    
    try:
        response = requests.get(ABN_SEARCH_URL, params=params, timeout=10)
        
        if response.status_code == 200:
            root = ET.fromstring(response.content)
            
            found = False
            for item in root.findall('.//{http://abr.business.gov.au/ABRXMLSearch/}searchResultsRecord'):
                abn_elem = item.find('.//{http://abr.business.gov.au/ABRXMLSearch/}ABN')
                name_elem = item.find('.//{http://abr.business.gov.au/ABRXMLSearch/}mainName')
                
                if abn_elem is not None and name_elem is not None:
                    abn_value = abn_elem.find('.//{http://abr.business.gov.au/ABRXMLSearch/}identifierValue')
                    org_name = name_elem.find('.//{http://abr.business.gov.au/ABRXMLSearch/}organisationName')
                    
                    if abn_value is not None and org_name is not None:
                        print(f"✅ {supplier}")
                        print(f"   ABN: {abn_value.text}")
                        print(f"   Legal Name: {org_name.text}")
                        print()
                        found = True
                        break
            
            if not found:
                print(f"⚠️  {supplier} - No ABN found")
                print()
        else:
            print(f"⚠️  {supplier} - API error: {response.status_code}")
            print()
            
    except Exception as e:
        print(f"⚠️  {supplier} - Error: {str(e)[:50]}")
        print()

print("✅ Done!")
