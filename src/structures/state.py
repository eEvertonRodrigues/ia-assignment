from .tree import Tree
from types import MethodType

class State(Tree):
    def __init__(self, value, children=None, evaluation=None, parent=None, generate=None):
        super().__init__(value, children)
        if evaluation is not None:
            self.evaluation = MethodType(evaluation, self)
        elif parent is not None:
            self.evaluation = MethodType(parent.evaluation.__func__, self)
        if generate is not None:
            self.generate = MethodType(generate, self)
        elif parent is not None:
            self.generate = MethodType(parent.generate.__func__, self)

    def add_child(self, child):
        if not isinstance(child, State):
            child = State(child)
        
        if child.evaluation.__func__ == State.evaluation:
            child.evaluation = MethodType(self.evaluation.__func__, child)
        if child.generate.__func__ == State.generate:
            child.generate = MethodType(self.generate.__func__, child)
        super().add_child(child)

    def evaluation(self):
        return self.value

    def generate(self):
        return self.children