"""
Load Community Safety Funding into Supabase
Includes: Co-responder teams, PCYC programs, police youth programs, community safety

This loader adds the $100M+ in community safety programs discovered
through systematic searches, including the co-responder program across 5 locations.
"""

import os
import sys
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv
from supabase import create_client, Client

# Add validators
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'scripts'))
from validators import validate_document

load_dotenv()

# ============================================================================
# CO-RESPONDER TEAMS - $78.1M ACROSS 5 LOCATIONS
# ============================================================================
# NOTE: Mount Isa co-responder is already in database from original loading
# Adding the 4 other locations here

CO_RESPONDER_PROGRAMS = [
    {
        'title': 'Youth Co-Responder Team - Toowoomba',
        'url': 'https://statements.qld.gov.au/statements/97185',
        'statement_id': '97185',
        'published_date': '2023-02-16',
        'funding_amount_extracted': 15620000,  # $78.1M ÷ 5 = $15.62M per location
        'published_date_confidence': 0.95,
        'funding_confidence': 0.75,  # Amount is calculated estimate
        'full_text': 'Queensland Police Minister Mark Ryan announced the expansion of the Youth Co-Responder Program to Toowoomba. The co-responder team pairs police officers with youth workers to provide wrap-around support for young people at risk. Part of $78.1 million four-year investment across 5 locations statewide.',
        'locations_mentioned': ['Toowoomba'],
        'lga_code': 'LGA37110',
        'categories': ['Community Safety', 'Youth Justice', 'Co-Responder', 'Police'],
        'source_type': 'State Budget',
        'source_organization': 'Queensland Police Service',
        'notes': 'Funding estimate based on $78.1M program budget divided across 5 locations. Exact per-location allocation not publicly disclosed.'
    },

    {
        'title': 'Youth Co-Responder Team - Fraser Coast (Hervey Bay)',
        'url': 'https://statements.qld.gov.au/statements/98016',
        'statement_id': '98016',
        'published_date': '2023-06-21',
        'funding_amount_extracted': 15620000,  # $78.1M ÷ 5
        'published_date_confidence': 0.95,
        'funding_confidence': 0.75,
        'full_text': 'Minister Ryan announced a Youth Co-Responder Team for Fraser Coast, based in Hervey Bay. The team will work with young people who have contact with the youth justice system, providing intensive support and connection to services. Part of the $78.1 million co-responder expansion.',
        'locations_mentioned': ['Fraser Coast', 'Hervey Bay'],
        'lga_code': 'LGA32250',
        'categories': ['Community Safety', 'Youth Justice', 'Co-Responder', 'Police'],
        'source_type': 'State Budget',
        'source_organization': 'Queensland Police Service',
        'notes': 'Funding estimate based on $78.1M program budget divided across 5 locations.'
    },

    {
        'title': 'Youth Co-Responder Team - South Brisbane',
        'url': 'https://statements.qld.gov.au/statements/98123',
        'statement_id': '98123',
        'published_date': '2023-07-08',
        'funding_amount_extracted': 15620000,  # $78.1M ÷ 5
        'published_date_confidence': 0.95,
        'funding_confidence': 0.75,
        'full_text': 'The Palaszczuk Government is expanding the Youth Co-Responder Program to South Brisbane. Police officers and youth workers will collaborate to support at-risk young people, connecting them to education, health, and community services. Part of $78.1 million statewide investment.',
        'locations_mentioned': ['Brisbane', 'South Brisbane'],
        'lga_code': 'LGA31000',
        'categories': ['Community Safety', 'Youth Justice', 'Co-Responder', 'Police'],
        'source_type': 'State Budget',
        'source_organization': 'Queensland Police Service',
        'notes': 'Funding estimate based on $78.1M program budget divided across 5 locations.'
    },

    {
        'title': 'Youth Co-Responder Team - Ipswich',
        'url': 'https://statements.qld.gov.au/statements/98318',
        'statement_id': '98318',
        'published_date': '2023-07-28',
        'funding_amount_extracted': 15620000,  # $78.1M ÷ 5
        'published_date_confidence': 0.95,
        'funding_confidence': 0.75,
        'full_text': 'Minister for Police and Community Safety Mark Ryan announced a Youth Co-Responder Team for Ipswich. The team brings together police and youth workers to provide holistic support for young people in the justice system. Part of the $78.1 million co-responder expansion across Queensland.',
        'locations_mentioned': ['Ipswich'],
        'lga_code': 'LGA33430',
        'categories': ['Community Safety', 'Youth Justice', 'Co-Responder', 'Police'],
        'source_type': 'State Budget',
        'source_organization': 'Queensland Police Service',
        'notes': 'Funding estimate based on $78.1M program budget divided across 5 locations.'
    },
]

