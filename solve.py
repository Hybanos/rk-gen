from sympy import sympify, solve, lambdify, diff
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as colors 
from scipy.linalg import solve as lin_solve

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

def newton(symbols, equations, s, config, guesses=50000, cap=5000, max_steps=100):
    # add obious condition: c_i = \sum_j a_ij
    for i in range(s-1):
        eq = []
        for j in range(i+1):
            eq.append(f"a_{i+2}{j+1}")
            sym = f"a_{i+2}{j+1}"
            if sym not in map(str, symbols):
                symbols.append(sympify(sym))
        equations.append(sympify(" + ".join(eq) + f" - c_{i+2}"))
    
    symbols.sort(key=lambda x: str(x))

    # Jacobian
    jacobian_matrix = []
    for i in range(len(equations)):
        tmp = []
        for j in range(len(symbols)):
            tmp.append(diff(equations[i], symbols[j]))
        jacobian_matrix.append(tmp)

    print(equations)
    print(*jacobian_matrix, sep="\n", end="\n\n")

    # lambify
    lb_equations = lambdify(symbols, equations)
    lb_jacobi = lambdify(symbols, jacobian_matrix)

    tol = 1e-3
    out_params = []
    fails = 0
    skips = 0
    for k in range(guesses):
        if len(out_params) > cap:
            break
        log = f"random search {k} : {round(k / guesses * 100, 3)}%, {len(out_params)} found. f={fails}, s={skips}    "
        print(log, end="\r")
        x = np.random.random((len(symbols))) * (config.ubound - config.lbound) + config.lbound
        try:
            i = 0
            while True:
                i += 1
                if i > max_steps:
                    skips += 1
                    raise Exception()
                if any(np.isnan(x)):
                    raise Exception()
                J = np.array(lb_jacobi(*x))
                f = np.array(lb_equations(*x))
                dx = np.linalg.solve(J.T @ J, -J.T @ f)
                alpha = 1.0
                # backtracking
                while np.linalg.norm(lb_equations(*(x + alpha*dx))) > (1 - 1e-4*alpha)*np.linalg.norm(f):
                    alpha = alpha * 0.5
                    if alpha < 1e-12:
                        raise Exception()
                # if not i%1000:
                    # print(f, i, log, sep="\n")
                if np.max(np.abs(f)) < tol:
                    break
                x = x + alpha * dx
            
            # filter "bad" solutions
            # if np.max(np.abs(x)) > 10:
            #     skips += 1
            #     continue
            print("\n", x, "\n")
            out_params.append(x)
        except KeyboardInterrupt as e:
            raise e
        except Exception as e:
            fails += 1
            # print(e)
            pass

    print("\ndone", " "*50)
    # print(*out_params, sep="\n")
    tableaux = []
    for o in out_params:
        tableaux.append(Tableau(symbols, o, s))
    
    return tableaux 

def gen_tableaux(symbols, equations, s, config):
    missing = len(symbols) - len(equations)
    step = (config.ubound - config.lbound) / config.l

    # add obious condition: c_i = \sum_j a_ij
    for i in range(s-1):
        eq = []
        for j in range(i+1):
            eq.append(f"a_{i+2}{j+1}")
            sym = f"a_{i+2}{j+1}"
            if sym not in map(str, symbols):
                symbols.append(sympify(sym))
        equations.append(sympify(" + ".join(eq) + f" - c_{i+2}"))
    
    symbols.sort(key=lambda x: str(x))
    print(symbols)

    # remove c_i from variables
    solve_for = []
    floating = [f"c_{i+1}" for i in range(1, s)]
    for sym in symbols:
        if not str(sym).startswith("c"):
            solve_for.append(sym)

    # solve system
    print("Equations:", *equations, sep="\n", end="\n\n")
    print("Variables:", *solve_for, sep="\n", end="\n\n")
    res = solve(equations, solve_for)
    print(res)
    if s == 2:
        res = list(res.values())
    if s == 3:
        res = res[0]
    print(*zip(solve_for, res), sep="\n", end="\n\n")

    funcs = [lambdify(floating, f) for f in res]

    # compute c_i values
    vals = [config.lbound for _ in range(missing)]
    vals_ind = [0 for _ in range(missing)]
    tableaux = []
    for i in range(config.l**missing):
        for j in range(missing):
            if (i % config.l**j) == 0 and i != 0:
                vals_ind[j] += 1
                vals[j] = config.lbound + step * vals_ind[j]
                for k in range(j):
                    vals[k] = config.lbound 
                    vals_ind[k] = 0

        # check params == 0 or diagonal
        if any(map(lambda x: abs(x) < 0.0001, vals)) \
        or abs(vals[0] - sum(vals[1:])) < 0.0001:
            tableaux.append(None)
            continue

        # compute coefs
        values = [f(*vals) for f in funcs]
        # add c_i values to output
        values.extend(vals)

        tableaux.append(Tableau(symbols, values, s))

    return tableaux


