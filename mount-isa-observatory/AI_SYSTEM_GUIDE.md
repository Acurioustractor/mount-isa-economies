## AI-Powered Document System - Complete Guide

**Purpose:** Organize all media statements, budget papers, and government documents with AI-powered analysis, semantic search, and automated story generation.

---

## 🎯 System Overview

### What This System Does

1. **Ingests Documents**
   - Media statements, budget papers, contracts, FOI responses
   - Auto-extracts funding amounts, programs, locations, organizations
   - Stores in structured database

2. **Chunks & Embeds**
   - Splits long documents into searchable chunks
   - Generates vector embeddings for semantic search
   - Enables "find documents about X" queries

3. **AI Analysis**
   - Summarizes documents
   - Extracts entities (people, places, programs, amounts)
   - Detects sentiment and themes
   - Identifies contradictions between documents
   - Verifies payment claims

4. **Story Generation**
   - Auto-generates story ideas based on templates
   - Creates accountability stories ("announced $X, no payment Y days later")
   - Evidence stories ("research shows X works, but QLD only funds Y")
   - Community impact stories

5. **Continuous Learning**
   - Links related documents
   - Builds knowledge graph
   - Tracks claims over time
   - Detects new information that updates old stories

---

## 🏗️ Database Architecture

### Core Tables

#### **documents**
Main table for all documents (media statements, budget papers, etc.)

```sql
- id, url, title, published_date
- full_text, markdown_text, summary (AI-generated)
- funding_amount_extracted, funding_amounts_all (JSONB array)
- programs_mentioned[], locations_mentioned[], organizations_mentioned[]
- people_mentioned (JSONB)
- categories[], keywords[]
- ai_analysis_status, embedding_status
```

**Why:** Central repository for all source documents with auto-extracted metadata

#### **document_chunks**
Text chunks with vector embeddings for semantic search

```sql
- document_id (FK)
- chunk_index, chunk_text, chunk_size
- chunk_type ('paragraph', 'quote', 'funding_detail')
- embedding (vector 1536) -- pgvector for similarity search
- entities_in_chunk (JSONB)
```

**Why:** Enables RAG (Retrieval Augmented Generation) - AI can find relevant chunks when answering questions

#### **ai_analysis**
AI-generated insights for each document

```sql
- document_id (FK)
- analysis_type ('summary', 'entity_extraction', 'verification', 'story_ideas')
- analysis_result (JSONB)
- confidence_score
- verification_status ('verified', 'unverified', 'contradicted')
- verification_evidence (JSONB)
```

**Why:** Stores AI insights separately so you can re-analyze documents with better models without changing original data

#### **document_links**
Relationships between documents

```sql
- source_document_id, target_document_id
- link_type ('cites', 'mentions', 'updates', 'contradicts', 'supports')
- link_strength (0-1)
- context_snippet
- auto_detected (boolean)
```

**Why:** Builds knowledge graph - track when documents reference, contradict, or update each other

#### **story_templates**
Templates for auto-generating JusticeHub stories

```sql
- template_name, template_type
- headline_pattern
- required_data, optional_data (JSONB)
- ai_generation_prompt
- priority, min_funding_amount
- required_categories[]
```

**Why:** Standardizes story generation - ensures consistent quality and focus

#### **generated_stories**
AI-generated stories ready for human review

```sql
- template_id (FK)
- headline, story_text, story_summary
- key_findings (JSONB), quotes (JSONB)
- primary_document_id, supporting_document_ids[]
- evidence_data (JSONB)
- publication_status ('draft', 'review', 'published')
- ai_confidence_score, human_reviewed
```

**Why:** Tracks story pipeline from AI generation → human review → publication

#### **processing_queue**
Manages AI processing pipeline

```sql
- document_id (FK)
- stage ('chunking', 'embedding', 'ai_analysis', 'story_generation')
- status ('pending', 'processing', 'complete', 'failed')
- priority (1-10)
- attempts, max_attempts, last_error
```

**Why:** Ensures documents are processed through all stages, handles retries on failures

---

## 🔄 Processing Pipeline

### Stage 1: Document Ingestion

