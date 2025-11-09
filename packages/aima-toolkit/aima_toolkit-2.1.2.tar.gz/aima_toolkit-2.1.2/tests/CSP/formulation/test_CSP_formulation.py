import pytest
from typing import Any

from src.aima_toolkit.ConstraintSatisfactionProblemPackage import ConstraintSatisfactionProblem, Constraint

def test_CSP_creation_wrong_paramaters():
  with pytest.raises(AssertionError):
    ConstraintSatisfactionProblem(["A", "B", "C"], { "A": { 1, 2 }, "B": { 2, 3 }, "D": { 4, 5 } })

def test_CSP_creation():
  test_csp = ConstraintSatisfactionProblem( [ "A", "B", "C" ], { "A": { 1, 2 }, "B": { 2, 3 }, "C": { 4, 5 } } )
  assert "A" in test_csp.variables
  assert "B" in test_csp.variables
  assert "C" in test_csp.variables
  assert test_csp.domains["A"] == {1, 2}
  assert test_csp.domains["B"] == {2, 3}
  assert test_csp.domains["C"] == {4, 5}


def test_CSP_constraints():
  def equal_constraint(assignment: dict[ str, Any ]):
    return assignment[ "A" ] == assignment[ "B" ]

  test_csp = ConstraintSatisfactionProblem( [ "A", "B", "C" ], { "A": { 1, 2 }, "B": { 2, 3 }, "C": { 4, 5 } } )
  equal_A_B_constraint = Constraint(["A", "B"], equal_constraint)
  test_csp.add_constraint(equal_A_B_constraint)

  assert equal_A_B_constraint in test_csp.var_to_constraints[ "A" ]
  assert equal_A_B_constraint in test_csp.var_to_constraints[ "B" ]
  assert equal_A_B_constraint not in test_csp.var_to_constraints[ "C" ]

  # test bad assignment (out of domain)
  with pytest.raises(AssertionError):
    invalid_assignment = { "A": 1, "B": 4, "C": 7}
    test_csp.is_consistent(invalid_assignment)

  # test good assignment (inconsistent assignment)
  inconsistent_assignment = { "A": 1, "B": 2, "C": 4}
  inconsistent_assignment2 = { "A": 2, "B": 3, "C": 4}
  assert test_csp.is_consistent(inconsistent_assignment) == False
  assert test_csp.is_consistent(inconsistent_assignment2) == False

  # test good assignment (consistent assignment)
  consistent_assignment = { "A": 2, "B": 2, "C": 4}
  consistent_assignment2 = { "A": 2, "B": 2, "C": 5}
  assert test_csp.is_consistent(consistent_assignment) == True
  assert test_csp.is_consistent(consistent_assignment2) == True
