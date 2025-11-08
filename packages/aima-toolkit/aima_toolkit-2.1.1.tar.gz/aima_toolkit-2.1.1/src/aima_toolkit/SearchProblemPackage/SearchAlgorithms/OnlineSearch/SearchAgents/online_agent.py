from .. import OnlineSearchProblem, OnlineSearchAction
from abc import ABC, abstractmethod
from typing import Generator


class OnlineAgent[S,A](ABC):
  def __init__(self, online_search_problem : OnlineSearchProblem[S,A]):
    self.problem = online_search_problem
    self.s: S | None = None
    self.a: A | OnlineSearchAction | None = None
    self.s_prime: S = self.problem.initial_state
    self.result: dict[tuple[S,A], S] = dict()

  def search(self) -> Generator[A | OnlineSearchAction , S, None]:
    while True:
      self.a = self.get_next_action()
      self.s_prime = yield self.a

  @abstractmethod
  def get_next_action(self) -> A | OnlineSearchAction:
    pass