# Mount Isa Economies - Scraping & Data Processing Scripts

This directory contains the data collection and processing scripts for the Mount Isa Community Economic Observatory project.

## 📋 Overview

Based on your current data quality issues, we've implemented a comprehensive solution:

### Current Problems (from your stats):
- ❌ **94% of documents missing real dates** (53/56 using fallback)
- ❌ **70% missing funding amounts** (only 17/56 have amounts)
- ❌ **Only 4 documents for Mount Isa** (primary focus area)
- ❌ **No confidence tracking** on extracted data
- ❌ **No validation** of data quality

### Solutions Implemented:
- ✅ **Multi-strategy date extraction** with confidence scoring
- ✅ **Multi-strategy funding amount extraction** with confidence scoring
- ✅ **Comprehensive validation framework** to catch quality issues early
- ✅ **Enhanced database schema** with confidence scores and validation warnings
- ✅ **Mount Isa-specific scrapers** to increase coverage
- ✅ **Integrated example** showing how everything works together

---

## 🗂️ File Structure

```
scripts/
├── README.md                          # This file
├── date_extractor.py                  # Multi-strategy date extraction
├── funding_extractor.py               # Multi-strategy funding amount extraction
├── validators.py                      # Data validation framework
├── integrated_scraper_example.py      # Example showing integrated usage
├── mount_isa_scrapers.py             # Mount Isa-specific scrapers
├── database_schema.sql                # Enhanced PostgreSQL schema
└── cleanup_and_fix_data.py           # Your existing cleanup script (commit it!)
```

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
# Create virtual environment (if not already done)
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 2. Set Up Environment Variables

Create a `.env` file in the project root:

```bash
# Supabase credentials
SUPABASE_URL=your_supabase_url
SUPABASE_KEY=your_supabase_key

# Optional: AI API keys (for enhanced extraction)
ANTHROPIC_API_KEY=your_anthropic_key
OPENAI_API_KEY=your_openai_key
```

### 3. Update Database Schema

Apply the enhanced schema to your Supabase database:

```bash
# Copy the contents of database_schema.sql and run in Supabase SQL editor
# Or use psql:
psql -h your-supabase-host -U postgres -d postgres -f scripts/database_schema.sql
```

### 4. Test the Extractors

```bash
# Test date extraction
python scripts/date_extractor.py

# Test funding extraction
python scripts/funding_extractor.py

# Test validation
python scripts/validators.py
```

### 5. Run Integrated Scraper

```bash
# Run the example scraper
python scripts/integrated_scraper_example.py
```

### 6. Run Mount Isa-Specific Scrapers

```bash
# This will scrape Mount Isa City Council, Queensland grants, etc.
python scripts/mount_isa_scrapers.py
```

---

## 📊 How It Works

### Multi-Strategy Date Extraction

The `DateExtractor` tries multiple strategies in order of confidence:

1. **Metadata extraction** (95% confidence) - from document metadata fields
2. **HTML meta tags** (90% confidence) - `<meta property="article:published_time">`
3. **Text patterns** (70-85% confidence) - regex for various date formats
4. **Dateparser library** (60% confidence) - fallback for complex formats

```python
from date_extractor import extract_date

date, confidence, method = extract_date(
    text=document_text,
    html=html_content,
    metadata={'published_date': '2024-03-15'}
)

if confidence > 0.7:
    print(f"High confidence date: {date} (method: {method})")
```

### Multi-Strategy Funding Amount Extraction

The `FundingExtractor` tries multiple patterns:

1. **Structured fields** (95% confidence) - metadata with amount fields
2. **Labeled currency** (90% confidence) - "Funding: $1,234,567"
3. **Currency patterns** (75-85% confidence) - "$1.2M", "$1,200,000"
4. **Written amounts** (65% confidence) - "five hundred thousand dollars"
5. **Table extraction** (75% confidence) - amounts in HTML tables

```python
from funding_extractor import extract_funding_amount

amount, confidence, method = extract_funding_amount(
    text=document_text,
    html=html_content
)

if amount and confidence > 0.7:
    print(f"Found amount: ${amount:,.2f} (method: {method})")
```

### Validation Framework

The `DocumentValidator` checks for:

- ✅ Required fields present
- ✅ Dates are reasonable (not future, not too old)
- ✅ Funding amounts are in valid range
- ✅ Locations match known Queensland locations
- ✅ Confidence scores are 0-1
- ✅ Categorization fields use valid values
- ✅ Duplicate detection via checksums

```python
from validators import validate_document

warnings, needs_review = validate_document(document)

if needs_review:
    for warning in warnings:
        print(f"[{warning.severity}] {warning.field}: {warning.message}")
```

---

## 🎯 Addressing Your Specific Issues

### Issue 1: 94% Missing Real Dates

**Solution:** The `date_extractor.py` module uses 4 different strategies to find dates.

**Before:**
```python
# Your scraper was probably doing this:
date = datetime.now()  # Fallback to today
```

**After:**
```python
from date_extractor import extract_date

date, confidence, method = extract_date(text, html, metadata)
if confidence < 0.7:
    # Flag for manual review instead of using fallback
    document['needs_review'] = True
```

**Expected improvement:** 70-90% success rate on date extraction

---

### Issue 2: 70% Missing Funding Amounts

**Solution:** The `funding_extractor.py` module handles many formats:
- $1,234,567.89
- $2.5 million
- $50K - $100K (ranges)
- "valued at $500,000"

**Expected improvement:** 60-80% success rate on funding extraction

---

### Issue 3: Only 4 Documents for Mount Isa

