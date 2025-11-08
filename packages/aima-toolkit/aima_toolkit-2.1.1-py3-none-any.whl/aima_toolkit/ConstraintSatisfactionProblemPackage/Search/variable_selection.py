from ..constraint_satisfaction_problem import Constraint, ConstraintSatisfactionProblem
from typing import Any, Callable

def select_unassigned_variable(csp : ConstraintSatisfactionProblem, assignment : dict[str, Any]) -> str:
  remaining_variables = set(csp.variables).difference(assignment.keys())
  assert len(remaining_variables) > 0

  chosen_variable = remaining_variables.pop()
  for variable in remaining_variables:
    chosen_var_domain_len = len(csp.inferences[chosen_variable])
    to_check_var_domain_len = len(csp.inferences[variable])
    if to_check_var_domain_len < chosen_var_domain_len or (to_check_var_domain_len == chosen_var_domain_len and  len(csp.var_to_constraints[variable]) > len(csp.domains[chosen_variable])) :
      chosen_variable = variable

  return chosen_variable