from ..constraint_satisfaction_problem import Constraint, ConstraintSatisfactionProblem
from typing import Any
import copy

def alldiff_constraint_func(assignment : dict[str, Any]) -> bool:
  return len(assignment.keys()) == len(set(assignment.values()))

def get_all_diff_constraint(vars : set[str]):
  return Constraint(list(vars), alldiff_constraint_func)

def add_alldiff_constraint_as_binary_constraint(csp : ConstraintSatisfactionProblem, vars : set[str]):
  assert all(var in csp.variables for var in vars)
  already_seen_vars : set[str] = set()
  for var1 in vars:
    already_seen_vars.add(var1)
    for var2 in vars - already_seen_vars:
      csp.add_constraint(Constraint([var1, var2], alldiff_constraint_func))

def alldiff_constraint_propagation(csp : ConstraintSatisfactionProblem, vars : set[str]):
  assert all(var in csp.variables for var in vars)
  all_values = set()
  remaining_vars = copy.deepcopy(vars)
  domain_copy = copy.deepcopy(csp.domains)
  for var in vars:
    if len(domain_copy[var]) == 1:
      value_to_remove = csp.domains[var].pop()

      remaining_vars.remove(var) # Remove the variable from remaining vars since it has a value now
      del domain_copy[var]  # Remove this variable's domain from the domain copy

      if value_to_remove in all_values:
        all_values.remove(value_to_remove) # If it was saved beforehand as a value that can be assigned remove it

      for remaining_var in remaining_vars:
        if value_to_remove in domain_copy[remaining_var]:
          domain_copy[remaining_var].remove(value_to_remove)
    elif len(domain_copy[var]) == 0:
      return False
    else:
      all_values |= domain_copy[var]

  return len(remaining_vars) <= len(all_values)

__all__ = ['alldiff_constraint_propagation', 'get_all_diff_constraint', 'add_alldiff_constraint_as_binary_constraint']