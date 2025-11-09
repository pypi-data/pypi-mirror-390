from src.aima_toolkit.ConstraintSatisfactionProblemPackage import ConstraintSatisfactionProblem, Constraint
from src.aima_toolkit.ConstraintSatisfactionProblemPackage.PremadeConstraints import alldiff_constraint, add_alldiff_constraint_as_binary_constraint, alldiff_constraint_propagation
from src.aima_toolkit.ConstraintSatisfactionProblemPackage.ConstraintPropagation import ac3, node_constraint_propagation

def test_alldiff_constraint():
  integers_from_zero_to_five = set(range(6))
  test_csp = ConstraintSatisfactionProblem(variables=['X1', 'X2', 'X3', 'X4'], domains={'X1': integers_from_zero_to_five, 'X2': integers_from_zero_to_five, 'X3': integers_from_zero_to_five, 'X4': integers_from_zero_to_five})
  assert alldiff_constraint_propagation(test_csp, {'X1', 'X2', 'X3', 'X4'}) == True

  test_csp_2 = ConstraintSatisfactionProblem(variables=['X1', 'X2', 'X3', 'X4'], domains={'X1': {1}, 'X2': {1,2}, 'X3': {1,2,3,4}, 'X4': {2,4}})
  assert alldiff_constraint_propagation(test_csp_2, {'X1', 'X2', 'X3', 'X4'}) == True

  test_csp_3 = ConstraintSatisfactionProblem(variables=['X1', 'X2', 'X3', 'X4'], domains={'X1': {1}, 'X2': {1}, 'X3': {1,2,3,4}, 'X4': {2,4}})
  assert alldiff_constraint_propagation(test_csp_3, {'X1', 'X2', 'X3', 'X4'}) == False

  test_csp_4 = ConstraintSatisfactionProblem(variables=['X1', 'X2', 'X3', 'X4'], domains={'X1': {1}, 'X2': {}, 'X3': {1,2,3,4}, 'X4': {2,4}})
  assert alldiff_constraint_propagation(test_csp_4, {'X1', 'X2', 'X3', 'X4'}) == False

def test_alldiff_as_binary():
  test_csp_2 = ConstraintSatisfactionProblem(variables=['X1', 'X2', 'X3', 'X4'], domains={'X1': {1}, 'X2': {1,2}, 'X3': {1,2,3,4}, 'X4': {2,4}})
  add_alldiff_constraint_as_binary_constraint(test_csp_2, {'X1', 'X2', 'X3', 'X4'})

  ac3(test_csp_2)
  assert test_csp_2.domains['X1'] == {1}
  assert test_csp_2.domains['X2'] == {2}
  assert test_csp_2.domains['X3'] == {3}
  assert test_csp_2.domains['X4'] == {4}

