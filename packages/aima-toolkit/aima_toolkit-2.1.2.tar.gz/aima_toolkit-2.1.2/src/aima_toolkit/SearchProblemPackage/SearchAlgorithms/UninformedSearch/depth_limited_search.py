from ...node import Node
from ...expand import expand
from ...queue import Stack
from ...searchproblem import SearchProblem, SearchStatus

def depth_limited_search(problem : SearchProblem, limit : int) -> tuple[SearchStatus, Node | None]:
  frontier = Stack()
  frontier.push(Node(problem.initial_state))

  result : SearchStatus = SearchStatus.FAILURE
  while len(frontier) > 0:
    node = frontier.pop()

    if problem.IS_GOAL(node.state):
      return SearchStatus.SUCCESS, node

    if node.depth < limit:
      for child in expand(problem=problem, node=node):
        frontier.push(child)
    else:
      result = SearchStatus.CUTOFF

  return result, None