import numpy as np
from tableau import Tableau

ODEs = [
    (
        lambda x, y: -2 * y * y + x * (2 * x + 3) * y - x,
        lambda x:1 / (2 * x + 3)
    ),
    (
        lambda x, y: np.tan(x) / np.cos(y),
        lambda x: np.asin(-np.log(np.abs(np.cos(x))))
    ),
    (
        lambda x, y: -(3 * x * x + 1) * y,
        lambda x: 5 * np.exp(-x**3 - x)
    )
]

def testall(tableau, config):
    err = []
    for ode in ODEs:
        err.append(abstract_rk(ode, tableau, config))
    return err

def abstract_rk(ode, tableau, config):
    f, exact = ode
    s = tableau.s

    t = config.startt
    Y = exact(t)
    dt = config.dt 

    while t < config.endt:
        stages = np.zeros(s)

        stages[0] = f(t + tableau.c[0] * dt, Y)
        for i in range(1, s):
            tmp = 0
            for j in range(i):
                tmp += stages[j] * tableau.A[i][j]
            tmp = Y + tmp * dt
            stages[i] = f(t + tableau.c[i] * dt, tmp)
        
        tmp = 0
        for i in range(s):
            tmp += stages[i] * tableau.b[i]
        Y = Y + tmp * dt

        t += dt

    # return (Y - exact(t)) / abs(exact(t))
    return (Y - exact(t))