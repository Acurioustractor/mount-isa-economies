"""
Chat with Mount Isa Economic Data via LLM
Uses RAG (Retrieval Augmented Generation) to answer questions about the local economy
"""

import os
from supabase import create_client, Client
import openai
from typing import List, Dict

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

SYSTEM_PROMPT = """You are an economic analyst helping the Mount Isa community understand their economy.

Your role:
- Provide clear, actionable insights about economic data
- Highlight funding opportunities and government contracts
- Frame everything in terms of community benefit
- Respect cultural values and community priorities
- Always cite specific data sources (contracts, grants, organizations)
- Use exact numbers and dates when available

When discussing money:
- Put numbers in context (e.g., "$500K is enough to employ 5 full-time staff")
- Identify patterns and opportunities
- Note if funding favors certain types of organizations

When discussing organizations:
- Highlight indigenous-owned and community-aligned businesses
- Show connections between funding, contracts, and local impact
- Identify gaps or underserved areas

Be helpful, respectful, and focused on empowering community decision-making.
"""

def generate_embedding(text: str) -> List[float]:
    """Generate OpenAI embedding for text"""
    response = openai.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def search_economic_data(question: str, filters: Dict = None, limit: int = 10) -> List[Dict]:
    """Search economic data using vector similarity"""

    # Generate embedding for question
    question_embedding = generate_embedding(question)

    # Call Supabase RPC function for similarity search
    result = supabase.rpc(
        'match_documents',
        {
            'query_embedding': question_embedding,
            'match_threshold': 0.7,
            'match_count': limit,
            'filter_metadata': filters or {}
        }
    ).execute()

    return result.data if result.data else []

def format_context(matches: List[Dict]) -> str:
    """Format search results into context for LLM"""
    if not matches:
        return "No relevant data found."

    context_parts = []

    for i, match in enumerate(matches, 1):
        context_parts.append(f"[Source {i}] {match['source_table']}")
        context_parts.append(match['content'])
        context_parts.append(f"Relevance: {match['similarity']:.0%}")
        context_parts.append("")

    return "\n".join(context_parts)

def chat(question: str, filters: Dict = None) -> str:
    """Answer a question about Mount Isa economic data"""

    print(f"\n💭 Question: {question}\n")
    print("🔍 Searching economic data...")

    # Search for relevant data
    matches = search_economic_data(question, filters, limit=15)

    if not matches:
        return "I couldn't find any relevant data to answer that question. Try asking about contracts, grants, organizations, or funding."

    print(f"✅ Found {len(matches)} relevant sources\n")
    print("🤖 Generating answer...\n")

    # Format context
    context = format_context(matches)

    # Call OpenAI for answer
    response = openai.chat.completions.create(
        model="gpt-4-turbo-preview",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Context from Mount Isa economic database:\n\n{context}\n\nQuestion: {question}"}
        ],
        temperature=0.7,
        max_tokens=1000
    )

    answer = response.choices[0].message.content

    # Add source count
    answer += f"\n\n📊 Based on {len(matches)} data sources from the economic observatory."

    return answer

def interactive_mode():
    """Run interactive chat session"""
    print("\n" + "="*80)
    print("💬 MOUNT ISA ECONOMIC OBSERVATORY - CHAT INTERFACE")
    print("="*80 + "\n")

    print("Ask questions about:")
    print("  • Government contracts in Mount Isa")
    print("  • Grant opportunities for local organizations")
    print("  • Economic flows and funding patterns")
    print("  • Organizations and their financial data")
    print("  • Community concerns and priorities\n")

    print("Example questions:")
    print("  - What grant opportunities are open for indigenous businesses?")
    print("  - Show me government contracts over $100,000 in Mount Isa")
    print("  - Which organizations received the most funding last year?")
    print("  - What do community members say about employment?\n")

    print("Type 'exit' or 'quit' to end\n")
    print("="*80 + "\n")

    while True:
        try:
            question = input("You: ").strip()

            if not question:
                continue

            if question.lower() in ['exit', 'quit', 'q']:
                print("\n👋 Thank you for using the Economic Observatory!\n")
                break

            # Determine filters based on question
            filters = {}

            if 'open' in question.lower() or 'opportunity' in question.lower():
                filters = {'status': 'open'}

            if 'indigenous' in question.lower():
                filters = {**filters, 'indigenous_owned': True}

            # Get answer
            answer = chat(question, filters)

            print(f"\n🤖 Answer:\n{answer}\n")
            print("-"*80 + "\n")

        except KeyboardInterrupt:
            print("\n\n👋 Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}\n")

# Example queries
def run_examples():
    """Run example queries"""
    print("\n" + "="*80)
    print("📊 RUNNING EXAMPLE QUERIES")
    print("="*80 + "\n")

    examples = [
        "What are the largest government contracts in Mount Isa in the last year?",
        "Show me grant opportunities available right now",
        "Which local organizations are indigenous-owned?",
        "What funding has been announced by the Queensland Parliament for Mount Isa?"
    ]

    for question in examples:
        print(f"\n{'='*80}")
        answer = chat(question)
        print(f"\n{answer}\n")
        print("="*80 + "\n")
        input("Press Enter for next question...")

if __name__ == '__main__':
    import sys

    if len(sys.argv) > 1:
        if sys.argv[1] == 'examples':
            run_examples()
        else:
            # Answer single question from command line
            question = ' '.join(sys.argv[1:])
            answer = chat(question)
            print(f"\n{answer}\n")
    else:
        interactive_mode()
