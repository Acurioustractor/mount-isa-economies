"""
Media Statements Scraper - Firecrawl Version

Uses Firecrawl to bypass 403 blocks on Queensland Government statements.
This version works when simple requests fail.

Setup:
1. Get Firecrawl API key: https://firecrawl.dev/ (500 free credits/month)
2. Add to .env: FIRECRAWL_API_KEY=fc-your_key_here
3. Install: pip install firecrawl-py
4. Run: python scrapers/mount_isa_media_statements_firecrawl.py

Why Firecrawl?
- Queensland Gov blocks simple requests (403 Forbidden)
- Firecrawl handles JavaScript, bypasses blocks, solves CAPTCHAs
- More reliable than user-agent spoofing or proxies
"""

import os
import sys
from datetime import datetime
from pathlib import Path
import pandas as pd
from dotenv import load_dotenv

# Add parent directory to path
sys.path.append(str(Path(__file__).parent))

# Load environment
load_dotenv()

from utils.firecrawl_scraper import FirecrawlScraper

# Known statement IDs from previous research
MOUNT_ISA_STATEMENTS = [
    {'id': '100887', 'title': 'On-Country program to begin in Mount Isa', 'date': 'July 2024'},
    {'id': '98003', 'title': 'New co-responder team tackling youth crime', 'date': 'June 2023'},
    {'id': '98337', 'title': 'More funding for Mount Isa Stronger Communities', 'date': 'Aug 2023'},
    {'id': '97933', 'title': 'Record youth justice budget', 'date': 'June 2023'},
    {'id': '100544', 'title': 'Police and Community Safety budget', 'date': 'June 2024'},
    {'id': '100864', 'title': 'Youth Co-Responder Teams reducing offending', 'date': 'July 2024'},
    {'id': '97577', 'title': 'Community grants - Mount Isa & Townsville', 'date': 'April 2023'},
    {'id': '89527', 'title': 'New funding to tackle youth crime', 'date': 'March 2020'},
    {'id': '97930', 'title': '$3.281B police operating budget', 'date': 'June 2023'},
    {'id': '97218', 'title': 'Tougher action on youth crime', 'date': 'Feb 2023'},
]

BASE_URL = 'https://statements.qld.gov.au/statements'


def scrape_media_statements():
    """
    Scrape Mount Isa media statements using Firecrawl
    """
    print("\n" + "="*80)
    print("📰 MOUNT ISA MEDIA STATEMENTS - FIRECRAWL SCRAPER")
    print("="*80 + "\n")

    # Initialize Firecrawl
    try:
        scraper = FirecrawlScraper()
    except ValueError as e:
        print(f"❌ {e}")
        print("\nSetup instructions:")
        print("  1. Get API key: https://firecrawl.dev/")
        print("  2. Add to .env: FIRECRAWL_API_KEY=fc-your_key_here")
        print("  3. Run: ./scripts/validate-env.sh to verify")
        return

    results = []

    for statement in MOUNT_ISA_STATEMENTS:
        statement_id = statement['id']
        url = f"{BASE_URL}/{statement_id}"

        print(f"\nScraping: {statement['title']} ({statement_id})")

        try:
            # Scrape with Firecrawl (bypasses 403 blocks!)
            result = scraper.scrape_url(url)

            # Extract content
            markdown = result.get('markdown', '')
            metadata = result.get('metadata', {})

            # Simple regex extraction from markdown
            import re

            # Extract dollar amounts
            amounts = re.findall(r'\$[\d,]+(?:\.\d+)?\s*(?:million|billion|M|B)?', markdown, re.IGNORECASE)
            funding_amount = ', '.join(amounts[:3]) if amounts else ''  # First 3 amounts

            # Extract common Mount Isa program keywords
            programs = []
            program_keywords = ['On-Country', 'Co-responder', 'Stronger Communities', 'PCYC',
                              'Community Connect', 'Youth Justice', 'Diversionary']
            for keyword in program_keywords:
                if keyword.lower() in markdown.lower():
                    programs.append(keyword)
            program_name = ', '.join(programs) if programs else ''

            # Extract organization mentions
            orgs = []
            if 'Mithangkaya Nguli' in markdown:
                orgs.append('Mithangkaya Nguli')
            if 'Young People Ahead' in markdown:
                orgs.append('Young People Ahead')
            recipient = ', '.join(orgs) if orgs else ''

            # Store result
            results.append({
                'statement_id': statement_id,
                'url': url,
                'title': metadata.get('title', statement['title']),
                'date': statement['date'],
                'funding_amount': funding_amount,
                'recipient': recipient,
                'program': program_name,
                'content_preview': markdown[:500],
                'full_content': markdown,
                'scraped_at': datetime.now().isoformat()
            })

            print(f"✅ Success: {metadata.get('title')}")
            if funding_amount:
                print(f"   Amounts: {funding_amount}")
            if recipient:
                print(f"   Recipient: {recipient}")

        except Exception as e:
            print(f"❌ Error scraping {statement_id}: {e}")
            results.append({
                'statement_id': statement_id,
                'url': url,
                'error': str(e),
                'scraped_at': datetime.now().isoformat()
            })

    # Save results
    print("\n" + "="*80)
    print("💾 SAVING RESULTS")
    print("="*80 + "\n")

    # Create output directory
    output_dir = Path(__file__).parent.parent / 'data' / 'media_statements'
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save CSV
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    csv_file = output_dir / f'mount_isa_statements_firecrawl_{timestamp}.csv'

    df = pd.DataFrame(results)
    df.to_csv(csv_file, index=False)

    print(f"✅ Saved {len(results)} statements to:")
    print(f"   {csv_file}")

    # Print summary
    print("\n" + "="*80)
    print("📊 SCRAPING SUMMARY")
    print("="*80 + "\n")

    successful = len([r for r in results if 'error' not in r])
    failed = len([r for r in results if 'error' in r])

    print(f"Total statements: {len(results)}")
    print(f"Successful: {successful}")
    print(f"Failed: {failed}")

    if successful > 0:
        print("\n✅ Successfully scraped statements with Firecrawl!")
        print("   Queensland Gov 403 blocks bypassed 🎉")

        # Show funding total
        amounts = []
        for r in results:
            if 'funding_amount' in r and r['funding_amount']:
                amounts.append(r['funding_amount'])

        if amounts:
            print(f"\nFunding amounts identified:")
            for amount in amounts[:5]:  # Show first 5
                print(f"  • {amount}")

    return results


if __name__ == '__main__':
    scrape_media_statements()
