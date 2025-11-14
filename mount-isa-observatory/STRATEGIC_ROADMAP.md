# Mount Isa Economic Observatory - Strategic Roadmap

**Vision**: World-class platform for understanding money flows in Australian communities, starting with Mount Isa youth justice, expanding to all sectors and communities.

**First Principles**: Follow the money from announcement → allocation → contract → payment → outcome

---

## Current State (What We Have)

### ✅ Completed
- **$33.88M identified** in Mount Isa youth justice funding (2020-2027)
- **10 media statements** scraped (bypassed 403 blocks with Firecrawl)
- **Key organizations** identified (Mithangkaya Nguli, Queensland Youth Services, 54 Reasons)
- **Programs mapped** (On-Country, Co-responder, Stronger Communities)
- **Outcomes documented** (73% reoffending reduction)
- **World-class .env management** (protected, validated, documented)
- **Working scrapers** (media statements, ABN lookup, Firecrawl integration)

### 📊 Data Quality
- **Announcements**: High confidence (official media statements)
- **Allocations**: Medium (need budget paper parsing)
- **Payments**: Low (need financial report verification)
- **Outcomes**: Medium (Co-responder data strong, On-Country pending)

---

## Phase 1: Complete Mount Isa Youth Justice (Next 2-4 weeks)

### 1.1 Fill Data Gaps

**Priority 1: Verify Actual Payments**
```
Goal: Confirm $24M actually reached Mithangkaya Nguli

Data Sources:
1. ACNC Financial Reports (Mithangkaya Nguli)
   - Download 5 years of annual reports
   - Extract: Total revenue, government grants, program spending
   - Match: $24M announcement → actual revenue received

2. Queensland Budget Papers (Service Delivery Statements)
   - Parse PDFs for Mount Isa allocations
   - Extract: Youth Justice & QPS budget line items
   - Track: Announced → budgeted → spent

3. Annual Reports (Dept of Youth Justice, QPS)
   - OCR/parse for Mount Isa mentions
   - Extract: Service statistics, client numbers, spending
   - Connect: Money → services delivered

4. Parliamentary Records
   - Questions on Notice about Mount Isa spending
   - Estimates hearing transcripts
   - Committee reports
```

**Priority 2: Complete Outcomes Mapping**
```
Programs with Known Outcomes:
✅ Youth Co-responder: 73% reoffending reduction
⏳ On-Country: Just launched (July 2024) - track quarterly
⏳ Stronger Communities: $7M invested - outcomes pending

Data Sources:
- Quarterly performance reports (Dept of Youth Justice)
- Crime statistics (QPS, ABS)
- Academic studies (Griffith, QUT, UQ)
- Media coverage (implementation progress)
- Community feedback (Mount Isa City Council)
```

**Priority 3: Build Complete Organization Profiles**
```
For Each Recipient Organization:

Mithangkaya Nguli:
- ABN: [lookup]
- ACNC registration: ✅ Confirmed
- Programs delivered: On-Country ($24M), other services
- Financial history: 5 years revenue, expenses, assets
- Key people: Board, management
- Track record: 40 years operation
- Outcomes: [collect from reports]

Queensland Youth Services:
- Grant: $130K (Proud Warrior)
- [Build full profile]

54 Reasons:
- Grant: $300K (Back to Community)
- [Build full profile]
```

### 1.2 Data Collection Automation

**Build Scrapers for Missing Sources**

```python
# Priority order for scraper development

1. ACNC Financial Report Downloader
   - Input: Organization name or ACN
   - Output: 5 years of annual reports (PDFs)
   - Extract: Financial summary data
   - Status: High priority - verifies actual payments

2. Budget Paper Parser
   - Input: PDF URLs (Youth Justice SDS, QPS SDS)
   - Output: Extracted tables, Mount Isa mentions
   - Use: pdfplumber or camelot-py
   - Status: High priority - confirms allocations

3. Annual Report Parser
   - Input: Department annual reports (PDFs)
   - Output: Mount Isa mentions, statistics, spending
   - OCR if needed (pytesseract)
   - Status: Medium priority

4. Parliamentary Records Scraper
   - Questions on Notice database search
   - Estimates hearing transcript download
   - Extract: Mount Isa funding mentions
   - Status: Medium priority

5. GrantConnect Scraper
   - Federal grants search
   - Filter: Mount Isa recipients
   - Extract: Grant details, amounts, dates
   - Status: Lower priority (smaller amounts)
```

