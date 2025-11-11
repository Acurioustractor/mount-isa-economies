# Integration Plan: Service Map + Economic Observatory

## What You Have (Two Powerful Systems)

### 1. Mount Isa Service Map (Existing)
- **44+ services** mapped (health, disability, youth, housing, legal, Indigenous)
- **127+ community interviews** with AI analysis
- **Scrapers** for Queensland Gov, NDIS, HealthDirect
- **PostgreSQL database** with service schema
- **Community voice** and gap identification

### 2. Mount Isa Economic Observatory (New)
- **Economic flows** tracking (money in/out)
- **Procurement data** (Queensland Gov, Commonwealth)
- **Business registry** (ABN Lookup)
- **Leakage analysis** tools
- **Investment opportunity** identification

## 🔗 How They Connect (THE MAGIC!)

```
Service Map                Economic Observatory
    ↓                            ↓
Health Services    ←→    Medicare/PBS Spending
NDIS Providers     ←→    NDIS Contract Values
Local Businesses   ←→    ABN Registry + Procurement
Community Needs    ←→    Service Gap Analysis
Indigenous Corps   ←→    ORIC + ACNC Data
```

## Integration Architecture

### Unified Database Schema

```
┌─────────────────────────────────────────┐
│   MOUNT ISA COMMUNITY DATA PLATFORM     │
├─────────────────────────────────────────┤
│                                         │
│  Service Map Tables:                    │
│  ├─ services                           │
│  ├─ service_providers                  │
│  ├─ community_interviews               │
│  └─ service_gaps                       │
│                                         │
│  Economic Observatory Tables:           │
│  ├─ fact_economic_flows                │
│  ├─ entities (businesses)              │
│  ├─ dim_geography                      │
│  └─ staging_* (data sources)           │
│                                         │
│  Integration Tables (NEW):              │
│  ├─ service_provider_entities          │
│  │   (links services → ABN/entities)   │
│  ├─ service_economic_flows             │
│  │   (links services → spending)       │
│  └─ community_need_opportunities       │
│      (links gaps → investments)        │
└─────────────────────────────────────────┘
```

## Combined Insights You'll Get

### 1. Service-Economic Linkage
**Question**: "How much does Mount Isa spend on health services vs. how many local providers exist?"

**Answer**:
- Medicare spending: $X million
- PBS spending: $Y million
- Local health providers: 12 (from service map)
- **Gap**: $Z million going to external specialists
- **Opportunity**: Train 3 local nurses = $500k stays local

### 2. Community Voice + Data
**Community Interview**: "We need more mental health services for youth"

**Economic Data**:
- Youth mental health spending: $2.3M/year
- Local providers: 2
- External providers: 8
- **Action**: Community investment to support local psychologist = 50 local youth served + $280k local

### 3. Indigenous Economic Development
**Service Map**: Indigenous corporations list
**Observatory**: ORIC + ACNC financial data
**Result**: Map Indigenous business capacity + procurement opportunities

## Implementation Steps

### Phase 1: Database Setup (Today - 30 mins)
```bash
# 1. Install PostgreSQL with PostGIS
brew install postgresql postgis  # Mac
# OR
sudo apt install postgresql postgis  # Linux

# 2. Create unified database
createdb mount_isa_platform

# 3. Enable extensions
psql mount_isa_platform -c "CREATE EXTENSION postgis;"

# 4. Load both schemas
psql mount_isa_platform < mount-isa-observatory/models/schema.sql
# Then load service map schema (we'll merge them)
```

### Phase 2: Import Existing Service Data (Today - 1 hour)
```bash
# Clone your service map repo
cd /Users/benknight/Code/
git clone https://github.com/Acurioustractor/mount-isa-service-map.git

# Create integration script to import services into observatory
python import_service_map_data.py
```

### Phase 3: Link Services to Economic Data (Today - 1 hour)
- Map service categories → ANZSIC codes
- Link health services → Medicare item numbers
- Connect NDIS providers → NDIS contract data
- Match service providers → ABN registry

### Phase 4: Register for Real Data APIs (Start Today, Receive 1-2 Days)
1. **ABN Lookup GUID** (CRITICAL)
   - Go to: https://abr.business.gov.au/Tools/WebServices
   - Register now (takes 1-2 business days to receive)

