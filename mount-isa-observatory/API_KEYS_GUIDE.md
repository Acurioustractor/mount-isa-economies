# API Keys & Configuration Guide

## Summary of Required Services

### ✅ Already Configured

**ABN Lookup GUID**: `e3df2bb0-a40b-40f9-b771-0cef7e9d667b`
- Status: **CONFIRMED & WORKING**
- Used by: Supplier lookups, business data enrichment
- No action needed

---

## 🔍 Keys You Need to Find

### 1. Supabase Configuration

**What it's for**: Cloud PostgreSQL database + vector embeddings for AI chat
**Used by**: `scripts/chat_with_data.py` (RAG/LLM interface)

**You need to find these 3 values from your Supabase dashboard**:

1. **SUPABASE_URL**
   - Format: `https://xxxxxxxxxxxxx.supabase.co`
   - Location: Supabase Dashboard → Settings → API
   - Example: `https://abcdefghijklm.supabase.co`

2. **SUPABASE_SERVICE_ROLE_KEY**
   - Format: Long JWT token starting with `eyJ...`
   - Location: Supabase Dashboard → Settings → API → Service Role Key
   - ⚠️ **SECRET** - Full admin access, never commit to git

3. **SUPABASE_ANON_KEY** (optional but recommended)
   - Format: Long JWT token starting with `eyJ...`
   - Location: Supabase Dashboard → Settings → API → Anon/Public Key
   - Used for public-facing queries

**How to find**:
- Go to: https://app.supabase.com/
- Select your project
- Click Settings (gear icon) → API
- Copy the values

**If you don't remember which Supabase project**:
- Check your browser history for `*.supabase.co`
- Check email for Supabase project creation confirmation
- Projects may be named: `mount-isa-observatory`, `mount-isa-platform`, etc.

---

### 2. OpenAI API Key

**What it's for**: GPT-4 for answering questions about economic data
**Used by**: `scripts/chat_with_data.py`

**You need**:

**OPENAI_API_KEY**
- Format: `sk-proj-...` or `sk-...` (starts with `sk-`)
- Location: https://platform.openai.com/api-keys
- Cost: Pay-per-use (embeddings + GPT-4 calls)

**How to find**:
- Go to: https://platform.openai.com/api-keys
- Look for existing key named something like "Mount Isa" or "Economic Observatory"
- ⚠️ If you can't find it, you may need to create a new one (OpenAI doesn't show keys after creation)

**If creating new key**:
```bash
# Go to: https://platform.openai.com/api-keys
# Click "Create new secret key"
# Name it: "Mount Isa Economic Observatory"
# Copy immediately - can't view again!
```

---

### 3. Firecrawl API Key (Recommended - Bypasses 403 Blocks)

**What it's for**: Advanced web scraping that bypasses anti-bot measures
**Used by**: Media statements scraper, any blocked government sites

**Why you need this**:
- Queensland Gov sites return 403 Forbidden with simple requests
- Firecrawl handles JavaScript rendering, CAPTCHAs, and anti-bot blocks
- More reliable than user-agent spoofing or proxies

**You need**:

**FIRECRAWL_API_KEY**
- Format: `fc-...` (starts with `fc-`)
- Location: https://firecrawl.dev/
- Cost: **FREE tier** - 500 credits/month, then $0.50 per 1,000 credits

**How to create**:
```bash
# 1. Go to: https://firecrawl.dev/
# 2. Sign up (GitHub login works)
# 3. Get API key from dashboard
# 4. Add to .env: FIRECRAWL_API_KEY=fc-your_key_here
```

**Installation**:
```bash
pip install firecrawl-py
```

**Test it works**:
```bash
python scrapers/mount_isa_media_statements_firecrawl.py
```

**Pricing Breakdown**:
- **Free tier**: 500 credits/month (enough for 500 pages)
- **Paid**: $25/month for 50,000 credits
- **One page scrape**: 1 credit
- **Structured extraction**: 2 credits

**Cost estimate for Mount Isa project**:
- Scraping 10 media statements: 10 credits
- With structured extraction: 20 credits
- Monthly scraping: ~100 credits
- **Fits easily in free tier! 🎉**

**When to use**:
- ✅ Queensland Government sites (403 blocks)
- ✅ JavaScript-heavy sites
- ✅ Sites with CAPTCHAs
- ✅ When simple requests fail
- ❌ When simple requests work (save credits)

---

### 4. Database Password (Optional - Only if NOT using Supabase)

**What it's for**: Local PostgreSQL database (alternative to Supabase)

**You need**:
- **DB_PASSWORD**: Your local PostgreSQL password

**When you need this**:
- If running database locally instead of Supabase cloud
- If you set up PostgreSQL on your machine

**If you don't remember**:
- Check: `~/.pgpass` (PostgreSQL password file)
- Check: Your password manager
- You may need to reset it: `ALTER USER postgres PASSWORD 'new_password';`

---

## 🔎 Where to Look for Old Keys