---

## Phase 2: Supabase Database Design (Week 3-4)

### 2.1 Core Schema

**Design Principles**:
- Normalized (no duplication)
- Trackable (full audit trail)
- Linkable (connect everything)
- Scalable (works for 100+ communities)
- Temporal (track changes over time)

**Schema**:

```sql
-- ============================================================================
-- ORGANIZATIONS
-- ============================================================================
CREATE TABLE organizations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    abn VARCHAR(11) UNIQUE,
    acn VARCHAR(9),
    name TEXT NOT NULL,
    legal_name TEXT,
    organization_type VARCHAR(50), -- 'charity', 'government', 'private', 'nfp'

    -- ACNC data
    acnc_registration_status VARCHAR(20),
    charity_size VARCHAR(20), -- 'small', 'medium', 'large'

    -- Location
    primary_location VARCHAR(100), -- 'Mount Isa', 'Brisbane', etc.
    addresses JSONB,

    -- Indigenous status
    indigenous_controlled BOOLEAN,
    indigenous_focused BOOLEAN,

    -- Metadata
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    data_sources JSONB -- Track where data came from
);

-- ============================================================================
-- PROGRAMS
-- ============================================================================
CREATE TABLE programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    official_name TEXT,
    program_code VARCHAR(50),

    -- Classification
    sector VARCHAR(50), -- 'youth_justice', 'health', 'education', etc.
    program_type VARCHAR(50), -- 'intervention', 'prevention', 'enforcement'

    -- Scope
    geographic_scope VARCHAR(50), -- 'Mount Isa', 'North West QLD', 'Statewide'
    target_population TEXT,

    -- Description
    description TEXT,
    objectives JSONB,

    -- Timeframe
    start_date DATE,
    end_date DATE,

    -- Administering body
    department_id UUID REFERENCES organizations(id),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- FUNDING ANNOUNCEMENTS
-- ============================================================================
CREATE TABLE funding_announcements (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- What
    program_id UUID REFERENCES programs(id),
    recipient_org_id UUID REFERENCES organizations(id),
    funding_body_id UUID REFERENCES organizations(id),

    -- How much
    amount_announced DECIMAL(15,2),
    amount_currency VARCHAR(3) DEFAULT 'AUD',
    funding_period_years INTEGER,

    -- When
    announcement_date DATE NOT NULL,
    funding_start_date DATE,
    funding_end_date DATE,

    -- Who announced
    minister VARCHAR(100),
    government VARCHAR(50), -- 'QLD State', 'Federal', 'Local'

    -- Source
    source_type VARCHAR(50), -- 'media_statement', 'budget_paper', 'press_release'
    source_url TEXT,
    source_document_id UUID REFERENCES documents(id),
    statement_id VARCHAR(50), -- e.g., '100887'

    -- Content
    title TEXT,
    description TEXT,
    key_points JSONB,

    -- Confidence
    confidence_score INTEGER CHECK (confidence_score BETWEEN 1 AND 5),
    verification_status VARCHAR(20), -- 'verified', 'unverified', 'conflicting'

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- BUDGET ALLOCATIONS
-- ============================================================================
CREATE TABLE budget_allocations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Links to announcement (if exists)
    announcement_id UUID REFERENCES funding_announcements(id),

    -- What
    program_id UUID REFERENCES programs(id),
    recipient_org_id UUID REFERENCES organizations(id),

    -- How much
    budget_amount DECIMAL(15,2) NOT NULL,
    financial_year VARCHAR(9), -- '2024-25'

    -- Source
    budget_paper_year INTEGER,
    department VARCHAR(100),
    source_document_id UUID REFERENCES documents(id),
    page_number INTEGER,
    table_reference VARCHAR(50),

    -- Classification
    budget_line_item TEXT,
    appropriation_type VARCHAR(50), -- 'operational', 'capital', 'grant'

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- ACTUAL PAYMENTS
-- ============================================================================
CREATE TABLE actual_payments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Links
    announcement_id UUID REFERENCES funding_announcements(id),
    allocation_id UUID REFERENCES budget_allocations(id),
    program_id UUID REFERENCES programs(id),

    -- Who paid whom
    payer_org_id UUID REFERENCES organizations(id), -- Government dept
    payee_org_id UUID REFERENCES organizations(id), -- Recipient

    -- How much
    amount_paid DECIMAL(15,2) NOT NULL,
    payment_date DATE,
    financial_year VARCHAR(9),

    -- Source
    source_type VARCHAR(50), -- 'annual_report', 'acnc_report', 'financial_statement'
    source_document_id UUID REFERENCES documents(id),

    -- Details
    payment_type VARCHAR(50), -- 'grant', 'contract', 'subsidy'
    contract_number VARCHAR(50),

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- OUTCOMES
-- ============================================================================
CREATE TABLE program_outcomes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- What program
    program_id UUID REFERENCES programs(id) NOT NULL,
    organization_id UUID REFERENCES organizations(id), -- Service provider

    -- When
    measurement_date DATE,
    reporting_period_start DATE,
    reporting_period_end DATE,

    -- Outcome metrics
    metric_name VARCHAR(100), -- 'reoffending_rate', 'clients_served', etc.
    metric_value DECIMAL(15,4),
    metric_unit VARCHAR(50), -- 'percent', 'count', 'rate'

    -- Comparison
    baseline_value DECIMAL(15,4),
    target_value DECIMAL(15,4),

    -- Context
    sample_size INTEGER,
    methodology TEXT,

    -- Source
    source_type VARCHAR(50), -- 'performance_report', 'evaluation', 'audit'
    source_document_id UUID REFERENCES documents(id),

    -- Quality
    confidence_level VARCHAR(20), -- 'high', 'medium', 'low'
    peer_reviewed BOOLEAN DEFAULT FALSE,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- DOCUMENTS
-- ============================================================================
CREATE TABLE documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Document details
    title TEXT,
    document_type VARCHAR(50), -- 'media_statement', 'budget_paper', 'annual_report'
    url TEXT,
    file_path TEXT, -- Local storage path

    -- Content
    full_text TEXT, -- Extracted content
    summary TEXT,

    -- Metadata
    publication_date DATE,
    author_organization_id UUID REFERENCES organizations(id),

    -- Processing
    scraped_at TIMESTAMP,
    processed_at TIMESTAMP,
    extraction_method VARCHAR(50), -- 'firecrawl', 'pdf_parse', 'ocr'

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- GEOGRAPHY (for expansion to multiple communities)
-- ============================================================================
CREATE TABLE geographies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL,
    geography_type VARCHAR(50), -- 'city', 'region', 'state', 'lga'
    parent_geography_id UUID REFERENCES geographies(id),

    -- Location
    latitude DECIMAL(10,8),
    longitude DECIMAL(11,8),
    boundary GEOMETRY(POLYGON, 4326), -- PostGIS

    -- Demographics
    population INTEGER,
    indigenous_population INTEGER,
    indigenous_percentage DECIMAL(5,2),

    -- Economic
    median_income DECIMAL(10,2),
    unemployment_rate DECIMAL(5,2),

    census_year INTEGER,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- CROSS-REFERENCE TABLE (Links funding across sources)
-- ============================================================================
CREATE TABLE funding_cross_references (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- Link different funding records that refer to same money
    announcement_id UUID REFERENCES funding_announcements(id),
    allocation_id UUID REFERENCES budget_allocations(id),
    payment_id UUID REFERENCES actual_payments(id),

    -- Confidence in link
    match_confidence VARCHAR(20), -- 'exact', 'probable', 'possible'
    match_reason TEXT,

    -- Discrepancies
    amount_variance DECIMAL(15,2),
    variance_explanation TEXT,

    verified_by VARCHAR(100),
    verified_at TIMESTAMP,

    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

-- ============================================================================
-- INDEXES FOR PERFORMANCE
-- ============================================================================
CREATE INDEX idx_orgs_abn ON organizations(abn);
CREATE INDEX idx_orgs_name ON organizations USING gin(name gin_trgm_ops);
CREATE INDEX idx_orgs_location ON organizations(primary_location);
CREATE INDEX idx_announcements_date ON funding_announcements(announcement_date);
CREATE INDEX idx_announcements_amount ON funding_announcements(amount_announced);
CREATE INDEX idx_payments_date ON actual_payments(payment_date);
CREATE INDEX idx_outcomes_program ON program_outcomes(program_id);
CREATE INDEX idx_outcomes_date ON program_outcomes(measurement_date);
```

