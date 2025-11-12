# Mount Isa Economic Observatory

**A world-class economic intelligence platform for community ownership and self-determination**

Built to support the Mount Isa and Kalkadoon community in understanding economic flows, accessing funding opportunities, and building generational wealth through cultural intelligence.

---

## 🎯 What This Does

- **📊 Tracks all economic data**: Government contracts, grants, charity financials, parliament announcements
- **🤖 LLM-powered insights**: Chat with your data, ask economic questions, get instant answers
- **🔔 Automated alerts**: Get notified when new grants open that match your eligibility
- **📈 Pattern detection**: Identify funding trends, economic gaps, and opportunities
- **💬 Community voices**: Overlay quantitative data with community conversations and priorities
- **🌱 Always updating**: Automated scrapers run daily to keep data current

---

## 🏗️ Architecture

**Database**: Supabase (PostgreSQL + pgvector)
- All economic data stored in structured tables
- Vector embeddings for semantic search
- Real-time updates via Edge Functions

**Data Sources**:
- Queensland Government contracts (530,960+ records)
- ACNC charity financial data
- Government grants (data.gov.au + ARC)
- Parliament/Hansard records
- Community conversations

**LLM Integration**:
- OpenAI embeddings (text-embedding-3-small)
- RAG (Retrieval Augmented Generation)
- Semantic search across all economic data

**Cost**: ~$50/month (Supabase Pro + OpenAI API)

---

## 📚 Documentation

- **[SUPABASE_ECONOMIC_OBSERVATORY_ARCHITECTURE.md](SUPABASE_ECONOMIC_OBSERVATORY_ARCHITECTURE.md)** - Complete technical architecture
- **[QUICK_START_GUIDE.md](QUICK_START_GUIDE.md)** - Get running in 1 hour
- **[DATA_SOURCES_COMPREHENSIVE.md](mount-isa-observatory/DATA_SOURCES_COMPREHENSIVE.md)** - All 15 data sources identified
- **[SCRAPER_FIXES.md](mount-isa-observatory/SCRAPER_FIXES.md)** - Documentation of fixed scrapers

---

## 🚀 Quick Start

### 1. Set Up Supabase (5 min)

```bash
# Create project at https://supabase.com
# Copy your project URL and keys

export SUPABASE_URL="https://your-project.supabase.co"
export SUPABASE_SERVICE_ROLE_KEY="your-service-role-key"
export OPENAI_API_KEY="your-openai-key"
```

### 2. Create Database Schema (2 min)

```bash
# In Supabase dashboard → SQL Editor
# Run: mount-isa-observatory/supabase/migrations/001_initial_schema.sql
```

### 3. Migrate Your Data (10 min)

```bash
cd mount-isa-observatory
pip install supabase openai pandas tqdm
python3 scripts/migrate_to_supabase.py
```

### 4. Generate Embeddings (10 min)

```bash
python3 scripts/generate_embeddings.py
```

### 5. Chat With Your Data!

```bash
python3 scripts/chat_with_data.py
```

Try questions like:
- "What grant opportunities are open for indigenous businesses?"
- "Show me government contracts in Mount Isa over $100,000"
- "Which organizations received the most funding last year?"

---

## 📁 Project Structure

```
mount-isa-economies/
├── mount-isa-observatory/
│   ├── supabase/
│   │   ├── migrations/        # Database schema
│   │   └── functions/         # Edge Functions (auto-scrapers)
│   ├── scripts/
│   │   ├── migrate_to_supabase.py     # Upload CSV data
│   │   ├── generate_embeddings.py     # Create vector embeddings
│   │   └── chat_with_data.py          # LLM chat interface
│   ├── scrapers/              # Data collection scripts
│   │   ├── qld_contracts_scraper.py
│   │   ├── acnc_financial_data.py
│   │   ├── grantconnect_api.py
│   │   ├── qld_parliament_scraper.py
│   │   └── qld_all_departments_scraper.py
│   ├── analysis/
│   │   └── analyze_contracts.py       # Find Mount Isa contracts
│   ├── dashboard/             # Web dashboard (coming soon)
│   └── data/                  # CSV data cache
├── SUPABASE_ECONOMIC_OBSERVATORY_ARCHITECTURE.md
├── QUICK_START_GUIDE.md
└── README.md
```

---

## 🎓 Key Features

### 1. **Comprehensive Data Collection**

