from treegen import Node, bfs, gen, from_text

from sympy import Symbol

class Factor:
    def __init__(self, type, nodes):
        self.type = type
        self.nodes = nodes
    
    def __repr__(self):
        return f"{self.type}_({" ".join(map(lambda x: x.label, self.nodes))})"

class Factors(list):
    def __init__(self):
        self.labels = set()
        self.values = {}

    def ready(self):
        for e in self:
            label = e.nodes[0].label
            self.labels.add(label)
    
    def append(self, e):
        super().append(e)
        self.ready()

    def sum(self, s):
        out = ""
        for k in k_permutations(len(self.labels), list(range(s))):
            d = {}
            for k, v in zip(self.labels, k):
                d[k] = v
            
            is_zero = False
            tmp = ""
            for f in self:
                if len(f.nodes) == 2 and d[f.nodes[1].label] > d[f.nodes[0].label]:
                    is_zero = True
                if f.type == "c" and d[f.nodes[0].label] == 0:
                    is_zero = True
                tmp += f"{f.type}_{"".join(map(lambda x: str(d[x.label]+1), f.nodes))}"
                tmp += " * "

            if not is_zero:
                out += tmp
                out = out[:-3] + " + "
        out = out[:-3]
        return out
    
    def __repr__(self):
        return " * ".join([str(f) for f in self])
    
def k_permutations(k, elements):
    # DIRTY EW
    s = set()    
    for perm in permutations(elements):
        # print(perm)
        indices = list(range(k))
        indices.append(len(elements))
        indices.append(0)

        while True:
            # print(indices)
            out = tuple([perm[i] for i in indices[:-2]])
            if out not in s:
                s.add(out)
                yield out
            j = 0
            while indices[j] + 1 == indices[j+1]:
                indices[j] = j
                j = j + 1
            if j >= k:
                break
            indices[j] = indices[j] + 1
        # print("")

def permutations(elements):
    k = len(elements)
    for p in _permutations(k, elements):
        yield p

def _permutations(k, elements):
    if k == 1:
        # print(elements)
        yield elements
        return
    
    for p in _permutations(k-1, elements):
        yield p
    for i in range(k-1):
        if k % 2:
            elements[0], elements[k-1] = elements[k-1], elements[0]
        else:
            elements[i], elements[k-1] = elements[k-1], elements[i]
        for p in _permutations(k-1, elements):
            yield p

def label_tree(t):
    label = 105 # i
    for n in bfs(t):
        if n == t:
            n.label = "i"
        if n.children:
            n.label = chr(label)
            label += 1
    
def generate_factors(t):
    factors = Factors()
    factors.append(Factor("b", [t]))
    for n in bfs(t):
        if n.children:
            for c in n.children:
                if c.children:
                    factors.append(Factor("a", [n, c]))
                else:
                    factors.append(Factor("c", [n]))

    return factors 

if __name__ == "__main__":
    s = 3
    for i in range(1, 4):
        print(f"===== N = {i} =====")
        for t in gen(i):
            # t = from_text("[..[..]]")
            label_tree(t)
            print(t)
            print("fact:", t.fact())
            # t.print_with_labels()
            factors = generate_factors(t)
            # print(factors)
            print("")
            factors.sum(s)
            print("\n")
