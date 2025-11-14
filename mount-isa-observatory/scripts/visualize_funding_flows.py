"""
Visualize Mount Isa Funding Flows

Creates interactive visualizations of funding flows from government through
programs to organizations and outcomes.

Visualizations:
- Sankey diagram: Government → Programs → Organizations
- Timeline: Funding announcements over time
- Bar chart: Top recipients
- Geographic map: Funding by location (if coordinates available)

Usage:
    python scripts/visualize_funding_flows.py
    python scripts/visualize_funding_flows.py --source csv  # Use CSV data instead of Supabase
    python scripts/visualize_funding_flows.py --output html  # Save as HTML
"""

import os
import sys
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from pathlib import Path
from typing import Dict, List, Tuple
from dotenv import load_dotenv

# Load environment
load_dotenv()


class FundingFlowVisualizer:
    """Create visualizations of Mount Isa funding flows"""

    def __init__(self, data_source: str = 'csv'):
        """
        Initialize visualizer

        Args:
            data_source: 'csv' or 'supabase'
        """
        self.data_source = data_source
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.output_dir = Path(__file__).parent.parent / 'visualizations'
        self.output_dir.mkdir(exist_ok=True)

        if data_source == 'supabase':
            self._init_supabase()
        else:
            self.funding_df = self._load_csv_data()

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
        self.funding_df = self._load_supabase_data()

    def _load_csv_data(self) -> pd.DataFrame:
        """Load data from CSV files"""
        csv_path = self.data_dir / 'media_statements' / 'mount_isa_statements_recovered.csv'

        if not csv_path.exists():
            raise FileNotFoundError(f"❌ Data file not found: {csv_path}")

        df = pd.read_csv(csv_path)

        # Parse funding amounts
        df['amount'] = df['funding_amount'].apply(self._parse_amount)

        # Clean up recipient names
        df['recipient_clean'] = df['recipient_organization'].apply(self._clean_recipient)

        return df

    def _load_supabase_data(self) -> pd.DataFrame:
        """Load data from Supabase using the funding flow view"""
        result = self.supabase.table('v_funding_flow').select('*').execute()

        if not result.data:
            raise ValueError("❌ No data found in Supabase")

        df = pd.DataFrame(result.data)

        # Rename columns to match CSV format for compatibility
        df = df.rename(columns={
            'amount_announced': 'amount',
            'recipient_organization': 'recipient_clean'
        })

        # Add date column from announcement_date
        if 'announcement_date' in df.columns:
            df['date'] = df['announcement_date']

        # Clean recipient names
        if 'recipient_clean' in df.columns:
            df['recipient_clean'] = df['recipient_clean'].fillna('Unspecified')
        else:
            df['recipient_clean'] = 'Unspecified'

        # Ensure amount is numeric
        if 'amount' in df.columns:
            df['amount'] = pd.to_numeric(df['amount'], errors='coerce').fillna(0)

        return df

    def _parse_amount(self, amount_str) -> float:
        """Parse funding amount from string"""
        if pd.isna(amount_str) or amount_str == 'N/A' or not amount_str:
            return 0

        amount_str = str(amount_str).replace('$', '').replace(',', '').strip()

        if 'M' in amount_str.upper() or 'million' in amount_str.lower():
            amount_str = amount_str.upper().replace('M', '').replace('ILLION', '').strip()
            return float(amount_str) * 1_000_000
        elif 'B' in amount_str.upper() or 'billion' in amount_str.lower():
            amount_str = amount_str.upper().replace('B', '').replace('ILLION', '').strip()
            return float(amount_str) * 1_000_000_000

        try:
            return float(amount_str)
        except:
            return 0

    def _clean_recipient(self, recipient_str) -> str:
        """Clean up recipient organization name"""
        if pd.isna(recipient_str) or not recipient_str:
            return 'Unspecified'

        # Remove dollar amounts from recipient names
        if '$' in recipient_str:
            recipient_str = recipient_str.split('$')[0].strip().rstrip(',')

        # Truncate long names
        if len(recipient_str) > 80:
            recipient_str = recipient_str[:77] + '...'

        return recipient_str

    def create_sankey_diagram(self, output_file: str = None) -> go.Figure:
        """
        Create Sankey diagram showing funding flows

        Args:
            output_file: Optional path to save HTML file

        Returns:
            Plotly figure
        """
        print("\n" + "=" * 80)
        print("📊 CREATING SANKEY DIAGRAM")
        print("=" * 80)

        # Prepare data for Sankey
        # We need: source nodes, target nodes, values

        # Filter to rows with valid amounts and recipients
        df = self.funding_df[
            (self.funding_df['amount'] > 0) &
            (self.funding_df['recipient_clean'].notna()) &
            (self.funding_df['recipient_clean'] != 'Unspecified')
        ].copy()

        if len(df) == 0:
            print("⚠️  No valid funding flows to visualize")
            return None

        # Build node lists
        all_nodes = []
        node_indices = {}

        # Add source node (Queensland Government)
        source_node = 'Queensland Government'
        all_nodes.append(source_node)
        node_indices[source_node] = 0

        # Add program nodes
        programs = df['program_name'].unique()
        for program in programs:
            if pd.notna(program):
                all_nodes.append(program)
                node_indices[program] = len(all_nodes) - 1

        # Add recipient nodes
        recipients = df['recipient_clean'].unique()
        for recipient in recipients:
            if recipient != 'Unspecified':
                all_nodes.append(recipient)
                node_indices[recipient] = len(all_nodes) - 1

        # Build links
        sources = []
        targets = []
        values = []
        labels = []
        colors = []

        # Government → Programs
        for program in programs:
            if pd.notna(program):
                amount = df[df['program_name'] == program]['amount'].sum()
                sources.append(node_indices[source_node])
                targets.append(node_indices[program])
                values.append(amount)
                labels.append(f"${amount/1_000_000:.1f}M")
                colors.append('rgba(31, 119, 180, 0.4)')  # Blue

        # Programs → Recipients
        for _, row in df.iterrows():
            if pd.notna(row['program_name']) and row['recipient_clean'] != 'Unspecified':
                sources.append(node_indices[row['program_name']])
                targets.append(node_indices[row['recipient_clean']])
                values.append(row['amount'])
                labels.append(f"${row['amount']/1_000_000:.1f}M")
                colors.append('rgba(255, 127, 14, 0.4)')  # Orange

        # Create figure
        fig = go.Figure(data=[go.Sankey(
            node=dict(
                pad=15,
                thickness=20,
                line=dict(color='black', width=0.5),
                label=all_nodes,
                color=['#1f77b4'] + ['#2ca02c'] * len(programs) + ['#ff7f0e'] * len(recipients)
            ),
            link=dict(
                source=sources,
                target=targets,
                value=values,
                label=labels,
                color=colors
            )
        )])

        # Calculate total funding
        total_funding = df['amount'].sum()

        fig.update_layout(
            title={
                'text': f"Mount Isa Youth Justice Funding Flows<br><sub>Total: ${total_funding/1_000_000:.1f}M | {len(df)} funding announcements</sub>",
                'x': 0.5,
                'xanchor': 'center'
            },
            font=dict(size=12),
            height=800,
            margin=dict(l=20, r=20, t=80, b=20)
        )

        # Save if requested
        if output_file:
            output_path = self.output_dir / output_file
            fig.write_html(str(output_path))
            print(f"✅ Saved Sankey diagram: {output_path}")

        return fig

    def create_timeline(self, output_file: str = None) -> go.Figure:
        """
        Create timeline of funding announcements

        Args:
            output_file: Optional path to save HTML file

        Returns:
            Plotly figure
        """
        print("\n" + "=" * 80)
        print("📅 CREATING TIMELINE")
        print("=" * 80)

        # Convert dates (handle mixed formats)
        df = self.funding_df.copy()
        df['date'] = pd.to_datetime(df['date'], format='mixed', errors='coerce')
        df = df[df['amount'] > 0].dropna(subset=['date']).sort_values('date')

        # Create figure
        fig = go.Figure()

        # Add scatter plot
        fig.add_trace(go.Scatter(
            x=df['date'],
            y=df['amount'] / 1_000_000,  # Convert to millions
            mode='markers+text',
            marker=dict(
                size=df['amount'] / 5_000_000,  # Scale marker size
                color=df['amount'],
                colorscale='Viridis',
                showscale=True,
                colorbar=dict(title='Amount ($M)')
            ),
            text=df['program_name'].apply(lambda x: x[:30] + '...' if len(str(x)) > 30 else x),
            textposition='top center',
            hovertemplate='<b>%{text}</b><br>' +
                         'Date: %{x}<br>' +
                         'Amount: $%{y:.1f}M<br>' +
                         '<extra></extra>'
        ))

        fig.update_layout(
            title='Mount Isa Youth Justice Funding Timeline',
            xaxis_title='Announcement Date',
            yaxis_title='Funding Amount ($M)',
            hovermode='closest',
            height=600
        )

        # Save if requested
        if output_file:
            output_path = self.output_dir / output_file
            fig.write_html(str(output_path))
            print(f"✅ Saved timeline: {output_path}")

        return fig

    def create_recipient_chart(self, output_file: str = None) -> go.Figure:
        """
        Create bar chart of top recipients

        Args:
            output_file: Optional path to save HTML file

        Returns:
            Plotly figure
        """
        print("\n" + "=" * 80)
        print("🏢 CREATING RECIPIENT CHART")
        print("=" * 80)

        # Group by recipient
        df = self.funding_df[self.funding_df['amount'] > 0].copy()

        recipient_totals = df.groupby('recipient_clean')['amount'].sum().sort_values(ascending=False)
        recipient_totals = recipient_totals[recipient_totals.index != 'Unspecified']

        # Create figure
        fig = go.Figure(data=[
            go.Bar(
                y=recipient_totals.index,
                x=recipient_totals.values / 1_000_000,
                orientation='h',
                marker=dict(
                    color=recipient_totals.values,
                    colorscale='Blues',
                    showscale=True,
                    colorbar=dict(title='Amount ($M)')
                ),
                text=[f'${v/1_000_000:.1f}M' for v in recipient_totals.values],
                textposition='auto'
            )
        ])

        fig.update_layout(
            title='Mount Isa Youth Justice Funding by Recipient',
            xaxis_title='Total Funding ($M)',
            yaxis_title='Recipient Organization',
            height=max(400, len(recipient_totals) * 40),
            margin=dict(l=300)  # More space for long org names
        )

        # Save if requested
        if output_file:
            output_path = self.output_dir / output_file
            fig.write_html(str(output_path))
            print(f"✅ Saved recipient chart: {output_path}")

        return fig

    def create_program_breakdown(self, output_file: str = None) -> go.Figure:
        """
        Create pie chart of funding by program type

        Args:
            output_file: Optional path to save HTML file

        Returns:
            Plotly figure
        """
        print("\n" + "=" * 80)
        print("📈 CREATING PROGRAM BREAKDOWN")
        print("=" * 80)

        # Group by program
        df = self.funding_df[self.funding_df['amount'] > 0].copy()

        program_totals = df.groupby('program_name')['amount'].sum().sort_values(ascending=False)

        # Create figure
        fig = go.Figure(data=[
            go.Pie(
                labels=program_totals.index,
                values=program_totals.values,
                hole=0.3,
                textinfo='label+percent',
                hovertemplate='<b>%{label}</b><br>' +
                             'Amount: $%{value:,.0f}<br>' +
                             'Percentage: %{percent}<br>' +
                             '<extra></extra>'
            )
        ])

        total_funding = program_totals.sum()

        fig.update_layout(
            title=f'Mount Isa Youth Justice Funding by Program<br><sub>Total: ${total_funding/1_000_000:.1f}M</sub>',
            height=600
        )

        # Save if requested
        if output_file:
            output_path = self.output_dir / output_file
            fig.write_html(str(output_path))
            print(f"✅ Saved program breakdown: {output_path}")

        return fig

    def generate_summary_stats(self):
        """Generate and print summary statistics"""
        print("\n" + "=" * 80)
        print("📊 FUNDING SUMMARY STATISTICS")
        print("=" * 80)

        df = self.funding_df[self.funding_df['amount'] > 0].copy()

        print(f"\nTotal funding: ${df['amount'].sum()/1_000_000:.1f}M")
        print(f"Number of announcements: {len(df)}")
        print(f"Number of programs: {df['program_name'].nunique()}")
        print(f"Number of recipients: {df['recipient_clean'].nunique()}")
        print(f"Date range: {df['date'].min()} to {df['date'].max()}")

        print(f"\nAverage funding per announcement: ${df['amount'].mean()/1_000_000:.1f}M")
        print(f"Median funding: ${df['amount'].median()/1_000_000:.1f}M")
        print(f"Largest single announcement: ${df['amount'].max()/1_000_000:.1f}M")

        print("\nTop 5 programs by funding:")
        top_programs = df.groupby('program_name')['amount'].sum().sort_values(ascending=False).head(5)
        for program, amount in top_programs.items():
            print(f"  • {program[:60]}: ${amount/1_000_000:.1f}M")

        print("\nTop 5 recipients by funding:")
        top_recipients = df.groupby('recipient_clean')['amount'].sum().sort_values(ascending=False).head(5)
        for recipient, amount in top_recipients.items():
            if recipient != 'Unspecified':
                print(f"  • {recipient[:60]}: ${amount/1_000_000:.1f}M")


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Visualize Mount Isa funding flows')
    parser.add_argument('--source', choices=['csv', 'supabase'], default='csv',
                       help='Data source (default: csv)')
    parser.add_argument('--output', choices=['show', 'html'], default='show',
                       help='Output mode (default: show)')
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🎨 MOUNT ISA FUNDING FLOW VISUALIZATIONS")
    print("=" * 80)

    try:
        # Initialize visualizer
        viz = FundingFlowVisualizer(data_source=args.source)

        # Generate summary stats
        viz.generate_summary_stats()

        # Create visualizations
        save_html = args.output == 'html'

        sankey = viz.create_sankey_diagram(
            output_file='funding_flow_sankey.html' if save_html else None
        )

        timeline = viz.create_timeline(
            output_file='funding_timeline.html' if save_html else None
        )

        recipient_chart = viz.create_recipient_chart(
            output_file='funding_by_recipient.html' if save_html else None
        )

        program_breakdown = viz.create_program_breakdown(
            output_file='funding_by_program.html' if save_html else None
        )

        if args.output == 'show':
            print("\n" + "=" * 80)
            print("📊 OPENING VISUALIZATIONS IN BROWSER")
            print("=" * 80)

            if sankey:
                sankey.show()
            timeline.show()
            recipient_chart.show()
            program_breakdown.show()

        print("\n" + "=" * 80)
        print("✅ VISUALIZATIONS COMPLETE")
        print("=" * 80)

        if save_html:
            output_dir = Path(__file__).parent.parent / 'visualizations'
            print(f"\n📁 HTML files saved to: {output_dir}")
            print("\nFiles created:")
            for file in output_dir.glob('*.html'):
                print(f"  • {file.name}")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
