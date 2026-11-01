from sympy import sympify, solve, lambdify, diff
from collections import OrderedDict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors 
from scipy.linalg import solve as lin_solve
from scipy.optimize import least_squares
import sys

import pretty
from treegen import Node, gen
from phi_t import Factor, Factors, label_tree, generate_factors
from test_method import testall, Config, ODEs
from tableau import Tableau, cache

def inc():
    inc.c += 1
    return inc.c
inc.c = -1

class OP:
    ADD = "ADD"
    MUL = "MUL"

class Binary:
    def __init__(self, lhs, rhs, op):
        self.lhs = lhs
        self.rhs = rhs
        self.OP = op
        self.count = inc()

    def sort(self):
        if self.lhs > self.rhs:
            self.rhs, self.lhs = self.lhs, self.rhs

    def debug(self):
        return f"BIN_{self.count}({self.lhs.debug()} {self.OP} {self.rhs.debug()})"

    def __lt__(self, o):
        return self.__repr__() < o.__repr__()

    def __repr__(self):
        if self.OP == OP.ADD:
            return f"({self.lhs} + {self.rhs})"
        if self.OP == OP.MUL:
            return f"{self.lhs} * {self.rhs}"

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, o):
        return self.__hash__() == o.__hash__()

class Leaf:
    def __init__(self, symbol):
        self.symbol = symbol
        self.count = inc() 

    def sort(self):
        pass

    def debug(self):
        return f"LEAF_{self.count}({self.symbol})"

    def __lt__(self, o):
        return self.__repr__() < o.__repr__()

    def __repr__(self):
        return f"{self.symbol}"

    def __hash__(self):
        return hash(self.__repr__())

    def __eq__(self, o):
        return self.__hash__() == o.__hash__()

class DAG:
    def __init__(self):
        self.layer_hashes = {}
        self.roots = {}
        self.hash_to_node = {}

    def count_operations(self):
        out = {}
        for node in self.hash_to_node.values():
            if not isinstance(node, Binary):
                continue
            if node.OP not in out:
                out[node.OP] = 0
            out[node.OP] += 1

        return out

    def get_or_hash_node(self, node):
        node.sort()
        node = self.hash_to_node.get(hash(node), node)
        self.hash_to_node[hash(node)] = node
        return node

    def add_expr(self, exp, name):
        node = self._add_expr(exp)
        self.roots[name] = node
        return node

    def _add_expr(self, exp):
        if " + " in exp:
            products = exp.split(" + ")
            n = len(products) // 2
            lhs = " + ".join(products[:n])
            rhs = " + ".join(products[n:])
            node = Binary(self._add_expr(lhs), self._add_expr(rhs), OP.ADD)

        elif " * " in exp:
            factors = exp.split(" * ")
            n = len(factors) // 2
            lhs = " * ".join(factors[:n])
            rhs = " * ".join(factors[n:])
            node = Binary(self._add_expr(lhs), self._add_expr(rhs), OP.MUL)

        else:
            node = Leaf(exp)

        return self.get_or_hash_node(node)

    def differentiate_node(self, node, variable: Leaf, name):
        node = self._differentiate_node(node, variable)
        self.roots[name] = node
        return node

    def _differentiate_node(self, node, variable: Leaf):
        out = None
        if isinstance(node, Leaf):
            if node == variable:
                out = Leaf("1")
            else:
                out = Leaf("0")

        else:
            if   node.OP == OP.ADD:
                out = Binary(self._differentiate_node(node.lhs, variable), self._differentiate_node(node.rhs, variable), OP.ADD)
            elif node.OP == OP.MUL:
                lhs = Binary(self._differentiate_node(node.lhs, variable), node.rhs, OP.MUL)
                rhs = Binary(node.lhs, self._differentiate_node(node.rhs, variable), OP.MUL)
                lhs = self.get_or_hash_node(lhs)
                rhs = self.get_or_hash_node(rhs)
                out = Binary(lhs, rhs, OP.ADD)

        return self.get_or_hash_node(out) 

    def build_layers(self):
        self.layer_hashes = {}
        for node in self.roots.values():
            self._build_layers(node)

    def _build_layers(self, node):
        layer = 0
        if isinstance(node, Binary):
            layer = max(self._build_layers(node.lhs), self._build_layers(node.rhs)) + 1

        if layer not in self.layer_hashes:
            self.layer_hashes[layer] = set()

        self.layer_hashes[layer].add(hash(node))

        return layer

    def eval(self, symbol_to_value):
        for key, value in symbol_to_value.items():
            node = self.get_or_hash_node(Leaf(key))
            node.value = value

        for i in range(1, len(self.layer_hashes)):
            layer = self.layer_hashes[i]
            for node_hash in layer:
                node = self.hash_to_node[node_hash]
                if node.OP == OP.ADD:
                    node.value = node.lhs.value + node.rhs.value
                if node.OP == OP.MUL:
                    node.value = node.lhs.value * node.rhs.value

    def apply_opt_passes(self):
        while True:
            last = sum(self.count_operations().values())
            for name, node in self.roots.items():
                self.roots[name] = self.opt_simplify_consts(node)
            self.opt_dead_code_removal()
            if sum(self.count_operations().values()) == last:
                break
            print(self.count_operations())
            

    def opt_simplify_consts(self, node):
        if isinstance(node, Leaf):
            return node

        out = Binary(node.lhs, node.rhs, node.OP)

        out.lhs = self.opt_simplify_consts(out.lhs)
        out.rhs = self.opt_simplify_consts(out.rhs)

        out = self.get_or_hash_node(out)

        if node.OP == OP.ADD and node.lhs == self.get_or_hash_node(Leaf(0)):
            return self.get_or_hash_node(node.rhs)
        if node.OP == OP.ADD and node.rhs == self.get_or_hash_node(Leaf(0)):
            return self.get_or_hash_node(node.lhs)

        if node.OP == OP.MUL and node.lhs == self.get_or_hash_node(Leaf(0)):
            return self.get_or_hash_node(Leaf(0))
        if node.OP == OP.MUL and node.rhs == self.get_or_hash_node(Leaf(0)):
            return self.get_or_hash_node(Leaf(0))

        if node.OP == OP.MUL and node.lhs == self.get_or_hash_node(Leaf(1)):
            return self.get_or_hash_node(node.rhs)
        if node.OP == OP.MUL and node.rhs == self.get_or_hash_node(Leaf(1)):
            return self.get_or_hash_node(node.lhs)

        return out

    def opt_dead_code_removal(self):
        all_nodes = set(self.hash_to_node.values())
        used_nodes = set()

        to_visit = set(self.roots.values())
        while to_visit:
            curr = to_visit.pop()
            used_nodes.add(curr)
            if isinstance(curr, Leaf):
                continue
            to_visit.add(curr.lhs)
            to_visit.add(curr.rhs)

        for node in all_nodes.difference(used_nodes):
            del self.hash_to_node[hash(node)]
            # print(node)

