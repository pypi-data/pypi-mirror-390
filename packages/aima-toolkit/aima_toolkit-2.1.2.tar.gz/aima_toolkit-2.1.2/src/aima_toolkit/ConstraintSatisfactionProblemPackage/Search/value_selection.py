from ..constraint_satisfaction_problem import Constraint, ConstraintSatisfactionProblem
from ...SearchProblemPackage.queue import PriorityQueue
from typing import Any, Callable

def least_constraining_value_eval_func(csp : ConstraintSatisfactionProblem, var : str, assignment : dict[str, Any ]) -> Callable[[ Any ], float ]:
  already_assigned_variables = assignment.keys( )
  neighboring_variables = { constraint.variables[0] if constraint.variables[0] != var else constraint.variables[1] for constraint in csp.var_to_constraints[var] if all( constraint_var not in already_assigned_variables for constraint_var in constraint.variables ) }
  def eval_func(value_for_var : Any) -> float:
    assert value_for_var in csp.inferences[var]
    conflicts = 0
    for neighbor in neighboring_variables:
      for neighbor_values in csp.inferences[neighbor]:
        if not all(  constraint.satisfied({ var : value_for_var, neighbor : neighbor_values}) for constraint in csp.var_to_constraints[neighbor] if var in constraint.variables ):
          conflicts += 1

    return conflicts

  return eval_func

def order_domain_values(csp : ConstraintSatisfactionProblem, var : str, assignment : dict[str, Any ]) -> PriorityQueue[Any]:
  prio_que = PriorityQueue[Any]( least_constraining_value_eval_func( csp, var, assignment ) )
  for value in csp.domains[var]:
    prio_que.push(value)

  return prio_que
