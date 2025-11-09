from src.aima_toolkit.ConstraintSatisfactionProblemPackage import ConstraintSatisfactionProblem, Constraint
from src.aima_toolkit.ConstraintSatisfactionProblemPackage.PremadeConstraints import alldiff_constraint, add_alldiff_constraint_as_binary_constraint, alldiff_constraint_propagation
from src.aima_toolkit.ConstraintSatisfactionProblemPackage.ConstraintPropagation import ac3, node_constraint_propagation
from src.aima_toolkit.ConstraintSatisfactionProblemPackage.Search.backtracking_search import backtracking_search

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
  assert ac3(mini_sudoku_csp) == True # call ac3

  assignment = backtracking_search(mini_sudoku_csp)
  assert mini_sudoku_csp.is_consistent(assignment) == True


def test_medium_sudoku():
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
  medium_sudoku_csp = ConstraintSatisfactionProblem(variables=variables, domains = dict( [ ( variable , sudoku_domain) for variable in variables ] ) )

  medium_sudoku_csp.domains[ 'X16' ] = { 3 }
  medium_sudoku_csp.domains[ 'X17' ] = { 4 }
  medium_sudoku_csp.domains[ 'X18' ] = { 6 }

  medium_sudoku_csp.domains[ 'X28' ] = { 9 }

  medium_sudoku_csp.domains[ 'X35' ] = { 5 }
  medium_sudoku_csp.domains[ 'X38' ] = { 8 }

  medium_sudoku_csp.domains[ 'X42' ] = { 8 }
  medium_sudoku_csp.domains[ 'X43' ] = { 4 }

  medium_sudoku_csp.domains[ 'X54' ] = { 8 }
  medium_sudoku_csp.domains[ 'X55' ] = { 9 }
  medium_sudoku_csp.domains[ 'X56' ] = { 5 }
  medium_sudoku_csp.domains[ 'X57' ] = { 3 }
  medium_sudoku_csp.domains[ 'X58' ] = { 7 }

  medium_sudoku_csp.domains[ 'X61' ] = { 5 }
  medium_sudoku_csp.domains[ 'X62' ] = { 7 }
  medium_sudoku_csp.domains[ 'X66' ] = { 4 }
  medium_sudoku_csp.domains[ 'X67' ] = { 6 }

  medium_sudoku_csp.domains[ 'X73' ] = { 7 }
  medium_sudoku_csp.domains[ 'X74' ] = { 2 }
  medium_sudoku_csp.domains[ 'X79' ] = { 6 }

  medium_sudoku_csp.domains[ 'X81' ] = { 8 }
  medium_sudoku_csp.domains[ 'X82' ] = { 9 }
  medium_sudoku_csp.domains[ 'X83' ] = { 6 }
  medium_sudoku_csp.domains[ 'X86' ] = { 7 }
  medium_sudoku_csp.domains[ 'X87' ] = { 2 }
  medium_sudoku_csp.domains[ 'X88' ] = { 5 }
  medium_sudoku_csp.domains[ 'X89' ] = { 1 }

  medium_sudoku_csp.domains[ 'X98' ] = { 4 }
  medium_sudoku_csp.domains[ 'X99' ] = { 7 }


  for row_block in range( 3 ):  # 0,1,2 -> row bands
    for col_block in range( 3 ):  # 0,1,2 -> column bands
      block_vars = {
        f"X{r}{c}"
        for r in range( row_block * 3 + 1, row_block * 3 + 4 )
        for c in range( col_block * 3 + 1, col_block * 3 + 4 )
      }
      add_alldiff_constraint_as_binary_constraint( medium_sudoku_csp, block_vars )

  for i in range(1,10):
    add_alldiff_constraint_as_binary_constraint(medium_sudoku_csp, { f"X{i}{col}" for col in range(1,10) } ) # Add all vertical constraints
    add_alldiff_constraint_as_binary_constraint(medium_sudoku_csp, { f"X{row}{i}" for row in range(1,10) } ) # Add all horizontal constraints

  assert ac3(medium_sudoku_csp) == True
  assignment = backtracking_search(medium_sudoku_csp)
  assert medium_sudoku_csp.is_consistent(assignment) == True
  print(assignment)
