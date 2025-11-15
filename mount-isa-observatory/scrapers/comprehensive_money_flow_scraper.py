"""
Mount Isa Money Flow - Comprehensive Data Collection Framework

Orchestrates scraping from all identified data sources:
1. Media Statements (QLD Gov)
2. Budget Papers (Service Delivery Statements)
3. Annual Reports (Youth Justice, QPS)
4. ACNC Charity Data (Mithangkaya Nguli + all Mount Isa charities)
5. Parliamentary Hansard & Questions on Notice
6. Federal Grants (GrantConnect)
7. Mount Isa City Council
8. Audit Office Reports

Saves everything to unified database structure.
"""
import pandas as pd
from pathlib import Path
from datetime import datetime
import requests
from bs4 import BeautifulSoup
import time
import json
import re

BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data' / 'money_flows'
DATA_DIR.mkdir(parents=True, exist_ok=True)

print("\n" + "="*80)
print("💰 MOUNT ISA MONEY FLOW - COMPREHENSIVE DATA COLLECTION")
print("="*80 + "\n")

# ============================================================================
# DATA SOURCES CONFIGURATION
# ============================================================================

DATA_SOURCES = {
    'media_statements': {
        'enabled': True,
        'priority': 1,
        'description': 'QLD Government ministerial media statements',
        'base_url': 'https://statements.qld.gov.au/statements',
        'known_ids': [100887, 98003, 97577, 89527, 98337, 100864, 97933, 97218, 100544, 97930]
    },
    'budget_papers': {
        'enabled': True,
        'priority': 2,
        'description': 'Service Delivery Statements & Budget Papers',
        'urls': [
            'https://budget.qld.gov.au/files/Budget-2024-25-SDS-Department-of-Youth-Justice-and-Victim-Support.pdf',
            'https://budget.qld.gov.au/files/Budget_2024-25_SDS_Queensland_Police_Service.pdf',
            'https://budget.qld.gov.au/regional-delivery-plans/north-west-queensland/'
        ]
    },
    'acnc_charities': {
        'enabled': True,
        'priority': 3,
        'description': 'ACNC charity financial reports',
        'search_postcode': '4825',
        'known_charities': [
            {
                'name': 'Mithangkaya Nguli - Young People Ahead',
                'acnc_id': '02061bf8-38af-e811-a963-000d3ad244fd'
            }
        ]
    },
    'annual_reports': {
        'enabled': True,
        'priority': 4,
        'description': 'Department annual reports',
        'departments': [
            {
                'name': 'Department of Youth Justice',
                'base_url': 'https://www.publications.qld.gov.au',
                'years': ['2023-24', '2022-23', '2021-22']
            },
            {
                'name': 'Queensland Police Service',
                'base_url': 'https://www.police.qld.gov.au',
                'years': ['2023-24', '2022-23', '2021-22']
            }
        ]
    },
    'parliament': {
        'enabled': True,
        'priority': 5,
        'description': 'Hansard, Questions on Notice, Committee Reports',
        'hansard_search': 'https://www.parliament.qld.gov.au/work-of-assembly/hansard',
        'qon_search': 'https://www.parliament.qld.gov.au/work-of-assembly/questions-on-notice'
    },
    'federal_grants': {
        'enabled': True,
        'priority': 6,
        'description': 'GrantConnect federal grants database',
        'base_url': 'https://www.grants.gov.au',
        'search_terms': ['Mount Isa', 'Mithangkaya Nguli', '4825']
    },
    'council_budget': {
        'enabled': True,
        'priority': 7,
        'description': 'Mount Isa City Council budget & annual reports',
        'base_url': 'https://www.mountisa.qld.gov.au',
        'budget_url': '/City-Council/Corporate-Publications/Budgets/Budget-2024-25'
    },
    'audit_office': {
        'enabled': True,
        'priority': 8,
        'description': 'Queensland Audit Office reports',
        'base_url': 'https://www.qao.qld.gov.au',
        'search_terms': ['youth justice', 'regional services']
    }
}

# ============================================================================
# UNIFIED DATA SCHEMA
# ============================================================================

class MoneyFlowRecord:
    """Unified data model for all money flow records"""
    def __init__(self):
        self.source = None              # Which data source
        self.record_type = None         # announcement, budget, actual_payment, report
        self.date = None                # Date of record
        self.amount = None              # Dollar amount
        self.amount_type = None         # announced, allocated, spent
        self.program_name = None        # Program receiving funding
        self.recipient_org = None       # Organization receiving money
        self.recipient_abn = None       # ABN if known
        self.funding_body = None        # Who's providing the money
        self.description = None         # Full description
        self.url = None                 # Source URL
        self.extracted_date = None      # When we scraped it
        self.mount_isa_relevance = None # High/Medium/Low
        self.validation_status = None   # verified, unverified, conflicting

