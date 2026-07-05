import numpy as np
import matplotlib.pyplot as plt
from sympy import sympify, solve, lambdify, diff

from treegen import gen
from phi_t import Factor, Factors, label_tree, generate_factors
from solve import generate_system, gen_tableaux
from test_method import Config, testall, ODEs

import pretty

def test():
    s = 2

    config = Config(300, -2.0, 2.0)

    symbols, equations = generate_system(s)
    tableaux = gen_tableaux(symbols, equations, s, config)

    fig, axs = plt.subplots(len(ODEs))
    if len(ODEs) == 1:
        axs = [axs]
    for j in range(len(ODEs)):
        config.dt = 0.01
        config.startt = config.dt
        config.endt = config.startt + config.dt

        c_vals = []
        errors = []
        while config.startt < np.pi * 2:

            sols = np.zeros(len(tableaux))
            for i, t in enumerate(tableaux):
                if t is not None:
                    err = testall(t, config)[j]
                    # sols.T[i] = np.abs(err)
                    sols.T[i] = err
                else:
                    sols.T[i] = np.nan
            
            m = np.nanmin(np.abs(sols))
            index = np.where(np.abs(sols) == m)[0][0]
            c_val = config.lbound + ((config.ubound - config.lbound) * index) / config.l
            c_vals.append(c_val)
            errors.append(sols[index])
            # print(index)

            config.startt += config.dt
            config.endt = config.startt + config.dt
        
        ran = np.arange(start=config.dt, stop=np.pi * 2, step=config.dt)
        axs[j].plot(ran, c_vals, label="c_2")
        axs[j].plot(ran, ODEs[j][0](ran, ODEs[j][1](ran)), label="ode")
        axs[j].plot(ran, ODEs[j][1](ran), label="exact")
        ax2 = axs[j].twinx()
        ax2.plot(ran, errors, label="err", color="gray", linestyle="--")
        ax2.set_ylabel("error")
        ax2.tick_params(axis="y")
        # ax2.set_yscale("symlog", linthresh=1e-10)
        axs[j].set_title(ODEs[j][2])
        axs[j].grid(which="both")

    plt.legend()
    plt.suptitle("[RK2] c_2 value with the lowest error")
    plt.show()

def stats(s):
    symbols = set()
    equations = []
    for i in range(1, s+1):
        for t in gen(i):
            label_tree(t)
            factors = generate_factors(t)
            lval = factors.sum(s) + f" - 1/{t.fact()}"
            equations.append(lval)
            symbols.update(sympify(lval).free_symbols)

    symbols = list(map(str,symbols))
    symbols.sort()

    counts = np.zeros(len(symbols), dtype=int)
    poly_total = 0
    for eq in equations:
        poly_total += eq.count("+") + 1
        print(sympify(eq))
        for i, symb in enumerate(symbols):
            counts[i] += eq.count(str(symb))
    
    
    a_count = s*(s-1)//2 - s + 1
    b_count = s
    c_count = s-1

    a = list(map(str, symbols))[:a_count]
    b = list(map(str, symbols))[a_count:a_count + b_count]
    c = list(map(str, symbols))[a_count + b_count:]

    plt.figure(figsize=(7, 5))
    plt.bar(a, counts[:a_count]                 , label="a")
    plt.bar(b, counts[a_count:a_count + b_count], label="b")
    plt.bar(c, counts[a_count + b_count:]       , label="c")
    plt.suptitle(f"s = {s}")
    plt.title(f"{poly_total} total sub-polynomials")
    # plt.tight_layout()
    plt.xticks(rotation=90)
    plt.legend()
    # plt.show()
    plt.savefig(f"bar_{s}.png")
    plt.cla()

if __name__ == "__main__":
    stats(9)
    # test()