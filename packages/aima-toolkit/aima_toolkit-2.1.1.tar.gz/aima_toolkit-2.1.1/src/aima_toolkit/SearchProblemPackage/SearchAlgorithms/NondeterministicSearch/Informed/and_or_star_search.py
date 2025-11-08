import math
from .... import Heuristic, AndNode, OrNode, SearchProblem, SearchStatus, PriorityQueue, nondeterministic_expand


def and_or_star_search(search_problem : SearchProblem, heuristic : Heuristic):
  return _or_star_search(search_problem, OrNode(search_problem.initial_state), path=[], heuristic=heuristic, f_limit=math.inf)

def _or_star_search[S,A](search_problem : SearchProblem[S,A], or_node : OrNode[S,A], path : list[S], heuristic : Heuristic, f_limit : float):
  if search_problem.IS_GOAL(or_node.state):
    return SearchStatus.SUCCESS, {or_node.state : {}}
  elif or_node.state in path:
    return SearchStatus.FAILURE, None

  frontier = PriorityQueue[AndNode](evaluation_func = lambda node : node.f)
  for and_node in nondeterministic_expand(search_problem, or_node, heuristic=heuristic):
    and_node.f = max(or_node.f, and_node.eval_score)
    frontier.push(and_node)

  while len(frontier) > 0:
    best_and_node = frontier.pop()
    if best_and_node.f > f_limit:
      return SearchStatus.CUTOFF, best_and_node.f

    alternative = frontier.best_eval_peak(best_and_node.f)
    status, result = _and_star_search(search_problem, best_and_node, path + [or_node.state], heuristic, alternative)
    if status == SearchStatus.CUTOFF:
      best_and_node.f = result
      frontier.push(best_and_node)
    elif status == SearchStatus.SUCCESS:
      return SearchStatus.SUCCESS, {
        or_node.state: {
          "action" : best_and_node.action,
          "outcomes" : result
        }
      }

  return SearchStatus.FAILURE, None

def _and_star_search[S,A](search_problem : SearchProblem[S,A], and_node : AndNode[S,A], path : list[S], heuristic : Heuristic, f_limit : float):
  plan : dict[S,A] = dict()
  for or_node in and_node.or_nodes:
    status, res = _or_star_search(search_problem, or_node, path, heuristic, f_limit)
    if status == SearchStatus.SUCCESS:
      plan = plan | res
    else:
      return status, res

  return SearchStatus.SUCCESS, plan

__all__ = ['and_or_star_search']
