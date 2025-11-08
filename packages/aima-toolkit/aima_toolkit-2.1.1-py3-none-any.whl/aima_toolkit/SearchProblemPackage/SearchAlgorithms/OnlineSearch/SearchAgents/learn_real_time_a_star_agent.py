from numpy.ma.core import argmin

from .online_agent import OnlineAgent
from .. import OnlineSearchProblem, OnlineSearchAction
from .... import Heuristic
from typing import Generator
import numpy as np

class LearnRealTimeAStarAgent[S,A](OnlineAgent[S,A]):
  def __init__(self, online_search_problem : OnlineSearchProblem[S,A], heuristic_function : Heuristic):
    super().__init__(online_search_problem)
    self.h = heuristic_function
    self.H: dict[S, float] = {}

  def get_next_action(self) -> A | OnlineSearchAction:
    if self.problem.IS_GOAL(self.s_prime):
      return OnlineSearchAction.STOP

    if self.s_prime not in self.H:
      self.H[self.s_prime] = self.h(self.s_prime)

    if self.s is not None:
      self.result[self.s, self.a] = self.s_prime
      self.H[self.s] = min(
        self.LRTA_COST(
          self.s,
          a,
          self.result.get( (self.s, a) )
        )
        for a in self.problem.ACTIONS(self.s)
      )

    b: list[A] = list(self.problem.ACTIONS(self.s_prime))
    costs : list[float] = list()
    for action in b:
      costs.append( self.LRTA_COST( self.s_prime, action, self.result.get( (self.s_prime, action) ) ) )
    action_index = argmin( costs )

    self.s = self.s_prime
    self.a = b[action_index]
    return self.a


  def LRTA_COST(self, state: S, action: A, new_state: S | None) -> float:
    if new_state is None:
      return self.h(state)
    else:
      return self.problem.ACTION_COST(state, action, new_state) + self.H[new_state]
