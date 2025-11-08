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
        'G2': graphs['undirected_chain'], 
        'G3': graphs['empty']
    }

# Load ground truth values
def load_ground_truth():
    with open('tests/test_answers/test_SD_CPDAGs_answers.json', 'r') as f:
        return json.load(f)

ground_truth = load_ground_truth()


#------------------pparent-------------------------

def test_SD_CPDAGs_pparent(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G3 = test_graphs['G3']

    result = metrics.SD_CPDAGs(G3, G1, type='pparent')
    assert result == ground_truth['SD_CPDAGs(empty,G1,type=pparent)']

    result = metrics.SD_CPDAGs(G3, G2, type='pparent')
    assert result == ground_truth['SD_CPDAGs(empty,G2,type=pparent)']

    result = metrics.SD_CPDAGs(G1, G2, type='pparent')
    assert result == ground_truth['SD_CPDAGs(G1,G2,type=pparent)']

    result = metrics.SD_CPDAGs(G2, G1, type='pparent')
    assert result == ground_truth['SD_CPDAGs(G2,G1,type=pparent)']

    result = metrics.SD_CPDAGs(G1, G1, type='pparent')
    assert result == ground_truth['SD_CPDAGs(G1,G1,type=pparent)']


#------------------MB-enhanced pparent-------------------------

def test_SD_CPDAGs_MB_enhanced_pparent(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G3 = test_graphs['G3']

    result = metrics.SD_CPDAGs(G3, G1, type='pparent', MB_enhanced=True)
    assert result == ground_truth['SD_CPDAGs(empty,G1,type=pparent,MB_enhanced=True)']

    result = metrics.SD_CPDAGs(G3, G2, type='pparent', MB_enhanced=True)
    assert result == ground_truth['SD_CPDAGs(empty,G2,type=pparent,MB_enhanced=True)']

    result = metrics.SD_CPDAGs(G1, G2, type='pparent', MB_enhanced=True)
    assert result == ground_truth['SD_CPDAGs(G1,G2,type=pparent,MB_enhanced=True)']

    result = metrics.SD_CPDAGs(G2, G1, type='pparent', MB_enhanced=True)
    assert result == ground_truth['SD_CPDAGs(G2,G1,type=pparent,MB_enhanced=True)']

    result = metrics.SD_CPDAGs(G1, G1, type='pparent', MB_enhanced=True)
    assert result == ground_truth['SD_CPDAGs(G1,G1,type=pparent,MB_enhanced=True)']


#------------------pancestor-------------------------

def test_SD_CPDAGs_pancestor(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G3 = test_graphs['G3']

    result = metrics.SD_CPDAGs(G3, G1, type='pancestor')
    assert result == ground_truth['SD_CPDAGs(empty,G1,type=pancestor)']

    result = metrics.SD_CPDAGs(G3, G2, type='pancestor')
    assert result == ground_truth['SD_CPDAGs(empty,G2,type=pancestor)']

    result = metrics.SD_CPDAGs(G1, G2, type='pancestor')
    assert result == ground_truth['SD_CPDAGs(G1,G2,type=pancestor)']

    result = metrics.SD_CPDAGs(G2, G1, type='pancestor')
    assert result == ground_truth['SD_CPDAGs(G2,G1,type=pancestor)']

    result = metrics.SD_CPDAGs(G1, G1, type='pancestor')
    assert result == ground_truth['SD_CPDAGs(G1,G1,type=pancestor)']


#------------------ZL-------------------------

def test_SD_CPDAGs_ZL(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G3 = test_graphs['G3']

    result = metrics.SD_CPDAGs(G3, G1, type='ZL')
    assert result == ground_truth['SD_CPDAGs(empty,G1,type=ZL)']

    result = metrics.SD_CPDAGs(G3, G2, type='ZL')
    assert result == ground_truth['SD_CPDAGs(empty,G2,type=ZL)']

    result = metrics.SD_CPDAGs(G1, G2, type='ZL')
    assert result == ground_truth['SD_CPDAGs(G1,G2,type=ZL)']

    result = metrics.SD_CPDAGs(G2, G1, type='ZL')
    assert result == ground_truth['SD_CPDAGs(G2,G1,type=ZL)']

    result = metrics.SD_CPDAGs(G1, G1, type='ZL')
    assert result == ground_truth['SD_CPDAGs(G1,G1,type=ZL)']


#------------------MB-enhanced ZL-------------------------

def test_SD_CPDAGs_MB_enhanced_ZL(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G3 = test_graphs['G3']

    result = metrics.SD_CPDAGs(G3, G1, type='ZL', MB_enhanced=True)
    assert result == ground_truth['SD_CPDAGs(empty,G1,type=ZL,MB_enhanced=True)']

    result = metrics.SD_CPDAGs(G3, G2, type='ZL', MB_enhanced=True)
    assert result == ground_truth['SD_CPDAGs(empty,G2,type=ZL,MB_enhanced=True)']

    result = metrics.SD_CPDAGs(G1, G2, type='ZL', MB_enhanced=True)
    assert result == ground_truth['SD_CPDAGs(G1,G2,type=ZL,MB_enhanced=True)']

    result = metrics.SD_CPDAGs(G2, G1, type='ZL', MB_enhanced=True)
    assert result == ground_truth['SD_CPDAGs(G2,G1,type=ZL,MB_enhanced=True)']

    result = metrics.SD_CPDAGs(G1, G1, type='ZL', MB_enhanced=True)
    assert result == ground_truth['SD_CPDAGs(G1,G1,type=ZL,MB_enhanced=True)']
