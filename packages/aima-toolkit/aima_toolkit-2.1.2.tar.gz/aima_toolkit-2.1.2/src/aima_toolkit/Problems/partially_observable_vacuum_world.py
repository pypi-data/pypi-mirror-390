from ..SearchProblemPackage.SearchAlgorithms.PartiallyObservableSearch.partially_observable_problem import PartiallyObservableProblem
from .vacuum_world import VacuumWorld
#   1 = agent left, both dirty
#   2 = agent right, both dirty
#   3 = agent left, left dirty, right clean
#   4 = agent right, left dirty, right clean
#   5 = agent left, left clean, right dirty
#   6 = agent right, left clean, right dirty
#   7 = agent left, both clean
#   8 = agent right, both clean

class PartiallyObservableVacuumWorld(PartiallyObservableProblem[int, str, tuple[str,str]]):
  def __init__(self, initial_state : frozenset[int]):
    assert initial_state <= {1,2,3,4,5,6,7,8}
    super().__init__(initial_state)
    self.P = VacuumWorld(1)

  def PERCEPT(self, state : int) -> tuple[str,str]:  # Returns None for sensorless, returns the state for observable, or it returns a percept describing the state
    if state in [1,3]:
      return 'L', 'Dirty'
    elif state in [5,7]:
      return 'L', 'Clean'
    elif state in [2,6]:
      return 'R', 'Dirty'
    else:
      return 'R', 'Clean'

  def PREDICT(self, state: int, action: str) -> frozenset[ int ]:
    return frozenset(self.P.RESULTS(state, action))

  def ACTION_COSTp(self, state: int, action: str, new_state: int) -> float:
    return 1

  def ACTIONSp(self, state: int) -> frozenset[ str ]:
    return frozenset(self.P.ACTIONS(state))

  def IS_GOALp(self, state: int) -> bool:
    return self.P.IS_GOAL(state)





