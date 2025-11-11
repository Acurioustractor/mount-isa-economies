Below is a field‑tested blueprint—sources, APIs, scrapers, and validation methods—to map all major economic flows into and out of Mount Isa (LGA: Mount Isa (C), ABS code LGA35300) across government ⇄ business ⇄ community. It’s written like a playbook a top‑tier economic analyst would hand to an intake/data team.

0) Scope, geography & identifiers

Primary unit: Local Government Area (LGA) Mount Isa (C) (ABS code LGA35300). Use ABS ASGS 2021 boundaries and official correspondence tables to translate data that arrive in SA2/SA3/postcode to LGA35300. 
Australian Bureau of Statistics
+2
Australian Bureau of Statistics
+2

Where you’ll need correspondences: Census (often SA2/SA3), ATO (often postcode), health (MBS/PBS at LGA), DSS (SA2 & LGA), labour (DEWR SALM at LGA). Keep a canonical geography bridge using ABS correspondences. 
Australian Bureau of Statistics
+1

1) Data inventory (by flow)
A. Government → Households/Providers (cash & in‑kind)

Health & medicines

MBS (Medicare) services & benefits by LGA: monthly series & dashboards (downloadable tables); extract LGA=Mount Isa (C). Use AIHW and Services Australia endpoints. 
AIHW
+2
Data.gov.au
+2

PBS medicines: monthly benefits & prescriptions by LGA. Useful to size external vs local pharmacy/dispensing spend. 
AIHW
+2
AIHW
+2

Income support & transfers

DSS payment demographics (JobSeeker, Age Pension, etc.) by LGA and SA2 (quarterly). Pull machine‑readable files from data.gov.au; use SA2 for finer granularity then aggregate via correspondences. 
Data.gov.au

Commonwealth procurement & grants

AusTender Contract Notice API (OCDS format) – query contracts by supplier location (postcode 4825) and by buyer agency; reveals Commonwealth dollars flowing to Mount Isa suppliers (and where locals supply outside). There is an official OCDS API & code. 
Data.gov.au
+1

GrantConnect (federal grants) – search grant awards to recipients in Mount Isa; export from portal (no public JSON documented, but bulk lists and award tables are available). 
grants.gov.au
+1

Queensland Government procurement

QTenders / Forward Procurement Pipeline (FPP) – forward look at State spending by category; scrape CSV on the Qld Open Data portal and filter by region/category relevant to North West Qld. For historical awarded contracts and arrangements, use Qld Open Data datasets & CKAN API. 
data.qld.gov.au
+3
data.qld.gov.au
+3
data.qld.gov.au
+3

Local government

Mount Isa City Council: Budget/Annual Report (operating & capital), procurement policy (local weighting, panels), and meeting papers. These give baseline local public spend, contract thresholds, and local preference rules. 
Mount Isa City Council

B. Households/Businesses ⇄ Businesses (earnings, turnover, leakage)

Business stock & industry structure

ABS Counts of Australian Businesses (CABEE) – active business counts by ANZSIC at LGA and SA2; use this to see gaps (e.g., electricians) vs demand. Latest reference period Jul 2021–Jun 2025. 
Australian Bureau of Statistics
+1

ABN Lookup Web Services (ABR public) – resolve local supplier list (postcode 4825; Mount Isa) with ABN, names/aliases, entity type. (Register for GUID; REST/JSON methods available + sample code.) 
ABN Lookup
+2
ABN Lookup
+2

ASIC registry APIs (business names / companies) – helpful to enrich entities (status, dates). Approval needed. 
ASIC

Income, wages & tax

ATO Taxation Statistics – postcode‑level tables for individuals (incomes, deductions), entity counts, PAYG, GST. Use to benchmark household income, small‑business density, and industry ratios; bridge to LGA using correspondences. 
Data.gov.au
+1

Labour market

DEWR Small Area Labour Markets (SALM) – LGA‑level unemployment/employment estimates; note ASGS 2021 changeover guidance for comparability. 
Employment and Workplace Relations

C. Community / Non‑profits / Indigenous Corporations

ACNC Charity Register (bulk open data) – list of registered charities, finances (from Annual Information Statements), service types; filter by Mount Isa LGA or postcode 4825. 
ACNC

