import copy

def generate_children(self):
    if self.children:
        return self.children

    score = self.evaluation()
    if score == 100 or score == -100:
        return self.children

    x_count = sum(row.count(1) for row in self.value.table)
    o_count = sum(row.count(-1) for row in self.value.table)
    is_x_turn = (x_count == o_count)

    for i in range(3):
        for j in range(3):
            if self.value.table[i][j] == 0:
                new_table = copy.deepcopy(self.value)
                new_table.set_table((i, j), player=is_x_turn)

                child_state = type(self)(
                    new_table,
                    evaluation=self.evaluation.__func__,
                    generate=self.generate.__func__
                )
                self.add_child(child_state)

    return self.children