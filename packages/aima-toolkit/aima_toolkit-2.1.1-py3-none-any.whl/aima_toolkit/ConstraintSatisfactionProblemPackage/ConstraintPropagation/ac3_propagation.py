from ..constraint_satisfaction_problem import ConstraintSatisfactionProblem, Constraint
from ...SearchProblemPackage.queue import FIFOQueue
import copy

VariableTuple = tuple[str, str]

def ac3(csp : ConstraintSatisfactionProblem, arcs : set[tuple[str, str]] | None = None) -> bool:
  constrained_variables = FIFOQueue[VariableTuple]()

  if arcs is not None:
    for arc in arcs:
      constrained_variables.push(arc)
  else:
    for constraint in csp.constraints:
      assert len(constraint.variables) == 2, "Tried to call ac3 propagation (Arc Consistency), on problems with non binary constraints"
      constrained_variables.push((constraint.variables[0], constraint.variables[1]))
      constrained_variables.push((constraint.variables[1], constraint.variables[0]))

  while len(constrained_variables) > 0:
    x1, x2 = constrained_variables.pop()

    if remove_inconsistencies(csp, x1, x2):
      if len(csp.domains[x1]) == 0:
        return False

      for neighboring_constraint in csp.var_to_constraints[x1]:
        first_var, second_var = neighboring_constraint.variables
        other_variable = first_var if first_var != x1 else second_var

        if other_variable == x2: continue
        new_variable_tuple = (other_variable, x1)

        if new_variable_tuple not in constrained_variables.que:
          constrained_variables.push(new_variable_tuple)



  return True

def remove_inconsistencies(csp : ConstraintSatisfactionProblem, x1 : str, x2 : str) -> bool:
  d1 = copy.deepcopy(csp.domains[x1])

  constraints = [ constraint  for constraint in csp.constraints if {x1, x2} == set(constraint.variables) ]
  if len(constraints) == 0: return False

  changed = False
  for x in csp.domains[x1]:
    if not any( all( constraint.satisfied( { x1 : x, x2 : y} ) for constraint in constraints)  for y in csp.domains[x2]):
      changed = True
      d1.remove(x)

  csp.domains[x1] = d1
  return changed

__all__ = ['ac3']