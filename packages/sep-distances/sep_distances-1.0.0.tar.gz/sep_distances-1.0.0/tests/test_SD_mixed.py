import json
import pytest

from codebase import mixed_graph as mixed
from codebase import metrics

from ..tests import Graphs_for_testing as G_testing

@pytest.fixture
def test_graphs():
    graphs = G_testing.generate_graphs()
    return {
        'G1': graphs['simple_collider'],
        'G2': graphs['chain'], 
        'G3': graphs['empty'],
        'G4': graphs['with_bidirected'],
        'G5': graphs['empty_4_nodes'],
        'G6': graphs['full_4_nodes']
    }

# Load ground truth values
def load_ground_truth():
    with open('tests/test_answers/test_SD_mixed_answers.json', 'r') as f:
        return json.load(f)

ground_truth = load_ground_truth()


#------------------ZL-------------------------

def test_SD_mixed_graphs_ZL(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G3 = test_graphs['G3']
    G4 = test_graphs['G4']

    result = metrics.SD_mixed_graphs(G3, G1, type='ZL')
    assert result == ground_truth['SD_mixed_graphs(empty,G1,type=ZL)']

    result = metrics.SD_mixed_graphs(G3, G2, type='ZL')
    assert result == ground_truth['SD_mixed_graphs(empty,G2,type=ZL)']

    result = metrics.SD_mixed_graphs(G1, G2, type='ZL')
    assert result == ground_truth['SD_mixed_graphs(G1,G2,type=ZL)']

    result = metrics.SD_mixed_graphs(G2, G1, type='ZL')
    assert result == ground_truth['SD_mixed_graphs(G2,G1,type=ZL)']

    result = metrics.SD_mixed_graphs(G1, G1, type='ZL')
    assert result == ground_truth['SD_mixed_graphs(G1,G1,type=ZL)']

    result = metrics.SD_mixed_graphs(G1, G4, type='ZL')
    assert result == ground_truth['SD_mixed_graphs(G1,G4,type=ZL)']

    result = metrics.SD_mixed_graphs(G4, G1, type='ZL')
    assert result == ground_truth['SD_mixed_graphs(G4,G1,type=ZL)']

    result = metrics.SD_mixed_graphs(G3, G4, type='ZL')
    assert result == ground_truth['SD_mixed_graphs(empty,G4,type=ZL)']

    result = metrics.SD_mixed_graphs(G4, G3, type='ZL')
    assert result == ground_truth['SD_mixed_graphs(G4,empty,type=ZL)']

    G5 = test_graphs['G5']
    G6 = test_graphs['G6']

    result = metrics.SD_mixed_graphs(G5, G6, type='ZL')
    assert result == ground_truth['SD_mixed_graphs(G5,G6,type=ZL)']

    result = metrics.SD_mixed_graphs(G6, G5, type='ZL')
    assert result == ground_truth['SD_mixed_graphs(G6,G5,type=ZL)']