def test_mini_sudoku():
  """
  [ - 1 - ]
  [ 2 - 4 ]
  [ 8 - - ]
  """

  variables = [ f'X{i}' for i in range(1, 10) ]
  sudoku_domain = set(range(1,10))

  mini_sudoku_csp = ConstraintSatisfactionProblem(variables=variables, domains = dict( [ ( variable , sudoku_domain) for variable in variables ] ) )

  # Add constraints for predefined values
  mini_sudoku_csp.add_constraint(Constraint(variables=['X2'], constraint_func = lambda assignment: assignment['X2'] == 1))
  mini_sudoku_csp.add_constraint(Constraint(variables=['X4'], constraint_func = lambda assignment: assignment['X4'] == 2))
  mini_sudoku_csp.add_constraint(Constraint(variables=['X6'], constraint_func = lambda assignment: assignment['X6'] == 4))
  mini_sudoku_csp.add_constraint(Constraint(variables=['X7'], constraint_func = lambda assignment: assignment['X7'] == 8))

  node_constraint_propagation(mini_sudoku_csp, remove_constraints_after=True) # Remove all of the constraint

  add_alldiff_constraint_as_binary_constraint(mini_sudoku_csp, set(variables)) # Add the alldiff constraint
  assert  ac3(mini_sudoku_csp) == True # call ac3

  assert mini_sudoku_csp.domains['X1'] == mini_sudoku_csp.domains['X3'] == mini_sudoku_csp.domains['X5'] == mini_sudoku_csp.domains['X8'] == mini_sudoku_csp.domains['X9'] == {3,5,6,7,9}
  assert mini_sudoku_csp.domains['X2'] == {1}
  assert mini_sudoku_csp.domains['X4'] == {2}
  assert mini_sudoku_csp.domains['X6'] == {4}
  assert mini_sudoku_csp.domains['X7'] == {8}

  mini_sudoku_csp_2 = ConstraintSatisfactionProblem(variables=variables, domains = dict( [ ( variable , sudoku_domain) for variable in variables ] ) )

  # Add constraints for predefined values
  mini_sudoku_csp_2.add_constraint(Constraint(variables=['X2'], constraint_func = lambda assignment: assignment['X2'] == 1))
  mini_sudoku_csp_2.add_constraint(Constraint(variables=['X4'], constraint_func = lambda assignment: assignment['X4'] == 2))
  mini_sudoku_csp_2.add_constraint(Constraint(variables=['X6'], constraint_func = lambda assignment: assignment['X6'] == 4))
  mini_sudoku_csp_2.add_constraint(Constraint(variables=['X7'], constraint_func = lambda assignment: assignment['X7'] == 8))

  node_constraint_propagation(mini_sudoku_csp_2, remove_constraints_after=True) # Remove all of the constraint
  add_alldiff_constraint_as_binary_constraint(mini_sudoku_csp_2, set(variables)) # Add the alldiff constraint

  mini_sudoku_csp_2.domains['X3'] = {2, 5, 1, 3}
  mini_sudoku_csp_2.domains['X9'] = {3, 8}

  assert ac3(mini_sudoku_csp_2) == True
  assert mini_sudoku_csp_2.domains['X1'] == mini_sudoku_csp_2.domains['X5'] == mini_sudoku_csp_2.domains['X8'] == {6,7,9}
  assert mini_sudoku_csp_2.domains['X3'] == {5}
  assert mini_sudoku_csp_2.domains['X9'] == {3}

