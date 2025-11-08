from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.NondeterministicSearch.Uninformed.nondeterministic_depth_first_search import nondeterministic_depth_first_search
from src.aima_toolkit.Problems.erratic_vacuum_world import ErraticVacuumWorld

def test_nondeterministic_depth_first_search():
  problem = ErraticVacuumWorld(initial_state=1)
  result = nondeterministic_depth_first_search(problem)
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
  } or result == {
    1 : {
      "action" : "Right",
      "outcomes" : {
        2 : {
          "action" : "Suck",
          "outcomes" : {
            8 : {},
            4 : {
              "action" : "Left",
              "outcomes" : {
                3 : {
                  "action" : "Suck",
                  "outcomes" : {
                    7 : {}
                  }
                }
              }
            }
          }
        }
      }
    }
  }
