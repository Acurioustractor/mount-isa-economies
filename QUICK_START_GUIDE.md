# Quick Start: Get Your Economic Observatory Running in 1 Hour

**What you'll have**: A live database with all your economic data, accessible via chat/LLM, automatically updating daily.

---

## Step 1: Create Supabase Project (5 minutes)

1. Go to https://supabase.com
2. Sign up (free tier works fine to start)
3. Click "New Project"
4. Name it: `mount-isa-economic-observatory`
5. Choose a password (save it)
6. Choose region: `Southeast Asia (Singapore)` (closest to Australia)
7. Wait ~2 minutes for project to provision

---

## Step 2: Run Database Setup (10 minutes)

1. In Supabase dashboard, click **"SQL Editor"** in left sidebar
2. Click **"New Query"**
3. Copy and paste ALL the SQL from `supabase/migrations/001_initial_schema.sql`
4. Click **"Run"**
5. You'll see "Success. No rows returned" - that's good!

This creates all your tables:
- organizations
- financial_records
- contracts
- grants
- parliament_records
- community_conversations
- document_embeddings (for LLM)

---

## Step 3: Load Your Existing Data (15 minutes)

### Option A: Upload via Dashboard (Easy)

1. In Supabase, go to **"Table Editor"**
2. Click **"contracts"** table
3. Click **"Insert"** → **"Import data via CSV"**
4. Upload `mount-isa-observatory/data/qld_contracts/*.csv`
5. Repeat for other tables

### Option B: Use Script (Better)

```bash
cd mount-isa-observatory
python3 scripts/migrate_to_supabase.py
```

This script will:
- Read all your CSV files
- Clean and transform data
- Upload to Supabase
- Show progress bars

---

## Step 4: Enable Vector Search (5 minutes)

1. In SQL Editor, run:

```sql
-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Create vector index
CREATE INDEX ON document_embeddings
USING hnsw (embedding vector_cosine_ops);
```

2. Get OpenAI API key:
   - Go to https://platform.openai.com/api-keys
   - Create new key
   - Copy it

3. In Supabase, go to **"Project Settings"** → **"Edge Functions"**
4. Add secret: `OPENAI_API_KEY` = your key

---

## Step 5: Generate Embeddings (10 minutes)

```bash
cd mount-isa-observatory
python3 scripts/generate_embeddings.py
```

This creates searchable chunks of all your data for LLM access.

Progress: `[████████████████████] 100% (1,234 / 1,234 documents embedded)`

---

## Step 6: Deploy Auto-Update Pipeline (10 minutes)

1. Install Supabase CLI:

```bash
brew install supabase/tap/supabase
```

2. Login:

```bash
supabase login
```

3. Link to your project:

```bash
cd mount-isa-observatory
supabase link --project-ref your-project-ref
```

(Find project-ref in Supabase dashboard → Settings → General)

4. Deploy scrapers:

```bash
supabase functions deploy daily-data-collection
supabase functions deploy grant-alerts
```

5. Set up daily schedule:

```sql
-- Run in SQL Editor
SELECT cron.schedule(
  'daily-data-collection',
  '0 2 * * *', -- 2 AM daily
  $$
  SELECT net.http_post(
    url := 'https://your-project.supabase.co/functions/v1/daily-data-collection',
    headers := jsonb_build_object('Authorization', 'Bearer ' || current_setting('app.service_role_key'))
  );
  $$
);
```

---

## Step 7: Test Your LLM Chat (5 minutes)

```bash
cd mount-isa-observatory
python3 scripts/chat_with_data.py
```

Try questions:
```
> What grant opportunities are open for indigenous businesses?
> Show me government contracts in Mount Isa over $100,000
> What do community members say about employment?
> How much funding has Mount Isa received in the last year?
```

---

## Step 8: Set Up Dashboard (10 minutes)

1. In `mount-isa-observatory/dashboard`, update `.env`:

```bash
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your-anon-key
```

2. Install and run:

```bash
cd dashboard
npm install
npm run dev
```

3. Open http://localhost:5173

You'll see:
- 🗺️ Map of all organizations
- 💰 Total funding flows
- 📊 Economic trends
- 💬 LLM chat interface
- 🔔 Grant alerts

---

## ✅ You're Done!

Your economic observatory is now:

✅ Storing all economic data in Supabase
✅ Searchable via LLM/chat
✅ Auto-updating daily
✅ Sending grant alerts
✅ Visualizing on dashboard
✅ Accessible from anywhere
✅ Costs ~$25/month

---

## What Happens Now (Automatic)

### Every Day at 2 AM:
1. ✅ Scrapers run automatically
2. ✅ New contracts downloaded
3. ✅ New grants discovered
4. ✅ Parliament records updated
5. ✅ Embeddings generated for new data
6. ✅ Analytics refreshed

### Every 4 Hours:
1. ✅ New grant opportunities detected
2. ✅ Matched to eligible organizations
3. ✅ Alerts sent (email/SMS)

### On Demand:
1. ✅ Chat with your data via LLM
2. ✅ Ask economic questions
3. ✅ Generate reports
4. ✅ Track funding flows

---

## Common Questions

### "How do I add community conversations?"

Dashboard → Community tab → "Add Conversation"

Or via SQL:
```sql
INSERT INTO community_conversations (
  participant_role,
  conversation_text,
  themes,
  conversation_date
) VALUES (
  'community_member',
  'We need more local job opportunities...',
  ARRAY['employment', 'local_business'],
  CURRENT_DATE
);
```

### "How do I see what data updated?"

```sql
-- See recent updates
SELECT
  source_table,
  COUNT(*) as new_records,
  MAX(created_at) as last_update
FROM (
  SELECT 'contracts' as source_table, created_at FROM contracts
  WHERE created_at > NOW() - INTERVAL '7 days'
  UNION ALL
  SELECT 'grants', created_at FROM grants
  WHERE created_at > NOW() - INTERVAL '7 days'
) combined
GROUP BY source_table;
```

### "How do I export data?"

Supabase dashboard → Table Editor → Select table → Export as CSV

Or via API:
```bash
curl "https://your-project.supabase.co/rest/v1/contracts?select=*" \
  -H "apikey: your-anon-key" \
  -H "Authorization: Bearer your-anon-key" \
  > contracts.json
```

### "Can I share this with the community?"

Yes! Two options:

1. **Public dashboard**: Set Row Level Security policies
2. **API access**: Generate read-only API keys
3. **Reports**: Export PDF reports via dashboard

### "How do I backup my data?"

Automatic daily backups on Supabase Pro plan ($25/month).

Manual backup:
```bash
supabase db dump > backup_$(date +%Y%m%d).sql
```

---

## Next: Add Your Custom Features

See `ADVANCED_FEATURES.md` for:
- 📧 Email grant alerts
- 📱 SMS notifications
- 🎨 Custom visualizations
- 🤝 Community contribution forms
- 📈 Advanced analytics
- 🌐 Public website
- 🔐 Multi-user access

---

## Get Help

- **Technical issues**: Check Supabase docs or Discord
- **Data questions**: Review `DATA_SOURCES_COMPREHENSIVE.md`
- **Architecture**: See `SUPABASE_ECONOMIC_OBSERVATORY_ARCHITECTURE.md`
- **Community**: Set up regular co-design sessions

---

**You now have a world-class economic intelligence platform.**
**Built for community ownership, powered by AI, updating automatically.**
**Cost: Less than a Netflix subscription.**
