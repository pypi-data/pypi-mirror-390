from typing import Iterable, Callable
from abc import ABC, abstractmethod

from ... import SearchProblem

class PartiallyObservableProblem[S,A,P](SearchProblem, ABC):
  @abstractmethod
  def PERCEPT(self, state) -> P: # Returns None for sensorless, returns the state for observable, or it returns a percept describing the state
    raise NotImplementedError

  @abstractmethod
  def PREDICT(self, state : S, action : A) -> frozenset[S]: # Equivalent to RESULTSp
    raise NotImplementedError

  @abstractmethod
  def ACTIONSp(self, state : S) -> frozenset[A]:
    raise NotImplementedError

  @abstractmethod
  def ACTION_COSTp(self, state : S, action : A, new_state : S) -> float:
    raise NotImplementedError

  @abstractmethod
  def IS_GOALp(self, state : S) -> bool:
    raise NotImplementedError

  def POSSIBLE_PERCEPTS(self, state: frozenset[ S ]) -> frozenset[ P ]:
    return frozenset( self.PERCEPT(s) for s in state )

  def __init__(self, initial_belief_state : frozenset[S], allow_illegal_actions : bool = False) -> None:
    super().__init__(initial_belief_state)
    self.allow_illegal_actions = allow_illegal_actions

  def IS_GOAL(self, state: frozenset[ S ]) -> bool:
    return all( self.IS_GOALp(concrete_state) for concrete_state in state )

  def UPDATE(self, state : frozenset[S ], percept : P) -> frozenset[ S ]:
    return frozenset(s for s in state if percept == self.PERCEPT( s ))

  def RESULTS(self, state : set[ S ], action : A) -> Iterable[ frozenset[ S ] ]:
    new_belief_state : frozenset[S] = frozenset( s_new for s in state for s_new in self.PREDICT(state=s, action=action))
    for percept in self.POSSIBLE_PERCEPTS( state=frozenset(new_belief_state) ):
      yield self.UPDATE(new_belief_state, percept)

  def ACTIONS(self, state : frozenset[ S ]) -> frozenset[ A ]:
    state = set(state)
    actions : set[A] = set(self.ACTIONSp( state=state.pop( ) ))
    for s in state:
      if self.allow_illegal_actions:
        actions |= self.ACTIONSp( s )
      else:
        actions &= self.ACTIONSp( s )

    return frozenset(actions)

  def ACTION_COST(self, state : frozenset[ S ], action : A, new_state : frozenset[ S ]) -> float:
    costs = (
        self.ACTION_COSTp(state=concrete_state, action=action, new_state=new_state)
        for concrete_state in state
        for predicted_new_state in self.PREDICT(state=concrete_state, action=action)
        if predicted_new_state in new_state
    )

    return max(costs, default=float("inf"))