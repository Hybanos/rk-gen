from sympy import Symbol, nsolve, sympify, solve_undetermined_coeffs
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors 

import pretty
from treegen import Node, gen
from phi_t import Factor, Factors, label_tree, generate_factors
from test_method import abstract_rk

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

    missing = len(symbols) - len(equations)
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

    l = 4
    lbound = -2.0
    ubound = 2.0
    vals = [lbound for _ in range(missing)]
    sols = np.zeros(l**missing)
    for i in range(l**missing):
        for j in range(missing):
            if (i % l**j) == 0 and i != 0:
                vals[j] += (ubound - lbound) / l
                for k in range(j):
                    vals[k] = lbound 
        for j in range(missing):
            equations[-1 - j] = sympify(f"c_{j+2} - {vals[j]}")
        
        print(*map(lambda x: round(x, 3), vals))
        try:
            res = nsolve(equations, symbols, [k+1 for k in range(len(symbols))], maxsteps=10, tol=1e-10)
            pretty.add_tableau(symbols, res, s)
            err = abstract_rk(symbols, res, s)
            sols[i] = abs(err)
        except Exception as e:
            print(e)
            sols[i] = float("nan")

    if missing == 1:
        plt.plot(np.arange(lbound, ubound, (ubound - lbound)/l), sols)
        plt.xlabel("c_2")
        plt.ylabel("| relative error |")
    
    elif missing == 2:
        plt.imshow(sols.reshape([l for _ in vals])[::-1,:], extent=[lbound, ubound, lbound, ubound], norm=colors.LogNorm())
        plt.xlabel("c_2")
        plt.ylabel("c_3")

if __name__ == "__main__":
    s = 3
    symbols, equations = generate_system(s)
    solve(symbols, equations, s)
    pretty.render()
    plt.show()