import json
import pytest

from codebase import metrics

from ..tests import Graphs_for_testing as G_testing

@pytest.fixture
def test_graphs():
    graphs = G_testing.generate_graphs()
    return {
        'G1': graphs['chain'],
        'G2': graphs['empty'], 
        'G3': graphs['undirected_chain'],
        'G4': graphs['with_bidirected']
    }

# Load ground truth values
def load_ground_truth():
    with open('tests/test_answers/test_SHD_answers.json', 'r') as f:
        return json.load(f)

ground_truth = load_ground_truth()

def test_SHD_DAGs(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    
    result = metrics.SHD_DAGs(G1, G2, normalized=False)
    assert result == ground_truth['SHD_DAGs(G1,G2,normalized=False)']
    
    result = metrics.SHD_DAGs(G2, G1, normalized=False)
    assert result == ground_truth['SHD_DAGs(G2,G1,normalized=False)']
    
    result = metrics.SHD_DAGs(G1, G2, normalized=True)
    assert result == ground_truth['SHD_DAGs(G1,G2,normalized=True)']
    
    result = metrics.SHD_DAGs(G2, G1, normalized=True)
    assert result == ground_truth['SHD_DAGs(G2,G1,normalized=True)']

def test_SHD_CPDAGs(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G3 = test_graphs['G3']

    result = metrics.SHD_CPDAGs(G1, G2, normalized=False)
    assert result == ground_truth['SHD_CPDAGs(G1,G2,normalized=False)']

    result = metrics.SHD_CPDAGs(G2, G1, normalized=False)
    assert result == ground_truth['SHD_CPDAGs(G2,G1,normalized=False)']

    result = metrics.SHD_CPDAGs(G1, G2, normalized=True)
    assert result == ground_truth['SHD_CPDAGs(G1,G2,normalized=True)']

    result = metrics.SHD_CPDAGs(G2, G1, normalized=True)
    assert result == ground_truth['SHD_CPDAGs(G2,G1,normalized=True)']

    result = metrics.SHD_CPDAGs(G3, G2, normalized=False)
    assert result == ground_truth['SHD_CPDAGs(G3,G2,normalized=False)']

    result = metrics.SHD_CPDAGs(G2, G3, normalized=False)
    assert result == ground_truth['SHD_CPDAGs(G2,G3,normalized=False)']

    result = metrics.SHD_CPDAGs(G1, G3, normalized=False)
    assert result == ground_truth['SHD_CPDAGs(G1,G3,normalized=False)']

    result = metrics.SHD_CPDAGs(G3, G1, normalized=False)
    assert result == ground_truth['SHD_CPDAGs(G3,G1,normalized=False)']

def test_SHD_MAGs(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G4 = test_graphs['G4']

    result = metrics.SHD_MAGs(G2, G4, normalized=False)
    assert result == ground_truth['SHD_MAGs(G2,G4,normalized=False)']

    result = metrics.SHD_MAGs(G1, G4, normalized=False)
    assert result == ground_truth['SHD_MAGs(G1,G4,normalized=False)']

    result = metrics.SHD_MAGs(G4, G1, normalized=False)
    assert result == ground_truth['SHD_MAGs(G4,G1,normalized=False)']
