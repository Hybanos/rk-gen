from sympy import Symbol, nsolve, sympify, solve_undetermined_coeffs, solve
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors 

import pretty
from treegen import Node, gen
from phi_t import Factor, Factors, label_tree, generate_factors
from test_method import testall, Config, ODEs
from tableau import Tableau, cache

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

    symbols = list(symbols)
    symbols.sort(key=lambda x: str(x))
    return symbols, equations


def gen_tableaux(symbols, equations, s, config):
    missing = len(symbols) - len(equations)
    step = (config.ubound - config.lbound) / config.l

    # add obious condition: c_i = \sum_j a_ij
    for i in range(s-1):
        eq = []
        for j in range(i+1):
            # equations.append(sympify(f"a_{i+2}{j+1} - c_{i+2}"))
            eq.append(f"a_{i+2}{j+1}")
            sym = f"a_{i+2}{j+1}"
            if sym not in map(str, symbols):
                symbols.append(sympify(sym))
        equations.append(sympify(" + ".join(eq) + f" - c_{i+2}"))
    
    symbols.sort(key=lambda x: str(x))
    print(symbols)

    # remove c_i from variables
    solve_for = []
    for sym in symbols:
        if not str(sym).startswith("c"):
            solve_for.append(sym)

    # solve system
    print(*equations, sep="\n")
    print(*solve_for, sep="\n")
    res = solve(equations, solve_for)
    if s == 2:
        res = list(res.values())
    if s == 3:
        res = res[0]
    print(*zip(solve_for, res), sep="\n", end="\n\n")

    # compute c_i values
    vals = [config.lbound for _ in range(missing)]
    vals_ind = [0 for _ in range(missing)]
    tableaux = []
    for i in range(config.l**missing):
        for j in range(missing):
            if (i % config.l**j) == 0 and i != 0:
                # vals[j] += (config.ubound - config.lbound) / config.l
                vals_ind[j] += 1
                vals[j] = config.lbound + step * vals_ind[j]
                for k in range(j):
                    vals[k] = config.lbound 
                    vals_ind[k] = 0
        
        # print(*map(lambda x: round(x, 3), vals), end=" ")
        if not i % 100:
            print(*vals_ind, *map(lambda x: round(x, 3), vals))

        values = []
        # substitute c_i in solved system 
        # print(res)
        for j, _ in enumerate(res):
            e = res[j]
            for k in range(missing):
                # print(e)
                e = e.subs(sympify(f"c_{k+2}"), vals[k])
            values.append(e)
        
        # add c_i values to output
        for j in range(missing):
            solve_for.append(f"c_{j+2}")
            values.append(vals[j])

        # print(*zip(symbols, values), sep="\n")
        # print("")
        # print(res)

        # print(vals, any(map(lambda x: abs(x) < 0.01), vals))
        try:
            if any(map(lambda x: x == float("nan"), values)) or \
               any(map(lambda x: abs(x) < 0.01, vals)):
                raise Exception("")
            tableau = Tableau(symbols, values, s)
        except Exception as e:
            tableau = None
        tableaux.append(tableau)

    return tableaux

def compare(tableaux, config):
    config.dt = 0.01
    config.startt = 0.0
    config.endt = 10.0
    s = 0
    sols = np.zeros((len(ODEs), len(tableaux)))
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
        plt.show()
        pretty.add_pic(f"errs_{i}.svg")
        plt.clf()

def drift(tableaux, config):
    # config.dt = 0.004
    # config.startt = 0.33
    step = 0.2
    config.dt = 0.01
    config.startt = -0.0
    config.endt = config.startt + step 

    n = 5
    fig, axs = plt.subplots(len(ODEs), n)

    for j in range(n):

        s = 0
        sols = np.zeros((len(ODEs), len(tableaux)))
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
                # axs[i, j].set_xlabel("c_2")
                # axs[i, j].set_ylabel("| relative error |")
        
            elif s >= 3:
                axs[i, j].imshow(x.reshape((config.l, config.l))[::-1,:], extent=[config.lbound, config.ubound, config.lbound, config.ubound], norm=colors.LogNorm())
                if i == 0:
                    axs[i, j].set_title(f"{round(config.startt, 3)}")
                if j == 0:
                    axs[i, j].set_ylabel(ODEs[i][2])
                # axs[i, j].set_xlabel("c_2")
                # axs[i, j].set_ylabel("c_3")
                # axs[j, i].colorbar()
        config.startt += step 
        config.endt +=  step

    # plt.tight_layout()
    # plt.colorbar()
    plt.show()
    plt.clf()

if __name__ == "__main__":
    s = 3
    symbols, equations = generate_system(s)
    pretty.add_system(symbols, equations)

    config = Config(100, -2.0, 2.0)
    # tableaux = gen_tableaux(symbols, equations, s, config)
    tableaux = gen_tableaux(symbols, equations, s, config)
    # tableaux = test(config)
    for t in tableaux:
        pretty.add_tableau(t)
    # compare(tableaux, config)
    pretty.render()
    drift(tableaux, config)
    cache.save()
