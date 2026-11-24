from sympy import sympify, solve, lambdify, diff, polys, algebras, matrices, Matrix, vector, simplify
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors 
from scipy.linalg import solve as lin_solve
from scipy.optimize import least_squares
import time

import pretty
from treegen import Node, gen
from phi_t import Factor, Factors, label_tree, generate_factors
from test_method import testall, Config, ODEs
from tableau import Tableau, cache
import simplifying_assumptions
from solve import generate_system

def solve_for_b(p, s):
    trees = simplifying_assumptions.gen_b_trees(p)

    d = [f"1/{t.fact()}" for t in trees]

    V = [[0 for i in range(s)] for j in range(p)]
    V[0] = [1 for i in range(s)]
    for i in range(p):
        for j in range(s-1):
            V[i][j+1] = sympify(f"c_{j+2}**{i}")

    z = [f"z_{ss+1}" for ss in range(s)]

    d = Matrix(d)
    V = Matrix(V)
    z = Matrix(z)
    # print(d)
    # print(V)
    # print(z)
    # V_i = simplify(V.pinv(method="RD"))
    V_i = V.transpose() @ simplify(matrices.Inverse(V @ V.transpose()))
    V_i = simplify(V_i)
    I_s = np.eye(s)
    print(V_i)

    b = V_i @ d + (I_s - V_i @ V) @ z
    b = simplify(b)
    print(*b, sep="\n")

if __name__ == "__main__":

    p = 3
    s = 3

    # p = 4
    # s = 4

    p = 5
    s = 6

    # p = 6
    # s = 8

    solve_for_b(p, s)

    # symbols, equations = generate_system(p, s)
    # G = polys.groebner(equations)
    # print(*equations, sep="\n")
    # print()
    # print(*G, sep="\n")
    
