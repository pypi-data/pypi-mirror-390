from src.aima_toolkit.ConstraintSatisfactionProblemPackage import ConstraintSatisfactionProblem, Constraint
from src.aima_toolkit.ConstraintSatisfactionProblemPackage.ConstraintPropagation import node_constraint_propagation
def test_node_consistency():
  one_to_ten_domain = set(range(1, 11))
  test_csp = ConstraintSatisfactionProblem(['X', 'Y'], { 'X' : one_to_ten_domain, 'Y' : one_to_ten_domain })
  x_bigger_then_5_constraint = Constraint(['X'], lambda assignment: assignment['X'] > 5)
  test_csp.add_constraint(x_bigger_then_5_constraint)

  assert set(test_csp.variables) == {'X', 'Y'}
  assert x_bigger_then_5_constraint in test_csp.constraints
  assert test_csp.domains['X'] == one_to_ten_domain
  assert test_csp.domains['Y'] == one_to_ten_domain

  node_constraint_propagation(test_csp, remove_constraints_after=True)
  assert set(test_csp.variables) == {'X', 'Y'}
  assert x_bigger_then_5_constraint not in test_csp.constraints
  assert test_csp.domains['X'] == {6,7,8,9,10}
  assert test_csp.domains['Y'] == one_to_ten_domain

def test_node_consistency_without_remove_constraints_after():
  one_to_ten_domain = set(range(1, 11))
  test_csp = ConstraintSatisfactionProblem(['X', 'Y'], { 'X' : one_to_ten_domain, 'Y' : one_to_ten_domain })
  x_bigger_then_5_constraint = Constraint(['X'], lambda assignment: assignment['X'] > 5)
  test_csp.add_constraint(x_bigger_then_5_constraint)

  assert set(test_csp.variables) == {'X', 'Y'}
  assert x_bigger_then_5_constraint in test_csp.constraints
  assert test_csp.domains['X'] == one_to_ten_domain
  assert test_csp.domains['Y'] == one_to_ten_domain

  node_constraint_propagation(test_csp, remove_constraints_after=False)
  assert set(test_csp.variables) == {'X', 'Y'}
  assert x_bigger_then_5_constraint in test_csp.constraints
  assert test_csp.domains['X'] == {6,7,8,9,10}
  assert test_csp.domains['Y'] == one_to_ten_domain