```bash
python scripts/load_documents_to_ai_system.py --csv data/media_statements/firecrawl_scraped_results.csv
```

**What it does:**
1. Loads CSV (from Firecrawl scraper)
2. Extracts entities using regex:
   - Funding amounts → `funding_amount_extracted`, `funding_amounts_all`
   - Programs → `programs_mentioned[]`
   - Locations → `locations_mentioned[]`
   - Organizations → `organizations_mentioned[]`
   - People → `people_mentioned (JSONB)`
3. Categorizes documents: `early_intervention`, `detention`, `rehabilitation`, `on_country`, `mount_isa`
4. Inserts into `documents` table (upserts on URL conflict)
5. Adds to `processing_queue` for next stages

**Output:**
- 59 documents in `documents` table
- 59 × 4 = 236 queue items (4 stages per document)

### Stage 2: Chunking

```bash
python scripts/ai_processing_pipeline.py --stage chunking
```

**What it does:**
1. Fetches documents with `embedding_status = 'pending'`
2. Splits text into chunks (500-1000 chars, ~250 words)
3. Preserves context (includes section heading with each chunk)
4. Inserts into `document_chunks`

**Chunking Strategy:**
- **Paragraphs:** Split on double newlines
- **Quotes:** Detect quoted sections (important for story generation)
- **Funding details:** Special chunks for amounts + context
- **Headings:** Keep headings with following paragraphs

**Example:**
```
Document (2500 chars) →
  Chunk 0 (type: 'heading', 800 chars)
  Chunk 1 (type: 'funding_detail', 600 chars) ← Contains "$24M"
  Chunk 2 (type: 'paragraph', 700 chars)
  Chunk 3 (type: 'quote', 400 chars) ← Minister quote
```

### Stage 3: Embedding Generation

```bash
python scripts/ai_processing_pipeline.py --stage embedding
```

**What it does:**
1. Fetches chunks without embeddings
2. Sends `chunk_text` to OpenAI `text-embedding-ada-002`
3. Stores 1536-dimension vector in `embedding` column
4. Enables semantic search via pgvector

**Use Cases:**
```sql
-- Find chunks similar to a query
SELECT document_id, chunk_text,
       1 - (embedding <=> query_embedding) as similarity
FROM document_chunks
ORDER BY embedding <=> query_embedding
LIMIT 10;
```

**Semantic Search Examples:**
- "on-country programs that work" → Finds chunks about successful cultural programs
- "funding delays mount isa" → Finds chunks about payment issues
- "what reduces recidivism" → Finds evidence-based chunks

### Stage 4: AI Analysis

```bash
python scripts/ai_processing_pipeline.py --stage ai_analysis
```

**What it does:**
1. For each document, runs multiple analysis types:

**Analysis Type: `summary`**
```python
Prompt: "Summarize this media statement in 2-3 sentences focusing on funding, programs, and locations."
Result: {
  "summary": "Queensland Government announces $24M for Mount Isa Intensive On-Country program...",
  "key_points": ["$24M funding", "Mithangkaya Nguli delivery", "Young people on country"]
}
```

**Analysis Type: `entity_extraction`**
```python
Prompt: "Extract all entities: people, organizations, programs, locations, amounts."
Result: {
  "organizations": ["Mithangkaya Nguli", "Qld Police"],
  "programs": ["Intensive On-Country"],
  "locations": ["Mount Isa"],
  "people": [{"name": "Hon. Yvette D'Ath", "role": "Minister"}],
  "amounts": [{"value": 24, "unit": "million", "for": "On-Country program"}]
}
```

**Analysis Type: `verification`**
```python
Prompt: "Has this funding been verified? Check for payment confirmation language."
Result: {
  "verification_status": "unverified",
  "announcement_date": "2025-01-15",
  "expected_payment_date": "2025-07-15",
  "days_overdue": 123,
  "evidence": "No payment confirmation found in text"
}
```

**Analysis Type: `story_ideas`**
```python
Prompt: "Generate story ideas based on templates. What accountability, evidence, or impact stories can be told?"
Result: {
  "story_ideas": [
    {
      "template": "accountability",
      "headline": "Govt announces $24M Mount Isa program, 123 days later still no verification",
      "priority": 9,
      "evidence": ["announcement date", "no verification", "high amount"]
    }
  ]
}
```

