from ..constraint_satisfaction_problem import Constraint, ConstraintSatisfactionProblem
from ..ConstraintPropagation.ac3_propagation import ac3
from ...SearchProblemPackage.queue import PriorityQueue
from typing import Any, Callable
import copy


from .search_inference import inference
from .value_selection import order_domain_values
from .variable_selection import select_unassigned_variable

def backtracking_search(csp : ConstraintSatisfactionProblem) -> dict[str, Any] | bool:
  if csp.inferences is None: csp.inferences = copy.deepcopy(csp.domains)
  result = backtrack(csp, {})
  csp.inferences = None
  return result

def backtrack(csp : ConstraintSatisfactionProblem, assignment : dict[str, Any]) -> dict[str, Any] | bool:
  if len(assignment) == len(csp.variables): return assignment

  var = select_unassigned_variable(csp, assignment)
  for value in order_domain_values(csp, var, assignment):
    if is_var_value_consistent(csp, var, value, assignment):
      assignment[var] = value
      old_inferences = csp.inferences
      inferences = inference(csp, var, assignment)

      if inferences != False:
        csp.inferences = inferences
        result = backtrack(csp, assignment)
        if result != False: return result
        csp.inferences = old_inferences

      del assignment[var]
      
  return False


def is_var_value_consistent(csp : ConstraintSatisfactionProblem, var : str, value : Any, assignment : dict[str, Any ]) -> bool:
  already_assigned_variables = assignment.keys( )
  constraints_to_check = { constraint for constraint in csp.var_to_constraints[var] if any(  const_var in already_assigned_variables for const_var in constraint.variables) }

  for constraint in constraints_to_check:
    other_variable = constraint.variables[0] if constraint.variables[0] != var else constraint.variables[1]
    if not constraint.satisfied( { var : value, other_variable : assignment[other_variable ] } ): return False

  return True


__all__ = ['backtracking_search']