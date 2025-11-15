# Quick Start: AI Document System

**You just scraped 59 statements ($9.1B in funding)!** Here's how to get them into the AI system in 3 steps.

---

## ✅ Step 1: Set Up Database Schema (5 minutes)

### 1a. Enable pgvector in Supabase

Go to your Supabase project SQL Editor and run:

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### 1b. Add AI Tables

Copy the contents of `database/schema_ai_document_chunks.sql` and paste into Supabase SQL Editor, then run it.

This creates:
- `documents` - Main table for all statements
- `document_chunks` - Text chunks with embeddings for search
- `ai_analysis` - AI-generated insights
- `document_links` - Relationships between documents
- `story_templates` - Templates for auto-generating stories
- `generated_stories` - AI-generated stories ready to publish
- `processing_queue` - Track AI processing pipeline
- `processing_logs` - Audit logs

**Verify it worked:**
```sql
SELECT table_name
FROM information_schema.tables
WHERE table_schema = 'public'
  AND table_name IN ('documents', 'document_chunks', 'ai_analysis');
```

Should see 3 rows (or more).

---

## ✅ Step 2: Load Your 59 Statements (2 minutes)

Run the loader:

```bash
python3 scripts/load_documents_to_ai_system.py \
  --csv /Users/benknight/Code/mount-isa/mount-isa-observatory/data/media_statements/firecrawl_scraped_results.csv
```

**What this does:**
- Loads 59 statements into `documents` table
- Extracts funding amounts, programs, locations automatically
- Categorizes each document (early_intervention, detention, on_country, etc.)
- Queues all documents for AI processing

**Expected output:**
```
✅ 59 documents loaded
✅ 236 processing queue items created (59 docs × 4 stages)
```

**Verify in Supabase:**
```sql
-- See your documents
SELECT
    id,
    title,
    published_date,
    funding_amount_extracted,
    array_length(programs_mentioned, 1) as programs_count,
    array_length(locations_mentioned, 1) as locations_count,
    categories
FROM documents
ORDER BY published_date DESC
LIMIT 10;

-- Check processing queue
SELECT stage, status, COUNT(*)
FROM processing_queue
GROUP BY stage, status;
```

---

## ✅ Step 3: Explore Your Data (immediate)

Now you can query your data! Here are some useful queries:

### 3a. Find Largest Funding Announcements

```sql
SELECT
    title,
    published_date,
    funding_amount_extracted as funding_m,
    programs_mentioned,
    locations_mentioned
FROM documents
WHERE funding_amount_extracted > 0
ORDER BY funding_amount_extracted DESC
LIMIT 20;
```

### 3b. Mount Isa Specific Programs

```sql
SELECT
    title,
    published_date,
    funding_amount_extracted,
    programs_mentioned
FROM documents
WHERE 'Mount Isa' = ANY(locations_mentioned)
   OR 'mount_isa' = ANY(categories)
ORDER BY published_date DESC;
```

### 3c. Recent 2025 Announcements

```sql
SELECT
    published_date,
    title,
    funding_amount_extracted,
    locations_mentioned
FROM documents
WHERE published_date >= '2025-01-01'
ORDER BY published_date DESC;
```

### 3d. What Categories Do We Have?

```sql
SELECT
    UNNEST(categories) as category,
    COUNT(*) as doc_count,
    SUM(funding_amount_extracted) as total_funding_m
FROM documents
GROUP BY category
ORDER BY doc_count DESC;
```

### 3e. Funding by Location

```sql
SELECT
    UNNEST(locations_mentioned) as location,
    COUNT(*) as announcements,
    SUM(funding_amount_extracted) as total_funding_m
FROM documents
WHERE funding_amount_extracted > 0
GROUP BY location
ORDER BY total_funding_m DESC
LIMIT 15;
```

### 3f. Timeline: When Are Announcements Made?

```sql
SELECT
    DATE_TRUNC('month', published_date) as month,
    COUNT(*) as announcements,
    SUM(funding_amount_extracted) as total_funding_m
FROM documents
GROUP BY month
ORDER BY month DESC;
```

---

## 🤖 Next: AI Processing (Optional - Requires OpenAI API)

### Prerequisites

You need an OpenAI API key for AI analysis. Add to `.env`:

```bash
OPENAI_API_KEY=sk-proj-...
```

### Run AI Pipeline (Coming Soon)

The AI pipeline will be created in the next step. It will:

1. **Chunk documents** - Split into searchable chunks
2. **Generate embeddings** - Enable semantic search
3. **AI analysis** - Summarize, extract entities, verify claims
4. **Generate stories** - Create accountability stories automatically

**Estimated cost for 59 documents:**
- Embeddings: $0.012
- Analysis: $1.18
- **Total: ~$1.20**

---

## 📊 What You Have Now

### Database Summary

Run this query to see your data:

```sql
SELECT
    COUNT(*) as total_documents,
    COUNT(*) FILTER (WHERE published_date >= '2025-01-01') as documents_2025,
    COUNT(*) FILTER (WHERE published_date >= '2024-01-01' AND published_date < '2025-01-01') as documents_2024,
    SUM(funding_amount_extracted) / 1000 as total_funding_billions,
    COUNT(DISTINCT UNNEST(locations_mentioned)) as unique_locations,
    COUNT(DISTINCT UNNEST(programs_mentioned)) as unique_programs,
    MIN(published_date) as earliest_date,
    MAX(published_date) as latest_date
FROM documents;
```

