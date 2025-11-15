-- Mount Isa Economic Observatory - Initial Database Schema
-- Run this in Supabase SQL Editor to set up all tables

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS postgis;
CREATE EXTENSION IF NOT EXISTS vector;
CREATE EXTENSION IF NOT EXISTS pg_cron;

-- ============================================================================
-- CORE TABLES
-- ============================================================================

-- Organizations: Charities, businesses, government agencies, community orgs
CREATE TABLE IF NOT EXISTS organizations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Basic info
  name TEXT NOT NULL,
  abn TEXT,
  acn TEXT,
  entity_type TEXT, -- 'charity', 'business', 'government', 'community_org'

  -- Location
  location GEOGRAPHY(POINT),
  address TEXT,
  suburb TEXT,
  postcode TEXT,
  state TEXT DEFAULT 'QLD',

  -- Contact
  phone TEXT,
  email TEXT,
  website TEXT,

  -- Classification
  industry_codes TEXT[],
  service_types TEXT[],

  -- Community alignment
  indigenous_owned BOOLEAN DEFAULT FALSE,
  kalkadoon_connected BOOLEAN DEFAULT FALSE,
  community_priority INTEGER CHECK (community_priority BETWEEN 1 AND 5),

  -- Data provenance
  source TEXT NOT NULL,
  source_id TEXT, -- ID in source system
  confidence_score NUMERIC(3,2) DEFAULT 1.00,
  last_verified_at TIMESTAMPTZ,

  -- Metadata
  raw_data JSONB,
  notes TEXT,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for organizations
CREATE INDEX IF NOT EXISTS idx_orgs_location ON organizations USING GIST(location);
CREATE INDEX IF NOT EXISTS idx_orgs_postcode ON organizations(postcode);
CREATE INDEX IF NOT EXISTS idx_orgs_abn ON organizations(abn);
CREATE INDEX IF NOT EXISTS idx_orgs_indigenous ON organizations(indigenous_owned);
CREATE INDEX IF NOT EXISTS idx_orgs_source ON organizations(source, source_id);

-- Financial records
CREATE TABLE IF NOT EXISTS financial_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID REFERENCES organizations(id) ON DELETE CASCADE,

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
  revenue_breakdown JSONB, -- {government_grants: 50000, services: 30000, ...}
  expense_breakdown JSONB,

  -- Source
  source TEXT NOT NULL,
  source_file TEXT,
  confidence_score NUMERIC(3,2) DEFAULT 1.00,

  -- Metadata
  raw_data JSONB,
  notes TEXT,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_financials_org ON financial_records(organization_id);
CREATE INDEX IF NOT EXISTS idx_financials_year ON financial_records(financial_year);
CREATE INDEX IF NOT EXISTS idx_financials_period ON financial_records USING GIST(reporting_period);

