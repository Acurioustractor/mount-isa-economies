# Mount Isa Money Flows - Data Collection Status

**Last Updated**: 2025-11-14

## Summary

✅ **Comprehensive scraping framework operational** - collecting from 6 of 8 data sources
⚠️ **Media statements blocked** - Queensland Gov now returns 403 Forbidden
📄 **PDF parsing needed** - most sources identified but require extraction

---

## Data Collected: 15 Records

### By Source
| Source | Records | Status |
|--------|---------|--------|
| Federal Grants (GrantConnect) | 5 | ✅ URLs identified, need HTML scraping |
| Council Budget | 3 | ✅ URLs identified, need PDF parsing |
| Parliament | 2 | ✅ Estimates hearing + QoN identified |
| Budget Papers | 2 | ✅ PDFs identified, need OCR/parsing |
| Annual Reports | 2 | ✅ PDFs identified, need OCR/parsing |
| ACNC Charities | 1 | ✅ Mithangkaya Nguli identified |
| **Media Statements** | 0 | ❌ **Blocked (403 Forbidden)** |
| Audit Office | 0 | ⏳ Not yet implemented |

### By Record Type
| Type | Count |
|------|-------|
| Council documents | 3 |
| Federal grants | 3 |
| Budget allocations | 2 |
| Reports | 2 |
| Federal programs | 2 |
| Actual payments | 1 |
| Parliamentary question | 1 |
| Estimates hearing | 1 |

---

## Key Findings

### 1. Mount Isa City Council Budget: $110.9M
- **Source**: https://www.mountisa.qld.gov.au/City-Council/Corporate-Publications/Budgets/Budget-2024-25
- **Year**: 2024-25
- **Status**: Total budget amount captured, breakdown needed

### 2. Mithangkaya Nguli Identified
- **Source**: ACNC Registry
- **URL**: https://www.acnc.gov.au/charity/charities/02061bf8-38af-e811-a963-000d3ad244fd
- **Status**: Organization identified, financial reports available for download

### 3. Budget Papers Located
- Youth Justice & Victim Support SDS 2024-25
- Queensland Police Service SDS 2024-25
- **Status**: PDFs require parsing for Mount Isa allocations

### 4. Annual Reports Located
- Department of Youth Justice 2023-24
- Queensland Police Service 2023-24
- **Status**: PDFs require OCR for Mount Isa mentions and statistics

### 5. Parliamentary Record Found
- **Estimates Hearing**: Minister announced Mithangkaya Nguli appointment (Aug 1, 2024)
- **Status**: Transcript available, needs detailed parsing

---

## Critical Issue: Media Statements Blocked

**Problem**: Queensland Government statements.qld.gov.au now returns 403 Forbidden for all requests

**Impact**: HIGH - Media statements contained the most detailed funding announcements:
- On-Country Program: $24M to Mithangkaya Nguli (Statement 100887)
- Youth Co-Responder Teams: $78.1M + $11.2M (Statements 98003, 100864)
- Stronger Communities: $7M (Statement 98337)
- Diversionary Centre: $4M
- Early Action Groups: $1.8M

**Known Statement IDs** (blocked but titles known):
1. 100887: On-Country program $24M (July 2024)
2. 98003: Co-responder team (June 2023)
3. 97577: Community grants
4. 89527: New funding youth crime
5. 98337: Stronger Communities $7M
6. 100864: Youth Co-Responder update
7. 97933: Record youth justice budget
8. 97218: Tougher action youth crime
9. 100544: Police & Community Safety budget
10. 97930: $3.281B police operating budget

**Workarounds**:
1. Manual download via web browser (headers may allow)
2. Use Internet Archive / Wayback Machine
3. Check if RSS feeds or API endpoints exist
4. FOI request for media statement content
5. Search Google Cache for content

---

## Next Steps

### Immediate (High Priority)

1. **Work around media statements block**
   - Try different User-Agent headers
   - Check for RSS feeds or API
   - Manual browser downloads
   - Internet Archive lookups

2. **Parse Budget Papers PDFs**
   - Extract Mount Isa mentions from Youth Justice SDS
   - Extract Mount Isa mentions from QPS SDS
   - Look for specific program allocations

3. **Scrape GrantConnect HTML**
   - Search Mount Isa grants
   - Search Mithangkaya Nguli
   - Search North West Queensland
   - Extract: program, amount, recipient, date

### Medium Priority

4. **Parse Annual Reports**
   - OCR Youth Justice Annual Report for Mount Isa statistics
   - OCR QPS Annual Report for Mount Isa policing data
   - Extract: service numbers, client counts, outcomes

5. **Download ACNC Financial Reports**
   - Get Mithangkaya Nguli annual reports (5 years)
   - Extract: total revenue, government grants, program descriptions
   - Match to government announcements

6. **Scrape Council Documents**
   - Download Youth Strategy 2023-2027
   - Parse for youth programs and funding
   - Extract council-funded initiatives

### Lower Priority

7. **Parliamentary Records Deep Dive**
   - Download Estimates hearing transcript
   - Search Questions on Notice database
   - Extract all Mount Isa youth justice mentions

8. **Implement Audit Office Scraper**
   - Search QAO reports for youth justice
   - Search for regional service delivery audits
   - Extract Mount Isa findings

