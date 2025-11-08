from typing import Self, Callable

class Node[S,A]:
  def __init__(self, state : S, parent : Self | None | "AndNode[S,A]" = None, path_cost : float | int = 0, action : A | None = None):
    self.state = state
    self.parent = parent
    self.path_cost = path_cost
    self.depth = 0 if parent is None else parent.depth + 1
    self.action = action
    self.f : float = 0

  def __str__(self) -> str:
    return self.__repr__()

  def __eq__(self, value: object) -> bool:
    return self.state == value.state if isinstance(value, Node) else False

  def __repr__(self) -> str:
    return f"Node({self.state}, cost={self.path_cost})"

  def get_path(self) -> list[S]:
    path = []
    current = self
    while current:
      path.append(current.state)
      current = current.parent

    return path[::-1]
  
  def get_actions(self) -> list[A]:
    actions = []
    current = self
    while current:
      if current.action is not None:
        actions.append(current.action)
      current = current.parent

    return actions[::-1]

OrNode = Node

class AndNode[S,A]:
  def __init__(self,parent : OrNode, action : A, or_nodes : tuple[Node[S,A]] | None = None, heuristic : Callable[[S], float] = lambda or_node: 0) -> None:
    self.or_nodes : tuple[OrNode, ...] = tuple() if or_nodes is None else or_nodes
    self.parent = parent
    self.action = action

    self.heuristic = heuristic

    self.f : float = 0
    self.eval_score : float = 0 if len(self.or_nodes) == 0 else self.get_eval_score()

  def __len__(self) -> int:
    return len(self.or_nodes)

  def __repr__(self) -> str:
    return f"AndNode({self.or_nodes})"

  def __eq__(self, value: Self) -> bool:
    if len(self.or_nodes) != len(value.or_nodes):
      return False
    else:
      for node in self.or_nodes:
        if node not in value.or_nodes:
          return False

    return True

  def add_or_node(self, node : OrNode[S,A]) -> None:
    self.or_nodes += (node,)

    new_eval_score = node.path_cost + self.heuristic(node.state)
    self.eval_score = new_eval_score if new_eval_score > self.eval_score else self.eval_score

  def get_eval_score(self) -> float:
    assert len( self.or_nodes ) > 0, "Cannot get an evaluation score for an empty node"
    max_eval_score = self.or_nodes[0].path_cost + self.heuristic(self.or_nodes[0])

    for or_node in self.or_nodes:
      max_eval_score = max(max_eval_score, or_node.path_cost + self.heuristic(or_node.state))

    return max_eval_score

  def change_heuristic(self, new_heuristic : Callable[[S], float]) -> None:
    self.heuristic = new_heuristic
    self.eval_score = self.get_eval_score()

  def max_eval_node(self, heuristic_function : Callable[[Node[S,A]], float]) -> tuple[Node[S,A], float]:
    assert len(self.or_nodes) > 0
    max_node = self.or_nodes[0]
    max_evaluation_score = max_node.path_cost + heuristic_function(max_node)
    for node in self.or_nodes:
      evaluation_score = node.path_cost + heuristic_function(node)
      if evaluation_score > max_evaluation_score:
        max_node = node
        max_evaluation_score = evaluation_score

    return max_node, max_evaluation_score


__all__ = ["Node", "OrNode", "AndNode"]