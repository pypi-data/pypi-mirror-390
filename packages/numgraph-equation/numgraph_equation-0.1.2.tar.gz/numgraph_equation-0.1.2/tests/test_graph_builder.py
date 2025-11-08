"""
Tests for the GraphBuilder module
"""

import pytest
import networkx as nx
from numgraph.parser import EquationParser
from numgraph.graph_builder import GraphBuilder


class TestGraphBuilder:
    
    def test_build_graph(self):
        """Test building a graph from parsed data"""
        parser = EquationParser("x**2 + y**2 = 25")
        nodes, edges = parser.parse()
        
        builder = GraphBuilder(nodes, edges)
        graph = builder.build()
        
        assert isinstance(graph, nx.DiGraph)
        assert graph.number_of_nodes() > 0
        assert graph.number_of_edges() > 0
    
    def test_graph_stats(self):
        """Test getting graph statistics"""
        parser = EquationParser("x**2 + y**2 = 25")
        nodes, edges = parser.parse()
        
        builder = GraphBuilder(nodes, edges)
        graph = builder.build()
        stats = builder.get_stats()
        
        assert 'num_nodes' in stats
        assert 'num_edges' in stats
        assert 'num_variables' in stats
        assert 'num_operators' in stats
        assert 'num_constants' in stats
        assert stats['num_variables'] >= 2  # x and y
    
    def test_get_variables(self):
        """Test extracting variables from the graph"""
        parser = EquationParser("x**2 + y**2 = 25")
        nodes, edges = parser.parse()
        
        builder = GraphBuilder(nodes, edges)
        graph = builder.build()
        variables = builder.get_variables()
        
        assert 'x' in variables
        assert 'y' in variables
    
    def test_to_undirected(self):
        """Test converting to undirected graph"""
        parser = EquationParser("y = x**2")
        nodes, edges = parser.parse()
        
        builder = GraphBuilder(nodes, edges)
        directed = builder.build()
        undirected = builder.to_undirected()
        
        assert isinstance(directed, nx.DiGraph)
        assert isinstance(undirected, nx.Graph)
        assert undirected.number_of_nodes() == directed.number_of_nodes()
    
    def test_export_graphml(self, tmp_path):
        """Test exporting to GraphML format"""
        parser = EquationParser("x**2 = 4")
        nodes, edges = parser.parse()
        
        builder = GraphBuilder(nodes, edges)
        graph = builder.build()
        
        output_file = tmp_path / "test.graphml"
        builder.export_graphml(str(output_file))
        
        assert output_file.exists()
    
    def test_export_gexf(self, tmp_path):
        """Test exporting to GEXF format"""
        parser = EquationParser("x**2 = 4")
        nodes, edges = parser.parse()
        
        builder = GraphBuilder(nodes, edges)
        graph = builder.build()
        
        output_file = tmp_path / "test.gexf"
        builder.export_gexf(str(output_file))
        
        assert output_file.exists()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