---

## Technical Challenges

### 1. PDF Parsing
**Challenge**: Most valuable data in PDFs (Budget Papers, Annual Reports)

**Solutions**:
- Use `pdfplumber` or `PyPDF2` for text extraction
- OCR with `pytesseract` if scanned PDFs
- Search for "Mount Isa" and extract context
- Regex for dollar amounts near Mount Isa mentions

**Code Template**:
```python
import pdfplumber
import re

def extract_mount_isa_funding(pdf_url):
    # Download PDF
    # Extract text
    # Search for "Mount Isa" mentions
    # Extract dollar amounts in context
    # Return structured data
```

### 2. 403 Blocking
**Challenge**: Queensland Gov blocking automated access

**Solutions**:
- Rotate User-Agents
- Add delays between requests
- Use proxies if necessary
- Manual fallback approach

### 3. Unstructured Data
**Challenge**: Data in narrative text, not tables

**Solutions**:
- NLP/LLM extraction of funding mentions
- Regex patterns for common formats
- Manual verification of key amounts

---

## Data Quality Assessment

### High Confidence
- ACNC organization identification ✅
- Council total budget amount ✅
- Source URLs verified ✅

### Medium Confidence
- Media statement titles and IDs (from prior research)
- Budget paper locations
- Annual report locations

### Low Confidence
- Specific funding amounts (need PDF parsing)
- Program breakdowns (need detailed extraction)
- Outcomes data (need annual report analysis)

### Missing
- Media statement content (blocked)
- PDF content details
- Federal grants amounts
- Multi-year trends

---

## Known Funding Amounts (From Prior Research)

These amounts were identified in previous research but need to be recaptured:

| Program | Amount | Period | Source Type |
|---------|--------|--------|-------------|
| Intensive On-Country | $24M | 2024-2027 | Media statement |
| Youth Co-Responder Teams | $78.1M | Multi-year | Media statement |
| Co-Responder Capacity | $11.2M | 2024 | Media statement |
| Stronger Communities | $7M | Multi-year | Media statement |
| On Country Trial | $4.2M | 2023 | Media statement |
| Diversionary Centre | $4M | 2024 | Media statement |
| Early Action Groups | $1.8M | Multi-year | Media statement |
| Additional Magistrate | $4.1M | 4 years | Budget papers |
| PCYC Upgrade | ~$1M | 2023 | Media statement |
| **TOTAL IDENTIFIED** | **~$134M+** | 2023-2027 | Multiple |

**Goal**: Recapture this data despite media statement blocking

---

## Success Metrics

To consider this data collection "complete", we need:

- [ ] All 10 media statements content recaptured (currently blocked)
- [ ] Budget Papers parsed with Mount Isa allocations extracted
- [ ] Annual Reports parsed with Mount Isa statistics extracted
- [ ] Federal grants searched and Mount Isa recipients identified
- [ ] ACNC financial reports downloaded for Mithangkaya Nguli
- [ ] Council documents downloaded and parsed
- [ ] Parliamentary records fully extracted
- [ ] All funding amounts in unified CSV with validation status
- [ ] Cross-referencing complete (same funding across multiple sources)
- [ ] Timeline visualization (announcements → allocations → payments)

---

## Files Generated

### Data Files
- `data/money_flows/mount_isa_money_flows_20251114_205202.csv` (15 records)
- `data/money_flows/mount_isa_money_flows_20251114_205202.json` (15 records)
- `data/media_statements/mount_isa_statements_20251114.csv` (10 blocked records)

### Code Files
- `scrapers/comprehensive_money_flow_scraper.py` (main orchestrator)
- `scrapers/mount_isa_media_statements.py` (blocked)

### Documentation
- `DATA_SOURCES_STRATEGY.md` (complete strategy)
- `DATA_COLLECTION_STATUS.md` (this file)

---

## Recommendations

### 1. Focus on Accessible Sources First
Since media statements are blocked, prioritize:
1. **PDF parsing** (Budget Papers, Annual Reports) - high value, accessible
2. **GrantConnect scraping** - federal grants are critical
3. **ACNC financial reports** - actual revenue received
4. **Council documents** - local spending perspective

### 2. Manual Intervention for Blocked Sources
- Open media statements in web browser
- Save HTML/PDF manually
- Add to data collection manually or via import script

### 3. Build PDF Parser
**Priority 1**: Create universal PDF parsing function:
```python
def parse_pdf_for_mount_isa(pdf_url, keywords):
    """
    Download PDF, extract text, search for Mount Isa + keywords
    Return: matching paragraphs, dollar amounts, context
    """
```

### 4. Implement Cross-Validation
Once data from multiple sources collected:
- Match same program across sources
- Flag discrepancies
- Calculate confidence scores
- Generate validation report

### 5. Build Outcomes Dashboard
After funding collection complete:
- Link money → programs → service providers → outcomes
- Show: $134M+ flows, who received it, what results achieved
- Visualization: Sankey diagram of money flows

---

## Next Session TODO

1. Try media statements workaround (Internet Archive, different headers)
2. Build PDF parser for Budget Papers
3. Implement GrantConnect HTML scraper
4. Download and analyze ACNC financial reports for Mithangkaya Nguli
5. Create validation script to cross-reference funding across sources
