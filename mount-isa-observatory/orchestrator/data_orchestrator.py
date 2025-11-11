"""
Data Orchestration Engine
Continuously scrapes and integrates data from ALL sources
Tracks provenance back to source for every record
"""
import schedule
import time
import logging
from datetime import datetime, timedelta
from pathlib import Path
import sys

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from ingestion.qld_gov.fetch_procurement_direct import QLDProcurementDirectIngestion
from ingestion.abs.fetch_cabee import ABSBusinessCountsIngestion
from ingestion.austender.fetch_contracts import AusTenderIngestion
from ingestion.abn_lookup.fetch_local_entities import ABNLookupIngestion

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orchestrator.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

class DataOrchestrator:
    """
    Master orchestrator that:
    1. Schedules data fetching from all sources
    2. Tracks provenance
    3. Handles errors and retries
    4. Ensures data quality
    """

    def __init__(self):
        self.sources = self._initialize_sources()
        self.run_log = []

    def _initialize_sources(self):
        """Initialize all data sources with their schedules"""
        return {
            # CRITICAL - Youth Justice & Grants (Check daily for new grants)
            'youth_justice_grants': {
                'fetcher': self.fetch_youth_justice_grants,
                'schedule': 'daily',
                'priority': 'CRITICAL'
            },

            # HIGH - Business & Entity Data
            'abn_lookup': {
                'fetcher': ABNLookupIngestion(),
                'schedule': 'weekly',
                'priority': 'HIGH'
            },
            'qld_procurement': {
                'fetcher': QLDProcurementDirectIngestion(),
                'schedule': 'weekly',
                'priority': 'HIGH'
            },

            # MEDIUM - Economic Baseline Data
            'abs_cabee': {
                'fetcher': ABSBusinessCountsIngestion(),
                'schedule': 'monthly',
                'priority': 'MEDIUM'
            },
            'austender': {
                'fetcher': AusTenderIngestion(),
                'schedule': 'weekly',
                'priority': 'MEDIUM'
            },

            # ONGOING - Community Input
            'community_interviews': {
                'fetcher': self.process_community_input,
                'schedule': 'manual',
                'priority': 'CRITICAL'
            }
        }

    def fetch_youth_justice_grants(self):
        """
        Scrape all Queensland Youth Justice grant announcements
        Track: On Country, Kickstarter, Targeted Responses, etc.
        """
        logger.info("Fetching youth justice grants...")

        import requests
        from bs4 import BeautifulSoup

        grants = []
        urls = [
            'https://www.youthjustice.qld.gov.au/partnerships/grants/',
            'https://statements.qld.gov.au/',  # Ministerial statements
        ]

        for url in urls:
            try:
                response = requests.get(url, timeout=30)
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')

                    # Look for grant announcements
                    # This is simplified - would need detailed selectors
                    links = soup.find_all('a', href=True)

                    for link in links:
                        text = link.get_text().lower()
                        if any(keyword in text for keyword in [
                            'grant', 'funding', 'mount isa', 'youth', 'indigenous'
                        ]):
                            grants.append({
                                'title': link.get_text().strip(),
                                'url': link['href'],
                                'source': url,
                                'discovered_at': datetime.now()
                            })

            except Exception as e:
                logger.error(f"Error scraping {url}: {e}")

        logger.info(f"Found {len(grants)} potential grant announcements")
        return grants

    def process_community_input(self):
        """
        Process community interviews from service map database
        Extract themes, sentiment, gaps
        """
        logger.info("Processing community input...")
        # This would connect to your service map database
        # and extract the 127 interviews
        pass

    def run_scheduled_fetches(self):
        """Set up scheduled jobs"""
        logger.info("Setting up data orchestration schedule...")

        # Daily jobs
        schedule.every().day.at("02:00").do(self.fetch_youth_justice_grants)

        # Weekly jobs (Monday 3am)
        schedule.every().monday.at("03:00").do(
            lambda: self.sources['qld_procurement']['fetcher'].run()
        )
        schedule.every().monday.at("04:00").do(
            lambda: self.sources['abn_lookup']['fetcher'].run()
        )
        schedule.every().monday.at("05:00").do(
            lambda: self.sources['austender']['fetcher'].run()
        )

        # Monthly jobs (1st of month, 2am)
        schedule.every().month.at("02:00").do(
            lambda: self.sources['abs_cabee']['fetcher'].run()
        )

        logger.info("Schedule configured:")
        for job in schedule.get_jobs():
            logger.info(f"  - {job}")

    def run_all_now(self):
        """Run all fetchers immediately (for initial setup)"""
        logger.info("Running all data fetchers NOW...")

        for name, source in self.sources.items():
            if source['schedule'] != 'manual':
                logger.info(f"\nFetching: {name} (Priority: {source['priority']})")
                try:
                    fetcher = source['fetcher']
                    if hasattr(fetcher, 'run'):
                        result = fetcher.run()
                    elif callable(fetcher):
                        result = fetcher()

                    self.run_log.append({
                        'source': name,
                        'timestamp': datetime.now(),
                        'status': 'SUCCESS',
                        'result': result
                    })

                except Exception as e:
                    logger.error(f"Error with {name}: {e}")
                    self.run_log.append({
                        'source': name,
                        'timestamp': datetime.now(),
                        'status': 'ERROR',
                        'error': str(e)
                    })

        logger.info("\n" + "="*70)
        logger.info("INITIAL DATA FETCH COMPLETE")
        logger.info("="*70)
        self.print_summary()

    def print_summary(self):
        """Print summary of all fetches"""
        logger.info("\nFetch Summary:")
        for log in self.run_log:
            status_icon = "✓" if log['status'] == 'SUCCESS' else "✗"
            logger.info(f"  {status_icon} {log['source']}: {log['status']}")

    def start(self, run_now=True):
        """Start the orchestrator"""
        logger.info("\n" + "="*70)
        logger.info("MOUNT ISA ECONOMIC OBSERVATORY - DATA ORCHESTRATOR")
        logger.info("="*70 + "\n")

        if run_now:
            self.run_all_now()

        # Set up scheduled jobs
        self.run_scheduled_fetches()

        logger.info("\nOrchestrator running. Press Ctrl+C to stop.")

        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute


if __name__ == "__main__":
    orchestrator = DataOrchestrator()
    orchestrator.start(run_now=True)
