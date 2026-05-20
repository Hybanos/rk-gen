from sympy import Symbol, nsolve, sympify, solve_undetermined_coeffs
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors 

import pretty
from treegen import Node, gen
from phi_t import Factor, Factors, label_tree, generate_factors
from test_method import testall 
from tableau import Tableau, cache

class Config:
    def __init__(self, l, lbound, ubound):
        self.l = l
        self.lbound = lbound
        self.ubound = ubound

        self.startt = 0
        self.endt = 1
        self.dt = 0.001

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

def gen_tableaux(symbols, equations, s, config):
    missing = len(symbols) - len(equations)

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

    vals = [config.lbound for _ in range(missing)]
    # sols = np.zeros((3, l**missing))
    tableaux = []
    for i in range(config.l**missing):
        for j in range(missing):
            if (i % config.l**j) == 0 and i != 0:
                vals[j] += (config.ubound - config.lbound) / config.l
                for k in range(j):
                    vals[k] = config.lbound 
        for j in range(missing):
            equations[-1 - j] = sympify(f"c_{j+2} - {vals[j]}")
        
        print(*map(lambda x: round(x, 3), vals), end=" ")
        tableau = cache.get(vals)
        # what the fuck is sympy doing here hello ?
        for k in range(1):
            if tableau is not None:
                break
            try:
                res = nsolve(equations, symbols, [k+1 for k in range(len(symbols))], maxsteps=100, tol=1e-30)
                tableau = Tableau(symbols, res, s)
                cache.cache(tableau)
            except Exception as e:
                print(e)
        tableaux.append(tableau)

    return tableaux

def compare(tableaux, config):
    s = 0
    sols = np.zeros((3, len(tableaux)))
    for i, t in enumerate(tableaux):
        if t is not None:
            s = t.s
            err = testall(t, config)
            sols.T[i] = np.abs(err)
        else:
            sols.T[i] = float("nan")

    for i, x in enumerate(sols):
        if s == 2:
            plt.plot(np.arange(config.lbound, config.ubound, (config.ubound - config.lbound)/config.l), x)
            plt.yscale("log")
            plt.xlabel("c_2")
            plt.ylabel("| relative error |")
    
        elif s >= 3:
            plt.imshow(x.reshape((config.l, config.l))[::-1,:], extent=[config.lbound, config.ubound, config.lbound, config.ubound], norm=colors.LogNorm())
            plt.xlabel("c_2")
            plt.ylabel("c_3")
            plt.colorbar()

        plt.tight_layout()
        plt.savefig(f"errs_{i}.svg")
        pretty.add_pic(f"errs_{i}.svg")
        plt.clf()

def drift(tableaux, config):
    config.startt = 0
    config.endt = 0.1

    n = 5
    fig, axs = plt.subplots(3, n)

    for j in range(n):
        config.startt += 0.2
        config.endt += 0.2

        s = 0
        sols = np.zeros((3, len(tableaux)))
        for i, t in enumerate(tableaux):
            if t is not None:
                s = t.s
                err = testall(t, config)
                sols.T[i] = np.abs(err)
            else:
                sols.T[i] = float("nan")

        for i, x in enumerate(sols):
            if s == 2:
                axs[i, j].plot(np.arange(config.lbound, config.ubound, (config.ubound - config.lbound)/config.l), x)
                axs[i, j].set_yscale("log")
                axs[i, j].set_xlabel("c_2")
                axs[i, j].set_ylabel("| relative error |")
        
            elif s >= 3:
                axs[i, j].imshow(x.reshape((config.l, config.l))[::-1,:], extent=[config.lbound, config.ubound, config.lbound, config.ubound], norm=colors.LogNorm())
                # axs[i, j].set_xlabel("c_2")
                # axs[i, j].set_ylabel("c_3")
                # axs[j, i].colorbar()

    # plt.tight_layout()
    # plt.colorbar()
    plt.show()

if __name__ == "__main__":
    s = 4
    symbols, equations = generate_system(s)
    pretty.add_system(symbols, equations)

    config = Config(20, -2.0, 2.0)
    tableaux = gen_tableaux(symbols, equations, s, config)
    for t in tableaux:
        pretty.add_tableau(t)
    # compare(tableaux, config)
    pretty.render()
    drift(tableaux, config)
    cache.save()