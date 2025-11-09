from typing import Iterable

from ..SearchProblemPackage import SearchProblem, OrNode

class VacuumWorld(SearchProblem[int, str]):
  # 1 = bot is left, left is dirty, right is dirty
  # 2 = bot is right, left is dirty, right is dirty
  # 3 = bot is left, left is dirty, right is clean
  # 4 = bot is right, left is dirty, right is clean
  # 5 = bot is left, left is clean, right is dirty
  # 6 = bot is right, left is clean, right is dirty
  # 7 = bot is left, left is clean, right is clean
  # 8 = bot is right, left is clean, right is clean

  def __init__(self, initial_state : int):
    assert 1 <= initial_state <= 8, "initial_state must be between 1 and 8"
    super().__init__(initial_state)

  def ACTIONS(self, state: int) -> set[str]:
    return {"Left", "Right", "Suck"}

  def RESULTS(self, state : int, action : str) -> set[int]:
    if action == "Left":
      if state in [1,3,5,7]:
        return { state }
      else:
        return { state - 1 }
    elif action == "Right":
      if state in [1,3,5,7]:
        return { state + 1 }
      else:
        return { state }
    else:
      if state == 1:
        return { 5 }
      elif state == 2:
        return { 4 }
      elif state == 3:
        return { 7 }
      elif state == 4:
        return { 4 }
      elif state == 5:
        return { 5 }
      elif state == 6:
        return { 8 }
      else:
        return { state }

  def ACTION_COST(self, state : int, action : str, new_state : int) -> float:
    return 1

  def IS_GOAL(self, state : int) -> bool:
    return state in [7, 8]

  @staticmethod
  def clean_square_heuristic(state : int) -> float:
    if state in [1,2]:
      return 2
    elif state in [3,4,5,6]:
      return 1
    else:
      return 0
