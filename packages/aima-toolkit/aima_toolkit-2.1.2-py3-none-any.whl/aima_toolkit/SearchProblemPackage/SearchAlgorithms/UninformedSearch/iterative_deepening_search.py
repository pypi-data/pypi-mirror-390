from itertools import count
from .depth_limited_search import depth_limited_search
from ...searchproblem import SearchProblem, SearchStatus

def iterative_deepening_search(problem : SearchProblem):
  for depth in count(start=0):
    search_status, result = depth_limited_search(problem, depth)
    if search_status != SearchStatus.CUTOFF:
      return search_status, result