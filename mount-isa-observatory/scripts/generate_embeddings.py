"""
Generate vector embeddings for all economic data
Makes data searchable via LLM/semantic search
"""

import os
from supabase import create_client, Client
import openai
from tqdm import tqdm
import time

# Configuration
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

if not all([SUPABASE_URL, SUPABASE_KEY, OPENAI_API_KEY]):
    print("❌ Error: Set environment variables:")
    print("  - SUPABASE_URL")
    print("  - SUPABASE_SERVICE_ROLE_KEY")
    print("  - OPENAI_API_KEY")
    exit(1)

# Initialize clients
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)
openai.api_key = OPENAI_API_KEY

print("\n" + "="*80)
print("🧠 GENERATING EMBEDDINGS FOR ECONOMIC DATA")
print("="*80 + "\n")

def generate_embedding(text: str):
    """Generate OpenAI embedding"""
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"  # 1536 dimensions, $0.02 per 1M tokens
    )
    return response.data[0].embedding

def chunk_contract(contract):
    """Create searchable chunk for a contract"""
    content = f"""CONTRACT: {contract.get('contract_title', 'Untitled')}
Supplier: {contract.get('supplier_name', 'Unknown')}
Agency: {contract.get('agency', 'Unknown')}
Value: ${contract.get('value', 0):,.2f} if contract.get('value') else 'Unknown'
Period: {contract.get('start_date', '')} to {contract.get('end_date', '')}
Description: {contract.get('contract_description', '')[:500]}"""

    metadata = {
        'type': 'contract',
        'value': float(contract.get('value', 0)) if contract.get('value') else None,
        'supplier_abn': contract.get('supplier_abn'),
        'agency': contract.get('agency'),
        'mount_isa_relevance': contract.get('mount_isa_relevance'),
        'date_range': f"[{contract.get('start_date')},{contract.get('end_date')}]"
    }

    return content, metadata

def chunk_grant(grant):
    """Create searchable chunk for a grant"""
    content = f"""GRANT: {grant.get('title', 'Untitled')}
Amount: ${grant.get('amount', 0):,.2f} if grant.get('amount') else f"${grant.get('amount_min', 0):,.0f} - ${grant.get('amount_max', 0):,.0f}"
Agency: {grant.get('funding_agency', 'Unknown')}
Status: {grant.get('status', 'Unknown')}
Closes: {grant.get('close_date', 'Unknown')}
Eligibility: {', '.join(grant.get('eligible_entities', []))}
Description: {grant.get('description', '')[:500]}"""

    metadata = {
        'type': 'grant',
        'status': grant.get('status'),
        'amount': float(grant.get('amount', 0)) if grant.get('amount') else None,
        'close_date': grant.get('close_date'),
        'mount_isa_eligible': grant.get('mount_isa_eligible'),
        'focus_areas': grant.get('focus_areas', [])
    }

    return content, metadata

def chunk_organization(org):
    """Create searchable chunk for an organization"""
    content = f"""ORGANIZATION: {org.get('name', 'Unknown')}
Type: {org.get('entity_type', 'Unknown')}
Location: {org.get('postcode', 'Unknown')}
Indigenous owned: {'Yes' if org.get('indigenous_owned') else 'No'}
Services: {', '.join(org.get('service_types', []))}
Contact: {org.get('phone', '')} | {org.get('email', '')}"""

    metadata = {
        'type': 'organization',
        'entity_type': org.get('entity_type'),
        'indigenous_owned': org.get('indigenous_owned'),
        'postcode': org.get('postcode'),
        'service_types': org.get('service_types', [])
    }

    return content, metadata

def chunk_financial_record(fin, org_name):
    """Create searchable chunk for financial records"""
    content = f"""FINANCIALS: {org_name} ({fin.get('financial_year', 'Unknown')})
Revenue: ${fin.get('revenue', 0):,.2f}
Expenses: ${fin.get('expenses', 0):,.2f}
Net Position: ${fin.get('net_position', 0):,.2f}
Employees: {fin.get('employees_fte', 0)} FTE
Volunteers: {fin.get('volunteers_count', 0)}"""

    metadata = {
        'type': 'financial_record',
        'year': fin.get('financial_year'),
        'revenue': float(fin.get('revenue', 0)) if fin.get('revenue') else None,
        'employees': float(fin.get('employees_fte', 0)) if fin.get('employees_fte') else None
    }

    return content, metadata

