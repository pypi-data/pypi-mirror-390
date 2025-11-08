"""
Tests for the Visualizer module
"""

import pytest
import networkx as nx
from numgraph.parser import EquationParser
from numgraph.graph_builder import GraphBuilder
from numgraph.visualizer import Visualizer


class TestVisualizer:
    
    def test_visualizer_init(self):
        """Test initializing the visualizer"""
        parser = EquationParser("x**2 + y**2 = 25")
        nodes, edges = parser.parse()
        
        builder = GraphBuilder(nodes, edges)
        graph = builder.build()
        
        viz = Visualizer(graph, equation="x**2 + y**2 = 25")
        assert viz.graph == graph
        assert viz.equation == "x**2 + y**2 = 25"
    
    def test_save_interactive(self, tmp_path):
        """Test saving interactive HTML visualization"""
        parser = EquationParser("x**2 = 4")
        nodes, edges = parser.parse()
        
        builder = GraphBuilder(nodes, edges)
        graph = builder.build()
        
        viz = Visualizer(graph, equation="x**2 = 4")
        output_file = tmp_path / "test_graph.html"
        viz.save_interactive(str(output_file))
        
        assert output_file.exists()
    
    def test_save_static(self, tmp_path):
        """Test saving static PNG visualization"""
        parser = EquationParser("x**2 = 4")
        nodes, edges = parser.parse()
        
        builder = GraphBuilder(nodes, edges)
        graph = builder.build()
        
        viz = Visualizer(graph, equation="x**2 = 4")
        output_file = tmp_path / "test_graph.png"
        viz.save_static(str(output_file))
        
        assert output_file.exists()
    
    def test_hierarchical_pos(self):
        """Test hierarchical position calculation"""
        parser = EquationParser("x + y = 5")
        nodes, edges = parser.parse()
        
        builder = GraphBuilder(nodes, edges)
        graph = builder.build()
        
        viz = Visualizer(graph)
        pos = viz._get_hierarchical_pos()
        
        assert isinstance(pos, dict)
        assert len(pos) == graph.number_of_nodes()
        
        # Check that positions are tuples of (x, y)
        for node_id, position in pos.items():
            assert isinstance(position, tuple)
            assert len(position) == 2


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
