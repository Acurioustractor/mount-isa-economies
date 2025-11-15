# Mount Isa Economic Observatory - World-Class Architecture

**Vision**: A living, breathing economic intelligence platform that empowers communities to own their data, understand their economy, and build generational wealth through cultural intelligence.

---

## 🎯 Core Principles

1. **Community Ownership** - Data belongs to the community, not extractive systems
2. **Cultural Intelligence** - Economic value aligned with Kalkadoon values and cultural practices
3. **Always Current** - Automated pipelines ensure data is never stale
4. **LLM-Native** - Designed for AI-powered insights and conversation
5. **Transparent Funding** - Every dollar tracked, every opportunity visible
6. **Simple & Clear** - Accessible to community members, not just economists

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    COMMUNITY INTERFACE                       │
│  - Chat with economic data (LLM)                            │
│  - Funding opportunity alerts                               │
│  - Economic pattern dashboards                              │
│  - Community conversation overlay                           │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                  SUPABASE CORE (Postgres)                    │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Economic   │  │   Vector     │  │  Community   │     │
│  │     Data     │  │  Embeddings  │  │   Stories    │     │
│  │   (Tables)   │  │  (pgvector)  │  │  (Threads)   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
│                                                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐     │
│  │   Funding    │  │  Analytics   │  │   Metadata   │     │
│  │   Tracker    │  │   Tables     │  │  & Lineage   │     │
│  └──────────────┘  └──────────────┘  └──────────────┘     │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│              AUTOMATED DATA PIPELINES                        │
│  - Daily scraper runs (Supabase Edge Functions)             │
│  - Automatic embedding generation                           │
│  - Change detection & alerts                                │
│  - Data cleaning & enrichment                               │
└─────────────────────────────────────────────────────────────┘
                              ↕
┌─────────────────────────────────────────────────────────────┐
│                    DATA SOURCES                              │
│  QLD Contracts | ACNC | Grants | Parliament | Community     │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Database Schema Design

### Core Tables

#### 1. **organizations**
```sql
CREATE TABLE organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name TEXT NOT NULL,
  abn TEXT,
  entity_type TEXT, -- charity, business, government, community_org
  location GEOGRAPHY(POINT),
  postcode TEXT,

  -- Contact
  phone TEXT,
  email TEXT,
  website TEXT,

  -- Classification
  industry_codes TEXT[],
  service_types TEXT[],

  -- Community alignment
  indigenous_owned BOOLEAN,
  kalkadoon_connected BOOLEAN,
  community_priority INTEGER, -- 1-5 rating

  -- Data provenance
  source TEXT NOT NULL, -- 'acnc', 'abn_lookup', 'community_input'
  last_verified_at TIMESTAMPTZ,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_orgs_location ON organizations USING GIST(location);
CREATE INDEX idx_orgs_postcode ON organizations(postcode);
CREATE INDEX idx_orgs_abn ON organizations(abn);
```

#### 2. **financial_records**
```sql
CREATE TABLE financial_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID REFERENCES organizations(id),

  -- Period
  financial_year INTEGER,
  reporting_period DATERANGE,

  -- Financials
  revenue NUMERIC(15,2),
  expenses NUMERIC(15,2),
  assets NUMERIC(15,2),
  liabilities NUMERIC(15,2),
  net_position NUMERIC(15,2),

  -- Employment
  employees_fte NUMERIC(8,2),
  volunteers_count INTEGER,

  -- Breakdown (JSONB for flexibility)
  revenue_breakdown JSONB, -- {government_grants: 50000, services: 30000, etc}
  expense_breakdown JSONB,

  -- Source
  source TEXT NOT NULL, -- 'acnc_ais', 'annual_report', 'estimates'
  confidence_score NUMERIC(3,2), -- 0.00 to 1.00

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_financials_org ON financial_records(organization_id);
CREATE INDEX idx_financials_year ON financial_records(financial_year);
```

