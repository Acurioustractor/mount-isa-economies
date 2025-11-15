# Mount Isa Economic Observatory - Supabase Setup Guide

**Complete guide to setting up the database, loading data, and creating visualizations**

---

## 📋 Quick Overview

This system tracks funding flows for Mount Isa youth justice programs from announcement through to outcomes:

**Announcement → Budget → Payment → Outcome**

### What You Get

- **$8.2B** in funding announcements tracked
- **10** media statements captured
- **Complete database schema** for tracking money flows
- **Interactive visualizations** (Sankey diagrams, timelines, charts)
- **World-class data provenance** (confidence scoring, source tracking)

---

## 🚀 Setup Steps

### Step 1: Set Up Supabase Account

1. **Create free account**: https://app.supabase.com/
2. **Create new project**:
   - Name: `mount-isa-observatory`
   - Database password: Choose strong password
   - Region: Sydney (closest to Mount Isa)
3. **Get credentials**:
   - Go to Project Settings → API
   - Copy `SUPABASE_URL`
   - Copy `service_role` key (secret, full access)

### Step 2: Add Credentials to .env

```bash
# Edit .env file
nano .env

# Add these lines:
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=your-service-role-key-here
```

### Step 3: Run Database Schema

1. **Open Supabase SQL Editor**:
   - Go to your project dashboard
   - Click "SQL Editor" in left sidebar
   - Click "New query"

2. **Run schema**:
   ```bash
   # Copy contents of database/supabase_schema.sql
   cat database/supabase_schema.sql
   ```
   - Paste into SQL Editor
   - Click "Run"
   - Should see "Success. No rows returned"

3. **Verify tables created**:
   - Click "Table Editor" in left sidebar
   - Should see: locations, organizations, programs, documents, funding_announcements, etc.

### Step 4: Install Python Dependencies

```bash
# Install Supabase client
pip install supabase

# Already installed from requirements-scraping.txt:
# - pandas, requests, python-dotenv, beautifulsoup4, plotly
```

### Step 5: Load Data

```bash
# Preview what will be loaded (dry run)
python scripts/load_data_to_supabase.py --dry-run

# Load data for real
python scripts/load_data_to_supabase.py
```

**Expected output**:
```
✅ Loaded 10 statements
Total funding: $8.2B
Organizations created: ~15
Programs created: ~10
```

### Step 6: Generate Visualizations

```bash
# Generate interactive HTML visualizations
python scripts/visualize_funding_flows.py --output html

# Files created in visualizations/ folder:
# - funding_flow_sankey.html    (Government → Programs → Organizations)
# - funding_timeline.html         (Announcements over time)
# - funding_by_recipient.html     (Top recipients bar chart)
# - funding_by_program.html       (Program breakdown pie chart)
```

**Open visualizations**:
```bash
# On Mac:
open visualizations/funding_flow_sankey.html

# On Linux:
xdg-open visualizations/funding_flow_sankey.html

# Or just drag the file to your browser
```

---

## 🗄️ Database Schema Overview

### Core Tables

#### `locations`
Communities where programs operate (Mount Isa, Doomadgee, etc.)

#### `organizations`
All entities (government, NGOs, businesses)
- Queensland Government
- Mithangkaya Nguli
- Queensland Police Service
- etc.

#### `programs`
Specific initiatives
- Intensive On-Country Program
- Youth Co-Responder Teams
- Stronger Communities
- etc.

#### `documents`
Source materials (media statements, budget papers, reports)

### Funding Flow Tables

#### `funding_announcements`
**What was promised** in media statements
- Links to: program, recipient org, funding body, document source
- Includes: amount, date, confidence score, verification status

#### `budget_allocations`
**What was actually budgeted** in budget papers
- Links to: announcement (if exists), program, recipient
- Enables comparison: announced vs budgeted

#### `actual_payments`
**What was actually paid** from contracts, financial reports
- Links to: announcement, allocation, payer, payee
- Enables comparison: budgeted vs paid

#### `program_outcomes`
**What results were achieved**
- Links to: program, location, funding announcement
- Tracks metrics: offending rates, participation, completion, etc.

### Key Views

#### `v_funding_flow`
Complete funding flow for each announcement with variance analysis

#### `v_mount_isa_funding`
Mount Isa-specific funding only

#### `v_program_outcomes_summary`
Program effectiveness metrics

---

## 📊 Using the Data

### Query Examples

**Total Mount Isa funding**:
```sql
SELECT SUM(amount_announced) / 1000000 as total_millions
FROM funding_announcements
WHERE is_mount_isa_specific = true;
```

**Funding by year**:
```sql
SELECT
    EXTRACT(YEAR FROM announcement_date) as year,
    SUM(amount_announced) / 1000000 as total_millions,
    COUNT(*) as announcement_count
FROM funding_announcements
GROUP BY year
ORDER BY year DESC;
```

