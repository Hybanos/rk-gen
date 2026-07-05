
class Node:
    def __init__(self):
        self.children: list = []
        self.label = ""
        self.value = 0
    
    def __repr__(self):
        if self.children:
            return f"[{"".join([str(s) for s in self.children])}]"
        else:
            return f"."
    
    def __repr_labels__(self):
        if self.children:
            return f"[{self.label}{"".join([s.__repr_labels__() for s in self.children])}]"
        else:
            return f"{self.label}"
    
    def _fact(self):
        return sum([c._fact() for c in self.children]) + 1

    def fact(self):
        f = 1
        for n in bfs(self):
            f *= n._fact()
        return f

    def order(self):
        return len(list(bfs(self)))

    def id(self):
        a = self.children
        a.sort()
        b = [b.id() for b in a]
        return f"({self.fact()}:{",".join(b)})"
    
    def print(self):
        print(self)
    
    def print_with_labels(self):
        print(self.__repr_labels__())
    
    def __lt__(self, other):
        return self.id() < other.id()
    
    def __hash__(self):
        return hash(self.id())

def from_text(text):
    if not len(text):
        return
    cursor = 0
    stack = []
    while cursor != len(text):
        c = text[cursor]
        if c == ".":
            if not stack:
                stack.append(Node())
            else:
                stack[-1].children.append(Node())
        elif c == "[":
            tmp = Node()
            if not stack:
                stack.append(tmp)
            else:
                stack[-1].children.append(tmp)
            stack.append(tmp)
        elif c == "]":
            stack.pop(-1)
        else:
            raise ValueError("invalid char")

        cursor += 1
    
    if len(stack) != 1:
        raise ValueError("Invalid string")
    return stack[0]

def bfs(root):
    to_visit = [root]
    while to_visit:
        node = to_visit.pop(0)
        yield node
        to_visit.extend(node.children)

def gen(nodes):
    s = set()

    root = Node()
    for t in _gen(root, nodes-1):
        if t not in s:
            yield t
            s.add(t)

def _gen(root, nodes_left):
    if nodes_left == 0:
        yield root
        return

    for node in bfs(root):
        add = Node()
        node.children.append(add)
        for t in _gen(root, nodes_left-1):
            yield t
        node.children.remove(add)

if __name__ == "__main__":
    a = range(1, 11)
    # # a = [4]
    for i in a:
        print(f"===== N = {i} =====")
        n = 0
        for t in gen(i):
            print(t)
            print(t.fact())
            n += 1
        print(f"Size = {n}\n")