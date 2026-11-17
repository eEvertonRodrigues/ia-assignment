def verify_winner(self):
    all_scores = (
        self.value.verify_lines() +
        self.value.verify_columns() +
        self.value.verify_main_diagonal() +
        self.value.verify_anti_diagonal()
    )

    if 100 in all_scores:
        return 100
    if -100 in all_scores:
        return -100

    return sum(all_scores)