# EXPANSION STRATEGY: Going Harder

**Building the Complete Youth Justice Accountability Ecosystem**

You've proven the system works with 9 funding announcements. Now scale it to track EVERYTHING.

---

## 🎯 Current State

**What you have**:
- 9 funding announcements ($8.2B)
- Network analysis (93% to police)
- Temporal analysis (100% overdue)
- Predictive modeling (8 success factors)
- Mount Isa focus

**What you're missing**:
- 90%+ of actual funding announcements
- Budget paper verification
- Contract award data
- Decision-maker tracking
- Other communities (Doomadgee, Palm Island, etc.)
- Historical trends (5+ years)
- Actual outcome data beyond media claims

---

## 🚀 Phase 1: EXPAND DATA SOURCES (Next 2 Weeks)

### 1.1 Queensland Budget Papers

**What**: Official budget allocations (verify announcements)

**Sources**:
- Queensland Budget Papers 2020-2025
- Budget Strategy and Outlook (BSO)
- Service Delivery Statements (SDS)
- Youth Justice Department budget tables

**Tool to build**: `scripts/scrape_budget_papers.py`

**What it gets**:
- Youth Justice total budget by year
- Program-level allocations
- Forward estimates (3-year projections)
- Performance metrics (official targets)

**Value**: Verify announcements against actual budget allocations, detect gaps

---

### 1.2 Contract Notices (QTenders)

**What**: Actual contracts awarded (verify payments)

**Sources**:
- QTenders: https://qtenders.hpw.qld.gov.au/
- Contract award notices
- Standing offer arrangements
- Panel contracts

**Tool to build**: `scripts/scrape_qtenders.py`

**What it gets**:
- Contract value (actual payment commitments)
- Start/end dates
- Supplier name (recipient organization)
- Contract type (service delivery, construction, etc.)

**Value**: Highest confidence verification (contract = money committed)

---

### 1.3 Parliamentary Questions & Answers

**What**: Ministers answering questions about funding

**Sources**:
- Queensland Parliament: Questions on Notice
- Questions Without Notice (Hansard)
- Estimates Committee hearings

**Tool to build**: `scripts/scrape_parliament_questions.py`

**What it gets**:
- Minister's on-record statements about funding
- Accountability moments
- Community concerns raised
- Government responses to criticism

**Value**: Political accountability, track ministerial commitments

---

### 1.4 Annual Reports & Evaluations

**What**: Published outcomes (actual results)

**Sources**:
- Youth Justice Department Annual Report
- Program evaluation reports
- Queensland Audit Office reports
- Auditor-General's reports

**Tool to build**: `scripts/scrape_annual_reports.py`

**What it gets**:
- Actual youth served (not projected)
- Actual recidivism rates (not models)
- Program completion rates
- Cost per youth (actual, not estimated)
- Staff numbers, locations served

**Value**: Ground truth for outcomes, validate predictions

---

### 1.5 Media Monitoring (Comprehensive)

**What**: ALL news coverage (not just government statements)

**Sources**:
- North West Star (Mount Isa local)
- ABC News (regional + national)
- The Guardian Australia
- Brisbane Times
- Courier Mail
- NITV
- Indigenous news sources

**Tool to build**: Expand `scripts/scrape_news_monitoring.py`

