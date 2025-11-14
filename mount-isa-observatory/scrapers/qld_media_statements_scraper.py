"""
Queensland Government Ministerial Media Statements Scraper
Finds all media releases mentioning Mount Isa with funding announcements

Target: https://statements.qld.gov.au/
Focus: Youth justice, police, community safety funding for Mount Isa
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime
import re
import time

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'media_statements'
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*80)
print("📰 QUEENSLAND MINISTERIAL MEDIA STATEMENTS SCRAPER")
print("="*80 + "\n")

# Search parameters
KEYWORDS = [
    "Mount Isa youth justice",
    "Mount Isa police",
    "Mount Isa community safety",
    "Mount Isa crime",
    "Mount Isa funding",
    "North West Queensland youth",
    "Mithangkaya Nguli"
]

BASE_URL = "https://statements.qld.gov.au"

def search_statements(keyword: str, page: int = 1) -> list:
    """Search for statements containing keyword"""
    search_url = f"{BASE_URL}/search"
    params = {
        'q': keyword,
        'page': page
    }

    try:
        response = requests.get(search_url, params=params, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Find all statement links
        statements = []

        # Look for article/statement cards
        for card in soup.find_all(['article', 'div'], class_=re.compile(r'statement|result|card', re.I)):
            link = card.find('a', href=re.compile(r'/statements/\d+'))
            if link:
                title = link.get_text(strip=True)
                url = link.get('href')
                if not url.startswith('http'):
                    url = BASE_URL + url

                # Extract statement ID from URL
                statement_id = re.search(r'/statements/(\d+)', url)
                if statement_id:
                    statement_id = statement_id.group(1)

                # Look for date
                date_elem = card.find(['time', 'span'], class_=re.compile(r'date', re.I))
                date = date_elem.get_text(strip=True) if date_elem else None

                statements.append({
                    'id': statement_id,
                    'title': title,
                    'url': url,
                    'date': date,
                    'keyword': keyword
                })

        return statements

    except Exception as e:
        print(f"  ⚠️  Error searching for '{keyword}': {e}")
        return []

def scrape_statement_details(statement_url: str) -> dict:
    """Scrape full details from a statement page"""
    try:
        response = requests.get(statement_url, timeout=30)
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Extract full content
        content = soup.find(['article', 'div'], class_=re.compile(r'content|body', re.I))
        full_text = content.get_text(separator=' ', strip=True) if content else ""

        # Look for metadata
        minister = None
        department = None
        date = None

        # Find minister/department
        meta_section = soup.find(['div', 'section'], class_=re.compile(r'meta|author', re.I))
        if meta_section:
            minister_elem = meta_section.find(text=re.compile(r'Minister|Premier', re.I))
            if minister_elem:
                minister = minister_elem.strip()

            dept_elem = meta_section.find(text=re.compile(r'Department', re.I))
            if dept_elem:
                department = dept_elem.strip()

        # Find date
        date_elem = soup.find('time')
        if date_elem:
            date = date_elem.get('datetime') or date_elem.get_text(strip=True)

        # Extract dollar amounts
        amounts = re.findall(r'\$[\d,]+(?:\.\d+)?\s*(?:million|billion|M|B)?', full_text, re.IGNORECASE)

        # Extract program names (common patterns)
        programs = []
        program_patterns = [
            r'(?:Intensive\s+)?On-?Country\s+[Pp]rogram',
            r'Youth\s+Co-?responder\s+Team',
            r'Stronger\s+Communities',
            r'Early\s+Action\s+Group',
            r'Diversionary\s+Centre',
            r'PCYC',
            r'Taskforce\s+Guardian'
        ]

        for pattern in program_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            programs.extend(matches)

        return {
            'minister': minister,
            'department': department,
            'date': date,
            'full_text': full_text,
            'amounts_mentioned': amounts,
            'programs_mentioned': list(set(programs))
        }

    except Exception as e:
        print(f"  ⚠️  Error scraping statement details: {e}")
        return {}

# Search for all keywords
all_statements = []
seen_ids = set()

for keyword in KEYWORDS:
    print(f"🔍 Searching for: {keyword}")

    # Search first 3 pages for each keyword
    for page in range(1, 4):
        statements = search_statements(keyword, page)

        for stmt in statements:
            # Deduplicate by ID
            if stmt['id'] not in seen_ids:
                seen_ids.add(stmt['id'])
                all_statements.append(stmt)

        if not statements:
            break  # No more results

        time.sleep(0.5)  # Rate limiting

    print(f"  Found {len(statements)} results\n")

print(f"\n✅ Found {len(all_statements)} unique statements\n")

# Scrape details for each statement
print("📥 Downloading statement details...\n")

detailed_statements = []

for i, stmt in enumerate(all_statements, 1):
    print(f"  [{i}/{len(all_statements)}] {stmt['title'][:60]}...")

    details = scrape_statement_details(stmt['url'])

    # Merge basic info with details
    stmt.update(details)
    detailed_statements.append(stmt)

    time.sleep(1)  # Rate limiting

# Convert to DataFrame
df = pd.DataFrame(detailed_statements)

# Save results
output_file = DATA_DIR / f'mount_isa_statements_{datetime.now().strftime("%Y%m%d")}.csv'
df.to_csv(output_file, index=False)

print(f"\n💾 Saved {len(df)} statements: {output_file}\n")

# Print summary
print("="*80)
print("📊 SUMMARY")
print("="*80 + "\n")

print(f"Total statements found: {len(df)}")

if len(df) > 0:
    # Count by keyword
    print("\nBy search term:")
    for keyword in KEYWORDS:
        count = len(df[df['keyword'] == keyword])
        if count > 0:
            print(f"  • {keyword}: {count}")

    # Show titles with amounts
    with_amounts = df[df['amounts_mentioned'].apply(lambda x: len(x) > 0 if isinstance(x, list) else False)]
    print(f"\nStatements with funding amounts: {len(with_amounts)}")

    if len(with_amounts) > 0:
        print("\nTop funding announcements:")
        for idx, row in with_amounts.head(10).iterrows():
            print(f"\n  • {row['title']}")
            print(f"    Date: {row.get('date', 'Unknown')}")
            print(f"    Amounts: {', '.join(row['amounts_mentioned'][:3])}")
            if row.get('programs_mentioned'):
                print(f"    Programs: {', '.join(row['programs_mentioned'][:3])}")

print("\n" + "="*80)
print("✅ SCRAPING COMPLETE")
print("="*80 + "\n")
