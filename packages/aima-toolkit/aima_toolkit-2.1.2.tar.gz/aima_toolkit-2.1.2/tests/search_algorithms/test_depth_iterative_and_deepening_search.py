from src.aima_toolkit.Problems import Tree_Search_Problem
from src.aima_toolkit.SearchProblemPackage import SearchStatus
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.UninformedSearch import depth_limited_search, iterative_deepening_search

class TestDepthLimitedSearch:
    def test_A_to_G_depth_bad(self):
      problem = Tree_Search_Problem(initial_state='A', goal_state='G')
      search_status, result_node = depth_limited_search(problem, limit=1)

      assert search_status == SearchStatus.CUTOFF
      assert result_node is None

    def test_A_to_H_depth_good(self):
      problem = Tree_Search_Problem(initial_state='A', goal_state='H')
      search_status, result_node = depth_limited_search(problem, limit=10)

      assert search_status == SearchStatus.FAILURE
      assert result_node is None

    def test_A_to_G_depth_good(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='G')
        search_status, result_node = depth_limited_search(problem, limit=10)

        assert search_status == SearchStatus.SUCCESS
        assert result_node.get_path() == ['A', 'C', 'G']

    def test_A_to_A_depth_good(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='A')
        search_status, result_node = depth_limited_search(problem, limit=0)

        assert search_status == SearchStatus.SUCCESS
        assert result_node.get_path() == ['A']

class TestIterativeDeepeningSearch:
    def test_A_to_A(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='A')
        search_status, result_node = iterative_deepening_search(problem)

        assert search_status == SearchStatus.SUCCESS
        assert result_node.get_path() == ['A']

    def test_A_to_B(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='B')
        search_status, result_node = iterative_deepening_search(problem)

        assert search_status == SearchStatus.SUCCESS
        assert result_node.get_path() == ['A', 'B']

    def test_A_to_C(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='C')
        search_status, result_node = iterative_deepening_search(problem)

        assert search_status == SearchStatus.SUCCESS
        assert result_node.get_path() == ['A', 'C']

    def test_A_to_D(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='D')
        search_status, result_node = iterative_deepening_search(problem)

        assert search_status == SearchStatus.SUCCESS
        assert result_node.get_path() == ['A', 'B', 'D']

    def test_A_to_E(self):
        problem = Tree_Search_Problem(initial_state='A', goal_state='E')
        search_status, result_node = iterative_deepening_search(problem)

        assert search_status == SearchStatus.SUCCESS
        assert result_node.get_path() == ['A', 'B', 'E']