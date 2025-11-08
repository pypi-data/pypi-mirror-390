"""
Example: Quadratic Function
Visualize the function y = x^2 - 4*x + 3
"""

from numgraph import make_graph

def main():
    print("=" * 60)
    print("Quadratic Function Example: y = x**2 - 4*x + 3")
    print("=" * 60)
    
    # Create and visualize the graph with function plot
    equation = "y = x**2 - 4*x + 3"
    graph = make_graph(
        equation, 
        visualize=True, 
        func_range=(-2, 6),
        save_path="quadratic_graph.html"
    )
    
    # Print statistics
    print(f"\nEquation: {equation}")
    print(f"Number of nodes: {graph.number_of_nodes()}")
    print(f"Number of edges: {graph.number_of_edges()}")
    
    # List nodes by type
    variables = [d['label'] for _, d in graph.nodes(data=True) if d.get('type') == 'variable']
    operators = [d['label'] for _, d in graph.nodes(data=True) if d.get('type') == 'operator']
    constants = [d['label'] for _, d in graph.nodes(data=True) if d.get('type') == 'constant']
    
    print(f"\nVariables: {set(variables)}")
    print(f"Operators: {set(operators)}")
    print(f"Constants: {set(constants)}")
    
    print("\n✓ Interactive graph saved as 'quadratic_graph.html'")
    print("✓ Function plot displayed")

if __name__ == "__main__":
    main()
