from ...searchproblem import *
from ...queue import PriorityQueue
from ...node import Node
from ...expand import expand

def a_star_search[S,A](problem: SearchProblem[S,A], heuristic : Heuristic) -> tuple[SearchStatus, Node[S,A] | None]:
  root_node = Node(problem.initial_state)

  frontier = PriorityQueue(evaluation_func=lambda node: node.path_cost + heuristic(node.state))
  reached : dict[S, Node[S,A]] = {root_node.state: root_node}

  frontier.push(root_node)
  while len(frontier) > 0:
    node = frontier.pop()

    if problem.IS_GOAL(node.state):
      return SearchStatus.SUCCESS, node
    elif is_cycle(node, reached):
      continue

    for successor in expand(problem=problem, node=node):
      if not is_cycle(successor, reached):
        reached[successor.state] = successor
        frontier.push(successor)

  return SearchStatus.FAILURE, None