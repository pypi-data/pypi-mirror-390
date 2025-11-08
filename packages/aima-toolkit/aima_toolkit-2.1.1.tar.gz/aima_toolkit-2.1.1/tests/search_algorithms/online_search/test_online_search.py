from collections.abc import Callable

from src.aima_toolkit.Problems.find_the_ip_phone import Switch, FindTheIPPhone, topology, learned_mac_address
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.OnlineSearch.SearchAgents import OnlineDFSAgent, LearnRealTimeAStarAgent
from src.aima_toolkit.SearchProblemPackage.SearchAlgorithms.OnlineSearch import OnlineSearchAction, OnlineSearchProblem
from pprint import pprint


def check_result(problem, wanted_switch, action_value_heuristic : Callable[[Switch, str], float]= lambda s,a: 0.0):
  dfs_agent = OnlineDFSAgent( problem, action_value_heuristic )
  agent_search = dfs_agent.search( )

  action = next( agent_search )
  current_switch = problem.initial_state
  while action != OnlineSearchAction.STOP:
    current_switch = topology[ action ]
    action = agent_search.send( current_switch )

  assert action == OnlineSearchAction.STOP
  assert wanted_switch == current_switch

def check_result_LRTA(problem : FindTheIPPhone, wanted_switch):
  lrta_agent = LearnRealTimeAStarAgent( problem,  FindTheIPPhone.get_heuristic(problem.goal_mac_address))
  agent_search = lrta_agent.search()

  action = next( agent_search )
  current_switch = problem.initial_state
  while action != OnlineSearchAction.STOP:
    current_switch = topology[ action ]
    action = agent_search.send( current_switch )

  assert action == OnlineSearchAction.STOP
  assert wanted_switch == current_switch

def test_DFS_agent():
  for start_ip in {"127.0.0.1", "127.0.0.2", "127.0.0.3", "127.0.0.4", "127.0.0.5", "127.0.0.6"}:
    check_result(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-05"), topology["127.0.0.6"])
    check_result(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-04"), topology["127.0.0.5"])
    check_result(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-03"), topology["127.0.0.3"])
    check_result(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-02"), topology["127.0.0.2"])
    check_result(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-01"), topology["127.0.0.2"])
    check_result(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-00"), topology["127.0.0.1"])

def test_LRTA_agent():
  for start_ip in {"127.0.0.1", "127.0.0.2", "127.0.0.3", "127.0.0.4", "127.0.0.5", "127.0.0.6"}:
    check_result_LRTA(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-05"), topology["127.0.0.6"])
    check_result_LRTA(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-04"), topology["127.0.0.5"])
    check_result_LRTA(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-03"), topology["127.0.0.3"])
    check_result_LRTA(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-02"), topology["127.0.0.2"])
    check_result_LRTA(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-01"), topology["127.0.0.2"])
    check_result_LRTA(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-00"), topology["127.0.0.1"])


def test_DFS_with_heuristic():
  for start_ip in {"127.0.0.1", "127.0.0.2", "127.0.0.3", "127.0.0.4", "127.0.0.5", "127.0.0.6"}:
    check_result(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-05"), topology["127.0.0.6"], FindTheIPPhone.get_action_value_heuristic("11-11-11-11-11-05"))
    check_result(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-04"), topology["127.0.0.5"], FindTheIPPhone.get_action_value_heuristic("11-11-11-11-11-04"))
    check_result(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-03"), topology["127.0.0.3"], FindTheIPPhone.get_action_value_heuristic("11-11-11-11-11-03"))
    check_result(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-02"), topology["127.0.0.2"], FindTheIPPhone.get_action_value_heuristic("11-11-11-11-11-02"))
    check_result(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-01"), topology["127.0.0.2"], FindTheIPPhone.get_action_value_heuristic("11-11-11-11-11-01"))
    check_result(FindTheIPPhone(topology[start_ip], "11-11-11-11-11-00"), topology["127.0.0.1"], FindTheIPPhone.get_action_value_heuristic("11-11-11-11-11-00"))

def test_non_existent_phone():
  problem = FindTheIPPhone(topology["127.0.0.1"], "11-11-11-11-11-0A")
  dfs_agent = OnlineDFSAgent( problem )
  agent_search = dfs_agent.search( )

  action = next( agent_search )
  current_switch = problem.initial_state
  while action != OnlineSearchAction.STOP:
    current_switch = topology[ action ]
    action = agent_search.send( current_switch )

  assert action == OnlineSearchAction.STOP
  assert problem.IS_GOAL( current_switch ) == False