(Optional) ORIC public register for Indigenous corporations (if you decide to include Indigenous economic organisations in the mapping). (You can add later.)

D. Mobility & non‑resident economic inflows (FIFO, visitors)

BITRE aviation + Mount Isa Airport passenger stats – monthly/annual passenger movements (commercial + charter). Proxy for contractor inflows and visitor spend. 
bitre.gov.au
+2
bitre.gov.au
+2

E. Geospatial foundations (address → region, supply catchments)

G‑NAF (Geoscape) – open geocoded address file; plus Datasets API and community loaders to get it into Postgres/PostGIS. Use for geocoding suppliers/customers & assigning regions. 
Data.gov.au
+2
GitHub
+2

ABS ASGS 2021 SA2/LGA boundary services – for tiling maps and region joins. 
ArcGIS

2) ETL: APIs & scraping—how to pull it (safely & repeatably)

Rule 1: Prefer APIs/CSV endpoints. Only scrape HTML when no API exists, and always respect robots.txt and T&Cs.

Core API patterns (illustrative)

ABS SDMX Data API (beta) – pull Census & economic series. Start with /dataflow to list datasets; fetch as CSV with labels via the Accept: application/vnd.sdmx.data+csv;labels=both header (fastest for pipelines). 
Australian Bureau of Statistics
+2
Australian Bureau of Statistics
+2

data.qld.gov.au CKAN – use package → resource → datastore_search for CSV/JSON (e.g., FPP and awarded contracts). 
data.qld.gov.au

AusTender OCDS API – query Contract Notice (CN) by dates, supplier ABN/postcode, or buyer; returns OCDS JSON; use the official repo’s README for endpoints and pagination. 
Data.gov.au
+1

ACNC Open Data – bulk datasets are on data.gov.au linked from ACNC “Download Charity Register” page; schedule weekly pulls (ACNC says it updates regularly). 
ACNC

ABN Lookup JSON services – register for a GUID; use Name search with locality filters; back‑off & cache to respect rate limits. 
ABN Lookup

AIHW Health dashboards (MBS/PBS) – prefer the “Data” pages offering CSV tables by LGA; store with date stamps. 
AIHW
+1

ATO TaxStats – pull Individuals Table 25 (by postcode) CSV and others; version every release; apply postcode→LGA bridge for Mount Isa. 
Data.gov.au
+1

BITRE aviation – monthly XLSX (airport traffic) + PDF summaries; parse XLSX directly; maintain route and airport codes. 
bitre.gov.au

Scraping (when required)

Local council pages (budget PDFs, agendas): build a Scrapy spider that finds PDFs, stores source URL + checksum, and extracts tables with Camelot/Tabula; log page title/date for audit. (Mount Isa Council budget & procurement policy pages are stable entry points.) 
Mount Isa City Council

QTenders web pages (if a specific detail lacks API): scrape list pages lightly; but prefer the Open Data FPP CSV and awarded contracts datasets instead. 
data.qld.gov.au
+1

Data store & orchestration

Storage: PostgreSQL + PostGIS (geocoding & boundaries), plus object storage for raw CSV/XLSX/PDF.

Pipelines: Prefect or Airflow for scheduled jobs; dbt for transforms (dimensional model).

Validation: Great Expectations for schema & range tests; pytest for joins/correspondences.

3) Modeling the money maps

Design a flows schema that can aggregate from transaction‑level (where available) up to LGA summaries:

Dimensions: date, geo_region (LGA/SA2), program (e.g., MBS group, PBS ATC), industry_ANZSIC, payer_type (Commonwealth/State/LGA/Household/Business), payee_type (Local business, External business, Household, Charity).

Facts: amount, count, inflow_outflow_flag, from_region, to_region, source_system, confidence.

Entity resolution: Maintain an entity table keyed by ABN/ACN; enrich from ABN Lookup/ASIC; classify local vs external using G‑NAF and ASGS lookups. 
Data.gov.au

Leakage mapping (where money leaves):

Join local spend proxies (e.g., MBS/PBS benefits, local gov vendors, AusTender awards to 4825 suppliers) to local capacity (CABEE counts by ANZSIC). The gaps (benefits or contracts with no matching local capacity) flag replacement opportunities (e.g., electricians). 
Australian Bureau of Statistics

