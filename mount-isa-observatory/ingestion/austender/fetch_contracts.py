"""
AusTender OCDS API Ingestion
Fetches Commonwealth procurement contracts for Mount Isa suppliers
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from datetime import datetime, timedelta
from base_ingestion import BaseIngestion


class AusTenderIngestion(BaseIngestion):
    """Fetch AusTender contract data for Mount Isa suppliers"""

    def __init__(self):
        super().__init__("austender")
        self.api_base = self.config['data_sources']['austender']['ocds_api']
        self.postcode = self.config['geography']['postcode']

    def fetch_contracts_by_supplier_location(self, start_date: str = None, end_date: str = None):
        """
        Fetch contracts where supplier is in Mount Isa (postcode 4825)

        Args:
            start_date: Start date in YYYY-MM-DD format (default: 5 years ago)
            end_date: End date in YYYY-MM-DD format (default: today)
        """
        if start_date is None:
            start_date = (datetime.now() - timedelta(days=365*5)).strftime("%Y-%m-%d")
        if end_date is None:
            end_date = datetime.now().strftime("%Y-%m-%d")

        self.logger.info(f"Fetching contracts for postcode {self.postcode} from {start_date} to {end_date}")

        # Note: The actual AusTender API endpoint structure
        # Based on the OCDS spec, we would query the releases endpoint
        contracts = []

        try:
            # Build query parameters
            # The actual API might use different parameter names
            params = {
                'supplierPostcode': self.postcode,
                'publishedFrom': start_date,
                'publishedTo': end_date,
                'limit': 100  # Pagination
            }

            url = f"{self.api_base}{self.config['data_sources']['austender']['search_endpoint']}"

            # Note: This is a simplified example
            # Real implementation would need to handle pagination
            page = 1
            has_more = True

            while has_more:
                params['page'] = page

                self.logger.info(f"Fetching page {page}...")

                try:
                    response = self.fetch_data(url, params=params)
                    data = response.json()

                    # OCDS structure typically has releases array
                    if 'releases' in data and len(data['releases']) > 0:
                        contracts.extend(data['releases'])
                        page += 1

                        # Check if more pages exist
                        if len(data['releases']) < params['limit']:
                            has_more = False
                    else:
                        has_more = False

                except Exception as e:
                    self.logger.error(f"Error fetching page {page}: {e}")
                    self.logger.info("Note: AusTender API may require registration or have different endpoint structure")
                    self.logger.info("Please verify API access at: https://www.tenders.gov.au")
                    has_more = False

        except Exception as e:
            self.logger.error(f"Error in AusTender ingestion: {e}")
            self.logger.info("For manual approach, visit AusTender search and filter by postcode 4825")

        return contracts

    def parse_ocds_contracts(self, contracts: list) -> pd.DataFrame:
        """Parse OCDS format contracts into flat DataFrame"""
        records = []

        for contract in contracts:
            try:
                # Extract key fields from OCDS structure
                record = {
                    'cn_id': contract.get('id'),
                    'publish_date': contract.get('date'),
                    'contract_value': self._extract_value(contract),
                    'supplier_abn': self._extract_supplier_abn(contract),
                    'supplier_name': self._extract_supplier_name(contract),
                    'supplier_postcode': self._extract_supplier_postcode(contract),
                    'buyer_name': self._extract_buyer_name(contract),
                    'contract_description': self._extract_description(contract),
                    'source_url': contract.get('url', ''),
                    'fetch_timestamp': datetime.now()
                }

                records.append(record)

            except Exception as e:
                self.logger.warning(f"Error parsing contract {contract.get('id')}: {e}")
                continue

        df = pd.DataFrame(records)
        return df

    def _extract_value(self, contract: dict) -> float:
        """Extract contract value from OCDS structure"""
        try:
            if 'contracts' in contract:
                return float(contract['contracts'][0].get('value', {}).get('amount', 0))
        except:
            pass
        return None

    def _extract_supplier_abn(self, contract: dict) -> str:
        """Extract supplier ABN"""
        try:
            if 'awards' in contract:
                suppliers = contract['awards'][0].get('suppliers', [])
                if suppliers:
                    return suppliers[0].get('identifier', {}).get('id', '')
        except:
            pass
        return None

    def _extract_supplier_name(self, contract: dict) -> str:
        """Extract supplier name"""
        try:
            if 'awards' in contract:
                suppliers = contract['awards'][0].get('suppliers', [])
                if suppliers:
                    return suppliers[0].get('name', '')
        except:
            pass
        return None

    def _extract_supplier_postcode(self, contract: dict) -> str:
        """Extract supplier postcode"""
        try:
            if 'awards' in contract:
                suppliers = contract['awards'][0].get('suppliers', [])
                if suppliers:
                    address = suppliers[0].get('address', {})
                    return address.get('postalCode', '')
        except:
            pass
        return None

    def _extract_buyer_name(self, contract: dict) -> str:
        """Extract buyer/agency name"""
        try:
            return contract.get('buyer', {}).get('name', '')
        except:
            pass
        return None

    def _extract_description(self, contract: dict) -> str:
        """Extract contract description"""
        try:
            return contract.get('tender', {}).get('description', '')
        except:
            pass
        return None

    def run(self, start_date: str = None, end_date: str = None):
        """Main execution method"""
        self.logger.info("Starting AusTender ingestion")

        # Fetch contracts
        contracts = self.fetch_contracts_by_supplier_location(start_date, end_date)

        if contracts:
            # Parse to DataFrame
            df = self.parse_ocds_contracts(contracts)

            if len(df) > 0:
                # Validate data
                required_cols = ['cn_id', 'supplier_name', 'supplier_postcode']
                if self.validate_data(df, required_cols):
                    # Save raw data
                    filepath = self.save_raw_data(df, "austender_contracts", format='csv')

                    # Record provenance
                    self.record_provenance(
                        source_url=self.api_base,
                        filepath=filepath,
                        record_count=len(df),
                        licence="CC BY 4.0"
                    )

                    self.logger.info(f"AusTender ingestion completed: {len(df)} contracts")
                    return df

        self.logger.warning("No contracts fetched - API may require registration or manual download")
        return None


if __name__ == "__main__":
    ingestion = AusTenderIngestion()
    ingestion.run()