#### 3. **contracts**
```sql
CREATE TABLE contracts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Parties
  agency TEXT NOT NULL,
  supplier_name TEXT,
  supplier_abn TEXT,
  supplier_id UUID REFERENCES organizations(id), -- linked after enrichment

  -- Contract details
  contract_title TEXT,
  contract_description TEXT,
  contract_number TEXT,

  -- Financials
  value NUMERIC(15,2),
  value_min NUMERIC(15,2),
  value_max NUMERIC(15,2),

  -- Dates
  start_date DATE,
  end_date DATE,
  publish_date DATE,

  -- Classification
  category TEXT,
  procurement_method TEXT,

  -- Location relevance
  mount_isa_relevance BOOLEAN DEFAULT FALSE,
  relevance_keywords TEXT[], -- matched keywords

  -- Raw data
  raw_data JSONB,

  source TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_contracts_supplier ON contracts(supplier_abn);
CREATE INDEX idx_contracts_agency ON contracts(agency);
CREATE INDEX idx_contracts_value ON contracts(value);
CREATE INDEX idx_contracts_mi_relevance ON contracts(mount_isa_relevance);
```

#### 4. **grants**
```sql
CREATE TABLE grants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Grant details
  grant_id TEXT UNIQUE, -- external ID
  title TEXT NOT NULL,
  description TEXT,
  program_name TEXT,

  -- Agency
  funding_agency TEXT,
  administering_body TEXT,

  -- Financials
  amount NUMERIC(15,2),
  amount_min NUMERIC(15,2),
  amount_max NUMERIC(15,2),

  -- Recipient (if awarded)
  recipient_name TEXT,
  recipient_abn TEXT,
  recipient_id UUID REFERENCES organizations(id),

  -- Timing
  grant_type TEXT, -- 'opportunity', 'awarded', 'announced'
  open_date DATE,
  close_date DATE,
  award_date DATE,
  start_date DATE,
  end_date DATE,

  -- Eligibility
  eligible_entities TEXT[], -- ['nfp', 'business', 'indigenous', 'local_gov']
  eligible_locations TEXT[], -- postcodes or regions

  -- Status
  status TEXT, -- 'open', 'closed', 'awarded', 'completed'

  -- Categorization
  focus_areas TEXT[], -- 'economic_dev', 'indigenous', 'health', 'education'

  -- Relevance
  mount_isa_eligible BOOLEAN,
  mount_isa_awarded BOOLEAN,

  -- URLs
  application_url TEXT,
  guidelines_url TEXT,

  source TEXT NOT NULL,
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_grants_status ON grants(status);
CREATE INDEX idx_grants_close_date ON grants(close_date);
CREATE INDEX idx_grants_mi_eligible ON grants(mount_isa_eligible);
CREATE INDEX idx_grants_recipient ON grants(recipient_abn);
```

#### 5. **parliament_records**
```sql
CREATE TABLE parliament_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Record type
  record_type TEXT, -- 'hansard', 'budget_estimates', 'ministerial_statement', 'qa'

  -- Details
  title TEXT,
  speaker TEXT,
  speaker_role TEXT, -- 'minister', 'mp', 'committee_member'

  -- Content
  content TEXT,
  summary TEXT,

  -- References
  funding_mentioned NUMERIC(15,2)[], -- array of amounts mentioned
  programs_mentioned TEXT[],
  commitments TEXT[],

  -- Date
  record_date DATE,
  session_name TEXT,

  -- Links
  url TEXT,
  pdf_url TEXT,

  -- Extraction
  mount_isa_mentions INTEGER,
  keywords_matched TEXT[],

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_parliament_date ON parliament_records(record_date);
CREATE INDEX idx_parliament_type ON parliament_records(record_type);
```

