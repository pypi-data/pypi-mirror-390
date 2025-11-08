"""
Example: Using numgraph in a larger application
Demonstrates how to integrate numgraph into your project
"""

from numgraph import make_graph
from numgraph.parser import EquationParser
from numgraph.graph_builder import GraphBuilder


class EquationAnalyzer:
    """
    A class that analyzes mathematical equations and provides insights.
    This is an example of how to use numgraph in your application.
    """
    
    def __init__(self):
        self.analyzed_equations = []
    
    def analyze(self, equation: str):
        """Analyze an equation and return insights"""
        print(f"\n{'='*60}")
        print(f"Analyzing: {equation}")
        print(f"{'='*60}")
        
        # Parse equation
        parser = EquationParser(equation)
        nodes, edges = parser.parse()
        
        # Build graph
        builder = GraphBuilder(nodes, edges)
        graph = builder.build()
        stats = builder.get_stats()
        
        # Extract information
        variables = builder.get_variables()
        
        # Create insights
        insights = {
            'equation': equation,
            'num_nodes': stats['num_nodes'],
            'num_edges': stats['num_edges'],
            'num_variables': stats['num_variables'],
            'num_operators': stats['num_operators'],
            'num_constants': stats['num_constants'],
            'variables': list(set(variables)),
            'complexity_score': self._calculate_complexity(stats),
            'graph': graph
        }
        
        # Store for later
        self.analyzed_equations.append(insights)
        
        # Print insights
        self._print_insights(insights)
        
        return insights
    
    def _calculate_complexity(self, stats):
        """Calculate a complexity score based on graph structure"""
        # Simple complexity metric
        score = (stats['num_operators'] * 2 + 
                stats['num_variables'] + 
                stats['max_depth'])
        return score
    
    def _print_insights(self, insights):
        """Print analysis insights"""
        print(f"\n📊 Analysis Results:")
        print(f"  • Variables: {insights['variables']}")
        print(f"  • Total Nodes: {insights['num_nodes']}")
        print(f"  • Operators: {insights['num_operators']}")
        print(f"  • Constants: {insights['num_constants']}")
        print(f"  • Complexity Score: {insights['complexity_score']}")
    
    def compare_equations(self):
        """Compare all analyzed equations"""
        if len(self.analyzed_equations) < 2:
            print("Need at least 2 equations to compare")
            return
        
        print(f"\n{'='*60}")
        print("Comparison Report")
        print(f"{'='*60}")
        
        for i, eq in enumerate(self.analyzed_equations, 1):
            print(f"\n[{i}] {eq['equation']}")
            print(f"    Variables: {len(eq['variables'])}")
            print(f"    Complexity: {eq['complexity_score']}")
        
        # Find most complex
        most_complex = max(self.analyzed_equations, 
                          key=lambda x: x['complexity_score'])
        print(f"\n🏆 Most Complex: {most_complex['equation']}")
        print(f"   Score: {most_complex['complexity_score']}")
    
    def visualize_all(self, output_dir="analysis_output"):
        """Generate visualizations for all analyzed equations"""
        import os
        os.makedirs(output_dir, exist_ok=True)
        
        print(f"\n📁 Saving visualizations to '{output_dir}/'...")
        
        for i, eq_data in enumerate(self.analyzed_equations, 1):
            equation = eq_data['equation']
            filename = f"{output_dir}/equation_{i}.html"
            
            # Create visualization
            make_graph(equation, save_path=filename)
            print(f"  ✓ Saved: {filename}")
        
        print(f"\n✅ All visualizations saved!")


def main():
    """Example usage"""
    
    # Create analyzer
    analyzer = EquationAnalyzer()
    
    # Analyze multiple equations
    equations = [
        "x**2 + y**2 = 25",
        "y = 2*x + 3",
        "x**2 + 2*x*y + y**2 = 16",
        "z = x**3 - 3*x**2*y + 3*x*y**2 - y**3",
    ]
    
    print("🔬 Equation Analyzer Demo")
    print("Using numgraph to analyze mathematical equations\n")
    
    # Analyze each equation
    for eq in equations:
        analyzer.analyze(eq)
    
    # Compare results
    analyzer.compare_equations()
    
    # Generate visualizations
    analyzer.visualize_all()
    
    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60)


if __name__ == "__main__":
    main()