# ============================================================================
# SCRAPER 1: MEDIA STATEMENTS (Already working!)
# ============================================================================

def scrape_media_statements():
    """Import and run the media statements scraper"""
    print("📰 [1/8] Scraping Media Statements...")

    # Use the existing scraper
    from mount_isa_media_statements import fetch_statement, KNOWN_STATEMENTS

    records = []
    for stmt in KNOWN_STATEMENTS:
        data = fetch_statement(stmt['id'])

        # Convert to MoneyFlowRecord format
        for amount in data.get('amounts_mentioned', []):
            record = {
                'source': 'media_statement',
                'record_type': 'announcement',
                'date': data.get('date'),
                'amount': amount,
                'amount_type': 'announced',
                'program_name': ', '.join(data.get('programs_mentioned', [])),
                'description': data.get('title'),
                'url': data.get('url'),
                'extracted_date': datetime.now().isoformat(),
                'mount_isa_relevance': 'High',
                'raw_data': data
            }
            records.append(record)

        time.sleep(1)

    print(f"  ✅ Found {len(records)} funding records\n")
    return records

# ============================================================================
# SCRAPER 2: ACNC CHARITY DATA
# ============================================================================

def scrape_acnc_charities():
    """Scrape ACNC for Mount Isa charities and their financials"""
    print("🏛️  [2/8] Scraping ACNC Charity Data...")

    records = []

    # Search for Mount Isa charities
    search_url = "https://www.acnc.gov.au/charity/advanced-charity-search"

    # Known charities
    for charity in DATA_SOURCES['acnc_charities']['known_charities']:
        acnc_url = f"https://www.acnc.gov.au/charity/charities/{charity['acnc_id']}"

        try:
            response = requests.get(acnc_url, timeout=30)
            soup = BeautifulSoup(response.content, 'html.parser')

            # Look for financial data tables
            # ACNC shows: Total revenue, Government grants, Expenses

            record = {
                'source': 'acnc',
                'record_type': 'actual_payment',
                'recipient_org': charity['name'],
                'url': acnc_url,
                'extracted_date': datetime.now().isoformat(),
                'mount_isa_relevance': 'High',
                'note': 'Financial data available at ACNC registry'
            }
            records.append(record)

            print(f"  ✅ {charity['name']}")
            time.sleep(2)

        except Exception as e:
            print(f"  ⚠️  Error: {e}")

    print(f"  ✅ Found {len(records)} charity records\n")
    return records

# ============================================================================
# SCRAPER 3: BUDGET PAPERS (PDF Download & Parse)
# ============================================================================

def scrape_budget_papers():
    """Download and parse budget PDFs for Mount Isa allocations"""
    print("📊 [3/8] Scraping Budget Papers...")

    records = []

    for url in DATA_SOURCES['budget_papers']['urls']:
        print(f"  Downloading: {url.split('/')[-1][:50]}...")

        try:
            # Download PDF or HTML
            if url.endswith('.pdf'):
                # Would use PyPDF2 or pdfplumber here
                record = {
                    'source': 'budget_papers',
                    'record_type': 'budget_allocation',
                    'amount_type': 'allocated',
                    'url': url,
                    'extracted_date': datetime.now().isoformat(),
                    'note': 'PDF requires manual parsing or OCR'
                }
                records.append(record)
            else:
                # HTML page
                response = requests.get(url, timeout=30)
                soup = BeautifulSoup(response.content, 'html.parser')

                # Search for "Mount Isa" mentions
                text = soup.get_text()
                if 'mount isa' in text.lower():
                    # Extract context
                    sentences = text.split('.')
                    for sentence in sentences:
                        if 'mount isa' in sentence.lower():
                            amounts = re.findall(r'\$[\d,]+(?:\.\d+)?\s*(?:million|billion)?', sentence, re.I)
                            if amounts:
                                record = {
                                    'source': 'budget_papers',
                                    'record_type': 'budget_allocation',
                                    'amount': amounts[0],
                                    'amount_type': 'allocated',
                                    'description': sentence.strip(),
                                    'url': url,
                                    'extracted_date': datetime.now().isoformat(),
                                    'mount_isa_relevance': 'High'
                                }
                                records.append(record)

            time.sleep(2)

        except Exception as e:
            print(f"  ⚠️  Error: {e}")

    print(f"  ✅ Found {len(records)} budget records\n")
    return records

# ============================================================================
# SCRAPER 4: ANNUAL REPORTS
# ============================================================================