#### 6. **community_conversations**
```sql
CREATE TABLE community_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Conversation
  participant_name TEXT, -- optional, can be anonymous
  participant_role TEXT, -- 'community_member', 'business_owner', 'elder', 'youth'

  -- Content
  conversation_text TEXT NOT NULL,
  themes TEXT[], -- auto-extracted or manual tags
  priorities TEXT[], -- what matters most
  concerns TEXT[],
  opportunities TEXT[],

  -- Context
  conversation_date DATE,
  conversation_type TEXT, -- 'interview', 'survey', 'workshop', 'casual'
  location TEXT,

  -- Connections to economic data
  related_organizations UUID[], -- array of organization IDs
  related_grants UUID[], -- grants mentioned
  related_contracts UUID[], -- contracts mentioned

  -- Privacy
  public BOOLEAN DEFAULT FALSE,
  consent_given BOOLEAN DEFAULT FALSE,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_conversations_date ON community_conversations(conversation_date);
CREATE INDEX idx_conversations_themes ON community_conversations USING GIN(themes);
```

---

## 🧠 Vector Embeddings for LLM Access

### Enable pgvector

```sql
CREATE EXTENSION IF NOT EXISTS vector;
```

### Document Embeddings Table

```sql
CREATE TABLE document_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Source reference
  source_table TEXT NOT NULL, -- 'contracts', 'grants', 'parliament_records', etc
  source_id UUID NOT NULL,

  -- Chunk information
  chunk_index INTEGER, -- for multi-chunk documents
  chunk_type TEXT, -- 'full_text', 'summary', 'financial_table', 'key_facts'

  -- Content
  content TEXT NOT NULL,

  -- Metadata (for filtering)
  metadata JSONB, -- {date_range, amount, agency, location, etc}

  -- Vector
  embedding VECTOR(1536), -- OpenAI ada-002 = 1536 dimensions

  -- Context preservation
  previous_chunk_id UUID REFERENCES document_embeddings(id),
  next_chunk_id UUID REFERENCES document_embeddings(id),

  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for fast similarity search
CREATE INDEX ON document_embeddings USING hnsw (embedding vector_cosine_ops);

-- Metadata index for filtered searches
CREATE INDEX idx_embeddings_metadata ON document_embeddings USING GIN(metadata);
CREATE INDEX idx_embeddings_source ON document_embeddings(source_table, source_id);
```

---

## 📝 Chunking Strategy for Economic Data

### 1. **Contract Documents**

**Approach**: Element-based chunking
- **Full contract**: One chunk with all details
- **Financial summary**: Separate chunk with just value, dates, parties
- **Description**: Standalone chunk for semantic search

```javascript
// Example chunk for contract
{
  content: "Contract: Road Maintenance Services\nSupplier: Mount Isa Road Services Pty Ltd\nValue: $450,000\nPeriod: 2023-2025\nDescription: Ongoing maintenance of urban roads in Mount Isa region...",
  metadata: {
    type: "contract",
    value: 450000,
    supplier_abn: "12345678901",
    agency: "QLD Transport",
    date_range: "[2023-01-01,2025-12-31)",
    location: "Mount Isa",
    indigenous_owned: true
  }
}
```

### 2. **Grant Opportunities**

**Approach**: Structured chunking with eligibility separation
- **Opportunity summary**: Title, amount, dates, agency
- **Eligibility criteria**: Separate chunk for matching
- **Application process**: Separate chunk

```javascript
{
  content: "GRANT OPPORTUNITY: Regional Business Development Fund\nAmount: $50,000 - $500,000\nClosing: 2025-06-30\nEligibility: Indigenous businesses, regional NFPs, community enterprises in North West Queensland\nFocus: Economic participation, job creation, cultural enterprises",
  metadata: {
    type: "grant_opportunity",
    status: "open",
    amount_range: [50000, 500000],
    close_date: "2025-06-30",
    eligible_locations: ["4825", "4823", "Mount Isa", "NW QLD"],
    eligible_entities: ["indigenous", "nfp", "business"],
    focus_areas: ["economic_dev", "indigenous", "jobs"]
  }
}
```

### 3. **Financial Records**

