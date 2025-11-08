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
        'G3': graphs['empty']
    }

# Load ground truth values
def load_ground_truth():
    with open('tests/test_answers/test_SD_DAGs_answers.json', 'r') as f:
        return json.load(f)

ground_truth = load_ground_truth()

#------------------parent-------------------------

def test_SD_DAGs_parent(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G3 = test_graphs['G3']

    result = metrics.SD_DAGs(G3, G1, type='parent')
    assert result == ground_truth['SD_DAGs(empty,G1,type=parent)']

    result = metrics.SD_DAGs(G3, G2, type='parent')
    assert result == ground_truth['SD_DAGs(empty,G2,type=parent)']

    result = metrics.SD_DAGs(G1, G2, type='parent')
    assert result == ground_truth['SD_DAGs(G1,G2,type=parent)']

    result = metrics.SD_DAGs(G2, G1, type='parent')
    assert result == ground_truth['SD_DAGs(G2,G1,type=parent)']

    result = metrics.SD_DAGs(G1, G1, type='parent')
    assert result == ground_truth['SD_DAGs(G1,G1,type=parent)']


#------------------MB-enhanced parent-------------------------

def test_SD_DAGs_MB_enhanced_parent(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G3 = test_graphs['G3']

    result = metrics.SD_DAGs(G3, G1, type='parent', MB_enhanced=True)
    assert result == ground_truth['SD_DAGs(empty,G1,type=parent,MB_enhanced=True)']

    result = metrics.SD_DAGs(G3, G2, type='parent', MB_enhanced=True)
    assert result == ground_truth['SD_DAGs(empty,G2,type=parent,MB_enhanced=True)']

    result = metrics.SD_DAGs(G1, G2, type='parent', MB_enhanced=True)
    assert result == ground_truth['SD_DAGs(G1,G2,type=parent,MB_enhanced=True)']

    result = metrics.SD_DAGs(G2, G1, type='parent', MB_enhanced=True)
    assert result == ground_truth['SD_DAGs(G2,G1,type=parent,MB_enhanced=True)']

    result = metrics.SD_DAGs(G1, G1, type='parent', MB_enhanced=True)
    assert result == ground_truth['SD_DAGs(G1,G1,type=parent,MB_enhanced=True)']

#------------------ancestor-------------------------

def test_SD_DAGs_ancestor(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G3 = test_graphs['G3']

    result = metrics.SD_DAGs(G3, G1, type='ancestor')
    assert result == ground_truth['SD_DAGs(empty,G1,type=ancestor)']

    result = metrics.SD_DAGs(G3, G2, type='ancestor')
    assert result == ground_truth['SD_DAGs(empty,G2,type=ancestor)']

    result = metrics.SD_DAGs(G1, G2, type='ancestor')
    assert result == ground_truth['SD_DAGs(G1,G2,type=ancestor)']
                                  
    result = metrics.SD_DAGs(G2, G1, type='ancestor')
    assert result == ground_truth['SD_DAGs(G2,G1,type=ancestor)']

    result = metrics.SD_DAGs(G1, G1, type='ancestor')
    assert result == ground_truth['SD_DAGs(G1,G1,type=ancestor)']


#------------------ZL-------------------------

def test_SD_DAGs_ZL(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G3 = test_graphs['G3']

    result = metrics.SD_DAGs(G3, G1, type='ZL')
    assert result == ground_truth['SD_DAGs(empty,G1,type=ZL)']

    result = metrics.SD_DAGs(G3, G2, type='ZL')
    assert result == ground_truth['SD_DAGs(empty,G2,type=ZL)']

    result = metrics.SD_DAGs(G1, G2, type='ZL')
    assert result == ground_truth['SD_DAGs(G1,G2,type=ZL)']

    result = metrics.SD_DAGs(G2, G1, type='ZL')
    assert result == ground_truth['SD_DAGs(G2,G1,type=ZL)']

    result = metrics.SD_DAGs(G1, G1, type='ZL')
    assert result == ground_truth['SD_DAGs(G1,G1,type=ZL)']

#------------------MB-enhanced ZL-------------------------

def test_SD_DAGs_MB_enhanced_ZL(test_graphs):
    G1 = test_graphs['G1']
    G2 = test_graphs['G2']
    G3 = test_graphs['G3']

    result = metrics.SD_DAGs(G3, G1, type='ZL', MB_enhanced=True)
    assert result == ground_truth['SD_DAGs(empty,G1,type=ZL,MB_enhanced=True)']

    result = metrics.SD_DAGs(G3, G2, type='ZL', MB_enhanced=True)
    assert result == ground_truth['SD_DAGs(empty,G2,type=ZL,MB_enhanced=True)']

    result = metrics.SD_DAGs(G1, G2, type='ZL', MB_enhanced=True)
    assert result == ground_truth['SD_DAGs(G1,G2,type=ZL,MB_enhanced=True)']

    result = metrics.SD_DAGs(G2, G1, type='ZL', MB_enhanced=True)
    assert result == ground_truth['SD_DAGs(G2,G1,type=ZL,MB_enhanced=True)']

    result = metrics.SD_DAGs(G1, G1, type='ZL', MB_enhanced=True)
    assert result == ground_truth['SD_DAGs(G1,G1,type=ZL,MB_enhanced=True)']