### 2.2 Data Pipeline

**ETL Process**:

```
1. EXTRACT (Scrapers)
   ↓
2. TRANSFORM (Python scripts)
   - Clean data
   - Standardize formats
   - Deduplicate
   - Match entities (fuzzy matching on names)
   - Calculate confidence scores
   ↓
3. LOAD (Supabase)
   - Insert new records
   - Update existing records
   - Create cross-references
   - Log changes
   ↓
4. VALIDATE
   - Check for anomalies
   - Flag conflicts
   - Generate quality reports
```

---

## Phase 3: Visualization & User Interface (Week 5-8)

### 3.1 Dashboard Views

**1. Money Flow Sankey Diagram**
```
Government → Programs → Organizations → Outcomes

Visual:
- Width of flow = amount
- Color = sector
- Hover = details

Example:
QLD Gov ($33.88M)
  ├→ On-Country $24M → Mithangkaya Nguli → [outcomes]
  ├→ Stronger Communities $7M → Mount Isa community → [outcomes]
  └→ Co-responder $2.45M → Multi-agency → 73% reoffending reduction
```

**2. Timeline View**
```
Track funding journey:

2020 ──→ 2021 ──→ 2022 ──→ 2023 ──→ 2024 ──→ 2025
  │              │              │         │
  └ On-Country   └ Stronger     └ Media   └ Contract
    trial          Communities    statement  to Mithangkaya
    announced                     $24M      Nguli

Show:
- Announcements (above line)
- Budget allocations (middle)
- Actual payments (below line)
- Outcomes (callouts)
```