All scrapers use the proven CKAN API pattern:
```python
CKAN_URL = "https://data.gov.au/api/3/action"
response = requests.get(f"{CKAN_URL}/package_search", params={'q': 'Mount Isa'})
```

**Data collected**:
- ✅ 530,960 QLD government contracts
- ✅ ACNC charity financials (revenue, expenses, staff)
- ✅ Government grants (opportunities + awarded)
- ✅ Parliament funding announcements
- ✅ Department datasets (health, education, transport)

### 2. **LLM-Powered Insights**

Every piece of data is:
- Chunked intelligently (structure-aware for financial data)
- Embedded using OpenAI (1536 dimensions)
- Stored in pgvector for fast similarity search
- Retrievable via natural language queries

### 3. **Community Ownership**

- **Data sovereignty**: Community controls their data
- **Cultural values**: Economic activities scored by cultural alignment
- **Community input**: Add conversations, corrections, insights
- **Transparent**: All funding sources and flows visible

### 4. **Automated Updates**

Supabase Edge Functions run daily:
- Scrape new contracts, grants, parliament records
- Generate embeddings for new data
- Detect new grant opportunities
- Send alerts to eligible organizations
- Refresh analytics

---

## 💡 Use Cases

### For Community Members
- "What grants can I apply for?"
- "Which local businesses are indigenous-owned?"
- "How much government money comes to Mount Isa?"

### For Organizations
- Automatic grant opportunity matching
- Track competitor funding
- Identify partnership opportunities
- Understand economic trends

### For Community Leaders
- Evidence-based advocacy
- Identify funding gaps
- Track government commitments
- Measure economic participation

### For Researchers
- Economic flow analysis
- Cultural economy metrics
- Policy impact assessment
- Community wellbeing indicators

---

## 🌱 Roadmap

### Phase 1: Foundation ✅
- ✅ Database schema
- ✅ Data migration scripts
- ✅ Vector embeddings
- ✅ Chat interface

### Phase 2: Automation (Current)
- ⏳ Deploy Edge Functions
- ⏳ Set up cron jobs
- ⏳ Grant alert system
- ⏳ Analytics dashboards

### Phase 3: Community Features
- ⏳ Public dashboard
- ⏳ Community contribution forms
- ⏳ Cultural value scoring
- ⏳ Opportunity matching

### Phase 4: Advanced Analytics
- ⏳ Economic pattern detection
- ⏳ Funding prediction
- ⏳ Impact measurement
- ⏳ Network analysis

---

## 🤝 Contributing

This project is built FOR the Mount Isa and Kalkadoon community.

**Community input needed**:
- Cultural value dimensions for scoring
- Priority data sources
- Dashboard features
- Community conversation themes

**Technical contributions**:
- Additional scrapers
- Analytics algorithms
- Dashboard components
- Documentation

---

## 📊 Data Sources

### Tier 1: Critical (Implemented)
- ✅ ACNC Charity Register
- ✅ QLD Government Contracts
- ✅ Government Grants (data.gov.au + ARC)
- ✅ Parliament Records

### Tier 2: High Value (In Progress)
- ⏳ ABN Lookup (waiting on GUID)
- ⏳ All QLD Departments via CKAN
- ⏳ Web enrichment of services

### Tier 3: Nice to Have
- Indigenous Business Australia (IBA)
- Regional Development Australia (RDA)
- Local council data

See [DATA_SOURCES_COMPREHENSIVE.md](mount-isa-observatory/DATA_SOURCES_COMPREHENSIVE.md) for full details.

---

## 🛠️ Technical Stack

- **Database**: Supabase (PostgreSQL 15 + PostGIS + pgvector)
- **Backend**: Supabase Edge Functions (Deno/TypeScript)
- **Embeddings**: OpenAI text-embedding-3-small (1536d, $0.02/1M tokens)
- **LLM**: GPT-4 Turbo (via OpenAI API)
- **Scrapers**: Python 3.11+ (requests, pandas, BeautifulSoup)
- **Frontend**: React + Vite + Leaflet (coming soon)

---

## 📝 License

This project is built for community benefit. Data sources retain their original licenses. Code is open for community use.

---

## 🙏 Acknowledgments

Built in collaboration with:
- Kalkadoon community members
- Mount Isa service providers
- Queensland Government (open data)
- ACNC (charity data)

**For questions or to get involved**: Contact via GitHub issues or community sessions.

---

**Economic data as a tool for self-determination, not extraction.**

**Building generational wealth through cultural intelligence.**
