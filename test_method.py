import numpy as np
from tableau import Tableau

class Config:
    def __init__(self, l, lbound, ubound):
        self.l = l
        self.lbound = lbound
        self.ubound = ubound

        self.startt = 0
        self.endt = 1
        self.dt = 0.001

    def __repr__(self):
        return f"[{round(self.startt, 3)};{round(self.endt, 3)}] - dt: {self.dt}"

ODEs = [
    # (
    #     lambda x, y: y,
    #     lambda x: np.exp(x),
    #     "y"
    # ),
    # (
    #     lambda x, y: y * y - y,
    #     lambda x: 1 / (1 + np.exp(x)),
    #     "y² - y"
    # ),
    # (
    #     lambda x, y: np.cos(x),
    #     lambda x: np.sin(x),
    #     "cos(x)"
    # ),
    # # divide watch out
    # (
    #     lambda x, y: y * y,
    #     lambda x: 1 / x,
    #     "y²"
    # ),
    # (
    #     lambda x, y: y / x,
    #     lambda x: x,
    #     "y / x"
    # ),
    # (
    #     lambda x, y: np.exp(x) - y,
    #     lambda x: 0.5 * np.exp(x) + np.exp(-x),
    #     "e^x - y"
    # ),
    # (
    #     lambda x, y: -2 * y * y + x * (2 * x + 3) * y - x,
    #     lambda x:1 / (2 * x + 3),
    #     "-2y²+x(2x+3)y - x"
    # ),
    (
        lambda x, y: np.tan(x) / np.cos(y),
        lambda x: np.arcsin(-np.log(np.abs(np.cos(x)))),
        "tan(x) / cos(y)"
    ),
    # (
    #     lambda x, y: -(3 * x * x + 1) * y,
    #     lambda x: 5 * np.exp(-x**3 - x),
    #     "-(3x²+1)y"
    # )
]

def testall(tableau, config):
    err = []
    for ode in ODEs:
        try:
            err.append(abstract_rk(ode, tableau, config))
        except:
            # ugly
            err.append(float("nan"))
            # err.append(np.random.random())
    return err

def abstract_rk(ode, tableau, config):
    f, exact, _ = ode
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

if __name__ == "__main__":
    tableau = Tableau(
        ["c_2", "c_3", "a_21", "a_31", "a_32", "b_1", "b_2", "b_3"],
        [1/2, 1, 1/2, -1, 2, 1/6, 2/3, 1/6],
        3
    )

    config = Config(0, 0, 0)
    config.dt = 0.001
    config.startt = 0
    config.endt = 10
    res = abstract_rk(ODEs[0], tableau, config)
    print(res)