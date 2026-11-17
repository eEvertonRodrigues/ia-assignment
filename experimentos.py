import copy
import json
import platform
import time
import types

from src.functions.generate_children import generate_children
from src.functions.optimizations import alpha_beta
from src.functions.policies import random_tiebreak
from src.functions.verify_winner import verify_winner
from src.models.minimax import Minimax
from src.structures.state import State
from src.structures.table import Table

NODE_COUNTER = {"nodes": 0}


def utility(self):
    score = verify_winner(types.SimpleNamespace(value=self.value))
    if score == 100:
        return 1
    if score == -100:
        return -1
    return 0


def winner(table):
    score = verify_winner(types.SimpleNamespace(value=table))
    if score == 100:
        return 1
    if score == -100:
        return -1
    return 0


def make_generation(reverse=False):
    def generate(self):
        NODE_COUNTER["nodes"] += 1
        if abs(utility(self)) == 1:
            return self.children
        before = len(self.children)
        generate_children(self)
        if reverse and len(self.children) > before:
            self.children.reverse()
        return self.children
    return generate


def new_state(table=None, reverse=False):
    return State(copy.deepcopy(table) if table is not None else Table(),
                 evaluation=utility, generate=make_generation(reverse))


def table_from(snapshot):
    table = Table()
    table.table = [list(row) for row in snapshot]
    return table


def snapshot(table):
    return [list(row) for row in table.table]


def cell_of(before, after):
    for i in range(3):
        for j in range(3):
            if before.table[i][j] != after.table[i][j]:
                return [i, j]
    return None


def decide(state, maximizing, optimization, random_policy=False):
    state.generate()

    selected = {}

    def policy(candidates, maximizing_player):
        if random_policy:
            chosen = random_tiebreak(candidates, maximizing_player)
        else:
            best = max(value for _, value in candidates) if maximizing_player else min(value for _, value in candidates)
            chosen = next(child for child, value in candidates if value == best)
        selected["move"] = chosen
        selected["value"] = next(value for child, value in candidates if child is chosen)
        return chosen

    agent = Minimax(state, policy=policy, optimization=optimization)
    NODE_COUNTER["nodes"] = 0
    start = time.perf_counter()
    move = agent.chose(maximizing_player=maximizing)
    elapsed = time.perf_counter() - start

    return move, {
        "move": cell_of(state.value, move.value) if move is not None else None,
        "value": selected.get("value"),
        "nodes": NODE_COUNTER["nodes"],
        "time_ms": round(elapsed * 1000, 3),
    }


def algorithm_name(optimization):
    return "Alfa-beta" if optimization is not None else "Minimax"


def run_match(x_optimization, o_optimization, human_side=None, human_moves=None):
    state = new_state()
    human = iter(human_moves or [])
    turn = 1
    sequence = []
    decisions = []
    states = []

    while True:
        state.generate()
        if not state.get_children():
            break

        maximizing = turn == 1
        player = "X" if maximizing else "O"
        states.append({"table": snapshot(state.value), "player": player})

        if human_side == turn:
            i, j = next(human)
            table = copy.deepcopy(state.value)
            if not table.set_table((i, j), player=maximizing):
                raise ValueError(f"jogada invalida: {(i, j)}")
            move = State(table, parent=state)
            cell = [i, j]
            sequence.append({"player": player, "cell": cell, "algorithm": "Humano"})
        else:
            optimization = x_optimization if maximizing else o_optimization
            move, info = decide(state, maximizing, optimization)
            cell = info["move"]
            info = {"algorithm": algorithm_name(optimization), "player": player,
                    "move_number": len(sequence) + 1, **info}
            decisions.append(info)
            sequence.append({"player": player, "cell": cell, "algorithm": info["algorithm"]})

        state = move
        turn = -turn

    result = winner(state.value)
    return {
        "x": algorithm_name(x_optimization),
        "o": algorithm_name(o_optimization),
        "human": "X" if human_side == 1 else "O" if human_side == -1 else None,
        "sequence": sequence,
        "result": {1: "X vence", -1: "O vence", 0: "Empate"}[result],
        "decisions": decisions,
        "states": states,
    }


def pick_states(matches, limit=5):
    seen = set()
    picked = []
    for match in matches:
        for index, state in enumerate(match["states"]):
            if index < 2:
                continue
            key = (tuple(tuple(row) for row in state["table"]), state["player"])
            if key in seen:
                continue
            seen.add(key)
            picked.append({"id": f"E{len(picked) + 1}", **state})
            if len(picked) == limit:
                return picked
    return picked


def measure(table, player, optimization, repetitions=10, reverse=False):
    maximizing = player == "X"
    times = []
    last = None
    for _ in range(repetitions):
        state = new_state(table, reverse=reverse)
        _, info = decide(state, maximizing, optimization)
        times.append(info["time_ms"])
        last = info
    return {
        "algorithm": algorithm_name(optimization),
        "move": last["move"],
        "value": last["value"],
        "nodes": last["nodes"],
        "time_ms": round(sum(times) / len(times), 3),
    }


def main():
    matches = [
        run_match(None, None, human_side=-1, human_moves=[(1, 1), (2, 2), (1, 0), (2, 0), (2, 1)]),
        run_match(alpha_beta, None, human_side=-1, human_moves=[(1, 1), (2, 2), (1, 0), (2, 0), (2, 1)]),
        run_match(None, None, human_side=1, human_moves=[(0, 0), (0, 1), (1, 2), (2, 0), (2, 2)]),
        run_match(None, alpha_beta, human_side=1, human_moves=[(0, 0), (0, 1), (1, 2), (2, 0), (2, 2)]),
    ]

    duels = [
        run_match(alpha_beta, None),
        run_match(None, alpha_beta),
    ]

    states = pick_states(matches + duels)
    comparison = []
    for state in states:
        table = table_from(state["table"])
        plain = measure(table, state["player"], None)
        pruned = measure(table, state["player"], alpha_beta)
        reduction = (plain["nodes"] - pruned["nodes"]) / plain["nodes"] * 100 if plain["nodes"] else 0
        comparison.append({
            "id": state["id"], "table": state["table"], "player": state["player"],
            "minimax": plain, "alfa_beta": pruned, "reduction": round(reduction, 2),
        })

    inversion_state = comparison[0]
    inversion_table = table_from(inversion_state["table"])
    inversion = {
        "id": inversion_state["id"],
        "table": inversion_state["table"],
        "player": inversion_state["player"],
        "normal": measure(inversion_table, inversion_state["player"], alpha_beta),
        "reversed": measure(inversion_table, inversion_state["player"], alpha_beta, reverse=True),
    }

    print(json.dumps({
        "ambiente": {"python": platform.python_version()},
        "partidas": matches,
        "duelos": duels,
        "comparacao": comparison,
        "inversao": inversion,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