def test_easy_sudoku():
  """
  [ 8 7 - - 4 2 9 1 5 ]
  [ 1 3 - 5 - 8 - 2 - ]
  [ 5 - 2 - - - - 8 3 ]
  [ 4 - 3 - - - 8 7 - ]
  [ - 6 7 - - 1 3 - - ]
  [ - - - - - - 2 5 - ]
  [ - - 4 6 - 5 - 3 - ]
  [ 6 - 1 - - 4 5 - 8 ]
  [ - 8 - 2 - - - - 4 ]
  """

  variables = [f"X{i}{j}" for i in range(1, 10) for j in range(1, 10)]
  sudoku_domain = set( range( 1, 10 ) )
  easy_sudoku_csp = ConstraintSatisfactionProblem(variables=variables, domains = dict( [ ( variable , sudoku_domain) for variable in variables ] ) )

  # Add constraints for predefined values
  easy_sudoku_csp.add_constraint(Constraint(variables=['X11'], constraint_func = lambda assignment: assignment['X11'] == 8))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X12'], constraint_func = lambda assignment: assignment['X12'] == 7))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X15'], constraint_func = lambda assignment: assignment['X15'] == 4))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X16'], constraint_func = lambda assignment: assignment['X16'] == 2))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X17'], constraint_func = lambda assignment: assignment['X17'] == 9))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X18'], constraint_func = lambda assignment: assignment['X18'] == 1))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X19'], constraint_func = lambda assignment: assignment['X19'] == 5))

  easy_sudoku_csp.add_constraint(Constraint(variables=['X21'], constraint_func = lambda assignment: assignment['X21'] == 1))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X22'], constraint_func = lambda assignment: assignment['X22'] == 3))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X24'], constraint_func = lambda assignment: assignment['X24'] == 5))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X26'], constraint_func = lambda assignment: assignment['X26'] == 8))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X28'], constraint_func = lambda assignment: assignment['X28'] == 2))

  easy_sudoku_csp.add_constraint(Constraint(variables=['X31'], constraint_func = lambda assignment: assignment['X31'] == 5))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X33'], constraint_func = lambda assignment: assignment['X33'] == 2))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X38'], constraint_func = lambda assignment: assignment['X38'] == 8))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X39'], constraint_func = lambda assignment: assignment['X39'] == 3))

  easy_sudoku_csp.add_constraint(Constraint(variables=['X41'], constraint_func = lambda assignment: assignment['X41'] == 4))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X43'], constraint_func = lambda assignment: assignment['X43'] == 3))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X47'], constraint_func = lambda assignment: assignment['X47'] == 8))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X48'], constraint_func = lambda assignment: assignment['X48'] == 7))

  easy_sudoku_csp.add_constraint(Constraint(variables=['X52'], constraint_func = lambda assignment: assignment['X52'] == 6))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X53'], constraint_func = lambda assignment: assignment['X53'] == 7))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X56'], constraint_func = lambda assignment: assignment['X56'] == 1))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X57'], constraint_func = lambda assignment: assignment['X57'] == 3))

  easy_sudoku_csp.add_constraint(Constraint(variables=['X67'], constraint_func = lambda assignment: assignment['X67'] == 2))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X68'], constraint_func = lambda assignment: assignment['X68'] == 5))

  easy_sudoku_csp.add_constraint(Constraint(variables=['X73'], constraint_func = lambda assignment: assignment['X73'] == 4))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X74'], constraint_func = lambda assignment: assignment['X74'] == 6))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X76'], constraint_func = lambda assignment: assignment['X76'] == 5))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X78'], constraint_func = lambda assignment: assignment['X78'] == 3))

  easy_sudoku_csp.add_constraint(Constraint(variables=['X81'], constraint_func = lambda assignment: assignment['X81'] == 6))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X83'], constraint_func = lambda assignment: assignment['X83'] == 1))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X86'], constraint_func = lambda assignment: assignment['X86'] == 4))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X87'], constraint_func = lambda assignment: assignment['X87'] == 5))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X89'], constraint_func = lambda assignment: assignment['X89'] == 8))

  easy_sudoku_csp.add_constraint(Constraint(variables=['X92'], constraint_func = lambda assignment: assignment['X92'] == 8))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X94'], constraint_func = lambda assignment: assignment['X94'] == 2))
  easy_sudoku_csp.add_constraint(Constraint(variables=['X99'], constraint_func = lambda assignment: assignment['X99'] == 4))

  node_constraint_propagation(easy_sudoku_csp, remove_constraints_after=True) # Remove all of the constraint

  for row_block in range( 3 ):  # 0,1,2 -> row bands
    for col_block in range( 3 ):  # 0,1,2 -> column bands
      block_vars = {
        f"X{r}{c}"
        for r in range( row_block * 3 + 1, row_block * 3 + 4 )
        for c in range( col_block * 3 + 1, col_block * 3 + 4 )
      }
      add_alldiff_constraint_as_binary_constraint( easy_sudoku_csp, block_vars )

  for i in range(1,10):
    add_alldiff_constraint_as_binary_constraint(easy_sudoku_csp, { f"X{i}{col}" for col in range(1,10) } ) # Add all vertical constraints
    add_alldiff_constraint_as_binary_constraint(easy_sudoku_csp, { f"X{row}{i}" for row in range(1,10) } ) # Add all horizontal constraints

  assert ac3(easy_sudoku_csp) == True
  assert easy_sudoku_csp.domains['X11'] == {8}
  assert easy_sudoku_csp.domains['X12'] == {7}
  assert easy_sudoku_csp.domains['X13'] == {6}
  assert easy_sudoku_csp.domains['X14'] == {3}
  assert easy_sudoku_csp.domains['X15'] == {4}
  assert easy_sudoku_csp.domains['X16'] == {2}
  assert easy_sudoku_csp.domains['X17'] == {9}
  assert easy_sudoku_csp.domains['X18'] == {1}
  assert easy_sudoku_csp.domains['X19'] == {5}

  assert easy_sudoku_csp.domains['X21'] == {1}
  assert easy_sudoku_csp.domains['X22'] == {3}
  assert easy_sudoku_csp.domains['X23'] == {9}
  assert easy_sudoku_csp.domains['X24'] == {5}
  assert easy_sudoku_csp.domains['X25'] == {6}
  assert easy_sudoku_csp.domains['X26'] == {8}
  assert easy_sudoku_csp.domains['X27'] == {4}
  assert easy_sudoku_csp.domains['X28'] == {2}
  assert easy_sudoku_csp.domains['X29'] == {7}

  assert easy_sudoku_csp.domains['X31'] == {5}
  assert easy_sudoku_csp.domains['X32'] == {4}
  assert easy_sudoku_csp.domains['X33'] == {2}
  assert easy_sudoku_csp.domains['X34'] == {1}
  assert easy_sudoku_csp.domains['X35'] == {9}
  assert easy_sudoku_csp.domains['X36'] == {7}
  assert easy_sudoku_csp.domains['X37'] == {6}
  assert easy_sudoku_csp.domains['X38'] == {8}
  assert easy_sudoku_csp.domains['X39'] == {3}

  assert easy_sudoku_csp.domains['X41'] == {4}
  assert easy_sudoku_csp.domains['X42'] == {5}
  assert easy_sudoku_csp.domains['X43'] == {3}
  assert easy_sudoku_csp.domains['X44'] == {9}
  assert easy_sudoku_csp.domains['X45'] == {2}
  assert easy_sudoku_csp.domains['X46'] == {6}
  assert easy_sudoku_csp.domains['X47'] == {8}
  assert easy_sudoku_csp.domains['X48'] == {7}
  assert easy_sudoku_csp.domains['X49'] == {1}

  assert easy_sudoku_csp.domains['X51'] == {2}
  assert easy_sudoku_csp.domains['X52'] == {6}
  assert easy_sudoku_csp.domains['X53'] == {7}
  assert easy_sudoku_csp.domains['X54'] == {8}
  assert easy_sudoku_csp.domains['X55'] == {5}
  assert easy_sudoku_csp.domains['X56'] == {1}
  assert easy_sudoku_csp.domains['X57'] == {3}
  assert easy_sudoku_csp.domains['X58'] == {4}
  assert easy_sudoku_csp.domains['X59'] == {9}

  assert easy_sudoku_csp.domains['X61'] == {9}
  assert easy_sudoku_csp.domains['X62'] == {1}
  assert easy_sudoku_csp.domains['X63'] == {8}
  assert easy_sudoku_csp.domains['X64'] == {4}
  assert easy_sudoku_csp.domains['X65'] == {7}
  assert easy_sudoku_csp.domains['X66'] == {3}
  assert easy_sudoku_csp.domains['X67'] == {2}
  assert easy_sudoku_csp.domains['X68'] == {5}
  assert easy_sudoku_csp.domains['X69'] == {6}

  assert easy_sudoku_csp.domains['X71'] == {7}
  assert easy_sudoku_csp.domains['X72'] == {9}
  assert easy_sudoku_csp.domains['X73'] == {4}
  assert easy_sudoku_csp.domains['X74'] == {6}
  assert easy_sudoku_csp.domains['X75'] == {8}
  assert easy_sudoku_csp.domains['X76'] == {5}
  assert easy_sudoku_csp.domains['X77'] == {1}
  assert easy_sudoku_csp.domains['X78'] == {3}
  assert easy_sudoku_csp.domains['X79'] == {2}

  assert easy_sudoku_csp.domains['X81'] == {6}
  assert easy_sudoku_csp.domains['X82'] == {2}
  assert easy_sudoku_csp.domains['X83'] == {1}
  assert easy_sudoku_csp.domains['X84'] == {7}
  assert easy_sudoku_csp.domains['X85'] == {3}
  assert easy_sudoku_csp.domains['X86'] == {4}
  assert easy_sudoku_csp.domains['X87'] == {5}
  assert easy_sudoku_csp.domains['X88'] == {9}
  assert easy_sudoku_csp.domains['X89'] == {8}

  assert easy_sudoku_csp.domains['X91'] == {3}
  assert easy_sudoku_csp.domains['X92'] == {8}
  assert easy_sudoku_csp.domains['X93'] == {5}
  assert easy_sudoku_csp.domains['X94'] == {2}
  assert easy_sudoku_csp.domains['X95'] == {1}
  assert easy_sudoku_csp.domains['X96'] == {9}
  assert easy_sudoku_csp.domains['X97'] == {7}
  assert easy_sudoku_csp.domains['X98'] == {6}
  assert easy_sudoku_csp.domains['X99'] == {4}