def embed_table(table_name, chunk_function, org_name_field=None):
    """Generate embeddings for all records in a table"""
    print(f"📊 Processing {table_name}...")

    # Get all records
    result = supabase.table(table_name).select('*').execute()
    records = result.data

    if not records:
        print(f"   No records found in {table_name}\n")
        return

    print(f"   Found {len(records):,} records")

    # Check if embeddings already exist
    existing = supabase.table('document_embeddings').select('source_id').eq('source_table', table_name).execute()
    existing_ids = {e['source_id'] for e in existing.data} if existing.data else set()

    # Filter to only new records
    new_records = [r for r in records if r['id'] not in existing_ids]

    if not new_records:
        print(f"   All records already embedded\n")
        return

    print(f"   Generating {len(new_records):,} new embeddings...")

    embedded_count = 0
    errors = 0

    for record in tqdm(new_records, desc=f"   {table_name}"):
        try:
            # Get organization name if needed
            org_name = None
            if org_name_field and record.get(org_name_field):
                org_result = supabase.table('organizations').select('name').eq('id', record[org_name_field]).single().execute()
                org_name = org_result.data['name'] if org_result.data else 'Unknown'

            # Create chunk
            if org_name:
                content, metadata = chunk_function(record, org_name)
            else:
                content, metadata = chunk_function(record)

            # Generate embedding
            embedding = generate_embedding(content)

            # Store in database
            supabase.table('document_embeddings').insert({
                'source_table': table_name,
                'source_id': record['id'],
                'content': content,
                'metadata': metadata,
                'embedding': embedding,
                'chunk_type': 'full_text'
            }).execute()

            embedded_count += 1

            # Rate limiting - OpenAI has 3,000 RPM limit on tier 1
            time.sleep(0.02)  # ~50 requests/second, well under limit

        except Exception as e:
            errors += 1
            if errors < 5:  # Only show first few errors
                print(f"\n   ⚠️  Error: {e}")

    print(f"   ✅ Embedded {embedded_count:,} records ({errors} errors)\n")

def verify_embeddings():
    """Verify embeddings were generated successfully"""
    print("="*80)
    print("✅ VERIFYING EMBEDDINGS")
    print("="*80 + "\n")

    result = supabase.table('document_embeddings').select('source_table', count='exact').execute()

    if not result.data:
        print("   ⚠️  No embeddings found\n")
        return

    # Count by source table
    from collections import Counter
    counts = Counter(e['source_table'] for e in result.data)

    for table, count in sorted(counts.items()):
        print(f"   {table:25} {count:>10,} embeddings")

    print(f"\n   TOTAL: {sum(counts.values()):,} embeddings\n")

    # Test similarity search
    print("🔍 Testing similarity search...\n")

    test_embedding = generate_embedding("government contracts")

    result = supabase.rpc('match_documents', {
        'query_embedding': test_embedding,
        'match_threshold': 0.5,
        'match_count': 3
    }).execute()

    if result.data:
        print("   ✅ Similarity search working!")
        print(f"   Found {len(result.data)} matches:\n")
        for match in result.data[:3]:
            print(f"   • {match['source_table']}: {match['similarity']:.0%} similar")
            print(f"     {match['content'][:100]}...\n")
    else:
        print("   ⚠️  Similarity search returned no results")

    print()

# Generate embeddings for all tables
if __name__ == '__main__':
    embed_table('contracts', chunk_contract)
    embed_table('grants', chunk_grant)
    embed_table('organizations', chunk_organization)
    embed_table('financial_records', chunk_financial_record, org_name_field='organization_id')

    verify_embeddings()

    print("="*80)
    print("✅ EMBEDDINGS GENERATION COMPLETE")
    print("="*80 + "\n")

    print("Your economic data is now searchable via LLM!\n")
    print("Next steps:")
    print("  1. Test the chat interface: python3 scripts/chat_with_data.py")
    print("  2. Deploy Edge Functions for automated updates")
    print("  3. Build dashboard for community access\n")

    # Estimate cost
    result = supabase.table('document_embeddings').select('content', count='exact').execute()
    total_tokens = sum(len(e['content'].split()) * 1.3 for e in result.data) if result.data else 0  # ~1.3 tokens per word
    cost = (total_tokens / 1_000_000) * 0.02  # $0.02 per 1M tokens

    print(f"💰 Embedding cost estimate: ${cost:.4f}\n")