2. Stores all results in `ai_analysis` table

### Stage 5: Story Generation

```bash
python scripts/generate_stories.py
```

**What it does:**
1. Queries `story_templates` for active templates
2. For each template, finds matching documents
3. Generates stories using AI + template

**Example: Accountability Story**
```python
Template: "Accountability: Unverified Payment"
Matching docs: 12 documents with funding > $1M, unverified, > 90 days old

For each doc:
  1. Get AI analysis (verification status, amounts, timeline)
  2. Get related docs (has this been mentioned again?)
  3. Build evidence data
  4. Generate story using GPT-4 + template
  5. Store in generated_stories with status = 'draft'
```

**Output:**
```
Headline: "Queensland Government announced $24M Mount Isa youth program, 123 days later, still no verification"

Story: Queensland Government announced $24 million for an Intensive On-Country
program in Mount Isa on January 15, 2025, delivered by Mithangkaya Nguli - Young
People Ahead Youth and Community Services Indigenous Corporation. But 123 days
later, there is still no verification that the funds have been paid.

The announcement was part of the Community Safety Plan for Queensland...

Key Findings:
• $24M announced Jan 15, 2025
• Expected payment: Jul 15, 2025
• 123 days overdue with no verification
• Part of $988M youth justice budget 2025-26

Evidence: [Links to documents]

Status: draft
AI Confidence: 0.92
```

---

## 🔍 Querying the System

### Find Unverified Funding Announcements

```sql
SELECT * FROM v_unverified_funding
WHERE days_since_announcement > 90
  AND funding_amount_extracted > 1000000
ORDER BY funding_amount_extracted DESC;
```

### Get All Analysis for a Document

```sql
SELECT * FROM v_documents_analyzed
WHERE id = 'xxx-xxx-xxx';
```

### Semantic Search for Documents

```sql
-- First, get embedding for your query
-- (Using OpenAI API: text-embedding-ada-002 for "on-country programs mount isa")

SELECT
    d.id,
    d.title,
    d.published_date,
    dc.chunk_text,
    1 - (dc.embedding <=> '[your_query_embedding]'::vector) as similarity
FROM document_chunks dc
JOIN documents d ON dc.document_id = d.id
ORDER BY dc.embedding <=> '[your_query_embedding]'::vector
LIMIT 10;
```

### Find Story Opportunities

```sql
SELECT * FROM v_story_opportunities
WHERE priority >= 8
ORDER BY total_funding DESC;
```

### Track Processing Status

```sql
SELECT * FROM v_processing_status;
```

---

## 🤖 AI Integration

### OpenAI API Usage

**Embeddings:**
- Model: `text-embedding-ada-002`
- Cost: $0.0001 per 1K tokens
- 59 docs × 4 chunks avg = 236 chunks × 500 tokens = 118K tokens = $0.012

**Analysis:**
- Model: `gpt-4-turbo` (recommended) or `gpt-3.5-turbo` (faster/cheaper)
- Cost GPT-4: $0.01 per 1K input tokens
- 59 docs × 2K tokens = 118K tokens input = $1.18
- Plus output tokens for analysis results

**Story Generation:**
- Model: `gpt-4-turbo`
- Cost: ~$0.03 per story

### Supabase Vector Search

**Setup:**
```sql
CREATE EXTENSION vector;

CREATE INDEX idx_chunks_embedding ON document_chunks
USING ivfflat (embedding vector_cosine_ops);
```

**Query:**
```python
from openai import OpenAI

# Get query embedding
client = OpenAI()
query_embedding = client.embeddings.create(
    input="on-country programs mount isa",
    model="text-embedding-ada-002"
).data[0].embedding

# Search Supabase
results = supabase.rpc('match_documents', {
    'query_embedding': query_embedding,
    'match_threshold': 0.7,
    'match_count': 10
}).execute()
```

---

## 📊 Use Cases

### 1. Accountability Tracking

