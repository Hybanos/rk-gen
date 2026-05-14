from sympy import Symbol, nsolve, sympify

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

    equations.append(sympify("c_2 - 1/2"))
    equations.append(sympify("c_3 - 1"))

    pretty.add_system(symbols, equations)

    res = nsolve(equations, symbols, [i+1 for i in range(len(symbols))])
    for sym, r in zip(symbols, res):
        print(f"{sym} = {r}")
    pretty.add_tableau(symbols, res, s)

if __name__ == "__main__":
    s = 3
    symbols, equations = generate_system(s)
    try:
        solve(symbols, equations, s)
    except Exception as e:
        print(e)
    finally:
        pretty.render()