# Economics Theory Testing Roadmap
## Applying World-Class Economics Research to Mount Isa

---

## 🎯 Core Question

**Can Mount Isa reduce economic leakage by 10 percentage points and prove Jane Jacobs' import replacement theory in a regional Australian context?**

---

## 📚 Theories We're Testing

### 1. **Jane Jacobs - Import Replacement Creates Growth**

**Theory:** Cities don't grow by exporting; they grow by replacing imports with local production.

**Mount Isa Test:**
```
Current State:
- Services imported: ~$150M/year (estimate)
- Local capacity: Unknown (need to measure)

10% Replacement Target:
- Replace $15M of imports with local services
- Expected outcome:
  - 50-100 new jobs (at $60K-100K wages)
  - LM3 multiplier of 2.5-3.5
  - $37M-52M total economic impact
```

**Data We Need:**
1. **Import Inventory**
   - What services are currently purchased externally?
   - From: Council procurement, hospital contracts, mining suppliers

2. **Local Capacity Map**
   - What CAN Mount Isa deliver now?
   - What COULD it deliver with training?
   - What will NEVER be local (and that's okay)?

3. **Replacement Opportunities**
   - Quick wins: Services that could localize immediately
   - Medium-term: 6-12 months of capacity building
   - Long-term: Major infrastructure/skills development

**Measurement Plan:**
```sql
-- Track over 12 months
WITH baseline AS (
  SELECT
    SUM(CASE WHEN supplier_location = 'Mount Isa' THEN amount ELSE 0 END) as local_spend,
    SUM(amount) as total_spend
  FROM procurement_data
  WHERE date BETWEEN '2025-01-01' AND '2025-12-31'
)
SELECT
  (local_spend / total_spend * 100) as local_percentage,
  (local_spend / total_spend * 100) - LAG(local_spend / total_spend * 100) OVER (ORDER BY year) as improvement
FROM baseline
GROUP BY year;
```

---

### 2. **Preston Model - Anchor Institution Procurement**

**Theory:** Large "anchor" institutions (hospitals, councils, universities) can drive local economy by committing to local procurement.

**Mount Isa Anchors:**
| Anchor | Annual Budget (Est) | Current Local % | 10% Target |
|--------|-------------------|----------------|------------|
| Mount Isa City Council | $80M | Unknown | +$8M local |
| Mount Isa Hospital | $40M | Unknown | +$4M local |
| Glencore Mount Isa Mines | $1B+ ops | <5% (est) | +$50M local |
| TAFE NW Queensland | $10M | Unknown | +$1M local |

**Preston Playbook (Adapted for Mount Isa):**

**Phase 1: Baseline (Months 1-3)**
- Map current procurement spending
- Categorize: What CAN be local vs what can't
- Survey local businesses: What can you supply?

**Phase 2: Commitment (Months 4-6)**
- Anchors sign MOU: "10% increase in local procurement"
- Change tender scoring: Add "local employment" weighting
- Remove unnecessary barriers (e.g., insurance requirements that exclude small firms)

**Phase 3: Capacity Building (Months 7-12)**
- TAFE training aligned to anchor needs
- Business consortia: Small firms collaborate to meet contracts
- Working capital support: Help firms scale up

**Phase 4: Measurement (Ongoing)**
- Quarterly reporting: $ local, jobs created
- LM3 analysis: How far does money circulate?
- Adjust and expand successful categories

---

### 3. **New Economics Foundation - LM3 Local Multiplier**

**Theory:** Money spent locally circulates 3 times before leaving the economy (vs 1 time for external spend).

**Mount Isa LM3 Study Design:**

**Sample Transactions:**
- Council contract to local builder: $500K
- Hospital supplies from local wholesaler: $200K
- Mining services from local firm: $1M

**Track 3 Rounds:**
```
Round 1: Initial Spend
- Local builder gets $500K
- Pays: $250K wages (local workers)
- Buys: $150K materials (external)
- Profit: $100K (owner, local)

Round 2: Recipients Spend Their Income
- Workers spend $200K locally (80% of wages)
  - Groceries: $100K
  - Rent: $50K
  - Services: $50K
- Owner spends $60K locally
  Total Round 2: $260K

Round 3: Next Round Recipients
- Grocery store owner spends $50K locally
- Landlord spends $20K locally
- Service providers spend $25K locally
  Total Round 3: $95K

LM3 Score = (500 + 260 + 95) / 500 = 1.71
```

**Comparison:**
- External spend LM3: ~1.0 (leaves immediately)
- Local spend LM3: 1.5-3.0 (circulates)
- **10% shift = 20-30% more economic activity**

**Data Collection Method:**
1. Survey 30 local businesses
2. Ask: "When you receive $100, how much do you spend in Mount Isa?"
3. Track 3 rounds of spending
4. Calculate LM3 score by sector

---

### 4. **Mariana Mazzucato - Mission-Oriented Innovation**

**Theory:** Government should set ambitious "moonshot" goals and coordinate investment to achieve them.

**Mount Isa Mission Candidates:**

**Option A: "Zero Youth Unemployment in 5 Years"**
- Current: ~15% youth unemployment (NW QLD average)
- Target: 0% by 2030
- Method: Guaranteed youth jobs in community wealth building

**Option B: "50% Energy Self-Sufficient by 2028"**
- Current: 100% imported energy
- Target: 50% local renewable generation
- Method: Solar + battery + hydrogen pilot

**Option C: "Localize 25% of Food Production"**
- Current: 95%+ food imported
- Target: 25% grown/processed locally
- Method: Hydroponic farms + cooperative processing

**Mission-Oriented Procurement:**
```
Instead of: "Buy X solar panels"
Mission: "Achieve 50% energy independence"
  → Opens opportunities for:
     - Local installation/maintenance
     - Community ownership models
     - Training programs
     - Innovation in desert conditions
```

---

### 5. **Kate Raworth - Doughnut Economics**

**Theory:** Economy should meet human needs (social foundation) without exceeding planetary boundaries (ecological ceiling).

**Mount Isa Doughnut:**

**Social Foundation (Inner Ring) - Are Needs Met?**
| Need | Status | Data Source |
|------|--------|-------------|
| Food | ⚠️ Limited local production | ABS food security data |
| Water | ✅ Adequate supply | Council water data |
| Health | ⚠️ Services 200km away | Hospital service maps |
| Education | ⚠️ Limited tertiary | TAFE enrollment data |
| Income | ⚠️ Unequal distribution | ATO taxation stats |
| Housing | ❌ Acute shortage | Real estate + homelessness data |
| Community | ? Unknown | Need community survey |

**Ecological Ceiling (Outer Ring) - Within Limits?**
| Boundary | Status | Data Source |
|----------|--------|-------------|
| Climate | ❌ High per-capita emissions | Scope 1+2+3 for mining |
| Water use | ⚠️ Moderate stress | Murray-Darling data |
| Land use | ❌ Mining footprint expanding | Satellite imagery |
| Biodiversity | ⚠️ Ecosystem impacts | EPBC Act assessments |

**Doughnut Sweet Spot:**
- **Currently:** Exceeding ecological ceiling while missing social foundation
- **Goal:** Move into the sweet spot (both met)

**Policy Implications:**
```
Current: Mining revenue → Government → Services (external) → Leaks out
Better: Mining revenue → Local procurement → Local jobs → Services → Stays local
Best: + Renewable energy + Food security + Housing + Within planetary boundaries
```

---

## 🧪 Experimental Design: Testing All Theories Together

### The Mount Isa Community Wealth Building Experiment

**Hypothesis:**
By applying import replacement (Jacobs) + anchor procurement (Preston) + local multipliers (NEF) + mission orientation (Mazzucato) + doughnut principles (Raworth), we can:
1. Reduce unemployment by 50%
2. Increase local procurement by 10 percentage points
3. Improve social outcomes (health, education, housing)
4. Reduce environmental impact per capita
5. Build economic resilience for post-mining transition

**Control Group:** Comparison towns in NW Queensland
**Treatment Group:** Mount Isa (implementing interventions)
**Duration:** 5 years
**Measurement Frequency:** Quarterly

---

## 📊 Data Collection Expansion Plan

### Priority 1: Procurement Data (Next 3 Months)

**Target Data:**
1. **Mount Isa City Council**
   - All contracts over $10K (last 5 years)
   - Classify: Local vs external supplier
   - Categories: Services, goods, construction

2. **AusTender (Commonwealth)**
   - All contracts to postcode 4825
   - Identify: Mount Isa firms winning federal work
   - Identify: Federal spend in region going to external firms

3. **Queensland Procurement**
   - QTenders forward pipeline
   - Historical contracts via CKAN API
   - Mount Isa relevance filter

**Scraper to Build:**
```python
# mount-isa-observatory/scrapers/procurement_comprehensive.py
class ProcurementMapper:
    def scrape_council_contracts():
        # Get council tender awards

    def scrape_austender():
        # Get federal contracts by postcode 4825

    def scrape_qld_procurement():
        # Get state contracts

    def classify_supplier_locality():
        # Use ABN Lookup to determine if supplier is local

    def calculate_leakage():
        # What % goes to external suppliers?
```

---

### Priority 2: Business Capacity Map (Months 4-6)

**What Local Businesses Can Actually Do:**

1. **ABN Lookup - All Mount Isa Businesses**
   - Postcode 4825 search
   - ANZSIC codes (industry classification)
   - Active vs inactive
   - **Estimated capacity:** 500-800 businesses

2. **Service Capabilities Survey**
   - Sample 100 businesses
   - Ask: "What can you supply? What would you need to supply more?"
   - Map to procurement categories

3. **Skills Inventory**
   - TAFE: What skills are being taught?
   - Job postings: What skills are demanded?
   - Gap: What skills are missing?

**Output:** "Mount Isa Can Supply" Database
```json
{
  "category": "Electrical services",
  "current_capacity": "$5M/year",
  "local_demand": "$15M/year",
  "gap": "$10M/year",
  "constraints": ["Limited qualified electricians", "No capacity for large projects"],
  "training_needed": "20 apprentices over 2 years",
  "import_replacement_potential": "High"
}
```

---

### Priority 3: Money Flow Tracking (Months 7-12)

**LM3 Field Study:**

1. **Select 30 Representative Businesses**
   - 10 retail
   - 10 services
   - 10 trades/construction

2. **Track Spending Rounds**
   - Round 1: Where do YOU spend your revenue?
   - Round 2: Where do THEY spend what you paid them?
   - Round 3: And where does it go next?

3. **Calculate LM3 by Sector**
   - Which sectors keep money local?
   - Which sectors leak most?
   - Where are intervention opportunities?

**Tools:**
- Qualtrics survey
- Bank statement analysis (anonymized)
- Receipt tracking pilot

---

### Priority 4: Social Outcomes (Ongoing)

**Beyond GDP - What Actually Matters:**

1. **Employment & Income**
   - SALM data (monthly unemployment by LGA)
   - ATO taxation statistics (postcode income distribution)
   - Census journey-to-work data

2. **Health & Wellbeing**
   - AIHW health indicators
   - Medicare claims data (aggregate)
   - Hospital utilization rates

3. **Education & Skills**
   - TAFE enrollment and completion
   - School NAPLAN results
   - University pathways (how many leave vs return?)

4. **Housing & Amenity**
   - Rental vacancy rates
   - Homelessness counts
   - Public space quality (need to develop metric)

5. **Community Connection**
   - Volunteering rates (ABS General Social Survey)
   - Community group participation
   - Subjective wellbeing survey

---

## 🎯 Immediate Action Plan (This Month)

### Week 1: Community Engagement
- [ ] Present COMMUNITY_SHOWCASE.md to council
- [ ] Workshop: "Does this data match your experience?"
- [ ] Recruit community advisory group

### Week 2: Data Sprint
- [ ] Scrape AusTender for Mount Isa contracts
- [ ] Request council procurement data (FOI if needed)
- [ ] Map Mount Isa businesses (ABN Lookup postcode 4825)

### Week 3: Analysis
- [ ] Calculate current local procurement %
- [ ] Identify top 10 import replacement opportunities
- [ ] Draft 10% local procurement pilot proposal

### Week 4: Proposal
- [ ] Present to council: "Partner with us on 10% pilot"
- [ ] Propose LM3 study
- [ ] Secure commitment from one anchor institution

---

## 📈 Success Criteria (How We'll Know It's Working)

### Year 1 Targets
- [ ] 500+ Mount Isa businesses mapped
- [ ] Baseline local procurement % established
- [ ] One anchor institution committed to 10% increase
- [ ] LM3 study completed (20+ businesses)
- [ ] 5 import replacement opportunities identified

### Year 3 Targets
- [ ] 10% increase in local procurement ($10M+)
- [ ] 50 new jobs created
- [ ] LM3 score improved from 1.5 to 2.0
- [ ] 3+ anchor institutions participating
- [ ] Doughnut analysis shows progress on social foundation

### Year 5 Targets
- [ ] 25% increase in local procurement ($25M+)
- [ ] 150 new jobs created
- [ ] Youth unemployment halved
- [ ] Model replicated in 3+ other regional towns
- [ ] Academic papers published validating approach

---

## 🌍 Comparison: How Mount Isa Compares to World Leaders

| Initiative | Location | Scale | Mount Isa Equivalent |
|-----------|----------|-------|---------------------|
| **Preston Model** | Preston, UK (pop 140K) | £200M redirected locally | $25M target |
| **Evergreen Cooperatives** | Cleveland, OH (pop 372K) | $50M worker-owned economy | $5M pilot |
| **Mondragon** | Euskadi, Spain (pop 80K region) | €12B cooperative economy | Long-term aspiration |
| **Transition Towns** | Totnes, UK (pop 8K) | £2M local currency | $200K local scrip pilot? |

**Mount Isa Advantage:**
- Smaller = more agile
- Mining wealth = leverage for investment
- Strong community identity
- Already has anchor institutions

**Mount Isa Challenge:**
- Remote = higher import costs
- Small population = limited local market
- Mining-dependent = boom/bust cycles
- Brain drain = youth leave for opportunities

---

## 🤝 Partnerships to Build

### Academic Partnerships
- **University of Queensland:** Economics department validation
- **Griffith University:** Regional development expertise
- **CSIRO:** Data science and mapping support

### Government Partnerships
- **Queensland Treasury:** Data sharing agreements
- **DLGRMA:** Regional development grants
- **ABS:** Custom data runs for Mount Isa

### International Learning
- **Preston City Council:** Study tour, methodology transfer
- **NEF (UK):** LM3 training and certification
- **Mondragon University:** Cooperative economy models

---

## 📚 Reading List (For Going Deeper)

1. **Jane Jacobs** - "The Economy of Cities" (1969)
2. **Matthew Brown & Rhian E. Jones** - "Paint Your Town Red: How Preston Took Back Control" (2021)
3. **Mariana Mazzucato** - "Mission Economy" (2021)
4. **Kate Raworth** - "Doughnut Economics" (2017)
5. **NEF** - "The Money Trail" (LM3 handbook)
6. **Tim Jackson** - "Prosperity Without Growth" (2009)
7. **Elinor Ostrom** - "Governing the Commons" (Nobel Prize work)

---

*This roadmap is a living document - update as we learn more!*