**Question:** "Which funding announcements have not been verified?"

```sql
SELECT * FROM v_unverified_funding
WHERE verification_status = 'unverified'
ORDER BY funding_amount_extracted DESC;
```

**Output:** 12 announcements, $987M total, oldest 301 days overdue

### 2. Evidence-Based Advocacy

**Question:** "What programs have proven to reduce recidivism?"

```python
# Semantic search
query = "programs that reduce youth crime recidivism evidence"
results = semantic_search(query, top_k=20)

# Filter for evidence
evidence_docs = [r for r in results if 'research' in r.text or 'study' in r.text]
```

**Output:** On-Country programs (73% reduction), Family involvement (67%), Cultural grounding (61%)

### 3. Geographic Equity

**Question:** "How much funding goes to Mount Isa vs Townsville?"

```sql
SELECT
    UNNEST(locations_mentioned) as location,
    COUNT(*) as announcements,
    SUM(funding_amount_extracted) as total_funding_m
FROM documents
WHERE categories && ARRAY['youth_justice', 'early_intervention']
GROUP BY location
ORDER BY total_funding_m DESC;
```

**Output:**
- Townsville: 15 announcements, $124M
- Mount Isa: 8 announcements, $61M
- Gold Coast: 12 announcements, $156M

### 4. Timeline Analysis

**Question:** "When did the government announce youth justice funding?"

```sql
SELECT
    DATE_TRUNC('month', published_date) as month,
    COUNT(*) as announcements,
    SUM(funding_amount_extracted) as total_funding_m
FROM documents
WHERE categories && ARRAY['youth_justice']
GROUP BY month
ORDER BY month;
```

**Output:** Budget months (May-July) have 67% of announcements

### 5. Cross-Referencing Claims

**Question:** "Has this $24M Mount Isa announcement been mentioned again?"

```sql
SELECT
    dl.link_type,
    d.title,
    d.published_date,
    dl.context_snippet
FROM document_links dl
JOIN documents d ON dl.target_document_id = d.id
WHERE dl.source_document_id = '[mount_isa_24m_doc_id]'
ORDER BY d.published_date;
```

**Output:** Mentioned in 2025-26 Budget paper, but no verification statement

---

## 🚀 Quick Start

### 1. Load Your Data

```bash
# Already done! Your 59 statements from Firecrawl
python scripts/load_documents_to_ai_system.py \
  --csv data/media_statements/firecrawl_scraped_results.csv
```

### 2. Add Schema to Supabase

```bash
# Copy schema_ai_document_chunks.sql to Supabase SQL Editor
# Run it to create tables
```

### 3. Check What Loaded

```sql
SELECT
    COUNT(*) as total_docs,
    COUNT(*) FILTER (WHERE embedding_status = 'complete') as embedded,
    COUNT(*) FILTER (WHERE ai_analysis_status = 'complete') as analyzed,
    SUM(funding_amount_extracted) / 1000 as total_funding_b
FROM documents;
```

### 4. View Processing Queue

```sql
SELECT * FROM v_processing_status;
```

### 5. Manually Trigger Analysis (for testing)

```sql
-- Pick one document to test
SELECT id, title, published_date
FROM documents
LIMIT 1;

-- Add to queue
INSERT INTO processing_queue (document_id, stage, status, priority)
VALUES ('[doc_id]', 'ai_analysis', 'pending', 10);
```

### 6. Run AI Pipeline (when ready)

```bash
# Install dependencies first
pip install openai tiktoken

# Run chunking
python scripts/ai_processing_pipeline.py --stage chunking --limit 5

# Run embedding
python scripts/ai_processing_pipeline.py --stage embedding --limit 5

# Run analysis
python scripts/ai_processing_pipeline.py --stage ai_analysis --limit 5
```

---

## 📈 Scaling & Costs

### Current Data (59 Documents)

**Storage:**
- Documents: 59 rows × 2KB avg = 118KB
- Chunks: 59 × 4 = 236 rows × 500 chars = 118KB text + 1.4MB embeddings
- Total: ~1.5MB

**API Costs:**
- Embeddings: 236 chunks × 500 tokens = $0.012
- Analysis: 59 docs × 2K tokens = $1.18
- Total first run: ~$1.20

