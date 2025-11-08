import pytest
import json
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
    with open('tests/test_answers/test_AIDs_answers.json', 'r') as f:
        return json.load(f)

ground_truth = load_ground_truth()

# Parent AID DAG tests
def test_parent_aid_dags_empty_G1(test_graphs):
    result = metrics.parent_AID_DAGs(test_graphs['G3'], test_graphs['G1'])
    assert result == ground_truth['parent_AID_DAGs(empty,G1)']

def test_parent_aid_dags_empty_G2(test_graphs):
    result = metrics.parent_AID_DAGs(test_graphs['G3'], test_graphs['G2'])
    assert result == ground_truth['parent_AID_DAGs(empty,G2)']

def test_parent_aid_dags_G1_empty(test_graphs):
    result = metrics.parent_AID_DAGs(test_graphs['G1'], test_graphs['G3'])
    assert result == ground_truth['parent_AID_DAGs(G1,empty)']

def test_parent_aid_dags_G2_empty(test_graphs):
    result = metrics.parent_AID_DAGs(test_graphs['G2'], test_graphs['G3'])
    assert result == ground_truth['parent_AID_DAGs(G2,empty)']

def test_parent_aid_dags_G1_G2(test_graphs):
    result = metrics.parent_AID_DAGs(test_graphs['G1'], test_graphs['G2'], normalized=False)
    assert result == ground_truth['parent_AID_DAGs(G1,G2)']

def test_sym_parent_aid_dags_empty_G1(test_graphs):
    result = metrics.sym_parent_AID_DAGs(test_graphs['G3'], test_graphs['G1'])
    assert result == ground_truth['sym_parent_AID_DAGs(empty,G1)']

def test_sym_parent_aid_dags_empty_G2(test_graphs):
    result = metrics.sym_parent_AID_DAGs(test_graphs['G3'], test_graphs['G2'])
    assert result == ground_truth['sym_parent_AID_DAGs(empty,G2)']

def test_sym_parent_aid_dags_G1_G2(test_graphs):
    result = metrics.sym_parent_AID_DAGs(test_graphs['G1'], test_graphs['G2'], normalized=False)
    assert result == ground_truth['sym_parent_AID_DAGs(G1,G2)']

# Ancestor AID DAG tests
def test_ancestor_aid_dags_empty_G1(test_graphs):
    result = metrics.ancestor_AID_DAGs(test_graphs['G3'], test_graphs['G1'])
    assert result == ground_truth['ancestor_AID_DAGs(empty,G1)']

def test_ancestor_aid_dags_empty_G2(test_graphs):
    result = metrics.ancestor_AID_DAGs(test_graphs['G3'], test_graphs['G2'])
    assert result == ground_truth['ancestor_AID_DAGs(empty,G2)']

def test_ancestor_aid_dags_G1_empty(test_graphs):
    result = metrics.ancestor_AID_DAGs(test_graphs['G1'], test_graphs['G3'])
    assert result == ground_truth['ancestor_AID_DAGs(G1,empty)']

def test_ancestor_aid_dags_G2_empty(test_graphs):
    result = metrics.ancestor_AID_DAGs(test_graphs['G2'], test_graphs['G3'])
    assert result == ground_truth['ancestor_AID_DAGs(G2,empty)']

def test_ancestor_aid_dags_G1_G2(test_graphs):
    result = metrics.ancestor_AID_DAGs(test_graphs['G1'], test_graphs['G2'], normalized=False)
    assert result == ground_truth['ancestor_AID_DAGs(G1,G2)']

def test_sym_ancestor_aid_dags_empty_G1(test_graphs):
    result = metrics.sym_ancestor_AID_DAGs(test_graphs['G3'], test_graphs['G1'])
    assert result == ground_truth['sym_ancestor_AID_DAGs(empty,G1)']

def test_sym_ancestor_aid_dags_empty_G2(test_graphs):
    result = metrics.sym_ancestor_AID_DAGs(test_graphs['G3'], test_graphs['G2'])
    assert result == ground_truth['sym_ancestor_AID_DAGs(empty,G2)']

def test_sym_ancestor_aid_dags_G1_G2(test_graphs):
    result = metrics.sym_ancestor_AID_DAGs(test_graphs['G1'], test_graphs['G2'], normalized=False)
    assert result == ground_truth['sym_ancestor_AID_DAGs(G1,G2)']