if __name__ == "__main__":
    sys.setrecursionlimit(10000)

    p = 3
    s = 3

    # p = 4
    # s = 4

    # p = 5
    # s = 6

    # p = 6
    # s = 8

    # p = 7
    # s = 10

    eq = []

    for i in range(1, p+1):
        for t in gen(i):
            pretty.add_tree(t)
            label_tree(t)
            factors = generate_factors(t)
            eq.append(factors.sum(s))

    operations = {
        OP.ADD: 0,
        OP.MUL: 0,
    }

    dag = DAG()
    for i, e in enumerate(eq):
        dag.add_expr(e, f"f_{i}")
        operations[OP.ADD] += e.count(" + ")
        operations[OP.MUL] += e.count(" * ")

    print(operations)
    print(dag.count_operations())

    symbols = set()
    symbol_values = {}
    for e in eq:
        symbols.update(list(map(str, sympify(e).free_symbols)))
    symbol_list = list(symbols)
    symbol_list.sort()
    symbol_values = OrderedDict(zip(symbol_list, range(1, len(symbols)+1)))
    for i in range(p-1):
        symbol_values[f"{i}"] = i
    print(symbol_values)

    for sym in symbols:
        i = 0
        for name in [f"f_{i}" for i in range(len(eq))]:
            node = dag.roots[name]
            dag.differentiate_node(node, dag.hash_to_node[hash(Leaf(sym))], f"∂f_{i}/∂{sym}")
            i += 1

    # for node in dag.hash_to_node.values():
    #     print(node)

    # print()
    # dag.build_layers()
    # dag.eval(symbol_to_value=symbol_values)
    # for name, node in dag.roots.items():
    #     print(name, node, node.value)
    # print(dag.count_operations())

    print(dag.count_operations())
    dag.apply_opt_passes()
    print(dag.count_operations())
    # for k, v in dag.hash_to_node.items():
    #     print(k, v, hash(v))

    # print()
    # dag.build_layers()
    # dag.eval(symbol_to_value=symbol_values)
    # for name, node in dag.roots.items():
    #     print(name, node, node.value)
    # print(dag.count_operations())

    # for k in dag.hash_to_node.values():
    #     print(k)

    # print(len(dag.hash_to_node.keys()), len(set(dag.hash_to_node.keys())))