class Table:
    def __init__(self):
        self.table = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]

    def set_table(self, coordinates, player=True):
        x, y = coordinates
        if self.table[x][y] != 0:
            return False

        self.table[x][y] = 1 if player else -1
        return True

    def _evaluate_line(self, line):
        x_count = line.count(1)
        o_count = line.count(-1)

        if x_count > 0 and o_count > 0:
            return 0  # Linha bloqueada, ninguém ganha aqui

        if x_count == 3:
            return 100
        elif o_count == 3:
            return -100
        elif x_count == 2:
            return 10
        elif o_count == 2:
            return -10
        elif x_count == 1:
            return 5
        elif o_count == 1:
            return -5

        return 0

    def verify_lines(self):
        scores = []
        for i in range(3):
            scores.append(self._evaluate_line(self.table[i]))
        return scores

    def verify_columns(self):
        scores = []
        for i in range(3):
            col = [self.table[0][i], self.table[1][i], self.table[2][i]]
            scores.append(self._evaluate_line(col))
        return scores

    def verify_main_diagonal(self):
        diag = [self.table[i][i] for i in range(3)]
        return [self._evaluate_line(diag)]

    def verify_anti_diagonal(self):
        anti_diag = [self.table[i][2 - i] for i in range(3)]
        return [self._evaluate_line(anti_diag)]

    def __str__(self):
        symbols = {1: "X", -1: "O", 0: " "}
        formatted_rows = ["    0   1   2"]

        for idx, row in enumerate(self.table):
            cells = [symbols[value] for value in row]
            formatted_rows.append(f"{idx} | " + " | ".join(cells) + " |")
            
            if idx < 2:
                formatted_rows.append("  +---+---+---+")

        return "\n".join(formatted_rows)