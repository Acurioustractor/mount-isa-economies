"""Test inserting a single co-responder program"""
import os
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

# Test program - no notes field
test_program = {
    'title': 'Youth Co-Responder Team - Toowoomba',
    'url': 'https://statements.qld.gov.au/statements/97185',
    'statement_id': '97185_test',  # Different ID to avoid conflicts
    'published_date': '2023-02-16',
    'funding_amount_extracted': 15620000,
    'published_date_confidence': 0.95,
    'funding_confidence': 0.75,
    'full_text': 'Queensland Police Minister Mark Ryan announced the expansion of the Youth Co-Responder Program to Toowoomba.',
    'locations_mentioned': ['Toowoomba'],
    'lga_code': 'LGA37110',
    'categories': ['Community Safety', 'Youth Justice', 'Co-Responder', 'Police'],
    'source_type': 'State Budget',
    'source_organization': 'Queensland Police Service',
}

print("Test program keys:")
print(list(test_program.keys()))
print()
print("Has 'notes'?", 'notes' in test_program)
print()

# Connect to Supabase
url = os.getenv('SUPABASE_URL')
key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
supabase = create_client(url, key)

print("Attempting insert...")
try:
    result = supabase.table('documents').insert(test_program).execute()
    print("✅ Success!")
    print(f"Inserted ID: {result.data[0].get('id') if result.data else 'unknown'}")
except Exception as e:
    print(f"❌ Error: {e}")
