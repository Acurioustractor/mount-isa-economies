# Loading All Communities Funding Data

## 📦 What We've Compiled

We've found comprehensive youth justice funding for **9 Queensland communities** totaling **$202.7M**:

| Community | Total Funding | Programs | Status |
|-----------|---------------|----------|--------|
| Mount Isa | $53.38M | 7 | ✅ Already in database |
| Cairns | $26.2M | 3 | 🔄 Ready to load |
| Gold Coast | $30.8M | 3 | 🔄 Ready to load |
| Logan | $20.9M | 2 | 🔄 Ready to load |
| Townsville | $28M | 3 | 🔄 Ready to load |
| Ipswich | $18.9M | 3 | 🔄 Ready to load |
| Rockhampton | $18M | 2 | 🔄 Ready to load |
| Torres Strait | $3.78M | 2 | 🔄 Ready to load (+$3M) |
| Palm Island | $2.74M | 2 | 🔄 Ready to load (+$2M) |

---

## 🚀 How to Load the Data

### Step 1: Set Up Supabase Credentials
Make sure you have a `.env` file with your Supabase credentials:

```bash
cd /home/user/mount-isa-economies/mount-isa-observatory
cp .env.example .env
nano .env  # Add your credentials
```

Required variables:
```
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key
```

### Step 2: Run the Loading Script
```bash
python3 scripts/load_all_communities_funding.py
```

This will:
- Load funding data for 8 communities (Mount Isa already loaded)
- Skip duplicates (won't re-add Mount Isa)
- Validate all data before inserting
- Show progress for each program
- Print summary statistics

---

## 📊 Expected Results

### New Records Added:
- **Total programs**: ~25 new records
- **New funding tracked**: ~$149M (beyond Mount Isa's $53M)
- **Communities updated**: 8 (Cairns, Gold Coast, Logan, Townsville, Ipswich, Rockhampton, Torres Strait, Palm Island)

### Database After Loading:
```
Total documents: ~86 (was 61)
Total funding: ~$202M (was $53M)

By community:
- Mount Isa: 9 docs, $53.38M
- Gold Coast: 3 docs, $30.8M
- Townsville: 3 docs, $28M
- Cairns: 3 docs, $26.2M
- Logan: 2 docs, $20.9M
- Ipswich: 3 docs, $18.9M
- Rockhampton: 2 docs, $18M
- Torres Strait: 8 docs, $3.78M
- Palm Island: 7 docs, $2.74M
```

---

## 📁 Files Created

### 1. **Loading Script**
`scripts/load_all_communities_funding.py`
- Comprehensive funding data for 8 communities
- Ready to load into Supabase
- Includes confidence scores and validation

### 2. **Funding Summary Document**
`data/media_statements/ALL_COMMUNITIES_FUNDING_SUMMARY.md`
- Complete breakdown of all $202.7M
- Program details, confidence levels, URLs
- Status: Which data is loaded vs ready to load

### 3. **Comparative Analysis**
`COMMUNITIES_FUNDING_COMPARISON.md`
- Mount Isa vs other communities
- Per capita analysis
- Economic impact calculations
- Key insights and recommendations

---

## 🔍 Data Quality Notes

### Confidence Levels:
- **0.95 (High)**: Explicitly stated amounts (e.g., Gold Coast $10M)
- **0.80 (Good)**: Calculated from program totals (e.g., $40M ÷ 2 schools)
- **0.70 (Medium)**: Estimated from typical allocations
- **0.60 (Lower)**: Regional estimates without specific breakdowns

### What's Verified:
✅ Mount Isa $53.38M - All programs from official statements
✅ Gold Coast Men of Business $10M - Explicitly stated
✅ Youth Justice Schools $40M total - Budget papers
✅ Crime Prevention Schools $50M total - Budget papers

### What Needs Verification:
⚠️ Staying on Track regional allocations - estimated
⚠️ Kickstarter individual program amounts - estimated
⚠️ Regional Reset per-location amounts - estimated (from $50M÷9)

---

## 📈 Next Steps After Loading

### 1. **Verify Database Stats**
```bash
python3 scripts/database_stats.py
```

Should show:
- 9 communities with funding data
- $202M+ total funding
- Mount Isa as #1 in absolute dollars
- Palm Island as #1 per capita

### 2. **Generate Comparison Charts**
Create visualizations:
- Total funding by community (bar chart)
- Per capita funding (scatter plot)
- Program types distribution (pie chart)
- Timeline of announcements (timeline)

### 3. **Verify Actual Delivery**
For each major program, check:
- Has the money actually flowed?
- Are programs operational?
- How many youth served?
- Local jobs created?

**Example verification for Mount Isa:**
- Call Mithangkaya Nguli: Has $24M arrived?
- Check council: Is Stronger Communities ($7M) operating?
- Interview co-responder team: How many staff?

---

## 🎯 Use Cases for This Data

### For Community Advocacy:
> "Mount Isa has been allocated $53.38M - we want to verify delivery and maximize local economic benefit."

### For Economic Analysis:
> "If $53.38M is fully delivered, it represents 7% of Mount Isa's annual economy with 50-80 jobs created."

### For Policy Research:
> "Comparing funding across 9 communities shows Mount Isa leads in absolute dollars ($53M) but Torres Strait/Palm Island lead per capita."

### For Transparency:
> "We've tracked $202M in youth justice funding across Queensland - here's where it's going."

---

## ⚠️ Troubleshooting

### If you see "Already in database - skipping":
✅ This is normal! It means Mount Isa data is already loaded.
The script will load the other 8 communities.

### If you see validation warnings:
⚠️ Review the warnings but they're informational only.
Data will still load unless there's a critical error.

### If you see database connection errors:
❌ Check your .env file has correct Supabase credentials
❌ Verify SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are set

---

## 📞 Support

### Data Questions:
- See `ALL_COMMUNITIES_FUNDING_SUMMARY.md` for full details
- Check `COMMUNITIES_FUNDING_COMPARISON.md` for analysis

### Technical Issues:
- Verify .env file exists with credentials
- Check Python dependencies installed: `pip3 install python-dotenv supabase`
- Try running Mount Isa script first to test connection:
  ```bash
  python3 scripts/load_funding_summary_to_db.py
  ```

---

## 🎉 What You'll Achieve

After loading this data, you'll have:

✅ **Comprehensive funding database** across 9 communities
✅ **$202M tracked** - 4x more than before
✅ **Comparative analysis** showing Mount Isa's position
✅ **Economic impact data** for advocacy
✅ **Foundation for testing** economics theories (Preston, LM3, Jacobs)

**You'll transform your database from:**
- 61 documents, $53M, 1 community focus

**To:**
- 86+ documents, $202M+, 9 communities compared

---

*Ready to load? Run:* `python3 scripts/load_all_communities_funding.py`
