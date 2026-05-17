import numpy as np

def f(x, y):
    return -2 * y * y + x * (2 * x + 3) * y - x

def exact(x):
    return 1 / (2 * x + 3)

# def f(x, y):
#     return np.tan(x) / np.cos(y)

# def exact(x):
#     return np.asin(-np.log(np.abs(np.cos(x))))

# def f(x, y):
#     return -(3 * x * x + 1) * y 

# def exact(x):
#     return 5 * np.exp(-x**3 - x)

def abstract_rk(symbols, coefs, s):

    d = dict(zip(map(str, symbols), coefs))
    B = np.zeros(s)
    C = np.zeros(s)
    A = np.zeros((s, s))
    for i in range(s):
        B[i] = d.get(f"b_{i+1}", 0)
        C[i] = d.get(f"c_{i+1}", 0)
        for j in range(s):
            A[i,j] = d.get(f"a_{i+1}{j+1}", 0)
    
    # print(d)
    # print(B)
    # print(C)
    # print(A)
    # print("")

    t = 0
    Y = exact(t)
    dt = 0.0001

    while t < 3:
        stages = np.zeros(s)

        stages[0] = f(t + C[0] * dt, Y)
        for i in range(1, s):
            tmp = 0
            for j in range(i):
                tmp += stages[j] * A[i][j]
            tmp = Y + tmp * dt
            stages[i] = f(t + C[i] * dt, tmp)
        
        tmp = 0
        for i in range(s):
            tmp += stages[i] * B[i]
        Y = Y + tmp * dt

        t += dt
        # print(Y, exact(t))

    # print("\n")

    return (Y - exact(t)) / abs(exact(t))