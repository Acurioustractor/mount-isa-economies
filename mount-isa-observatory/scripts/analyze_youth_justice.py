"""
Analyze Youth Justice Services Data (1,075 services!)
Explore what services exist, where they are, and what gaps might exist
"""
import pandas as pd
from pathlib import Path
import json

print("\n" + "="*80)
print("📊 ANALYZING YOUTH JUSTICE SERVICES DATA")
print("="*80 + "\n")

data_dir = Path(__file__).parent.parent / 'data' / 'exports'

# Load all youth justice data
services_file = data_dir / 'youth_justice_services_export.csv'
orgs_file = data_dir / 'youth_justice_organizations_export.csv'
locations_file = data_dir / 'youth_justice_locations_export.csv'
taxonomy_file = data_dir / 'youth_justice_taxonomy_export.csv'

# ============================================================================
# PART 1: Services Overview
# ============================================================================

print("="*80)
print("PART 1: SERVICES OVERVIEW")
print("="*80 + "\n")

df_services = pd.read_csv(services_file)
print(f"Total services: {len(df_services):,}\n")

# Show column structure
print("Available data fields:")
for col in df_services.columns:
    non_null = df_services[col].notna().sum()
    pct = non_null / len(df_services) * 100
    if pct > 10:  # Only show fields with >10% data
        print(f"  • {col:30s}: {non_null:>5,} ({pct:>5.1f}%) populated")
print()

# Sample services
print("\nSample services:\n")
for idx, service in df_services.head(10).iterrows():
    print(f"{idx+1}. {service.get('name', 'Unknown')}")
    if pd.notna(service.get('description')):
        desc = str(service['description'])[:100]
        print(f"   {desc}...")
    if pd.notna(service.get('taxonomy_term')):
        print(f"   Category: {service['taxonomy_term']}")
    print()

# ============================================================================
# PART 2: Geographic Distribution
# ============================================================================

print("="*80)
print("PART 2: GEOGRAPHIC DISTRIBUTION")
print("="*80 + "\n")

df_locations = pd.read_csv(locations_file)
print(f"Total locations: {len(df_locations):,}\n")

# Services by state
if 'state' in df_locations.columns:
    print("Services by state:")
    state_counts = df_locations['state'].value_counts()
    for state, count in state_counts.head(10).items():
        print(f"  {state:20s}: {count:>6,} services")
    print()

# Services by suburb/city
if 'suburb' in df_locations.columns:
    print("\nTop 20 suburbs/cities with services:")
    suburb_counts = df_locations['suburb'].value_counts()
    for suburb, count in suburb_counts.head(20).items():
        print(f"  {suburb:40s}: {count:>5,} services")
    print()

# Mount Isa specific
mount_isa_locations = df_locations[
    df_locations['suburb'].str.contains('Mount Isa', case=False, na=False) |
    df_locations['postal_code'].astype(str).str.contains('4825', na=False)
]

if len(mount_isa_locations) > 0:
    print(f"\n🎯 MOUNT ISA: {len(mount_isa_locations)} services found!\n")

    # Get the actual services for Mount Isa
    mount_isa_service_ids = mount_isa_locations['service_id'].unique()
    mount_isa_services = df_services[df_services['id'].isin(mount_isa_service_ids)]

    print("Mount Isa services:")
    for idx, service in mount_isa_services.head(20).iterrows():
        print(f"  • {service.get('name', 'Unknown')}")
        if pd.notna(service.get('taxonomy_term')):
            print(f"    Category: {service['taxonomy_term']}")
    print()
else:
    print("\n⚠️  No services found specifically in Mount Isa")
    print("    (This data might be Queensland-wide or national)\n")

# ============================================================================
# PART 3: Service Categories (Taxonomy)
# ============================================================================

print("="*80)
print("PART 3: SERVICE CATEGORIES")
print("="*80 + "\n")

df_taxonomy = pd.read_csv(taxonomy_file)
print(f"Total taxonomy terms: {len(df_taxonomy):,}\n")

# Show taxonomy structure
if 'name' in df_taxonomy.columns:
    print("Service categories:\n")
    for idx, term in df_taxonomy.head(30).iterrows():
        print(f"  • {term.get('name', 'Unknown')}")
        if pd.notna(term.get('description')):
            desc = str(term['description'])[:80]
            print(f"    {desc}...")
    print()

