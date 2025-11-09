from ..constraint_satisfaction_problem import ConstraintSatisfactionProblem
from ..ConstraintPropagation.ac3_propagation import ac3
from typing import Any, Callable
import copy


def inference(csp : ConstraintSatisfactionProblem, var : str, assignment : dict[str, Any]) -> dict[str, set[Any]] | bool:
  neighboring_variables = { constraint.variables[0] if constraint.variables[0] != var else constraint.variables[1] for constraint in csp.var_to_constraints[var] }
  neighboring_arcs = { (neighboring_variable, var) for neighboring_variable in neighboring_variables }

  temp_domain = {}
  for variable in csp.variables:
    temp_domain[variable] = { assignment[variable] } if variable in assignment else copy.deepcopy(csp.domains[variable])

  temp_csp = ConstraintSatisfactionProblem( variables=csp.variables, domains=temp_domain )
  if ac3( temp_csp, arcs=neighboring_arcs ):
    return temp_csp.domains
  else:
    return False