import sympy

equations = [
    "b_1 + b_2 + b_3 + b_4 - 1",
    "b_2*c_2 + b_3*c_3 + b_4*c_4 - 1/2",
    "b_2*c_2**2 + b_3*c_3**2 + b_4*c_4**2 - 1/3",
    "a_32*b_3*c_2 + a_42*b_4*c_2 + a_43*b_4*c_3 - 1/6",
    "b_2*c_2**3 + b_3*c_3**3 + b_4*c_4**3 - 1/4",
    "a_32*b_3*c_2*c_3 + a_42*b_4*c_2*c_4 + a_43*b_4*c_3*c_4 - 1/8",
    "a_32*b_3*c_2**2 + a_42*b_4*c_2**2 + a_43*b_4*c_3**2 - 1/12",
    "a_32*a_43*b_4*c_2 - 1/24",
    # "a_21 - c_2",
    # "a_31 + a_32 - c_3",
    # "a_41 + a_42 + a_43 - c_4"
]

solve_for = [
    "b_1",
    "b_2",
    "b_3",
    "b_4",
    # "a_21",
    # "a_31",
    # "a_32",
    # "a_41",
    # "a_42",
    # "a_43",
]

equations = list(map(sympy.sympify, equations))
solve_for = list(map(sympy.sympify, solve_for))

tmp_equ = [
    equations[0],
    equations[1],
    equations[2],
    equations[4],
]

print(*tmp_equ, sep="\n", end="\n\n")
res = sympy.solve(tmp_equ, solve_for)
print(res)

for i in range(len(equations)):
    eq = equations[i]
    for k, v in res.items():
        eq = eq.subs(k, v)
    # eq.simplify()
    equations[i] = eq

print(*equations, sep="\n", end="\n\n")

solve_for = [
    "a_32",
    "a_42",
    "a_43"
]
tmp_equ = [
    equations[3],
    equations[5],
    equations[6],
]

res = sympy.solve(tmp_equ, solve_for)
print(res)
for i in range(len(equations)):
    eq = equations[i]
    for k, v in res.items():
        eq = eq.subs(k, v)
    # eq.simplify()
    equations[i] = eq

print(*equations, sep="\n", end="\n\n")

solve_for = [
    "c_4"
]

tmp_equ = [
    equations[7]
]
res = sympy.solve(tmp_equ, solve_for)
for i in range(len(equations)):
    eq = equations[i]
    eq = eq.subs("c_4", 1)
    # eq.simplify()
    equations[i] = eq

print(*equations, sep="\n", end="\n\n")

solve_for = [

]