# Services by category
if 'taxonomy_term' in df_services.columns:
    print("\nServices by category:\n")
    category_counts = df_services['taxonomy_term'].value_counts()
    for category, count in category_counts.head(20).items():
        print(f"  {category:50s}: {count:>5,} services")
    print()

# ============================================================================
# PART 4: Organizations
# ============================================================================

print("="*80)
print("PART 4: ORGANIZATIONS")
print("="*80 + "\n")

df_orgs = pd.read_csv(orgs_file)
print(f"Total organizations: {len(df_orgs):,}\n")

# Show organization structure
print("Sample organizations:\n")
for idx, org in df_orgs.head(10).iterrows():
    print(f"{idx+1}. {org.get('name', 'Unknown')}")
    if pd.notna(org.get('description')):
        desc = str(org['description'])[:100]
        print(f"   {desc}...")
    print()

# ============================================================================
# PART 5: Data Quality Assessment
# ============================================================================

print("="*80)
print("PART 5: DATA QUALITY ASSESSMENT")
print("="*80 + "\n")

# Check completeness
completeness = {}
for col in df_services.columns:
    non_null = df_services[col].notna().sum()
    pct = non_null / len(df_services) * 100
    completeness[col] = pct

print("Data completeness:\n")
high_quality = [(k, v) for k, v in completeness.items() if v >= 80]
medium_quality = [(k, v) for k, v in completeness.items() if 30 <= v < 80]
low_quality = [(k, v) for k, v in completeness.items() if v < 30]

if high_quality:
    print("✅ High quality (>80% complete):")
    for col, pct in sorted(high_quality, key=lambda x: x[1], reverse=True):
        print(f"   {col:30s}: {pct:>5.1f}%")
    print()

if medium_quality:
    print("⚠️  Medium quality (30-80% complete):")
    for col, pct in sorted(medium_quality, key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {col:30s}: {pct:>5.1f}%")
    print()

if low_quality:
    print("❌ Low quality (<30% complete):")
    for col, pct in sorted(low_quality, key=lambda x: x[1], reverse=True)[:10]:
        print(f"   {col:30s}: {pct:>5.1f}%")
    print()

# ============================================================================
# SUMMARY & RECOMMENDATIONS
# ============================================================================

print("="*80)
print("🎯 KEY FINDINGS & RECOMMENDATIONS")
print("="*80 + "\n")

findings = []

# Finding 1: Data volume
findings.append(f"✅ Comprehensive dataset: {len(df_services):,} services, {len(df_orgs):,} organizations")

# Finding 2: Geographic coverage
if 'state' in df_locations.columns:
    states = df_locations['state'].unique()
    findings.append(f"✅ Geographic coverage: {len(states)} states/territories")

# Finding 3: Mount Isa specific
if len(mount_isa_locations) > 0:
    findings.append(f"✅ Mount Isa services: {len(mount_isa_locations)} services identified")
else:
    findings.append(f"⚠️  Mount Isa services: None specifically tagged - may need manual filtering")

# Finding 4: Categories
if 'taxonomy_term' in df_services.columns:
    categories = df_services['taxonomy_term'].nunique()
    findings.append(f"✅ Service diversity: {categories} unique categories")

print("Findings:\n")
for finding in findings:
    print(f"  {finding}")

print("\n" + "="*80)
print("📋 RECOMMENDATIONS FOR MOUNT ISA ECONOMIC OBSERVATORY")
print("="*80 + "\n")

recommendations = [
    "1. Filter youth justice services for Mount Isa region (postcode 4825)",
    "2. Match organizations to economic flows (grants, funding sources)",
    "3. Identify which services are Indigenous-led or culturally safe",
    "4. Map service gaps by comparing to community needs",
    "5. Track funding flows to youth justice organizations",
    "6. Identify opportunities for local service development",
]

for rec in recommendations:
    print(f"  {rec}")

print("\n" + "="*80)
print("✅ ANALYSIS COMPLETE")
print("="*80 + "\n")

print("🚀 Next steps:")
print("  1. Filter services for Mount Isa: create mount_isa_filtered.csv")
print("  2. Import into economic observatory database")
print("  3. Match to funding sources and economic flows")
print("  4. Generate service gap analysis")
print()
