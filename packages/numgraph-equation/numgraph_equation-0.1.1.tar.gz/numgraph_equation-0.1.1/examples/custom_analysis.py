"""
Example: Custom Analysis
Demonstrates advanced usage with custom graph analysis
"""

from numgraph.parser import EquationParser
from numgraph.graph_builder import GraphBuilder
from numgraph.visualizer import Visualizer

def main():
    print("=" * 60)
    print("Custom Analysis Example")
    print("=" * 60)
    
    # Equation: x^2 + 2*x*y + y^2 = 16
    equation = "x**2 + 2*x*y + y**2 = 16"
    print(f"\nAnalyzing: {equation}")
    
    # Step 1: Parse the equation
    print("\n[1] Parsing equation...")
    parser = EquationParser(equation)
    nodes, edges = parser.parse()
    print(f"    ✓ Found {len(nodes)} nodes and {len(edges)} edges")
    
    # Step 2: Build the graph
    print("\n[2] Building graph...")
    builder = GraphBuilder(nodes, edges)
    graph = builder.build()
    
    # Get statistics
    stats = builder.get_stats()
    print(f"    ✓ Graph Statistics:")
    print(f"      - Nodes: {stats['num_nodes']}")
    print(f"      - Edges: {stats['num_edges']}")
    print(f"      - Variables: {stats['num_variables']}")
    print(f"      - Operators: {stats['num_operators']}")
    print(f"      - Constants: {stats['num_constants']}")
    print(f"      - Max Depth: {stats['max_depth']}")
    
    # Step 3: Visualize
    print("\n[3] Creating visualizations...")
    viz = Visualizer(graph, equation=equation)
    
    # Interactive visualization
    viz.save_interactive("custom_analysis.html")
    print("    ✓ Interactive HTML saved")
    
    # Static visualization
    viz.save_static("custom_analysis.png", dpi=300)
    print("    ✓ Static PNG saved")
    
    # Step 4: Export to different formats
    print("\n[4] Exporting graph data...")
    builder.export_graphml("custom_analysis.graphml")
    print("    ✓ GraphML format saved")
    
    builder.export_gexf("custom_analysis.gexf")
    print("    ✓ GEXF format saved")
    
    # Step 5: Analyze variables
    print("\n[5] Variable Analysis:")
    variables = builder.get_variables()
    print(f"    Variables found: {set(variables)}")
    print(f"    Variable count: {len(set(variables))}")
    
    print("\n" + "=" * 60)
    print("Analysis complete! Check the generated files.")
    print("=" * 60)

if __name__ == "__main__":
    main()
