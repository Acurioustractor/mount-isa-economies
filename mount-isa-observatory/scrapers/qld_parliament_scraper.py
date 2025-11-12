"""
Queensland Parliament & Hansard Scraper
Scrapes parliament records, budget estimates, Hansard for Mount Isa mentions

Gets: Funding announcements, ministerial statements, questions, budget allocations
"""
import requests
from bs4 import BeautifulSoup
import pandas as pd
from pathlib import Path
from datetime import datetime
import time
import re

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'parliament'
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*80)
print("🏛️  QUEENSLAND PARLIAMENT & HANSARD SCRAPER")
print("="*80 + "\n")

class QLDParliamentScraper:
    """Scrape QLD Parliament records"""

    def __init__(self):
        self.base_url = "https://www.parliament.qld.gov.au"
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
        })

    def search_hansard(self, search_term, limit=50):
        """Search Hansard records"""
        print(f"🔍 Searching Hansard for: {search_term}\n")

        # QLD Parliament Hansard search
        search_url = f"{self.base_url}/work-of-the-assembly/hansard"

        results = []

        try:
            # This would require finding the actual search API/form
            # For now, we'll scrape the Hansard index pages

            response = self.session.get(search_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find Hansard links
            hansard_links = soup.find_all('a', href=re.compile(r'hansard', re.I))

            print(f"   Found {len(hansard_links)} Hansard documents\n")

            # Sample first few for Mount Isa mentions
            for idx, link in enumerate(hansard_links[:limit], 1):
                href = link.get('href')
                if not href.startswith('http'):
                    href = f"{self.base_url}{href}"

                print(f"   Checking document {idx}/{min(limit, len(hansard_links))}: {link.text[:50]}...")

                try:
                    doc_response = self.session.get(href, timeout=30)
                    doc_response.raise_for_status()

                    # Search for term in document
                    text = doc_response.text.lower()
                    if search_term.lower() in text:
                        count = text.count(search_term.lower())
                        print(f"      ✅ Found {count} mentions")

                        results.append({
                            'document': link.text.strip(),
                            'url': href,
                            'mentions': count,
                            'search_term': search_term,
                            'found_date': datetime.now().isoformat()
                        })

                except Exception as e:
                    print(f"      ⚠️  Error: {e}")

                time.sleep(1)  # Rate limiting

        except Exception as e:
            print(f"   ❌ Error searching Hansard: {e}")

        return results

    def get_budget_estimates(self, year=2024):
        """Get budget estimates hearings"""
        print(f"📊 Fetching {year} Budget Estimates...\n")

        # Budget estimates are published separately
        budget_url = f"{self.base_url}/work-of-the-assembly/committees/estimates"

        try:
            response = self.session.get(budget_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            print(f"   Fetched budget estimates page")

            # Find PDF/document links
            doc_links = soup.find_all('a', href=re.compile(r'\.(pdf|doc|docx)$', re.I))

            print(f"   Found {len(doc_links)} budget documents\n")

            docs = []
            for link in doc_links[:20]:  # Sample first 20
                href = link.get('href')
                if not href.startswith('http'):
                    href = f"{self.base_url}{href}"

                docs.append({
                    'title': link.text.strip(),
                    'url': href,
                    'year': year
                })

                print(f"   • {link.text[:60]}")

            return docs

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []

    def search_ministerial_statements(self, search_term):
        """Search ministerial statements"""
        print(f"\n📢 Searching Ministerial Statements for: {search_term}\n")

        # Ministerial statements are often in Hansard or separate publications
        statements_url = f"{self.base_url}/work-of-the-assembly/tabled-papers"

        results = []

        try:
            response = self.session.get(statements_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Search page content
            text = soup.get_text()
            if search_term.lower() in text.lower():
                print(f"   ✅ Found mentions in tabled papers page")

                # Extract context around mentions
                pattern = re.compile(f'.{{0,100}}{re.escape(search_term)}.{{0,100}}', re.I)
                contexts = pattern.findall(text)

                for context in contexts[:10]:  # First 10 mentions
                    results.append({
                        'type': 'Ministerial Statement',
                        'context': context.strip(),
                        'search_term': search_term,
                        'url': statements_url
                    })

                    print(f"   Context: {context[:80]}...")

        except Exception as e:
            print(f"   ❌ Error: {e}")

        return results

    def get_regional_qa(self):
        """Get questions about regional Queensland"""
        print(f"\n❓ Fetching Regional Queensland Questions...\n")

        # Questions on notice often contain regional issues
        qa_url = f"{self.base_url}/work-of-the-assembly/questions"

        try:
            response = self.session.get(qa_url, timeout=30)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Find question links
            question_links = soup.find_all('a', string=re.compile(r'region|mount isa|north west', re.I))

            print(f"   Found {len(question_links)} relevant questions\n")

            questions = []
            for link in question_links[:20]:
                href = link.get('href')
                if href and not href.startswith('http'):
                    href = f"{self.base_url}{href}"

                questions.append({
                    'question': link.text.strip(),
                    'url': href
                })

                print(f"   • {link.text[:70]}")

            return questions

        except Exception as e:
            print(f"   ❌ Error: {e}")
            return []


# Main execution
if __name__ == '__main__':
    scraper = QLDParliamentScraper()

    all_results = {
        'hansard': [],
        'budget': [],
        'statements': [],
        'questions': []
    }

    # Search terms for Mount Isa
    search_terms = [
        'Mount Isa',
        'North West Queensland',
        'Kalkadoon',
    ]

    # 1. Search Hansard
    print("="*80)
    print("PHASE 1: HANSARD RECORDS")
    print("="*80 + "\n")

    for term in search_terms:
        results = scraper.search_hansard(term, limit=10)
        all_results['hansard'].extend(results)

    # 2. Budget estimates
    print("\n" + "="*80)
    print("PHASE 2: BUDGET ESTIMATES")
    print("="*80 + "\n")

    budget_docs = scraper.get_budget_estimates(2024)
    all_results['budget'] = budget_docs

    # 3. Ministerial statements
    print("\n" + "="*80)
    print("PHASE 3: MINISTERIAL STATEMENTS")
    print("="*80 + "\n")

    for term in search_terms:
        statements = scraper.search_ministerial_statements(term)
        all_results['statements'].extend(statements)

    # 4. Regional Q&A
    print("\n" + "="*80)
    print("PHASE 4: REGIONAL QUESTIONS")
    print("="*80 + "\n")

    questions = scraper.get_regional_qa()
    all_results['questions'] = questions

    # Save results
    print("\n" + "="*80)
    print("💾 SAVING RESULTS")
    print("="*80 + "\n")

    for category, data in all_results.items():
        if data:
            df = pd.DataFrame(data)
            output_file = DATA_DIR / f'parliament_{category}_{datetime.now().strftime("%Y%m%d")}.csv'
            df.to_csv(output_file, index=False)

            print(f"✅ {category}: {len(data)} items → {output_file.name}")

    print("\n" + "="*80)
    print("✅ PARLIAMENT SCRAPE COMPLETE")
    print("="*80 + "\n")

    print("🎯 Summary:")
    print(f"   Hansard mentions: {len(all_results['hansard'])}")
    print(f"   Budget documents: {len(all_results['budget'])}")
    print(f"   Ministerial statements: {len(all_results['statements'])}")
    print(f"   Regional questions: {len(all_results['questions'])}")
    print()

    print("💡 Next steps:")
    print("  1. Download and analyze budget PDFs")
    print("  2. Extract funding amounts from Hansard")
    print("  3. Track ministerial commitments")
    print("  4. Monitor answered questions for data")
    print()
