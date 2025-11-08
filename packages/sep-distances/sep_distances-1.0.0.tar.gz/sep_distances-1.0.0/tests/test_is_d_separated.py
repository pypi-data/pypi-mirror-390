from codebase import mixed_graph as mixed
import json
import pytest
from ..tests import Graphs_for_testing as G_testing

@pytest.fixture
def test_graphs():
    graphs = G_testing.generate_graphs()
    return {
        'G1': graphs['chain'],
        'G2': graphs['simple_collider']
    }


# Load ground truth values
def load_ground_truth():
    with open('tests/test_answers/test_is_d_separated_answers.json', 'r') as f:
        return json.load(f)

ground_truth = load_ground_truth()



def test_G1_is_d_separated(test_graphs):
    G1 = test_graphs['G1']
    assert G1.is_d_separated(x={'X1',},y={'X5',},z=set(),DAG_check=False) == ground_truth["G1.is_d_separated(x={'X1',},y={'X5',},z=set(),DAG_check=False)"]
    assert G1.is_d_separated(x={'X1',},y={'X5',},z={'X4'},DAG_check=True) == ground_truth["G1.is_d_separated(x={'X1',},y={'X5',},z={'X4'},DAG_check=True)"]
    assert G1.is_d_separated(x={'X1',},y={'X5',},z={'X4','X3'},DAG_check=True) == ground_truth["G1.is_d_separated(x={'X1',},y={'X5',},z={'X4','X3'},DAG_check=True)"]


def test_G2_is_d_separated(test_graphs):
    G2 = test_graphs['G2']
    assert G2.is_d_separated(x={'X1',},y={'X5',},z=set(),DAG_check=False) == ground_truth["G2.is_d_separated(x={'X1',},y={'X5',},z=set(),DAG_check=False)"]
    assert G2.is_d_separated(x={'X1',},y={'X5',},z={'X4'},DAG_check=True) == ground_truth["G2.is_d_separated(x={'X1',},y={'X5',},z={'X4'},DAG_check=True)"]
    assert G2.is_d_separated(x={'X1',},y={'X5',},z={'X4','X3'},DAG_check=True) == ground_truth["G2.is_d_separated(x={'X1',},y={'X5',},z={'X4','X3'},DAG_check=True)"]
