"""
Equation Parser Module
Parses mathematical equations into nodes and edges using sympy.
"""

import sympy as sp
from sympy.parsing.sympy_parser import parse_expr
from typing import List, Tuple, Set


class EquationParser:
    """
    Parses mathematical equations and extracts nodes (variables, operations, constants)
    and edges (relationships between them).
    """
    
    def __init__(self, equation: str):
        """
        Initialize the parser with an equation string.
        
        Parameters:
        -----------
        equation : str
            Mathematical equation (e.g., "x**2 + y**2 = 25")
        """
        self.equation = equation
        self.nodes = []
        self.edges = []
        self.expr = None
        
    def parse(self) -> Tuple[List[dict], List[dict]]:
        """
        Parse the equation into nodes and edges.
        
        Returns:
        --------
        tuple
            (nodes, edges) where nodes is a list of dicts with node info
            and edges is a list of dicts with edge info
        """
        # Handle equations with '='
        if '=' in self.equation:
            left, right = self.equation.split('=')
            left_expr = parse_expr(left.strip())
            right_expr = parse_expr(right.strip())
            
            # Create equation node
            eq_node = {
                'id': 'equation',
                'label': '=',
                'type': 'operator',
                'level': 0
            }
            self.nodes.append(eq_node)
            
            # Parse left side
            left_root = self._parse_expression(left_expr, level=1, side='left')
            self.edges.append({
                'source': left_root,
                'target': 'equation',
                'label': 'left'
            })
            
            # Parse right side
            right_root = self._parse_expression(right_expr, level=1, side='right')
            self.edges.append({
                'source': right_root,
                'target': 'equation',
                'label': 'right'
            })
        else:
            # Just an expression
            expr = parse_expr(self.equation.strip())
            self._parse_expression(expr, level=0)
        
        return self.nodes, self.edges
    
    def _parse_expression(self, expr, level=0, side='', parent_id=None) -> str:
        """
        Recursively parse a sympy expression into nodes and edges.
        
        Parameters:
        -----------
        expr : sympy.Expr
            Sympy expression to parse
        level : int
            Depth level in the tree
        side : str
            Which side of equation ('left', 'right', or '')
        parent_id : str
            ID of parent node
            
        Returns:
        --------
        str
            ID of the root node of this expression
        """
        node_id = f"{side}_{str(expr)}_{level}_{len(self.nodes)}"
        
        # Determine node type and create node
        if isinstance(expr, sp.Symbol):
            # Variable
            node = {
                'id': node_id,
                'label': str(expr),
                'type': 'variable',
                'level': level
            }
        elif isinstance(expr, sp.Number):
            # Constant
            node = {
                'id': node_id,
                'label': str(expr),
                'type': 'constant',
                'level': level
            }
        elif isinstance(expr, sp.Add):
            # Addition
            node = {
                'id': node_id,
                'label': '+',
                'type': 'operator',
                'level': level
            }
            self.nodes.append(node)
            
            # Parse operands
            for arg in expr.args:
                child_id = self._parse_expression(arg, level + 1, side)
                self.edges.append({
                    'source': child_id,
                    'target': node_id,
                    'label': 'operand'
                })
            return node_id
            
        elif isinstance(expr, sp.Mul):
            # Multiplication
            node = {
                'id': node_id,
                'label': '*',
                'type': 'operator',
                'level': level
            }
            self.nodes.append(node)
            
            # Parse operands
            for arg in expr.args:
                child_id = self._parse_expression(arg, level + 1, side)
                self.edges.append({
                    'source': child_id,
                    'target': node_id,
                    'label': 'operand'
                })
            return node_id
            
        elif isinstance(expr, sp.Pow):
            # Power
            base, exp = expr.args
            node = {
                'id': node_id,
                'label': f'^{exp}',
                'type': 'operator',
                'level': level
            }
            self.nodes.append(node)
            
            # Parse base
            base_id = self._parse_expression(base, level + 1, side)
            self.edges.append({
                'source': base_id,
                'target': node_id,
                'label': 'base'
            })
            
            # Parse exponent if it's complex
            if not isinstance(exp, sp.Number):
                exp_id = self._parse_expression(exp, level + 1, side)
                self.edges.append({
                    'source': exp_id,
                    'target': node_id,
                    'label': 'exponent'
                })
            return node_id
            
        elif isinstance(expr, sp.Function):
            # Function (sin, cos, etc.)
            node = {
                'id': node_id,
                'label': expr.func.__name__,
                'type': 'function',
                'level': level
            }
            self.nodes.append(node)
            
            # Parse arguments
            for arg in expr.args:
                arg_id = self._parse_expression(arg, level + 1, side)
                self.edges.append({
                    'source': arg_id,
                    'target': node_id,
                    'label': 'argument'
                })
            return node_id
        else:
            # Generic expression
            node = {
                'id': node_id,
                'label': str(expr),
                'type': 'expression',
                'level': level
            }
        
        self.nodes.append(node)
        return node_id
    
    def get_variables(self) -> Set[str]:
        """
        Extract all variables from the equation.
        
        Returns:
        --------
        set
            Set of variable names
        """
        return {node['label'] for node in self.nodes if node['type'] == 'variable'}
    
    def get_operators(self) -> Set[str]:
        """
        Extract all operators from the equation.
        
        Returns:
        --------
        set
            Set of operator symbols
        """
        return {node['label'] for node in self.nodes if node['type'] == 'operator'}