2. **MyGov Developer** (for Medicare/PBS data)
   - Register at: https://developer.humanservices.gov.au/

3. **NDIS Data** (you may already have access via scrapers)
   - Check: https://data.ndis.gov.au/

### Phase 5: Enhanced Service Map Features (Next Week)
- Add "Economic Impact" to each service page
- Show "Local vs External" spending per category
- Display "Community Investment Opportunities"

## Quick Wins (What You Can Do TODAY)

### Win 1: Import Your 44 Services
```python
# Script to import service map → observatory
# Links services to industries and locations
```

### Win 2: Match Services to ABN Registry
```python
# For each service provider with an ABN:
# - Look up in ABN registry
# - Classify as local/external
# - Link to economic flows
```

### Win 3: Community Needs → Investment Opportunities
```python
# From 127 interviews:
# - Extract service gaps
# - Match to economic leakage categories
# - Generate investment priorities
```

## Example Integrated Insights

### Health Services Example
```
Service Map Data:
  - 12 local health providers
  - 8 in "General Practice"
  - 4 in "Allied Health"
  - Gap: "Need more mental health, dental"

Economic Observatory Data:
  - Medicare spending: $15.2M/year
  - PBS spending: $3.8M/year
  - 65% going to out-of-town specialists

Combined Insight:
  - $12.4M leaking for specialist care
  - Community identified mental health gap
  - Opportunity: Support 2 local psychologists
  - Impact: $800k/year stays local, 200 clients served
```

### NDIS Services Example
```
Service Map Data:
  - 6 NDIS providers in Mount Isa
  - Community feedback: "Long wait times"

Economic Observatory Data:
  - NDIS spending in 4825: $4.5M/year
  - Local providers: $1.2M (27%)
  - External providers: $3.3M (73%)

Combined Insight:
  - $3.3M going to fly-in providers
  - Could support 15 local disability workers
  - Reduce wait times + keep money local
```

## Data Sources to Add (Priority Order)

### Immediate (No API Keys Needed)
1. ✅ Your existing 44 services (service map)
2. ✅ Your 127 community interviews
3. ✅ Queensland Open Data (already working)
4. ⏳ ABS Census data (public)

### Short-term (1-2 Weeks - Need Registration)
5. ⏳ ABN Lookup (register today!)
6. ⏳ NDIS Provider data
7. ⏳ Medicare statistics by LGA

### Medium-term (1-2 Months - May Need Approval)
8. ⏳ PBS data by LGA
9. ⏳ DSS payment demographics
10. ⏳ Mount Isa City Council procurement

## Success Metrics (After Integration)

### Data Completeness
- [ ] 100% of service map providers matched to ABN
- [ ] 80%+ of services linked to economic flows
- [ ] All community-identified gaps mapped to opportunities

### Community Impact
- [ ] Dashboard shows "Local vs External" for each service type
- [ ] Investment priorities ranked by community need + economic impact
- [ ] Quarterly reports combining service gaps + spending analysis

### Economic Outcomes (12-Month Pilot)
- [ ] 10% increase in local service retention
- [ ] $X million redirected to local providers
- [ ] Y new local jobs in high-gap areas
- [ ] Z% improvement in community wellbeing scores

## Next Actions (In Order)

### RIGHT NOW (Next 30 Minutes)
1. **Register for ABN Lookup GUID**
   - Go to: https://abr.business.gov.au/Tools/WebServices
   - Fill out form
   - Use: "Community economic research and service mapping"

2. **Install PostgreSQL** (if not already installed)
   ```bash
   brew install postgresql postgis
   brew services start postgresql
   ```

3. **Clone your service map repo**
   ```bash
   cd ~/Code
   git clone https://github.com/Acurioustractor/mount-isa-service-map.git
   ```

### TODAY (Next 2 Hours)
4. Create unified database
5. Import your 44 services
6. Run integration analysis
7. Generate first combined report

### THIS WEEK
8. Wait for ABN GUID (1-2 days)
9. Match all service providers to ABN registry
10. Link community interviews to economic opportunities
11. Build integrated dashboard

Ready to start? Let me create the scripts!
