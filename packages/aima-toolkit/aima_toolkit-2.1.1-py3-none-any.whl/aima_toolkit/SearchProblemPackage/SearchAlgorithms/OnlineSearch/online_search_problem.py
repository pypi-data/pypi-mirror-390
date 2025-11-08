from abc import ABC, abstractmethod
from enum import Enum, auto

class OnlineSearchProblem[S,A](ABC):
  def __init__(self, initial_state : S):
    self.initial_state : S = initial_state

  @abstractmethod
  def ACTIONS(self, state : S) -> frozenset[A]:
    pass

  @abstractmethod
  def ACTION_COST(self, state : S, action : A, new_state : S) -> float:
    pass

  @abstractmethod
  def IS_GOAL(self, state : S) -> bool:
    pass


class OnlineSearchAction(Enum):
  STOP = auto()