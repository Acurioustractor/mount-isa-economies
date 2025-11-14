# JusticeHub Integration Guide: Building the Complete Story

**How to combine all data sources to create powerful, evidence-based stories**

---

## 🎯 The Complete Evidence Ecosystem

You now have **4 data layers** that work together:

1. **💰 Funding Flow**: Announcements → Budget → Payment (accountability)
2. **📰 Community Voice**: News, media, real stories (human impact)
3. **📊 Outcomes Data**: What works, cost-effectiveness (evidence)
4. **❓ Gap Analysis**: What's missing, what's needed (advocacy)

**This guide shows how to combine them into JusticeHub stories that move people to action.**

---

## 📚 Story Types & Data Sources

### Story Type 1: "The Money Actually Arrived" (Verification)

**When to use**: Payment verified in ACNC or contract registry

**Data sources**:
- `v_funding_flow` (announcement → payment)
- `actual_payments` (verified payment)
- `documents` (source ACNC report)

**Example Query**:
```sql
-- Recently verified payments
SELECT
    fa.announcement_date,
    p.name as program,
    o.name as recipient,
    fa.amount_announced / 1000000 as announced_m,
    ap.amount_paid / 1000000 as paid_m,
    ap.payment_date,
    d.title as verification_source
FROM actual_payments ap
JOIN funding_announcements fa ON ap.announcement_id = fa.id
JOIN programs p ON ap.program_id = p.id
JOIN organizations o ON ap.payee_org_id = o.id
JOIN documents d ON ap.source_document_id = d.id
WHERE ap.confidence_score = 5  -- Highest confidence
AND ap.created_at > NOW() - INTERVAL '30 days'
ORDER BY ap.payment_date DESC;
```

**JusticeHub Story Template**:
```markdown
# ✅ VERIFIED: $24M On-Country Funding Reached Mount Isa

**The promise became reality.**

**Announced**: July 23, 2024 by Queensland Government
**Recipient**: Mithangkaya Nguli AIS
**Amount**: $24M
**Verified**: [Date] via ACNC Annual Information Statement

This is what accountability looks like. The money arrived.

[Link to funding flow visualization]
[Link to ACNC source document]
```

---

### Story Type 2: "This Program Works" (Evidence)

**When to use**: Productivity Commission or evaluation data shows success

**Data sources**:
- `program_outcomes` (specific program results)
- `benchmark_data` (Productivity Commission)
- `cost_effectiveness` (cost-benefit analysis)

**Example Query**:
```sql
-- Compare Mount Isa program to state/national benchmarks
SELECT
    'Mount Isa On-Country' as program,
    po.metric_name,
    po.metric_value as mount_isa_result,
    bd_qld.metric_value as qld_average,
    bd_nat.metric_value as national_average,
    CASE
        WHEN po.metric_name ILIKE '%recidivism%' THEN
            po.metric_value - bd_qld.metric_value
        ELSE
            bd_qld.metric_value - po.metric_value
    END as improvement_vs_qld
FROM program_outcomes po
LEFT JOIN benchmark_data bd_qld ON
    bd_qld.metric_name = po.metric_name
    AND bd_qld.jurisdiction = 'Queensland'
LEFT JOIN benchmark_data bd_nat ON
    bd_nat.metric_name = po.metric_name
    AND bd_nat.jurisdiction = 'National'
WHERE po.program_id = (SELECT id FROM programs WHERE name = 'Intensive On-Country Program')
ORDER BY po.metric_name;
```

**JusticeHub Story Template**:
```markdown
# 📊 PROVEN: On-Country Programs Reduce Recidivism by 73%

**The evidence is clear: It works.**

**Co-Responder Teams with On-Country components:**
- 73% reduction in serious repeat offending
- Average offences: 25 → 7 in 6 months
- Cost: $97/day vs $1,305/day detention

**Comparison to alternatives:**
- Detention recidivism: 52.3% (Queensland average)
- On-Country recidivism: **Significantly lower** (evaluation data)
- Cost savings: **$440,920 per youth per year**

**What this means:**
Every dollar invested in On-Country programs saves $13 in detention costs.

[Link to Productivity Commission data]
[Link to evaluation report]
```