def scrape_annual_reports():
    """Download department annual reports and extract Mount Isa data"""
    print("📄 [4/8] Scraping Annual Reports...")

    records = []

    # Known annual report URLs
    reports = [
        {
            'dept': 'Youth Justice',
            'url': 'https://www.publications.qld.gov.au/ckan-publications-attachments-prod/resources/3e45ff41-5e61-46c3-9d16-f3116cc70b4c/yj-annual-report-2023-2024.pdf',
            'year': '2023-24'
        },
        {
            'dept': 'QPS',
            'url': 'https://www.police.qld.gov.au/sites/default/files/2024-09/QPS Annual Report 2023-24.pdf',
            'year': '2023-24'
        }
    ]

    for report in reports:
        print(f"  {report['dept']} {report['year']}")

        record = {
            'source': 'annual_report',
            'record_type': 'report',
            'funding_body': report['dept'],
            'date': report['year'],
            'url': report['url'],
            'extracted_date': datetime.now().isoformat(),
            'note': 'PDF requires OCR/parsing for Mount Isa mentions'
        }
        records.append(record)

    print(f"  ✅ Found {len(records)} annual reports\n")
    return records

# ============================================================================
# SCRAPER 5: PARLIAMENT - HANSARD & QUESTIONS ON NOTICE
# ============================================================================

def scrape_parliament():
    """Search Parliament records for Mount Isa youth justice mentions"""
    print("🏛️  [5/8] Scraping Parliament Records...")

    records = []

    # Known Questions on Notice about Mount Isa
    # These would come from searching the Parliament website
    # For now, we'll note that they exist and need manual access

    record = {
        'source': 'parliament',
        'record_type': 'parliamentary_question',
        'description': 'Questions on Notice about Mount Isa youth justice spending',
        'url': 'https://www.parliament.qld.gov.au/work-of-assembly/questions-on-notice',
        'extracted_date': datetime.now().isoformat(),
        'note': 'Search required: "Mount Isa" + "youth justice" + "funding"'
    }
    records.append(record)

    # Estimates hearing transcripts (we already identified these)
    estimates_records = [
        {
            'source': 'parliament',
            'record_type': 'estimates_hearing',
            'date': '2024-08-01',
            'description': 'Minister announced Mithangkaya Nguli appointment in Mount Isa',
            'url': 'https://documents.parliament.qld.gov.au/com/EETSC-5CF2/C20242025-8DED/2024_08_01_EstimatesEEC.pdf',
            'extracted_date': datetime.now().isoformat(),
            'mount_isa_relevance': 'High'
        }
    ]
    records.extend(estimates_records)

    print(f"  ✅ Found {len(records)} parliamentary records\n")
    return records

# ============================================================================
# SCRAPER 6: FEDERAL GRANTCONNECT
# ============================================================================

def scrape_federal_grants():
    """Search GrantConnect for federal grants to Mount Isa"""
    print("🇦🇺 [6/8] Scraping Federal Grants (GrantConnect)...")

    records = []

    # GrantConnect API endpoint
    base_url = "https://www.grants.gov.au"

    # Search terms
    search_terms = ['Mount Isa', 'Mithangkaya Nguli', 'North West Queensland']

    for term in search_terms:
        print(f"  Searching: {term}")

        # Note: GrantConnect doesn't have a public API, would need to scrape HTML
        # or use their data downloads

        record = {
            'source': 'grantconnect',
            'record_type': 'federal_grant',
            'description': f'Federal grants search: {term}',
            'url': f'{base_url}/?event=public.search&term={term.replace(" ", "+")}',
            'extracted_date': datetime.now().isoformat(),
            'note': 'Requires HTML scraping or data download'
        }
        records.append(record)

    # Known federal programs that might fund Mount Isa
    federal_programs = [
        {
            'source': 'grantconnect',
            'record_type': 'federal_program',
            'program_name': 'Indigenous Advancement Strategy',
            'funding_body': 'NIAA',
            'url': 'https://www.niaa.gov.au/indigenous-affairs/grants-and-funding',
            'extracted_date': datetime.now().isoformat(),
            'mount_isa_relevance': 'Medium',
            'note': 'May have Mount Isa recipients - requires detailed search'
        },
        {
            'source': 'grantconnect',
            'record_type': 'federal_program',
            'program_name': 'Safer Communities Fund',
            'funding_body': 'Department of Home Affairs',
            'url': 'https://www.homeaffairs.gov.au/about-us/grants-and-tenders/grants',
            'extracted_date': datetime.now().isoformat(),
            'mount_isa_relevance': 'Medium'
        }
    ]
    records.extend(federal_programs)

    print(f"  ✅ Found {len(records)} federal grant records\n")
    return records

# ============================================================================
# SCRAPER 7: MOUNT ISA CITY COUNCIL
# ============================================================================