**Solution:** The `mount_isa_scrapers.py` module includes:

1. **Mount Isa City Council scraper**
   - News and announcements
   - Budget documents
   - Procurement/tenders

2. **Queensland Grants scraper**
   - Search specifically for "Mount Isa" grants
   - Regional/remote community grants

3. **Regional Development scraper**
   - NW Queensland organizations
   - Chamber of Commerce

4. **AusTender scraper**
   - Filter by postcode 4825
   - Commonwealth contracts to Mount Isa

**Expected improvement:** 50-100+ documents for Mount Isa

---

### Issue 4: No Confidence Tracking

**Solution:** Every extraction now returns a confidence score:

```python
{
    'date': '2024-03-15',
    'date_confidence': 0.85,
    'date_extraction_method': 'html_meta.article:published_time',

    'funding_amount': 500000.00,
    'funding_confidence': 0.90,
    'funding_extraction_method': 'labeled_dollar_amount',

    'location': 'Mount Isa',
    'location_confidence': 0.95
}
```

**Benefits:**
- Filter to high-quality data only
- Identify documents needing manual review
- Track extraction method success rates

---

### Issue 5: No Validation

**Solution:** Every document now goes through validation:

```python
validation_warnings: [
    {
        'severity': 'warning',
        'field': 'date',
        'message': 'Date is exactly today - may be fallback default'
    },
    {
        'severity': 'info',
        'field': 'funding_amount',
        'message': 'Amount is round number ($500,000) - may be estimate'
    }
]
```

**Benefits:**
- Catch errors before they enter database
- Flag suspicious data
- Track data quality metrics

---

## 📈 Database Improvements

### New Fields

The enhanced schema adds:

```sql
-- Confidence scores
date_confidence          NUMERIC(3,2)
funding_confidence       NUMERIC(3,2)
location_confidence      NUMERIC(3,2)

-- Extraction methods
date_extraction_method   TEXT
funding_extraction_method TEXT

-- Quality tracking
needs_review             BOOLEAN
validation_warnings      JSONB
checksum                 TEXT  -- for duplicate detection
```

### New Views

```sql
-- Documents needing review (low confidence or warnings)
SELECT * FROM documents_needing_review;

-- High-quality documents only (confidence >= 0.8)
SELECT * FROM documents_high_quality;

-- Statistics
SELECT * FROM document_statistics;
SELECT * FROM location_statistics;
```

---

## 🔧 How to Integrate with Your Existing Code

If you already have scraping code in `cleanup_and_fix_data.py`, here's how to integrate:

```python
# In your existing scraper
from date_extractor import extract_date
from funding_extractor import extract_funding_amount
from validators import validate_document

def process_document(url, content, html):
    # Extract date (instead of using fallback)
    date, date_conf, date_method = extract_date(content, html)

    # Extract funding amount
    amount, amount_conf, amount_method = extract_funding_amount(content, html)

    # Build document
    document = {
        'title': extract_title(html),
        'url': url,
        'content': content,
        'date': date,
        'date_confidence': date_conf,
        'date_extraction_method': date_method,
        'funding_amount': amount,
        'funding_confidence': amount_conf,
        'funding_extraction_method': amount_method,
        # ... other fields
    }

    # Validate before saving
    warnings, needs_review = validate_document(document)

    # Save to database
    if needs_review:
        print(f"⚠️  Document needs review: {len(warnings)} warnings")

    return document
```

---

## 📊 Expected Results

After implementing these improvements, you should see:

### Before (Current State):
```
Total documents: 56
With funding amounts: 17 (30%)
Unique dates: 4
Documents with today's date: 53 (94%)
Mount Isa documents: 4
```

### After (Expected):
```
Total documents: 150+
With funding amounts: 100+ (65%+)
Unique dates: 80+
Documents with today's date: 5-10 (5-7%)
Mount Isa documents: 50+

Average confidence scores:
  Date: 0.82
  Funding: 0.79
  Location: 0.88

Documents needing review: 15-20 (10-15%)
```

---

## 🚦 Next Steps

1. **Commit your existing scripts** so we can see what you're currently doing
2. **Run the test scrapers** to validate the approach works for your sources
3. **Update database schema** in Supabase
4. **Integrate extractors** into your existing scraping code
5. **Run Mount Isa scrapers** to increase coverage
6. **Review low-confidence documents** manually to improve extractors
7. **Add AI/LLM extraction** for the most difficult cases

---

## 🤝 Contributing

When adding new scrapers:

1. Inherit from `IntegratedScraper`
2. Set a unique `source_system` identifier
3. Use the extraction and validation modules
4. Be respectful of rate limits (add `time.sleep()`)
5. Handle errors gracefully

---

## 📚 Resources

- [Queensland Open Data Portal](https://www.data.qld.gov.au/)
- [AusTender API Documentation](https://www.tenders.gov.au/?event=public.api.show)
- [ABS ASGS 2021](https://www.abs.gov.au/statistics/standards/australian-statistical-geography-standard-asgs-edition-3/jul2021-jun2026)
- [Mount Isa City Council](https://www.mountisa.qld.gov.au/)

---

## ❓ Questions?

If you run into issues:

1. Check the validation warnings in the database
2. Review the extraction confidence scores
3. Look at the `extraction_method` fields to see what's working
4. Run the test scripts to verify extractors work
5. Share your `cleanup_and_fix_data.py` for specific integration help

---

**Built for the Mount Isa Community Economic Observatory**
*Measuring local economic flows, identifying leakages, enabling import replacement*
