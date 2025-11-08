from operator import contains
from typing import TypedDict, cast, Callable
from ..SearchProblemPackage.SearchAlgorithms.OnlineSearch import OnlineSearchProblem
class NeighborInfo(TypedDict):
    IPv4: str
    sysName: str
    local_interface: str
    neighbor_interface: str

class Switch:
  def __init__(self, ip_address : str, cdp_neighbors : tuple[NeighborInfo,...]):
    self.ip_address : str = ip_address
    self.cdp_neighbors : tuple[NeighborInfo,...] = cdp_neighbors

  def __eq__(self, other):
    return isinstance(other, Switch) and self.ip_address == other.ip_address

  def __hash__(self):
    return hash(self.ip_address)

  def __str__(self):
    return self.ip_address

  def __repr__(self):
    return f"Switch({self.ip_address})"

topology = {
  "127.0.0.1" : Switch( #S1
    "127.0.0.1",
    (
      cast(NeighborInfo, { "IPv4": "127.0.0.2", "sysName" : "S2", "local_interface" : "ge1", "neighbor_interface" : "ge1" }),
      cast(NeighborInfo, { "IPv4": "127.1.1.1", "sysName" : "SEP11-11-11-11-11-00", "local_interface" : "ge2", "neighbor_interface" : "ge1" }),
    )
  ),

  "127.0.0.2": Switch(  # S2
    "127.0.0.2",
    (
      cast( NeighborInfo, { "IPv4": "127.0.0.1", "sysName": "S1", "local_interface": "ge1", "neighbor_interface": "ge1" } ),
      cast( NeighborInfo, { "IPv4": "127.0.0.3", "sysName": "S3", "local_interface": "ge2", "neighbor_interface": "ge1" } ),
      cast( NeighborInfo, { "IPv4": "127.0.0.5", "sysName": "S5", "local_interface": "ge3", "neighbor_interface": "ge1" } ),
      cast( NeighborInfo, { "IPv4": "127.1.2.1", "sysName": "SEP11-11-11-11-11-01", "local_interface": "ge4", "neighbor_interface": "ge1" } ),
      cast( NeighborInfo, { "IPv4": "127.1.2.2", "sysName": "ATA11-11-11-11-11-02", "local_interface": "ge5", "neighbor_interface": "ge1" } ),
    )
  ),

  "127.0.0.3": Switch(  # S3
    "127.0.0.3",
    (
      cast( NeighborInfo, { "IPv4": "127.0.0.2", "sysName": "S2", "local_interface": "ge1", "neighbor_interface": "ge2" } ),
      cast( NeighborInfo, { "IPv4": "127.0.0.5", "sysName": "S5", "local_interface": "ge2", "neighbor_interface": "ge2" } ),
      cast( NeighborInfo, { "IPv4": "127.0.0.4", "sysName": "S3", "local_interface": "ge3", "neighbor_interface": "ge1" } ),
      cast( NeighborInfo, { "IPv4": "127.1.3.1", "sysName": "ATA11-11-11-11-11-03", "local_interface": "ge4", "neighbor_interface": "ge1" } ),
    )
  ),

  "127.0.0.4": Switch(  # S4
    "127.0.0.4",
    (
      cast( NeighborInfo, { "IPv4": "127.0.0.3", "sysName": "S3", "local_interface": "ge1", "neighbor_interface": "ge3" } ),
      cast( NeighborInfo, { "IPv4": "127.0.0.5", "sysName": "S5", "local_interface": "ge2", "neighbor_interface": "ge3" } ),
      cast( NeighborInfo, { "IPv4": "127.0.0.6", "sysName": "S6", "local_interface": "ge3", "neighbor_interface": "ge1" } ),
    )
  ),

  "127.0.0.5": Switch(  # S5
    "127.0.0.5",
    (
      cast( NeighborInfo, { "IPv4": "127.0.0.2", "sysName": "S2", "local_interface": "ge1", "neighbor_interface": "ge3" } ),
      cast( NeighborInfo, { "IPv4": "127.0.0.3", "sysName": "S3", "local_interface": "ge2", "neighbor_interface": "ge2" } ),
      cast( NeighborInfo, { "IPv4": "127.0.0.4", "sysName": "S4", "local_interface": "ge3", "neighbor_interface": "ge2" } ),
      cast( NeighborInfo, { "IPv4": "127.1.5.1", "sysName": "SEP11-11-11-11-11-04", "local_interface": "ge4", "neighbor_interface": "ge1" } ),
    )
  ),

  "127.0.0.6": Switch(  # S6
    "127.0.0.6",
    (
      cast( NeighborInfo, { "IPv4": "127.0.0.4", "sysName": "S4", "local_interface": "ge1", "neighbor_interface": "ge3" } ),
      cast( NeighborInfo, { "IPv4": "127.1.6.1", "sysName": "SEP11-11-11-11-11-05", "local_interface": "ge2", "neighbor_interface": "ge1" } ),
    )
  )
}

