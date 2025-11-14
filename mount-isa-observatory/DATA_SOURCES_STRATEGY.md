# Mount Isa Economics Observatory - Comprehensive Data Sources Strategy

## Problem Statement
Understanding money flows for youth justice, police, and community safety programs in Mount Isa requires going BEYOND contract disclosures to access:
- Government budget allocations
- Program announcements
- Service provider reports
- Outcomes data
- Media coverage

## Identified Money Flows (2023-2027): ~$134M+

### Youth Justice Programs
1. Intensive On-Country Program - $24M (Mithangkaya Nguli)
2. Youth Co-responder Teams - $78.1M + $11.2M capacity increase
3. Stronger Communities - $7M
4. On Country Trial - $4.2M
5. Early Action Groups - $1.8M
6. Diversionary Centre Upgrade - $4M
7. Additional Magistrate - $4.1M
8. PCYC Upgrade - ~$1M
9. Police accommodation - Part of $684M program
10. Additional case managers - Intensive Family Support

---

## Data Source Categories & Access Methods

### 1. QUEENSLAND GOVERNMENT BUDGET PAPERS ✅

**What it contains:**
- Line-by-line departmental budgets
- Regional action plans
- Service delivery statements
- Capital works programs

**How to access:**
```
Base URL: https://budget.qld.gov.au/
- Budget Papers (Annual, released June/July)
- Regional Delivery Plans (PDF downloads)
- Service Delivery Statements by department
- Budget mapping tool: https://budgetmap.treasury.qld.gov.au/
```

**Key documents for Mount Isa:**
- `/files/Budget-2024-25-SDS-Department-of-Youth-Justice-and-Victim-Support.pdf`
- `/files/Budget_2024-25_SDS_Queensland_Police_Service.pdf`
- `/regional-delivery-plans/north-west-queensland/`

**Scraping strategy:**
1. Download all Service Delivery Statements (SDS) annually
2. Parse PDFs for "Mount Isa", "North West Queensland", "4825"
3. Extract dollar amounts, program names, timelines
4. Track year-over-year changes

**Example findings:**
- Additional magistrate in Mount Isa: $4.1M over 4 years
- Diversionary Centre upgrade: $4M
- Regional infrastructure spending

---

### 2. MINISTERIAL MEDIA STATEMENTS ✅

**What it contains:**
- Funding announcements
- Program launches
- Political commitments
- Specific dollar amounts

**How to access:**
```
Base URL: https://statements.qld.gov.au/

API/Search approach:
- Search by keyword: "Mount Isa" + "youth justice" / "police" / "funding"
- Filter by minister/department
- Date range filtering available
```

**Scraping strategy:**
1. Search all statements containing "Mount Isa"
2. Filter for: youth justice, police, community safety, crime
3. Extract: date, amount, program name, minister, department
4. Create timeline of announcements

**Key statements found:**
- Statement 100887: On-Country program $24M (July 2024)
- Statement 98003: Co-responder team announcement (June 2023)
- Statement 97577: Community grants
- Statement 89527: New funding to tackle youth crime
- Statement 98337: Stronger Communities $7M

**Automation script needed:**
```python
def scrape_ministerial_statements(keywords, date_from, date_to):
    # Search statements.qld.gov.au
    # Parse HTML for funding amounts
    # Extract program details
    # Store in database
```

---

### 3. DEPARTMENT ANNUAL REPORTS ✅

**What it contains:**
- Regional service delivery statistics
- Program outcomes
- Financial performance
- Service center locations

**How to access:**
```
Base URL: https://www.publications.qld.gov.au/

Department of Youth Justice:
- Annual Report 2023-24: resource/3e45ff41-5e61-46c3-9d16-f3116cc70b4c/yj-annual-report-2023-2024.pdf
- Lists Mount Isa service centre explicitly

Queensland Police Service:
- Annual Report 2023-24: https://www.police.qld.gov.au/sites/default/files/2024-09/QPS Annual Report 2023-24.pdf
- Regional policing statistics
```

