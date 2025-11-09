from .online_agent import OnlineAgent
from .. import OnlineSearchAction, OnlineSearchProblem
from typing import Callable
from .... import PriorityQueue
class OnlineDFSAgent[S,A](OnlineAgent[S,A]):
  def __init__(self, search_problem : OnlineSearchProblem[S,A], action_value_heuristic : Callable[[S,A],float] = lambda s,a: 0):
    super().__init__(search_problem)
    self.h = action_value_heuristic
    self.untried : dict[S, PriorityQueue[A]] = dict()
    self.un_backtracked : dict[S, list[S]] = dict()
    self.backtracked : dict[S, list[S]] = dict()

  def get_next_action(self) -> A | OnlineSearchAction:
    if self.problem.IS_GOAL(self.s_prime):
      return OnlineSearchAction.STOP

    if self.untried.get(self.s_prime) is None:
      self.untried[self.s_prime] = PriorityQueue(lambda a: self.h(self.s_prime, a))
      self.un_backtracked[self.s_prime] = list()
      self.backtracked[self.s_prime] = list()
      for action in self.problem.ACTIONS(self.s_prime):
        self.untried[self.s_prime].push(action)

    if self.s is not None:
      self.result[self.s, self.a] = self.s_prime
      if self.s not in self.un_backtracked[self.s_prime] and self.s not in self.backtracked[self.s_prime]:
        self.un_backtracked[self.s_prime].append(self.s)

    if len(self.untried[self.s_prime]) == 0:
      if len(self.un_backtracked[self.s_prime]) == 0:
        return OnlineSearchAction.STOP

      state_to_revisit = self.un_backtracked[self.s_prime].pop()
      self.backtracked[self.s_prime].append(state_to_revisit)
      self.a = OnlineSearchAction.STOP
      for action in self.problem.ACTIONS(self.s_prime):
        if self.result[self.s_prime, action] == state_to_revisit:
          self.a = action
          break
    else:
      self.a = self.untried[self.s_prime].pop()

    self.s = self.s_prime
    return self.a
