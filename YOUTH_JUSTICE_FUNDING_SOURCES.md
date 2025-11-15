# Youth Justice Funding Sources - Queensland

## 🎯 Where to Find Youth Justice Funding Data

Based on recent Queensland Government announcements (2023-2025)

---

## 💰 Major Youth Justice Funding Programs

### 1. **Community Youth Response** (2023-2024)
- **Amount:** $100M over 4 years
- **Focus:** Diversion programs, community-led responses
- **Locations:** 17 communities including:
  - Palm Island ✓ (Already in your data: $735K)
  - Townsville ✓
  - Cairns ✓
  - **Mount Isa** (Need to verify allocation)
  - Torres Strait communities ✓

**Where to scrape:**
- https://www.youthjustice.qld.gov.au/community-youth-response
- Media releases tagged "Community Youth Response"
- Local council announcements of CYR funding

---

### 2. **Youth Co-Responder Teams** (2023-2024)
- **Amount:** $200M+ over 4 years
- **What:** Police + youth workers partnering
- **Locations:** Major regional centers

**Mount Isa relevance:** HIGH - regional policing hub

**Where to scrape:**
- https://www.police.qld.gov.au/youth-co-responder
- Joint QPS + Youth Justice announcements
- Search: "youth co-responder" + "Mount Isa"

---

### 3. **On Country Programs** (Indigenous Youth)
- **Amount:** $150M+ (various programs)
- **Focus:** Cultural healing, on-country programs
- **Target:** Remote Indigenous communities

**Mount Isa relevance:** VERY HIGH - NW Queensland Indigenous communities

**Programs include:**
- Doomadgee On Country program
- Mornington Island youth programs
- Torres Strait initiatives
- Gulf communities programs

**Where to scrape:**
- https://www.youthjustice.qld.gov.au/indigenous-youth
- Treaty and Truth Telling Commission announcements
- NIAA (National Indigenous Australians Agency) grants

---

### 4. **Youth Detention Center Upgrades** (Infrastructure)
- **Amount:** $500M+ (2023-2025)
- **What:** New facilities, refurbishments
- **Locations:**
  - Brisbane Youth Detention Centre upgrade
  - Regional facility proposals
  - Therapeutic facilities

**Mount Isa relevance:** MEDIUM - regional youth may be diverted to new facilities

**Where to scrape:**
- Queensland Works announcements
- DJAG (Department of Justice) capital works
- Search: "youth detention" + "infrastructure"

---

### 5. **Funding We're Missing - Quick Wins**

Based on announcements we should find but haven't yet:

#### A. **2024-25 Budget Allocation**
- **Total Youth Justice budget:** ~$800M
- **New initiatives:** $50M announced June 2024
- **Where:** Budget Paper No. 3 - Service Delivery Statements

**Action:** Download and extract:
```
https://budget.qld.gov.au/files/2024-SDS-Youth_Justice.pdf
```

Look for:
- Capital works by location
- Program funding by region
- Mount Isa specific allocations

---

#### B. **Community Safety Fund Grants**
- **Amount:** Variable (grants of $50K-$500K)
- **Focus:** Crime prevention, youth engagement
- **Eligibility:** Community organizations, councils

**Action:** Scrape awarded grants:
```
https://www.qld.gov.au/community/grants/community-safety
```

Filter for:
- Youth programs
- Regional Queensland
- Mount Isa organizations

---

#### C. **Local Thriving Communities Grants**
- **Amount:** Up to $1M per project
- **Focus:** Place-based solutions
- **Target:** Disadvantaged communities

**Mount Isa relevance:** VERY HIGH - exactly the target demographic

**Action:** Check awarded grants:
```
https://www.dlgrma.qld.gov.au/local-government/thriving-communities
```

---

## 🔍 Search Strategies

### Strategy 1: Time-Based Search
Recent major announcements (last 12 months):

```python
search_dates = [
    "June 2024",  # State Budget
    "May 2024",   # Pre-budget announcements
    "March 2024", # Quarterly updates
    "December 2023", # Mid-year review
    "October 2023",  # Budget estimates
]

for date in search_dates:
    search_query = f"youth justice funding {date}"
    # Scrape statements.qld.gov.au
```

### Strategy 2: Minister-Based Search
Key ministers who announce youth justice funding:

1. **Minister for Youth Justice**
   - Current: Hon. Di Farmer MP
   - Search: All media releases

2. **Premier**
   - Major announcements
   - Cabinet decisions on youth justice

3. **Attorney-General**
   - Justice system reforms
   - Detention center funding

4. **Minister for Indigenous Affairs**
   - On Country programs
   - Indigenous youth initiatives

### Strategy 3: Location-Based Search
For Mount Isa specifically:

```python
mount_isa_keywords = [
    "Mount Isa youth",
    "North West Queensland youth",
    "Mount Isa community safety",
    "Mount Isa crime prevention",
    "4825 youth programs",  # Postcode
]
```

---

## 📊 Expected Funding Breakdown

Based on Queensland's youth justice spend patterns:

| Category | Annual $ (Est) | Mount Isa Share (Est) |
|----------|---------------|---------------------|
| **Community Programs** | $50M | $500K-$1M (1-2%) |
| **On Country** | $40M | $2M-$3M (5-7%) |
| **Infrastructure** | $100M | $1M-$2M (1-2%) |
| **Co-Responder Teams** | $50M | $500K (1%) |
| **Youth Support Services** | $30M | $300K-$500K (1-1.5%) |
| **TOTAL** | $270M/year | **$4.3M-$7M/year** |

