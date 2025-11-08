from src.aima_toolkit.Problems import PartiallyObservableVacuumWorld, SensorlessVacuumWorld, VacuumWorld
from src.aima_toolkit.SearchProblemPackage import SearchStatus
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.NondeterministicSearch.Uninformed import nondeterministic_uniform_cost_search
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.NondeterministicSearch.Informed import and_or_star_search
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.UninformedSearch import uniform_cost_search
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.InformedSearch import a_star_search
from pprint import pprint

def heuristic(state : frozenset[int]) -> float:
  return max(VacuumWorld.clean_square_heuristic(s) for s in state)

def test_solution():
  problem = PartiallyObservableVacuumWorld(initial_state=frozenset({1,3}))

  print("\n\n\n")
  status1, result1 = and_or_star_search(problem, heuristic=heuristic)
  status2, result2 = nondeterministic_uniform_cost_search(problem)
  assert status1 == status2 == SearchStatus.SUCCESS

  expectedResults = [{frozenset({1, 3}): {'action': 'Suck',
                      'outcomes': {frozenset({5, 7}): {'action': 'Right',
                                                       'outcomes': {frozenset({6}): {'action': 'Suck',
                                                                                     'outcomes': {frozenset({8}): {}}},
                                                                    frozenset({8}): {}}}}}},
                     {
                       frozenset({1,3}) : {
                         'action': 'Right',
                         'outcomes': {
                            frozenset({2}): {
                              'action': 'Suck',
                              'outcomes' : {
                                frozenset({4}) : {
                                  'action': 'Left',
                                  'outcomes': {
                                    frozenset({3}): {
                                      'action': 'Suck',
                                      'outcomes' : {
                                        frozenset({7}) : {}
                                      }
                                    }
                                  }
                                }
                              }
                            },
                           frozenset({4}): {
                             'action': 'Left',
                             'outcomes': {
                               frozenset({3}): {
                                 'action': 'Suck',
                                 'outcomes': {
                                   frozenset({7}): {}
                                 }
                               }
                             }
                           }
                         }
                       }
                     }

                    ]
  assert result1 == expectedResults[0]
  assert result2 in expectedResults

def test_sensorless():
  problem = SensorlessVacuumWorld(initial_state=frozenset({1,2,3,4,5,6,7,8}))
  expected_result = [["Right", "Suck", "Left", "Suck"], ["Left", "Suck", "Right", "Suck"]]
  search_status, result_node = uniform_cost_search(problem)
  assert search_status == SearchStatus.SUCCESS
  assert result_node.get_actions() in expected_result

  search_status, result_node = a_star_search(problem, heuristic)
  assert search_status == SearchStatus.SUCCESS
  assert result_node.get_actions() in expected_result