"""
Visualizer Module
Visualizes equation graphs using matplotlib and pyvis.
"""

import networkx as nx
import matplotlib.pyplot as plt
from pyvis.network import Network
import numpy as np
from typing import Tuple, Optional
import sympy as sp
from sympy.parsing.sympy_parser import parse_expr


class Visualizer:
    """
    Visualizes equation graphs using matplotlib for static plots
    and pyvis for interactive HTML visualizations.
    """
    
    def __init__(self, graph: nx.DiGraph, equation: str = ""):
        """
        Initialize the visualizer.
        
        Parameters:
        -----------
        graph : networkx.DiGraph
            Graph to visualize
        equation : str, optional
            Original equation string for context
        """
        self.graph = graph
        self.equation = equation
        
        # Color scheme for different node types
        self.colors = {
            'variable': '#FF6B6B',    # Red
            'operator': '#4ECDC4',    # Teal
            'constant': '#95E1D3',    # Light green
            'function': '#FFA07A',    # Light salmon
            'expression': '#DDA0DD',  # Plum
        }
        
    def show_static(self, figsize: Tuple[int, int] = (12, 8)):
        """
        Display a static matplotlib visualization.
        
        Parameters:
        -----------
        figsize : tuple, optional
            Figure size as (width, height)
        """
        plt.figure(figsize=figsize)
        
        # Use hierarchical layout
        pos = self._get_hierarchical_pos()
        
        # Get node colors based on type
        node_colors = [self.colors.get(self.graph.nodes[node].get('type', 'expression'), '#DDA0DD')
                      for node in self.graph.nodes()]
        
        # Get node labels
        labels = {node: self.graph.nodes[node].get('label', str(node))
                 for node in self.graph.nodes()}
        
        # Draw the graph
        nx.draw(self.graph, pos,
                node_color=node_colors,
                node_size=2000,
                labels=labels,
                font_size=10,
                font_weight='bold',
                arrows=True,
                arrowsize=20,
                edge_color='gray',
                alpha=0.9,
                with_labels=True)
        
        # Add title
        if self.equation:
            plt.title(f"Graph Structure: {self.equation}", fontsize=14, fontweight='bold')
        else:
            plt.title("Equation Graph Structure", fontsize=14, fontweight='bold')
        
        # Add legend
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                     markerfacecolor=color, markersize=10, label=node_type.title())
                          for node_type, color in self.colors.items()]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.axis('off')
        plt.tight_layout()
        plt.show()
    
    def show_interactive(self, height: str = "600px", width: str = "100%"):
        """
        Display an interactive pyvis visualization.
        
        Parameters:
        -----------
        height : str, optional
            Height of the visualization
        width : str, optional
            Width of the visualization
        """
        net = Network(height=height, width=width, directed=True, cdn_resources='remote')
        
        # Add nodes with colors and titles
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            label = node_data.get('label', str(node))
            node_type = node_data.get('type', 'expression')
            color = self.colors.get(node_type, '#DDA0DD')
            
            title = f"{node_type.title()}: {label}"
            net.add_node(node, label=label, color=color, title=title, size=25)
        
        # Add edges
        for source, target, data in self.graph.edges(data=True):
            label = data.get('label', '')
            net.add_edge(source, target, title=label, label=label)
        
        # Configure physics for better layout
        net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=150, spring_strength=0.04)
        
        # Show the network
        net.save_graph("equation_graph.html")
        print(f"Interactive graph saved as 'equation_graph.html'")
        print(f"Equation: {self.equation}")
    
    def save_interactive(self, filename: str):
        """
        Save an interactive pyvis visualization to a file.
        
        Parameters:
        -----------
        filename : str
            Path to save the HTML file
        """
        net = Network(height="600px", width="100%", directed=True, cdn_resources='remote')
        
        # Add nodes
        for node in self.graph.nodes():
            node_data = self.graph.nodes[node]
            label = node_data.get('label', str(node))
            node_type = node_data.get('type', 'expression')
            color = self.colors.get(node_type, '#DDA0DD')
            
            title = f"{node_type.title()}: {label}"
            net.add_node(node, label=label, color=color, title=title, size=25)
        
        # Add edges
        for source, target, data in self.graph.edges(data=True):
            label = data.get('label', '')
            net.add_edge(source, target, title=label, label=label)
        
        # Configure physics for better layout
        net.barnes_hut(gravity=-8000, central_gravity=0.3, spring_length=150, spring_strength=0.04)
        
        # Save to file
        net.save_graph(filename)
        print(f"Interactive graph saved as '{filename}'")
    
    def plot_function(self, func_range: Tuple[float, float], num_points: int = 100):
        """
        Plot the function if the equation represents a function.
        
        Parameters:
        -----------
        func_range : tuple
            Range as (min, max) for x values
        num_points : int, optional
            Number of points to evaluate
        """
        if '=' not in self.equation:
            print("Not a function equation. Skipping function plot.")
            return
        
        try:
            left, right = self.equation.split('=')
            
            # Try to parse as y = f(x)
            if 'y' in left and 'y' not in right:
                # y = f(x)
                x = sp.Symbol('x')
                expr = parse_expr(right.strip())
                func = sp.lambdify(x, expr, 'numpy')
                
                x_vals = np.linspace(func_range[0], func_range[1], num_points)
                y_vals = func(x_vals)
                
                plt.figure(figsize=(10, 6))
                plt.plot(x_vals, y_vals, linewidth=2, color='#4ECDC4')
                plt.grid(True, alpha=0.3)
                plt.xlabel('x', fontsize=12)
                plt.ylabel('y', fontsize=12)
                plt.title(f'Function Plot: {self.equation}', fontsize=14, fontweight='bold')
                plt.axhline(y=0, color='k', linewidth=0.5)
                plt.axvline(x=0, color='k', linewidth=0.5)
                plt.tight_layout()
                plt.show()
            else:
                print("Could not determine function form. Expected y = f(x).")
        except Exception as e:
            print(f"Error plotting function: {e}")
    
    def _get_hierarchical_pos(self):
        """
        Calculate hierarchical positions for nodes based on their level.
        
        Returns:
        --------
        dict
            Dictionary mapping node IDs to (x, y) positions
        """
        # Group nodes by level
        levels = {}
        for node in self.graph.nodes():
            level = self.graph.nodes[node].get('level', 0)
            if level not in levels:
                levels[level] = []
            levels[level].append(node)
        
        # Calculate positions
        pos = {}
        max_width = max(len(nodes) for nodes in levels.values()) if levels else 1
        
        for level, nodes in levels.items():
            y = -level  # Top to bottom
            num_nodes = len(nodes)
            for i, node in enumerate(nodes):
                x = (i - num_nodes / 2) * (max_width / (num_nodes + 1))
                pos[node] = (x, y)
        
        return pos
    
    def save_static(self, filename: str, figsize: Tuple[int, int] = (12, 8), dpi: int = 300):
        """
        Save a static matplotlib visualization to a file.
        
        Parameters:
        -----------
        filename : str
            Path to save the image file
        figsize : tuple, optional
            Figure size as (width, height)
        dpi : int, optional
            Resolution in dots per inch
        """
        plt.figure(figsize=figsize)
        
        pos = self._get_hierarchical_pos()
        node_colors = [self.colors.get(self.graph.nodes[node].get('type', 'expression'), '#DDA0DD')
                      for node in self.graph.nodes()]
        labels = {node: self.graph.nodes[node].get('label', str(node))
                 for node in self.graph.nodes()}
        
        nx.draw(self.graph, pos,
                node_color=node_colors,
                node_size=2000,
                labels=labels,
                font_size=10,
                font_weight='bold',
                arrows=True,
                arrowsize=20,
                edge_color='gray',
                alpha=0.9,
                with_labels=True)
        
        if self.equation:
            plt.title(f"Graph Structure: {self.equation}", fontsize=14, fontweight='bold')
        else:
            plt.title("Equation Graph Structure", fontsize=14, fontweight='bold')
        
        legend_elements = [plt.Line2D([0], [0], marker='o', color='w',
                                     markerfacecolor=color, markersize=10, label=node_type.title())
                          for node_type, color in self.colors.items()]
        plt.legend(handles=legend_elements, loc='upper right')
        
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(filename, dpi=dpi, bbox_inches='tight')
        plt.close()
        print(f"Static graph saved as '{filename}'")
