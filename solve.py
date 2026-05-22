from sympy import Symbol, nsolve, sympify, solve_undetermined_coeffs, solve
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

    symbols = list(symbols)
    symbols.sort(key=lambda x: str(x))
    return symbols, equations


def test2(symbols, equations, s, config):
    missing = len(symbols) - len(equations)
    step = (config.ubound - config.lbound) / config.l

    # add obious condition: c_i = \sum_j a_ij
    for i in range(missing):
        eq = []
        for j in range(i+1):
            # equations.append(sympify(f"a_{i+2}{j+1} - c_{i+2}"))
            eq.append(f"a_{i+2}{j+1}")
            if f"a_{i+2}{j+1}" not in map(str, symbols):
                symbols.append(sympify(f"a_{i+2}{j+1}"))
        equations.append(sympify(" + ".join(eq) + f" - c_{i+2}"))
    
    symbols.sort(key=lambda x: str(x))

    # remove c_i from variables
    solve_for = []
    for sym in symbols:
        if not str(sym).startswith("c"):
            solve_for.append(sym)

    # solve system
    res = solve(equations, solve_for)
    res = res[0]
    print(*zip(solve_for, res), sep="\n")

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
        # if not i % 100:
        # print(*vals_ind, *map(lambda x: round(x, 3), vals))

        values = []
        # substitute c_i in solved system 
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
                res = nsolve(equations, symbols, [k+1 for k in range(len(symbols))], maxsteps=10, tol=1e-30)
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
    # config.dt = 0.004
    # config.startt = 0.33
    step = 0.1
    config.dt = 0.01
    config.startt = -0.2
    config.endt = config.startt + step 

    n = 5
    fig, axs = plt.subplots(3, n)

    for j in range(n):

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
                if i == 0:
                    axs[i, j].set_title(f"{round(config.startt, 3)}")
                # axs[i, j].set_xlabel("c_2")
                # axs[i, j].set_ylabel("c_3")
                # axs[j, i].colorbar()
        config.startt += step 
        config.endt +=  step

    # plt.tight_layout()
    # plt.colorbar()
    plt.show()

def test(config):
    tableaux = []
    step = (config.ubound - config.lbound) / config.l
    for i in range(config.l):
        c_3 = config.lbound + i * step
        for j in range(config.l):
            # print(i, j)
            c_2 = config.lbound + j * step
            try:
                #   b[1](2 - 3*c[2] - 3*c[3] + 6*c[2]*c[3])/(6*c[2]*c[3]), b[2] -> (-2 + 3*c[3])/(6*c[2]*(-c[2] + c[3])), b[3] -> (-2 + 3*c[2])/(6*(c[2] - c[3])*c[3]), a[3][2] -> ((c[2] - c[3])*c[3])/(c[2]*(-2 + 3*c[2]))
                b_1 = (2 - 3 * c_2 - 3 * c_3 + 6 * c_2 * c_3) / (6 * c_2 * c_3)
                b_2 = (-2 + 3 * c_3) / (6 * c_2 * (-c_2 + c_3))
                b_3 = (-2 + 3 * c_2) / (6 * c_3 * (c_2 - c_3))
                a_32 = ((c_2 - c_3) * c_3) / c_2 * (-2 + 3 * c_2)

                a_21 = c_2
                a_31 = c_3 - a_32

                tableau = Tableau(
                    ["c_2", "c_3", "b_1", "b_2", "b_3", "a_21", "a_31", "a_32"],
                    [c_2, c_3, b_1, b_2, b_3, a_21, a_31, a_32],
                    3 
                )
                tableaux.append(tableau)
            except:
                tableaux.append(None)
            
    return tableaux

if __name__ == "__main__":
    s = 3
    symbols, equations = generate_system(s)
    pretty.add_system(symbols, equations)

    config = Config(10, -2.0, 2.0)
    # tableaux = gen_tableaux(symbols, equations, s, config)
    tableaux = test2(symbols, equations, s, config)
    # tableaux = test(config)
    for t in tableaux:
        pretty.add_tableau(t)
        if t is not None:
            t.print()
            print("")
    # compare(tableaux, config)
    pretty.render()
    drift(tableaux, config)
    cache.save()
