"""
Example: Circle Equation
Visualize the equation x^2 + y^2 = 25 (a circle with radius 5)
"""

from numgraph import make_graph

def main():
    print("=" * 60)
    print("Circle Equation Example: x**2 + y**2 = 25")
    print("=" * 60)
    
    # Create and visualize the graph
    equation = "x**2 + y**2 = 25"
    graph = make_graph(equation, visualize=True, save_path="circle_graph.html")
    
    # Print some statistics
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
    
    print("\n✓ Interactive graph saved as 'circle_graph.html'")
    print("  Open this file in your browser to explore!")

if __name__ == "__main__":
    main()