**3. Geographic Map**
```
Mount Isa (interactive map):
- Pins for service locations
- Heat map of funding concentration
- Demographics overlay
- Clickable for details

Later: Compare multiple communities
```

**4. Organization Network Graph**
```
Show relationships:
- Government depts (large nodes)
- Programs (medium nodes)
- Service providers (medium nodes)
- Outcomes (small nodes)

Connections = money flows
Click node = details
```

**5. Sector Comparison Dashboard**
```
Youth Justice | Health | Education | Infrastructure
   $33.88M    | TBD    | TBD       | TBD

For each:
- Total funding
- # programs
- # organizations
- Key outcomes
- Efficiency metrics ($ per outcome)
```

**6. Detailed Data Tables**
```
Sortable, filterable tables for deep dive:

- All announcements (10+ columns)
- All organizations (ABN, name, type, total received)
- All programs (name, amount, outcomes)
- All payments (date, amount, recipient)
- All outcomes (metric, value, date)

Export: CSV, Excel, JSON
```

### 3.2 Storytelling Views

**1. "Follow the Money" Flow**
```
User selects: $24M On-Country Program

Story unfolds:
1. Announcement (July 2024, Minister's statement)
2. Background (Why? Youth crime, community safety)
3. Budget allocation (Which department, which line item)
4. Tender process (Who bid, who won, why)
5. Contract award (Mithangkaya Nguli, contract details)
6. Payments made (Quarterly payments, total to date)
7. Services delivered (What happened on ground)
8. Outcomes achieved (Metrics, success stories)
9. Community impact (Interviews, quotes, photos)
```

