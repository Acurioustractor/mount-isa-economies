# Mount Isa Community Economic Observatory

A comprehensive system for mapping economic flows, identifying leakages, and building community wealth in Mount Isa, Queensland.

## Overview

This observatory implements the strategy outlined in the Mount Isa Community Economies documentation to:

1. **Map Money Flows**: Track where dollars enter, circulate within, and leak out of the Mount Isa economy
2. **Identify Service Gaps**: Find opportunities where local businesses could replace external spending
3. **Support Local Investment**: Provide data to guide community investment in local capacity
4. **Track Progress**: Measure success of localization initiatives toward a 10% improvement goal

Based on the "leaky bucket" model of local economics, this system helps the community see, understand, and act on economic opportunities.

## Quick Start

### Prerequisites

- Python 3.9+
- PostgreSQL 14+ with PostGIS extension
- 8GB RAM minimum
- API keys (see Configuration section)

### Installation

```bash
# Clone repository
git clone https://github.com/your-org/mount-isa-observatory
cd mount-isa-observatory

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp .env.example .env
# Edit .env with your API keys and database credentials
```

### Database Setup

```bash
# Create database
createdb mount_isa_observatory

# Enable PostGIS
psql mount_isa_observatory -c "CREATE EXTENSION postgis;"

# Run schema
psql mount_isa_observatory < models/schema.sql
```

### Configuration

Create a `.env` file with required credentials:

```env
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=mount_isa_observatory
DB_USER=postgres
DB_PASSWORD=your_password

# API Keys
ABN_LOOKUP_GUID=your_abn_guid
# Register at: https://abr.business.gov.au/Tools/WebServices

ASIC_API_KEY=your_asic_key
# Optional - for enhanced entity data
```

## Architecture

```
mount-isa-observatory/
├── ingestion/          # Data collection from APIs
│   ├── abs/           # Australian Bureau of Statistics
│   ├── ato/           # Australian Taxation Office
│   ├── austender/     # Commonwealth Procurement
│   ├── qld_gov/       # Queensland Government
│   ├── aihw/          # Health data (MBS/PBS)
│   ├── dss/           # Social Services payments
│   ├── acnc/          # Charity Register
│   └── abn_lookup/    # Entity resolution
├── models/            # Database schemas
├── transforms/        # Data transformation (dbt)
├── analysis/          # Leakage analysis tools
├── validation/        # Data quality tests
├── dashboards/        # Visualization config
├── config/            # Configuration
└── docs/              # Documentation
```

## Data Sources

The observatory integrates data from:

| Source | Purpose | Update Frequency |
|--------|---------|------------------|
| **ABS CABEE** | Business counts by industry | Annual |
| **ABN Lookup** | Local business registry | Real-time |
| **AusTender** | Commonwealth procurement | Daily |
| **QLD Procurement** | State contracts | Weekly |
| **AIHW MBS/PBS** | Health spending by LGA | Monthly |
| **DSS Payments** | Social welfare transfers | Quarterly |
| **BITRE Aviation** | Airport passenger data | Monthly |
| **ACNC Register** | Charity/NFP data | Weekly |
| **ATO TaxStats** | Income by postcode | Annual |

All sources are documented with provenance tracking (URL, fetch timestamp, file hash, licence).

## Usage

### 1. Data Ingestion

Fetch data from configured sources:

```bash
# Fetch all sources
python ingestion/run_all.py

# Or fetch individually
python ingestion/abs/fetch_cabee.py
python ingestion/austender/fetch_contracts.py
python ingestion/abn_lookup/fetch_local_entities.py
python ingestion/qld_gov/fetch_procurement.py
```

### 2. Run Analysis

Generate leakage analysis:

```bash
python analysis/leakage_analyzer.py
```

Output includes:
- Total annual leakage
- Top 20 leakage categories
- Service gaps (high demand, low local supply)
- 10% localization target calculations
- Local multiplier estimates

### 3. Validation

Ensure data quality:

```bash
python validation/test_data_quality.py
```

Tests include:
- ✓ Geography integrity (100% mapped to LGA/SA2)
- ✓ Entity resolution (all ABNs classified)
- ✓ Cross-source consistency
- ✓ Outlier detection
- ✓ Time series continuity
- ✓ Provenance completeness

### 4. Dashboard

Launch the visualization dashboard:

```bash
# Using Apache Superset (recommended)
superset run -p 8088

# Or using Metabase
java -jar metabase.jar

# Dashboard configuration in dashboards/dashboard_config.py
```

## Key Concepts

### The Leaky Bucket Model

Money flows into Mount Isa through:
- Mining wages (FIFO workers)
- Government transfers (Medicare, pensions, grants)
- Tourism/visitors

Money leaks out when spent on:
- Chain stores (profits leave)
- Online shopping (0% local retention)
- External contractors
- Fly-in specialists

**Goal**: Plug leaks by developing local capacity.

### Local Multiplier Effect

Research shows:
- **Local independent business**: 48¢ of every $1 recirculates locally
- **Chain store**: Only 14¢ stays local
- **Online shopping**: ~0¢ stays local

**Impact**: Shifting 10% of spending from chains to local businesses can create significant economic gains.

### Import Replacement

Jane Jacobs' concept: systematically replace external purchases with local production. Example:

> If Mount Isa spends $2M/year on external electricians, training 5 local electricians could:
> - Keep $2M circulating locally
> - Create 5 permanent jobs
> - Generate ~$3-4M total economic impact (via multiplier)

## Dashboard Features

### 1. Key Metrics
- **Local Retention Rate**: % of spending that stays local (Target: 60%)
- **Annual Leakage**: Total $ leaving economy
- **Local Business Count**: Active local enterprises
- **Jobs Created**: From import replacement initiatives