def scrape_council_budget():
    """Download Mount Isa City Council budget and annual reports"""
    print("🏢 [7/8] Scraping Mount Isa City Council Budget...")

    records = []

    base_url = "https://www.mountisa.qld.gov.au"

    # Known council documents
    council_docs = [
        {
            'name': 'Budget 2024-25',
            'url': f'{base_url}/City-Council/Corporate-Publications/Budgets/Budget-2024-25',
            'amount': '$110.9 million',
            'description': 'Total council budget 2024-25'
        },
        {
            'name': 'Youth Strategy 2023-2027',
            'url': 'https://issuu.com/mountisa7/docs/atria_group_mount_isa_city_council_youth_strategy_',
            'description': 'Mount Isa Youth Strategy - contains youth program priorities'
        },
        {
            'name': 'Annual Report 2023-24',
            'url': f'{base_url}/City-Council/Corporate-Publications/',
            'description': 'Council annual report with program outcomes'
        }
    ]

    for doc in council_docs:
        print(f"  {doc['name']}")

        record = {
            'source': 'council_budget',
            'record_type': 'council_document',
            'description': doc['description'],
            'url': doc['url'],
            'amount': doc.get('amount'),
            'extracted_date': datetime.now().isoformat(),
            'mount_isa_relevance': 'High',
            'note': 'Requires PDF/HTML download and parsing'
        }
        records.append(record)

    print(f"  ✅ Found {len(records)} council records\n")
    return records

# ============================================================================
# SCRAPER 8: QUEENSLAND AUDIT OFFICE
# ============================================================================

def scrape_audit_reports():
    """Search QAO for youth justice and regional service audits"""
    print("📋 [8/8] Scraping Queensland Audit Office Reports...")

    records = []

    base_url = "https://www.qao.qld.gov.au"

    # Known relevant audit reports
    audit_reports = [
        {
            'title': 'Managing repeat offenders in youth justice',
            'date': '2024',
            'url': f'{base_url}/reports-resources/reports-parliament',
            'description': 'Performance audit of youth justice programs',
            'relevance': 'High - may contain Mount Isa data'
        },
        {
            'title': 'Regional service delivery',
            'url': f'{base_url}/reports-resources/reports-parliament',
            'description': 'Audits of regional government service delivery',
            'relevance': 'Medium - may include North West Queensland'
        },
        {
            'title': 'Police resources in regional Queensland',
            'url': f'{base_url}/reports-resources/reports-parliament',
            'description': 'Audit of police resourcing in regional areas',
            'relevance': 'Medium - may include Mount Isa station'
        }
    ]

    for report in audit_reports:
        print(f"  {report['title']}")

        record = {
            'source': 'audit_office',
            'record_type': 'audit_report',
            'description': report['description'],
            'date': report.get('date'),
            'url': report['url'],
            'extracted_date': datetime.now().isoformat(),
            'mount_isa_relevance': report['relevance'],
            'note': 'Search QAO website for specific reports'
        }
        records.append(record)

    print(f"  ✅ Found {len(records)} audit records\n")
    return records

# ============================================================================
# MAIN ORCHESTRATOR
# ============================================================================

def run_comprehensive_scrape():
    """Run all scrapers and combine results"""

    all_records = []

    # Run each scraper in priority order
    scrapers = [
        ('media_statements', scrape_media_statements),
        ('acnc_charities', scrape_acnc_charities),
        ('budget_papers', scrape_budget_papers),
        ('annual_reports', scrape_annual_reports),
        ('parliament', scrape_parliament),
        ('federal_grants', scrape_federal_grants),
        ('council_budget', scrape_council_budget),
        ('audit_reports', scrape_audit_reports),
    ]

    for source_name, scraper_func in scrapers:
        if DATA_SOURCES.get(source_name, {}).get('enabled', False):
            try:
                records = scraper_func()
                all_records.extend(records)
            except Exception as e:
                print(f"  ⚠️  Error in {source_name}: {e}\n")

    # Convert to DataFrame
    df = pd.DataFrame(all_records)

    # Save comprehensive dataset
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = DATA_DIR / f'mount_isa_money_flows_{timestamp}.csv'
    df.to_csv(output_file, index=False)

    # Save JSON for detailed data
    json_file = DATA_DIR / f'mount_isa_money_flows_{timestamp}.json'
    with open(json_file, 'w') as f:
        json.dump(all_records, f, indent=2, default=str)

    print("\n" + "="*80)
    print("📊 COMPREHENSIVE DATA COLLECTION COMPLETE")
    print("="*80 + "\n")

    print(f"Total records collected: {len(all_records)}")
    print(f"\nBy source:")
    if len(df) > 0:
        print(df['source'].value_counts().to_string())

        print(f"\n\nBy record type:")
        print(df['record_type'].value_counts().to_string())

    print(f"\n💾 Saved:")
    print(f"  CSV: {output_file}")
    print(f"  JSON: {json_file}\n")

    return df

if __name__ == '__main__':
    df = run_comprehensive_scrape()
