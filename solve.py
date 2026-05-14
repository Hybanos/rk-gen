from sympy import Symbol, nsolve, sympify, solve_undetermined_coeffs
import numpy as np

import pretty
from treegen import Node, gen
from phi_t import Factor, Factors, label_tree, generate_factors

def generate_system(s):
    equations = []
    symbols = set()
    for i in range(1, s+1):
        for t in gen(i):
            pretty.add_tree(t)
            label_tree(t)
            factors = generate_factors(t)
            lval = factors.sum(s) + f" - 1/{t.fact()}"
            e = sympify(lval)
            equations.append(e)
            symbols.update(e.free_symbols)

    return list(symbols), equations

def solve(symbols, equations, s):
    print(len(equations), len(symbols))
    print(*equations, sep="\n")
    print(*symbols, sep="\n")

    # equations.append(sympify("a_21 - c_2"))
    # # equations.append(sympify("a_31 + a_32 - c_3"))
    # symbols.append("a_21")
    # # symbols.append("a_31")

    # pretty.add_system(symbols, equations)

    # equations.append(None)
    # # equations.append(None)

    # for i in range(0, 10 + 1):
    #     # for j in range(-10, 10):
    #         equations[-1] = sympify(f"c_{2} - {i / 10}")
    #         # equations[-1] = sympify(f"c_{3} - {j / 10}")

    #         try:
    #             res = nsolve(equations, symbols, [k+1 for k in range(len(symbols))])
    #             pretty.add_tableau(symbols, res, s)
    #         except Exception as e:
    #             print(i, i, e)

    missing = len(symbols) - len(equations)
    vals = [0 for _ in range(missing)]

    pretty.add_system(symbols, equations)

    for i in range(missing):
        eq = []
        for j in range(i+1):
            # equations.append(sympify(f"a_{i+2}{j+1} - c_{i+2}"))
            eq.append(f"a_{i+2}{j+1}")
            if f"a_{i+2}{j+1}" not in map(str, symbols):
                symbols.append(f"a_{i+2}{j+1}")
        equations.append(" + ".join(eq) + f" - c_{i+2}")

    for i in range(missing):
        equations.append(None)

    l = 20
    for i in range(l**missing):
        for j in range(missing):
            if (i % l**j) == 0:
                vals[j] += 1 / l
                for k in range(j):
                    vals[k] = 0
        
        # print(*map(lambda x: round(x, 2), vals))
        
        for j in range(missing):
            equations[-1 - j] = sympify(f"c_{j+2} - {vals[j]}")
        
        # print(equations, symbols, sep="\n")
        try:
            res = nsolve(equations, symbols, [k+1 for k in range(len(symbols))])
            pretty.add_tableau(symbols, res, s)
        except Exception as e:
            print(*vals, e)

if __name__ == "__main__":
    s = 3
    symbols, equations = generate_system(s)
    solve(symbols, equations, s)
    pretty.render()