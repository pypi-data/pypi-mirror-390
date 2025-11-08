from src.aima_toolkit.ConstraintSatisfactionProblemPackage import ConstraintSatisfactionProblem, Constraint
from src.aima_toolkit.ConstraintSatisfactionProblemPackage.ConstraintPropagation import ac3

def test_ac3_propagation():
  integers_from_zero_to_ten = set(range(11))
  test_csp = ConstraintSatisfactionProblem(variables=['X', 'Y'], domains={'X': integers_from_zero_to_ten, 'Y': integers_from_zero_to_ten})
  sum_geq_15 = Constraint(['X', 'Y'], lambda assignment: assignment['X'] + assignment['Y'] >= 15)

  test_csp.add_constraint(sum_geq_15)
  ac3(test_csp)

  for x in test_csp.domains['X']:
    assert all( any(constraint.satisfied({ 'X' : x, 'Y' : y}) for y in test_csp.domains['Y']) for constraint in test_csp.constraints )

  for y in test_csp.domains['Y']:
    assert all( any(constraint.satisfied({ 'X' : x, 'Y' : y}) for x in test_csp.domains['X']) for constraint in test_csp.constraints )

