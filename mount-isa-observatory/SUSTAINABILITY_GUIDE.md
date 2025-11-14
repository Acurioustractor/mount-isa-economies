# Sustainability Guide: Building a Self-Sustaining Economic Observatory

**How to maintain and expand this system to feed your JusticeHub platform**

---

## 🎯 The Goal

Build a **self-sustaining system** that:
1. Automatically collects new funding data
2. Verifies payments as they happen
3. Tracks outcomes over time
4. Feeds stories to JusticeHub
5. Expands to other communities and sectors

---

## 📅 Monthly Maintenance (2 hours/month)

### Week 1: New Announcements

**Task**: Scrape new media statements

```bash
# Run monthly
python scrapers/mount_isa_media_statements_firecrawl.py

# Load new data
python scripts/load_data_to_supabase.py

# Regenerate visualizations
python scripts/visualize_funding_flows.py --source supabase --output html
```

**What to look for**:
- New youth justice announcements
- Mount Isa mentions
- Funding amounts
- Program names

**Time**: 30 minutes

### Week 2: Verification

**Task**: Check for new payments

```bash
# Check ACNC for new annual reports
python scripts/verify_acnc_payment.py

# If found, add to database
python scripts/verify_acnc_payment.py --add-to-database
```

**What to check**:
- Mithangkaya Nguli AIS (published Oct-Dec annually)
- Other Mount Isa organizations
- Contract directory updates

**Time**: 30 minutes

### Week 3: Gap Analysis

**Task**: Update gap analysis

```bash
# Regenerate with latest data
python scripts/build_gap_analysis.py --output html
```

**What to review**:
- New gaps (announcements without payments)
- Closed gaps (verified payments)
- Trends over time

**Time**: 15 minutes

### Week 4: JusticeHub Update

**Task**: Extract stories for platform

**What to share**:
- New verified payments ("$24M reached Mithangkaya Nguli ✓")
- Success stories (outcomes data)
- Accountability stories (large gaps)
- Community impact

**Time**: 45 minutes

---

## 🤖 Automation Opportunities

### Level 1: Semi-Automated (Now)

**What you do manually**:
- Run scripts monthly
- Review new data
- Add verified payments
- Update JusticeHub

**Effort**: 2 hours/month

### Level 2: Scheduled Automation (3 months)

**Set up cron jobs / GitHub Actions**:

```yaml
# .github/workflows/monthly-scrape.yml
name: Monthly Data Collection
on:
  schedule:
    - cron: '0 0 1 * *'  # 1st of every month

jobs:
  scrape:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Scrape media statements
        run: python scrapers/mount_isa_media_statements_firecrawl.py
      - name: Load to Supabase
        run: python scripts/load_data_to_supabase.py
      - name: Generate visualizations
        run: python scripts/visualize_funding_flows.py --source supabase --output html
      - name: Commit results
        run: |
          git add visualizations/
          git commit -m "Auto-update: $(date)"
          git push
```

**Effort**: 1 hour/month (just review)

### Level 3: Fully Automated (6-12 months)

**Advanced automation**:
- AI scraper monitors all QLD Gov websites
- Auto-extracts funding announcements
- Cross-references with ACNC automatically
- Sends alerts when gaps found
- Auto-generates JusticeHub posts

**Effort**: 15 minutes/month (just review alerts)

---

## 🔗 JusticeHub Integration

### Story Types to Extract

#### 1. **Verification Stories**

**When**: Payment verified in ACNC

**Template**:
> ✅ **VERIFIED**: $24M On-Country Funding Reached Mithangkaya Nguli
>
> Government announced: July 2024
> Payment verified: [Date from ACNC]
> Source: [ACNC AIS 2024-25]
>
> This means: Promises became reality. The money arrived.

**Impact**: Builds trust, shows accountability works

#### 2. **Outcome Stories**

**When**: New results data available

**Template**:
> 📊 **RESULTS**: Co-Responder Teams Reduce Youth Offending by 73%
>
> Investment: $100M statewide
> Result: 73% reduction in repeat offending
> Cohort: Serious repeat offenders in Mount Isa
>
> This means: The program works. Funding creates impact.

**Impact**: Shows what works, evidence for more funding

#### 3. **Gap Stories**

**When**: Large announced-payment gap found

**Template**:
> ❓ **ACCOUNTABILITY**: $7M Stronger Communities - Where Is It?
>
> Announced: Aug 2023 ($7M through 2026-27)
> Budgeted: [Checking budget papers]
> Paid: [Not yet verified]
>
> Question: Has this funding reached Mount Isa yet?

**Impact**: Holds government accountable

#### 4. **Community Impact Stories**

**When**: Linking funding to real stories

**Template**:
> 💡 **IMPACT**: How $430K Transformed Youth Support
>
> Recipients:
> - Queensland Youth Services: $130K (Proud Warrior project)
> - 54 Reasons: $300K (Back to Community program)
>
> [Link to community member story]
>
> This is what funding looks like on the ground.

**Impact**: Humanizes the data

### Integration Methods

#### Option 1: Manual (Now)

1. Monthly: Review new data
2. Select 2-3 stories
3. Write posts for JusticeHub
4. Link to visualizations

**Effort**: 45 min/month

#### Option 2: API (6 months)

