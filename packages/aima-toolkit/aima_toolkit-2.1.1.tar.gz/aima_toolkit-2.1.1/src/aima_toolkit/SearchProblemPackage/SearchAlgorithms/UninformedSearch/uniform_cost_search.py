from ... import is_cycle, simple_is_cycle
from ...node import Node
from ...expand import expand
from ...queue import PriorityQueue
from ...searchproblem import SearchProblem, SearchStatus

def uniform_cost_search[S,A](problem : SearchProblem[S,A]) -> tuple[SearchStatus, Node[S,A] | None]:
  node = Node(problem.initial_state)

  frontier = PriorityQueue(lambda node: node.path_cost)
  frontier.push(node)
  reached : dict[S, Node[S,A]] = {node.state : node}
  
  while len(frontier) > 0:
    node = frontier.pop()

    if problem.IS_GOAL(node.state):
      return SearchStatus.SUCCESS, node
    elif node.path_cost != 0 and is_cycle(node, reached):
      continue

    for child in expand(problem=problem, node=node):
      if not is_cycle(child, reached):
        reached[child.state] = child
        frontier.push(child)

  return SearchStatus.FAILURE, None