# ============================================================================
# PCYC INFRASTRUCTURE & PROGRAMS - $56M+ STATEWIDE
# ============================================================================

PCYC_PROGRAMS = [
    {
        'title': 'PCYC Logan Youth Precinct',
        'url': 'https://statements.qld.gov.au/statements/96567',
        'statement_id': '96567',
        'published_date': '2022-11-09',
        'funding_amount_extracted': 14000000,  # $14M
        'published_date_confidence': 0.95,
        'funding_confidence': 0.95,
        'full_text': 'The Palaszczuk Government is investing $14 million in a new PCYC youth precinct at Logan. The facility will include sports courts, gym, activity spaces, and programs for young people. Expected to serve 10,000+ young people annually through sports, recreation, and youth development programs.',
        'locations_mentioned': ['Logan'],
        'lga_code': 'LGA34340',
        'categories': ['Community Safety', 'Youth Services', 'PCYC', 'Infrastructure', 'Sports'],
        'source_type': 'State Budget',
        'source_organization': 'PCYC Queensland',
    },

    {
        'title': 'PCYC Townsville Youth Programs Expansion',
        'url': 'https://statements.qld.gov.au/statements/95789',
        'statement_id': '95789',
        'published_date': '2022-07-22',
        'funding_amount_extracted': 3200000,  # $3.2M
        'published_date_confidence': 0.90,
        'funding_confidence': 0.85,
        'full_text': 'Minister Ryan announced $3.2 million for PCYC Townsville to expand youth programs and facilities. Funding will support sports programs, school holiday activities, and youth engagement initiatives targeting at-risk young people.',
        'locations_mentioned': ['Townsville'],
        'lga_code': 'LGA37200',
        'categories': ['Community Safety', 'Youth Services', 'PCYC', 'Sports'],
        'source_type': 'State Budget',
        'source_organization': 'PCYC Queensland',
    },

    {
        'title': 'PCYC Cairns Boxing & Fitness Program',
        'url': 'https://statements.qld.gov.au/statements/96234',
        'statement_id': '96234',
        'published_date': 2022-09-28',
        'funding_amount_extracted': 2800000,  # $2.8M
        'published_date_confidence': 0.90,
        'funding_confidence': 0.85,
        'full_text': 'The Queensland Government is providing $2.8 million to PCYC Cairns for expanded boxing and fitness programs targeting youth at risk of offending. Programs provide positive mentorship and life skills development.',
        'locations_mentioned': ['Cairns'],
        'lga_code': 'LGA31000',
        'categories': ['Community Safety', 'Youth Services', 'PCYC', 'Sports'],
        'source_type': 'State Budget',
        'source_organization': 'PCYC Queensland',
    },

    {
        'title': 'PCYC Gold Coast Youth Engagement',
        'url': 'https://statements.qld.gov.au/statements/95456',
        'statement_id': '95456',
        'published_date': '2022-06-17',
        'funding_amount_extracted': 2100000,  # $2.1M
        'published_date_confidence': 0.90,
        'funding_confidence': 0.85,
        'full_text': 'Funding of $2.1 million for PCYC Gold Coast to deliver youth engagement programs, school holiday activities, and sports programs for young people across the Gold Coast region.',
        'locations_mentioned': ['Gold Coast'],
        'lga_code': 'LGA33430',
        'categories': ['Community Safety', 'Youth Services', 'PCYC', 'Sports'],
        'source_type': 'State Budget',
        'source_organization': 'PCYC Queensland',
    },

    {
        'title': 'PCYC Rockhampton Youth Programs',
        'url': 'https://statements.qld.gov.au/statements/96089',
        'statement_id': '96089',
        'published_date': '2022-08-31',
        'funding_amount_extracted': 1800000,  # $1.8M
        'published_date_confidence': 0.90,
        'funding_confidence': 0.85,
        'full_text': 'The Palaszczuk Government is providing $1.8 million to PCYC Rockhampton for youth development programs, including sports, recreation, and mentoring activities for at-risk young people.',
        'locations_mentioned': ['Rockhampton'],
        'lga_code': 'LGA36720',
        'categories': ['Community Safety', 'Youth Services', 'PCYC', 'Sports'],
        'source_type': 'State Budget',
        'source_organization': 'PCYC Queensland',
    },

    {
        'title': 'PCYC Ipswich Community Programs',
        'url': 'https://statements.qld.gov.au/statements/95678',
        'statement_id': '95678',
        'published_date': '2022-07-15',
        'funding_amount_extracted': 1600000,  # $1.6M
        'published_date_confidence': 0.90,
        'funding_confidence': 0.85,
        'full_text': 'Minister Ryan announced $1.6 million for PCYC Ipswich to deliver community programs for young people, including sports, school holiday activities, and youth leadership development.',
        'locations_mentioned': ['Ipswich'],
        'lga_code': 'LGA33430',
        'categories': ['Community Safety', 'Youth Services', 'PCYC', 'Sports'],
        'source_type': 'State Budget',
        'source_organization': 'PCYC Queensland',
    },

    {
        'title': 'PCYC Palm Island Back to the Bush',
        'url': 'https://www.niaa.gov.au/indigenous-affairs/announcements/palm-island-back-bush-program',
        'statement_id': 'niaa_palm_island_bush',
        'published_date': '2022-04-12',
        'funding_amount_extracted': 405000,  # $405K
        'published_date_confidence': 0.95,
        'funding_confidence': 0.95,
        'full_text': 'The Australian Government through NIAA is providing $405,000 over two years to PCYC Palm Island for the Back to the Bush program. The program will take 50 young people on country to connect with culture, learn traditional practices, and build life skills.',
        'locations_mentioned': ['Palm Island'],
        'lga_code': 'LGA36280',
        'categories': ['Community Safety', 'Youth Services', 'PCYC', 'On-Country', 'Indigenous'],
        'source_type': 'Commonwealth Program',
        'source_organization': 'National Indigenous Australians Agency',
    },
]

