from simulator_tree_loader import get_sim_tree_v1

def test_simulator_tree_loads():
    tree = get_sim_tree_v1()
    assert isinstance(tree, dict)
    assert len(tree) > 0
