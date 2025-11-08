from codebase import mixed_graph as mixed
from codebase import metrics
import json
import pytest
from ..tests import Graphs_for_testing as G_testing


@pytest.fixture
def test_graphs():
    graphs = G_testing.generate_graphs()
    return {
        'G1': graphs['cyclic'],
        'G2': graphs['chain'], 
        'G3': graphs['empty']
    }

# Load ground truth values
def load_ground_truth():
    with open('tests/test_answers/test_sc_metric_cyclic_answers.json', 'r') as f:
        return json.load(f)

ground_truth = load_ground_truth()

def test_metric_directed_cyclic_graphs_cases(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G3 = test_graphs['G3']

    assert metrics.metric_directed_cyclic_graphs(G3,G1,type ='sc', max_order=None, randomize_higher_order = 0, normalized= True) == ground_truth['metric_directed_cyclic_graphs(empty,G1,type =sc, max_order=None, randomize_higher_order = 0, normalized= True)']
    assert metrics.metric_directed_cyclic_graphs(G3,G1,type ='s', max_order=None, randomize_higher_order = 0, normalized= True) == ground_truth['metric_directed_cyclic_graphs(empty,G1,type =s, max_order=None, randomize_higher_order = 0, normalized= True)']
    assert metrics.metric_directed_cyclic_graphs(G3,G1,type ='c', max_order=None, randomize_higher_order = 0, normalized= True) == ground_truth['metric_directed_cyclic_graphs(empty,G1,type =c, max_order=None, randomize_higher_order = 0, normalized= True)']
    assert metrics.metric_directed_cyclic_graphs(G2,G1,type ='sc', max_order=None, randomize_higher_order = 0, normalized= True) == ground_truth['metric_directed_cyclic_graphs(G2,G1,type =sc, max_order=None, randomize_higher_order = 0, normalized= True)']
