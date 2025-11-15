"""
Verify ACNC Payment for Mithangkaya Nguli

Checks ACNC financial reports to verify if the $24M On-Country funding was received.

ACNC Charity: Mithangkaya Nguli – Young People Ahead Youth and Community Services
ABN: 82 673 830 363
Charity ID: 6d8c8e4a-ea6e-e811-a95f-000d3ad24077

Expected Payment: $24M (announced July 2024)
Expected in: 2024-25 Financial Year report

Usage:
    python scripts/verify_acnc_payment.py
    python scripts/verify_acnc_payment.py --add-to-database  # Add verified payment to Supabase
"""

import os
import sys
import requests
from pathlib import Path
from typing import Optional, Dict
from datetime import datetime
from dotenv import load_dotenv

# Load environment
load_dotenv()


class ACNCPaymentVerifier:
    """Verify payments in ACNC charity financial reports"""

    def __init__(self):
        """Initialize ACNC verifier"""
        self.base_url = "https://www.acnc.gov.au"

        # Mithangkaya Nguli details
        self.charity_name = "Mithangkaya Nguli – Young People Ahead Youth and Community Services Indigenous Corporation"
        self.abn = "82673830363"
        self.charity_id = "6d8c8e4a-ea6e-e811-a95f-000d3ad24077"

        # Expected payment
        self.expected_amount = 24_000_000
        self.program_name = "Intensive On-Country Program"
        self.announcement_date = "2024-07-23"

    def get_acnc_data_url(self) -> str:
        """
        Get ACNC charity page URL

        Returns:
            URL to charity page
        """
        # ACNC charity page
        return f"{self.base_url}/charity/charities/{self.charity_id}/documents"

    def manual_verification_guide(self):
        """
        Print manual verification guide for user to follow
        """
        print("\n" + "=" * 80)
        print("📋 MANUAL VERIFICATION GUIDE - ACNC Financial Reports")
        print("=" * 80)

        print(f"\n🎯 Target Charity: {self.charity_name}")
        print(f"   ABN: {self.abn}")
        print(f"   Expected Payment: ${self.expected_amount:,}")
        print(f"   Program: {self.program_name}")
        print(f"   Announced: {self.announcement_date}")

        print("\n" + "=" * 80)
        print("📥 STEP 1: Download Financial Reports")
        print("=" * 80)

        acnc_url = self.get_acnc_data_url()
        print(f"\n1. Go to: {acnc_url}")
        print("\n2. Look for documents:")
        print("   - 2024 Annual Information Statement (AIS)")
        print("   - 2025 Annual Information Statement (if available)")
        print("   - Financial statements 2024-25")

        print("\n3. Download the most recent:")
        print("   - Annual Information Statement")
        print("   - Financial statements (if separate)")

        print("\n" + "=" * 80)
        print("🔍 STEP 2: Check for $24M Payment")
        print("=" * 80)

        print("\n📊 What to look for in the AIS:")

        print("\n1. **Total Revenue** (Question 15 or similar)")
        print("   Expected: ~$24M or higher if payment received")
        print("   Previous years: Check historical revenue for comparison")

        print("\n2. **Government Grants** (Question 17 or similar)")
        print("   Look for:")
        print("   - Queensland Government grants")
        print("   - Youth Justice Department")
        print("   - On-Country Program")
        print("   - Amount: $24M or similar")

        print("\n3. **Cash Flow Statement**")
        print("   - Receipts from government")
        print("   - Large increases in 2024-25")

        print("\n4. **Notes to Financial Statements**")
        print("   - Grant income")
        print("   - Conditional vs unconditional grants")
        print("   - Multi-year grant arrangements")

        print("\n" + "=" * 80)
        print("✅ STEP 3: Record Your Findings")
        print("=" * 80)

        print("\nRecord the following:")
        print("  1. Total revenue reported:")
        print("  2. Government grants total:")
        print("  3. Specific On-Country grant (if listed separately):")
        print("  4. Financial year:")
        print("  5. Document date:")

        print("\n" + "=" * 80)
        print("💾 STEP 4: Add to Database")
        print("=" * 80)

        print("\nIf you found the $24M payment, run:")
        print("  python scripts/verify_acnc_payment.py --add-to-database")
        print("\nYou'll be prompted to enter:")
        print("  - Amount received")
        print("  - Payment date (approximate)")
        print("  - Source document (AIS year)")

        print("\n" + "=" * 80)
        print("🔗 USEFUL LINKS")
        print("=" * 80)

        print(f"\nACNC Charity Search: https://www.acnc.gov.au/charity")
        print(f"Direct Link: {acnc_url}")
        print(f"ABN Lookup: https://abr.business.gov.au/ABN/View?abn={self.abn}")

        print("\n" + "=" * 80)
        print("📝 NOTES")
        print("=" * 80)

        print("\n- ACNC reports are usually 6-12 months delayed")
        print("- 2024-25 reports may not be available until late 2025")
        print("- Check both 2024 and 2025 AIS when available")
        print("- Large grants often have conditions and payment schedules")
        print("- May be paid in installments over multiple years")

        print("\n" + "=" * 80)

    def add_payment_to_database_interactive(self):
        """
        Interactive prompt to add verified payment to database
        """
        print("\n" + "=" * 80)
        print("💾 ADD VERIFIED PAYMENT TO DATABASE")
        print("=" * 80)

        # Check if Supabase is configured
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not supabase_url or not supabase_key:
            print("\n❌ Supabase not configured.")
            print("   Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY in .env")
            return

        print("\nDid you find the $24M payment in ACNC reports? (y/n): ", end='')
        found = input().strip().lower()

        if found != 'y':
            print("\n⚠️  Payment not found or not verified. Database not updated.")
            print("\nNext steps:")
            print("  1. Wait for 2024-25 AIS to be published")
            print("  2. Check again in 3-6 months")
            print("  3. Consider FOI request for payment confirmation")
            return

        print("\n" + "=" * 80)
        print("📝 ENTER PAYMENT DETAILS")
        print("=" * 80)

        # Get payment details
        print("\n1. Amount received (in dollars, e.g., 24000000): $", end='')
        amount = float(input().strip().replace(',', ''))

        print("\n2. Payment date (YYYY-MM-DD, approximate if not exact): ", end='')
        payment_date = input().strip()

        print("\n3. Financial year (e.g., 2024-25): ", end='')
        financial_year = input().strip()

        print("\n4. Source document (e.g., '2024 AIS', '2025 Financial Statements'): ", end='')
        source_doc = input().strip()

        print("\n5. Additional notes (optional): ", end='')
        notes = input().strip()

        # Confirm
        print("\n" + "=" * 80)
        print("CONFIRM DETAILS")
        print("=" * 80)
        print(f"\nOrganization: {self.charity_name}")
        print(f"Program: {self.program_name}")
        print(f"Amount: ${amount:,.2f}")
        print(f"Payment Date: {payment_date}")
        print(f"Financial Year: {financial_year}")
        print(f"Source: {source_doc}")
        if notes:
            print(f"Notes: {notes}")

        print("\nAdd to database? (y/n): ", end='')
        confirm = input().strip().lower()

        if confirm != 'y':
            print("\n❌ Cancelled. Database not updated.")
            return

        # Add to database
        try:
            from supabase import create_client

            supabase = create_client(supabase_url, supabase_key)

            # Get organization IDs
            qld_gov = supabase.table('organizations') \
                .select('id') \
                .eq('name', 'Queensland Government') \
                .execute()

            mithangkaya = supabase.table('organizations') \
                .select('id') \
                .ilike('name', f'%{self.charity_name[:20]}%') \
                .execute()

            if not qld_gov.data or not mithangkaya.data:
                print("\n❌ Organizations not found in database")
                return

            qld_gov_id = qld_gov.data[0]['id']
            mithangkaya_id = mithangkaya.data[0]['id']

            # Get program and announcement IDs
            program = supabase.table('programs') \
                .select('id') \
                .eq('name', self.program_name) \
                .execute()

            if not program.data:
                print(f"\n❌ Program '{self.program_name}' not found")
                return

            program_id = program.data[0]['id']

            # Get announcement
            announcement = supabase.table('funding_announcements') \
                .select('id') \
                .eq('program_id', program_id) \
                .execute()

            announcement_id = announcement.data[0]['id'] if announcement.data else None

            # Create document
            doc = {
                'document_type': 'ACNC Annual Information Statement',
                'title': f"{self.charity_name} - {source_doc}",
                'publication_date': payment_date,
                'document_identifier': f"ACNC_{financial_year}_{self.abn}"
            }

            doc_result = supabase.table('documents').insert(doc).execute()
            doc_id = doc_result.data[0]['id'] if doc_result.data else None

            # Create actual payment
            payment = {
                'announcement_id': announcement_id,
                'program_id': program_id,
                'payer_org_id': qld_gov_id,
                'payee_org_id': mithangkaya_id,
                'amount_paid': amount,
                'payment_date': payment_date,
                'financial_year': financial_year,
                'payment_type': 'Grant',
                'payment_description': f"On-Country Program payment verified via {source_doc}",
                'source_document_id': doc_id,
                'confidence_score': 5  # Highest - verified in ACNC report
            }

            if notes:
                payment['payment_description'] += f" - {notes}"

            result = supabase.table('actual_payments').insert(payment).execute()

            print("\n" + "=" * 80)
            print("✅ PAYMENT VERIFIED AND ADDED TO DATABASE")
            print("=" * 80)

            print(f"\nPayment ID: {result.data[0]['id']}")
            print(f"Amount: ${amount:,.2f}")
            print(f"Confidence Score: 5/5 (ACNC verified)")
            print(f"Status: Payment verified in official financial reports")

            print("\n🎯 What this means:")
            print("  ✅ The $24M announcement has been VERIFIED")
            print("  ✅ Money actually flowed to Mithangkaya Nguli")
            print("  ✅ Can now track: Announcement → Budget → Payment ✓")

            print("\n📊 Next steps:")
            print("  1. Regenerate visualizations to show verified payment")
            print("  2. Update gap analysis (one less gap!)")
            print("  3. Add to your JusticeHub platform as verified data")

        except Exception as e:
            print(f"\n❌ Error adding to database: {e}")
            import traceback
            traceback.print_exc()


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Verify ACNC payment for Mithangkaya Nguli')
    parser.add_argument('--add-to-database', action='store_true',
                       help='Interactive prompt to add verified payment to database')
    args = parser.parse_args()

    verifier = ACNCPaymentVerifier()

    if args.add_to_database:
        verifier.add_payment_to_database_interactive()
    else:
        verifier.manual_verification_guide()


if __name__ == '__main__':
    main()