**Expected results:**
- Total documents: 59
- Total funding: $9.1B
- Date range: 2006 → November 2025
- Unique locations: ~15
- Unique programs: ~10-15

### Top Funding Programs

```sql
SELECT
    UNNEST(programs_mentioned) as program,
    COUNT(*) as mentions,
    SUM(funding_amount_extracted) as total_funding_m
FROM documents
WHERE funding_amount_extracted > 0
GROUP BY program
ORDER BY total_funding_m DESC
LIMIT 10;
```

### Coverage by Year

```sql
SELECT
    EXTRACT(YEAR FROM published_date) as year,
    COUNT(*) as documents,
    SUM(funding_amount_extracted) as total_funding_m
FROM documents
GROUP BY year
ORDER BY year DESC;
```

---

## 🎯 Common Use Cases

### Find All Mount Isa Announcements

```sql
SELECT
    published_date,
    title,
    funding_amount_extracted,
    programs_mentioned,
    url
FROM documents
WHERE 'Mount Isa' = ANY(locations_mentioned)
ORDER BY published_date DESC;
```

### Find On-Country Programs

```sql
SELECT
    title,
    published_date,
    funding_amount_extracted,
    locations_mentioned
FROM documents
WHERE 'on_country' = ANY(categories)
   OR programs_mentioned && ARRAY['On-Country', 'On Country']
ORDER BY funding_amount_extracted DESC;
```

### Find Recent (2025) Early Intervention Programs

```sql
SELECT
    title,
    published_date,
    funding_amount_extracted,
    programs_mentioned,
    locations_mentioned
FROM documents
WHERE published_date >= '2025-01-01'
  AND 'early_intervention' = ANY(categories)
ORDER BY published_date DESC;
```

### Search for Specific Keywords

```sql
SELECT
    title,
    published_date,
    funding_amount_extracted,
    full_text
FROM documents
WHERE full_text ILIKE '%staying on track%'
   OR full_text ILIKE '%regional reset%'
ORDER BY published_date DESC;
```

---

## 🔍 Understanding Your Data

### Most Common Programs

```sql
SELECT
    program,
    COUNT(*) as frequency
FROM (
    SELECT UNNEST(programs_mentioned) as program
    FROM documents
) programs
GROUP BY program
ORDER BY frequency DESC;
```

### Most Mentioned Locations

```sql
SELECT
    location,
    COUNT(*) as mentions,
    SUM(funding_amount_extracted) FILTER (WHERE funding_amount_extracted > 0) as total_funding_m
FROM (
    SELECT
        UNNEST(locations_mentioned) as location,
        funding_amount_extracted
    FROM documents
) locations
GROUP BY location
ORDER BY mentions DESC;
```

### Documents by Category

```sql
SELECT
    category,
    COUNT(*) as documents,
    ROUND(AVG(funding_amount_extracted), 2) as avg_funding_m,
    SUM(funding_amount_extracted) as total_funding_m
FROM (
    SELECT
        UNNEST(categories) as category,
        funding_amount_extracted
    FROM documents
) cat
GROUP BY category
ORDER BY documents DESC;
```

---

## 📈 Next Steps

### 1. Explore the Full Guide

See `AI_SYSTEM_GUIDE.md` for:
- Complete architecture explanation
- AI processing pipeline details
- Story generation templates
- Semantic search setup
- Advanced querying

### 2. Add More Data

Continue scraping and loading:

```bash
# Scrape more URLs (you have 109 total discovered)
python3 scripts/scrape_discovered_urls_firecrawl.py

# Load to AI system
python3 scripts/load_documents_to_ai_system.py \
  --csv data/media_statements/firecrawl_scraped_results.csv
```

### 3. Set Up Semantic Search (Requires pgvector + OpenAI)

```sql
-- Create vector index (after generating embeddings)
CREATE INDEX idx_chunks_embedding ON document_chunks
USING ivfflat (embedding vector_cosine_ops)
WITH (lists = 100);
```

### 4. Generate Stories

Once AI analysis is complete, generate stories:

```bash
python3 scripts/generate_stories.py
```

---

## 🐛 Troubleshooting

### "Table doesn't exist"

You need to run the schema first:
```bash
# Copy contents of database/schema_ai_document_chunks.sql
# Paste into Supabase SQL Editor
# Run it
```

### "Foreign key violation"

Make sure you ran the full schema, not just parts.

### "CSV file not found"

Use the full path from your terminal output:
```bash
/Users/benknight/Code/mount-isa/mount-isa-observatory/data/media_statements/firecrawl_scraped_results.csv
```

### "No data returned"

Check if documents loaded:
```sql
SELECT COUNT(*) FROM documents;
```

Should be > 0.

---

## 🎉 You're Ready!

You now have:
- ✅ 59 documents in database
- ✅ $9.1B in funding tracked
- ✅ Auto-extracted entities (programs, locations, amounts)
- ✅ Categorized documents
- ✅ Ready for AI analysis

**Next:** Run some queries and explore your data! See the Use Cases section above.

---

**Questions?** See the full guide: `AI_SYSTEM_GUIDE.md`