**2. "Organization Profile" Story**
```
Deep dive on Mithangkaya Nguli:

- History (40 years in Mount Isa)
- Mission ("To Stand Something Up Always")
- Programs delivered
- Total funding received (all sources, all time)
- Financial health (revenue, expenses, assets)
- Track record (successes, challenges)
- Key people (board, management)
- Community reputation
- Outcomes achieved
```

**3. "What Works" Analysis**
```
Compare program effectiveness:

Co-responder Teams:
- Investment: $100M statewide
- Mount Isa share: ~$20M (estimate)
- Outcome: 73% reoffending reduction
- Cost per outcome: $X per young person diverted

On-Country Program:
- Investment: $24M
- Outcome: TBD (just launched)
- Expected: Cultural connection, reduced reoffending

Stronger Communities:
- Investment: $7M
- Outcome: TBD
```

### 3.3 Technology Stack

**Frontend**:
```
- Next.js (React framework)
- TypeScript
- Tailwind CSS
- D3.js (custom visualizations)
- Recharts (charts)
- React Flow (network graphs)
- Mapbox (maps)
```

**Backend**:
```
- Supabase (database + auth + realtime)
- Python (data processing)
- Pandas (data analysis)
- FastAPI (custom API if needed)
```

**Hosting**:
```
- Vercel (frontend)
- Supabase Cloud (database)
- GitHub (code + version control)
```

---

## Phase 4: Expand to All Sectors (Month 3-6)

### 4.1 Sector Priority Order

**Mount Isa Sectors** (in order):

1. ✅ **Youth Justice** (Started)
2. **Health** (Next)
   - Mount Isa Hospital funding
   - Royal Flying Doctor Service
   - Mental health programs
   - Indigenous health programs

3. **Education**
   - School funding
   - TAFE programs
   - University presence
   - Early childhood

4. **Infrastructure**
   - Roads, bridges
   - Water, sewer
   - Communications
   - Energy

5. **Economic Development**
   - Mining industry support
   - Small business grants
   - Tourism funding
   - Diversification programs

6. **Environment**
   - Rehabilitation programs
   - Water management
   - Land care

7. **Housing**
   - Social housing
   - Indigenous housing
   - Homelessness services

8. **Community Services**
   - Family support
   - Domestic violence
   - Aged care
   - Disability services

### 4.2 Replication Strategy

**For Each New Sector**:

```
1. Research (1 week)
   - Identify key programs
   - Find data sources
   - Map organizations

2. Scraping (1 week)
   - Build/adapt scrapers
   - Collect announcements
   - Download documents

3. Processing (1 week)
   - Extract data
   - Match entities
   - Calculate amounts

4. Validation (1 week)
   - Cross-reference sources
   - Verify payments
   - Check outcomes

5. Visualization (ongoing)
   - Add to dashboards
   - Update comparisons
   - Refresh stories
```

---

## Phase 5: Expand to Other Communities (Month 6-12)

### 5.1 Community Selection Criteria

**Priority Communities**:

1. **Similar demographics** (Indigenous population, remoteness)
   - Tennant Creek, NT
   - Kununurra, WA
   - Alice Springs, NT

2. **Same state** (easier to compare)
   - Townsville
   - Cairns
   - Rockhampton
   - Toowoomba

3. **High need** (crime, health, education gaps)
   - Based on national data

4. **Data availability** (communities with good reporting)

### 5.2 Comparative Analysis

Once multiple communities:

**Compare**:
- Funding per capita
- Program diversity
- Outcomes achieved
- Best practices
- Gaps and opportunities

**Questions to answer**:
- Which communities get more/less funding?
- Which programs work best where?
- Are outcomes consistent across communities?
- What can communities learn from each other?

---

## Phase 6: Build the Public Platform (Month 6-12)

### 6.1 User Personas

**1. Community Members**
- Want: Simple, visual understanding of where money goes
- Need: Stories, not statistics
- Access: Mobile-friendly, low bandwidth