**Approach**: Table-aware chunking
- **Yearly summary**: Revenue, expenses, net in narrative form
- **Detailed breakdown**: Revenue sources, expense categories as structured text
- **Trends**: Multi-year comparison chunk

```javascript
{
  content: "Mount Isa Community Services 2023 Financials\nRevenue: $1.2M (↑15% from 2022)\n- Government grants: $800K (67%)\n- Service fees: $300K (25%)\n- Donations: $100K (8%)\nExpenses: $1.1M\n- Staff: $650K\n- Programs: $350K\n- Admin: $100K\nNet: +$100K\nEmployees: 12 FTE",
  metadata: {
    type: "financial_record",
    organization_id: "uuid...",
    organization_name: "Mount Isa Community Services",
    year: 2023,
    revenue: 1200000,
    expenses: 1100000,
    employees: 12,
    indigenous_owned: false
  }
}
```

### 4. **Parliament Records**

**Approach**: Semantic chunking by topic
- **Each funding announcement**: Separate chunk
- **Policy commitments**: Separate chunk
- **Q&A pairs**: Each question-answer as chunk

```javascript
{
  content: "Minister announced $5M for North West Queensland infrastructure upgrade in Budget Estimates 2024. Focus on Mount Isa water infrastructure and road safety improvements. Funding allocated over 3 years starting July 2024.",
  metadata: {
    type: "parliament_record",
    record_type: "budget_estimates",
    date: "2024-06-15",
    speaker: "Hon. Minister for Regional Development",
    funding_amount: 5000000,
    location: "Mount Isa",
    keywords: ["infrastructure", "water", "roads", "funding"]
  }
}
```

### 5. **Community Conversations**

**Approach**: Theme-based chunking
- **By topic**: Each distinct topic/concern as separate chunk
- **With context**: Include participant role and date

```javascript
{
  content: "Community elder shared: 'We need more local job opportunities that respect our cultural practices. The mining contracts go to big companies from Brisbane, not local businesses. Young people leave because there's no future here unless you work for the mine.'\nTheme: Local employment, cultural alignment, youth retention",
  metadata: {
    type: "community_conversation",
    date: "2024-11-01",
    participant_role: "elder",
    themes: ["employment", "cultural_practices", "youth", "local_business"],
    sentiment: "concerned",
    location: "Mount Isa"
  }
}
```

---

## 🔄 Automated Data Pipeline

### Supabase Edge Functions (Deno)

#### Daily Scraper Function

```typescript
// supabase/functions/daily-data-collection/index.ts

import { serve } from "https://deno.land/std@0.168.0/http/server.ts"
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

serve(async (req) => {
  const supabase = createClient(
    Deno.env.get('SUPABASE_URL'),
    Deno.env.get('SUPABASE_SERVICE_ROLE_KEY')
  )

  // 1. Run all scrapers
  const scrapers = [
    { name: 'contracts', url: 'https://data.qld.gov.au/api/3/action/...' },
    { name: 'grants', url: 'https://data.gov.au/api/3/action/...' },
    { name: 'acnc', url: 'https://data.gov.au/api/3/action/...' },
    { name: 'parliament', url: 'https://www.parliament.qld.gov.au/api/...' }
  ]

  const results = []

  for (const scraper of scrapers) {
    try {
      console.log(`Running ${scraper.name} scraper...`)

      // Fetch data
      const data = await fetchScraperData(scraper)

      // Store in appropriate table
      const inserted = await storeData(supabase, scraper.name, data)

      // Generate embeddings for new records
      await generateEmbeddings(supabase, scraper.name, inserted)

      results.push({ scraper: scraper.name, records: inserted.length, status: 'success' })

    } catch (error) {
      results.push({ scraper: scraper.name, error: error.message, status: 'failed' })
    }
  }

  // 2. Check for new grant opportunities
  const newGrants = await detectNewGrants(supabase)
  if (newGrants.length > 0) {
    await sendGrantAlerts(supabase, newGrants)
  }

  // 3. Update analytics tables
  await refreshAnalytics(supabase)

  return new Response(JSON.stringify({ success: true, results }), {
    headers: { 'Content-Type': 'application/json' }
  })
})

async function generateEmbeddings(supabase, tableName, records) {
  for (const record of records) {
    // Generate text chunk
    const chunk = createChunk(tableName, record)

    // Call OpenAI embeddings API
    const embedding = await fetch('https://api.openai.com/v1/embeddings', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${Deno.env.get('OPENAI_API_KEY')}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        input: chunk.content,
        model: 'text-embedding-3-small' // 1536 dimensions, cheaper than ada-002
      })
    }).then(r => r.json())

    // Store embedding
    await supabase.from('document_embeddings').insert({
      source_table: tableName,
      source_id: record.id,
      content: chunk.content,
      metadata: chunk.metadata,
      embedding: embedding.data[0].embedding
    })
  }
}
```

