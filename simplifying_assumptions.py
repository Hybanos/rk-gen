from sympy import sympify, solve, lambdify, diff
from collections import OrderedDict
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors 
from scipy.linalg import solve as lin_solve
from scipy.optimize import least_squares
import sys
import random
import graphviz

import pretty
from treegen import Node, gen, bfs
from phi_t import Factor, Factors, label_tree, generate_factors
from test_method import testall, Config, ODEs
from tableau import Tableau, cache

def gen_b_trees(p):
    trees = [Node()]
    root = Node()
    for i in range(1, p):
        root.children.append(Node()) 
        trees.append(root.copy())
    return trees

def match_c_assumption(t1, t2):
    base_facts = [t1.fact(), t2.fact()]
    base_facts.sort()
    ratio = base_facts[1] / base_facts[0]
    g1 = bfs(t1)
    g2 = bfs(t2)
    for i in range(t1.order()):
        n1 = next(g1)
        n2 = next(g2)
        facts = [n1.fact(), n2.fact()]
        facts.sort()
        if facts[1] / facts[0] not in (1, ratio):
            return False

    print(t1, t2, ratio)
    return True

def gen_c_trees(p):
    trees = []

    n_total = 0
    for i in range(1, p+1):
        current_order_trees = []
        for t in gen(i):
            tt = t.copy()
            label_tree(tt)
            current_order_trees.append(tt)
        filtered_out_mask = [0 for _ in range(len(current_order_trees))]
        n_total += len(current_order_trees)

        # current_order_trees = current_order_trees[::-1]

        for i in range(len(current_order_trees)):
            if filtered_out_mask[i]:
                continue
            for j in range(i+1, len(current_order_trees)):
                t1 = current_order_trees[i]
                t2 = current_order_trees[j]
                if match_c_assumption(t1, t2):
                    # TODO : compute which tree is the best to remove ?
                    filtered_out_mask[j] = 1

        for i in range(len(current_order_trees)):
            print(current_order_trees[i], filtered_out_mask[i])
            if not filtered_out_mask[i]:
                trees.append(current_order_trees[i])
        print(f"ratio : {filtered_out_mask.count(1)}/{len(filtered_out_mask)} - {filtered_out_mask.count(1) / len(filtered_out_mask)}")
        print(f"total : {len(trees)}/{n_total} - {len(trees) / n_total}")

    return trees

def gen_c_conditions(p, s):
    equations = []

    for k in range(2, s):
        for i in range(2, s+1):
            lhs = []
            rhs = ""
            for j in range(2, i):
                lhs.append(f"a_{i}{j} * " + " * ".join([f"c_{j}" for _ in range(k-1)]))
            rhs += f"1/{k} * " + " * ".join([f"c_{i}" for _ in range(k)])
            equations.append(" + ".join(lhs) + " - " + rhs)

    return equations

if __name__ == "__main__":

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

    # trees = gen_c_trees(p)
    print(*gen_c_conditions(p, s), sep="\n")
    # print(*list(gen(5)), sep="\n")

