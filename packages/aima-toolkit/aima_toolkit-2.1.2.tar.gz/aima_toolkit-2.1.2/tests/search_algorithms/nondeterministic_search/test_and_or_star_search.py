from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.NondeterministicSearch.Informed.and_or_star_search import and_or_star_search
from src.aima_toolkit.SearchProblemPackage import SearchStatus
from src.aima_toolkit.Problems import ErraticVacuumWorld, VacuumWorld
from pprint import pprint

def test_and_or_star_search():
  problem = ErraticVacuumWorld(initial_state=1)
  status, result = and_or_star_search(problem, heuristic=VacuumWorld.clean_square_heuristic)
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
