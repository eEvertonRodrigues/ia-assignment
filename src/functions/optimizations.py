def alpha_beta(state, maximizing_player):
    def search(node, flag, alpha, beta):
        node.generate()
        if node.is_leaf():
            return node.evaluation()
        if flag:
            value = float('-inf')
            for child in node.get_children():
                value = max(value, search(child, False, alpha, beta))
                alpha = max(alpha, value)
                if beta <= alpha:
                    break
            return value
        value = float('inf')
        for child in node.get_children():
            value = min(value, search(child, True, alpha, beta))
            beta = min(beta, value)
            if beta <= alpha:
                break
        return value
    return search(state, maximizing_player, float('-inf'), float('inf'))
