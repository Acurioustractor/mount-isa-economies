# Additional Data Loaders - Education & Community Safety

## 🎯 What These Loaders Add

You've already loaded $166.75M using `load_comprehensive_funding.py`.

These two new loaders add the remaining programs we discovered:

### 1. **load_education_infrastructure.py** - $315M+
- Logan: 7 programs, $315M (schools, special education)
- Townsville: 2 programs, $22.5M (TAFE, school expansion)
- Cairns: 2 programs, $26.5M (Marine College, school expansion)
- Gold Coast: 1 program, $12.3M (school expansion)
- Ipswich: 1 program, $15.2M (school expansion)
- Rockhampton: 1 program, $8.5M (TAFE)

**Total Education Infrastructure: $315.2M**

### 2. **load_community_safety.py** - $116M+
- Co-Responder Teams: 4 new locations, $62.5M (Toowoomba, Fraser Coast, Brisbane, Ipswich)
- PCYC Programs: 7 locations, $25.9M (Logan, Townsville, Cairns, Gold Coast, etc.)
- Community Safety: 6 programs, $22.6M (action plans, night patrols, diversion)
- Engine Immobilisers: 2 locations, $8.3M (Townsville, Cairns)

**Total Community Safety: $119.3M**

---

## 📊 Expected Totals After Loading All Scripts

| Script | Programs | Funding | Status |
|--------|----------|---------|--------|
| load_comprehensive_funding.py | 19 | $166.75M | ✅ Already loaded |
| **load_education_infrastructure.py** | 14 | $315.2M | 🆕 Run this next |
| **load_community_safety.py** | 24 | $119.3M | 🆕 Run this next |
| **GRAND TOTAL** | **57** | **$601.25M** | |

---

## 🚀 How to Run

Make sure you're in your virtual environment first:

```bash
cd ~/mount-isa-economies/mount-isa-observatory
source venv/bin/activate
```

### Step 1: Load Education Infrastructure

```bash
python scripts/load_education_infrastructure.py
```

**Expected output:**
```
💾 LOADING EDUCATION INFRASTRUCTURE TO SUPABASE

Programs to load: 14
  - Logan: 7 programs
  - Townsville: 2 programs
  - Cairns: 2 programs
  - Gold Coast: 1 programs
  - Ipswich: 1 programs
  - Rockhampton: 1 programs

✅ Connected to Supabase

📄 Yarrabilba State Secondary College - New School Construction
   Location: Logan, Yarrabilba
   Amount: $65,000,000
   Category: Education, Infrastructure, Secondary Education
   ✅ Loaded successfully

... (continues for all 14 programs)

💵 TOTAL EDUCATION INFRASTRUCTURE: $315,200,000
```

### Step 2: Load Community Safety Programs

```bash
python scripts/load_community_safety.py
```

**Expected output:**
```
🚔 LOADING COMMUNITY SAFETY PROGRAMS TO SUPABASE

Programs to load: 24
  - Co-Responder Teams: 4 programs
  - PCYC Programs: 7 programs
  - Community Safety: 6 programs
  - Engine Immobiliser: 2 programs

✅ Connected to Supabase

📄 Youth Co-Responder Team - Toowoomba
   Location: Toowoomba
   Amount: $15,620,000
   Category: Community Safety, Youth Justice, Co-Responder, Police
   ✅ Loaded successfully

... (continues for all 24 programs)

💵 TOTAL COMMUNITY SAFETY: $119,305,000
```

### Step 3: Deactivate Virtual Environment

```bash
deactivate
```

---

## 📈 Updated Community Totals

After running all three loaders, your database will show:

| Community | Previous | +Education | +Safety | NEW TOTAL |
|-----------|----------|------------|---------|-----------|
| **Logan** | $71M | +$315M | +$17M | **$403M** 🚀 |
| **Townsville** | $67M | +$23M | +$30M | **$120M** |
| **Cairns** | $73M | +$27M | +$13M | **$113M** |
| **Mount Isa** | $57M | - | - | **$57M** ✅ |
| **Gold Coast** | $51M | +$12M | +$4M | **$67M** |
| **Ipswich** | $41M | +$15M | +$17M | **$73M** |
| **Rockhampton** | $24M | +$9M | +$3M | **$36M** |
| **Toowoomba** | $16M | - | +$16M | **$32M** |
| **Fraser Coast** | $16M | - | +$16M | **$32M** |

**GRAND TOTAL: ~$933M** (up from $202M original tracking!)

---

## 🔍 What Makes Logan #1?

Logan's $403M total is driven by **massive education infrastructure investment**:

