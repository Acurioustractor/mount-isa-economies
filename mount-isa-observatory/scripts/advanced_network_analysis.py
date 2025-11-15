"""
Advanced Network Analysis - Follow the Money, Find the Power

Analyzes the network of funding relationships to reveal:
- Who funds whom (and how much, how often)
- Power structures (who controls funding decisions)
- Patterns (repeat funding, preference for certain organization types)
- Influence networks (relationships between decision-makers)
- Funding concentration (is money going to few or many organizations)

This goes beyond simple tracking to reveal systemic patterns.

Usage:
    python scripts/advanced_network_analysis.py
    python scripts/advanced_network_analysis.py --visualize
    python scripts/advanced_network_analysis.py --export-gephi
"""

import os
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from dotenv import load_dotenv
import pandas as pd
import json

# Load environment
load_dotenv()


class NetworkAnalyzer:
    """Analyze funding networks to reveal power structures"""

    def __init__(self):
        """Initialize analyzer"""
        # Check if Supabase is configured
        self.supabase_url = os.getenv('SUPABASE_URL')
        self.supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

        if not self.supabase_url or not self.supabase_key:
            raise ValueError("Supabase not configured. Set SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY")

        from supabase import create_client
        self.supabase = create_client(self.supabase_url, self.supabase_key)

        # Output directory
        self.output_dir = Path(__file__).parent.parent / 'analysis' / 'network'
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def analyze_funding_network(self) -> Dict:
        """
        Analyze the network of funding relationships

        Returns:
            Dictionary of network statistics and insights
        """
        print("\n" + "=" * 80)
        print("🕸️  FUNDING NETWORK ANALYSIS")
        print("=" * 80)

        # Get funding network data
        result = self.supabase.table('v_funding_network').select('*').execute()
        df = pd.DataFrame(result.data)

        if df.empty:
            print("\n❌ No funding network data available")
            print("   Make sure funding data is loaded to Supabase")
            return {}

        print(f"\n📊 Network size: {len(df)} funding relationships")

        # Network statistics
        stats = {
            'total_relationships': len(df),
            'unique_funders': df['funder_name'].nunique(),
            'unique_recipients': df['recipient_name'].nunique(),
            'total_funding_m': df['total_funding_m'].sum(),
            'avg_funding_per_relationship_m': df['total_funding_m'].mean(),
            'median_funding_per_relationship_m': df['total_funding_m'].median(),
        }

        # Funding concentration (Gini coefficient-like measure)
        # Are a few organizations getting most of the money?
        df_sorted = df.sort_values('total_funding_m')
        cumsum = df_sorted['total_funding_m'].cumsum()
        total = df_sorted['total_funding_m'].sum()
        concentration = (2 * (cumsum * range(1, len(df) + 1)).sum() / (len(df) * total)) - (len(df) + 1) / len(df)
        stats['funding_concentration'] = concentration  # 0 = equal distribution, 1 = one org gets everything

        print("\n" + "=" * 80)
        print("📈 NETWORK STATISTICS")
        print("=" * 80)
        print(f"\nUnique funders: {stats['unique_funders']}")
        print(f"Unique recipients: {stats['unique_recipients']}")
        print(f"Total funding: ${stats['total_funding_m']:.1f}M")
        print(f"Average per relationship: ${stats['avg_funding_per_relationship_m']:.1f}M")
        print(f"Funding concentration: {stats['funding_concentration']:.2f} (0=equal, 1=concentrated)")

        # Top funders
        print("\n" + "=" * 80)
        print("💰 TOP FUNDERS")
        print("=" * 80)

        top_funders = df.groupby('funder_name').agg({
            'total_funding_m': 'sum',
            'recipient_name': 'count',
            'funder_type': 'first'
        }).sort_values('total_funding_m', ascending=False).head(10)

        top_funders.columns = ['Total Funding $M', 'Recipients', 'Type']

        print("\n" + top_funders.to_string())

        # Top recipients
        print("\n" + "=" * 80)
        print("🎯 TOP RECIPIENTS")
        print("=" * 80)

        top_recipients = df.groupby('recipient_name').agg({
            'total_funding_m': 'sum',
            'funding_count': 'sum',
            'recipient_type': 'first'
        }).sort_values('total_funding_m', ascending=False).head(10)

        top_recipients.columns = ['Total Received $M', 'Funding Count', 'Type']

        print("\n" + top_recipients.to_string())

        # Repeat funding relationships
        print("\n" + "=" * 80)
        print("🔄 REPEAT FUNDING RELATIONSHIPS")
        print("=" * 80)
        print("\nRelationships with multiple funding instances (repeat funding):\n")

        repeat_relationships = df[df['funding_count'] > 1].sort_values('funding_count', ascending=False)

        if repeat_relationships.empty:
            print("No repeat funding relationships found")
        else:
            for _, row in repeat_relationships.head(10).iterrows():
                print(f"  {row['funder_name']} → {row['recipient_name']}")
                print(f"    Funding instances: {row['funding_count']}")
                print(f"    Total: ${row['total_funding_m']:.1f}M")
                print(f"    Programs: {', '.join(row['programs_funded'])}")
                print()

        # Organization type patterns
        print("\n" + "=" * 80)
        print("🏢 FUNDING BY ORGANIZATION TYPE")
        print("=" * 80)

        type_patterns = df.groupby(['funder_type', 'recipient_type']).agg({
            'total_funding_m': 'sum',
            'funding_count': 'sum'
        }).sort_values('total_funding_m', ascending=False)

        print("\nWho funds whom (by organization type):\n")
        for (funder_type, recipient_type), row in type_patterns.head(15).iterrows():
            print(f"  {funder_type} → {recipient_type}")
            print(f"    ${row['total_funding_m']:.1f}M across {row['funding_count']} instances")

        # Save analysis
        stats_file = self.output_dir / 'network_statistics.json'
        with open(stats_file, 'w') as f:
            json.dump(stats, f, indent=2, default=str)

        print(f"\n✅ Network statistics saved: {stats_file}")

        return stats

    def detect_funding_patterns(self) -> pd.DataFrame:
        """
        Detect patterns in funding relationships

        Returns:
            DataFrame of detected patterns
        """
        print("\n" + "=" * 80)
        print("🔍 PATTERN DETECTION")
        print("=" * 80)

        result = self.supabase.table('v_funding_network').select('*').execute()
        df = pd.DataFrame(result.data)

        if df.empty:
            print("\n❌ No funding network data available")
            return pd.DataFrame()

        patterns = []

        # Pattern 1: Monopolistic relationships (one funder dominates a recipient)
        for recipient in df['recipient_name'].unique():
            recipient_data = df[df['recipient_name'] == recipient]
            if len(recipient_data) > 1:  # Multiple funders
                max_funding = recipient_data['total_funding_m'].max()
                total_funding = recipient_data['total_funding_m'].sum()
                concentration = max_funding / total_funding

                if concentration > 0.8:  # One funder is 80%+ of total
                    dominant_funder = recipient_data.loc[recipient_data['total_funding_m'].idxmax(), 'funder_name']
                    patterns.append({
                        'pattern_type': 'monopolistic_funding',
                        'description': f'{dominant_funder} provides {concentration*100:.0f}% of funding to {recipient}',
                        'entities': [dominant_funder, recipient],
                        'funding_amount_m': max_funding,
                        'significance': 'high' if concentration > 0.9 else 'medium'
                    })

        # Pattern 2: Exclusive relationships (funder only funds one recipient for a program type)
        funder_diversity = df.groupby('funder_name')['recipient_name'].nunique()
        for funder, recipient_count in funder_diversity.items():
            if recipient_count == 1:
                recipient = df[df['funder_name'] == funder].iloc[0]['recipient_name']
                total_funding = df[df['funder_name'] == funder]['total_funding_m'].sum()
                patterns.append({
                    'pattern_type': 'exclusive_relationship',
                    'description': f'{funder} exclusively funds {recipient}',
                    'entities': [funder, recipient],
                    'funding_amount_m': total_funding,
                    'significance': 'medium'
                })

        # Pattern 3: Hub organizations (receive from many funders)
        recipient_funder_counts = df.groupby('recipient_name')['funder_name'].nunique()
        for recipient, funder_count in recipient_funder_counts.items():
            if funder_count >= 3:  # Receives from 3+ different funders
                total_funding = df[df['recipient_name'] == recipient]['total_funding_m'].sum()
                patterns.append({
                    'pattern_type': 'hub_organization',
                    'description': f'{recipient} receives funding from {funder_count} different funders',
                    'entities': [recipient],
                    'funding_amount_m': total_funding,
                    'significance': 'high' if funder_count >= 5 else 'medium'
                })

        # Pattern 4: Long-term relationships (funding over multiple years)
        for _, row in df.iterrows():
            if pd.notna(row['first_funding_date']) and pd.notna(row['latest_funding_date']):
                first = pd.to_datetime(row['first_funding_date'])
                latest = pd.to_datetime(row['latest_funding_date'])
                years = (latest - first).days / 365

                if years >= 3 and row['funding_count'] >= 3:
                    patterns.append({
                        'pattern_type': 'long_term_partnership',
                        'description': f'{row["funder_name"]} → {row["recipient_name"]} for {years:.1f} years',
                        'entities': [row['funder_name'], row['recipient_name']],
                        'funding_amount_m': row['total_funding_m'],
                        'significance': 'high' if years >= 5 else 'medium'
                    })

        patterns_df = pd.DataFrame(patterns)

        if not patterns_df.empty:
            print(f"\n🔍 Detected {len(patterns_df)} patterns:\n")

            for pattern_type in patterns_df['pattern_type'].unique():
                type_patterns = patterns_df[patterns_df['pattern_type'] == pattern_type]
                print(f"\n{pattern_type.replace('_', ' ').title()} ({len(type_patterns)}):")

                for _, p in type_patterns.head(5).iterrows():
                    print(f"  • {p['description']}")
                    print(f"    Funding: ${p['funding_amount_m']:.1f}M | Significance: {p['significance']}")

            # Save patterns
            patterns_file = self.output_dir / 'detected_patterns.csv'
            patterns_df.to_csv(patterns_file, index=False)
            print(f"\n✅ Patterns saved: {patterns_file}")

        else:
            print("\nNo significant patterns detected")

        return patterns_df

    def create_network_visualization_data(self) -> Dict:
        """
        Create network data for visualization (Gephi, D3, etc.)

        Returns:
            Dictionary with nodes and edges for network graph
        """
        print("\n" + "=" * 80)
        print("🎨 CREATING NETWORK VISUALIZATION DATA")
        print("=" * 80)

        result = self.supabase.table('v_funding_network').select('*').execute()
        df = pd.DataFrame(result.data)

        if df.empty:
            print("\n❌ No funding network data available")
            return {}

        # Nodes (organizations)
        nodes = []
        all_orgs = set(df['funder_name'].tolist() + df['recipient_name'].tolist())

        for org in all_orgs:
            # Is this org a funder, recipient, or both?
            is_funder = org in df['funder_name'].values
            is_recipient = org in df['recipient_name'].values

            # Total funded (if funder)
            total_funded = df[df['funder_name'] == org]['total_funding_m'].sum() if is_funder else 0

            # Total received (if recipient)
            total_received = df[df['recipient_name'] == org]['total_funding_m'].sum() if is_recipient else 0

            # Node size (bigger = more money involved)
            size = total_funded + total_received

            # Node type
            if is_funder and is_recipient:
                node_type = 'both'
            elif is_funder:
                node_type = 'funder'
            else:
                node_type = 'recipient'

            nodes.append({
                'id': org,
                'label': org,
                'type': node_type,
                'total_funded_m': total_funded,
                'total_received_m': total_received,
                'size': size
            })

        # Edges (funding relationships)
        edges = []
        for _, row in df.iterrows():
            edges.append({
                'source': row['funder_name'],
                'target': row['recipient_name'],
                'weight': row['total_funding_m'],
                'funding_count': row['funding_count'],
                'programs': row['programs_funded']
            })

        network_data = {
            'nodes': nodes,
            'edges': edges,
            'metadata': {
                'total_nodes': len(nodes),
                'total_edges': len(edges),
                'created_date': datetime.now().isoformat()
            }
        }

        # Save as JSON for D3/web visualizations
        json_file = self.output_dir / 'network_graph.json'
        with open(json_file, 'w') as f:
            json.dump(network_data, f, indent=2, default=str)

        print(f"\n✅ Network graph data saved: {json_file}")
        print(f"   Nodes: {len(nodes)}")
        print(f"   Edges: {len(edges)}")

        # Save as GEXF for Gephi
        gexf_file = self.output_dir / 'network_graph.gexf'
        self._export_gexf(network_data, gexf_file)
        print(f"✅ Gephi file saved: {gexf_file}")

        print("\n💡 Use these files to visualize the funding network:")
        print("   - network_graph.json: Import into D3.js, Vis.js, or web tools")
        print("   - network_graph.gexf: Open in Gephi for advanced network analysis")

        return network_data

    def _export_gexf(self, network_data: Dict, output_file: Path):
        """Export network to GEXF format for Gephi"""
        gexf_content = ['<?xml version="1.0" encoding="UTF-8"?>']
        gexf_content.append('<gexf xmlns="http://www.gexf.net/1.2draft" version="1.2">')
        gexf_content.append('  <graph mode="static" defaultedgetype="directed">')

        # Nodes
        gexf_content.append('    <nodes>')
        for i, node in enumerate(network_data['nodes']):
            gexf_content.append(f'      <node id="{i}" label="{node["label"]}">')
            gexf_content.append('        <attvalues>')
            gexf_content.append(f'          <attvalue for="0" value="{node["type"]}"/>')
            gexf_content.append(f'          <attvalue for="1" value="{node["size"]}"/>')
            gexf_content.append('        </attvalues>')
            gexf_content.append('      </node>')
        gexf_content.append('    </nodes>')

        # Edges
        gexf_content.append('    <edges>')
        node_id_map = {node['id']: i for i, node in enumerate(network_data['nodes'])}

        for i, edge in enumerate(network_data['edges']):
            source_id = node_id_map[edge['source']]
            target_id = node_id_map[edge['target']]
            weight = edge['weight']
            gexf_content.append(f'      <edge id="{i}" source="{source_id}" target="{target_id}" weight="{weight}"/>')
        gexf_content.append('    </edges>')

        gexf_content.append('  </graph>')
        gexf_content.append('</gexf>')

        with open(output_file, 'w') as f:
            f.write('\n'.join(gexf_content))

    def generate_insights_report(self, stats: Dict, patterns: pd.DataFrame) -> str:
        """
        Generate insights report combining all analyses

        Returns:
            Path to markdown report
        """
        print("\n" + "=" * 80)
        print("📝 GENERATING INSIGHTS REPORT")
        print("=" * 80)

        report = []
        report.append("# Funding Network Analysis - Insights Report")
        report.append(f"\n**Generated**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        report.append("\n---\n")

        # Executive summary
        report.append("## 🎯 Executive Summary\n")

        if stats:
            concentration = stats.get('funding_concentration', 0)

            if concentration > 0.7:
                report.append(f"⚠️ **High funding concentration detected** (Gini: {concentration:.2f})")
                report.append("   - A small number of organizations receive most funding")
                report.append("   - Consider equity and access implications")
            elif concentration > 0.4:
                report.append(f"📊 **Moderate funding concentration** (Gini: {concentration:.2f})")
                report.append("   - Funding is somewhat concentrated but not extreme")
            else:
                report.append(f"✅ **Relatively equal funding distribution** (Gini: {concentration:.2f})")
                report.append("   - Funding is spread across multiple organizations")

            report.append(f"\n- **{stats['unique_funders']} funders** → **{stats['unique_recipients']} recipients**")
            report.append(f"- **${stats['total_funding_m']:.1f}M total** across {stats['total_relationships']} relationships")
            report.append("")

        # Detected patterns
        if not patterns.empty:
            report.append("\n## 🔍 Detected Patterns\n")

            for pattern_type in patterns['pattern_type'].unique():
                type_patterns = patterns[patterns['pattern_type'] == pattern_type]
                high_sig = len(type_patterns[type_patterns['significance'] == 'high'])

                report.append(f"### {pattern_type.replace('_', ' ').title()}")
                report.append(f"\n{len(type_patterns)} detected ({high_sig} high significance)\n")

                for _, p in type_patterns.head(5).iterrows():
                    report.append(f"- {p['description']}")
                    report.append(f"  - Funding: ${p['funding_amount_m']:.1f}M")
                report.append("")

        # Implications
        report.append("\n## 💡 Implications for Mount Isa\n")
        report.append("### Funding Diversity")
        report.append("- Organizations with single funders are vulnerable to funding cuts")
        report.append("- Diversifying funding sources increases sustainability")
        report.append("")

        report.append("### Long-term Partnerships")
        report.append("- Repeat funding relationships indicate trust and proven delivery")
        report.append("- Can be leveraged for expansion and scale")
        report.append("")

        report.append("### Equity Considerations")
        report.append("- Analyze if Indigenous-led organizations have equitable access to funding")
        report.append("- Check if funding concentration excludes emerging or smaller organizations")
        report.append("")

        # Save report
        report_file = self.output_dir / 'network_analysis_report.md'
        with open(report_file, 'w') as f:
            f.write('\n'.join(report))

        print(f"\n✅ Insights report saved: {report_file}")

        return str(report_file)


def main():
    """Main execution"""
    import argparse

    parser = argparse.ArgumentParser(description='Analyze funding networks')
    parser.add_argument('--visualize', action='store_true',
                       help='Create network visualization data')
    parser.add_argument('--export-gephi', action='store_true',
                       help='Export to Gephi format')
    args = parser.parse_args()

    print("\n" + "=" * 80)
    print("🕸️  ADVANCED NETWORK ANALYSIS")
    print("=" * 80)

    try:
        analyzer = NetworkAnalyzer()

        # Core analysis
        stats = analyzer.analyze_funding_network()
        patterns = analyzer.detect_funding_patterns()

        # Visualizations if requested
        if args.visualize or args.export_gephi:
            network_data = analyzer.create_network_visualization_data()

        # Generate insights report
        report_path = analyzer.generate_insights_report(stats, patterns)

        print("\n" + "=" * 80)
        print("✅ ANALYSIS COMPLETE")
        print("=" * 80)
        print(f"\nResults saved to: analysis/network/")
        print("\n📊 What you can do now:")
        print("  1. Review insights report: network_analysis_report.md")
        print("  2. Explore detected patterns: detected_patterns.csv")
        print("  3. Visualize network: Open network_graph.gexf in Gephi")
        print("  4. Use for JusticeHub stories: Show funding concentration, repeat relationships")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
