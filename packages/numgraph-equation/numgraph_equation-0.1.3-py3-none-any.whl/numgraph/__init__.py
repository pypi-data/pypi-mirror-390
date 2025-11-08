"""
numgraph - Convert mathematical equations into graph structures
"""

__version__ = "0.1.0"
__author__ = "Ayush Mishra"

from numgraph.parser import EquationParser
from numgraph.graph_builder import GraphBuilder
from numgraph.visualizer import Visualizer

def make_graph(equation, visualize=False, func_range=None, save_path=None):
    """
    Main function to create a graph from a mathematical equation.
    
    Parameters:
    -----------
    equation : str
        Mathematical equation or function (e.g., "x**2 + y**2 = 25")
    visualize : bool, optional
        Whether to display the visualization (default: False)
    func_range : tuple, optional
        Range for function evaluation as (min, max) (default: None)
    save_path : str, optional
        Path to save interactive HTML visualization (default: None)
    
    Returns:
    --------
    networkx.Graph
        Graph representation of the equation
    
    Examples:
    ---------
    >>> from numgraph import make_graph
    >>> graph = make_graph("x**2 + y**2 = 25", visualize=True)
    >>> graph = make_graph("y = x**2 - 4*x + 3", func_range=(-10, 10), visualize=True)
    """
    # Parse the equation
    parser = EquationParser(equation)
    nodes, edges = parser.parse()
    
    # Build the graph
    builder = GraphBuilder(nodes, edges)
    graph = builder.build()
    
    # Add metadata
    graph.graph['equation'] = equation
    
    # Visualize if requested
    if visualize or save_path:
        viz = Visualizer(graph, equation=equation)
        
        if save_path:
            viz.save_interactive(save_path)
        
        if visualize:
            viz.show_interactive()
            
        # If it's a function with a range, also plot the function
        if func_range and '=' in equation:
            viz.plot_function(func_range)
    
    return graph

__all__ = [
    'make_graph',
    'EquationParser',
    'GraphBuilder',
    'Visualizer',
]