#### Grant Alert Function

```typescript
// supabase/functions/grant-alerts/index.ts

async function detectNewGrants(supabase) {
  // Find grants opened in last 24 hours
  const { data: newGrants } = await supabase
    .from('grants')
    .select('*')
    .eq('status', 'open')
    .eq('mount_isa_eligible', true)
    .gte('created_at', new Date(Date.now() - 24 * 60 * 60 * 1000).toISOString())

  return newGrants || []
}

async function sendGrantAlerts(supabase, grants) {
  for (const grant of grants) {
    // Find matching organizations
    const matches = await findEligibleOrgs(supabase, grant)

    for (const org of matches) {
      // Store alert
      await supabase.from('grant_alerts').insert({
        grant_id: grant.id,
        organization_id: org.id,
        match_score: org.match_score,
        match_reasons: org.match_reasons
      })

      // Send notification (email, SMS, etc)
      await sendNotification(org, grant)
    }
  }
}
```

### Scheduled Jobs (Supabase Cron)

```sql
-- Run daily at 2 AM AEST
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

-- Check for new grants every 4 hours
SELECT cron.schedule(
  'grant-monitoring',
  '0 */4 * * *', -- Every 4 hours
  $$
  SELECT net.http_post(
    url := 'https://your-project.supabase.co/functions/v1/grant-alerts',
    headers := jsonb_build_object('Authorization', 'Bearer ' || current_setting('app.service_role_key'))
  );
  $$
);
```

---

## 📈 Analytics & Pattern Detection

### Materialized Views for Fast Queries

```sql
-- Economic flow by organization
CREATE MATERIALIZED VIEW economic_flows AS
SELECT
  o.id,
  o.name,
  o.indigenous_owned,
  o.kalkadoon_connected,
  -- Money IN
  COALESCE(SUM(g.amount), 0) as total_grants_received,
  COALESCE(SUM(c.value), 0) as total_contracts_won,
  COALESCE(SUM(f.revenue), 0) as total_revenue,
  -- Money OUT
  COALESCE(SUM(f.expenses), 0) as total_expenses,
  -- Net position
  COALESCE(SUM(f.net_position), 0) as net_economic_position,
  -- Employment
  COALESCE(SUM(f.employees_fte), 0) as total_employees,
  -- Time
  MIN(COALESCE(g.award_date, c.start_date, f.reporting_period)) as first_activity,
  MAX(COALESCE(g.award_date, c.start_date, f.reporting_period)) as last_activity
FROM organizations o
LEFT JOIN grants g ON g.recipient_id = o.id
LEFT JOIN contracts c ON c.supplier_id = o.id
LEFT JOIN financial_records f ON f.organization_id = o.id
GROUP BY o.id, o.name, o.indigenous_owned, o.kalkadoon_connected;

-- Refresh daily
CREATE INDEX ON economic_flows(id);
SELECT cron.schedule('refresh-economic-flows', '0 3 * * *',
  'REFRESH MATERIALIZED VIEW economic_flows');
```

