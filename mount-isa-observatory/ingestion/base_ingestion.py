"""
Base ingestion class with common functionality for all data sources
"""
import os
import hashlib
import logging
from datetime import datetime
from typing import Optional, Dict, Any
import yaml
import requests
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

class BaseIngestion:
    """Base class for all data ingestion processes"""

    def __init__(self, source_name: str, config_path: str = None):
        self.source_name = source_name
        self.logger = logging.getLogger(f"ingestion.{source_name}")

        # Load configuration
        if config_path is None:
            config_path = Path(__file__).parent.parent / "config" / "config.yaml"

        with open(config_path, 'r') as f:
            self.config = yaml.safe_load(f)

        # Setup data directories
        self.raw_dir = Path(self.config['etl']['raw_data_dir']) / source_name
        self.staged_dir = Path(self.config['etl']['staged_data_dir']) / source_name
        self.processed_dir = Path(self.config['etl']['processed_data_dir']) / source_name

        # Create directories if they don't exist
        self.raw_dir.mkdir(parents=True, exist_ok=True)
        self.staged_dir.mkdir(parents=True, exist_ok=True)
        self.processed_dir.mkdir(parents=True, exist_ok=True)

        # Setup session with retry logic
        self.session = self._create_session()

    def _create_session(self) -> requests.Session:
        """Create requests session with retry logic"""
        from requests.adapters import HTTPAdapter
        from urllib3.util.retry import Retry

        session = requests.Session()

        retry_strategy = Retry(
            total=4,
            backoff_factor=2,  # 2s, 4s, 8s, 16s
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST"]
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        session.mount("http://", adapter)
        session.mount("https://", adapter)

        return session

    def fetch_data(self, url: str, params: Optional[Dict] = None,
                   headers: Optional[Dict] = None) -> requests.Response:
        """Fetch data from URL with retry logic"""
        self.logger.info(f"Fetching data from: {url}")

        try:
            response = self.session.get(url, params=params, headers=headers, timeout=60)
            response.raise_for_status()
            return response
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Error fetching data: {e}")
            raise

    def save_raw_data(self, data: Any, filename: str, format: str = 'csv') -> Path:
        """Save raw data to file with timestamp and hash"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = self.raw_dir / f"{filename}_{timestamp}.{format}"

        if format == 'csv' and isinstance(data, pd.DataFrame):
            data.to_csv(filepath, index=False)
        elif format == 'json':
            import json
            with open(filepath, 'w') as f:
                json.dump(data, f, indent=2)
        elif format == 'xlsx' and isinstance(data, pd.DataFrame):
            data.to_excel(filepath, index=False)
        else:
            # Binary data or other formats
            with open(filepath, 'wb') as f:
                f.write(data if isinstance(data, bytes) else str(data).encode())

        # Calculate file hash
        file_hash = self._calculate_file_hash(filepath)

        self.logger.info(f"Saved raw data to: {filepath}")
        self.logger.info(f"File hash (SHA-256): {file_hash}")

        return filepath

    def _calculate_file_hash(self, filepath: Path) -> str:
        """Calculate SHA-256 hash of file"""
        sha256_hash = hashlib.sha256()
        with open(filepath, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()

    def record_provenance(self, source_url: str, filepath: Path,
                          record_count: int, licence: str = None):
        """Record data provenance for audit trail"""
        file_hash = self._calculate_file_hash(filepath)

        provenance = {
            'source_name': self.source_name,
            'source_url': source_url,
            'fetch_timestamp': datetime.now().isoformat(),
            'record_count': record_count,
            'file_hash': file_hash,
            'licence': licence,
            'filepath': str(filepath)
        }

        # Save provenance record
        provenance_file = self.raw_dir / f"provenance_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        import json
        with open(provenance_file, 'w') as f:
            json.dump(provenance, f, indent=2)

        self.logger.info(f"Recorded provenance: {provenance_file}")

        return provenance

    def get_lga_config(self) -> Dict[str, str]:
        """Get Mount Isa LGA configuration"""
        return self.config['geography']

    def validate_data(self, df: pd.DataFrame, required_columns: list) -> bool:
        """Basic validation - check required columns exist"""
        missing_columns = set(required_columns) - set(df.columns)
        if missing_columns:
            self.logger.error(f"Missing required columns: {missing_columns}")
            return False

        self.logger.info(f"Data validation passed. Rows: {len(df)}, Columns: {len(df.columns)}")
        return True
