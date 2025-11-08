from .node import *
from .searchproblem import SearchProblem
from typing import Iterator, Callable
from collections.abc import Iterable

def expand[S,A](problem : SearchProblem[S,A], node : Node[S,A]):
  state = node.state

  for action in problem.ACTIONS(state):
    new_state = set(problem.RESULTS(state=state, action=action))
    assert len(new_state) == 1, "Tried to use deterministic expand on nondeterministic problem"

    new_state = new_state.pop()
    cost = node.path_cost + problem.ACTION_COST(state = state, action = action, new_state = new_state)

    yield Node(new_state, parent=node, path_cost= cost, action=action)

def local_expand(problem: SearchProblem, node : Node):
    """
    Takes a node and expands it locally, not saving the path and only showing nodes that are local
    :param problem:
    :param node:
    :return:
    """
    state = node.state

    for action in problem.ACTIONS(state):
      new_state = list( problem.RESULTS( state=state, action=action ) )
      assert len( new_state ) == 1, "classical local expand used on non deterministic problem"
      new_state = new_state[ 0 ]

      yield Node(new_state)

def nondeterministic_expand[S,A](problem: SearchProblem[S,A], node : OrNode[S,A], heuristic : Callable[[OrNode], float] = lambda or_node: 0) -> Iterator[AndNode[S,A]]:
  state = node.state
  for action in problem.ACTIONS(state):
    new_belief_state = problem.RESULTS(state=state, action=action)
    and_node = AndNode( parent=node, action=action, heuristic=heuristic )

    for new_state in new_belief_state:
      cost = node.path_cost + problem.ACTION_COST( state=state, action=action, new_state=new_state)
      and_node.add_or_node( OrNode(new_state, action=action, path_cost=cost, parent=node) )

    yield and_node

__all__ = ['expand', 'local_expand', 'nondeterministic_expand']