1. **New Special School: $120M** - Purpose-built special education facility
2. **Corymbia State School: $89.7M** - New primary school
3. **Yarrabilba State Secondary: $65M** - New high school
4. **FamilyLinQ Hub: $27M** - Community hub (from previous loader)
5. **Beenleigh State High: $15.8M** - School expansion
6. **PCYC Logan: $14M** - Youth precinct (from this loader)
7. **Youth Foyer: $6.2M** - Housing expansion (from previous loader)

**Education alone: $315M of Logan's $403M total (78%!)**

This reflects Logan's status as one of Queensland's fastest-growing regions, requiring substantial education infrastructure for population growth.

---

## 📊 Per Capita Rankings (UNCHANGED)

Even with Logan at #1 for total funding, **Mount Isa still dominates per capita**:

| Rank | Community | Total $ | Population | Per Capita |
|------|-----------|---------|------------|------------|
| 1 | **Mount Isa** | $57M | 18,500 | **$3,081** 👑 |
| 2 | Palm Island | $3M | 2,700 | $1,114 |
| 3 | Logan | $403M | 326,615 | $1,234 |
| 4 | Torres Strait | $4M | 4,500 | $837 |
| 5 | Townsville | $120M | 180,820 | $664 |

**Mount Isa remains exceptional on a per capita basis** - 2.5× higher than Logan, 4.6× higher than Townsville!

---

## ⚠️ Important Notes

### Co-Responder Funding Estimates

The co-responder team amounts ($15.62M per location) are **calculated estimates**, not confirmed:

- **Total program budget:** $78.1M over 4 years (confirmed)
- **Number of locations:** 5 (confirmed)
- **Per-location split:** $78.1M ÷ 5 = $15.62M (estimated - not publicly disclosed)

The scripts mark these with:
- `funding_confidence: 0.75` (lower than confirmed amounts)
- Notes field explaining the estimate

### Education Infrastructure

All education infrastructure amounts are from official Queensland Government media statements and budget papers. These are:
- **Announced funding** (high confidence)
- May include multi-year capital costs
- Opening dates vary (2023-2025)

### Already in Database

If you run these scripts and see "Already in database - skipping", that's normal! The scripts check for duplicates before inserting.

---

## 🎨 Next Steps After Loading

### 1. Check Database Stats

```bash
python scripts/database_stats.py
```

Should now show:
- Total documents: ~88 (was 79)
- Total funding: ~$601M (was $167M)
- Logan as #1 for total funding
- Mount Isa still #1 per capita

### 2. View in Supabase Dashboard

1. Go to your Supabase project
2. Click "Table Editor"
3. Select "documents" table
4. Filter by community to see new programs

### 3. Update Dashboard Visualization

The `dashboard/funding.html` file currently has hardcoded data. To update it:

**Option A: Update embedded data** (manual)
- Edit `dashboard/funding-dashboard.js`
- Update `communitiesData` array with new totals
- Refresh browser

**Option B: Dynamic data** (recommended)
- Create API endpoint or export script
- Fetch from Supabase
- Auto-update dashboard

---

## 📁 Files Created

```
scripts/
├── load_comprehensive_funding.py     # $167M - headspace, foyers, historical
├── load_education_infrastructure.py  # $315M - schools, TAFE  🆕
├── load_community_safety.py          # $119M - police, PCYC   🆕
└── README_ADDITIONAL_LOADERS.md      # This file            🆕
```

---

## ✅ Success Checklist

- [ ] Virtual environment activated
- [ ] Run `load_education_infrastructure.py`
- [ ] See 14 programs loaded successfully
- [ ] Run `load_community_safety.py`
- [ ] See 24 programs loaded successfully
- [ ] Check database stats - should show ~$601M total
- [ ] Logan now shows as #1 for total funding
- [ ] Mount Isa still #1 per capita

---

## 🔮 What's Still Missing?

We discovered $697-806M total, and these scripts load $601M.

**Still to add (~$100-200M):**
1. Remaining historical programs (Rockhampton, Ipswich 2020-2024 detailed search)
2. Smaller community programs (Cherbourg, Yarrabah, Wujal Wujal - amounts not disclosed)
3. Statewide program allocations (hard to attribute to specific communities)
4. Commonwealth contracts beyond headspace (AusTender $150-200M)

**How to add later:**
- Create additional loader scripts following the same pattern
- Use Supabase UI for one-off manual entries
- Request FOI for exact program allocations

---

**Ready to load?** Run the scripts above and watch your database grow from $167M → $601M!

**Questions?** Check the troubleshooting section in `scripts/README_LOAD_COMPREHENSIVE.md`
