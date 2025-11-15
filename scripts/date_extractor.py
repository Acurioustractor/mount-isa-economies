"""
Multi-strategy date extraction for Queensland government documents
"""
import re
from datetime import datetime, timedelta
from typing import Optional, Tuple
import dateparser
from bs4 import BeautifulSoup


class DateExtractor:
    """Extract dates using multiple strategies with confidence scoring"""

    def __init__(self):
        self.strategies = [
            self.extract_from_metadata,
            self.extract_from_html_meta,
            self.extract_from_text_patterns,
            self.extract_with_dateparser,
        ]

    def extract(self, text: str, html: str = None, metadata: dict = None) -> Tuple[Optional[datetime], float, str]:
        """
        Try multiple strategies to extract a date.

        Returns:
            (date, confidence_score, method_used)
            confidence_score: 0.0 to 1.0
        """
        for strategy in self.strategies:
            result = strategy(text, html, metadata)
            if result[0]:  # If date found
                date, confidence, method = result
                # Validate the date is reasonable
                if self._is_reasonable_date(date):
                    return date, confidence, method

        return None, 0.0, "none"

    def extract_from_metadata(self, text: str, html: str = None, metadata: dict = None) -> Tuple[Optional[datetime], float, str]:
        """Extract from document metadata (highest confidence)"""
        if not metadata:
            return None, 0.0, "metadata"

        date_fields = ['published_date', 'date', 'publication_date', 'created_date', 'modified_date']
        for field in date_fields:
            if field in metadata and metadata[field]:
                try:
                    date = dateparser.parse(str(metadata[field]))
                    if date:
                        return date, 0.95, f"metadata.{field}"
                except:
                    continue

        return None, 0.0, "metadata"

    def extract_from_html_meta(self, text: str, html: str = None, metadata: dict = None) -> Tuple[Optional[datetime], float, str]:
        """Extract from HTML meta tags (high confidence)"""
        if not html:
            return None, 0.0, "html_meta"

        try:
            soup = BeautifulSoup(html, 'html.parser')

            # Try various meta tag patterns
            meta_patterns = [
                ('property', 'article:published_time'),
                ('property', 'og:published_time'),
                ('name', 'publish_date'),
                ('name', 'date'),
                ('name', 'DC.date'),
                ('itemprop', 'datePublished'),
            ]

            for attr, value in meta_patterns:
                tag = soup.find('meta', attrs={attr: value})
                if tag and tag.get('content'):
                    date = dateparser.parse(tag['content'])
                    if date:
                        return date, 0.90, f"html_meta.{value}"

            # Try time tags
            time_tag = soup.find('time', attrs={'datetime': True})
            if time_tag:
                date = dateparser.parse(time_tag['datetime'])
                if date:
                    return date, 0.85, "html_time_tag"

        except Exception as e:
            pass

        return None, 0.0, "html_meta"

    def extract_from_text_patterns(self, text: str, html: str = None, metadata: dict = None) -> Tuple[Optional[datetime], float, str]:
        """Extract using regex patterns (medium confidence)"""
        if not text:
            return None, 0.0, "text_patterns"

        # Australian date patterns common in Queensland government docs
        patterns = [
            # DD Month YYYY or D Month YYYY
            (r'\b(\d{1,2})\s+(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{4})\b',
             0.80, 'text.day_month_year'),

            # DD/MM/YYYY or D/M/YYYY
            (r'\b(\d{1,2})/(\d{1,2})/(\d{4})\b',
             0.70, 'text.dd_mm_yyyy'),

            # YYYY-MM-DD (ISO format)
            (r'\b(\d{4})-(\d{2})-(\d{2})\b',
             0.75, 'text.iso_date'),

            # Month DD, YYYY
            (r'\b(January|February|March|April|May|June|July|August|September|October|November|December)\s+(\d{1,2}),?\s+(\d{4})\b',
             0.78, 'text.month_day_year'),

            # Common patterns in government docs
            (r'(?:Published|Updated|Released|Date):\s*(\d{1,2}[/-]\d{1,2}[/-]\d{4})',
             0.85, 'text.labeled_date'),
        ]

        for pattern, confidence, method in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    date = dateparser.parse(match.group(0))
                    if date:
                        return date, confidence, method
                except:
                    continue

        return None, 0.0, "text_patterns"

    def extract_with_dateparser(self, text: str, html: str = None, metadata: dict = None) -> Tuple[Optional[datetime], float, str]:
        """Use dateparser library as fallback (lower confidence)"""
        if not text:
            return None, 0.0, "dateparser"

        # Try to find dates in first 2000 characters (where metadata usually is)
        sample = text[:2000]

        # Look for sentences with date indicators
        date_keywords = [
            'published', 'released', 'updated', 'announced',
            'date', 'as of', 'effective', 'issued'
        ]

        for keyword in date_keywords:
            pattern = rf'{keyword}[:\s]+([^\n]+?)(?:\.|$)'
            match = re.search(pattern, sample, re.IGNORECASE)
            if match:
                date = dateparser.parse(match.group(1), settings={
                    'PREFER_DAY_OF_MONTH': 'first',
                    'PREFER_DATES_FROM': 'past'
                })
                if date:
                    return date, 0.60, f"dateparser.{keyword}"

        return None, 0.0, "dateparser"

    def _is_reasonable_date(self, date: datetime) -> bool:
        """Check if date is reasonable for Queensland government documents"""
        now = datetime.now()

        # Not in the future (allow up to 7 days for timezones/scheduling)
        if date > now + timedelta(days=7):
            return False

        # Not before 2000 (modern digital documents)
        if date.year < 2000:
            return False

        # Not too old (most relevant docs from last 20 years)
        if date < now - timedelta(days=365*20):
            return False

        return True


# Convenience function
def extract_date(text: str, html: str = None, metadata: dict = None) -> Tuple[Optional[datetime], float, str]:
    """
    Extract date from document using multiple strategies.

    Args:
        text: Plain text content of document
        html: HTML content (if available)
        metadata: Dictionary of metadata (if available)

    Returns:
        Tuple of (date, confidence_score, extraction_method)

    Example:
        >>> date, confidence, method = extract_date(document_text, html, metadata)
        >>> if confidence > 0.7:
        >>>     print(f"Found date {date} using {method} (confidence: {confidence})")
    """
    extractor = DateExtractor()
    return extractor.extract(text, html, metadata)


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "Published: 15 March 2024",
        "This grant was announced on 23/06/2023",
        "Released: 2024-01-15",
        "Date: March 15, 2024",
        "Updated 15/3/2024 by Queensland Government",
    ]

    extractor = DateExtractor()
    for test in test_cases:
        date, confidence, method = extractor.extract(test)
        print(f"Text: {test}")
        print(f"  → Date: {date}, Confidence: {confidence:.2f}, Method: {method}\n")