---

### Story Type 3: "The Community Speaks" (Voice)

**When to use**: News articles capture community impact

**Data sources**:
- `news_articles` (media monitoring)
- `v_program_media_coverage` (sentiment analysis)
- `v_news_by_type` (success stories vs problems)

**Example Query**:
```sql
-- Recent positive news about Mount Isa programs
SELECT
    title,
    source,
    published_date,
    sentiment,
    summary,
    quotes,
    url
FROM news_articles
WHERE sentiment = 'positive'
AND article_type IN ('success_story', 'outcome_report')
AND (
    programs_mentioned @> ARRAY['On-Country']
    OR organizations_mentioned @> ARRAY['Mithangkaya Nguli']
)
ORDER BY published_date DESC
LIMIT 5;
```

**JusticeHub Story Template**:
```markdown
# 💬 VOICES: "On-Country Changed My Life"

**Real stories from Mount Isa**

[Quote from news article - direct community voice]

**What the media is saying:**
- [North West Star article]: "Youth reconnecting with culture"
- [ABC NW QLD]: "Program shows promising results"
- [Community member quote]: [Powerful personal story]

**The data backs it up:**
- [Link to outcome data]
- [Link to funding verification]

This is what success looks like on the ground.

[Link to news sources]
```

---

### Story Type 4: "Where's the Money?" (Accountability)

**When to use**: Large gap between announcement and verified payment

**Data sources**:
- `v_funding_flow` (gaps)
- `funding_announcements` (what was promised)
- `actual_payments` (what was verified)
- `benchmark_data` (what it should cost)

**Example Query**:
```sql
-- Programs with large unverified funding
SELECT
    program_name,
    recipient_organization,
    amount_announced / 1000000 as announced_m,
    total_paid / 1000000 as verified_paid_m,
    (amount_announced - total_paid) / 1000000 as gap_m,
    announcement_date,
    EXTRACT(YEAR FROM AGE(CURRENT_DATE, announcement_date::date)) as years_since_announced
FROM v_funding_flow
WHERE (amount_announced - total_paid) > 1000000  -- $1M+ gap
AND is_mount_isa_specific = true
ORDER BY gap_m DESC;
```

**JusticeHub Story Template**:
```markdown
# ❓ ACCOUNTABILITY: $7M Announced, Still Waiting for Verification

**The question Mount Isa deserves to have answered.**

**What was announced:**
- Program: Stronger Communities
- Amount: $7M (through 2026-27)
- Date: August 2023
- Purpose: Youth support and diversion

**What we've verified:**
- Budget allocation: [Checking budget papers]
- Payment received: [Not yet verified in ACNC]
- Time elapsed: [X] months

**Why this matters:**
Every month of delay costs the community. Based on Productivity Commission data, this funding could:
- Support [X] youth on community programs
- Save $440,920 per youth diverted from detention
- Reduce recidivism by [X]%

**We're tracking it. We'll verify it. Promises should become reality.**

[Link to gap analysis]
[Link to how we track funding]
```

---

## 🔄 Monthly JusticeHub Workflow

### Week 1: Data Collection (30 minutes)

**Run automated scrapers:**
```bash
# New media statements
python scrapers/mount_isa_media_statements_firecrawl.py
python scripts/load_data_to_supabase.py

# News monitoring
python scripts/scrape_news_monitoring.py --days-back 30 --add-to-database

# Check for new ACNC reports (quarterly)
python scripts/verify_acnc_payment.py
```

### Week 2: Analysis (30 minutes)

**Update visualizations:**
```bash
# Funding flows
python scripts/visualize_funding_flows.py --source supabase --output html

# Gap analysis
python scripts/build_gap_analysis.py --output html
```

**Check for stories:**
```sql
-- New verifications?
SELECT COUNT(*) FROM actual_payments WHERE created_at > NOW() - INTERVAL '30 days';

-- New gaps?
SELECT COUNT(*) FROM v_funding_flow WHERE gap_announcement_to_payment > 1000000;

-- Positive news?
SELECT COUNT(*) FROM news_articles WHERE sentiment = 'positive' AND published_date > NOW() - INTERVAL '30 days';
```

