"""
Data validation framework for Queensland government documents
"""
from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Dict, Any, Optional
import hashlib


class ValidationWarning:
    """Represents a validation warning"""

    def __init__(self, severity: str, field: str, message: str, value: Any = None):
        self.severity = severity  # 'error', 'warning', 'info'
        self.field = field
        self.message = message
        self.value = value

    def to_dict(self) -> dict:
        return {
            'severity': self.severity,
            'field': self.field,
            'message': self.message,
            'value': str(self.value) if self.value is not None else None
        }


class DocumentValidator:
    """Validate scraped documents and flag quality issues"""

    def __init__(self):
        self.warnings = []

    def validate(self, document: Dict[str, Any]) -> List[ValidationWarning]:
        """
        Run all validation rules on a document.

        Args:
            document: Dictionary with document fields

        Returns:
            List of ValidationWarning objects
        """
        self.warnings = []

        # Run all validation checks
        self._validate_required_fields(document)
        self._validate_date(document)
        self._validate_funding_amount(document)
        self._validate_location(document)
        self._validate_confidence_scores(document)
        self._validate_categorization(document)
        self._validate_source_tracking(document)
        self._check_duplicate_detection(document)

        return self.warnings

    def _add_warning(self, severity: str, field: str, message: str, value: Any = None):
        """Helper to add a warning"""
        self.warnings.append(ValidationWarning(severity, field, message, value))

    def _validate_required_fields(self, doc: Dict[str, Any]):
        """Check required fields are present"""
        required_fields = ['title', 'url', 'source_system']

        for field in required_fields:
            if not doc.get(field):
                self._add_warning('error', field, f"Required field '{field}' is missing")

        # At least one of content or html should be present
        if not doc.get('content') and not doc.get('html'):
            self._add_warning('error', 'content', "Document has no content or HTML")

    def _validate_date(self, doc: Dict[str, Any]):
        """Validate date field"""
        date = doc.get('date')
        confidence = doc.get('date_confidence')

        if not date:
            self._add_warning('warning', 'date', "No date extracted from document")
            return

        # Check if date is a datetime object or string
        if isinstance(date, str):
            try:
                date = datetime.fromisoformat(date.replace('Z', '+00:00'))
            except:
                self._add_warning('error', 'date', f"Invalid date format: {date}", date)
                return

        now = datetime.now()

        # Future date check (allow 7 days for timezone differences)
        if date > now + timedelta(days=7):
            self._add_warning('error', 'date', f"Date is in the future: {date}", date)

        # Very old date check
        if date.year < 2000:
            self._add_warning('warning', 'date', f"Date is before 2000: {date}", date)

        # Check if date is exactly today (likely a fallback)
        if date.date() == now.date():
            self._add_warning('warning', 'date', "Date is exactly today - may be fallback default", date)

        # Low confidence warning
        if confidence is not None and confidence < 0.7:
            self._add_warning('info', 'date_confidence',
                            f"Low confidence on date extraction: {confidence:.2f}",
                            confidence)

    def _validate_funding_amount(self, doc: Dict[str, Any]):
        """Validate funding amount"""
        amount = doc.get('funding_amount')
        confidence = doc.get('funding_confidence')
        title = doc.get('title', '').lower()

        # Check if document appears to be about funding but has no amount
        funding_keywords = ['grant', 'funding', 'award', 'investment', 'allocated', '$', 'million']
        appears_to_be_funding = any(keyword in title for keyword in funding_keywords)

        if not amount:
            if appears_to_be_funding:
                self._add_warning('warning', 'funding_amount',
                                "Document appears to be about funding but no amount extracted")
            return

        # Convert to Decimal if needed
        if isinstance(amount, (int, float, str)):
            try:
                amount = Decimal(str(amount))
            except:
                self._add_warning('error', 'funding_amount', f"Invalid amount format: {amount}", amount)
                return

        # Suspiciously small amounts
        if amount < Decimal('100'):
            self._add_warning('warning', 'funding_amount',
                            f"Amount is very small: ${amount:,.2f}", amount)

        # Suspiciously large amounts
        if amount > Decimal('100000000'):  # $100 million
            self._add_warning('warning', 'funding_amount',
                            f"Amount is very large: ${amount:,.2f} - verify accuracy", amount)

        # Very large amounts for local grants
        if amount > Decimal('1000000000'):  # $1 billion
            self._add_warning('error', 'funding_amount',
                            f"Amount exceeds $1 billion: ${amount:,.2f} - likely extraction error", amount)

        # Low confidence warning
        if confidence is not None and confidence < 0.7:
            self._add_warning('info', 'funding_confidence',
                            f"Low confidence on funding extraction: {confidence:.2f}",
                            confidence)

        # Round number check (might indicate estimate vs actual)
        if amount % Decimal('1000000') == 0:  # Exact millions
            self._add_warning('info', 'funding_amount',
                            f"Amount is round number (${amount:,.0f}) - may be estimate", amount)

    def _validate_location(self, doc: Dict[str, Any]):
        """Validate location fields"""
        location = doc.get('location')
        lga_code = doc.get('lga_code')
        confidence = doc.get('location_confidence')

        if not location:
            self._add_warning('warning', 'location', "No location extracted from document")
            return

        # Known Queensland locations (partial list)
        known_qld_locations = [
            'mount isa', 'townsville', 'cairns', 'brisbane', 'gold coast',
            'torres strait', 'palm island', 'doomadgee', 'burketown',
            'north queensland', 'central queensland', 'logan', 'ipswich'
        ]

        location_lower = location.lower()
        is_known = any(known in location_lower for known in known_qld_locations)

        if not is_known:
            self._add_warning('info', 'location',
                            f"Location '{location}' not in known Queensland locations list")

        # Check LGA code format if present
        if lga_code and not lga_code.startswith('LGA'):
            self._add_warning('warning', 'lga_code',
                            f"LGA code '{lga_code}' doesn't match expected format (LGAXXXXX)")

        # Mount Isa specific check (LGA35300)
        if 'mount isa' in location_lower and lga_code != 'LGA35300':
            self._add_warning('warning', 'lga_code',
                            f"Mount Isa location should have LGA code LGA35300, got: {lga_code}")

        # Low confidence warning
        if confidence is not None and confidence < 0.7:
            self._add_warning('info', 'location_confidence',
                            f"Low confidence on location extraction: {confidence:.2f}",
                            confidence)

    def _validate_confidence_scores(self, doc: Dict[str, Any]):
        """Validate confidence scores are in valid range"""
        confidence_fields = [
            'date_confidence',
            'funding_confidence',
            'location_confidence',
            'categorization_confidence'
        ]

        for field in confidence_fields:
            confidence = doc.get(field)
            if confidence is not None:
                try:
                    confidence = float(confidence)
                    if not (0.0 <= confidence <= 1.0):
                        self._add_warning('error', field,
                                        f"Confidence score must be between 0 and 1, got: {confidence}",
                                        confidence)
                except (ValueError, TypeError):
                    self._add_warning('error', field,
                                    f"Confidence score must be numeric, got: {confidence}",
                                    confidence)

    def _validate_categorization(self, doc: Dict[str, Any]):
        """Validate categorization fields"""
        valid_program_types = ['MBS', 'PBS', 'grant', 'procurement', 'other']
        valid_payer_types = ['Commonwealth', 'State', 'LGA', 'Household', 'Business']
        valid_payee_types = ['Local business', 'External business', 'Household', 'Charity']

        program_type = doc.get('program_type')
        if program_type and program_type not in valid_program_types:
            self._add_warning('warning', 'program_type',
                            f"Invalid program_type: {program_type}. Expected one of: {valid_program_types}",
                            program_type)

        payer_type = doc.get('payer_type')
        if payer_type and payer_type not in valid_payer_types:
            self._add_warning('warning', 'payer_type',
                            f"Invalid payer_type: {payer_type}. Expected one of: {valid_payer_types}",
                            payer_type)

        payee_type = doc.get('payee_type')
        if payee_type and payee_type not in valid_payee_types:
            self._add_warning('warning', 'payee_type',
                            f"Invalid payee_type: {payee_type}. Expected one of: {valid_payee_types}",
                            payee_type)

    def _validate_source_tracking(self, doc: Dict[str, Any]):
        """Validate source tracking fields"""
        source_system = doc.get('source_system')
        source_url = doc.get('source_url')
        url = doc.get('url')

        if not source_system:
            self._add_warning('error', 'source_system', "source_system is required for tracking")

        # URL should be valid
        if url and not (url.startswith('http://') or url.startswith('https://')):
            self._add_warning('warning', 'url', f"URL doesn't start with http:// or https://: {url}", url)

    def _check_duplicate_detection(self, doc: Dict[str, Any]):
        """Generate checksum for duplicate detection"""
        content = doc.get('content', '')
        url = doc.get('url', '')

        if content:
            # Generate checksum from content
            checksum = hashlib.md5(content.encode('utf-8')).hexdigest()
            doc['checksum'] = checksum
        elif url:
            # Use URL as fallback
            checksum = hashlib.md5(url.encode('utf-8')).hexdigest()
            doc['checksum'] = checksum
        else:
            self._add_warning('warning', 'checksum', "Cannot generate checksum - no content or URL")

    def needs_review(self) -> bool:
        """Check if document should be flagged for manual review"""
        # Flag for review if there are any errors or multiple warnings
        error_count = sum(1 for w in self.warnings if w.severity == 'error')
        warning_count = sum(1 for w in self.warnings if w.severity == 'warning')

        return error_count > 0 or warning_count >= 3


