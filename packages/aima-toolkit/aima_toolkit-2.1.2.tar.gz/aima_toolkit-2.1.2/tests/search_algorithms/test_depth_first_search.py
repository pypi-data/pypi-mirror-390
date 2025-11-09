from src.aima_toolkit.Problems import Tree_Search_Problem
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.UninformedSearch import depth_first_search
from src.aima_toolkit.SearchProblemPackage import SearchStatus

def test_A_to_G():
    problem = Tree_Search_Problem(initial_state='A', goal_state='G')
    search_status, result_node = depth_first_search(problem)

    assert search_status == SearchStatus.SUCCESS
    assert result_node.get_path() == ['A', 'C', 'G']

def test_A_to_H():
    problem = Tree_Search_Problem(initial_state='A', goal_state='H')
    search_status, result_node = depth_first_search(problem)

    assert  search_status == SearchStatus.FAILURE
    assert result_node is None

def test_A_to_A():
    problem = Tree_Search_Problem(initial_state='A', goal_state='A')
    search_status, result_node = depth_first_search(problem)


    assert  search_status == SearchStatus.SUCCESS
    assert result_node.get_path() == ['A']

def test_A_to_B():
    problem = Tree_Search_Problem(initial_state='A', goal_state='B')
    search_status, result_node = depth_first_search(problem)

    assert search_status == SearchStatus.SUCCESS
    assert result_node.get_path() == ['A', 'B']

def test_A_to_C():
    problem = Tree_Search_Problem(initial_state='A', goal_state='C')
    search_status, result_node = depth_first_search(problem)

    assert search_status == SearchStatus.SUCCESS
    assert result_node.get_path() == ['A', 'C']

def test_A_to_D():
    problem = Tree_Search_Problem(initial_state='A', goal_state='D')
    search_status, result_node = depth_first_search(problem)

    assert  search_status == SearchStatus.SUCCESS
    assert result_node.get_path() == ['A', 'B', 'D']

def test_A_to_E():
    problem = Tree_Search_Problem(initial_state='A', goal_state='E')
    search_status, result_node = depth_first_search(problem)

    assert search_status == SearchStatus.SUCCESS
    assert result_node.get_path() == ['A', 'B', 'E']