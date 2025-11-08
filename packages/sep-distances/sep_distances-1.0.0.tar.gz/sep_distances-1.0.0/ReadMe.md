This repository provides an implementation of separation distances and s/c-metrics
for causal graphs as introduced in the paper ['Separation-based distance metrics for causal graphs'](https://proceedings.mlr.press/v258/wahl25b.html).

Below is a short description of the important source files and how to use them.

## Files

- [`codebase/mixed_graph.py`](./codebase/mixed_graph.py)
	- Contains the `LabelledMixedGraph` class: a compact representation for directed, undirected,
		bidirected and semidirected edges. Useful helpers include conversion to/from NetworkX,
		adding/removing edges, methods to compute skeletons and CPDAGs, finding v-structures,
		computing Markov blankets, BayesBall, minimal d-separators and several converters
		(`get_canonical_directed_graph`, `get_acyclification`, etc.). This is the main graph data
		structure used by the metrics.

- [`codebase/metrics.py`](./codebase/metrics.py)
	- Implements the distance/metric functions comparing two graphs. Major groups of functions:
		- SHD (Structural Hamming Distance) for DAGs/CPDAGs/MAGs: `SHD_DAGs`, `SHD_CPDAGs`, `SHD_MAGs`.
		- AID (Adjustment Identification Distances) wrappers using `gadjid` (e.g. `parent_AID_DAGs`).
		- Separation distances (SD) for DAGs, CPDAGs, and mixed graphs: `SD_DAGs`, `SD_CPDAGs`, `SD_mixed_graphs`.
		- s/c-metrics and variants (s-metric, c-metric, sc-metric) for DAGs, CPDAGs, mixed graphs and
			graphs with cycles (`metric_DAGs`, `metric_CPDAGs`, `metric_mixed_graphs`, `metric_directed_cyclic_graphs`).
		- Utilities: `generate_triples` (create separation statements) and several helper wrappers.

- [`tests/`](./tests/)
	- Unit tests covering behavior of `mixed_graph.py` and `metrics.py`. The tests include many focused
		test cases (CPDAGs, DAGs, mixed graphs, AIDs, SHD, SD, s/c metrics, and related helpers). Run them
		with `pytest` (instructions below).

## Quick examples

Basic usage pattern in [example.py](example.py) (import, construct graphs, compute a metric):

```python
from codebase import mixed_graph as mg
from codebase import metrics as metrics

# create two simple DAGs
G1 = mg.LabelledMixedGraph(nodes={"A", "B", "C"})
G1.add_directed("A", "B")
G1.add_directed("B", "C")

G2 = mg.LabelledMixedGraph(nodes={"A", "B", "C"})
G2.add_directed("A", "B")
G2.add_directed("A", "C")

# Compute SHD (Structural Hamming Distance) between DAGs
shd = metrics.SHD_DAGs(G1, G2, normalized=True)
print("SHD (normalized):", shd)

# Compute separation distance (SD) using parent separation
sd = metrics.SD_DAGs(G1, G2, type='parent', normalized=True)
print("SD (parent, normalized):", sd)

# Compute an sc-metric between DAGs (default uses all orders)
sc = metrics.metric_DAGs(G1, G2, type='sc', normalized=True)
print("sc-metric:", sc)
```

Notes:
- Many metric functions expect the same node set in both graphs. They typically check `graph1.nodes == graph2.nodes`.
- For CPDAGs some functions compute or require a representative DAG of the MEC (see `get_representative_of_MEC`).
- AID functions rely on the external `gadjid` package; install it to use those functions.

## Running tests

1. Install dependencies (recommended in a virtual environment):

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. Run the test suite with pytest from the project root:

```bash
pytest -q
```

If you only want to run a single test file, use e.g. `pytest -q tests/test_SHD.py`.

Currently, the test suite does not have any tests configured. Instead you should use run it once to check if all the requirements are installed correctly and as example usage for the respective metrics.

If you want to run a test file directly, you need to change the way the imports are called. Currently the imports are structured in a way that work well with pytest, but won't work if you run the file directly.

Example change in [tests/test_AIDs.py](tests/test_AIDs.py).:
```python
''' Comment out current imports '''
# from codebase import mixed_graph as mixed
# from codebase import metrics

# from ..tests import Graphs_for_testing as G_testing

''' Replace with the following '''
import os
import sys

# add project root to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from codebase import mixed_graph as mixed
from codebase import metrics

import Graphs_for_testing as G_testing
```

## Installation / requirements

- Python 3.10+ is required (see [`setup.cfg`](setup.cfg)).
- The project depends on packages listed in [`requirements.txt`](requirements.txt) / [`setup.cfg`](setup.cfg). Notable dependencies:
	- `networkx`, `numpy`, `scipy`, `gadjid` (optional but required for AID functions).

## License

This project is released under the GNU General Public License v3 (GPLv3). See [`LICENSE.txt`](LICENSE.txt) for the full text.

## Contact & attribution

Original research and initial code: Jonas Wahl & Jakob Runge
Package implementation and maintenance: Muhammad Haris Owais Ahmed

If you have questions, bug reports, or performance suggestions, please open an issue or contact the maintainers listed in [`setup.cfg`](setup.cfg).