**2. Local Government**
- Want: Track funding, identify gaps
- Need: Detailed data, comparisons
- Access: Desktop, export capabilities

**3. Service Providers**
- Want: Find funding opportunities
- Need: Program details, tender info
- Access: Searchable database

**4. Researchers/Journalists**
- Want: Deep analysis, historical data
- Need: Raw data, methodology
- Access: API, bulk downloads

**5. Policy Makers**
- Want: Evidence for decisions
- Need: Outcomes data, comparisons
- Access: Executive summaries, briefings

### 6.2 Features for Each Persona

**Community Members**:
```
- Homepage: "Where does Mount Isa's money come from?"
- Simple Sankey: Gov → Programs → Outcomes
- Stories: "Meet the people making a difference"
- News feed: Latest announcements
- Simple search: "Show me youth justice funding"
```

**Local Government**:
```
- Dashboard: All sectors, all time
- Gap analysis: "What are we missing?"
- Benchmark: Compare to similar communities
- Reports: Generate PDF summaries
- Alerts: New funding announcements
```

**Service Providers**:
```
- Opportunity finder: Open grants/tenders
- Organization profiles: Who wins what
- Success factors: What makes good proposals
- Network: Connect with others
- Resources: Templates, guides
```

**Researchers**:
```
- API access: Programmatic data retrieval
- Bulk downloads: All data as CSV/JSON
- Methodology: How we collect/verify
- Changelog: What's new
- Citation: How to reference
```

**Policy Makers**:
```
- Executive summaries: 1-page overviews
- Evidence briefs: What works
- Cost-effectiveness: $ per outcome
- Recommendations: Based on data
- Custom reports: On demand
```

---

## Success Metrics

### Short-term (3 months)
- ✅ Mount Isa youth justice complete (all sources, verified)
- ✅ 100+ organizations profiled
- ✅ 50+ programs documented
- ✅ Supabase fully operational
- ✅ Basic dashboard live
- ✅ 1,000 data points collected

### Medium-term (6 months)
- ✅ 3+ sectors complete for Mount Isa
- ✅ Comparative analysis published
- ✅ Public platform launched
- ✅ 100+ active users
- ✅ 1 media article/month

### Long-term (12 months)
- ✅ 5+ communities tracked
- ✅ All major sectors covered
- ✅ 10,000+ data points
- ✅ 1,000+ active users
- ✅ Research partnerships (universities)
- ✅ Policy impact (cited in decisions)

---

## Next Immediate Steps (This Week)

### 1. Run Firecrawl Scraper (Complete)
```bash
python scrapers/mount_isa_media_statements_firecrawl.py
```
**Result**: Full content for all 10 media statements

### 2. Build ACNC Scraper
```
Target: Download Mithangkaya Nguli financial reports
Verify: $24M revenue in 2024-25
Time: 2-3 hours
```

### 3. Build Budget Paper Parser
```
Target: Extract Mount Isa mentions from Youth Justice SDS
Find: Budget line items for On-Country, Co-responder
Time: 4-6 hours
```

### 4. Design Supabase Schema
```
Implement: Core tables (organizations, programs, funding)
Load: Initial data from media statements
Test: Queries and relationships
Time: 1 day
```

### 5. Build First Visualization
```
Create: Simple Sankey diagram
Data: $33.88M flows
Tool: D3.js or Python (plotly)
Time: 4-6 hours
```

---

## World-Class Features to Build

### 1. **Confidence Scoring System**
```
For every data point, calculate confidence:

Score 5 (Verified):
- Multiple sources confirm same amount
- Official documents (contracts, financials)
- Cross-referenced and matched

Score 4 (High Confidence):
- Official announcement
- One authoritative source
- Consistent with budget papers

Score 3 (Medium Confidence):
- Media statement only
- No budget paper confirmation
- Reasonable but unverified

Score 2 (Low Confidence):
- Secondary source
- Estimates or rounded figures
- Awaiting verification

Score 1 (Unverified):
- Single mention
- No official documentation
- Requires investigation
```