**Current data shows:** Only $30 for Mount Isa
**Gap:** ~$4-7M missing annually!

---

## 🎯 Action Plan for Data Collection

### Week 1: Quick Wins
- [ ] Run youth_justice_comprehensive.py scraper
- [ ] Download 2024-25 budget SDS (PDF)
- [ ] Search for "Mount Isa" in last 12 months of statements

### Week 2: Deep Dive
- [ ] FOI request: Youth Justice funding by LGA (2022-2024)
- [ ] Contact Mount Isa City Council: What youth justice grants received?
- [ ] Interview local youth service providers: What funding do they get?

### Week 3: Verification
- [ ] Cross-reference funding announcements with actual delivery
- [ ] Check: Did announced programs actually reach Mount Isa?
- [ ] Identify: Gaps between announced funding and local receipt

---

## 📞 Data Sources - Direct Links

### Government Portals
1. **Youth Justice Department**
   - News: https://www.youthjustice.qld.gov.au/news-media
   - Programs: https://www.youthjustice.qld.gov.au/about-us/programs-initiatives

2. **Ministerial Media Statements**
   - Search: https://statements.qld.gov.au/
   - Filter: Youth Justice, Community Safety
   - Date range: Last 24 months

3. **Budget Papers**
   - 2024-25: https://budget.qld.gov.au/2024-25/
   - SDS: https://budget.qld.gov.au/files/2024-SDS-Youth_Justice.pdf
   - Capital Works: https://budget.qld.gov.au/files/2024-Budget-Strategy-and-Outlook.pdf

4. **Grants Portal**
   - Active: https://www.grants.services.qld.gov.au/
   - Awarded: Often requires FOI

### Parliamentary Resources
1. **Budget Estimates Hearings**
   - Transcripts: https://www.parliament.qld.gov.au/work-of-committees/estimates
   - Youth Justice Committee: Search for Mount Isa mentions

2. **Parliamentary Questions**
   - Search Hansard for "youth justice Mount Isa"
   - MPs asking about regional funding

### Local Sources
1. **Mount Isa City Council**
   - Council grants register
   - Youth services funded
   - Partnership agreements with state

2. **Local Media**
   - North West Star
   - ABC Western Queensland
   - Announcements of local programs

---

## 🚨 Red Flags to Investigate

### Funding Announcement vs Reality Gap

**Palm Island example:**
- Announced: $5M for youth programs (2023)
- Your data shows: $735K
- **Gap: $4.27M** - Where is it?

**Possible explanations:**
1. Multi-year funding (not all spent yet)
2. Different funding streams (not all captured)
3. Infrastructure vs programs (different buckets)
4. Announced ≠ delivered (political vs actual)

**Action:** Verify each announced amount:
```
Announcement → Appropriation → Allocation → Delivery → Impact
```

Track at each stage!

---

## 💡 Tips for Scraping Youth Justice Data

### 1. **Keywords That Work**
Good keywords for finding funding:
- "youth justice funding"
- "community youth response"
- "youth co-responder"
- "on country program"
- "diversion program"
- "youth support services"
- "youth crime prevention"

Bad keywords (too broad):
- "youth" (gets education, sport, etc.)
- "justice" (gets court system, corrections)

### 2. **Date Patterns**
Queensland Government announces funding in cycles:
- **June:** State budget (big announcements)
- **December:** Mid-year review (updates)
- **Quarterly:** Regular program updates

### 3. **Location Extraction**
Youth justice funding often uses code words:
- "Remote communities" = Torres Strait, Cape York, Gulf
- "Regional centers" = Townsville, Cairns, Rockhampton
- "Growth corridors" = SE Queensland

**Mount Isa is often in "remote" or "regional" categories**

---

## 📈 Expected Results from Scraping

### Optimistic Scenario
- Find 50+ youth justice announcements
- Identify $20M+ in funding
- Verify Mount Isa receives $2-5M annually
- Build complete funding timeline

### Realistic Scenario
- Find 30+ announcements
- Identify $10-15M in funding
- Verify Mount Isa receives $1-3M annually
- Identify major gaps in data

### Pessimistic Scenario (Still Useful!)
- Find 15+ announcements
- Identify $5M in funding
- **Prove Mount Isa is underfunded** compared to peer communities
- Use gap as advocacy tool

---

## 🎯 Next Steps After Scraping

### 1. Analysis
- Compare Mount Isa to similar regional towns
- Calculate per-capita funding rates
- Identify funding gaps

### 2. Verification
- Contact Youth Justice Department
- FOI request for Mount Isa allocations
- Interview local service providers

### 3. Advocacy
- Present findings to council
- Share with local MPs
- Media release: "Data shows funding gap"

### 4. Solutions
- Identify unfunded needs
- Match to available grant programs
- Support local orgs to apply

---

## 📞 Contact Points

### Queensland Government
- **Youth Justice Dept:** youthjustice@justice.qld.gov.au
- **Budget inquiries:** budget@treasury.qld.gov.au
- **FOI requests:** rti.youthjustice@justice.qld.gov.au

### Local
- **Mount Isa City Council:** council@mountisa.qld.gov.au
- **Local MP:** (Traeger electorate)

---

*This guide is based on publicly available information as of November 2025*
*Update as new programs are announced*