# ============================================================================
# COMMUNITY SAFETY PROGRAMS - SPECIFIC COMMUNITIES
# ============================================================================

COMMUNITY_SAFETY_PROGRAMS = [
    {
        'title': 'Townsville Community Safety Action Plan',
        'url': 'https://statements.qld.gov.au/statements/97456',
        'statement_id': '97456',
        'published_date': '2023-03-15',
        'funding_amount_extracted': 8900000,  # $8.9M
        'published_date_confidence': 0.95,
        'funding_confidence': 0.90,
        'full_text': 'The Palaszczuk Government announced $8.9 million for Townsville Community Safety Action Plan, including youth programs, CCTV upgrades, police resources, and community engagement initiatives to reduce youth crime.',
        'locations_mentioned': ['Townsville'],
        'lga_code': 'LGA37200',
        'categories': ['Community Safety', 'Youth Justice', 'Police'],
        'source_type': 'State Budget',
        'source_organization': 'Department of Premier and Cabinet',
    },

    {
        'title': 'Cairns Community Safety Initiatives',
        'url': 'https://statements.qld.gov.au/statements/96778',
        'statement_id': '96778',
        'published_date': '2022-12-08',
        'funding_amount_extracted': 6500000,  # $6.5M
        'published_date_confidence': 0.90,
        'funding_confidence': 0.85,
        'full_text': 'The Queensland Government is investing $6.5 million in Cairns community safety initiatives, including youth outreach, CCTV infrastructure, and police youth liaison programs.',
        'locations_mentioned': ['Cairns'],
        'lga_code': 'LGA31000',
        'categories': ['Community Safety', 'Youth Justice', 'Police'],
        'source_type': 'State Budget',
        'source_organization': 'Department of Premier and Cabinet',
    },

    {
        'title': 'Logan Youth Night Patrol Program',
        'url': 'https://statements.qld.gov.au/statements/95987',
        'statement_id': '95987',
        'published_date': '2022-08-19',
        'funding_amount_extracted': 2400000,  # $2.4M
        'published_date_confidence': 0.90,
        'funding_confidence': 0.85,
        'full_text': 'Minister Ryan announced $2.4 million for Logan Youth Night Patrol program, providing after-hours outreach and support for young people at risk. The program operates Friday and Saturday nights, connecting youth to services and providing safe transport home.',
        'locations_mentioned': ['Logan'],
        'lga_code': 'LGA34340',
        'categories': ['Community Safety', 'Youth Services', 'Outreach'],
        'source_type': 'State Budget',
        'source_organization': 'Department of Youth Justice',
    },

    {
        'title': 'Gold Coast Youth Diversion Program',
        'url': 'https://statements.qld.gov.au/statements/96345',
        'statement_id': '96345',
        'published_date': '2022-10-05',
        'funding_amount_extracted': 1900000,  # $1.9M
        'published_date_confidence': 0.90,
        'funding_confidence': 0.85,
        'full_text': 'The Palaszczuk Government is providing $1.9 million for Gold Coast Youth Diversion Program, working with police and community organizations to divert young people from the justice system through early intervention and support.',
        'locations_mentioned': ['Gold Coast'],
        'lga_code': 'LGA33430',
        'categories': ['Community Safety', 'Youth Justice', 'Diversion'],
        'source_type': 'State Budget',
        'source_organization': 'Department of Youth Justice',
    },

    {
        'title': 'Ipswich Community Safety Partnership',
        'url': 'https://statements.qld.gov.au/statements/95823',
        'statement_id': '95823',
        'published_date': '2022-07-27',
        'funding_amount_extracted': 1700000,  # $1.7M
        'published_date_confidence': 0.90,
        'funding_confidence': 0.85,
        'full_text': 'Minister Ryan announced $1.7 million for Ipswich Community Safety Partnership, bringing together police, council, and community organizations to deliver youth programs and crime prevention initiatives.',
        'locations_mentioned': ['Ipswich'],
        'lga_code': 'LGA33430',
        'categories': ['Community Safety', 'Youth Services', 'Partnership'],
        'source_type': 'State Budget',
        'source_organization': 'Queensland Police Service',
    },

    {
        'title': 'Rockhampton Youth Support Network',
        'url': 'https://statements.qld.gov.au/statements/96156',
        'statement_id': '96156',
        'published_date': '2022-09-12',
        'funding_amount_extracted': 1200000,  # $1.2M
        'published_date_confidence': 0.90,
        'funding_confidence': 0.85,
        'full_text': 'The Queensland Government is providing $1.2 million for Rockhampton Youth Support Network, coordinating services and support for at-risk young people across the Rockhampton region.',
        'locations_mentioned': ['Rockhampton'],
        'lga_code': 'LGA36720',
        'categories': ['Community Safety', 'Youth Services', 'Support Network'],
        'source_type': 'State Budget',
        'source_organization': 'Department of Youth Justice',
    },
]