### 2. **Automated Anomaly Detection**
```
Flag for review:
- Amounts don't match across sources (>10% variance)
- Expected payments not made
- Unusual patterns (sudden spike/drop)
- Missing outcomes data
- Organizations receiving but not reporting
```

### 3. **Temporal Analysis**
```
Track changes over time:
- Funding trends (increasing/decreasing)
- Program lifecycle (start, peak, end)
- Outcome trajectories (improving/declining)
- Seasonal patterns
```

### 4. **Predictive Analytics**
```
Based on historical data:
- When will next funding round be announced?
- Which programs likely to get renewed?
- Projected outcomes based on funding levels
- Gap analysis (unmet needs)
```

### 5. **Collaborative Platform**
```
Allow community input:
- Report missing data
- Suggest corrections
- Share local knowledge
- Add context to numbers
- Rate program effectiveness (from experience)
```

---

## Technical Excellence Checklist

### Data Quality
- [ ] Every data point has source URL
- [ ] Every amount has confidence score
- [ ] Every organization has ABN/ACN
- [ ] Every program has outcomes tracking
- [ ] Cross-references validated
- [ ] Historical changes logged
- [ ] Anomalies flagged

### Performance
- [ ] Dashboard loads <2 seconds
- [ ] API responses <500ms
- [ ] Database queries optimized
- [ ] Caching implemented
- [ ] Mobile-optimized
- [ ] Works on 3G connection

### Accessibility
- [ ] WCAG 2.1 Level AA compliant
- [ ] Screen reader compatible
- [ ] Keyboard navigation
- [ ] High contrast mode
- [ ] Text resize support
- [ ] Multiple language support

### Documentation
- [ ] User guide
- [ ] API documentation
- [ ] Data dictionary
- [ ] Methodology white paper
- [ ] Video tutorials
- [ ] FAQ

### Security
- [ ] Data encrypted at rest
- [ ] HTTPS everywhere
- [ ] SQL injection protected
- [ ] XSS protected
- [ ] Regular security audits
- [ ] Privacy policy
- [ ] Terms of service

---

## Budget & Resources Needed

### Free Tier (Current)
- Firecrawl: 500 credits/month (enough for ongoing)
- Supabase: Free tier (500MB, sufficient to start)
- GitHub: Free (public repo)
- Vercel: Free (hobby tier)
- **Cost: $0/month**

### Growth Tier (Month 3-6)
- Firecrawl: Starter $25/month (50K credits)
- Supabase: Pro $25/month (8GB)
- Custom domain: $15/year
- **Cost: ~$50/month**

### Scale Tier (Month 6-12)
- Firecrawl: Growth $99/month (200K credits)
- Supabase: Pro $25/month
- CDN/hosting: $50/month
- **Cost: ~$175/month**

### Human Resources
- You: Strategy, oversight, storytelling
- Developer (you or contractor): Implementation
- Community liaison: Ground truth, validation
- Optional: Designer for polish

---

## Call to Action

**This Week**:
1. ✅ Review this strategic plan
2. Run Firecrawl scraper to completion
3. Build ACNC financial report scraper
4. Start Supabase schema design

**This Month**:
1. Complete Mount Isa youth justice data collection
2. Implement Supabase database
3. Build first visualization (Sankey diagram)
4. Publish first public report

**This Quarter**:
1. Expand to 2-3 more sectors
2. Launch public dashboard
3. Engage community for feedback
4. Start comparative analysis

---

## Why This Will Be World-Class

1. **Comprehensive**: Every dollar tracked from announcement to outcome
2. **Transparent**: All methodology public, open source
3. **Verified**: Multiple sources, confidence scoring
4. **Visual**: Complex data made simple
5. **Actionable**: Insights drive decisions
6. **Replicable**: Model works for any community
7. **Community-driven**: Local knowledge integrated
8. **Evidence-based**: Links money to outcomes
9. **Accessible**: Works for everyone
10. **Sustainable**: Built to grow over time

**Let's build this. Start with what works (youth justice), perfect it, then scale.**