**Scraping strategy:**
1. Download all departmental annual reports (PDF)
2. OCR/parse for "Mount Isa" mentions
3. Extract service statistics (# of young people served, # of interventions, etc.)
4. Extract outcomes data (reoffending rates, diversion success, etc.)

**Example data points:**
- Mount Isa listed as one of 20+ youth justice service centers
- Regional police statistics
- Program performance metrics

---

### 4. PARLIAMENTARY ESTIMATES HEARINGS ✅

**What it contains:**
- Ministers questioned on spending
- Regional breakdowns requested
- Program justifications
- Specific Mount Isa mentions

**How to access:**
```
Base URL: https://www.parliament.qld.gov.au/Work-of-Committees/Estimates-Hearings

Transcripts: https://documents.parliament.qld.gov.au/

Example:
- 2024 Youth Justice Estimates: /com/EETSC-5CF2/C20242025-8DED/2024_08_01_EstimatesEEC.pdf
```

**Scraping strategy:**
1. Download all Estimates transcripts (PDF)
2. Search for "Mount Isa" mentions
3. Extract context: questions asked, minister responses, dollar amounts
4. Track commitments made

**Example findings:**
- Minister announced Mithangkaya Nguli appointment "just last week in Mount Isa"
- Discussion of On-Country program implementation

---

### 5. PRODUCTIVITY COMMISSION REPORTS ✅

**What it contains:**
- Overcoming Indigenous Disadvantage reports
- Youth justice statistics by state/territory
- Detention rates, recidivism rates
- National benchmarking data

**How to access:**
```
Base URL: https://www.pc.gov.au/

Key reports:
- Overcoming Indigenous Disadvantage 2020: /inquiries-research/overcoming-indigenous-disadvantage/2020/
- Report on Government Services - Youth Justice: /ongoing/report-on-government-services/2024/community-services/youth-justice
- Closing the Gap dashboard: /closing-the-gap-data/dashboard/
```

**Scraping strategy:**
1. Download biennial reports
2. Extract Queensland-specific data
3. Look for regional breakdowns (rare but sometimes available)
4. Track Indigenous youth justice outcomes

**Data limitations:**
- National/state level data mostly
- Mount Isa not usually broken out separately
- But provides context: QLD Aboriginal youth detention rate 22x non-Indigenous

---

### 6. ACNC CHARITY REPORTS ✅

**What it contains:**
- Annual Information Statements
- Financial reports for charities/Indigenous corporations
- Revenue sources (government grants)
- Program descriptions

**How to access:**
```
Base URL: https://www.acnc.gov.au/charity/charities/

Search: "Mount Isa" + filter by Queensland
Or: Direct charity lookup

Mithangkaya Nguli:
- ABN/ICN: Look up via ACNC registry
- Annual reports (if filed)
- Financial statements
```

**Scraping strategy:**
1. Search all charities in Mount Isa (postcode 4825)
2. Filter for: youth services, Indigenous services, community safety
3. Download annual reports
4. Extract: revenue, government grants, program descriptions
5. Match to government funding announcements

**Key organizations found:**
1. **Mithangkaya Nguli** - Young People Ahead Youth and Community Services Indigenous Corporation
   - ACNC link: /charity/charities/02061bf8-38af-e811-a963-000d3ad244fd
   - Programs: Bail Support, Youth Housing, On-Country program ($24M contract)
   - In operation for nearly 40 years
   - "Mithangkaya Nguli" = "To Stand Something Up Always" (Kalkadoon language)

**Next: Find ALL Mount Isa service providers**

---

### 7. MOUNT ISA CITY COUNCIL BUDGET ✅

**What it contains:**
- Local government spending on youth programs
- Community safety initiatives
- Co-funded programs with state government

**How to access:**
```
Base URL: https://www.mountisa.qld.gov.au/

Budget documents: /City-Council/Corporate-Publications/Budgets/Budget-2024-25
Youth Strategy: Mount Isa Youth Strategy 2023-2027
Council meeting minutes
```

**Scraping strategy:**
1. Download annual budgets (PDF)
2. Download Youth Strategy 2023-2027
3. Extract council-funded youth programs
4. Identify state/local co-funding arrangements

**Example:**
- Total budget 2024-25: $110.9 million
- Youth Strategy 2023-2027 contains priorities

---

### 8. AIHW (AUSTRALIAN INSTITUTE OF HEALTH & WELFARE) ✅

**What it contains:**
- Youth Justice in Australia annual reports
- State/territory breakdowns
- Detention statistics
- Community-based supervision data

**How to access:**
```
Base URL: https://www.aihw.gov.au/

Youth Justice reports: /reports/youth-justice/
- Youth Justice in Australia 2023-24
- Data tables and appendices
- State/territory systems descriptions
```

**Scraping strategy:**
1. Download annual Youth Justice in Australia reports
2. Extract Queensland-specific data
3. Look for regional breakdowns (rare)
4. Track trends in youth detention, supervision

**Data available:**
- Queensland youth justice system description
- Policies and programs
- Statistical trends
- But NOT Mount Isa-specific

---

### 9. LOCAL MEDIA - NORTH WEST STAR ✅

**What it contains:**
- Local coverage of funding announcements
- Community reaction
- Implementation progress
- Outcomes reporting

**How to access:**
```
Base URL: https://www.northweststar.com.au/

Sections:
- /news/court-crime/
- Search function for articles
```

**Scraping strategy:**
1. Search for: "youth crime", "funding", "police", "youth justice"
2. Extract: dates, amounts, programs mentioned
3. Identify local organizations/people involved
4. Track implementation progress

**Example articles found:**
- Taskforce Guardian youth crime crackdown (May 2024)
- PCYC $1M upgrade (Sept 2023)
- Ministers speaking out on youth crime
- Crime statistics reporting

---

### 10. QUEENSLAND PARLIAMENT - COMMITTEE REPORTS ✅

**What it contains:**
- Youth Justice Reform Select Committee
- Inquiries into youth crime
- Regional consultations
- Recommendations

**How to access:**
```
Base URL: https://www.parliament.qld.gov.au/Work-of-Committees/

Youth Justice Reform Select Committee: /Committees/Committee-Details?cid=232&id=4295
Tabled papers and reports
```

**Scraping strategy:**
1. Download all committee reports on youth justice
2. Search for Mount Isa mentions
3. Extract recommendations
4. Track government responses

---

### 11. FOI (FREEDOM OF INFORMATION) REQUESTS 💡

**What it could contain:**
- Detailed regional spending breakdowns
- Program-specific budgets for Mount Isa
- Youth justice staffing numbers
- Detailed outcomes data

**How to access:**
```
QLD Right to Information:
- Portal: https://www.oic.qld.gov.au/
- Can request specific spending data for Mount Isa region

Example requests:
1. "Youth justice program spending in Mount Isa 2020-2025 by program"
2. "Police operational budget for Mount Isa station 2020-2025"
3. "Outcomes data for On-Country program participants"
```

**Strategy:**
- File targeted FOI requests for data NOT publicly available
- Request spreadsheets/databases (easier to process than PDFs)
- Focus on: regional breakdowns, outcomes data, staffing numbers

---

## IMPLEMENTATION PRIORITY

### Phase 1: Automated Scrapers (1-2 weeks)

1. **Media Statements Scraper**
   ```python
   # Scrape statements.qld.gov.au for Mount Isa mentions
   # Extract: date, minister, department, $ amount, program
   # Store in database
   ```

2. **Budget Papers Downloader**
   ```python
   # Download all Service Delivery Statements
   # Parse PDFs for Mount Isa/North West Queensland
   # Extract financial data
   ```

3. **ACNC Charity Searcher**
   ```python
   # Search ACNC for Mount Isa charities (postcode 4825)
   # Download annual reports
   # Extract government grant revenue
   ```

### Phase 2: Document Analysis (2-3 weeks)

4. **Annual Reports Processor**
   - Download Youth Justice + QPS annual reports (5 years)
   - OCR and search for Mount Isa
   - Extract service statistics

5. **Estimates Transcripts Analyzer**
   - Download Estimates hearings transcripts
   - Search for Mount Isa mentions
   - Extract commitments

6. **North West Star Archive Scraper**
   - Scrape local newspaper articles
   - Build timeline of local coverage

### Phase 3: Outcomes & Analysis (ongoing)

7. **Outcomes Data Tracker**
   - Combine program spending with outcomes
   - Track: reoffending rates, diversion success, community safety metrics
   - Link money flows to results

8. **Money Flow Visualization**
   - Map: Government → Programs → Service Providers → Outcomes
   - Show: $134M+ flows through Mount Isa youth justice system
   - Interactive dashboard

---

## DATA SCHEMA

### Programs Table
```sql
CREATE TABLE programs (
    id SERIAL PRIMARY KEY,
    name TEXT,
    description TEXT,
    total_funding DECIMAL,
    funding_period TEXT,
    announced_date DATE,
    source_url TEXT,
    department TEXT,
    region TEXT
);
```

### Service Providers Table
```sql
CREATE TABLE service_providers (
    id SERIAL PRIMARY KEY,
    name TEXT,
    acnc_id TEXT,
    abn TEXT,
    location TEXT,
    programs_delivered TEXT[],
    total_revenue DECIMAL,
    government_grants DECIMAL,
    year INT
);
```

### Outcomes Table
```sql
CREATE TABLE outcomes (
    id SERIAL PRIMARY KEY,
    program_id INT REFERENCES programs(id),
    metric_name TEXT,
    metric_value DECIMAL,
    reporting_period TEXT,
    source_url TEXT
);
```

### Media Coverage Table
```sql
CREATE TABLE media_coverage (
    id SERIAL PRIMARY KEY,
    publication TEXT,
    title TEXT,
    date DATE,
    url TEXT,
    programs_mentioned TEXT[],
    amounts_mentioned DECIMAL[]
);
```

---

## SUCCESS METRICS

After implementing this strategy, we should be able to answer:

1. **Total spending**: How much has been allocated to youth justice/police in Mount Isa (2020-2025)?
   - Current answer: **$134M+ identified** (2023-2027)

2. **Program breakdown**: What programs received funding and how much?
   - Current: 10+ programs identified with specific amounts

3. **Service providers**: Who delivers these services?
   - Current: Mithangkaya Nguli confirmed for $24M On-Country program

4. **Outcomes**: What results have these programs achieved?
   - Gap: Need to scrape annual reports and outcomes data

5. **Money flow**: Government → Programs → Providers → Outcomes
   - Partially mapped, need complete flow visualization

6. **Timeline**: When were programs announced/implemented?
   - Can be built from media statements + budget papers

---

## NEXT STEPS

1. Build media statements scraper (highest ROI)
2. Create ACNC Mount Isa charity database
3. Download and parse budget papers (5 years)
4. Set up Supabase tables for data storage
5. Build dashboard showing money flows
6. File FOI requests for missing data

**The contract disclosures were the WRONG data source. This strategy gets us the RIGHT data.**