def validate_document(document: Dict[str, Any]) -> tuple[List[ValidationWarning], bool]:
    """
    Convenience function to validate a document.

    Args:
        document: Dictionary with document fields

    Returns:
        Tuple of (warnings_list, needs_review_flag)

    Example:
        >>> doc = {'title': 'Grant announcement', 'date': '2024-03-15', ...}
        >>> warnings, needs_review = validate_document(doc)
        >>> if needs_review:
        >>>     print("Document flagged for review:")
        >>>     for warning in warnings:
        >>>         print(f"  {warning.severity}: {warning.message}")
    """
    validator = DocumentValidator()
    warnings = validator.validate(document)
    needs_review = validator.needs_review()

    # Add needs_review flag to document
    document['needs_review'] = needs_review

    # Add warnings as JSON
    if warnings:
        document['validation_warnings'] = [w.to_dict() for w in warnings]

    return warnings, needs_review


if __name__ == "__main__":
    # Test validation
    test_doc = {
        'title': 'Test Grant Announcement',
        'url': 'https://example.gov.au/grant',
        'source_system': 'test_scraper',
        'content': 'This is a test document about a grant.',
        'date': datetime(2024, 3, 15),
        'date_confidence': 0.85,
        'funding_amount': Decimal('500000'),
        'funding_confidence': 0.90,
        'location': 'Mount Isa',
        'lga_code': 'LGA35300',
        'location_confidence': 0.95,
    }

    warnings, needs_review = validate_document(test_doc)

    print(f"Validation complete: {len(warnings)} warnings")
    print(f"Needs review: {needs_review}")
    print("\nWarnings:")
    for w in warnings:
        print(f"  [{w.severity.upper()}] {w.field}: {w.message}")
