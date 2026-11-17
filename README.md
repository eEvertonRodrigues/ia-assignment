# Jogo da Velha com Minimax

Projeto didático de jogo da velha (3x3) com busca Minimax, geração de estados, heurística, política de desempate e opção de poda alpha-beta.

## Executar

```bash
python3 main.py
```

O menu oferece: `1)` humano contra o modelo, `2)` dois modelos brigando, `3)` demo determinística. Antes da partida você escolhe lado humano, alpha-beta, política (random/determinística) e tabuleiro inicial. Ao final pode repetir a mesma configuração ou configurar outra.

## Arquitetura

| Camada | Arquivos | Papel |
| --- | --- | --- |
| Estruturas | `src/structures/` | Tabuleiro, árvore genérica e estado do jogo |
| Regras do jogo | `src/functions/verify_winner.py`, `src/functions/generate_children.py` | Avaliar e expandir estados |
| Busca | `src/models/minimax.py` | Escolher a melhor jogada |
| Extensões | `src/functions/policies.py`, `src/functions/optimizations.py` | Desempate e poda alpha-beta |
| Partida | `src/functions/play.py` | Alternar turnos e executar jogadas |
| Interface | `main.py` | Menu, cronômetro e configuração |
| Exemplo antigo | `src/models/sample_minimax.py` | Demonstração isolada de Minimax, não usada pelo jogo |

## Arquivos

| Arquivo | O que tem |
| --- | --- |
| `main.py` | `main()`, menu, leitura/validação do tabuleiro inicial, `demo()` e cronômetro |
| `src/structures/table.py` | `Table`: matriz 3x3, `set_table`, verificação de linhas/colunas/diagonais e `__str__` |
| `src/structures/tree.py` | `Tree`: `value`, `children`, `add_child`, `is_leaf`, `get_children` e `__str__` |
| `src/structures/state.py` | `State`: uma `Tree` cujo `value` é `Table`, com `evaluation` e `generate` injetadas |
| `src/functions/verify_winner.py` | Heurística: soma linhas/colunas/diagonais; vitória vale `+100`/`-100` |
| `src/functions/generate_children.py` | Cria um filho por casa vazia, com `deepcopy` do tabuleiro e turno inferido pela contagem de peças |
| `src/functions/policies.py` | `random_tiebreak`: escolhe ao acaso entre os candidatos de melhor valor |
| `src/functions/optimizations.py` | `alpha_beta`: mesma busca com poda por α/β |
| `src/functions/play.py` | Classe `Play` (`play_against_model` / `play_models`) e `clear_pending_input` |
| `src/models/minimax.py` | Classe `Minimax` com `policy` e `optimization` opcionais |

## Estruturas principais

| Estrutura | Campos / métodos importantes | Por que existe assim |
| --- | --- | --- |
| `Table` | `table`, `set_table(coord, player=True)`, `verify_lines`, `verify_columns`, diagonais | Separa o tabuleiro das regras de busca; `True` grava X (`1`) e `False` grava O (`-1`) |
| `Tree` | `value`, `children`, `add_child`, `is_leaf()` | Árvore genérica reutilizável; `is_leaf()` significa "sem filhos" |
| `State` | herda `Tree`, recebe `evaluation` e `generate` ou um `parent` | O estado sabe avaliar e se expandir, mas não conhece o Minimax |
| `Minimax` | `root_state`, `policy`, `optimization`, `run`, `chose`, `_minimax` | Busca isolada: trocar política ou poda não exige alterar a recursão |
| `Play` | `play_against_model`, `play_models`, helpers privados | Dono da partida; recebe regras por parâmetro e não contém menu |

## Decisões de design

- **Injeção de dependência:** `State` recebe `evaluation`/`generate`; `Minimax` recebe `policy`/`optimization`; `Play` recebe `table`, `evaluation`, `generation`, `policy` e `optimization`. Assim cada parte pode ser trocada sem editar o núcleo.
- **`MethodType`:** as funções injetadas viram métodos do `State`. Por isso se passa `self.generate.__func__` em vez de `self.generate` (já ligado), que causaria argumento duplo.
- **Geração idempotente:** `generate_children` retorna os filhos existentes, para em vitória e nunca altera o tabuleiro do pai — cada filho usa uma cópia.
- **Turno pela contagem:** `x_count == o_count` define que é a vez de X; isso evita guardar um flag de turno separado do tabuleiro.
- **Fim de jogo:** como `Tree.is_leaf()` só verifica `children`, o loop de `Play` chama `state.generate()` antes de decidir se a partida acabou.
- **Jogada humana:** usa `deepcopy` + `set_table` + `State(parent=state)`, sem procurar o filho correspondente na lista gerada. `parent` reaplica as mesmas funções injetadas.
- **Desempate:** `random_tiebreak` sorteia entre os melhores valores, variando as aberturas sem abrir mão da jogada ótima. `policy=None` usa o laço determinístico do próprio `Minimax`.
- **Alpha-beta:** calcula cada filho da raiz com janela completa, mantendo valores exatos para o desempate; a poda acontece na recursão interna.
- **Separação de interface:** o menu vive em `main.py`. Jogada digitada antes do prompt é descartada por `clear_pending_input`, evitando a impressão de que o modelo jogou duas vezes seguidas.

## Fluxo de uma jogada

1. `main.py` lê as opções e chama `Play.play_against_model(...)` ou `Play.play_models(...)`.
2. `Play` monta o `State` inicial com `Table` e as funções escolhidas.
3. O loop gera os filhos; se não houver filhos, a partida terminou.
4. O agente chama `Minimax.chose(...)`; o humano informa `linha coluna`, que vira um novo `State`.
5. A jogada é impressa, o `root_state` dos agentes é atualizado e o turno alterna.

## Como estender

Basta escrever uma função com o formato esperado e passá-la como parâmetro de `Play`:

| Extensão | Assinatura | Parâmetro |
| --- | --- | --- |
| Nova heurística | `fn(state)` | `evaluation` |
| Nova geração | `fn(state)` | `generation` |
| Nova política | `fn(candidates, maximizing_player)` | `policy` |
| Nova poda | `fn(state, maximizing_player)` | `optimization` |