### 2. Money Flow Visualization
- **Sankey Diagram**: Shows flows from payers → recipients
- **Geographic Flow Map**: Where money flows to/from
- **Trend Analysis**: Local vs external spending over time

### 3. Opportunities
- **Leakage Treemap**: Top categories of external spending
- **Service Gap Matrix**: High demand + low local supply = opportunity
- **Pilot Progress**: Track toward 10% localization goal

## 30-60-90 Day Implementation Plan

### Days 1-30: Standing Up the Pipes
- ✓ Set up PostgreSQL/PostGIS database
- ✓ Load ASGS correspondences & G-NAF
- ✓ Connect to 8+ data sources (ABS, ATO, AusTender, QLD, etc.)
- ✓ Build initial dashboards
- Run first validation tests

### Days 31-60: Leakage Map & Opportunity Screen
- Build entity graph (ABN/ASIC) with local/external classification
- Publish leakage treemap: top 10 categories
- Identify service gaps via capacity analysis
- Convene with Mount Isa Council & TAFE on priority trades

### Days 61-90: Pilot Implementation
- Launch community investment pool
- Target 2-3 high-impact categories for localization
- Establish quarterly refresh schedule
- Publish transparent methodology

## Validation & Quality Assurance

World-class verification includes:

### 1. Provenance Tracking
- Every data fetch recorded (URL, date, hash, licence)
- Full audit trail from raw → staged → processed

### 2. Geographic Integrity
- 100% of records mapped to valid LGA/SA2 codes
- ASGS correspondence tables applied consistently

### 3. Cross-Source Reconciliation
- MBS totals match AIHW dashboards
- AusTender counts reconcile with ABN registry
- ATO incomes align with Census medians

### 4. Statistical Tests
- Z-score outlier detection (threshold: 3.0)
- Time series continuity checks
- Quarterly variance analysis

### 5. Ground Truth Verification
- Sample 30 ABNs quarterly (phone/web check)
- Council budget reconciliation
- Community feedback loops

## Community Engagement

### Youth Involvement
- **Tech Teams**: Students build dashboard, collect data
- **Trade Pathways**: Training in identified gap areas (electricians, care workers)
- **Storytelling**: Youth media documenting local business success stories

### Town Halls & Reporting
- Quarterly community meetings to review dashboard
- Annual "State of the Local Economy" report
- Celebrate local businesses filling gaps

### Indigenous Leadership
Mount Isa sits on Kalkadoon country. The observatory should:
- Prioritize Indigenous business development
- Support Indigenous-controlled investment trusts
- Honor traditional knowledge systems alongside economic metrics

## API Reference

### Leakage Analyzer

```python
from analysis.leakage_analyzer import LeakageAnalyzer

analyzer = LeakageAnalyzer()

# Get total leakage
total = analyzer.calculate_total_leakage()

# Identify top leakages
top_leaks = analyzer.identify_top_leakages(limit=10)

# Find service gaps
gaps = analyzer.identify_service_gaps(min_spending=100000)

# Calculate localization target
target = analyzer.calculate_localization_target(target_percentage=10)

# Generate full report
report = analyzer.generate_leakage_report(output_path="report.json")
```

### Data Ingestion

```python
from ingestion.austender.fetch_contracts import AusTenderIngestion

ingestion = AusTenderIngestion()
contracts = ingestion.run(start_date="2019-01-01", end_date="2024-12-31")
```

## Contributing

This is a community-led initiative. Contributions welcome:

1. **Data Sources**: Add new ingestion scripts
2. **Analysis**: Improve leakage detection algorithms
3. **Visualizations**: Design new dashboard widgets
4. **Documentation**: Clarify usage, add examples
5. **Testing**: Expand validation coverage

See `CONTRIBUTING.md` for guidelines.

## Licenses & Attribution

### Data Licenses
- **ABS Data**: CC BY 4.0
- **AIHW Data**: Open with attribution
- **Queensland Open Data**: CC BY 4.0
- **ACNC Data**: Open datasets
- **ATO TaxStats**: CC BY 2.5 AU
- **G-NAF**: Geoscape open terms

### Code License
MIT License - see `LICENSE` file

### Attribution
Inspired by:
- New Economics Foundation's "Plugging the Leaks" methodology
- Preston Model (UK) community wealth building
- Jane Jacobs' import replacement theory
- Mount Isa Community Platform (service mapping)

## Resources

### Strategy Documents
- `../Community Economies.md` - Strategic vision and pilot design
- `../APIs and site for data.md` - Technical data source blueprint

### External Links
- [ABS Data API](https://api.data.abs.gov.au/)
- [AusTender OCDS API](https://www.tenders.gov.au/api)
- [ABN Lookup Services](https://abr.business.gov.au/Tools/WebServices)
- [Queensland Open Data](https://data.qld.gov.au/)
- [AIHW Data](https://www.aihw.gov.au/)

### Community Support
- **Mount Isa City Council**: Economic Development
- **TAFE Queensland**: Skills training partnerships
- **Local Business Groups**: Implementation partners

## Contact & Support

- **Project Lead**: [Your Name/Organization]
- **Email**: [contact email]
- **Community Forum**: [forum link]
- **Issues**: [GitHub Issues link]

## Acknowledgments

This project recognizes the Kalkadoon people as Traditional Owners of the land on which Mount Isa stands.

Built with support from the Mount Isa community, local businesses, and residents committed to building a resilient, self-sustaining local economy.

---

**Remember**: The goal isn't just better data—it's stronger community, more local jobs, and money that stays home to build the future Mount Isa deserves.
