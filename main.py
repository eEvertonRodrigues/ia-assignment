import copy
import time

from src.functions.generate_children import generate_children as gc
from src.functions.optimizations import alpha_beta
from src.functions.play import Play, clear_pending_input
from src.functions.policies import random_tiebreak
from src.functions.verify_winner import verify_winner as vw
from src.models.minimax import Minimax as mm
from src.structures.state import State as st
from src.structures.table import Table as tb


def demo():
    state = st(tb(), evaluation=vw, generate=gc)
    minimax = mm(state)
    print("Estado inicial:")
    print(state)

    state.generate()

    best_state = minimax.chose(maximizing_player=True)
    print("\nMelhor jogada escolhida pelo Minimax:")
    print(best_state)
    print(f"Pontuação da avaliação: {minimax.run(maximizing_player=True)}")


def _prompt(text):
    clear_pending_input()
    return input(text)


def _ask_yes_no(text):
    return _prompt(f"{text} (s/n): ").strip().lower().startswith("s")


def _ask_table():
    if not _ask_yes_no("Usar tabuleiro inicial customizado?"):
        return None

    while True:
        raw = _prompt("Jogadas iniciais (ex.: 0 0 X; 1 1 O | Enter para vazio): ").replace("'", "").replace('"', "").strip()
        table = tb()
        error = None
        if not raw:
            return table

        for group in raw.split(";"):
            parts = group.split()
            if not parts:
                continue
            if len(parts) != 3:
                error = "Use grupos 'linha coluna letra' separados por ';'."
                break
            try:
                i, j = int(parts[0]), int(parts[1])
            except ValueError:
                error = "Linha e coluna devem ser numeros."
                break
            if not (0 <= i < 3 and 0 <= j < 3):
                error = "Use linha e coluna entre 0 e 2."
                break
            letter = parts[2].upper()
            if letter not in ("X", "O"):
                error = "A letra deve ser X ou O."
                break
            if not table.set_table((i, j), player=letter == "X"):
                error = "Casa repetida."
                break

        if error is None:
            x_count = sum(row.count(1) for row in table.table)
            o_count = sum(row.count(-1) for row in table.table)
            if x_count not in (o_count, o_count + 1):
                error = "Contagem invalida: X deve ter o mesmo numero de O ou um a mais."
            elif abs(st(table, evaluation=vw).evaluation()) >= 100:
                error = "O tabuleiro ja comeca com um vencedor."

        if error is not None:
            print(error)
            continue
        return table


def _configure():
    while True:
        mode = _prompt("1) contra o modelo\n2) modelos brigando\n3) demo deterministica\n").strip()
        if mode in ("1", "2", "3"):
            break
        print("Opcao invalida.")

    if mode == "3":
        return mode, None, None

    human_is_x = _ask_yes_no("Voce joga como X?") if mode == "1" else None
    optimization = alpha_beta if _ask_yes_no("Usar poda alpha-beta?") else None

    while True:
        policy_choice = _prompt("Politica: 1) random 2) deterministica\n").strip()
        if policy_choice in ("1", "2"):
            break
        print("Opcao invalida.")
    policy = random_tiebreak if policy_choice == "1" else None

    table = _ask_table()
    return mode, human_is_x, {"table": table, "policy": policy, "optimization": optimization}


def main():
    play = Play()
    while True:
        mode, human_is_x, config = _configure()
        while True:
            if mode == "3":
                demo()
            else:
                kwargs = dict(config)
                if kwargs["table"] is not None:
                    kwargs["table"] = copy.deepcopy(kwargs["table"])

                start = time.perf_counter()
                if mode == "1":
                    play.play_against_model(human_is_x=human_is_x, **kwargs)
                else:
                    play.play_models(**kwargs)
                elapsed = time.perf_counter() - start

                label = "Tempo total (inclui jogadas humanas)" if mode == "1" else "Tempo"
                print(f"{label}: {elapsed:.2f}s")

            if not _ask_yes_no("Jogar novamente?"):
                break
        if not _ask_yes_no("Configurar outra partida?"):
            break


if __name__ == "__main__":
    main()