def compare(tableaux, config):
    config.dt = 0.01
    config.startt = 0.0
    config.endt = 1.0
    s = 0
    sols = np.zeros((len(ODEs), len(tableaux)))
    for i, t in enumerate(tableaux):
        if t is not None:
            s = t.s
            err = testall(t, config)
            sols.T[i] = np.abs(err)
            # sols.T[i] = err
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
            # plt.imshow(x.reshape((config.l, config.l))[::-1,:], extent=[config.lbound, config.ubound, config.lbound, config.ubound], norm=colors.CenteredNorm())
            plt.xlabel("c_2")
            plt.ylabel("c_3")
            plt.title(ODEs[i][2])
            plt.colorbar()

        plt.tight_layout()
        plt.savefig(f"errs_{i}.svg")
        # plt.show()
        pretty.add_pic(f"errs_{i}.svg")
        plt.clf()

def drift(tableaux, config):
    n = 4

    step = np.pi * 2 / n
    step = 0.002
    config.dt = 0.01
    # trange = 0.01 * 50
    trange = config.dt
    config.startt = 0.0
    config.endt = config.startt + trange

    fig, axs = plt.subplots(len(ODEs), n)

    for j in range(n):

        s = 0
        sols = np.zeros((len(ODEs), len(tableaux)))
        for i, t in enumerate(tableaux):
            if t is not None:
                s = t.s
                err = testall(t, config)
                sols.T[i] = np.abs(err)
                # sols.T[i] = err
            else:
                sols.T[i] = float("nan")

        for i, x in enumerate(sols):
            if s == 2:
                axs[i, j].plot(np.arange(config.lbound, config.ubound, (config.ubound - config.lbound)/config.l), x)
                axs[i, j].set_yscale("log")
                axs[i, j].grid(which="both")
                if i == 0:
                    axs[i, j].set_title(f"{round(config.startt, 3)}")
                if j == 0:
                    axs[i, j].set_ylabel(ODEs[i][2])
        
            elif s >= 3:
                # axs[i, j].imshow(x.reshape((config.l, config.l))[::-1,:], extent=[config.lbound, config.ubound, config.lbound, config.ubound], norm=colors.SymLogNorm(1e-16), cmap="coolwarm")
                axs[i, j].imshow(x.reshape((config.l, config.l))[::-1,:], extent=[config.lbound, config.ubound, config.lbound, config.ubound], norm=colors.LogNorm())
                if i == 0:
                    axs[i, j].set_title(f"{round(config.startt, 3)}")
                if j == 0:
                    axs[i, j].set_ylabel(ODEs[i][2])
        config.startt += step 
        config.endt = config.startt + trange

    plt.suptitle(str(config))
    plt.show()
    plt.clf()

if __name__ == "__main__":
    s = 3
    symbols, equations = generate_system(s)
    pretty.add_system(symbols, equations)

    config = Config(100, -2.0, 2.0)
    # tableaux = newton(symbols, equations, s, config)
    tableaux = gen_tableaux(symbols, equations, s, config)
    for t in tableaux:
        pretty.add_tableau(t)
    # compare(tableaux, config)
    drift(tableaux, config)
    pretty.render()
    # cache.save()
