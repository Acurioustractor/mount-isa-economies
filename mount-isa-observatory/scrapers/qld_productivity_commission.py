"""
Queensland Productivity Commission Scraper
Gets regional economic reports, productivity analyses, and recommendations

Source: https://www.qpc.qld.gov.au/
Focus: Reports mentioning Mount Isa, North West Queensland, regional development
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import re

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'qpc_reports'
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*80)
print("📊 QUEENSLAND PRODUCTIVITY COMMISSION SCRAPER")
print("="*80 + "\n")

class QPCScraper:
    """Scrape QPC reports and data"""

    def __init__(self):
        self.base_url = "https://www.qpc.qld.gov.au"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def get_all_reports(self):
        """Get list of all published reports"""
        print("📥 Fetching QPC reports...\n")

        reports_url = f"{self.base_url}/inquiries/"

        try:
            response = self.session.get(reports_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            reports = []

            # Find report links
            report_links = soup.find_all('a', href=True)

            for link in report_links:
                href = link['href']
                text = link.text.strip()

                # Filter for actual reports
                if '/inquiries/' in href or '/report' in href.lower():
                    full_url = href if href.startswith('http') else f"{self.base_url}{href}"

                    reports.append({
                        'title': text,
                        'url': full_url,
                        'found_date': datetime.now().isoformat()
                    })

            print(f"✅ Found {len(reports)} reports\n")
            return reports

        except Exception as e:
            print(f"❌ Error fetching reports: {e}")
            return []

    def search_report_content(self, report_url, search_terms):
        """Search if a report mentions specific terms"""
        try:
            response = self.session.get(report_url, timeout=30)
            response.raise_for_status()

            text = response.text.lower()

            mentions = {}
            for term in search_terms:
                count = text.count(term.lower())
                if count > 0:
                    mentions[term] = count

            return mentions

        except Exception as e:
            return {}

    def download_report_pdf(self, pdf_url, filename):
        """Download a PDF report"""
        try:
            response = self.session.get(pdf_url, timeout=60)
            response.raise_for_status()

            output_file = DATA_DIR / filename
            with open(output_file, 'wb') as f:
                f.write(response.content)

            print(f"   ✅ Downloaded: {filename}")
            return output_file

        except Exception as e:
            print(f"   ❌ Error downloading {filename}: {e}")
            return None


# Main execution
if __name__ == '__main__':
    scraper = QPCScraper()

    # Get all reports
    reports = scraper.get_all_reports()

    if not reports:
        print("⚠️  No reports found")
        print("\nManual fallback:")
        print("Visit: https://www.qpc.qld.gov.au/inquiries/")
        print("Look for reports mentioning:")
        print("  • North West Queensland")
        print("  • Regional development")
        print("  • Remote communities")
        print("  • Mining regions")
        exit()

    # Search for Mount Isa / regional mentions
    print("🔍 Searching reports for Mount Isa mentions...\n")

    search_terms = [
        "Mount Isa",
        "North West Queensland",
        "Kalkadoon",
        "regional Queensland",
        "remote communities",
        "mining regions"
    ]

    relevant_reports = []

    for report in reports:
        print(f"Checking: {report['title'][:60]}...")

        mentions = scraper.search_report_content(report['url'], search_terms)

        if mentions:
            print(f"   ✅ Found mentions: {mentions}")
            report['mentions'] = mentions
            relevant_reports.append(report)
        else:
            print(f"   - No mentions")

        time.sleep(1)  # Rate limiting

    print(f"\n✅ Found {len(relevant_reports)} relevant reports\n")

    if relevant_reports:
        print("="*80)
        print("📊 RELEVANT QPC REPORTS")
        print("="*80 + "\n")

        for idx, report in enumerate(relevant_reports, 1):
            print(f"{idx}. {report['title']}")
            print(f"   URL: {report['url']}")
            print(f"   Mentions: {report['mentions']}")
            print()

        # Save results
        df = pd.DataFrame(relevant_reports)
        output_file = DATA_DIR / f'qpc_relevant_reports_{datetime.now().strftime("%Y%m%d")}.csv'
        df.to_csv(output_file, index=False)

        print(f"💾 Saved: {output_file}\n")

        # Download PDFs of most relevant reports
        print("📥 Downloading most relevant report PDFs...\n")

        for report in relevant_reports[:5]:  # Top 5
            # Try to find PDF link
            try:
                response = scraper.session.get(report['url'], timeout=30)
                soup = BeautifulSoup(response.text, 'html.parser')

                pdf_links = soup.find_all('a', href=re.compile(r'\.pdf$', re.I))

                for link in pdf_links:
                    pdf_url = link['href']
                    if not pdf_url.startswith('http'):
                        pdf_url = f"{scraper.base_url}{pdf_url}"

                    filename = f"{report['title'][:50].replace('/', '-')}.pdf"
                    scraper.download_report_pdf(pdf_url, filename)
                    break  # Only download first PDF

            except Exception as e:
                print(f"   ⚠️  Error processing {report['title']}: {e}")

    print("\n" + "="*80)
    print("✅ QPC SCRAPE COMPLETE")
    print("="*80 + "\n")

    print("💡 Next steps:")
    print("  1. Review downloaded reports in data/qpc_reports/")
    print("  2. Extract economic data and recommendations")
    print("  3. Look for Mount Isa-specific findings")
    print("  4. Track policy recommendations affecting the region\n")
