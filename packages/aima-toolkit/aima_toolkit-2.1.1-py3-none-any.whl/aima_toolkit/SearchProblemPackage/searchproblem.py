from enum import Enum, auto
from typing import Callable, Union, TypeAlias, Iterable, Any
from .node import Node
from abc import abstractmethod, ABC
type Heuristic[S] = Callable[[S], float]

class SearchStatus(Enum):
    FAILURE = auto()
    CUTOFF = auto()
    SUCCESS = auto()

class SearchProblem[S, A](ABC):
  def __init__(self, initial_state : S):
    self.initial_state = initial_state

  @abstractmethod
  def ACTIONS(self, state: S) -> frozenset[A] | Iterable[A]:
    """
    Return a set of actions, or iterable over the actions, that can be performed on this search problem.

    Args:
        state: The state you wish to check the actions for.

    Returns:
        Set of actions that can be done in the given state.
    """
    raise NotImplementedError("This method should be overridden by subclasses")

  @abstractmethod
  def RESULTS(self, state : S, action : A) -> frozenset[S]:
    """
    Takes a state and an action done on that state and returns the set of all possible states, or an iterable over the actions
    Args:
      state: The state you wish to do an action on.
      action: The action you wish to do.

    Returns:
      A set of actions that can be done in the given state, or an iterable over the set of actions.
    """
    raise NotImplementedError("This method should be overridden by subclasses")

  @abstractmethod
  def ACTION_COST(self, state : S, action : A, new_state : S) -> float:
    """

    Args:
      state: starting state
      action: action to do on the starting state
      new_state: the state you get after performing the action

    Returns:
      The cost of getting from the starting state to the new state whilst doing the given action
    """
    raise NotImplementedError("This method should be overridden by subclasses")

  @abstractmethod
  def IS_GOAL(self, state : S) -> bool:
    """

    Args:
      state: The state you are checking

    Returns:
      True if the state is a goal state, False otherwise.
    """
    raise NotImplementedError("This method should be overridden by subclasses")

def is_cycle[S](node : Node[S, Any], reached : dict[S, Node[S, Any]]) -> bool:
  state : S = node.state

  if isinstance(state, frozenset): # We are working with belief states
    for possible_states in reached.keys():
      if state.issuperset(possible_states) and node.path_cost > reached[possible_states].path_cost:
        print(f"Prunning {state} because of {possible_states}")
        return True

    return False
  else:
    return state in reached.keys() and node.path_cost > reached[state].path_cost

def simple_is_cycle[S](node : Node[S, Any], reached : list[Node[S, Any]]) -> bool:
  state : S = node.state
  if isinstance(state, frozenset):
    return any( state.issuperset(reached_node.state) for reached_node in reached)
  else:
    return node in reached

__all__ = ['SearchProblem', 'Heuristic', 'SearchStatus', "is_cycle", "simple_is_cycle"]