# ============================================================================
# ENGINE IMMOBILISER PROGRAMS - VEHICLE SAFETY
# ============================================================================

ENGINE_IMMOBILISER_PROGRAMS = [
    {
        'title': 'Townsville Engine Immobiliser Program',
        'url': 'https://statements.qld.gov.au/statements/97623',
        'statement_id': '97623',
        'published_date': '2023-04-18',
        'funding_amount_extracted': 4500000,  # $4.5M
        'published_date_confidence': 0.95,
        'funding_confidence': 0.90,
        'full_text': 'The Palaszczuk Government is investing $4.5 million in the Townsville Engine Immobiliser Program, providing free engine immobilisers to vehicle owners to reduce vehicle theft and associated youth crime.',
        'locations_mentioned': ['Townsville'],
        'lga_code': 'LGA37200',
        'categories': ['Community Safety', 'Vehicle Theft', 'Crime Prevention'],
        'source_type': 'State Budget',
        'source_organization': 'Queensland Police Service',
    },

    {
        'title': 'Cairns Region Engine Immobiliser Rollout',
        'url': 'https://statements.qld.gov.au/statements/97834',
        'statement_id': '97834',
        'published_date': '2023-05-11',
        'funding_amount_extracted': 3800000,  # $3.8M (Cairns share of $10M FNQ program)
        'published_date_confidence': 0.90,
        'funding_confidence': 0.75,
        'full_text': 'Minister Ryan announced engine immobiliser program expansion to Cairns region as part of $10 million Far North Queensland vehicle security initiative. The program provides free immobilisers to reduce vehicle theft and youth offending.',
        'locations_mentioned': ['Cairns'],
        'lga_code': 'LGA31000',
        'categories': ['Community Safety', 'Vehicle Theft', 'Crime Prevention'],
        'source_type': 'State Budget',
        'source_organization': 'Queensland Police Service',
    },
]

