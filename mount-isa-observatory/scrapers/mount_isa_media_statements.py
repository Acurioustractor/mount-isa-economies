"""
Mount Isa Media Statements - Direct Fetcher
Uses known statement IDs from research to fetch details

Known Mount Isa statements from web search:
- 100887: On-Country program $24M (July 2024)
- 98003: Co-responder team (June 2023)
- 97577: Community grants
- 89527: New funding to tackle youth crime
- 98337: Stronger Communities $7M
- 100864: Youth Co-Responder Teams update
- 97933: Record youth justice budget
- 97218: Tougher action on youth crime
- 100544: Police and Community Safety budget
- 97930: Police operating budget
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
print("📰 MOUNT ISA MINISTERIAL STATEMENTS - DIRECT FETCH")
print("="*80 + "\n")

# Known statement IDs from research
KNOWN_STATEMENTS = [
    {'id': '100887', 'title': 'On-Country program to begin in Mount Isa', 'date': 'July 2024'},
    {'id': '98003', 'title': 'New co-responder team tackling youth crime in Mount Isa', 'date': 'June 2023'},
    {'id': '97577', 'title': 'Community grants help tackle youth offending in Mount Isa, Townsville'},
    {'id': '89527', 'title': 'New funding to tackle youth crime in Mount Isa'},
    {'id': '98337', 'title': 'More funding for Mount Isa Stronger Communities approach'},
    {'id': '100864', 'title': 'Youth Co-Responder Teams contributing to reduced offending'},
    {'id': '97933', 'title': 'Record youth justice budget puts community safety first'},
    {'id': '97218', 'title': 'Putting community safety first with tougher action on youth crime'},
    {'id': '100544', 'title': 'Miles Labor Government delivers record Police and Community Safety budget'},
    {'id': '97930', 'title': 'Record $3.281 billion operating budget to bolster police services'},
]

BASE_URL = "https://statements.qld.gov.au/statements"

def fetch_statement(statement_id: str) -> dict:
    """Fetch full statement details"""
    url = f"{BASE_URL}/{statement_id}"

    try:
        print(f"  Fetching statement {statement_id}...")

        response = requests.get(url, timeout=30, headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })
        response.raise_for_status()

        soup = BeautifulSoup(response.content, 'html.parser')

        # Look for JSON-LD structured data (this is where the real content is!)
        json_ld = soup.find('script', type='application/ld+json')

        title = "Unknown"
        date = None
        full_text = ""

        if json_ld:
            import json
            try:
                data = json.loads(json_ld.string)
                title = data.get('headline', data.get('name', 'Unknown'))
                date = data.get('datePublished', data.get('dateCreated'))

                # Get article body (contains HTML tags, need to clean)
                article_body = data.get('articleBody', '')
                # Remove HTML tags
                article_soup = BeautifulSoup(article_body, 'html.parser')
                full_text = article_soup.get_text(separator=' ', strip=True)

            except:
                pass

        # Fallback to regular HTML parsing if JSON-LD fails
        if not full_text:
            title_elem = soup.find(['h1', 'h2'])
            title = title_elem.get_text(strip=True) if title_elem else "Unknown"

            content_div = soup.find(['article', 'div'], class_=re.compile(r'content|body|statement', re.I))
            if not content_div:
                content_div = soup.find('main')
            full_text = content_div.get_text(separator=' ', strip=True) if content_div else soup.get_text(separator=' ', strip=True)

        # Extract all dollar amounts
        amounts = re.findall(r'\$[\d,]+(?:\.\d+)?\s*(?:million|billion|M|B)?', full_text, re.IGNORECASE)

        # Extract program names
        programs = []
        program_patterns = [
            r'(?:Intensive\s+)?On-?Country\s+[Pp]rogram',
            r'Youth\s+Co-?[Rr]esponder\s+Team',
            r'Stronger\s+Communities',
            r'Early\s+Action\s+Group',
            r'Diversionary\s+Centre',
            r'PCYC',
            r'Taskforce\s+Guardian',
            r'Mithangkaya\s+Nguli',
            r'Young\s+People\s+Ahead'
        ]

        for pattern in program_patterns:
            matches = re.findall(pattern, full_text, re.IGNORECASE)
            programs.extend([m for m in matches])

        # Extract key quotes about Mount Isa
        mount_isa_context = []
        sentences = full_text.split('.')
        for sentence in sentences:
            if 'mount isa' in sentence.lower():
                mount_isa_context.append(sentence.strip())

        return {
            'statement_id': statement_id,
            'url': url,
            'title': title,
            'date': date,
            'full_text': full_text,
            'amounts_mentioned': amounts,
            'programs_mentioned': list(set(programs)),
            'mount_isa_context': mount_isa_context[:5],  # Top 5 mentions
            'scraped_date': datetime.now().isoformat()
        }

    except Exception as e:
        print(f"  ⚠️  Error fetching {statement_id}: {e}")
        return {
            'statement_id': statement_id,
            'url': f"{BASE_URL}/{statement_id}",
            'error': str(e)
        }

# Fetch all known statements
all_data = []

for stmt in KNOWN_STATEMENTS:
    data = fetch_statement(stmt['id'])

    # Merge with known info
    data['known_title'] = stmt.get('title')
    data['known_date'] = stmt.get('date')

    all_data.append(data)
    time.sleep(2)  # Rate limiting

# Convert to DataFrame
df = pd.DataFrame(all_data)

# Save results
output_file = DATA_DIR / f'mount_isa_statements_{datetime.now().strftime("%Y%m%d")}.csv'
df.to_csv(output_file, index=False)

print(f"\n💾 Saved {len(df)} statements: {output_file}\n")

# Print summary
print("="*80)
print("📊 FUNDING ANNOUNCEMENTS SUMMARY")
print("="*80 + "\n")

successful = df[~df['title'].isna()]
print(f"Successfully fetched: {len(successful)} of {len(df)}")

if len(successful) > 0:
    print("\n" + "="*80)
    print("KEY FINDINGS:")
    print("="*80 + "\n")

    for idx, row in successful.iterrows():
        print(f"📌 {row['title']}")
        print(f"   Date: {row.get('date', 'Unknown')}")
        print(f"   URL: {row['url']}")

        # Parse amounts_mentioned which might be a string representation of a list
        amounts = row.get('amounts_mentioned', [])
        if isinstance(amounts, str):
            import ast
            try:
                amounts = ast.literal_eval(amounts)
            except:
                amounts = []

        if amounts and len(amounts) > 0:
            print(f"   💰 Amounts: {', '.join(amounts[:5])}")

        # Parse programs_mentioned
        programs = row.get('programs_mentioned', [])
        if isinstance(programs, str):
            try:
                programs = ast.literal_eval(programs)
            except:
                programs = []

        if programs and len(programs) > 0:
            print(f"   🎯 Programs: {', '.join(set(programs[:5]))}")

        # Parse mount_isa_context
        context = row.get('mount_isa_context', [])
        if isinstance(context, str):
            try:
                context = ast.literal_eval(context)
            except:
                context = []

        if context and len(context) > 0:
            print(f"   📝 Context: {context[0][:150]}...")

        print()

print("="*80)
print("✅ COMPLETE")
print("="*80 + "\n")

print("💡 Next steps:")
print("  1. Review the CSV file for all funding details")
print("  2. Extract specific program allocations")
print("  3. Build timeline of announcements")
print("  4. Match to service providers (ACNC data)")