**Top programs**:
```sql
SELECT
    p.name as program,
    SUM(fa.amount_announced) / 1000000 as total_millions,
    COUNT(fa.id) as announcements
FROM funding_announcements fa
JOIN programs p ON fa.program_id = p.id
GROUP BY p.name
ORDER BY total_millions DESC
LIMIT 10;
```

**Funding gaps** (announced vs allocated):
```sql
SELECT * FROM v_funding_flow
WHERE announcement_vs_allocation_gap > 0
ORDER BY announcement_vs_allocation_gap DESC;
```

### Python API Examples

```python
from supabase import create_client
import os

# Initialize
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

# Get all Mount Isa funding
result = supabase.table('v_mount_isa_funding').select('*').execute()
print(f"Found {len(result.data)} Mount Isa funding announcements")

# Get specific program
result = supabase.table('programs') \
    .select('*, funding_announcements(*)') \
    .eq('name', 'Intensive On-Country Program') \
    .execute()

# Add new funding announcement
new_announcement = {
    'program_id': program_id,
    'funding_body_id': qld_gov_id,
    'amount_announced': 5000000,
    'announcement_date': '2024-11-14',
    'source_document_id': doc_id,
    'confidence_score': 4,
    'is_mount_isa_specific': True
}
result = supabase.table('funding_announcements').insert(new_announcement).execute()
```

---

## 🎨 Visualizations

### Sankey Diagram
Shows funding flow: **Government → Programs → Organizations**

**Key insights**:
- Largest flows: Police and Community Safety Budget → QPS ($4.4B)
- Direct Mount Isa allocation: On-Country Program → Mithangkaya Nguli ($24M)
- Multi-community programs split across locations

### Timeline
Shows when funding was announced over time

**Key insights**:
- Funding spike in June 2023 and 2024 (budget season)
- Major On-Country announcement July 2024 ($24M)
- Sustained investment 2020-2024

### Recipient Chart
Top organizations by total funding received

**Key insights**:
- QPS dominates ($7.6B across multiple announcements)
- Indigenous orgs: Mithangkaya Nguli ($24M)
- Community groups: Queensland Youth Services, 54 Reasons

### Program Breakdown
Pie chart of funding by program type

**Key insights**:
- Police budgets dominate (94%)
- Specific programs: On-Country, Co-responder, Stronger Communities
- Mix of capital and operating funding

---

## 🔄 Data Updates

### Adding New Media Statements

1. **Update CSV**:
   ```bash
   # Add new row to data/media_statements/mount_isa_statements_recovered.csv
   ```

2. **Reload data**:
   ```bash
   python scripts/load_data_to_supabase.py
   # Script detects duplicates and skips them
   ```

3. **Regenerate visualizations**:
   ```bash
   python scripts/visualize_funding_flows.py --output html
   ```

### Adding Budget Data

When budget papers are released:

1. **Parse PDF** (using PyPDF2 or similar)
2. **Extract line items** for Mount Isa programs
3. **Load as budget_allocations**:
   ```python
   allocation = {
       'announcement_id': announcement_id,  # Link to announcement
       'program_id': program_id,
       'amount_allocated': 24000000,
       'financial_year': '2024-25',
       'source_document_id': budget_doc_id,
       'confidence_score': 4  # Budget papers = high confidence
   }
   supabase.table('budget_allocations').insert(allocation).execute()
   ```

4. **Check for gaps**:
   ```sql
   SELECT * FROM v_funding_flow
   WHERE announcement_vs_allocation_gap > 1000000;
   ```

### Adding Payment Data

When contracts or financial reports are available:

1. **Load contract/payment data**
2. **Insert as actual_payments**:
   ```python
   payment = {
       'announcement_id': announcement_id,
       'allocation_id': allocation_id,
       'payer_org_id': dept_youth_justice_id,
       'payee_org_id': mithangkaya_nguli_id,
       'amount_paid': 8000000,  # First installment
       'payment_date': '2024-08-15',
       'financial_year': '2024-25',
       'source_document_id': contract_doc_id,
       'confidence_score': 5  # Actual contracts = highest confidence
   }
   supabase.table('actual_payments').insert(payment).execute()
   ```

3. **Track payment vs allocation**:
   ```sql
   SELECT
       allocation_vs_payment_gap,
       program_name,
       recipient_organization
   FROM v_funding_flow
   WHERE allocation_vs_payment_gap > 0;
   ```

---

## 🔍 Data Quality & Confidence Scoring

### Confidence Levels (1-5)

| Score | Meaning | Examples |
|-------|---------|----------|
| **5** | Verified payment | Bank statement, signed contract, financial report |
| **4** | Official budget | Budget papers, portfolio budget statements |
| **3** | Media announcement | Ministerial media statements, press releases |
| **2** | Estimate/projection | Internal memos, cabinet submissions |
| **1** | Unverified claim | News articles, social media |

### Verification Workflow

1. **Initial load**: confidence_score = 3, verification_status = 'unverified'
2. **Cross-reference with budget**: Update to score = 4 if budget confirms
3. **Find actual payment**: Update to score = 5, status = 'verified'
4. **Flag discrepancies**: Set status = 'disputed' if amounts don't match