### Week 3: Story Writing (1 hour)

**Pick 2-3 stories:**
1. One verification (if available)
2. One evidence/outcome story
3. One community voice or accountability story

**Use templates above**, link to:
- Visualizations (from `/visualizations`)
- Source documents (from database)
- Comparison data (Productivity Commission)

### Week 4: Publish & Share (30 minutes)

**On JusticeHub:**
- Publish stories
- Embed visualizations
- Link to source data

**Share:**
- Social media
- Community groups
- Government stakeholders

**Total time**: 2.5 hours/month for 6-12 stories/year

---

## 📊 Power Queries for JusticeHub

### Query 1: "Mount Isa Funding Summary"
```sql
SELECT
    SUM(amount_announced) / 1000000 as total_announced_m,
    SUM(total_paid) / 1000000 as total_verified_m,
    SUM(amount_announced - total_paid) / 1000000 as total_gap_m,
    (SUM(total_paid) / NULLIF(SUM(amount_announced), 0) * 100) as verification_rate
FROM v_funding_flow
WHERE is_mount_isa_specific = true;
```

### Query 2: "Cost-Effectiveness Dashboard"
```sql
-- Show cost per outcome for different intervention types
SELECT
    intervention_type,
    AVG(cost_per_participant) as avg_cost_per_person,
    AVG(cost_benefit_ratio) as avg_benefit_per_dollar,
    COUNT(*) as program_count
FROM cost_effectiveness
GROUP BY intervention_type
ORDER BY avg_benefit_per_dollar DESC;
```

### Query 3: "Indigenous Evidence Base"
```sql
-- Strongest evidence for On-Country programs
SELECT
    title,
    organization,
    key_findings,
    evidence_strength,
    mount_isa_relevance
FROM indigenous_evidence
WHERE sector = 'youth_justice'
AND program_area @> ARRAY['rehabilitation', 'diversion']
AND evidence_strength IN ('strong', 'moderate')
ORDER BY publication_year DESC;
```

### Query 4: "Media Sentiment Tracker"
```sql
-- Track how media coverage changes over time
SELECT
    DATE_TRUNC('month', published_date) as month,
    sentiment,
    COUNT(*) as article_count,
    ARRAY_AGG(DISTINCT source) as media_outlets
FROM news_articles
WHERE published_date > NOW() - INTERVAL '12 months'
GROUP BY DATE_TRUNC('month', published_date), sentiment
ORDER BY month DESC, sentiment;
```

### Query 5: "Accountability Scorecard"
```sql
-- How are we doing on verification?
SELECT
    CASE
        WHEN total_paid >= amount_announced * 0.95 THEN 'Fully Paid'
        WHEN total_paid > 0 THEN 'Partially Paid'
        WHEN total_allocated > 0 THEN 'Budgeted Only'
        ELSE 'Announced Only'
    END as status,
    COUNT(*) as program_count,
    SUM(amount_announced) / 1000000 as total_amount_m
FROM v_funding_flow
WHERE is_mount_isa_specific = true
GROUP BY status
ORDER BY
    CASE status
        WHEN 'Fully Paid' THEN 1
        WHEN 'Partially Paid' THEN 2
        WHEN 'Budgeted Only' THEN 3
        ELSE 4
    END;
```

---

## 🎨 Visualization Strategy

### For Each Story Type:

**Verification Stories**:
- Waterfall chart (announcement → budget → payment)
- Timeline (when announced vs when paid)

**Evidence Stories**:
- Bar chart (Mount Isa vs Queensland vs National)
- Cost comparison (detention vs community)
- Outcome trends (recidivism over time)

**Community Voice**:
- Sentiment pie chart (positive/neutral/negative coverage)
- Quote highlights (pull quotes from articles)