4) Verification & quality assurance (what a regulator/economist would check)

Source‑of‑truth bias & definitional alignment

Use ABS methodology notes (CABEE scope), and ASGS correspondences to ensure apples‑to‑apples. Log every remap (postcode→LGA). 
Australian Bureau of Statistics
+1

Triangulation

Income reality check: ATO individual incomes (postcodes in 4825) vs Census median incomes vs DSS payment counts – track share of income from transfers vs wages. 
Data.gov.au
+1

Health spend check: MBS/PBS per‑capita vs AIHW dashboard; ensure LGA totals match downloaded tables. 
AIHW
+1

Procurement check: AusTender local supplier counts vs ABN Lookup entity list (address in G‑NAF within LGA boundary). 
Data.gov.au
+1

Statistical tests

Time‑series continuity: flag structural breaks at ASGS 2021 changeover (SALM, Census). 
Employment and Workplace Relations

Outlier windows: Z‑score window on monthly MBS/PBS; cross‑check with known events (e.g., influx from charter flights). 
bitre.gov.au

Ground truth

Vendor spot‑checks: sample 30 suppliers (ABN & address), phone/web verify; keep signed‑off audit log.

Local council reconciliation: compare council budget line items vs known tenders; consult Procurement Policy thresholds/weightings to understand local preference effect. 
Mount Isa City Council

Provenance & replayability

Store raw → staged → modeled with hashes, fetch timestamps, and source URLs; versioned dbt models with tests.

5) Tooling to see the flows

Dashboards: Apache Superset or Metabase for tabular/graphs; Kepler.gl / QGIS for geospatial layers (e.g., heatmaps of supplier locations vs contracts).

Tracing software (open & low cost):

OpenSpending for budget/spend cube visualizations (treemaps/bubble trees). Use for council/State/Federal spend slices. 
docs.openspending.org
+1

OCDS data model & R/Python tooling for procurement timelines and supplier market share. 
standard.open-contracting.org
+1

6) “How to” – concrete pulls you can run first

Replace {…} with your keys/filters. These outline what to fetch and how to align it to Mount Isa (C).

ABS business counts (CABEE)

Download LGA table (latest release) → filter Mount Isa (C) → join ANZSIC classification for sectoral gaps. 
Australian Bureau of Statistics

ABN Lookup (local suppliers)

Use MatchingNames or SearchByName with locality=Mount Isa and postcode 4825; cache results; store ABN, entity name, main business location. 
ABN Lookup

AusTender OCDS

Query supplier address → 4825 and award_date >= 2019-01-01. Shape to from=Commonwealth Buyer → to=Local Supplier flows; also invert to find local suppliers paid by non‑local buyers (inflows). 
Data.gov.au

Queensland procurement (awarded & pipeline)

Pull FPP CSV; filter by categories relevant to Mount Isa region (transport, health, infrastructure). Pull awarded contracts dataset; geocode suppliers with G‑NAF to mark local vs non‑local. 
data.qld.gov.au
+1

MBS/PBS by LGA

Download monthly MBS and PBS tables for Mount Isa (C); compute per‑capita using ABS LGA population; trend by group (e.g., GP, diagnostics) to identify services with high out‑of‑region leakage. 
AIHW
+1

DSS payments

Load quarterly LGA file; compute share of adults on key payments; link to training pipeline needs (electricians, care workers). 
Data.gov.au

BITRE / ISA Airport

Parse monthly airport XLSX; tag charter vs RPT if available; proxy non‑resident contractor inflow; overlay with mining shutdowns/expansions timelines. 
bitre.gov.au
+1

Council budget & policy

Extract operating & capital line items from budget PDFs; map to local vs external vendor capacity using CABEE & ABN lists; note local preference policy settings. 
Mount Isa City Council

7) Estimating replacement & reinvestment opportunities

Find the “bridge” categories: Categories where benefits/contract spend are large but local provider capacity is thin (e.g., electricians, plumbers, aged care, diagnostics). Combine MBS/PBS (household health demand), council/State procurement (public demand), CABEE (local supply headcount), ABN/ASIC (who exists), and airport flow spikes (non‑resident specialists). 
bitre.gov.au
+3
AIHW
+3
AIHW
+3

