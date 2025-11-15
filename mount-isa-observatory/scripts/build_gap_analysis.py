"""
Gap Analysis Visualization - Funding Accountability

Shows the gap between:
- What was ANNOUNCED (media statements)
- What was BUDGETED (budget papers)
- What was PAID (ACNC reports, contracts)

This is the accountability layer - where did the money go?

Usage:
    python scripts/build_gap_analysis.py
    python scripts/build_gap_analysis.py --output html  # Save visualization
    python scripts/build_gap_analysis.py --mount-isa-only  # Mount Isa specific only
"""

import os
import sys
from pathlib import Path
from typing import Dict, List
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from dotenv import load_dotenv

# Load environment
load_dotenv()


class GapAnalyzer:
    """Analyze gaps in funding flow from announcement to payment"""

    def __init__(self, data_source='supabase'):
        """
        Initialize gap analyzer

        Args:
            data_source: 'supabase' or 'csv'
        """
        self.data_source = data_source
        self.output_dir = Path(__file__).parent.parent / 'visualizations'
        self.output_dir.mkdir(exist_ok=True)

        if data_source == 'supabase':
            self._init_supabase()
        else:
            raise ValueError("CSV source not yet supported for gap analysis. Use supabase.")

    def _init_supabase(self):
        """Initialize Supabase connection"""
        try:
            from supabase import create_client
        except ImportError:
            print("❌ Supabase not installed. Run: pip install supabase")
            sys.exit(1)

        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("❌ SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY must be set")

        self.supabase = create_client(supabase_url, supabase_key)
        print(f"✅ Connected to Supabase: {supabase_url}")

    def get_funding_gaps(self, mount_isa_only: bool = False) -> pd.DataFrame:
        """
        Get funding flow data with gaps

        Args:
            mount_isa_only: Only include Mount Isa specific funding

        Returns:
            DataFrame with announced, allocated, paid, and gaps
        """
        print("\n" + "=" * 80)
        print("📊 CALCULATING FUNDING GAPS")
        print("=" * 80)

        # Get from funding flow view
        result = self.supabase.table('v_funding_flow').select('*').execute()

        if not result.data:
            raise ValueError("❌ No data found in Supabase")

        df = pd.DataFrame(result.data)

        # Filter if needed
        if mount_isa_only:
            # Mount Isa specific announcements
            mi_result = self.supabase.table('funding_announcements') \
                .select('id') \
                .eq('is_mount_isa_specific', True) \
                .execute()

            mi_ids = [r['id'] for r in mi_result.data]
            df = df[df['announcement_id'].isin(mi_ids)]

        # Convert to numeric
        df['amount_announced'] = pd.to_numeric(df['amount_announced'], errors='coerce').fillna(0)
        df['total_allocated'] = pd.to_numeric(df['total_allocated'], errors='coerce').fillna(0)
        df['total_paid'] = pd.to_numeric(df['total_paid'], errors='coerce').fillna(0)

        # Calculate gaps
        df['gap_announcement_to_budget'] = df['amount_announced'] - df['total_allocated']
        df['gap_budget_to_payment'] = df['total_allocated'] - df['total_paid']
        df['gap_announcement_to_payment'] = df['amount_announced'] - df['total_paid']

        # Add status
        def get_status(row):
            if row['total_paid'] > 0:
                if row['total_paid'] >= row['amount_announced'] * 0.95:  # Within 5%
                    return 'Fully Paid'
                else:
                    return 'Partially Paid'
            elif row['total_allocated'] > 0:
                return 'Budgeted'
            else:
                return 'Announced Only'

        df['status'] = df.apply(get_status, axis=1)

        print(f"\nLoaded {len(df)} funding flows")
        print(f"Fully Paid: {len(df[df['status'] == 'Fully Paid'])}")
        print(f"Partially Paid: {len(df[df['status'] == 'Partially Paid'])}")
        print(f"Budgeted: {len(df[df['status'] == 'Budgeted'])}")
        print(f"Announced Only: {len(df[df['status'] == 'Announced Only'])}")

        return df

    def create_waterfall_chart(self, df: pd.DataFrame, output_file: str = None) -> go.Figure:
        """
        Create waterfall chart showing funding flow with gaps

        Args:
            df: DataFrame with funding data
            output_file: Optional file to save

        Returns:
            Plotly figure
        """
        print("\n" + "=" * 80)
        print("📊 CREATING WATERFALL CHART")
        print("=" * 80)

        # Calculate totals
        total_announced = df['amount_announced'].sum()
        total_allocated = df['total_allocated'].sum()
        total_paid = df['total_paid'].sum()

        gap_1 = total_announced - total_allocated  # Announcement → Budget gap
        gap_2 = total_allocated - total_paid  # Budget → Payment gap

        # Waterfall data
        fig = go.Figure(go.Waterfall(
            name="Funding Flow",
            orientation="v",
            measure=["absolute", "relative", "relative", "total"],
            x=["Announced", "Budget Gap", "Payment Gap", "Actually Paid"],
            textposition="outside",
            text=[
                f"${total_announced/1_000_000:.1f}M",
                f"-${gap_1/1_000_000:.1f}M" if gap_1 > 0 else f"+${abs(gap_1)/1_000_000:.1f}M",
                f"-${gap_2/1_000_000:.1f}M" if gap_2 > 0 else f"+${abs(gap_2)/1_000_000:.1f}M",
                f"${total_paid/1_000_000:.1f}M"
            ],
            y=[
                total_announced,
                -gap_1,
                -gap_2,
                total_paid
            ],
            connector={"line": {"color": "rgb(63, 63, 63)"}},
            decreasing={"marker": {"color": "#d62728"}},  # Red for gaps
            increasing={"marker": {"color": "#2ca02c"}},  # Green for additions
            totals={"marker": {"color": "#1f77b4"}}  # Blue for totals
        ))

        fig.update_layout(
            title=f"Mount Isa Youth Justice Funding Flow - Where Did the Money Go?<br><sub>Total Announced: ${total_announced/1_000_000:.1f}M | Actually Paid: ${total_paid/1_000_000:.1f}M | Gap: ${(total_announced - total_paid)/1_000_000:.1f}M</sub>",
            showlegend=False,
            yaxis_title="Amount ($)",
            xaxis_title="",
            height=600
        )

        # Save if requested
        if output_file:
            output_path = self.output_dir / output_file
            fig.write_html(str(output_path))
            print(f"✅ Saved waterfall chart: {output_path}")

        return fig

    def create_gap_table(self, df: pd.DataFrame, output_file: str = None) -> go.Figure:
        """
        Create table showing gaps for each program

        Args:
            df: DataFrame with funding data
            output_file: Optional file to save

        Returns:
            Plotly figure
        """
        print("\n" + "=" * 80)
        print("📋 CREATING GAP TABLE")
        print("=" * 80)

        # Sort by announcement amount
        df_sorted = df.sort_values('amount_announced', ascending=False).copy()

        # Create table
        fig = go.Figure(data=[go.Table(
            header=dict(
                values=[
                    'Program',
                    'Announced<br>($M)',
                    'Budgeted<br>($M)',
                    'Paid<br>($M)',
                    'Gap<br>($M)',
                    'Status'
                ],
                fill_color='#1f77b4',
                font=dict(color='white', size=12),
                align='left'
            ),
            cells=dict(
                values=[
                    df_sorted['program_name'],
                    [f"${x/1_000_000:.2f}" for x in df_sorted['amount_announced']],
                    [f"${x/1_000_000:.2f}" if x > 0 else "—" for x in df_sorted['total_allocated']],
                    [f"${x/1_000_000:.2f}" if x > 0 else "—" for x in df_sorted['total_paid']],
                    [f"${x/1_000_000:.2f}" if x > 0 else "—" for x in df_sorted['gap_announcement_to_payment']],
                    df_sorted['status']
                ],
                fill_color=[
                    'white',
                    'white',
                    'white',
                    'white',
                    ['#ffcccc' if x > 1_000_000 else '#ccffcc' if x <= 0 else 'white' for x in df_sorted['gap_announcement_to_payment']],  # Red if big gap
                    'white'
                ],
                align='left'
            )
        )])

        fig.update_layout(
            title="Funding Flow Status by Program",
            height=max(400, len(df_sorted) * 40 + 100)
        )

        # Save if requested
        if output_file:
            output_path = self.output_dir / output_file
            fig.write_html(str(output_path))
            print(f"✅ Saved gap table: {output_path}")

        return fig

    def create_status_breakdown(self, df: pd.DataFrame, output_file: str = None) -> go.Figure:
        """
        Create pie chart showing status breakdown

        Args:
            df: DataFrame with funding data
            output_file: Optional file to save

        Returns:
            Plotly figure
        """
        print("\n" + "=" * 80)
        print("📈 CREATING STATUS BREAKDOWN")
        print("=" * 80)

        # Group by status
        status_summary = df.groupby('status').agg({
            'amount_announced': 'sum',
            'program_name': 'count'
        }).reset_index()

        status_summary.columns = ['Status', 'Total Amount', 'Count']

        # Create pie chart
        fig = go.Figure(data=[go.Pie(
            labels=status_summary['Status'],
            values=status_summary['Total Amount'],
            hole=0.3,
            textinfo='label+percent',
            hovertemplate='<b>%{label}</b><br>' +
                         'Amount: $%{value:,.0f}<br>' +
                         'Percentage: %{percent}<br>' +
                         '<extra></extra>'
        )])

        total = status_summary['Total Amount'].sum()

        fig.update_layout(
            title=f'Funding Status Breakdown<br><sub>Total: ${total/1_000_000:.1f}M</sub>',
            height=500
        )

        # Save if requested
        if output_file:
            output_path = self.output_dir / output_file
            fig.write_html(str(output_path))
            print(f"✅ Saved status breakdown: {output_path}")

        return fig

    def print_summary(self, df: pd.DataFrame):
        """Print summary statistics"""
        print("\n" + "=" * 80)
        print("📊 GAP ANALYSIS SUMMARY")
        print("=" * 80)

        total_announced = df['amount_announced'].sum()
        total_allocated = df['total_allocated'].sum()
        total_paid = df['total_paid'].sum()

        print(f"\n💰 TOTAL AMOUNTS:")
        print(f"  Announced: ${total_announced/1_000_000:.2f}M")
        print(f"  Budgeted:  ${total_allocated/1_000_000:.2f}M")
        print(f"  Paid:      ${total_paid/1_000_000:.2f}M")

        print(f"\n❌ GAPS:")
        print(f"  Announcement → Budget: ${(total_announced - total_allocated)/1_000_000:.2f}M")
        print(f"  Budget → Payment:      ${(total_allocated - total_paid)/1_000_000:.2f}M")
        print(f"  Announcement → Payment: ${(total_announced - total_paid)/1_000_000:.2f}M")

        print(f"\n📊 VERIFICATION RATE:")
        verification_rate = (total_paid / total_announced * 100) if total_announced > 0 else 0
        print(f"  {verification_rate:.1f}% of announced funding verified as paid")

        # Programs with largest gaps
        print(f"\n🚨 LARGEST GAPS:")
        top_gaps = df.nlargest(5, 'gap_announcement_to_payment')[['program_name', 'gap_announcement_to_payment']]
        for idx, row in top_gaps.iterrows():
            if row['gap_announcement_to_payment'] > 0:
                print(f"  {row['program_name'][:60]}: ${row['gap_announcement_to_payment']/1_000_000:.2f}M")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Build gap analysis visualization')
    parser.add_argument('--output', choices=['show', 'html'], default='show',
                       help='Output mode (default: show)')
    parser.add_argument('--mount-isa-only', action='store_true',
                       help='Only analyze Mount Isa specific funding')
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🔍 MOUNT ISA FUNDING GAP ANALYSIS")
    print("=" * 80)

    try:
        # Initialize analyzer
        analyzer = GapAnalyzer(data_source='supabase')

        # Get data
        df = analyzer.get_funding_gaps(mount_isa_only=args.mount_isa_only)

        # Print summary
        analyzer.print_summary(df)

        # Create visualizations
        save_html = args.output == 'html'

        waterfall = analyzer.create_waterfall_chart(
            df,
            output_file='funding_gap_waterfall.html' if save_html else None
        )

        gap_table = analyzer.create_gap_table(
            df,
            output_file='funding_gap_table.html' if save_html else None
        )

        status_breakdown = analyzer.create_status_breakdown(
            df,
            output_file='funding_status_breakdown.html' if save_html else None
        )

        if args.output == 'show':
            print("\n" + "=" * 80)
            print("📊 OPENING VISUALIZATIONS IN BROWSER")
            print("=" * 80)

            waterfall.show()
            gap_table.show()
            status_breakdown.show()

        print("\n" + "=" * 80)
        print("✅ GAP ANALYSIS COMPLETE")
        print("=" * 80)

        if save_html:
            output_dir = Path(__file__).parent.parent / 'visualizations'
            print(f"\n📁 HTML files saved to: {output_dir}")
            print("\nFiles created:")
            print("  • funding_gap_waterfall.html")
            print("  • funding_gap_table.html")
            print("  • funding_status_breakdown.html")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
