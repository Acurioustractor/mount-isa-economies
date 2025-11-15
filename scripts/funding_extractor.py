"""
Multi-strategy funding amount extraction for Queensland government documents
"""
import re
from typing import Optional, Tuple, List
from decimal import Decimal


class FundingExtractor:
    """Extract funding amounts using multiple strategies with confidence scoring"""

    def __init__(self):
        self.strategies = [
            self.extract_from_structured_fields,
            self.extract_currency_patterns,
            self.extract_written_amounts,
            self.extract_from_tables,
        ]

    def extract(self, text: str, html: str = None, metadata: dict = None) -> Tuple[Optional[Decimal], float, str]:
        """
        Try multiple strategies to extract a funding amount.

        Returns:
            (amount, confidence_score, method_used)
            amount: Decimal in AUD
            confidence_score: 0.0 to 1.0
        """
        results = []

        for strategy in self.strategies:
            result = strategy(text, html, metadata)
            if result[0] is not None:  # If amount found
                amount, confidence, method = result
                # Validate the amount is reasonable
                if self._is_reasonable_amount(amount):
                    results.append((amount, confidence, method))

        # Return highest confidence result
        if results:
            results.sort(key=lambda x: x[1], reverse=True)
            return results[0]

        return None, 0.0, "none"

    def extract_all(self, text: str, html: str = None, metadata: dict = None) -> List[Tuple[Decimal, float, str]]:
        """Extract all funding amounts found (useful for documents with multiple amounts)"""
        results = []

        for strategy in self.strategies:
            result = strategy(text, html, metadata)
            if result[0] is not None:
                amount, confidence, method = result
                if self._is_reasonable_amount(amount):
                    results.append((amount, confidence, method))

        # Sort by confidence
        results.sort(key=lambda x: x[1], reverse=True)
        return results

    def extract_from_structured_fields(self, text: str, html: str = None, metadata: dict = None) -> Tuple[Optional[Decimal], float, str]:
        """Extract from metadata/structured fields (highest confidence)"""
        if not metadata:
            return None, 0.0, "structured_fields"

        amount_fields = ['amount', 'funding_amount', 'grant_amount', 'value', 'funding_value']
        for field in amount_fields:
            if field in metadata and metadata[field]:
                try:
                    amount = self._parse_amount_string(str(metadata[field]))
                    if amount:
                        return amount, 0.95, f"metadata.{field}"
                except:
                    continue

        return None, 0.0, "structured_fields"

    def extract_currency_patterns(self, text: str, html: str = None, metadata: dict = None) -> Tuple[Optional[Decimal], float, str]:
        """Extract using currency patterns (high confidence)"""
        if not text:
            return None, 0.0, "currency_patterns"

        # Patterns for Australian currency
        patterns = [
            # Labeled amounts (highest confidence)
            (r'(?:funding|grant|amount|value|worth|valued at|total)(?:\s+of)?[:\s]+\$\s*([\d,]+(?:\.\d{2})?)\s*(?:million|m\b)?',
             0.90, 'labeled_dollar_amount'),

            # $X million / $X.Y million
            (r'\$\s*([\d,]+(?:\.\d+)?)\s*(?:million|m\b)',
             0.85, 'dollar_million'),

            # $X,XXX,XXX or $X,XXX
            (r'\$\s*([\d,]+\.\d{2})\b',
             0.80, 'dollar_cents'),

            (r'\$\s*([\d,]+)\b',
             0.75, 'dollar_whole'),

            # X million dollars
            (r'\b([\d,]+(?:\.\d+)?)\s*million\s+dollars?',
             0.82, 'million_dollars'),

            # Written out amounts
            (r'(?:funding|grant|amount|value)[:\s]+(?:AUD\s*)?([\d,]+(?:\.\d{2})?)',
             0.78, 'labeled_numeric'),

            # Range patterns (take the maximum)
            (r'\$\s*([\d,]+(?:\.\d+)?)\s*(?:million|m\b)?\s*(?:to|[-–])\s*\$\s*([\d,]+(?:\.\d+)?)\s*(?:million|m\b)?',
             0.70, 'dollar_range'),
        ]

        for pattern, base_confidence, method in patterns:
            matches = list(re.finditer(pattern, text, re.IGNORECASE))
            if matches:
                # Take the first match (usually the main amount)
                match = matches[0]
                try:
                    amount = self._parse_matched_amount(match, pattern)
                    if amount:
                        return amount, base_confidence, f"currency.{method}"
                except:
                    continue

        return None, 0.0, "currency_patterns"

    def extract_written_amounts(self, text: str, html: str = None, metadata: dict = None) -> Tuple[Optional[Decimal], float, str]:
        """Extract amounts written in words"""
        if not text:
            return None, 0.0, "written_amounts"

        # Common written patterns in government documents
        written_numbers = {
            'one': 1, 'two': 2, 'three': 3, 'four': 4, 'five': 5,
            'six': 6, 'seven': 7, 'eight': 8, 'nine': 9, 'ten': 10,
            'eleven': 11, 'twelve': 12, 'thirteen': 13, 'fourteen': 14, 'fifteen': 15,
            'sixteen': 16, 'seventeen': 17, 'eighteen': 18, 'nineteen': 19, 'twenty': 20,
            'thirty': 30, 'forty': 40, 'fifty': 50, 'sixty': 60, 'seventy': 70,
            'eighty': 80, 'ninety': 90, 'hundred': 100, 'thousand': 1000, 'million': 1000000
        }

        # Pattern: "five hundred thousand dollars"
        pattern = r'\b((?:' + '|'.join(written_numbers.keys()) + r')(?:\s+(?:' + '|'.join(written_numbers.keys()) + r'))*)\s+dollars?\b'
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            words = match.group(1).lower().split()
            try:
                amount = self._words_to_number(words, written_numbers)
                if amount:
                    return Decimal(str(amount)), 0.65, "written_words"
            except:
                pass

        return None, 0.0, "written_amounts"

    def extract_from_tables(self, text: str, html: str = None, metadata: dict = None) -> Tuple[Optional[Decimal], float, str]:
        """Extract from tables (if HTML available)"""
        if not html:
            return None, 0.0, "tables"

        try:
            from bs4 import BeautifulSoup
            soup = BeautifulSoup(html, 'html.parser')

            # Look for tables
            tables = soup.find_all('table')
            for table in tables:
                # Look for cells with currency values
                cells = table.find_all(['td', 'th'])
                for cell in cells:
                    text_content = cell.get_text()
                    if '$' in text_content or 'amount' in text_content.lower():
                        amount_match = re.search(r'\$\s*([\d,]+(?:\.\d{2})?)', text_content)
                        if amount_match:
                            amount = self._parse_amount_string(amount_match.group(1))
                            if amount:
                                return amount, 0.75, "table_cell"

        except ImportError:
            pass
        except Exception:
            pass

        return None, 0.0, "tables"

    def _parse_matched_amount(self, match, pattern: str) -> Optional[Decimal]:
        """Parse amount from regex match"""
        if 'range' in pattern.lower():
            # For ranges, take the maximum (group 2)
            if len(match.groups()) >= 2:
                amount_str = match.group(2)
            else:
                amount_str = match.group(1)
        else:
            amount_str = match.group(1)

        # Check if it's in millions
        full_match = match.group(0)
        is_million = bool(re.search(r'million|m\b', full_match, re.IGNORECASE))

        # Parse the number
        amount = self._parse_amount_string(amount_str)

        if amount and is_million:
            amount = amount * Decimal('1000000')

        return amount

    def _parse_amount_string(self, amount_str: str) -> Optional[Decimal]:
        """Convert string like '1,234,567.89' to Decimal"""
        try:
            # Remove commas and spaces
            cleaned = amount_str.replace(',', '').replace(' ', '').strip()

            # Remove any currency symbols
            cleaned = cleaned.replace('$', '').replace('AUD', '')

            if cleaned:
                return Decimal(cleaned)
        except:
            pass

        return None

    def _words_to_number(self, words: List[str], word_values: dict) -> Optional[int]:
        """Convert written numbers to actual numbers"""
        total = 0
        current = 0

        for word in words:
            word = word.lower()
            if word not in word_values:
                continue

            value = word_values[word]

            if value >= 1000:
                current = current * value if current else value
                total += current
                current = 0
            elif value >= 100:
                current = current * value if current else value
            else:
                current += value

        return total + current if total or current else None

    def _is_reasonable_amount(self, amount: Decimal) -> bool:
        """Check if amount is reasonable for government funding"""
        if amount <= 0:
            return False

        # Queensland government grants typically range from $1,000 to $100 million
        # Allow wider range for safety
        if amount < Decimal('100'):  # Less than $100 is suspicious
            return False

        if amount > Decimal('1000000000'):  # More than $1 billion is suspicious for local grants
            return False

        return True


