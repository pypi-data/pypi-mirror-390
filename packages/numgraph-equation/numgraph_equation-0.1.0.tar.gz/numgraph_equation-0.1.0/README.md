# numgraph 🔢➡️📊

[![PyPI version](https://badge.fury.io/py/numgraph.svg)](https://badge.fury.io/py/numgraph)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![CI](https://github.com/ayushmishra/numgraph/workflows/CI/badge.svg)](https://github.com/ayushmishra/numgraph/actions)
[![codecov](https://codecov.io/gh/ayushmishra/numgraph/branch/main/graph/badge.svg)](https://codecov.io/gh/ayushmishra/numgraph)

A Python library that converts mathematical equations, functions, or datasets into graph/network structures for visualization and analysis.

## 🎯 What is numgraph?

**numgraph** turns mathematical relationships into nodes and edges, then visualizes them. This helps users see how variables and operations interact — perfect for:

- 📚 Students learning algebra/calculus
- 🔬 Data scientists analyzing feature dependencies
- 🧪 Researchers visualizing formulas or constraints

## 🚀 Quick Start

### Installation

Install from PyPI (once published):
```bash
pip install numgraph
```

Or install from source:
```bash
git clone https://github.com/ayushmishra/numgraph.git
cd numgraph
pip install -e .
```

For development:
```bash
pip install -e ".[dev]"
```

### Basic Usage

```python
from numgraph import make_graph

# Parse and visualize an equation
make_graph("x**2 + y**2 = 25", visualize=True)

# Create a function graph
make_graph("y = x**2 - 4*x + 3", func_range=(-10, 10), visualize=True)
```

## 📦 Features

### ✅ Phase 1: Core Functionality (MVP)
- Parse mathematical equations using `sympy`
- Build graph structures with `networkx`
- Visualize using `matplotlib` and `pyvis`
- Export graphs to various formats

### 🔮 Phase 2: Function Graphs
- Plot functional relationships
- Show variable dependency graphs
- Evaluate functions over ranges

### 📊 Phase 3: Dataset Integration (Coming Soon)
- Build correlation graphs from DataFrames
- Analyze feature relationships
- Threshold-based edge creation

### 🧠 Phase 4: Advanced Features (Planned)
- Auto-detect independent/dependent variables
- Bipartite graph visualization
- Export to `.graphml`, `.png`, etc.
- AI-based function simplification

## 📖 Examples

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

## 🛠️ API Reference

### `make_graph(equation, visualize=False, func_range=None, save_path=None)`

Main function to create and optionally visualize equation graphs.

**Parameters:**
- `equation` (str): Mathematical equation or function
- `visualize` (bool): Whether to show visualization
- `func_range` (tuple): Range for function evaluation (min, max)
- `save_path` (str): Path to save interactive HTML visualization

**Returns:**
- `networkx.Graph`: Graph representation of the equation

## 🏗️ Project Structure

```
numgraph/
│
├── numgraph/
│   ├── __init__.py         # Main API
│   ├── parser.py           # Equation parsing logic
│   ├── graph_builder.py    # NetworkX graph creation
│   ├── visualizer.py       # Matplotlib/Pyvis visualization
│   └── dataset.py          # Dataset → graph (future)
│
├── examples/
│   ├── circle_equation.py
│   ├── quadratic_function.py
│   └── custom_analysis.py
│
├── tests/
│   ├── test_parser.py
│   ├── test_graph_builder.py
│   └── test_visualizer.py
│
├── setup.py
├── README.md
└── requirements.txt
```

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test
python -m pytest tests/test_parser.py -v
```

## 📄 License

MIT License - feel free to use this project however you'd like!

## 🤝 Contributing

Contributions are welcome! Please read [CONTRIBUTING.md](CONTRIBUTING.md) for details on our code of conduct and the process for submitting pull requests.

## 📝 Publishing

To publish this package to PyPI for others to use, see [PUBLISHING.md](PUBLISHING.md) for detailed instructions.

## 📋 Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and release notes.

## 🔗 Tech Stack

- **sympy** → Symbolic mathematics and parsing
- **networkx** → Graph creation and analysis
- **pyvis** → Interactive network visualization
- **matplotlib** → Static plotting
- **numpy** → Numerical computations

## 🎓 Use Cases

### For Students
- Visualize how equations are structured
- Understand operator precedence
- See variable relationships clearly

### For Educators
- Create interactive math visualizations
- Demonstrate equation parsing
- Teaching tool for graph theory

### For Researchers
- Analyze mathematical formula structure
- Study equation complexity
- Visualize algorithm dependencies

### For Developers
- Parse mathematical expressions
- Build equation-based applications
- Create mathematical documentation

## 📮 Contact

For questions or suggestions, please open an issue on GitHub.

## ⭐ Show Your Support

If you find numgraph helpful, please give it a star on GitHub!

## 🙏 Acknowledgments

Built with these amazing libraries:
- [SymPy](https://www.sympy.org/) - Symbolic mathematics
- [NetworkX](https://networkx.org/) - Complex networks
- [Matplotlib](https://matplotlib.org/) - Plotting library
- [PyVis](https://pyvis.readthedocs.io/) - Interactive visualizations

---

Made with ❤️ for math and graph enthusiasts!