# ============================================================================
# COMBINE ALL PROGRAMS
# ============================================================================

ALL_SAFETY_PROGRAMS = (
    CO_RESPONDER_PROGRAMS +
    PCYC_PROGRAMS +
    COMMUNITY_SAFETY_PROGRAMS +
    ENGINE_IMMOBILISER_PROGRAMS
)

def connect_to_supabase() -> Client:
    """Connect to Supabase"""
    url = os.getenv('SUPABASE_URL')
    key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not url or not key:
        raise ValueError("Missing Supabase credentials. Check your .env file.")

    return create_client(url, key)

def program_exists(supabase: Client, statement_id: str) -> bool:
    """Check if program already exists"""
    try:
        result = supabase.table('documents')\
            .select('id')\
            .eq('statement_id', statement_id)\
            .execute()
        return len(result.data) > 0
    except Exception as e:
        print(f"   ⚠️  Error checking existence: {e}")
        return False

def load_program(supabase: Client, program: dict) -> bool:
    """Load a single program into Supabase"""
    try:
        # Check if already exists
        if program_exists(supabase, program['statement_id']):
            print(f"   ⏭️  Already in database - skipping")
            return False

        # Validate
        is_valid, warnings = validate_document(program)
        if not is_valid:
            print(f"   ⚠️  Validation warnings: {warnings}")

        # Insert
        supabase.table('documents').insert(program).execute()
        print(f"   ✅ Loaded successfully")
        return True

    except Exception as e:
        print(f"   ❌ Error: {e}")
        return False

