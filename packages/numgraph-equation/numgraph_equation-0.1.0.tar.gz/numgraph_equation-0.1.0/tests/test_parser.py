"""
Tests for the EquationParser module
"""

import pytest
from numgraph.parser import EquationParser


class TestEquationParser:
    
    def test_simple_equation(self):
        """Test parsing a simple equation"""
        parser = EquationParser("x**2 + y**2 = 25")
        nodes, edges = parser.parse()
        
        assert len(nodes) > 0
        assert len(edges) > 0
        
        # Check that we have an equation node
        eq_nodes = [n for n in nodes if n['type'] == 'operator' and n['label'] == '=']
        assert len(eq_nodes) == 1
    
    def test_variable_extraction(self):
        """Test extracting variables from equation"""
        parser = EquationParser("x**2 + y**2 = 25")
        nodes, edges = parser.parse()
        variables = parser.get_variables()
        
        assert 'x' in variables
        assert 'y' in variables
        assert len(variables) == 2
    
    def test_operator_extraction(self):
        """Test extracting operators from equation"""
        parser = EquationParser("x**2 + y**2 = 25")
        nodes, edges = parser.parse()
        operators = parser.get_operators()
        
        assert '+' in operators
        assert '=' in operators
    
    def test_linear_equation(self):
        """Test parsing a linear equation"""
        parser = EquationParser("y = 2*x + 3")
        nodes, edges = parser.parse()
        
        assert len(nodes) > 0
        variables = parser.get_variables()
        assert 'x' in variables
        assert 'y' in variables
    
    def test_quadratic_equation(self):
        """Test parsing a quadratic equation"""
        parser = EquationParser("y = x**2 - 4*x + 3")
        nodes, edges = parser.parse()
        
        assert len(nodes) > 0
        variables = parser.get_variables()
        assert 'x' in variables
        assert 'y' in variables
    
    def test_expression_only(self):
        """Test parsing just an expression (no equals)"""
        parser = EquationParser("x**2 + 2*x + 1")
        nodes, edges = parser.parse()
        
        assert len(nodes) > 0
        variables = parser.get_variables()
        assert 'x' in variables
    
    def test_complex_expression(self):
        """Test parsing a more complex expression"""
        parser = EquationParser("x**2 + 2*x*y + y**2 = 16")
        nodes, edges = parser.parse()
        
        assert len(nodes) > 0
        variables = parser.get_variables()
        assert 'x' in variables
        assert 'y' in variables


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
