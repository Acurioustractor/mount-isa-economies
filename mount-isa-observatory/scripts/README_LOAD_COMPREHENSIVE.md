# Loading Comprehensive Funding Data to Supabase

## 🎯 What This Does

This script loads **$90M+ in newly discovered funding** into your Supabase database so you can visualize and analyze it.

**What gets loaded:**
- ✅ 9 headspace centers ($27M/year)
- ✅ 3 Youth Foyers ($36.25M)
- ✅ Townsville historical programs ($21.45M)
- ✅ Cairns historical programs ($41.6M)
- ✅ Logan historical programs ($41M)

**Total:** ~30 programs, $90M+ in funding

---

## 📋 Prerequisites

### 1. Supabase Credentials

You need a `.env` file with your Supabase credentials:

```bash
cd /home/user/mount-isa-economies/mount-isa-observatory
```

Check if you have a `.env` file:
```bash
ls -la .env
```

If not, copy from example:
```bash
cp .env.example .env
nano .env
```

Add these lines:
```
SUPABASE_URL=your_supabase_project_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

**Where to find these:**
1. Go to your Supabase project
2. Click "Settings" (gear icon)
3. Click "API"
4. Copy "Project URL" → `SUPABASE_URL`
5. Copy "service_role" key (secret!) → `SUPABASE_SERVICE_ROLE_KEY`

### 2. Python Dependencies

Install required packages:
```bash
pip3 install python-dotenv supabase
```

Or if you have issues:
```bash
pip3 install --upgrade cffi cryptography python-dotenv supabase
```

---

## 🚀 How to Run

### Simple Method:

```bash
cd /home/user/mount-isa-economies/mount-isa-observatory
python3 scripts/load_comprehensive_funding.py
```

### What You'll See:

```
================================================================================
💾 LOADING COMPREHENSIVE FUNDING DISCOVERIES TO SUPABASE
================================================================================

Programs to load: 30
  - headspace centers: 9
  - Youth Foyers: 3
  - Townsville historical: 3
  - Cairns historical: 2
  - Logan historical: 2

✅ Connected to Supabase

📄 headspace Mount Isa
   Location: Mount Isa
   Amount: $3,500,000
   Category: Mental Health
   ✅ Loaded successfully

📄 headspace Southport
   Location: Gold Coast
   Amount: $3,000,000
   Category: Mental Health
   ✅ Loaded successfully

... (continues for all 30 programs)

================================================================================
📊 LOADING SUMMARY
================================================================================

Total programs: 30
Loaded: 25
Skipped (already in DB): 5
Errors: 0

💰 FUNDING BY CATEGORY:
================================================================================

Mental Health:
  Programs: 9
  Total: $27,200,000

Youth Housing:
  Programs: 3
  Total: $36,250,000

... (etc)

