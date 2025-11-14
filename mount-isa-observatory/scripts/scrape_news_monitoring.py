"""
News Monitoring Scraper - Community Voice

Automatically monitors news sources for Mount Isa youth justice coverage.
Captures community voice, real stories, problems, and successes.

Sources:
- North West Star (local)
- ABC North West QLD (regional)
- NITV (Indigenous perspective)
- The Conversation (analysis)
- Guardian Australia (in-depth)

What it finds:
- Community quotes
- Success stories
- Problems/concerns
- Program mentions
- Funding discussions

Usage:
    python scripts/scrape_news_monitoring.py
    python scripts/scrape_news_monitoring.py --add-to-database
    python scripts/scrape_news_monitoring.py --days-back 30  # Last 30 days
"""

import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import requests
from bs4 import BeautifulSoup
import feedparser
from dotenv import load_dotenv

# Load environment
load_dotenv()


class NewsMonitor:
    """Monitor news sources for Mount Isa youth justice coverage"""

    def __init__(self):
        """Initialize news monitor"""
        self.keywords = [
            'mount isa youth',
            'mount isa justice',
            'mithangkaya nguli',
            'on-country',
            'youth co-responder',
            'mount isa crime',
            'northwest queensland youth'
        ]

        self.sources = {
            'abc_nw_qld': {
                'name': 'ABC North West Queensland',
                'rss': 'https://www.abc.net.au/news/feed/51120/rss.xml',
                'type': 'rss'
            },
            # Add more as available
        }

    def search_google_news(self, query: str, days_back: int = 7) -> List[Dict]:
        """
        Search Google News for relevant articles

        Args:
            query: Search query
            days_back: How many days to search back

        Returns:
            List of article dictionaries
        """
        print(f"\n🔍 Searching Google News: '{query}'")

        # Using RSS feed approach (Google News RSS)
        # Format: https://news.google.com/rss/search?q=query&hl=en-AU&gl=AU&ceid=AU:en
        rss_url = f"https://news.google.com/rss/search?q={query.replace(' ', '+')}&hl=en-AU&gl=AU&ceid=AU:en"

        try:
            feed = feedparser.parse(rss_url)

            articles = []
            cutoff_date = datetime.now() - timedelta(days=days_back)

            for entry in feed.entries:
                # Parse date
                if hasattr(entry, 'published_parsed'):
                    pub_date = datetime(*entry.published_parsed[:6])
                else:
                    pub_date = datetime.now()

                if pub_date < cutoff_date:
                    continue

                article = {
                    'title': entry.title,
                    'url': entry.link,
                    'published': pub_date.isoformat(),
                    'source': entry.source.title if hasattr(entry, 'source') else 'Google News',
                    'summary': entry.summary if hasattr(entry, 'summary') else ''
                }

                articles.append(article)
                print(f"  ✅ Found: {article['title'][:60]}... ({article['source']})")

            print(f"  Total found: {len(articles)}")
            return articles

        except Exception as e:
            print(f"  ❌ Error searching Google News: {e}")
            return []

    def analyze_article(self, article: Dict) -> Dict:
        """
        Analyze article for relevant information

        Args:
            article: Article dictionary

        Returns:
            Enhanced article with analysis
        """
        # Extract mentions
        text = f"{article['title']} {article.get('summary', '')}".lower()

        # Detect programs
        programs = []
        if 'on-country' in text or 'on country' in text:
            programs.append('On-Country Program')
        if 'co-responder' in text:
            programs.append('Youth Co-Responder Teams')
        if 'stronger communities' in text:
            programs.append('Stronger Communities')
        if 'pcyc' in text:
            programs.append('PCYC')

        # Detect organizations
        organizations = []
        if 'mithangkaya nguli' in text:
            organizations.append('Mithangkaya Nguli')
        if 'young people ahead' in text:
            organizations.append('Mithangkaya Nguli')

        # Detect funding mentions
        import re
        funding_pattern = r'\$[\d,]+(?:\.\d+)?\s*(?:million|m|billion|b)?'
        funding_mentions = re.findall(funding_pattern, text, re.IGNORECASE)

        # Classify type
        article_type = 'general'
        if any(word in text for word in ['success', 'achievement', 'reduction', 'improvement']):
            article_type = 'success_story'
        elif any(word in text for word in ['concern', 'problem', 'crisis', 'failure']):
            article_type = 'problem'
        elif any(word in text for word in ['announce', 'funding', 'budget', 'grant']):
            article_type = 'funding_announcement'
        elif any(word in text for word in ['outcome', 'result', 'data', 'report']):
            article_type = 'outcome_report'

        # Sentiment (basic)
        sentiment = 'neutral'
        positive_words = ['success', 'improve', 'reduction', 'achieve', 'positive', 'effective']
        negative_words = ['problem', 'concern', 'crisis', 'fail', 'increase', 'worsen']

        pos_count = sum(1 for word in positive_words if word in text)
        neg_count = sum(1 for word in negative_words if word in text)

        if pos_count > neg_count:
            sentiment = 'positive'
        elif neg_count > pos_count:
            sentiment = 'negative'

        # Add analysis
        article['programs_mentioned'] = programs
        article['organizations_mentioned'] = organizations
        article['funding_mentioned'] = funding_mentions
        article['article_type'] = article_type
        article['sentiment'] = sentiment

        return article

    def collect_news(self, days_back: int = 7) -> List[Dict]:
        """
        Collect news from all sources

        Args:
            days_back: How many days to search back

        Returns:
            List of analyzed articles
        """
        print("\n" + "=" * 80)
        print("📰 NEWS MONITORING - Mount Isa Youth Justice")
        print("=" * 80)

        all_articles = []

        # Search each keyword
        for keyword in self.keywords:
            articles = self.search_google_news(keyword, days_back=days_back)

            # Analyze each article
            for article in articles:
                analyzed = self.analyze_article(article)
                all_articles.append(analyzed)

        # Deduplicate by URL
        seen_urls = set()
        unique_articles = []
        for article in all_articles:
            if article['url'] not in seen_urls:
                seen_urls.add(article['url'])
                unique_articles.append(article)

        print("\n" + "=" * 80)
        print(f"📊 FOUND {len(unique_articles)} UNIQUE ARTICLES")
        print("=" * 80)

        # Summary by type
        types = {}
        for article in unique_articles:
            article_type = article['article_type']
            types[article_type] = types.get(article_type, 0) + 1

        print("\nBy type:")
        for article_type, count in types.items():
            print(f"  {article_type}: {count}")

        # Summary by sentiment
        sentiments = {}
        for article in unique_articles:
            sentiment = article['sentiment']
            sentiments[sentiment] = sentiments.get(sentiment, 0) + 1

        print("\nBy sentiment:")
        for sentiment, count in sentiments.items():
            print(f"  {sentiment}: {count}")

        return unique_articles

    def add_to_database(self, articles: List[Dict]):
        """
        Add articles to Supabase database

        Args:
            articles: List of analyzed articles
        """
        print("\n" + "=" * 80)
        print("💾 ADDING TO DATABASE")
        print("=" * 80)

        # Check if Supabase configured
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not supabase_url or not supabase_key:
            print("\n❌ Supabase not configured")
            return

        try:
            from supabase import create_client
            supabase = create_client(supabase_url, supabase_key)

            # Create news_articles table if it doesn't exist
            # (You'll need to add this to your schema)

            loaded = 0
            skipped = 0

            for article in articles:
                # Check if exists
                existing = supabase.table('news_articles') \
                    .select('id') \
                    .eq('url', article['url']) \
                    .execute()

                if existing.data:
                    print(f"  ⚠️  Already exists: {article['title'][:60]}...")
                    skipped += 1
                    continue

                # Insert
                news_article = {
                    'title': article['title'],
                    'url': article['url'],
                    'published_date': article['published'],
                    'source': article['source'],
                    'summary': article.get('summary', ''),
                    'article_type': article['article_type'],
                    'sentiment': article['sentiment'],
                    'programs_mentioned': article['programs_mentioned'],
                    'organizations_mentioned': article['organizations_mentioned'],
                    'funding_mentioned': article['funding_mentioned']
                }

                result = supabase.table('news_articles').insert(news_article).execute()

                if result.data:
                    print(f"  ✅ Added: {article['title'][:60]}...")
                    loaded += 1

            print("\n" + "=" * 80)
            print(f"✅ Loaded {loaded} articles")
            print(f"⚠️  Skipped {skipped} duplicates")
            print("=" * 80)

        except Exception as e:
            print(f"\n❌ Error: {e}")
            import traceback
            traceback.print_exc()

    def print_articles(self, articles: List[Dict], limit: int = 10):
        """
        Print articles summary

        Args:
            articles: List of articles
            limit: Max articles to print
        """
        print("\n" + "=" * 80)
        print("📰 RECENT ARTICLES")
        print("=" * 80)

        for i, article in enumerate(articles[:limit], 1):
            print(f"\n{i}. {article['title']}")
            print(f"   Source: {article['source']}")
            print(f"   Date: {article['published'][:10]}")
            print(f"   Type: {article['article_type']} | Sentiment: {article['sentiment']}")
            if article['programs_mentioned']:
                print(f"   Programs: {', '.join(article['programs_mentioned'])}")
            if article['organizations_mentioned']:
                print(f"   Organizations: {', '.join(article['organizations_mentioned'])}")
            if article['funding_mentioned']:
                print(f"   Funding: {', '.join(article['funding_mentioned'])}")
            print(f"   URL: {article['url']}")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Monitor news for Mount Isa youth justice')
    parser.add_argument('--days-back', type=int, default=7,
                       help='How many days to search back (default: 7)')
    parser.add_argument('--add-to-database', action='store_true',
                       help='Add articles to Supabase database')
    args = parser.parse_args()

    monitor = NewsMonitor()

    # Collect news
    articles = monitor.collect_news(days_back=args.days_back)

    # Print summary
    monitor.print_articles(articles)

    # Add to database if requested
    if args.add_to_database:
        monitor.add_to_database(articles)


if __name__ == '__main__':
    main()
