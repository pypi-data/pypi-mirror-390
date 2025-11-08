from .... import SearchProblem, SearchStatus

def nondeterministic_depth_first_search[S,A](problem : SearchProblem[S,A]) -> SearchStatus | dict:
  return _or_search(problem, problem.initial_state, [])

def _or_search[S,A](problem : SearchProblem[S,A], state : S, path : list) -> SearchStatus | dict:
  if problem.IS_GOAL(state):
    return {
      state: {}
    }
  elif state in path:
    return SearchStatus.FAILURE

  for action in problem.ACTIONS(state):
    plan = _and_search(
      problem,
      set(
        problem.RESULTS(
          state, action
        )
      ),
      [state] + path
    )

    if plan != SearchStatus.FAILURE:
      return {
        state : {
          "action" : action,
          "outcomes" : plan
        }
      }

  return SearchStatus.FAILURE

def _and_search[S,A](problem : SearchProblem[S,A], states : set[S], path : list[S]) -> SearchStatus | dict:
  plan = dict()
  for state in states:
    plan_i = _or_search(problem, state, path)
    if plan_i == SearchStatus.FAILURE:
      return SearchStatus.FAILURE
    else:
      plan = plan | plan_i

  return plan

__all__ = ['nondeterministic_depth_first_search']