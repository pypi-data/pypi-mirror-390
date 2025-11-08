# numgraph

[![PyPI version](https://badge.fury.io/py/numgraph-equation.svg)](https://pypi.org/project/numgraph-equation/)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

A Python library that converts mathematical equations into graph/network structures for visualization and analysis.

## What is numgraph?

numgraph turns mathematical relationships into nodes and edges, then visualizes them as interactive graphs. This helps users understand how variables and operations interact.

**Use cases:**
- Students learning algebra and calculus
- Data scientists analyzing feature dependencies
- Researchers visualizing mathematical formulas

## Quick Start

### Installation

Install from PyPI:
```bash
pip install numgraph-equation
```

Or install from source:
```bash
git clone https://github.com/Ayush-07-Mishra/numgraph.git
cd numgraph
pip install -e .
```

### Basic Usage

```python
from numgraph import make_graph

# Parse and visualize an equation
make_graph("x**2 + y**2 = 25", visualize=True)

# Create a function graph
make_graph("y = x**2 - 4*x + 3", func_range=(-10, 10), visualize=True)
```

## Features

- Parse mathematical equations using SymPy
- Build graph structures with NetworkX
- Interactive HTML visualizations with PyVis
- Static plots with Matplotlib
- Export to GraphML and GEXF formats
- Function plotting with custom ranges

## Examples

### Circle Equation

```python
from numgraph import make_graph

# Visualize the circle equation
make_graph("x**2 + y**2 = 25", visualize=True, save_path="circle.html")
```

### Quadratic Function

```python
from numgraph import make_graph

# Plot a parabola
make_graph("y = x**2 - 4*x + 3", func_range=(-2, 6), visualize=True)
```

### Custom Graph Analysis

```python
from numgraph.parser import EquationParser
from numgraph.graph_builder import GraphBuilder
from numgraph.visualizer import Visualizer

# Parse equation
parser = EquationParser("x**2 + 2*x*y + y**2 = 16")
nodes, edges = parser.parse()

# Build graph
builder = GraphBuilder(nodes, edges)
graph = builder.build()

# Visualize
viz = Visualizer(graph)
viz.show_interactive()  # Interactive HTML visualization
viz.show_static()       # Static matplotlib plot
```

## API Reference

### make_graph(equation, visualize=False, func_range=None, save_path=None)

Main function to create and optionally visualize equation graphs.

**Parameters:**
- `equation` (str): Mathematical equation or function
- `visualize` (bool): Whether to show visualization
- `func_range` (tuple): Range for function evaluation (min, max)
- `save_path` (str): Path to save interactive HTML visualization

**Returns:**
- `networkx.Graph`: Graph representation of the equation

## Project Structure

```
numgraph/
├── numgraph/
│   ├── __init__.py         # Main API
│   ├── parser.py           # Equation parsing
│   ├── graph_builder.py    # Graph creation
│   ├── visualizer.py       # Visualization
│   └── dataset.py          # Dataset utilities
├── examples/
│   ├── circle_equation.py
│   ├── quadratic_function.py
│   └── custom_analysis.py
├── tests/
│   ├── test_parser.py
│   ├── test_graph_builder.py
│   └── test_visualizer.py
├── setup.py
├── README.md
└── requirements.txt
```

## Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_parser.py -v
```

## Dependencies

- sympy - Symbolic mathematics and parsing
- networkx - Graph creation and analysis
- pyvis - Interactive network visualization
- matplotlib - Static plotting
- numpy - Numerical computations

## Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details.

## Contact

For questions or support: luckymishra312004@gmail.com

### For Students
- Visualize how equations are structured
- Understand operator precedence
- See variable relationships clearly

### For Educators
## Contact

For questions or support: luckymishra312004@gmail.com