Build a one‑year pilot: set a 10% localization goal in two categories (e.g., electrotechnology & in‑home care) aligned with TAFE QLD Mount Isa apprenticeship pathways (electrician Cert III). Track jobs created, leakage reduced, and social outcomes. 
TAFE Queensland
+1

8) Governance, ethics & licensing

Licences: ABS (CC BY 4.0), AIHW (open with attribution), Qld Open Data (CC BY 4.0), ACNC open datasets, ATO TaxStats (CC BY 2.5 AU), G‑NAF (Geoscape open terms). Respect each dataset’s licence and don’t republish personal data. 
Data.gov.au

API terms: ABN Lookup requires a GUID and has usage limits; do not bulk‑harvest beyond purpose. 
ABN Lookup

9) Architecture at a glance

Ingest: Python (requests, pandas, pandasdmx for ABS), ckanapi for CKAN portals; Scrapy for PDFs.

Store: Postgres/PostGIS + S3‑like bucket for raw; DuckDB for fast ad‑hoc joins.

Transform: dbt (dimension/fact models with tests).

Validate: Great Expectations (+ pytest for geo joins, key uniqueness).

Viz: Superset/Metabase (KPIs: inflows, outflows, local share), Kepler.gl for maps, OpenSpending for budget treemaps. 
docs.openspending.org

10) 30–60–90 day plan (practical)

Days 1–30 (standing up the pipes)

Stand up Postgres/PostGIS; load ASGS correspondences & G‑NAF core.

Connect ABS CABEE, DSS, MBS/PBS, ATO Table 25, BITRE, Qld FPP & awarded contracts, AusTender OCDS, ACNC. First QA dashboards (level‑1). 
ACNC
+9
Australian Bureau of Statistics
+9
Data.gov.au
+9

Days 31–60 (leakage map & opportunity screen)

Build entity graph of suppliers (ABN/ASIC) and tag local vs non‑local.

Publish leakage treemap: top 10 categories where spend leaves Mount Isa.

Convene with council & TAFE on priority trade pathways (electricians/care). 
TAFE Queensland

Days 61–90 (pilot implementation & verification)

Create community investment pool pipeline (identify investable gaps; small tools/training grants aligned to local providers).

Establish verification runs (quarterly refresh & variance notes) and publish a transparent methodology page.

11) What “world‑class verification” looks like (checklist)

Provenance notebook (per source: URL, fetch date, licence, schema, checksum).

Geo integrity: 100% of records mapped to SA2/LGA with valid codes; ZERO unmapped after remediation.

Cross‑source consistency: totals reconcile within tolerance (e.g., MBS LGA totals vs AIHW dashboard for same period). 
AIHW

Sampling: 30 ABNs manually verified quarterly (registered address in Mount Isa; phone/web check). 
ABN Lookup

Change logs: ASGS changeovers and catalogue updates annotated (e.g., SALM moving to ASGS 2021). 
Employment and Workplace Relations

12) A note on feasibility & gaps

Bank/card transaction data (the gold standard for leakage) isn’t open. Your best public‑data proxy is health & public procurement plus business counts and airport flows. That still yields high‑signal targets for local replacement. 
Australian Bureau of Statistics
+1

Handy links (for your engineers)

ABS Data API (SDMX) user guide & examples. 
Australian Bureau of Statistics
+2
Australian Bureau of Statistics
+2

ASGS correspondences (LGA/SA2) & allocation files. 
Australian Bureau of Statistics
+1

Queensland Open Data CKAN API guide. 
data.qld.gov.au

AusTender OCDS API (code & docs). 
Data.gov.au
+1

ABN Lookup JSON services & sample code. 
ABN Lookup
+1

AIHW MBS/PBS by LGA data pages. 
AIHW
+1

DSS payment demographics (LGA/SA2). 
Data.gov.au

BITRE airport traffic data & Mount Isa Airport stats. 
bitre.gov.au
+1

G‑NAF open data & loaders. 
Data.gov.au
+1

Mount Isa City Council procurement/budget portal. 
Mount Isa City Council

Want me to scaffold this?

If you’d like, I can generate a minimal repo structure (dbt models, ingestion scripts with example API calls, validation checks, and a Superset starter dashboard spec) tailored to Mount Isa (C) and the categories you want to localize first (e.g., electrotechnology and care services).