learned_mac_address = {
  "127.0.0.1" : {
    "11-11-11-11-11-00" : "ge2",
    "11-11-11-11-11-01" : "ge1",
    "11-11-11-11-11-02" : "ge1",
    "11-11-11-11-11-03" : "ge1",
    "11-11-11-11-11-04" : "ge1",
    "11-11-11-11-11-05" : "ge1",
  },

  "127.0.0.2" : {
    "11-11-11-11-11-00" : "ge1",
    "11-11-11-11-11-01" : "ge4",
    "11-11-11-11-11-02" : "ge5",
    "11-11-11-11-11-03" : "ge2",
    "11-11-11-11-11-04" : "ge3",
    "11-11-11-11-11-05" : "ge3",
  },

  "127.0.0.3" : {
    "11-11-11-11-11-00" : "ge1",
    "11-11-11-11-11-01" : "ge1",
    "11-11-11-11-11-02" : "ge1",
    "11-11-11-11-11-03" : "ge4",
    "11-11-11-11-11-04" : "ge2",
    "11-11-11-11-11-05" : "ge3",
  },

  "127.0.0.4" : {
    "11-11-11-11-11-00" : "ge1",
    "11-11-11-11-11-01" : "ge1",
    "11-11-11-11-11-02" : "ge1",
    "11-11-11-11-11-03" : "ge1",
    "11-11-11-11-11-04" : "ge2",
    "11-11-11-11-11-05" : "ge3",
  },

  "127.0.0.5" : {
    "11-11-11-11-11-00" : "ge1",
    "11-11-11-11-11-01" : "ge1",
    "11-11-11-11-11-02" : "ge1",
    "11-11-11-11-11-03" : "ge2",
    "11-11-11-11-11-04" : "ge4",
    "11-11-11-11-11-05" : "ge3",
  },

  "127.0.0.6" : {
    "11-11-11-11-11-00" : "ge1",
    "11-11-11-11-11-01" : "ge1",
    "11-11-11-11-11-02" : "ge1",
    "11-11-11-11-11-03" : "ge1",
    "11-11-11-11-11-04" : "ge1",
    "11-11-11-11-11-05" : "ge2",
  },

}

distance_to_goal = {
  "127.0.0.1" : {
    "11-11-11-11-11-00" : 0,
    "11-11-11-11-11-01" : 1,
    "11-11-11-11-11-02" : 1,
    "11-11-11-11-11-03" : 2,
    "11-11-11-11-11-04" : 2,
    "11-11-11-11-11-05" : 4
  },

  "127.0.0.2" : {
    "11-11-11-11-11-00" : 1,
    "11-11-11-11-11-01" : 0,
    "11-11-11-11-11-02" : 0,
    "11-11-11-11-11-03" : 1,
    "11-11-11-11-11-04" : 1,
    "11-11-11-11-11-05" : 3,
  },

  "127.0.0.3" : {
    "11-11-11-11-11-00" : 2,
    "11-11-11-11-11-01" : 1,
    "11-11-11-11-11-02" : 1,
    "11-11-11-11-11-03" : 0,
    "11-11-11-11-11-04" : 1,
    "11-11-11-11-11-05" : 2,
  },

  "127.0.0.4" : {
    "11-11-11-11-11-00" : 3,
    "11-11-11-11-11-01" : 2,
    "11-11-11-11-11-02" : 2,
    "11-11-11-11-11-03" : 1,
    "11-11-11-11-11-04" : 1,
    "11-11-11-11-11-05" : 1,
  },

  "127.0.0.5" : {
    "11-11-11-11-11-00" : 2,
    "11-11-11-11-11-01" : 1,
    "11-11-11-11-11-02" : 1,
    "11-11-11-11-11-03" : 1,
    "11-11-11-11-11-04" : 0,
    "11-11-11-11-11-05" : 2,
  },

  "127.0.0.6" : {
    "11-11-11-11-11-00" : 4,
    "11-11-11-11-11-01" : 3,
    "11-11-11-11-11-02" : 3,
    "11-11-11-11-11-03" : 3,
    "11-11-11-11-11-04" : 3,
    "11-11-11-11-11-05" : 0,
  }
}

class FindTheIPPhone(OnlineSearchProblem[Switch, str]):
  def __init__(self, initial_state : Switch, goal_mac_address : str):
    super().__init__(initial_state)
    self.goal_mac_address = goal_mac_address
    self.solution_sysName : tuple[str,str] = (f"SEP{self.goal_mac_address}", f"ATA{self.goal_mac_address}")

  def ACTIONS(self, state: Switch) -> frozenset[ str ]:
    actions : set[str] = set()
    for neighbor in state.cdp_neighbors:
      if all(prefix not in neighbor["sysName"] for prefix in ("ATA", "SEP")):
        actions.add(neighbor["IPv4"])

    return frozenset(actions)

  def ACTION_COST(self, state: Switch, action: str, new_state: Switch) -> float:
    return 1.0

  def IS_GOAL(self, state: Switch) -> bool:
    for neighbor in state.cdp_neighbors:
      if neighbor["sysName"] in self.solution_sysName:
        return True

    return False

  @staticmethod
  def get_heuristic(goal_mac_address : str) -> Callable[[Switch], float]:
    solution_sys_name : tuple[str,str] = (f"SEP{goal_mac_address}", f"ATA{goal_mac_address}")
    def h(state : Switch) -> float:
      return distance_to_goal[state.ip_address][goal_mac_address]

    return h

  @staticmethod
  def get_action_value_heuristic(goal_mac_address : str) -> Callable[[Switch, str], float]:
    def h(state : Switch, action : str) -> float:
      best_guess_interface = next( interface for mac_add, interface in learned_mac_address[state.ip_address].items() if mac_add == goal_mac_address )
      ip_to_best_guess = next ( best_neighbor["IPv4"] for best_neighbor in state.cdp_neighbors if best_neighbor["local_interface"] == best_guess_interface )

      return 0.0 if action == ip_to_best_guess else 1.0

    return h

__all__ = ["FindTheIPPhone"]