### 1. Check Old .env File Backups

```bash
# In your mount-isa-observatory directory
ls -la .env*
# Look for: .env.backup, .env.old, .env.local

# Also check parent directory
ls -la ../.env*

# Check Time Machine or other backups
```

### 2. Check Git History (Private Repos Only)

```bash
# Search git history for Supabase
git log --all --full-history --source -- **/.env

# Search for commits with "supabase" or "openai"
git log --all --grep="supabase\|openai\|API"
```

### 3. Check Other Files

```bash
# Search all files for Supabase URL pattern
grep -r "supabase.co" ~/mount-isa-economies/ 2>/dev/null

# Search for OpenAI key pattern
grep -r "sk-proj" ~/mount-isa-economies/ 2>/dev/null
grep -r "OPENAI_API_KEY" ~/mount-isa-economies/ 2>/dev/null
```

### 4. Check Password Managers
- 1Password
- LastPass
- Bitwarden
- macOS Keychain

Search for:
- "Supabase"
- "OpenAI"
- "Mount Isa"
- "Economic Observatory"

### 5. Check Email
Search your email for:
- "Supabase" + "project created"
- "OpenAI" + "API key"
- "mount-isa"

---

## 🚀 What Works Without Additional Keys

You can use these features **RIGHT NOW** with just the ABN GUID:

✅ **All Data Scrapers**:
- Media statements (via WebSearch)
- Budget papers
- ACNC charity lookups
- Federal grants
- ABN business lookups
- Contract data
- Council documents

✅ **Data Collection**:
- `python3 scrapers/comprehensive_money_flow_scraper.py`
- `python3 scrapers/abn_lookup_professional.py`
- All Queensland government data sources

❌ **Requires Supabase + OpenAI**:
- `python3 scripts/chat_with_data.py` (AI chat interface)
- RAG/semantic search
- Vector embeddings

---

## 📋 Priority Order

### Immediate (You Have Everything)
1. ✅ Continue data scraping - ABN GUID confirmed working
2. ✅ Collect Mount Isa funding data - no additional keys needed

### When You Find Supabase Keys
1. Test connection: `python3 -c "from supabase import create_client; print('Connected')"`
2. Set up vector embeddings for chat interface
3. Import scraped data into Supabase

### When You Find OpenAI Key (or Create New)
1. Test: `python3 -c "import openai; openai.api_key='YOUR_KEY'; print('Valid')"`
2. Enable AI chat interface
3. Run: `python3 scripts/chat_with_data.py`

---

## 🔐 Security Best Practices

1. **Never commit .env to git**
   - Already in `.gitignore` ✅

2. **Use different keys for dev/prod**
   - Create separate OpenAI keys for testing

3. **Rotate keys periodically**
   - Especially if shared or exposed

4. **Backup your .env file securely**
   - Encrypted backup on different machine
   - Password manager
   - NOT in the same git repo

---

## 🆘 If You Can't Find Old Keys

### Supabase
**Option 1**: Find existing project
- Login to https://app.supabase.com/
- Look for "mount-isa" project
- Get keys from Settings → API

**Option 2**: Create new project (free tier)
```bash
# Go to: https://app.supabase.com/
# Click "New Project"
# Name: mount-isa-observatory
# Free tier: 500MB database, 2GB bandwidth/month
# Get keys immediately after creation
```

### OpenAI
**Must create new key** (old keys can't be viewed)
```bash
# Go to: https://platform.openai.com/api-keys
# Click "Create new secret key"
# Name: "Mount Isa Economic Observatory"
# Copy immediately!
```

**Cost estimate**:
- Embeddings: ~$0.10 per 1M tokens
- GPT-4: ~$0.03 per 1K tokens
- Expected monthly: $5-20 for moderate use

---

## 📞 Support Resources

**Supabase**:
- Docs: https://supabase.com/docs
- Support: https://supabase.com/dashboard/support

**OpenAI**:
- Docs: https://platform.openai.com/docs
- API Keys: https://platform.openai.com/api-keys
- Usage: https://platform.openai.com/usage

**ABN Lookup**:
- Web Services: https://abr.business.gov.au/Tools/WebServices
- Your GUID: e3df2bb0-a40b-40f9-b771-0cef7e9d667b ✅

---

## ✅ Current Status

As of 2025-11-14:

| Service | Status | Notes |
|---------|--------|-------|
| ABN Lookup GUID | ✅ Confirmed | e3df2bb0-a40b-40f9-b771-0cef7e9d667b |
| Supabase URL | ❓ Need to find | Check dashboard or old backups |
| Supabase Service Key | ❓ Need to find | Check dashboard or old backups |
| OpenAI API Key | ❓ Need to find | May need to create new |
| Database Password | ⚪ Optional | Only if using local PostgreSQL |
| ASIC API Key | ⚪ Optional | Not currently used |

**Next Action**: Search for Supabase and OpenAI keys using the methods above, or create new ones if needed.
