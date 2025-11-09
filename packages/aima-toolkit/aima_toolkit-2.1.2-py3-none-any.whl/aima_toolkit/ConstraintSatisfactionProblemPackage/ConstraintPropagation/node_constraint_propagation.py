from ..constraint_satisfaction_problem import ConstraintSatisfactionProblem, Constraint
from ...SearchProblemPackage.queue import FIFOQueue


def node_constraint_propagation(csp: ConstraintSatisfactionProblem, remove_constraints_after : bool = True) -> bool:
  constraints = FIFOQueue()

  for constraint in csp.constraints:
    if len(constraint.variables) == 1:
      constraints.push(constraint)

  while len(constraints) > 0:
    constraint = constraints.pop()
    variable = constraint.variables[0]

    variable_domain = csp.domains[variable]
    csp.domains[variable] = {value for value in variable_domain if constraint.satisfied({variable : value})}

    if len(csp.domains[variable]) == 0:
      return False

  if remove_constraints_after:
    csp.constraints = [constraint for constraint in csp.constraints if len(constraint.variables) != 1]
    for variable in csp.variables:
      csp.var_to_constraints[variable] = [constraint for constraint in csp.var_to_constraints[variable] if len(constraint.variables) != 1]
  return True

__all__ = ["node_constraint_propagation"]