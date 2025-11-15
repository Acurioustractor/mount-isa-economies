# COMPREHENSIVE DATA SOURCES FOR MOUNT ISA ECONOMIC OBSERVATORY

## CURRENT STATUS: What We Actually Have

### Mount Isa Services (46)
- ✅ Name, description, contact info
- ✅ Categories
- ❌ NO financial data
- ❌ NO employee counts
- ❌ NO revenue data
- ❌ NO funding sources

### Youth Justice Services (1,075)
- ✅ Names
- ❌ MINIMAL descriptions
- ❌ NO financial data
- ❌ NO funding information
- ❌ NO outcomes data

## WHAT WE NEED: World-Class Data Sources

### TIER 1: CRITICAL - Implement Immediately

#### 1. ABN Lookup API
**Purpose:** Get business financial data, employee counts, GST status
**API:** https://abr.business.gov.au/abrxmlsearch/
**Data Available:**
- Entity name, ABN, ACN
- GST registration status
- Business location
- Entity type (company, trust, partnership)
- Registration date
- Trading names

**Implementation:** FREE API with GUID registration
**Value:** Links services to businesses, gets basic financial indicators

#### 2. ASIC Company Data
**Purpose:** Detailed company financials for larger organizations
**API:** https://data.gov.au/dataset/asic-companies
**Data Available:**
- Annual revenue (for companies)
- Asset values
- Directors
- Share structure
- Annual reports

**Implementation:** Scrape from ASIC website or buy bulk data ($$$)
**Value:** Real financial data for incorporated services

#### 3. GrantConnect - FULL Implementation
**Purpose:** ALL government grants to Mount Isa region
**API:** https://www.grants.gov.au/
**Data Available:**
- Grant programs
- Recipients
- Dollar amounts
- Grant dates
- Grant purposes
- Reporting requirements

**Current Status:** Basic scraper fails
**Need:** Professional API integration
**Value:** Track $10M+ in government funding

#### 4. ACNC Charity Register - FIXED Version
**Purpose:** Financial data for ALL charities and non-profits
**API:** https://data.gov.au/dataset/acnc-register
**Data Available:**
- Annual revenue
- Expenses
- Assets
- Employees
- Volunteers
- Beneficiaries
- Program areas

**Current Status:** Download fails
**Need:** Direct CSV download + parsing
**Value:** Financial data for 50+ Mount Isa charities

#### 5. Queensland Government Contracts
**Purpose:** All QLD government spending in Mount Isa region
**API:** https://data.qld.gov.au/dataset/qld-government-contracts
**Data Available:**
- Contract values
- Suppliers
- Departments
- Contract dates
- Descriptions

**Current Status:** Not implemented
**Need:** CKAN API integration
**Value:** Track $100M+ in government spending

---

### TIER 2: HIGH VALUE - Implement This Month

#### 6. ABS Data by Region
**Purpose:** Economic indicators for Mount Isa region
**API:** https://api.data.abs.gov.au/
**Data Available:**
- Employment by industry
- Income levels
- Population demographics
- Business counts by sector
- Economic indicators

**Value:** Macro context for local economy

#### 7. Queensland Budget Papers
**Purpose:** Detailed government spending by region
**Source:** https://budget.qld.gov.au/
**Data Available:**
- Health spending in NW Queensland
- Education funding
- Infrastructure projects
- Regional development grants

**Need:** PDF scraping + data extraction
**Value:** Multi-year funding trends

#### 8. Indigenous Procurement Policy Data
**Purpose:** Government contracts to Indigenous businesses
**Source:** https://www.niaa.gov.au/indigenous-affairs/economic-development/indigenous-procurement-policy
**Data Available:**
- Contract values
- Indigenous businesses
- Federal departments
- Contract types

**Value:** Track Indigenous economic participation

#### 9. Mining Royalties and Economic Contribution
**Purpose:** Mining sector economic data
**Source:** https://www.resources.qld.gov.au/
**Data Available:**
- Royalties by mine
- Employment
- Production volumes
- Economic contribution reports

**Value:** Track $800M+ mining sector impact

#### 10. Job Ads and Labor Market Data
**Purpose:** Employment trends and opportunities
**API:** https://www.jobsandskills.gov.au/data
**Data Available:**
- Job vacancies by region
- Skill demands
- Salary ranges
- Employment growth

**Value:** Track labor market health

---

### TIER 3: ENRICHMENT - Implement Quarterly

#### 11. Web Scraping for Service Details
**Target Sites:**
- Service websites (get updated info)
- Facebook pages (operating hours, reviews)
- Google Places (ratings, photos, hours)
- LinkedIn (employee counts, growth)

