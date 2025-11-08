"""
Graph Builder Module
Builds NetworkX graph structures from parsed equation data.
"""

import networkx as nx
from typing import List, Dict


class GraphBuilder:
    """
    Builds a NetworkX graph from parsed equation nodes and edges.
    """
    
    def __init__(self, nodes: List[Dict], edges: List[Dict]):
        """
        Initialize the graph builder.
        
        Parameters:
        -----------
        nodes : list
            List of node dictionaries with 'id', 'label', 'type', etc.
        edges : list
            List of edge dictionaries with 'source', 'target', 'label'
        """
        self.nodes = nodes
        self.edges = edges
        self.graph = nx.DiGraph()
        
    def build(self) -> nx.DiGraph:
        """
        Build the NetworkX graph.
        
        Returns:
        --------
        networkx.DiGraph
            Directed graph representing the equation structure
        """
        # Add nodes with attributes
        for node in self.nodes:
            node_id = node['id']
            self.graph.add_node(
                node_id,
                label=node['label'],
                type=node['type'],
                level=node.get('level', 0)
            )
        
        # Add edges with attributes
        for edge in self.edges:
            self.graph.add_edge(
                edge['source'],
                edge['target'],
                label=edge.get('label', '')
            )
        
        return self.graph
    
    def get_stats(self) -> Dict:
        """
        Get statistics about the graph.
        
        Returns:
        --------
        dict
            Dictionary with graph statistics
        """
        stats = {
            'num_nodes': self.graph.number_of_nodes(),
            'num_edges': self.graph.number_of_edges(),
            'num_variables': len([n for n, d in self.graph.nodes(data=True) 
                                 if d.get('type') == 'variable']),
            'num_operators': len([n for n, d in self.graph.nodes(data=True) 
                                 if d.get('type') == 'operator']),
            'num_constants': len([n for n, d in self.graph.nodes(data=True) 
                                 if d.get('type') == 'constant']),
            'max_depth': max([d.get('level', 0) for _, d in self.graph.nodes(data=True)]) 
                        if self.graph.number_of_nodes() > 0 else 0
        }
        return stats
    
    def get_variables(self) -> List[str]:
        """
        Get all variable nodes in the graph.
        
        Returns:
        --------
        list
            List of variable labels
        """
        return [d['label'] for _, d in self.graph.nodes(data=True) 
                if d.get('type') == 'variable']
    
    def to_undirected(self) -> nx.Graph:
        """
        Convert the directed graph to an undirected graph.
        
        Returns:
        --------
        networkx.Graph
            Undirected version of the graph
        """
        return self.graph.to_undirected()
    
    def export_graphml(self, filename: str):
        """
        Export the graph to GraphML format.
        
        Parameters:
        -----------
        filename : str
            Path to save the GraphML file
        """
        nx.write_graphml(self.graph, filename)
    
    def export_gexf(self, filename: str):
        """
        Export the graph to GEXF format.
        
        Parameters:
        -----------
        filename : str
            Path to save the GEXF file
        """
        nx.write_gexf(self.graph, filename)