# Convenience function
def extract_funding_amount(text: str, html: str = None, metadata: dict = None) -> Tuple[Optional[Decimal], float, str]:
    """
    Extract funding amount from document using multiple strategies.

    Args:
        text: Plain text content of document
        html: HTML content (if available)
        metadata: Dictionary of metadata (if available)

    Returns:
        Tuple of (amount, confidence_score, extraction_method)

    Example:
        >>> amount, confidence, method = extract_funding_amount(document_text)
        >>> if confidence > 0.7:
        >>>     print(f"Found amount ${amount:,.2f} using {method} (confidence: {confidence})")
    """
    extractor = FundingExtractor()
    return extractor.extract(text, html, metadata)


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "Grant amount: $1,234,567.89",
        "Funding of $2.5 million",
        "This project is valued at $500,000",
        "Funding: $50K to $100K",
        "A grant worth five hundred thousand dollars",
        "Total value $1.2M announced today",
    ]

    extractor = FundingExtractor()
    for test in test_cases:
        amount, confidence, method = extractor.extract(test)
        if amount:
            print(f"Text: {test}")
            print(f"  → Amount: ${amount:,.2f}, Confidence: {confidence:.2f}, Method: {method}\n")
        else:
            print(f"Text: {test}")
            print(f"  → No amount found\n")