================================================================================
💵 TOTAL NEW FUNDING LOADED: $90,450,000
================================================================================
```

---

## 📊 After Loading - View Your Data

### Check Database Stats:

```bash
python3 scripts/database_stats.py
```

Should now show:
- Total documents: ~91 (was 61)
- Total funding: ~$143M (was $53M)
- Mount Isa now includes headspace: $55-58M total

### Open Dashboard:

```bash
cd dashboard
open funding.html
# OR
firefox funding.html
```

The dashboard will now show comprehensive data!

---

## 🔍 What Gets Added to Each Community

### Mount Isa
**BEFORE:** $53.38M (7 programs)
**AFTER:** $56.88M (8 programs)
**NEW:** +$3.5M headspace Mount Isa

### Gold Coast
**BEFORE:** $30.8M (3 programs)
**AFTER:** $50.75M (6 programs)
**NEW:**
- +$14.95M Gold Coast Youth Foyer
- +$3M headspace Southport
- +$2.7M headspace Upper Coomera

### Townsville
**BEFORE:** $28M (3 programs)
**AFTER:** $67.45M (10 programs)
**NEW:**
- +$19.2M Working Together, Changing the Story
- +$15.1M Townsville Youth Foyer
- +$1.5M On Country Program
- +$750K The Lighthouse (boost)
- +$3M headspace Townsville

### Cairns
**BEFORE:** $28M (3 programs)
**AFTER:** $72.6M (7 programs)
**NEW:**
- +$24M Youth Mental Health Unit
- +$17.6M Marine College Expansion
- +$3M headspace Cairns

### Logan
**BEFORE:** $20.9M (2 programs)
**AFTER:** $71.1M (7 programs)
**NEW:**
- +$27M FamilyLinQ Hub
- +$14M PCYC Logan Precinct
- +$6.2M Youth Foyer expansion
- +$3M headspace Meadowbrook

### Ipswich, Rockhampton, Toowoomba
Each gets +$3M for headspace center

---

## ⚠️ Troubleshooting

### Error: "Missing Supabase credentials"
- Check your `.env` file exists
- Verify `SUPABASE_URL` and `SUPABASE_SERVICE_ROLE_KEY` are set
- Make sure there are no spaces around the `=` sign

### Error: "ModuleNotFoundError: No module named 'supabase'"
```bash
pip3 install supabase python-dotenv
```

### Error: "ModuleNotFoundError: No module named '_cffi_backend'"
```bash
pip3 install --upgrade cffi cryptography
```

### Error: "duplicate key value violates unique constraint"
This is OK! It means that program is already in your database. The script skips it and continues.

### Programs show as "Already in database - skipping"
✅ This is normal if you've run the script before. It won't create duplicates.

---

## 🎨 Next Steps: Update Dashboard

After loading, you'll want to update the dashboard to show all the new data:

### 1. The dashboard already exists at:
```
dashboard/funding.html
```

### 2. To update it with database data (instead of hardcoded):
We'd need to create an API endpoint or data export. For now, the dashboard uses hardcoded data from our research.

### 3. To see database data directly:
Use Supabase dashboard:
1. Go to your Supabase project
2. Click "Table Editor"
3. Select "documents" table
4. You'll see all programs listed

### 4. Or query programmatically:
```python
from supabase import create_client
import os
from dotenv import load_dotenv

load_dotenv()
supabase = create_client(
    os.getenv('SUPABASE_URL'),
    os.getenv('SUPABASE_SERVICE_ROLE_KEY')
)

# Get all programs by community
results = supabase.table('documents')\
    .select('*')\
    .contains('locations_mentioned', ['Mount Isa'])\
    .execute()

total = sum(r['funding_amount_extracted'] for r in results.data if r['funding_amount_extracted'])
print(f"Mount Isa total: ${total:,.0f}")
```

---

## 📈 Expected Results

After loading, your database will show:

**Mount Isa:** $56.88M (↑ from $53.38M)
- Added headspace center

**Gold Coast:** $50.75M (↑ from $30.8M)
- Added Youth Foyer + 2 headspace centers

**Townsville:** $67.45M (↑ from $28M)
- Added historical programs + Youth Foyer + headspace

**Cairns:** $72.6M (↑ from $28M)
- Added historical programs + headspace

**Logan:** $71.1M (↑ from $20.9M)
- Added historical programs + Youth Foyer + headspace

**Total Database:** ~$350M+ (↑ from $202M)

---

## 💡 What's Still Missing

This loader includes ~30 programs worth $90M, but we found $418M+ in total.

**Not yet included in this loader:**
- Education infrastructure ($210M for Logan alone)
- Community Safety programs ($100M+)
- Commonwealth contracts ($150-200M)
- Remaining historical programs

**Why not included yet:**
- Need more detailed program-by-program breakdowns
- Some are statewide programs (need to calculate regional allocations)
- Education infrastructure may need separate table

**To add later:**
Create additional loader scripts or manually add via Supabase UI.

---

## ✅ Success Checklist

- [ ] .env file created with Supabase credentials
- [ ] Python dependencies installed
- [ ] Script runs without errors
- [ ] See "Loaded successfully" for new programs
- [ ] Check database stats show increased totals
- [ ] View data in Supabase Table Editor
- [ ] Dashboard shows updated information

---

**Ready to load?** Run: `python3 scripts/load_comprehensive_funding.py`

**Need help?** Check the error messages above or verify your .env file is correct.