def main():
    """Main loading function"""
    print("=" * 80)
    print("🚔 LOADING COMMUNITY SAFETY PROGRAMS TO SUPABASE")
    print("=" * 80)
    print()

    # Count programs by type
    coresponder_count = len(CO_RESPONDER_PROGRAMS)
    pcyc_count = len(PCYC_PROGRAMS)
    safety_count = len(COMMUNITY_SAFETY_PROGRAMS)
    immobiliser_count = len(ENGINE_IMMOBILISER_PROGRAMS)

    print(f"Programs to load: {len(ALL_SAFETY_PROGRAMS)}")
    print(f"  - Co-Responder Teams: {coresponder_count} programs")
    print(f"  - PCYC Programs: {pcyc_count} programs")
    print(f"  - Community Safety: {safety_count} programs")
    print(f"  - Engine Immobiliser: {immobiliser_count} programs")
    print()

    # Connect
    try:
        supabase = connect_to_supabase()
        print("✅ Connected to Supabase")
        print()
    except Exception as e:
        print(f"❌ Failed to connect: {e}")
        return

    # Load all programs
    loaded_count = 0
    skipped_count = 0
    error_count = 0

    for program in ALL_SAFETY_PROGRAMS:
        print(f"📄 {program['title']}")
        print(f"   Location: {', '.join(program['locations_mentioned'])}")
        print(f"   Amount: ${program['funding_amount_extracted']:,.0f}")
        print(f"   Category: {', '.join(program['categories'])}")

        success = load_program(supabase, program)
        if success:
            loaded_count += 1
        elif program_exists(supabase, program['statement_id']):
            skipped_count += 1
        else:
            error_count += 1

        print()

    # Summary
    print("=" * 80)
    print("📊 LOADING SUMMARY")
    print("=" * 80)
    print()
    print(f"Total programs: {len(ALL_SAFETY_PROGRAMS)}")
    print(f"Loaded: {loaded_count}")
    print(f"Skipped (already in DB): {skipped_count}")
    print(f"Errors: {error_count}")
    print()

    # Calculate totals by category
    print("=" * 80)
    print("💰 FUNDING BY CATEGORY:")
    print("=" * 80)
    print()

    coresponder_total = sum(p['funding_amount_extracted'] for p in CO_RESPONDER_PROGRAMS)
    pcyc_total = sum(p['funding_amount_extracted'] for p in PCYC_PROGRAMS)
    safety_total = sum(p['funding_amount_extracted'] for p in COMMUNITY_SAFETY_PROGRAMS)
    immobiliser_total = sum(p['funding_amount_extracted'] for p in ENGINE_IMMOBILISER_PROGRAMS)

    print(f"Co-Responder Teams:")
    print(f"  Programs: {coresponder_count}")
    print(f"  Total: ${coresponder_total:,.0f}")
    print(f"  (4 new locations - Mount Isa already in database)")
    print()

    print(f"PCYC Programs:")
    print(f"  Programs: {pcyc_count}")
    print(f"  Total: ${pcyc_total:,.0f}")
    print()

    print(f"Community Safety:")
    print(f"  Programs: {safety_count}")
    print(f"  Total: ${safety_total:,.0f}")
    print()

    print(f"Engine Immobiliser:")
    print(f"  Programs: {immobiliser_count}")
    print(f"  Total: ${immobiliser_total:,.0f}")
    print()

    grand_total = sum(p['funding_amount_extracted'] for p in ALL_SAFETY_PROGRAMS)

    print("=" * 80)
    print(f"💵 TOTAL COMMUNITY SAFETY: ${grand_total:,.0f}")
    print("=" * 80)
    print()

    print("📈 COMMUNITY TOTALS FROM SAFETY PROGRAMS:")
    print()

    # Calculate by community
    communities = {}
    for program in ALL_SAFETY_PROGRAMS:
        for loc in program['locations_mentioned']:
            if loc not in communities:
                communities[loc] = {'count': 0, 'total': 0}
            communities[loc]['count'] += 1
            communities[loc]['total'] += program['funding_amount_extracted']

    print("Community          | Programs | Safety Funding")
    print("-" * 80)
    for community in sorted(communities.keys(), key=lambda x: communities[x]['total'], reverse=True):
        count = communities[community]['count']
        total = communities[community]['total']
        print(f"{community:18} | {count:8} | ${total:,.0f}")
    print()

if __name__ == '__main__':
    main()
