"""
Web Enrichment Scraper
Scrapes service websites to fill in missing data:
- Operating hours
- Full descriptions
- Staff counts
- Programs offered
- Contact details
- Social media links
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import re
from urllib.parse import urlparse

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'enriched'
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*80)
print("🌐 WEB ENRICHMENT SCRAPER")
print("="*80 + "\n")

class WebEnricher:
    """Scrape service websites to enrich data"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def enrich_service(self, service):
        """Enrich a single service by scraping its website"""
        website = service.get('website')

        if not website or pd.isna(website):
            return service

        print(f"🔍 Enriching: {service.get('name', 'Unknown')}")
        print(f"   Website: {website}")

        try:
            # Ensure URL has scheme
            if not website.startswith('http'):
                website = f"https://{website}"

            response = self.session.get(website, timeout=15)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Extract various data points
            enriched = service.copy()

            # 1. Extract meta description if service description is missing
            if not service.get('description') or pd.isna(service.get('description')):
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                if meta_desc and meta_desc.get('content'):
                    enriched['description'] = meta_desc['content']
                    print(f"   ✅ Found description")

            # 2. Look for operating hours
            hours_keywords = ['hours', 'opening hours', 'open', 'operating hours']
            for keyword in hours_keywords:
                elements = soup.find_all(string=re.compile(keyword, re.I))
                if elements:
                    # Get parent elements
                    for elem in elements[:3]:
                        parent_text = elem.parent.get_text(strip=True)
                        if len(parent_text) < 200:  # Reasonable length
                            enriched['operating_hours_from_web'] = parent_text
                            print(f"   ✅ Found operating hours")
                            break
                    if 'operating_hours_from_web' in enriched:
                        break

            # 3. Find email addresses
            emails = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', response.text)
            if emails and (not service.get('email') or pd.isna(service.get('email'))):
                # Filter out common non-contact emails
                valid_emails = [e for e in emails if not any(skip in e.lower()
                               for skip in ['example.com', 'test@', 'noreply'])]
                if valid_emails:
                    enriched['email'] = valid_emails[0]
                    enriched['all_emails_found'] = ', '.join(valid_emails[:3])
                    print(f"   ✅ Found email: {valid_emails[0]}")

            # 4. Find phone numbers
            phones = re.findall(r'(\+?\d{1,3}[-.\s]?)?\(?\d{2,4}\)?[-.\s]?\d{3,4}[-.\s]?\d{3,4}', response.text)
            if phones and (not service.get('phone') or pd.isna(service.get('phone'))):
                # Clean and deduplicate
                clean_phones = list(set([p.strip() for p in phones if len(p.strip()) > 8]))
                if clean_phones:
                    enriched['phone'] = clean_phones[0]
                    enriched['all_phones_found'] = ', '.join(clean_phones[:3])
                    print(f"   ✅ Found phone: {clean_phones[0]}")

            # 5. Find social media links
            social_platforms = {
                'facebook': r'facebook\.com/[^/\s"\']+',
                'twitter': r'twitter\.com/[^/\s"\']+',
                'instagram': r'instagram\.com/[^/\s"\']+',
                'linkedin': r'linkedin\.com/[^/\s"\']+',
            }

            for platform, pattern in social_platforms.items():
                if not service.get(platform) or pd.isna(service.get(platform)):
                    matches = re.findall(pattern, response.text, re.I)
                    if matches:
                        enriched[platform] = f"https://{matches[0]}"
                        print(f"   ✅ Found {platform}: {matches[0]}")

            # 6. Extract full text for keyword analysis
            text_content = soup.get_text()

            # Count mentions of key service areas
            service_keywords = {
                'youth': r'\byouth\b',
                'families': r'\bfamil(y|ies)\b',
                'mental_health': r'\bmental health\b',
                'substance': r'\b(drug|alcohol|substance)\b',
                'housing': r'\bhousing\b',
                'employment': r'\b(job|employment|work)\b',
                'education': r'\b(education|training|learn)\b',
                'legal': r'\b(legal|law|court)\b',
                'health': r'\bhealth\b',
            }

            keyword_mentions = {}
            for keyword, pattern in service_keywords.items():
                matches = len(re.findall(pattern, text_content, re.I))
                if matches > 0:
                    keyword_mentions[keyword] = matches

            if keyword_mentions:
                enriched['service_focus_keywords'] = json.dumps(keyword_mentions)
                print(f"   ✅ Identified focus areas: {list(keyword_mentions.keys())}")

            # 7. Look for staff/team mentions
            staff_indicators = [
                r'(\d+)\s+staff',
                r'team of (\d+)',
                r'(\d+)\s+employees',
                r'(\d+)\s+workers',
            ]

            for pattern in staff_indicators:
                matches = re.findall(pattern, text_content, re.I)
                if matches:
                    enriched['estimated_staff_from_web'] = int(matches[0])
                    print(f"   ✅ Found staff count: {matches[0]}")
                    break

            enriched['last_web_scrape'] = datetime.now().isoformat()
            enriched['website_accessible'] = True

            print(f"   ✅ Enrichment complete\n")
            return enriched

        except requests.exceptions.Timeout:
            print(f"   ⏱️  Timeout\n")
            service['website_accessible'] = False
            service['last_web_scrape'] = datetime.now().isoformat()
            return service

        except requests.exceptions.RequestException as e:
            print(f"   ❌ Error: {e}\n")
            service['website_accessible'] = False
            service['last_web_scrape'] = datetime.now().isoformat()
            return service

        except Exception as e:
            print(f"   ❌ Unexpected error: {e}\n")
            return service


# Main execution
if __name__ == '__main__':
    import json

    # Load services to enrich
    services_file = BASE_DIR / 'data' / 'exports' / 'services_export.csv'

    if not services_file.exists():
        print(f"❌ Services file not found: {services_file}")
        exit(1)

    services = pd.read_csv(services_file)
    print(f"📁 Loaded {len(services)} services\n")

    # Filter for services with websites
    services_with_websites = services[services['website'].notna()].copy()
    print(f"🌐 {len(services_with_websites)} services have websites\n")

    print("="*80)
    print("STARTING WEB ENRICHMENT")
    print("="*80 + "\n")

    enricher = WebEnricher()
    enriched_services = []

    for idx, service in services_with_websites.iterrows():
        enriched = enricher.enrich_service(service.to_dict())
        enriched_services.append(enriched)

        # Rate limiting
        time.sleep(2)

        # Progress update
        if (len(enriched_services)) % 10 == 0:
            print(f"   Progress: {len(enriched_services)}/{len(services_with_websites)}\n")

    # Create enriched dataframe
    enriched_df = pd.DataFrame(enriched_services)

    # Save enriched data
    output_file = DATA_DIR / f'services_enriched_{datetime.now().strftime("%Y%m%d")}.csv'
    enriched_df.to_csv(output_file, index=False)

    print("\n" + "="*80)
    print("📊 ENRICHMENT SUMMARY")
    print("="*80 + "\n")

    print(f"Total services processed: {len(enriched_df)}")
    print(f"Websites accessible: {enriched_df['website_accessible'].sum()}")
    print()

    # Show enrichment stats
    new_fields = ['operating_hours_from_web', 'all_emails_found', 'all_phones_found',
                  'service_focus_keywords', 'estimated_staff_from_web']

    for field in new_fields:
        if field in enriched_df.columns:
            count = enriched_df[field].notna().sum()
            print(f"   {field}: {count} services")

    print(f"\n💾 Saved: {output_file}\n")

    print("="*80)
    print("✅ WEB ENRICHMENT COMPLETE")
    print("="*80 + "\n")
