from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.NondeterministicSearch.Uninformed.nondeterministic_uniform_cost_search import nondeterministic_uniform_cost_search
from src.aima_toolkit.SearchProblemPackage import SearchStatus
from src.aima_toolkit.Problems.erratic_vacuum_world import ErraticVacuumWorld
from pprint import pprint

def test_nondeterministic_uniform_cost_search():
  problem = ErraticVacuumWorld(initial_state=1)
  status, result = nondeterministic_uniform_cost_search(problem)
  assert status == SearchStatus.SUCCESS
  assert result == {
    1 : {
      "action" : "Suck",
      "outcomes" : {
        7 : {},
        5 : {
          "action" : "Right",
          "outcomes" : {
            6 : {
              "action" : "Suck",
              "outcomes" : {
                8 : {}
              }
            }
          }
        }
      }
    }
  }