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
    with open('tests/test_answers/test_c_metric_DAGs_answers.json', 'r') as f:
        return json.load(f)

ground_truth = load_ground_truth()

def test_metric_dags_empty_G1_base(test_graphs):
    result = metrics.metric_DAGs(test_graphs['G3'], test_graphs['G1'], type='c', 
                               max_order=None, randomize_higher_order=0, normalized=True)
    assert result == ground_truth['metric_DAGs(empty,G1,type =c, max_order=None, randomize_higher_order = 0, normalized= True)']

def test_metric_dags_G1_G1_base(test_graphs):
    result = metrics.metric_DAGs(test_graphs['G1'], test_graphs['G1'], type='c', 
                               max_order=None, randomize_higher_order=0, normalized=True)
    assert result == ground_truth['metric_DAGs(G1,G1,type =c, max_order=None, randomize_higher_order = 0, normalized= True)']

def test_metric_dags_empty_G1_order2(test_graphs):
    result = metrics.metric_DAGs(test_graphs['G3'], test_graphs['G1'], type='c', 
                               max_order=2, randomize_higher_order=0, normalized=True)
    assert result == ground_truth['metric_DAGs(empty,G1,type =c, max_order=2, randomize_higher_order = 0, normalized= True)']

def test_metric_dags_G1_G1_order2(test_graphs):
    result = metrics.metric_DAGs(test_graphs['G1'], test_graphs['G1'], type='c', 
                               max_order=2, randomize_higher_order=0, normalized=True)
    assert result == ground_truth['metric_DAGs(G1,G1,type =c, max_order=2, randomize_higher_order = 0, normalized= True)']

def test_metric_dags_empty_G1_order2_rand100(test_graphs):
    result = metrics.metric_DAGs(test_graphs['G3'], test_graphs['G1'], type='c', 
                               max_order=2, randomize_higher_order=100, normalized=True)
    assert result == ground_truth['metric_DAGs(empty,G1,type =c, max_order=2, randomize_higher_order = 100, normalized= True)']

def test_metric_dags_G1_G1_order2_rand100(test_graphs):
    result = metrics.metric_DAGs(test_graphs['G1'], test_graphs['G1'], type='c', 
                               max_order=2, randomize_higher_order=100, normalized=True)
    assert result == ground_truth['metric_DAGs(G1,G1,type =c, max_order=2, randomize_higher_order = 100, normalized= True)']

def test_metric_dags_empty_G1_order2_rand100_unnorm(test_graphs):
    result = metrics.metric_DAGs(test_graphs['G3'], test_graphs['G1'], type='c', 
                               max_order=2, randomize_higher_order=100, normalized=False)
    assert result == ground_truth['metric_DAGs(empty,G1,type =c, max_order=2, randomize_higher_order = 100, normalized= False)']

def test_metric_dags_G1_G1_order2_rand100_unnorm(test_graphs):
    result = metrics.metric_DAGs(test_graphs['G1'], test_graphs['G1'], type='c', 
                               max_order=2, randomize_higher_order=100, normalized=False)
    assert result == ground_truth['metric_DAGs(G1,G1,type =c, max_order=2, randomize_higher_order = 100, normalized= False)']

def test_metric_dags_G2_G1(test_graphs):
    result = metrics.metric_DAGs(test_graphs['G2'], test_graphs['G1'], type='c', 
                               max_order=None, randomize_higher_order=0, normalized=True)
    assert result == ground_truth['metric_DAGs(G2,G1,type =c, max_order=None, randomize_higher_order = 0, normalized= True)']

def test_metric_dags_G1_G2(test_graphs):
    result = metrics.metric_DAGs(test_graphs['G1'], test_graphs['G2'], type='c', 
                               max_order=None, randomize_higher_order=0, normalized=True)
    assert result == ground_truth['metric_DAGs(G1,G2,type =c, max_order=None, randomize_higher_order = 0, normalized= True)']

def test_metric_dags_G1_empty(test_graphs):
    result = metrics.metric_DAGs(test_graphs['G1'], test_graphs['G3'], type='c', 
                               max_order=2, randomize_higher_order=0, normalized=True)
    assert result == ground_truth['metric_DAGs(G1,empty,type =c, max_order=2, randomize_higher_order = 0, normalized= True)']
