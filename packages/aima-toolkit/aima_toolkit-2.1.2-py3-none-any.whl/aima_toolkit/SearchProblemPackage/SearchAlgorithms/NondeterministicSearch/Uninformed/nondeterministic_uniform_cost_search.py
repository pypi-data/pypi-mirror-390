from ..Informed.and_or_star_search import and_or_star_search
from .... import SearchProblem

def nondeterministic_uniform_cost_search(problem: SearchProblem):
  return and_or_star_search(problem, lambda node: 0)