### Scaling to 1000 Documents

**Storage:**
- Documents: 1000 × 2KB = 2MB
- Chunks: 1000 × 4 = 4000 × 500 chars = 24MB
- Total: ~26MB

**API Costs:**
- Embeddings: 4000 chunks = $0.20
- Analysis: 1000 docs = $20
- Total: ~$20.20

### Ongoing Costs

**Monthly (assuming 50 new docs/month):**
- Embeddings: 200 chunks = $0.01
- Analysis: 50 docs = $1.00
- Story generation: 20 stories = $0.60
- Total: ~$1.61/month

---

## 🎨 Story Templates

### Built-In Templates

**1. Accountability: Unverified Payment**
- Priority: 10
- Min funding: $1M
- Headline: "Government announced $X for Y in Z, but {days} days later, still no verification of payment"

**2. Evidence: What Works**
- Priority: 9
- Headline: "Research shows {program_type} reduces youth crime by X%, but Queensland invests only $Y"

**3. Community Voice: Impact Story**
- Priority: 8
- Min funding: $500K
- Headline: "{Community} receives $X for {program}, but locals say {reality}"

**4. Verification: Payment Confirmed**
- Priority: 7
- Min funding: $1M
- Headline: "Exclusive: $X payment for {program} confirmed, {months} months after announcement"

### Adding Custom Templates

```sql
INSERT INTO story_templates (
    template_name,
    template_type,
    headline_pattern,
    required_data,
    ai_generation_prompt,
    priority,
    min_funding_amount
) VALUES (
    'Spending Comparison: Urban vs Remote',
    'analysis',
    'Urban communities receive ${X}M per capita, remote areas get ${Y}M - a ${Z}x difference',
    '{"geographic_data": true, "per_capita_spending": true}',
    'Compare per-capita youth justice spending between urban and remote communities. Calculate disparities and explain impact.',
    8,
    NULL
);
```

---

## 🔧 Maintenance

### Weekly Tasks

1. **Check processing queue**
```sql
SELECT * FROM v_processing_status;
```

2. **Retry failed jobs**
```sql
UPDATE processing_queue
SET status = 'pending', attempts = 0
WHERE status = 'failed' AND last_error NOT LIKE '%API key%';
```

3. **Review generated stories**
```sql
SELECT COUNT(*)
FROM generated_stories
WHERE publication_status = 'draft';
```

### Monthly Tasks

1. **Re-analyze old documents** (to check for verification updates)
```sql
UPDATE ai_analysis
SET created_at = NOW() - INTERVAL '35 days'
WHERE analysis_type = 'verification'
  AND created_at < NOW() - INTERVAL '30 days';
```

2. **Clean up processed queue items**
```sql
DELETE FROM processing_queue
WHERE status = 'complete'
  AND updated_at < NOW() - INTERVAL '30 days';
```

3. **Review story opportunities**
```sql
SELECT * FROM v_story_opportunities
ORDER BY priority DESC, total_funding DESC;
```

---

## 💡 Next Features to Build

1. **Auto-verification checker**
   - Scrape QTenders for contract awards
   - Match to funding announcements
   - Auto-update verification_status

2. **Email alerts**
   - When high-priority story is generated
   - When verification status changes
   - Weekly digest of new documents

3. **Public API**
   - Expose semantic search
   - Allow community to query data
   - Track API usage

4. **Dashboard**
   - Funding over time
   - Verification rates
   - Geographic distribution
   - Story pipeline status

5. **Integration with JusticeHub**
   - Auto-publish verified stories
   - Embed search widget
   - Show real-time data

---

## 📚 Resources

- **pgvector docs:** https://github.com/pgvector/pgvector
- **OpenAI embeddings:** https://platform.openai.com/docs/guides/embeddings
- **Supabase vector search:** https://supabase.com/docs/guides/ai
- **RAG patterns:** https://www.anthropic.com/index/retrieval-augmented-generation

---

**Last Updated:** 2025-11-15
**Version:** 1.0
**Status:** Ready for production with 59 documents loaded
