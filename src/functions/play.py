import copy
import select
import sys
import termios

from ..structures.table import Table
from ..structures.state import State
from .verify_winner import verify_winner
from .generate_children import generate_children
from .policies import random_tiebreak
from ..models.minimax import Minimax


def clear_pending_input(warning="Digite novamente apos o prompt."):
    if not sys.stdin.isatty():
        return
    try:
        if not select.select([sys.stdin], [], [], 0)[0]:
            return
        termios.tcflush(sys.stdin, termios.TCIFLUSH)
    except (OSError, ValueError, termios.error):
        return
    print(warning)


class Play:
    def play_against_model(self, human_is_x=True, table=None, evaluation=None, generation=None, policy=random_tiebreak, optimization=None):
        state = self._state(table, evaluation, generation)
        ai_x = Minimax(state, policy=policy, optimization=optimization) if not human_is_x else None
        ai_o = Minimax(state, policy=policy, optimization=optimization) if human_is_x else None
        return self._run(state, [(ai_x, True, "X"), (ai_o, False, "O")], human_is_x)

    def play_models(self, table=None, evaluation=None, generation=None, policy=random_tiebreak, optimization=None):
        state = self._state(table, evaluation, generation)
        agents = [(Minimax(state, policy=policy, optimization=optimization), True, "X"),
                  (Minimax(state, policy=policy, optimization=optimization), False, "O")]
        return self._run(state, agents, None)

    def _state(self, table, evaluation, generation):
        return State(table if table is not None else Table(),
                     evaluation=evaluation if evaluation is not None else verify_winner,
                     generate=generation if generation is not None else generate_children)

    def _run(self, state, sides, human_player):
        print("Voce comeca." if human_player else "O agente X comeca.")
        print(state.value)
        turn = 0
        move_number = 0

        while True:
            state.generate()
            if not state.get_children():
                break

            agent, maximizing, label = sides[turn]
            if agent is None:
                move = self._human_move(state, human_player)
            else:
                move = agent.chose(maximizing_player=maximizing)

            if move is None:
                break

            cell = next((i, j) for i in range(3) for j in range(3)
                        if state.value.table[i][j] != move.value.table[i][j])
            move_number += 1
            actor = "Voce" if agent is None else "Agente"
            print(f"Jogada {move_number} - {actor} {label} ({'MAX' if maximizing else 'MIN'}): {cell}")
            print(move.value)

            state = move
            for other, _, _ in sides:
                if other is not None:
                    other.root_state = state
            turn = 1 - turn

        score = state.evaluation()
        if score == 100:
            result = "X vence"
        elif score == -100:
            result = "O vence"
        else:
            result = "Empate"
        print(result)
        return state

    def _human_move(self, state, player):
        clear_pending_input("Jogada ignorada: digite apos o prompt.")
        while True:
            raw = input("Sua jogada (linha coluna, 0-2): ").strip().split()
            if len(raw) != 2:
                print("Informe linha e coluna.")
                continue
            try:
                i, j = int(raw[0]), int(raw[1])
            except ValueError:
                print("Valores invalidos.")
                continue
            if not (0 <= i < 3 and 0 <= j < 3):
                print("Use valores entre 0 e 2.")
                continue

            new_table = copy.deepcopy(state.value)
            if not new_table.set_table((i, j), player=player):
                print("Casa ocupada.")
                continue
            return State(new_table, parent=state)