-- Contracts
CREATE TABLE IF NOT EXISTS contracts (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Parties
  agency TEXT NOT NULL,
  agency_abn TEXT,
  supplier_name TEXT,
  supplier_abn TEXT,
  supplier_id UUID REFERENCES organizations(id),

  -- Contract details
  contract_title TEXT,
  contract_description TEXT,
  contract_number TEXT,
  contract_type TEXT,

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
  standing_offer BOOLEAN,

  -- Location relevance
  mount_isa_relevance BOOLEAN DEFAULT FALSE,
  relevance_keywords TEXT[],
  relevance_score NUMERIC(3,2),

  -- Source
  source TEXT NOT NULL,
  source_file TEXT,
  source_url TEXT,

  -- Metadata
  raw_data JSONB,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_contracts_supplier_abn ON contracts(supplier_abn);
CREATE INDEX IF NOT EXISTS idx_contracts_supplier_id ON contracts(supplier_id);
CREATE INDEX IF NOT EXISTS idx_contracts_agency ON contracts(agency);
CREATE INDEX IF NOT EXISTS idx_contracts_value ON contracts(value DESC);
CREATE INDEX IF NOT EXISTS idx_contracts_dates ON contracts(start_date, end_date);
CREATE INDEX IF NOT EXISTS idx_contracts_mi_relevance ON contracts(mount_isa_relevance) WHERE mount_isa_relevance = true;

-- Grants
CREATE TABLE IF NOT EXISTS grants (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Grant details
  grant_id TEXT UNIQUE,
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
  eligible_activities TEXT[],

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
  source_url TEXT,

  -- Source
  source TEXT NOT NULL,

  -- Metadata
  raw_data JSONB,

  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_grants_status ON grants(status);
CREATE INDEX IF NOT EXISTS idx_grants_close_date ON grants(close_date);
CREATE INDEX IF NOT EXISTS idx_grants_mi_eligible ON grants(mount_isa_eligible) WHERE mount_isa_eligible = true;
CREATE INDEX IF NOT EXISTS idx_grants_recipient ON grants(recipient_abn);
CREATE INDEX IF NOT EXISTS idx_grants_recipient_id ON grants(recipient_id);
CREATE INDEX IF NOT EXISTS idx_grants_focus ON grants USING GIN(focus_areas);

-- Parliament records
CREATE TABLE IF NOT EXISTS parliament_records (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Record type
  record_type TEXT, -- 'hansard', 'budget_estimates', 'ministerial_statement', 'qa'

  -- Details
  title TEXT,
  speaker TEXT,
  speaker_role TEXT,

  -- Content
  content TEXT,
  summary TEXT,

  -- References
  funding_mentioned NUMERIC(15,2)[],
  programs_mentioned TEXT[],
  commitments TEXT[],

  -- Date
  record_date DATE,
  session_name TEXT,
  parliament_type TEXT, -- 'state', 'federal'

  -- Links
  url TEXT,
  pdf_url TEXT,

  -- Extraction
  mount_isa_mentions INTEGER DEFAULT 0,
  keywords_matched TEXT[],

  -- Source
  source TEXT NOT NULL,

  -- Metadata
  raw_data JSONB,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_parliament_date ON parliament_records(record_date DESC);
CREATE INDEX IF NOT EXISTS idx_parliament_type ON parliament_records(record_type);
CREATE INDEX IF NOT EXISTS idx_parliament_mi ON parliament_records(mount_isa_mentions) WHERE mount_isa_mentions > 0;

-- Community conversations
CREATE TABLE IF NOT EXISTS community_conversations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Participant
  participant_name TEXT,
  participant_role TEXT, -- 'community_member', 'business_owner', 'elder', 'youth', 'service_provider'
  participant_organization TEXT,

  -- Content
  conversation_text TEXT NOT NULL,
  themes TEXT[],
  priorities TEXT[],
  concerns TEXT[],
  opportunities TEXT[],

  -- Context
  conversation_date DATE,
  conversation_type TEXT, -- 'interview', 'survey', 'workshop', 'casual', 'feedback'
  location TEXT,

  -- Connections to economic data
  related_organizations UUID[],
  related_grants UUID[],
  related_contracts UUID[],

  -- Privacy
  public BOOLEAN DEFAULT FALSE,
  consent_given BOOLEAN DEFAULT FALSE,
  anonymous BOOLEAN DEFAULT FALSE,

  -- Analysis
  sentiment TEXT, -- 'positive', 'neutral', 'concerned', 'urgent'

  -- Metadata
  notes TEXT,

  created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_date ON community_conversations(conversation_date DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_themes ON community_conversations USING GIN(themes);
CREATE INDEX IF NOT EXISTS idx_conversations_public ON community_conversations(public) WHERE public = true;

-- ============================================================================
-- VECTOR EMBEDDINGS FOR LLM ACCESS
-- ============================================================================

CREATE TABLE IF NOT EXISTS document_embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

  -- Source reference
  source_table TEXT NOT NULL,
  source_id UUID NOT NULL,

  -- Chunk information
  chunk_index INTEGER DEFAULT 0,
  chunk_type TEXT, -- 'full_text', 'summary', 'financial_table', 'key_facts'
  total_chunks INTEGER DEFAULT 1,

  -- Content
  content TEXT NOT NULL,

  -- Metadata (for filtering)
  metadata JSONB,

  -- Vector
  embedding VECTOR(1536), -- OpenAI text-embedding-3-small

  -- Context preservation
  previous_chunk_id UUID REFERENCES document_embeddings(id),
  next_chunk_id UUID REFERENCES document_embeddings(id),

  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- HNSW index for fast similarity search
CREATE INDEX IF NOT EXISTS idx_embeddings_hnsw ON document_embeddings
USING hnsw (embedding vector_cosine_ops);

-- Metadata index for filtered searches
CREATE INDEX IF NOT EXISTS idx_embeddings_metadata ON document_embeddings USING GIN(metadata);
CREATE INDEX IF NOT EXISTS idx_embeddings_source ON document_embeddings(source_table, source_id);

-- ============================================================================
-- ANALYTICS & DERIVED DATA
-- ============================================================================

-- Economic flows materialized view
CREATE MATERIALIZED VIEW IF NOT EXISTS economic_flows AS
SELECT
  o.id,
  o.name,
  o.entity_type,
  o.indigenous_owned,
  o.kalkadoon_connected,
  o.postcode,

  -- Money IN
  COALESCE(SUM(DISTINCT g.amount), 0) as total_grants_received,
  COUNT(DISTINCT g.id) FILTER (WHERE g.status = 'awarded') as grants_count,
  COALESCE(SUM(DISTINCT c.value), 0) as total_contracts_won,
  COUNT(DISTINCT c.id) as contracts_count,
  COALESCE(MAX(f.revenue), 0) as latest_revenue,

  -- Money OUT
  COALESCE(MAX(f.expenses), 0) as latest_expenses,

  -- Net position
  COALESCE(MAX(f.net_position), 0) as latest_net_position,

  -- Employment
  COALESCE(MAX(f.employees_fte), 0) as latest_employees,
  COALESCE(MAX(f.volunteers_count), 0) as latest_volunteers,

  -- Time
  MIN(LEAST(
    COALESCE(g.award_date, '9999-12-31'::date),
    COALESCE(c.start_date, '9999-12-31'::date),
    COALESCE(lower(f.reporting_period), '9999-12-31'::date)
  )) as first_activity,
  MAX(GREATEST(
    COALESCE(g.award_date, '1900-01-01'::date),
    COALESCE(c.end_date, '1900-01-01'::date),
    COALESCE(upper(f.reporting_period), '1900-01-01'::date)
  )) as last_activity

FROM organizations o
LEFT JOIN grants g ON g.recipient_id = o.id
LEFT JOIN contracts c ON c.supplier_id = o.id
LEFT JOIN financial_records f ON f.organization_id = o.id
GROUP BY o.id, o.name, o.entity_type, o.indigenous_owned, o.kalkadoon_connected, o.postcode;

CREATE UNIQUE INDEX IF NOT EXISTS idx_economic_flows_id ON economic_flows(id);

-- Funding trends over time
CREATE MATERIALIZED VIEW IF NOT EXISTS funding_trends AS
SELECT
  DATE_TRUNC('quarter', COALESCE(award_date, start_date)) as quarter,
  funding_agency,
  UNNEST(focus_areas) as focus_area,
  COUNT(*) as grant_count,
  SUM(amount) as total_funding,
  AVG(amount) as avg_grant_size,
  COUNT(*) FILTER (WHERE recipient_id IN
    (SELECT id FROM organizations WHERE indigenous_owned = true)) as indigenous_grants,
  SUM(amount) FILTER (WHERE recipient_id IN
    (SELECT id FROM organizations WHERE indigenous_owned = true)) as indigenous_funding
FROM grants
WHERE status = 'awarded'
  AND amount IS NOT NULL
GROUP BY quarter, funding_agency, focus_area
ORDER BY quarter DESC;

CREATE INDEX IF NOT EXISTS idx_funding_trends_quarter ON funding_trends(quarter DESC);

-- ============================================================================
-- HELPER FUNCTIONS
-- ============================================================================

-- Vector similarity search function
CREATE OR REPLACE FUNCTION match_documents(
  query_embedding VECTOR(1536),
  match_threshold FLOAT DEFAULT 0.7,
  match_count INT DEFAULT 10,
  filter_metadata JSONB DEFAULT '{}'::jsonb
)
RETURNS TABLE (
  id UUID,
  source_table TEXT,
  source_id UUID,
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
    document_embeddings.source_table,
    document_embeddings.source_id,
    document_embeddings.content,
    document_embeddings.metadata,
    1 - (document_embeddings.embedding <=> query_embedding) as similarity
  FROM document_embeddings
  WHERE 1 - (document_embeddings.embedding <=> query_embedding) > match_threshold
    AND (filter_metadata = '{}'::jsonb OR document_embeddings.metadata @> filter_metadata)
  ORDER BY document_embeddings.embedding <=> query_embedding
  LIMIT match_count;
END;
$$;

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = NOW();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to tables
CREATE TRIGGER update_organizations_updated_at BEFORE UPDATE ON organizations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_financial_records_updated_at BEFORE UPDATE ON financial_records
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_contracts_updated_at BEFORE UPDATE ON contracts
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_grants_updated_at BEFORE UPDATE ON grants
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on tables
ALTER TABLE organizations ENABLE ROW LEVEL SECURITY;
ALTER TABLE financial_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE contracts ENABLE ROW LEVEL SECURITY;
ALTER TABLE grants ENABLE ROW LEVEL SECURITY;
ALTER TABLE parliament_records ENABLE ROW LEVEL SECURITY;
ALTER TABLE community_conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE document_embeddings ENABLE ROW LEVEL SECURITY;

-- Public read access to most tables (adjust as needed)
CREATE POLICY "Public read access" ON organizations FOR SELECT USING (true);
CREATE POLICY "Public read access" ON financial_records FOR SELECT USING (true);
CREATE POLICY "Public read access" ON contracts FOR SELECT USING (true);
CREATE POLICY "Public read access" ON grants FOR SELECT USING (true);
CREATE POLICY "Public read access" ON parliament_records FOR SELECT USING (true);
CREATE POLICY "Public read access" ON document_embeddings FOR SELECT USING (true);

-- Only public community conversations visible
CREATE POLICY "Public community conversations" ON community_conversations
  FOR SELECT USING (public = true);

-- ============================================================================
-- REFRESH SCHEDULES (using pg_cron)
-- ============================================================================

-- Refresh economic flows daily at 3 AM
SELECT cron.schedule(
  'refresh-economic-flows',
  '0 3 * * *',
  $$REFRESH MATERIALIZED VIEW CONCURRENTLY economic_flows$$
);

-- Refresh funding trends daily at 3:30 AM
SELECT cron.schedule(
  'refresh-funding-trends',
  '30 3 * * *',
  $$REFRESH MATERIALIZED VIEW CONCURRENTLY funding_trends$$
);

-- ============================================================================
-- INITIAL DATA VALIDATION
-- ============================================================================

-- Check tables created successfully
DO $$
DECLARE
  table_count INTEGER;
BEGIN
  SELECT COUNT(*) INTO table_count
  FROM information_schema.tables
  WHERE table_schema = 'public'
    AND table_name IN (
      'organizations',
      'financial_records',
      'contracts',
      'grants',
      'parliament_records',
      'community_conversations',
      'document_embeddings'
    );

  RAISE NOTICE 'Created % core tables', table_count;

  IF table_count < 7 THEN
    RAISE EXCEPTION 'Not all tables created successfully';
  END IF;
END $$;

-- Success message
DO $$
BEGIN
  RAISE NOTICE '
================================================================================
✅ MOUNT ISA ECONOMIC OBSERVATORY - DATABASE SETUP COMPLETE
================================================================================

Core Tables Created:
  • organizations
  • financial_records
  • contracts
  • grants
  • parliament_records
  • community_conversations
  • document_embeddings

Analytics Views:
  • economic_flows
  • funding_trends

Extensions Enabled:
  • postgis (for location data)
  • pgvector (for LLM embeddings)
  • pg_cron (for scheduled jobs)

Next Steps:
  1. Upload your CSV data using migration script
  2. Generate embeddings for LLM access
  3. Deploy Edge Functions for automated scrapers
  4. Set up dashboard

See QUICK_START_GUIDE.md for detailed instructions.
================================================================================
';
END $$;
