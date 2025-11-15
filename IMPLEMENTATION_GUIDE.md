# Mount Isa Community Economies: Implementation Guide

This guide connects the **strategy** (vision and approach) with the **technical implementation** (data systems and tools).

## Documents Overview

### 1. Community Economies.md
**Purpose**: Strategic vision for building a self-sustaining local economy

**Key Concepts**:
- The "leaky bucket" model of local economics
- Community fabric: formal and informal caregivers
- Import replacement strategies (Jane Jacobs)
- Local multiplier effect (48% vs 14% retention)
- One-year 10% localization pilot design
- Community Economic Observatory concept

**Main Message**: Mount Isa can strengthen its economy by mapping money flows, identifying where money leaks out, and systematically developing local capacity to replace external spending.

### 2. APIs and site for data.md
**Purpose**: Technical blueprint for data infrastructure

**Key Components**:
- Data source catalog (ABS, ATO, AusTender, Queensland Gov, etc.)
- API endpoints and access methods
- ETL architecture (PostgreSQL/PostGIS, dbt, Prefect)
- Validation methodology
- 30-60-90 day implementation timeline
- Concrete code examples for each API

**Main Message**: Here's exactly how to build the data pipes to power the Economic Observatory.

### 3. mount-isa-observatory/ (This Implementation)
**Purpose**: Working codebase that implements the strategy

**What It Does**:
- Ingests data from 8+ public data sources
- Tracks economic flows in/out of Mount Isa
- Identifies leakages and service gaps
- Provides dashboards for community decision-making
- Validates data quality
- Supports the 10% localization pilot

## How They Connect

```
Community Economies.md
    ↓ (provides vision & strategy)
APIs and site for data.md
    ↓ (provides technical blueprint)
mount-isa-observatory/
    ↓ (implements the system)
Community Dashboard & Action
```

## Implementation Roadmap

### Phase 1: Foundation (Weeks 1-4) ✓
**What**: Set up core infrastructure
**Deliverables**:
- ✓ PostgreSQL database with economic flow schema
- ✓ Data ingestion scripts for major sources
- ✓ Entity resolution system (ABN Lookup)
- ✓ Basic validation tests

**Status**: COMPLETE (implemented in `mount-isa-observatory/`)

### Phase 2: Data Population (Weeks 5-8)
**What**: Fetch and load historical data
**Tasks**:
1. Run all ingestion scripts to populate database
2. Geocode entities using G-NAF
3. Classify local vs external using postcode 4825
4. Run validation suite
5. Fix any data quality issues

**Commands**:
```bash
cd mount-isa-observatory
python ingestion/run_all.py
python validation/test_data_quality.py
```

### Phase 3: Analysis & Visualization (Weeks 9-12)
**What**: Generate insights and build dashboard
**Tasks**:
1. Run leakage analysis to identify top categories
2. Calculate service gaps
3. Set up dashboard (Superset/Metabase)
4. Configure visualizations
5. Generate first community report

**Commands**:
```bash
python analysis/leakage_analyzer.py
python analysis/generate_report.py --output community_report.pdf
```

### Phase 4: Community Launch (Month 4)
**What**: Present to community and start pilot
**Tasks**:
1. Host town hall to share findings
2. Identify 2-3 priority categories for localization
3. Launch community investment fund
4. Set up quarterly review schedule
5. Begin tracking pilot metrics

**Deliverables**:
- Public dashboard accessible to community
- List of service gaps with localization plans
- Community investment fund structure
- Quarterly review schedule

### Phase 5: Pilot Execution (Months 5-16)
**What**: Run one-year 10% localization pilot
**Activities**:
- Train local workers in gap areas (e.g., electricians)
- Support new local businesses
- Redirect procurement to local suppliers
- Track metrics monthly
- Celebrate successes publicly

**Success Metrics**:
- 10% increase in local retention rate
- $X million kept circulating locally
- Y new local jobs created
- Z service gaps filled

## Key Implementation Decisions

### 1. Which Categories to Localize First?

Run this analysis:
```python
from analysis.leakage_analyzer import LeakageAnalyzer

analyzer = LeakageAnalyzer()
gaps = analyzer.identify_service_gaps()

# Filter for:
# 1. High external spending (>$500k/year)
# 2. Low local capacity (<3 providers)
# 3. Trainable/achievable (not highly specialized)

priority_gaps = gaps[
    (gaps['external_spending'] > 500000) &
    (gaps['local_provider_count'] < 3)
].head(10)
```

Common candidates:
- Electrical services
- Plumbing & gasfitting
- In-home aged care
- Diagnostic services (medical)
- Small construction trades

### 2. How to Structure Community Investment?

Options from the strategy:
1. **Community Bank Branch** (Bendigo model)
   - Local shareholders own branch
   - Profits reinvested locally
   - $366M returned to Australian communities since 1998

2. **Cooperative Investment Fund**
   - Members pool capital
   - Democratic decision-making
   - Fund local training & startups

3. **Indigenous-Controlled Trust**
   - Recognizes Kalkadoon country
   - Prioritizes Indigenous enterprise
   - Honors self-determination

**Recommendation**: Start with cooperative fund, explore Bendigo partnership for long-term sustainability.

### 3. How to Engage Youth?

From Community Economies.md:
- **Tech Teams**: Students maintain dashboard, collect data
- **Trade Pathways**: Apprenticeships in gap areas
- **Storytelling**: Youth media documenting success

**Implementation**:
```bash
# Youth can contribute to codebase
git clone mount-isa-observatory
# Add new visualizations, fix bugs, add data sources

# Youth summit to present findings
python analysis/generate_youth_report.py
```

## Technical Architecture