```python
# JusticeHub API integration
import requests

# Get latest verified payments
response = supabase.table('actual_payments') \
    .select('*, organizations(*), programs(*)') \
    .gte('created_at', last_month) \
    .execute()

# Auto-post to JusticeHub
for payment in response.data:
    justicehub_api.create_story({
        'type': 'verification',
        'title': f"✅ VERIFIED: ${payment['amount_paid']/1_000_000}M to {payment['organization']['name']}",
        'data': payment,
        'visualization_url': f"https://observatory.justicehub.com/flow/{payment['id']}"
    })
```

#### Option 3: Embedded Dashboards (12 months)

**Embed interactive visualizations directly in JusticeHub**:

```html
<!-- JusticeHub page -->
<h2>Mount Isa Funding Tracker</h2>
<iframe src="https://observatory.justicehub.com/embed/sankey" width="100%" height="600"></iframe>

<h3>Latest Verifications</h3>
<div id="latest-payments"></div>

<script>
  // Load from Supabase
  fetch('https://[your-supabase-url]/rest/v1/actual_payments?limit=5')
    .then(r => r.json())
    .then(payments => {
      // Render latest payments
    });
</script>
```

---

## 🌍 Expansion Strategy

### Phase 1: Complete Mount Isa Youth Justice (Done)

✅ Media statements
✅ Database schema
✅ Visualizations
✅ Verification tools

**Next**: Complete verification (ACNC, budget papers)

### Phase 2: Expand Sectors (3 months)

**Add**:
- Education funding (schools, scholarships)
- Health funding (hospital, clinics, services)
- Housing funding (social housing, repairs)
- Employment funding (job programs, training)

**Method**: Same schema, different scrapers

**Effort**: 1-2 days per sector

### Phase 3: Expand Communities (6 months)

**Add**:
- Doomadgee
- Mornington Island
- Burketown
- Other Northwest Queensland communities

**Method**: Same system, different location filters

**Comparison**:
```sql
-- Per capita funding comparison
SELECT
    l.name as community,
    SUM(fa.amount_announced) / l.population as per_capita_funding
FROM funding_announcements fa
JOIN locations l ON fa.target_locations @> ARRAY[l.id]
GROUP BY l.name, l.population
ORDER BY per_capita_funding DESC;
```

### Phase 4: Statewide (12 months)

**Track all Queensland remote community funding**

**Become**: The authoritative source for remote funding data

---

## 📊 Success Metrics

### Month 1
- ✅ System running
- ✅ Monthly data updates
- ✅ First JusticeHub story

### Month 3
- ✅ First payment verified
- ✅ Gap analysis published
- ✅ 3-5 JusticeHub stories

### Month 6
- ✅ 2-3 sectors added
- ✅ Automated data collection
- ✅ Regular JusticeHub features

### Month 12
- ✅ 3-5 communities tracked
- ✅ Public dashboard launched
- ✅ Recognized data source

---

## 💰 Sustainability Model

### Free Tier (Individual)

**What you get**:
- All tools and scripts
- Monthly data updates
- Basic visualizations
- JusticeHub integration

**Cost**: Your time (2 hours/month)

### Grants/Funding (Organization)

**Potential funders**:
- Philanthropy (Paul Ramsay Foundation, etc.)
- Government (transparency initiatives)
- Research grants (universities)

**Budget for**:
- Developer time (automation)
- Data collection (FOI requests)
- Server costs (Supabase, hosting)
- Expansion (other communities)

**Ask**: $50K-$100K/year for full-time development

### Partnership Model (Government)

**Pitch to Queensland Government**:

> "We've built a transparency system that tracks your funding from announcement to outcome. Partner with us to make it official."

**What they get**:
- Transparency & accountability
- Evidence base for policy
- Community trust

**What you get**:
- Official data access
- Funding for development
- Platform legitimacy

---

## 🎓 Knowledge Transfer

### Documentation

✅ Complete code documentation
✅ Setup guides (Supabase, visualization)
✅ Data collection workflows
✅ Verification processes

### Training Materials

**Create**:
- Video tutorials (how to run scripts)
- Written guides (how to verify payments)
- FAQ (common questions)
- Troubleshooting guide

### Community Building

**Build around it**:
- GitHub community
- Monthly community calls
- Slack/Discord channel
- Contributors guide

---

## 🚀 Next Actions (This Week)

### Day 1: Verify Payment
```bash
git pull
python scripts/verify_acnc_payment.py
# Follow guide, check ACNC
```

### Day 2: Run Gap Analysis
```bash
python scripts/build_gap_analysis.py --output html
# Review gaps, identify priorities
```

### Day 3: Customize One-Pager
```bash
# Edit ONE_PAGER_TEMPLATE.md
# Add your JusticeHub branding
# Customize for your audience
```

### Day 4: First JusticeHub Story
- Pick one verification or outcome
- Write 300-word story
- Link to visualization
- Publish on JusticeHub

### Day 5-7: Plan Automation
- Set up GitHub Actions (or cron)
- Schedule monthly scraper
- Set reminders for verification checks

---

## 💡 Key Principle

**"Build once, use everywhere"**

Everything you build for Mount Isa youth justice can be reused for:
- Other sectors
- Other communities
- Other states/countries

**This is how you scale impact.**

---

## ✅ Summary

**You've built**:
1. Data collection system
2. Verification system
3. Visualization system
4. Story generation system

**Now maintain it**:
- 2 hours/month
- Monthly data updates
- Regular JusticeHub stories

**Then expand it**:
- More sectors
- More communities
- Full automation

**The goal**: Every Australian can track every dollar from announcement to outcome.

**You're building that. One community, one sector at a time.**

---

*Need help? Questions? Want to contribute?*

[Your contact for JusticeHub / Observatory]