```sql
-- Funding trends over time
CREATE MATERIALIZED VIEW funding_trends AS
SELECT
  DATE_TRUNC('quarter', COALESCE(award_date, start_date)) as quarter,
  funding_agency,
  focus_areas,
  COUNT(*) as grant_count,
  SUM(amount) as total_funding,
  AVG(amount) as avg_grant_size,
  COUNT(*) FILTER (WHERE recipient_id IN
    (SELECT id FROM organizations WHERE indigenous_owned = true)) as indigenous_grants,
  SUM(amount) FILTER (WHERE recipient_id IN
    (SELECT id FROM organizations WHERE indigenous_owned = true)) as indigenous_funding
FROM grants
WHERE status = 'awarded'
  AND mount_isa_awarded = true
GROUP BY quarter, funding_agency, focus_areas
ORDER BY quarter DESC;
```

---

## 💬 LLM Integration for Community Conversations

### RAG Query Function

```typescript
// Semantic search across all economic data
async function queryEconomicData(question: string, filters: object = {}) {
  // 1. Generate embedding for question
  const questionEmbedding = await generateEmbedding(question)

  // 2. Semantic search in vector store
  const { data: similarChunks } = await supabase.rpc('match_documents', {
    query_embedding: questionEmbedding,
    match_threshold: 0.7,
    match_count: 20,
    filter_metadata: filters
  })

  // 3. Retrieve full context
  const context = similarChunks.map(chunk => ({
    content: chunk.content,
    source: chunk.metadata.type,
    ...chunk.metadata
  }))

  // 4. Call LLM with context
  const response = await callLLM({
    system: `You are an economic analyst helping the Mount Isa community understand their economy.
             Use the provided data to answer questions clearly and highlight opportunities.
             Always cite specific data sources (contracts, grants, etc).
             Frame insights in terms of community benefit and cultural values.`,
    context: context,
    question: question
  })

  return response
}

// Postgres function for similarity search
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding VECTOR(1536),
  match_threshold FLOAT,
  match_count INT,
  filter_metadata JSONB DEFAULT '{}'
)
RETURNS TABLE (
  id UUID,
  content TEXT,
  metadata JSONB,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    document_embeddings.id,
    document_embeddings.content,
    document_embeddings.metadata,
    1 - (document_embeddings.embedding <=> query_embedding) as similarity
  FROM document_embeddings
  WHERE 1 - (document_embeddings.embedding <=> query_embedding) > match_threshold
    AND (filter_metadata = '{}'::jsonb OR document_embeddings.metadata @> filter_metadata)
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;
```

### Example Queries

```javascript
// "Show me all funding opportunities for indigenous businesses"
await queryEconomicData(
  "What grant opportunities are available for indigenous businesses in Mount Isa?",
  {
    type: "grant_opportunity",
    status: "open",
    eligible_entities: ["indigenous"]
  }
)

// "Where does government money go in our community?"
await queryEconomicData(
  "Show me the flow of government contracts and grants in Mount Isa over the last 3 years"
)

// "What do community members say about local employment?"
await queryEconomicData(
  "What are community concerns about jobs and employment?",
  {
    type: "community_conversation",
    themes: ["employment"]
  }
)
```

---

## 🌱 Community Ownership Features

### 1. **Community Data Contribution**

