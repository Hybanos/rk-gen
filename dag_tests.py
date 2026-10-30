from sympy import sympify, solve, lambdify, diff
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

class Node:
    def __init__(self):
        self.value = 0

class Binary(Node):
    def __init__(self, lhs, rhs, op):
        self.lhs = lhs
        self.rhs = rhs
        self.OP = op
        self.count = inc()

    def __repr__(self):
        return f"BIN_{self.count}({self.lhs} {self.OP} {self.rhs})"

class Leaf(Node):
    def __init__(self, symbol):
        self.symbol = symbol
        self.count = inc() 

    def __repr__(self):
        return f"LEAF_{self.count}({self.symbol})"

    def __hash__(self):
        return hash(self.symbol)

class DAG:
    def __init__(self):
        self.layers = {}
        self.leaves = set()
        self.roots = set()
        self.expr_to_node = {}

    def count_operations(self):
        out = {}
        for key, val in self.expr_to_node.items():
            if not isinstance(val, Binary):
                continue
            if val.OP not in out:
                out[val.OP] = 0
            out[val.OP] += 1

        return out

    def add_leaf(self, symbol):
        leaf = Leaf(symbol)
        self.leaves.add(leaf)
        return leaf

    def add_expr(self, exp):
        node = self.expr_to_node.get(exp, None)
        if node is None:
            node = self._add_expr(exp)

        self.roots.add(exp)
        return node

    def _add_expr(self, exp):
        node = self.expr_to_node.get(exp, None)
        if node is None:
            if " + " in exp:
                products = exp.split(" + ")
                products.sort()
                n = len(products) // 2
                lhs = " + ".join(products[:n])
                rhs = " + ".join(products[n:])
                # lhs = " + ".join(products[:-1])
                # rhs = products[-1]
                node = Binary(self._add_expr(lhs), self._add_expr(rhs), OP.ADD)

            elif " * " in exp:
                factors = exp.split(" * ")
                factors.sort()
                n = len(factors) // 2
                lhs = " * ".join(factors[:n])
                rhs = " * ".join(factors[n:])
                # lhs = " * ".join(factors[:-1])
                # rhs = factors[-1]
                node = Binary(self._add_expr(lhs), self._add_expr(rhs), OP.MUL)

            else:
                node = Leaf(exp)
                self.leaves.add(node)

            self.expr_to_node[exp] = node

        return node

    def build_layers(self):
        for exp in self.roots:
            self._build_layers(self.expr_to_node[exp])

    def _build_layers(self, node):
        layer = 0
        if isinstance(node, Binary):
            layer = max(self._build_layers(node.lhs), self._build_layers(node.rhs)) + 1

        if layer not in self.layers:
            self.layers[layer] = set()

        self.layers[layer].add(node)

        return layer

    def eval(self, symbol_to_value):
        for key, value in symbol_to_value.items():
            self.expr_to_node[key].value = value

        for i in range(1, len(self.layers)):
            layer = self.layers[i]
            for node in layer:
                if node.OP == OP.ADD:
                    node.value = node.lhs.value + node.rhs.value
                if node.OP == OP.MUL:
                    node.value = node.lhs.value * node.rhs.value

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

    # print(*eq, sep="\n", end="\n\n")

    operations = {
        OP.ADD: 0,
        OP.MUL: 0,
    }

    dag = DAG()
    for e in eq:
        dag.add_expr(e)
        operations[OP.ADD] += e.count(" + ")
        operations[OP.MUL] += e.count(" * ")

    print(operations)
    print(dag.count_operations())

    dag.build_layers()
    for layer, nodes in dag.layers.items():
        print(layer, nodes)
    print()

    symbols = set()
    for e in eq:
        symbols.update(list(map(str, sympify(e).free_symbols)))
    symbols = dict(zip(symbols, range(1, len(symbols)+1)))
    print(symbols)

    dag.eval(symbol_to_value=symbols)
    for exp in dag.roots:
        print(exp, dag.expr_to_node[exp], dag.expr_to_node[exp].value)