**Accountability Stories**:
- Gap table (what's verified vs what's not)
- Time-since-announcement chart (how long we've been waiting)

---

## 💡 Advanced Integration: Embedded Dashboards

### Option 1: Static HTML Embeds

```html
<!-- In JusticeHub page -->
<h2>Mount Isa Funding Tracker</h2>
<iframe src="/static/visualizations/funding_flow_sankey.html"
        width="100%" height="600" frameborder="0"></iframe>
```

### Option 2: Live Supabase Queries

```javascript
// In JusticeHub frontend
import { createClient } from '@supabase/supabase-js'

const supabase = createClient(SUPABASE_URL, SUPABASE_ANON_KEY)

// Get latest verifications
const { data, error } = await supabase
  .from('actual_payments')
  .select('*, programs(*), organizations(*)')
  .gte('payment_date', '2024-01-01')
  .order('payment_date', { ascending: false })
  .limit(5)

// Render as cards or table
```

### Option 3: API Endpoint

```python
# Create API endpoint for JusticeHub
from fastapi import FastAPI
from supabase import create_client

app = FastAPI()

@app.get("/api/funding-summary")
async def funding_summary():
    supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

    result = supabase.table('v_funding_flow') \
        .select('*') \
        .eq('is_mount_isa_specific', True) \
        .execute()

    return {
        'total_announced': sum(r['amount_announced'] for r in result.data),
        'total_verified': sum(r['total_paid'] for r in result.data),
        'programs': len(result.data),
        'last_updated': datetime.now().isoformat()
    }
```

---

## 🚀 Launch Checklist

### Before First JusticeHub Story:

- [ ] All database schemas loaded (supabase_schema.sql, news, benchmarks)
- [ ] Initial data loaded (media statements, Productivity Commission)
- [ ] Visualizations generated and tested
- [ ] At least one payment verified (or gap identified)
- [ ] News monitoring running (30 days of data)
- [ ] Comparison report reviewed

### For Each Story:

- [ ] Data verified (check Supabase queries)
- [ ] Sources linked (documents table has URLs)
- [ ] Visualizations embedded or linked
- [ ] Story follows template (verification/evidence/voice/accountability)
- [ ] Call to action included (what reader should do)
- [ ] Shared with community for feedback

---

## 🎯 Impact Metrics for JusticeHub

Track these to show impact:

**Engagement**:
- Story views
- Time on page
- Shares (social media)
- Comments/feedback

**Accountability**:
- Gaps identified
- Gaps closed (verified payments)
- FOI requests submitted
- Government responses received

**Evidence**:
- Datasets maintained
- Reports published
- Media citations
- Policy discussions

**Community**:
- Community members reached
- Organizations engaged
- Traditional media coverage
- Government acknowledgment

---

## 💪 The Complete Story Arc

**Act 1: The Announcement**
> "Queensland Government announces $24M for Mount Isa On-Country program"
> [Media statement, funding_announcements table]

**Act 2: The Wait**
> "3 months later, we check: Has the money arrived?"
> [Gap analysis, v_funding_flow]

**Act 3: The Evidence**
> "While we wait, here's why On-Country programs work: 73% reduction in reoffending"
> [Productivity Commission, program_outcomes]

**Act 4: The Community**
> "Mount Isa families say: 'This program changed my son's life'"
> [News monitoring, community quotes]

**Act 5: The Verification**
> "✅ VERIFIED: $24M arrived. ACNC report confirms payment to Mithangkaya Nguli"
> [actual_payments, confidence_score=5]

**Act 6: The Impact**
> "What $24M buys: 50 youth on-country, $4.4M saved in detention costs, families reconnected"
> [All data sources combined]

**This is how you build trust. This is how you create change.**

---

## 📞 Support & Questions

**Data Questions**: Check QUICK_START.md for common queries

**Technical Issues**: Check SUSTAINABILITY_GUIDE.md for troubleshooting

**Story Ideas**: Review DATA_SOURCES_EXPANSION.md for more sources

**Integration Help**: This guide!

---

**You have everything you need to build Australia's most transparent youth justice accountability system.**

**Now tell the stories. The data is ready. The community is waiting.**

🚀