```sql
-- Community members can add their perspectives
CREATE TABLE community_data_contributions (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  contributor_email TEXT, -- optional

  contribution_type TEXT, -- 'correction', 'addition', 'insight', 'opportunity'

  -- What they're contributing about
  related_table TEXT,
  related_id UUID,

  -- Their contribution
  contribution_text TEXT NOT NULL,
  supporting_evidence TEXT,

  -- Validation
  verified BOOLEAN DEFAULT FALSE,
  verified_by UUID,
  verified_at TIMESTAMPTZ,

  -- Impact
  incorporated BOOLEAN DEFAULT FALSE,
  impact_description TEXT,

  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 2. **Value Alignment Scoring**

```sql
-- Score economic activities by cultural values
CREATE TABLE cultural_value_scores (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- What's being scored
  entity_type TEXT, -- 'organization', 'contract', 'grant'
  entity_id UUID,

  -- Value dimensions (Kalkadoon-specific)
  land_connection_score INTEGER, -- 1-5
  community_benefit_score INTEGER,
  cultural_respect_score INTEGER,
  long_term_sustainability_score INTEGER,
  local_employment_score INTEGER,

  -- Overall
  total_value_score INTEGER,

  -- Who scored it
  scored_by TEXT, -- 'community', 'algorithm', 'expert'
  scorer_notes TEXT,

  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

### 3. **Opportunity Matching**

```sql
-- Match community members/orgs with opportunities
CREATE TABLE opportunity_matches (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  opportunity_type TEXT, -- 'grant', 'contract', 'partnership'
  opportunity_id UUID,

  matched_to_type TEXT, -- 'organization', 'individual'
  matched_to_id UUID,

  match_score NUMERIC(3,2), -- 0.00 to 1.00
  match_reasons JSONB, -- {eligible: true, relevant_experience: true, ...}

  -- Action
  status TEXT DEFAULT 'pending', -- 'pending', 'notified', 'interested', 'applied', 'declined'
  notified_at TIMESTAMPTZ,

  created_at TIMESTAMPTZ DEFAULT NOW()
);
```

---

## 🚀 Simple Implementation Plan

### Phase 1: Foundation (Week 1-2)
1. ✅ Set up Supabase project
2. ✅ Create core tables (organizations, contracts, grants, financials)
3. ✅ Enable pgvector extension
4. ✅ Migrate existing CSV data to Supabase

### Phase 2: Data Pipeline (Week 3-4)
1. ✅ Convert Python scrapers to Supabase Edge Functions
2. ✅ Set up daily cron jobs
3. ✅ Implement embedding generation pipeline
4. ✅ Create chunking functions for each data type

### Phase 3: LLM Interface (Week 5-6)
1. ✅ Build RAG query function
2. ✅ Create simple chat interface
3. ✅ Implement grant alert system
4. ✅ Add analytics materialized views

### Phase 4: Community Layer (Week 7-8)
1. ✅ Add community conversation table
2. ✅ Build contribution system
3. ✅ Implement cultural value scoring
4. ✅ Create opportunity matching

### Phase 5: Refinement (Week 9-10)
1. ✅ Data quality improvements
2. ✅ Performance optimization
3. ✅ Community testing and feedback
4. ✅ Documentation and training

---

## 💰 Cost Estimate

### Supabase (assuming Pro plan)
- Database: $25/month (includes 8GB database, 250GB bandwidth)
- Edge Functions: ~$10/month (for daily scrapers)
- Storage: ~$5/month (for CSV backups)

### OpenAI API
- Embeddings (text-embedding-3-small): ~$0.02 per 1M tokens
- Estimated: ~10,000 documents × 500 tokens = 5M tokens = $0.10 one-time
- Monthly updates: ~$1-2/month

### Total: ~$50/month for world-class economic intelligence platform

---

## 🎓 Next Steps

1. **Set up Supabase project** - Create account, new project
2. **Run schema migration** - Execute all CREATE TABLE statements
3. **Migrate existing data** - Upload current CSVs
4. **Deploy first Edge Function** - Start with contracts scraper
5. **Generate initial embeddings** - Process existing data
6. **Build simple chat interface** - Test RAG queries
7. **Community co-design session** - Validate with Kalkadoon representatives

---

## 📚 Resources

- Supabase Docs: https://supabase.com/docs
- pgvector Guide: https://supabase.com/docs/guides/database/extensions/pgvector
- LangChain Supabase: https://js.langchain.com/docs/integrations/vectorstores/supabase/
- OpenAI Embeddings: https://platform.openai.com/docs/guides/embeddings
- Indigenous Data Sovereignty: https://www.gida-global.org/

---

**Built for the Mount Isa community, by the community.**
**Economic data as a tool for self-determination, not extraction.**
