from ..structures.state import State

class Minimax:
    def __init__(self, root_state, policy=None, optimization=None):
        self.root_state = root_state
        self.policy = policy
        self.optimization = optimization

    def run(self, maximizing_player=True):
        return self._minimax(self.root_state, maximizing_player)

    def chose(self, maximizing_player=True):
        candidates = []
        for child in self.root_state.get_children():
            candidates.append((child, self._minimax(child, not maximizing_player)))

        if not candidates:
            return None
        if self.policy is not None:
            return self.policy(candidates, maximizing_player)

        best_value = float('-inf') if maximizing_player else float('inf')
        best_move = None
        for child, value in candidates:
            if (maximizing_player and value > best_value) or (not maximizing_player and value < best_value):
                best_value = value
                best_move = child

        return best_move

    def _minimax(self, state, maximizing_player):
        if self.optimization is not None:
            return self.optimization(state, maximizing_player)

        state.generate()
        
        if state.is_leaf():
            return state.evaluation()

        if maximizing_player:
            max_eval = float('-inf')
            for child in state.get_children():
                eval = self._minimax(child, False)
                max_eval = max(max_eval, eval)
            return max_eval
        else:
            min_eval = float('inf')
            for child in state.get_children():
                eval = self._minimax(child, True)
                min_eval = min(min_eval, eval)
            return min_eval