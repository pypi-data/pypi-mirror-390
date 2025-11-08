from typing import override, Iterable

from src.aima_toolkit.SearchProblemPackage import nondeterministic_expand, OrNode, AndNode, SearchProblem

class MockupProblem(SearchProblem):
  """
  Tree that starts at Node 0
  and on the left you get an AND node with OR nodes A B C
  on right you get AND node with OR nodes D E
  """
  def __init__(self):
    super().__init__(None)

  def ACTIONS(self, state: str) -> set[str]:
    return { "LEFT", "RIGHT" }

  def RESULTS(self, state : str, action : str) -> set[str]:
    if action == "LEFT":
      return {"A", "B", "C"}
    else:
      return {"D", "E"}

  def ACTION_COST(self, state : str, action : str, new_state : str) -> float:
    if new_state == "A" or new_state == "E":
      return 2
    else:
      return 1

  def IS_GOAL(self, state : str) -> bool:
    return True


def test_nondeterministic_expand():
  mock_problem = MockupProblem()
  dummy_node = OrNode("0")

  and_nodes : list[AndNode[str,str]] = list(nondeterministic_expand(mock_problem, dummy_node))
  dummy_heuristic = lambda or_node: 1

  for and_node in and_nodes:
    assert 2 <= len(and_node.or_nodes) <= 3
    states = [node.state for node in and_node.or_nodes]

    if len(and_node.or_nodes) == 2:
      assert "D" in states
      assert "E" in states
      assert and_node.max_eval_node(dummy_heuristic) == (OrNode("E"), 3)
    else:
      assert "A" in states
      assert "B" in states
      assert "C" in states
      assert and_node.max_eval_node( dummy_heuristic ) == (OrNode( "A" ), 3)
