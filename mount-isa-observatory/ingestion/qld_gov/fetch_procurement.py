"""
Queensland Government Procurement Ingestion
Fetches QLD procurement data via CKAN API (FPP and awarded contracts)
"""
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import pandas as pd
from ckanapi import RemoteCKAN
from base_ingestion import BaseIngestion


class QLDProcurementIngestion(BaseIngestion):
    """Fetch Queensland Government procurement data"""

    def __init__(self):
        super().__init__("qld_procurement")
        self.ckan_url = "https://data.qld.gov.au"
        self.ckan = RemoteCKAN(self.ckan_url)

        # Package IDs from config
        self.fpp_package = self.config['data_sources']['qld_gov']['fpp_package']
        self.contracts_package = self.config['data_sources']['qld_gov']['contracts_package']

    def fetch_forward_procurement_pipeline(self):
        """Fetch Forward Procurement Pipeline (FPP) data"""
        self.logger.info("Fetching QLD Forward Procurement Pipeline data")

        try:
            # Get package metadata
            package = self.ckan.action.package_show(id=self.fpp_package)

            self.logger.info(f"Package: {package['title']}")
            self.logger.info(f"Resources: {len(package['resources'])}")

            # Get the latest CSV resource
            csv_resources = [r for r in package['resources']
                           if r['format'].upper() == 'CSV']

            if not csv_resources:
                self.logger.warning("No CSV resources found in FPP package")
                return None

            # Use the first CSV (or most recent)
            resource = csv_resources[0]
            resource_url = resource['url']

            self.logger.info(f"Downloading from: {resource_url}")

            # Download CSV
            df = pd.read_csv(resource_url)

            self.logger.info(f"Downloaded {len(df)} FPP records")

            # Filter for North West Queensland / Mount Isa region
            # This would depend on how regions are coded in the data
            # Example filters:
            if 'Region' in df.columns:
                df_filtered = df[df['Region'].str.contains('North West|Mount Isa', case=False, na=False)]
            elif 'Location' in df.columns:
                df_filtered = df[df['Location'].str.contains('North West|Mount Isa', case=False, na=False)]
            else:
                self.logger.info("No region/location column found - keeping all records")
                df_filtered = df

            df_filtered['fetch_timestamp'] = pd.Timestamp.now()
            df_filtered['source_dataset'] = 'FPP'

            return df_filtered

        except Exception as e:
            self.logger.error(f"Error fetching FPP data: {e}")
            return None

    def fetch_awarded_contracts(self):
        """Fetch awarded contracts data"""
        self.logger.info("Fetching QLD awarded contracts data")

        try:
            # Get package metadata
            package = self.ckan.action.package_show(id=self.contracts_package)

            self.logger.info(f"Package: {package['title']}")

            # Get CSV resources
            csv_resources = [r for r in package['resources']
                           if r['format'].upper() == 'CSV']

            if not csv_resources:
                self.logger.warning("No CSV resources found in contracts package")
                return None

            resource = csv_resources[0]
            resource_url = resource['url']

            self.logger.info(f"Downloading from: {resource_url}")

            # Download CSV
            df = pd.read_csv(resource_url)

            self.logger.info(f"Downloaded {len(df)} contract records")

            df['fetch_timestamp'] = pd.Timestamp.now()
            df['source_dataset'] = 'AWARDED'

            return df

        except Exception as e:
            self.logger.error(f"Error fetching awarded contracts: {e}")
            return None

    def geocode_suppliers(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Geocode supplier locations to identify local vs external

        Args:
            df: DataFrame with supplier location information
        """
        self.logger.info("Geocoding suppliers to identify local vs external")

        # This is a simplified version
        # Full implementation would use G-NAF and PostGIS

        # Check for supplier location/postcode columns
        location_cols = [col for col in df.columns
                        if 'supplier' in col.lower() and
                        ('location' in col.lower() or 'postcode' in col.lower() or 'address' in col.lower())]

        if location_cols:
            # Simple check for Mount Isa
            df['is_local'] = False

            for col in location_cols:
                mask = df[col].astype(str).str.contains('4825|Mount Isa|Mt Isa', case=False, na=False)
                df.loc[mask, 'is_local'] = True

            local_count = df['is_local'].sum()
            self.logger.info(f"Identified {local_count} local suppliers ({local_count/len(df)*100:.1f}%)")

        return df

    def run(self):
        """Main execution method"""
        self.logger.info("Starting QLD procurement ingestion")

        results = {}

        # Fetch FPP
        df_fpp = self.fetch_forward_procurement_pipeline()
        if df_fpp is not None and len(df_fpp) > 0:
            filepath = self.save_raw_data(df_fpp, "qld_fpp", format='csv')
            self.record_provenance(
                source_url=f"{self.ckan_url}/dataset/{self.fpp_package}",
                filepath=filepath,
                record_count=len(df_fpp),
                licence="CC BY 4.0"
            )
            results['fpp'] = df_fpp

        # Fetch Awarded Contracts
        df_contracts = self.fetch_awarded_contracts()
        if df_contracts is not None and len(df_contracts) > 0:
            # Geocode suppliers
            df_contracts = self.geocode_suppliers(df_contracts)

            filepath = self.save_raw_data(df_contracts, "qld_awarded_contracts", format='csv')
            self.record_provenance(
                source_url=f"{self.ckan_url}/dataset/{self.contracts_package}",
                filepath=filepath,
                record_count=len(df_contracts),
                licence="CC BY 4.0"
            )
            results['contracts'] = df_contracts

        self.logger.info(f"QLD procurement ingestion completed: {len(results)} datasets")
        return results


if __name__ == "__main__":
    ingestion = QLDProcurementIngestion()
    ingestion.run()