# CPDAG Parent tests
def test_parent_aid_cpdags_empty_G1(test_graphs):
    result = metrics.parent_AID_CPDAGs(test_graphs['G3'], test_graphs['G1'])
    assert result == ground_truth['parent_AID_CPDAGs(empty,G1)']

def test_parent_aid_cpdags_empty_G2(test_graphs):
    result = metrics.parent_AID_CPDAGs(test_graphs['G3'], test_graphs['G2'])
    assert result == ground_truth['parent_AID_CPDAGs(empty,G2)']

def test_parent_aid_cpdags_G1_empty(test_graphs):
    result = metrics.parent_AID_CPDAGs(test_graphs['G1'], test_graphs['G3'])
    assert result == ground_truth['parent_AID_CPDAGs(G1,empty)']

def test_parent_aid_cpdags_G2_empty(test_graphs):
    result = metrics.parent_AID_CPDAGs(test_graphs['G2'], test_graphs['G3'])
    assert result == ground_truth['parent_AID_CPDAGs(G2,empty)']

def test_parent_aid_cpdags_G1_G2(test_graphs):
    result = metrics.parent_AID_CPDAGs(test_graphs['G1'], test_graphs['G2'], normalized=False)
    assert result == ground_truth['parent_AID_CPDAGs(G1,G2)']

def test_sym_parent_aid_cpdags_empty_G1(test_graphs):
    result = metrics.sym_parent_AID_CPDAGs(test_graphs['G3'], test_graphs['G1'])
    assert result == ground_truth['sym_parent_AID_CPDAGs(empty,G1)']

def test_sym_parent_aid_cpdags_empty_G2(test_graphs):
    result = metrics.sym_parent_AID_CPDAGs(test_graphs['G3'], test_graphs['G2'])
    assert result == ground_truth['sym_parent_AID_CPDAGs(empty,G2)']

def test_sym_parent_aid_cpdags_G1_G2(test_graphs):
    result = metrics.sym_parent_AID_CPDAGs(test_graphs['G1'], test_graphs['G2'], normalized=False)
    assert result == ground_truth['sym_parent_AID_CPDAGs(G1,G2)']

# CPDAG Ancestor tests
def test_ancestor_aid_cpdags_empty_G1(test_graphs):
    result = metrics.ancestor_AID_CPDAGs(test_graphs['G3'], test_graphs['G1'])
    assert result == ground_truth['ancestor_AID_CPDAGs(empty,G1)']

def test_ancestor_aid_cpdags_empty_G2(test_graphs):
    result = metrics.ancestor_AID_CPDAGs(test_graphs['G3'], test_graphs['G2'])
    assert result == ground_truth['ancestor_AID_CPDAGs(empty,G2)']

def test_ancestor_aid_cpdags_G1_empty(test_graphs):
    result = metrics.ancestor_AID_CPDAGs(test_graphs['G1'], test_graphs['G3'])
    assert result == ground_truth['ancestor_AID_CPDAGs(G1,empty)']

def test_ancestor_aid_cpdags_G2_empty(test_graphs):
    result = metrics.ancestor_AID_CPDAGs(test_graphs['G2'], test_graphs['G3'])
    assert result == ground_truth['ancestor_AID_CPDAGs(G2,empty)']

def test_ancestor_aid_cpdags_G1_G2(test_graphs):
    result = metrics.ancestor_AID_CPDAGs(test_graphs['G1'], test_graphs['G2'], normalized=False)
    assert result == ground_truth['ancestor_AID_CPDAGs(G1,G2)']

def test_sym_ancestor_aid_cpdags_empty_G1(test_graphs):
    result = metrics.sym_ancestor_AID_CPDAGs(test_graphs['G3'], test_graphs['G1'])
    assert result == ground_truth['sym_ancestor_AID_CPDAGs(empty,G1)']

def test_sym_ancestor_aid_cpdags_empty_G2(test_graphs):
    result = metrics.sym_ancestor_AID_CPDAGs(test_graphs['G3'], test_graphs['G2'])
    assert result == ground_truth['sym_ancestor_AID_CPDAGs(empty,G2)']

def test_sym_ancestor_aid_cpdags_G1_G2(test_graphs):
    result = metrics.sym_ancestor_AID_CPDAGs(test_graphs['G1'], test_graphs['G2'], normalized=False)
    assert result == ground_truth['sym_ancestor_AID_CPDAGs(G1,G2)']