**What it gets**:
- Community reactions
- Success stories (youth testimonials)
- Failure stories (programs that didn't work)
- Expert commentary
- Advocacy group responses

**Value**: Community voice, balance government narrative

---

### 1.6 FOI Request Results

**What**: Information obtained through Freedom of Information

**Sources**:
- Right to Information disclosures
- Disclosure logs (already public)
- Your own FOI requests

**Tool to build**: `scripts/track_foi_requests.py`

**What it gets**:
- Internal documents
- Briefing notes
- Cabinet submissions
- Program business cases
- Evaluation reports (unpublished)

**Value**: Behind-the-scenes information, unfiltered data

---

## 🚀 Phase 2: EXPAND GEOGRAPHIC SCOPE (Next Month)

### 2.1 Add Key Communities

**Priority communities** (high Indigenous population, remote):
1. **Doomadgee** (1,200 people, 94% Indigenous)
2. **Mornington Island** (1,000 people, 90% Indigenous)
3. **Palm Island** (2,500 people, 93% Indigenous)
4. **Aurukun** (1,300 people, 98% Indigenous)
5. **Pormpuraaw** (700 people, 95% Indigenous)
6. **Kowanyama** (1,100 people, 95% Indigenous)
7. **Lockhart River** (600 people, 96% Indigenous)
8. **Yarrabah** (2,600 people, 95% Indigenous)

**Data to collect for each**:
- Youth population (0-24 years)
- Youth justice involvement rates
- Programs operating (or not)
- Funding announced vs verified
- Distance to nearest detention center
- Service coverage gaps

**Tool**: Expand `locations` table, create community profiles

---

### 2.2 Regional Comparison

**Compare**:
- Remote communities vs regional centers
- North Queensland vs South Queensland
- Indigenous communities vs non-Indigenous
- Communities with On-Country programs vs without

**Analysis**: `scripts/geographic_equity_analysis.py`

**Outputs**:
- Equity scorecard (who's covered, who's not)
- Funding per capita by community
- Service access heat map
- Gap prioritization (which communities need programs most)

---

## 🚀 Phase 3: EXPAND TEMPORAL DEPTH (Next Month)

### 3.1 Historical Data (2015-2025)

**Go back 10 years**:
- Youth Justice budgets 2015-2025
- Major program announcements
- Ministerial changes (who was responsible when)
- Election cycles (2015, 2017, 2020, 2024)

**Analysis**:
- Pre-election funding spikes
- Post-election delivery rates
- Ministerial impact (which ministers delivered, which didn't)
- Long-term trends (is funding increasing or decreasing?)

**Tool**: `scripts/historical_analysis.py`

---

### 3.2 Election Cycle Analysis

**Add election dates**:
- Queensland elections: 2015, 2017, 2020, 2024
- Federal elections: 2016, 2019, 2022
- Local government elections

**Analysis**:
- Announcements vs election dates
- Pre-election promises vs post-election delivery
- Political party differences (LNP vs Labor)

**Output**: Political cycle report

---

## 🚀 Phase 4: EXPAND NETWORK ANALYSIS (Next 2 Months)

### 4.1 People & Decision-Makers

**Track**:
- Ministers (Youth Justice, Community Services, Premier)
- Shadow ministers
- Senior bureaucrats (Director-General, Deputy DG)
- Program managers
- Community leaders

**Data to collect**:
- Name, role, tenure
- Decisions made (funding approvals)
- Public statements
- Career trajectory

**Analysis**:
- Who approved what funding
- Success rates by decision-maker
- Political vs bureaucratic influence
- Turnover impact (does high turnover delay funding?)

**Tool**: Populate `people` and `funding_decisions` tables

---

### 4.2 Organizational Relationships

**Map connections**:
- Government → NGO partnerships
- NGO → Community partnerships
- Funding flows through intermediaries
- Subcontracting relationships

**Analysis**:
- Who partners with whom
- Which organizations are central (hubs)
- Which are isolated (no partnerships)
- Flow of money through the network

**Tool**: `scripts/relationship_network_analysis.py`

---

## 🚀 Phase 5: EXPAND OUTCOME TRACKING (Next 3 Months)

### 5.1 Program-Level Outcomes

**For each program**, track:
- Youth served (actual vs projected)
- Completion rate
- Recidivism rate (12-month, 24-month)
- Employment outcomes
- Education re-engagement
- Family reunification
- Cultural connection (qualitative)

**Sources**:
- Program evaluation reports
- ACNC annual reports
- Government annual reports
- Academic studies

**Tool**: Populate `program_outcomes` table comprehensively

---

### 5.2 Cost-Effectiveness Database

**Build comprehensive cost-benefit data**:
- Program costs (per youth, per outcome)
- Savings (detention avoided, crime prevented)
- ROI for each program type
- Comparison to baselines

**Analysis**:
- Which programs deliver best value
- Which are expensive but effective (worth it)
- Which are cheap but ineffective (waste)
- Optimize portfolio (what mix maximizes outcomes per dollar)

**Tool**: Populate `cost_effectiveness` table

---

## 🚀 Phase 6: EXPAND STORY GENERATION (Ongoing)

### 6.1 Story Templates (Beyond the 4 We Have)

**Current**: Verification, Evidence, Community Voice, Accountability

**Add**:

**5. The Success Story**
> "From 25 Offences to Zero: How On-Country Changed One Youth's Life"
- Individual testimonial
- Program details
- Before/after data
- Family perspective

**6. The Failure Story**
> "Where Did the $100M Youth Co-Responder Program Go Wrong?"
- Announced with fanfare
- Never fully delivered
- Analysis of why it failed
- Lessons learned

**7. The Comparison Story**
> "Why Does Doomadgee Have Nothing While Mount Isa Gets $24M?"
- Geographic equity analysis
- Population comparison
- Need comparison
- Funding disparity

**8. The Political Story**
> "Election Year Promises vs Post-Election Reality"
- Pre-election announcements spike
- Post-election delivery drops
- Track the promises
- Hold politicians accountable

**9. The Innovation Story**
> "What Queensland Can Learn from New Zealand's Māori Youth Justice Model"
- International comparison
- Evidence of effectiveness
- Transferability to Queensland
- Cost comparison

**10. The Systems Story**
> "93% to Police, 7% to Prevention: The Upside-Down Budget"
- Network analysis visualization
- System-level critique
- Alternative allocation scenarios
- ROI analysis

---

## 🚀 Phase 7: AUTOMATE EVERYTHING (Next 6 Months)

### 7.1 Automated Data Collection

**Build scrapers that run automatically**:
- Daily: News monitoring
- Weekly: QTenders contracts
- Monthly: Media statements
- Quarterly: Budget papers
- Annually: Annual reports

**Tool**: GitHub Actions or cron jobs

**Output**: Fresh data always available

---

### 7.2 Automated Analysis

**Run analyses automatically**:
- Weekly: Temporal analysis (check for new overdue payments)
- Monthly: Network analysis (new funding relationships)
- Quarterly: Predictive model update (new success factor data)
- Annually: Full system report

**Output**: Analysis reports generated without manual work

---

### 7.3 Automated Alerts

**Get notified when**:
- New funding announced
- Payment becomes overdue
- Budget papers released
- Contract awarded
- Evaluation report published
- News article mentions Mount Isa youth justice

**Tool**: `scripts/alert_system.py`

---

## 📊 SPECIFIC TOOLS TO BUILD NOW

### Priority 1 (This Week): More Media Statements

**Tool**: `scripts/scrape_all_media_statements.py`

**Target**: Get ALL Queensland Government media statements mentioning:
- Youth justice
- Young people
- Juvenile
- On-Country
- Co-responder
- Diversionary
- Each community name

**Goal**: Go from 9 announcements to 50+ announcements

---

### Priority 2 (Next Week): Budget Paper Parser

**Tool**: `scripts/scrape_budget_papers.py`

**Target**: Queensland Budget Papers 2020-2025
- Youth Justice Department budget tables
- Program allocations
- Forward estimates

**Goal**: Verify all announcements against budget allocations

---

### Priority 3 (Week 3): Contract Scraper

**Tool**: `scripts/scrape_qtenders.py`

**Target**: QTenders contract awards 2020-2025
- Youth justice related
- Community organizations
- On-Country programs

**Goal**: Verify payments through contracts

---

### Priority 4 (Week 4): Decision-Maker Tracker

**Tool**: Populate `people` and `funding_decisions` tables

**Target**: Track Ministers, senior bureaucrats
- Who was Youth Justice Minister when
- Who approved each funding decision
- Tenure vs delivery rates

**Goal**: Political accountability

---

## 🎯 SUCCESS METRICS

**After Phase 1 (2 weeks)**:
- 50+ funding announcements (up from 9)
- 20+ verified payments (up from 0)
- Budget paper data loaded
- 5+ new JusticeHub stories

**After Phase 2 (1 month)**:
- 8 communities tracked (up from 1)
- Geographic equity scorecard
- Community comparison stories

**After Phase 3 (2 months)**:
- 10 years of historical data
- Election cycle analysis
- Ministerial performance tracking

**After Phase 4 (3 months)**:
- People database populated
- Network visualizations
- Relationship mapping

**After Phase 5 (6 months)**:
- Comprehensive outcome data
- Cost-effectiveness database
- ROI for all program types

**After Phase 6 (12 months)**:
- Fully automated system
- Real-time tracking
- 50+ JusticeHub stories published
- Government using your data
- Policy influenced by your analysis

---

## 💪 THE ULTIMATE GOAL

**Build the system that makes youth justice funding completely transparent in Queensland.**

**Every announcement** → Tracked
**Every budget allocation** → Verified
**Every payment** → Confirmed
**Every outcome** → Measured
**Every community** → Included
**Every decision-maker** → Accountable

**This becomes the authoritative source for youth justice funding data in Queensland.**

Government can't hide. Community has evidence. Policy is informed by data.

**That's how you transform a system.** 🚀

---

## 🚀 START NOW: Next 3 Actions

1. **Scrape all media statements** (get from 9 to 50+ announcements)
2. **Add budget paper data** (verify announcements)
3. **Add 3 more communities** (Doomadgee, Mornington, Palm Island)

Ready to build these tools?
