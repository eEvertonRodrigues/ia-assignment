from typing import Generic, TypeVar, List

N = TypeVar('N')

class Tree(Generic[N]):
    def __init__(self, value: N, children: List['Tree[N]'] = None):
        self.value = value
        self.children = children if children is not None else []

    def add_child(self, child: 'Tree[N]'):
        self.children.append(child)

    def is_leaf(self):
        return len(self.children) == 0

    def get_children(self):
        return self.children

    def __repr__(self):
        return f"Tree(value={self.value}, children={self.children})"
  
    def __str__(self):
      lines = [str(self.value)]
      def print_children(node, prefix=""):
          for i, child in enumerate(node.children):
              is_last = i == len(node.children) - 1
              if is_last:
                  lines.append(prefix + "└── " + str(child.value))
                  new_prefix = prefix + "    "
              else:
                  lines.append(prefix + "├── " + str(child.value))
                  new_prefix = prefix + "│   "

              print_children(child, new_prefix)
      print_children(self)
      return "\n".join(lines)