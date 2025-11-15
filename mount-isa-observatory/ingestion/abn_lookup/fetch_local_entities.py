"""
ABN Lookup API Ingestion
Fetches and resolves local business entities in Mount Isa
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import os
import pandas as pd
import requests
import time
from base_ingestion import BaseIngestion


class ABNLookupIngestion(BaseIngestion):
    """Fetch ABN data for Mount Isa businesses"""

    def __init__(self):
        super().__init__("abn_lookup")
        self.api_url = self.config['data_sources']['abn_lookup']['json_api']
        self.guid = os.getenv('ABN_LOOKUP_GUID')
        self.postcode = self.config['geography']['postcode']
        self.locality = "Mount Isa"

        if not self.guid:
            self.logger.warning("ABN_LOOKUP_GUID not set in environment variables")
            self.logger.info("Register for GUID at: https://abr.business.gov.au/Tools/WebServices")

    def search_by_locality(self, locality: str = None, postcode: str = None):
        """
        Search for businesses by locality and postcode

        Args:
            locality: Suburb/town name (default: Mount Isa)
            postcode: Postcode (default: 4825)
        """
        if locality is None:
            locality = self.locality
        if postcode is None:
            postcode = self.postcode

        if not self.guid:
            self.logger.error("Cannot search without ABN_LOOKUP_GUID")
            return []

        self.logger.info(f"Searching ABN Lookup for businesses in {locality}, {postcode}")

        entities = []

        try:
            # ABN Lookup JSON API endpoint structure
            # Note: The actual endpoint structure may vary
            url = f"{self.api_url}ABRSearchByNameAdvanced.aspx"

            params = {
                'guid': self.guid,
                'name': '',  # Empty to get all
                'postcode': postcode,
                'legalName': '',
                'tradingName': '',
                'NSW': 'N',
                'SA': 'N',
                'ACT': 'N',
                'VIC': 'N',
                'WA': 'N',
                'NT': 'N',
                'QLD': 'Y',  # Queensland only
                'TAS': 'N',
                'activeABNs': 'Y',
                'currentGroundTruthABNs': 'Y',
                'callback': 'callback'
            }

            # Rate limiting - respect API limits
            time.sleep(1)

            response = self.fetch_data(url, params=params)
            data = response.json()

            # Parse response
            if 'Names' in data:
                for item in data['Names']:
                    entity = {
                        'abn': item.get('Abn'),
                        'entity_name': item.get('Name'),
                        'entity_type': item.get('EntityTypeCode'),
                        'postcode': item.get('Postcode'),
                        'state': item.get('StateCode'),
                        'status': item.get('Status'),
                        'fetch_timestamp': pd.Timestamp.now()
                    }
                    entities.append(entity)

            self.logger.info(f"Found {len(entities)} entities")

        except Exception as e:
            self.logger.error(f"Error searching ABN Lookup: {e}")
            self.logger.info("Note: ABN Lookup requires GUID registration and has rate limits")

        return entities

    def get_abn_details(self, abn: str):
        """
        Get detailed information for a specific ABN

        Args:
            abn: The ABN to lookup
        """
        if not self.guid:
            self.logger.error("Cannot lookup ABN without ABN_LOOKUP_GUID")
            return None

        self.logger.info(f"Looking up details for ABN: {abn}")

        try:
            url = f"{self.api_url}SearchByABN.aspx"

            params = {
                'guid': self.guid,
                'abn': abn.replace(' ', ''),
                'callback': 'callback'
            }

            # Rate limiting
            time.sleep(0.5)

            response = self.fetch_data(url, params=params)
            data = response.json()

            if 'Abn' in data:
                details = {
                    'abn': data.get('Abn'),
                    'acn': data.get('Acn'),
                    'entity_name': data.get('EntityName'),
                    'entity_type': data.get('EntityTypeName'),
                    'trading_name': data.get('BusinessName', [{}])[0].get('Name') if data.get('BusinessName') else None,
                    'main_business_location': data.get('MainBusinessPhysicalAddress', {}).get('Postcode'),
                    'postcode': data.get('MainBusinessPhysicalAddress', {}).get('Postcode'),
                    'state': data.get('MainBusinessPhysicalAddress', {}).get('StateCode'),
                    'gst_registered': data.get('Gst') is not None,
                    'status': data.get('EntityStatus', {}).get('EntityStatusCode')
                }

                return details

        except Exception as e:
            self.logger.error(f"Error looking up ABN {abn}: {e}")

        return None

    def enrich_entity_list(self, abns: list) -> pd.DataFrame:
        """
        Enrich a list of ABNs with detailed information

        Args:
            abns: List of ABN strings
        """
        self.logger.info(f"Enriching {len(abns)} ABNs with detailed information")

        entities = []

        for i, abn in enumerate(abns):
            if (i + 1) % 10 == 0:
                self.logger.info(f"Processed {i + 1}/{len(abns)} ABNs")

            details = self.get_abn_details(abn)
            if details:
                entities.append(details)

            # Rate limiting - max ~60 requests per minute
            time.sleep(1)

        df = pd.DataFrame(entities)
        return df

    def run(self):
        """Main execution method"""
        self.logger.info("Starting ABN Lookup ingestion")

        # Search for local entities
        entities = self.search_by_locality()

        if entities:
            df = pd.DataFrame(entities)

            # Save raw search results
            filepath = self.save_raw_data(df, "abn_search_mount_isa", format='csv')

            # Record provenance
            self.record_provenance(
                source_url=self.api_url,
                filepath=filepath,
                record_count=len(df),
                licence="ABN Lookup Terms of Use"
            )

            self.logger.info(f"ABN Lookup ingestion completed: {len(df)} entities")
            return df
        else:
            self.logger.warning("No entities fetched - check GUID configuration")
            return None


if __name__ == "__main__":
    ingestion = ABNLookupIngestion()
    ingestion.run()