**Tools:** BeautifulSoup, Selenium, Scrapy
**Value:** Enrich existing services with current data

#### 12. Social Media Sentiment
**Sources:**
- Facebook page insights
- Twitter mentions
- Google reviews
- Community forums

**Value:** Community perception of services

#### 13. Property Data
**Purpose:** Track commercial real estate, understand business presence
**Source:** https://data.qld.gov.au/dataset/property-sales
**Data Available:**
- Commercial property sales
- Rental prices
- Vacancy rates
- Property types

**Value:** Economic health indicator

#### 14. Education and Training
**Purpose:** Skills development and workforce capacity
**Source:** https://www.myskills.gov.au/
**Data Available:**
- Training providers
- Course offerings
- Completion rates
- Employment outcomes

**Value:** Workforce development tracking

#### 15. Health Services Data
**Purpose:** Health system capacity and usage
**Source:** https://www.health.qld.gov.au/data
**Data Available:**
- Hospital admissions
- Emergency department visits
- Health workforce
- Service availability

**Value:** Health system monitoring

---

## IMPLEMENTATION PRIORITY MATRIX

### Week 1: Fix Critical Data Collection
1. ✅ ABN Lookup API - Get GUID, implement scraper
2. ✅ ACNC - Fix download, parse all charities
3. ✅ GrantConnect - Build proper API client
4. ✅ QLD Contracts - CKAN integration

**Expected Output:** Financial data for 500+ entities

### Week 2: Enrich Existing Services
5. ✅ Web scraping for all 1,121 services
6. ✅ Google Places API for ratings/hours
7. ✅ Facebook scraping for updates
8. ✅ LinkedIn for employee data

**Expected Output:** 80% services with complete data

### Week 3: Government Spending
9. ✅ Queensland Budget data extraction
10. ✅ Indigenous procurement tracking
11. ✅ Mining sector contribution data

**Expected Output:** Track $200M+ government spending

### Week 4: Economic Indicators
12. ✅ ABS regional data
13. ✅ Job market data
14. ✅ Property data

**Expected Output:** Full economic context

---

## TECHNICAL ARCHITECTURE

### Professional Scrapers (Not Current Shit)

```python
# Enterprise-grade scraper with:
- Rate limiting
- Retry logic with exponential backoff
- Proxy rotation
- User agent rotation
- Error handling and logging
- Data validation
- Deduplication
- Change detection
```

### Continuous Updates

```python
# Intelligent scheduler:
- High-value sources: Daily
- Medium value: Weekly
- Low volatility: Monthly
- Change detection triggers immediate update
```

### Data Quality

```python
# Validation pipeline:
- Schema validation
- Completeness checks
- Accuracy verification
- Duplicate detection
- Anomaly detection
- Source verification
```

---

## ESTIMATED DATA VOLUME

After full implementation:

- **Services:** 1,121 → 2,000+ (as we find more)
- **Organizations:** 1,044 → 1,500+
- **Financial Records:** 0 → 1,500+ (annual revenue/expenses)
- **Grants:** 0 → 500+ ($50M+ tracked)
- **Contracts:** 0 → 1,000+ ($200M+ tracked)
- **Economic Indicators:** 0 → 100+ metrics
- **Employment Data:** 0 → 50+ data points

**Total:** From 6,126 mostly empty records → 20,000+ rich, actionable data points

---

## SUCCESS METRICS

### Data Completeness
- 90%+ services with contact info
- 80%+ services with financial data
- 70%+ services with employee counts
- 60%+ services with funding sources

### Data Currency
- 95%+ data less than 30 days old
- 100% critical sources updated weekly
- All government data updated within 24 hours of publication

### Data Quality
- <1% duplicate records
- <5% data quality issues
- 100% source provenance tracked

---

## NEXT ACTIONS

Create these files:
1. `scrapers/abn_lookup_professional.py` - Enterprise ABN scraper
2. `scrapers/acnc_financial_data.py` - Full charity financials
3. `scrapers/grantconnect_api.py` - Proper GrantConnect client
4. `scrapers/qld_contracts_scraper.py` - Government contracts
5. `scrapers/web_enrichment.py` - Scrape service websites
6. `scrapers/google_places.py` - Get ratings/hours/reviews
7. `orchestration/intelligent_scheduler.py` - Smart update system
8. `validation/data_quality.py` - Quality assurance pipeline

**DO THIS NOW. BUILD PROPER SCRAPERS. GET REAL DATA.**