### Data Flow
```
External APIs
    ↓
Ingestion Scripts (Python)
    ↓
Raw Data Storage (PostgreSQL + S3)
    ↓
Staging Tables
    ↓
Transformation (dbt)
    ↓
Fact/Dimension Tables
    ↓
Analysis Tools
    ↓
Dashboard (Superset)
    ↓
Community
```

### Key Tables

**fact_economic_flows**: Every transaction/flow
- payer_entity_id, payee_entity_id
- amount, date
- is_leakage (TRUE if money left)
- flow_direction (INFLOW/OUTFLOW/INTERNAL)

**entities**: All businesses/organizations
- abn, entity_name
- is_local (TRUE if postcode 4825)
- primary_anzsic (industry)

**dim_geography**: Geographic regions
- LGA, SA2, postcode mappings
- PostGIS boundaries

### Key Queries

**Total Leakage**:
```sql
SELECT SUM(amount)
FROM fact_economic_flows
WHERE is_leakage = TRUE
  AND date >= '2024-01-01';
```

**Service Gaps**:
```sql
SELECT
    industry,
    SUM(amount) AS external_spending,
    COUNT(DISTINCT local_providers) AS local_count
FROM fact_economic_flows f
JOIN entities e ON ...
WHERE is_leakage = TRUE
GROUP BY industry
HAVING local_count < 3
ORDER BY external_spending DESC;
```

## Deployment

### Local Development
```bash
# Setup
git clone [repo]
cd mount-isa-observatory
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure
cp .env.example .env
# Edit .env with credentials

# Database
createdb mount_isa_observatory
psql mount_isa_observatory < models/schema.sql

# Run
python ingestion/run_all.py
```

### Production Deployment

**Option 1: Cloud (AWS/Azure)**
- RDS PostgreSQL with PostGIS
- EC2/App Service for ingestion jobs
- S3/Blob Storage for raw files
- Managed Superset (Preset.io)

**Option 2: On-Premises (Council Server)**
- PostgreSQL 14+ with PostGIS
- Cron jobs for ingestion
- Nginx for dashboard
- Local backup strategy

**Option 3: Hybrid**
- Data in cloud (security/backup)
- Dashboard hosted locally
- Community access via VPN/auth

### Scheduling

Use cron or Prefect for automated runs:
```bash
# Daily: AusTender, QLD procurement
0 2 * * * cd /opt/observatory && python ingestion/austender/fetch_contracts.py

# Monthly: MBS/PBS, BITRE
0 3 1 * * cd /opt/observatory && python ingestion/aihw/fetch_mbs.py

# Quarterly: DSS payments, validation
0 4 1 1,4,7,10 * cd /opt/observatory && python validation/test_data_quality.py
```

## Success Metrics

### Economic Metrics
- **Local Retention Rate**: Start ~50%, Target 60%
- **Annual Leakage**: Reduce by $10M+ in year 1
- **Local Jobs Created**: 50+ new permanent jobs
- **New Businesses**: 10+ new local enterprises

### Social Metrics
- **Youth Retention**: Reduce out-migration
- **Community Trust**: Survey-based wellbeing index
- **Service Access**: % with local access to key services
- **Participation**: Attendance at town halls, dashboard views

### Data Metrics
- **Source Coverage**: 8+ sources ingesting successfully
- **Data Quality**: >95% validation pass rate
- **Timeliness**: <30 days lag for monthly sources
- **Usage**: Dashboard views, report downloads

## Common Challenges & Solutions

### Challenge 1: API Access / Keys
**Problem**: Some APIs require registration or have rate limits
**Solution**:
- Register early (ABN Lookup GUID can take days)
- Implement polite scraping for non-API sources
- Cache aggressively to reduce API calls

### Challenge 2: Geographic Matching
**Problem**: Data comes in different geographies (LGA, SA2, postcode)
**Solution**:
- Use ABS correspondence files
- Implement fuzzy postcode matching
- Manual review edge cases

### Challenge 3: Entity Resolution
**Problem**: Same business has multiple names/ABNs
**Solution**:
- Use ABN as primary key
- Match on trading names + address
- Manual verification sample (30/quarter)

### Challenge 4: Community Engagement
**Problem**: Data is technical, community needs stories
**Solution**:
- Pair every metric with human story
- Host regular accessible town halls
- Youth media team translates data to narrative

## Next Steps

1. **Immediate** (This Week):
   - Run `mount-isa-observatory` setup
   - Test ingestion scripts
   - Generate first leakage report

2. **Short-term** (This Month):
   - Populate database with historical data
   - Set up dashboard
   - Identify pilot categories

3. **Medium-term** (Next 3 Months):
   - Launch community investment fund
   - Begin pilot interventions
   - Quarterly review #1

4. **Long-term** (Next Year):
   - Complete 10% localization pilot
   - Measure economic impact
   - Share model with other communities

## Getting Help

### Technical Support
- Issues: [GitHub Issues]
- Email: [technical contact]
- Slack: [community workspace]

### Strategy Support
- Community meetings: [schedule]
- Council liaison: [contact]
- TAFE partnership: [contact]

### Funding
- Community investment fund: [details]
- Grant opportunities: [list]
- Crowdfunding campaigns: [platform]

## Conclusion

This implementation brings together:
- **Vision** (Community Economies strategy)
- **Blueprint** (APIs and data sources)
- **Code** (mount-isa-observatory)
- **Community** (you!)

The goal: A Mount Isa where money circulates locally, jobs are plentiful, and the community controls its economic destiny.

**Let's build it together.**

---

*"Don't fly in and fly out expecting to solve our problems—the solutions are within us, waiting to be connected and unleashed."*