### Data Provenance

Every record links to source document:
- Media statement URL
- Budget paper page number
- Contract document ID
- Financial report section

**Always ask**: "Where did this number come from?"

---

## 📈 Next Steps

### Immediate (This Week)

1. ✅ Load media statements data
2. ✅ Generate visualizations
3. ⏳ Add budget data from 2024-25 budget papers
4. ⏳ Download Mithangkaya Nguli financial reports from ACNC

### Short-term (This Month)

1. **Verify $24M On-Country payment**
   - Check if payment appears in ACNC financials
   - Look for contract on QLD Contracts Directory
   - Track installment schedule

2. **Parse budget papers**
   - 2023-24 and 2024-25 Service Delivery Statements
   - Extract Youth Justice budget line items
   - Load as budget_allocations

3. **Add outcome metrics**
   - Annual report data (offending rates, participation)
   - Evaluation reports
   - Link to program_outcomes table

### Medium-term (Next 3 Months)

1. **Expand to other sectors**
   - Education, Health, Housing, Employment
   - Same funding flow tracking approach
   - Cross-sector analysis

2. **Expand to other communities**
   - Doomadgee, Mornington Island, Townsville
   - Compare funding per capita
   - Identify inequities

3. **Build public dashboard**
   - Next.js frontend
   - Interactive visualizations
   - Search and filter by location, sector, year

### Long-term (Next 6-12 Months)

1. **Automation**
   - Auto-scrape new media statements
   - Auto-parse budget papers
   - Alert on new funding announcements

2. **AI/LLM integration**
   - Chat interface: "How much youth justice funding has Mount Isa received?"
   - Document summarization
   - Anomaly detection

3. **Impact analysis**
   - Correlate funding with outcomes
   - Cost-benefit analysis
   - Evidence-based recommendations

---

## 🔧 Troubleshooting

### "No module named 'supabase'"
```bash
pip install supabase
```

### "SUPABASE_URL not set"
Check your .env file:
```bash
cat .env | grep SUPABASE
```

### Visualizations not showing
```bash
# Check plotly installed
pip install plotly kaleido

# Run with verbose output
python scripts/visualize_funding_flows.py --output html
```

### Data not loading
```bash
# Run in dry-run mode to see what would happen
python scripts/load_data_to_supabase.py --dry-run

# Check Supabase logs in dashboard
# Project → Logs → Database
```

### Duplicate data
The loader checks for duplicates (by source_document_id). If you need to reload:
```sql
-- Delete all funding announcements
DELETE FROM funding_announcements;

-- Then re-run loader
python scripts/load_data_to_supabase.py
```

---

## 🌟 What Makes This World-Class?

1. **Complete provenance**: Every number links to source document
2. **Confidence scoring**: Know what's verified vs estimated
3. **Full funding flow**: Track announcement → budget → payment → outcome
4. **Cross-community comparable**: Same schema works for any community
5. **Multi-sector**: Youth justice today, education/health/housing tomorrow
6. **Audit trail**: timestamps, verification status, who verified when
7. **Gap analysis**: Automatically detect announcement vs payment gaps
8. **Outcome tracking**: Connect funding to results

---

## 📚 Additional Resources

- **Supabase Docs**: https://supabase.com/docs
- **SQL Tutorial**: https://www.postgresql.org/docs/current/tutorial.html
- **Plotly Visualizations**: https://plotly.com/python/
- **Firecrawl Setup** (for enhanced scraping): See `FIRECRAWL_SETUP.md`

---

## 💡 Key Insights from Current Data

### $8.2B Total Announcements (2020-2024)

**Top Programs**:
1. Police & Community Safety Budget: $4.4B (2024-25)
2. Police Operating Budget: $3.3B (2023-24)
3. Youth Justice Budget: $397M (2023-24)
4. Co-Responder Teams: $100M (statewide)
5. On-Country Program: $24M (Mount Isa specific)

**Direct Mount Isa Allocations**:
- Intensive On-Country: $24M (Mithangkaya Nguli)
- Stronger Communities: $7M (2023-2027)
- Community Connect: $2.45M (2020-2023)
- Community Grants: $430K (QYS + 54 Reasons)

**Total Direct Mount Isa**: **$33.88M** (2020-2027)

### Key Questions to Answer Next

1. **Did the money actually flow?**
   - Has Mithangkaya Nguli received the $24M?
   - Check ACNC financial reports 2024-25

2. **What were the outcomes?**
   - Co-responder teams show 73% reduction in reoffending
   - What outcomes for On-Country program?

3. **Are there gaps?**
   - Announced vs budgeted vs paid
   - Where is money stuck?

4. **Is Mount Isa getting fair share?**
   - Compare to similar remote communities
   - Per capita funding analysis

---

**You now have a world-class economic observatory! 🎉**

Next: Start answering the hard questions with data.
