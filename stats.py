import os
import sys
from solve import generate_system
import matplotlib.pyplot as plt

def save_system(s):
    symbols, equations = generate_system(s)
    symbols = map(str, symbols)
    equations = map(str, equations)
    
    with open(f"system_{s}.txt", "w") as f:
        for sym in symbols:
            f.write(f"{sym} ")
        f.write("\n")
        for e in equations:
            f.write(f"{e}\n")

def stats(s):
    if not os.path.exists(f"system_{s}.txt"):
        save_system(s)
    
    with open(f"system_{s}.txt", "r") as f:
        data = f.readlines()

    symbols = data[0].split()
    equations = data[1:]

    d = {}
    for eq in equations:
        c = str(eq).count("+") + 1
        if c not in d:
            d[c] = 0
        d[c] += 1

    pairs = list(zip(d.keys(), d.values()))
    pairs.sort(key=lambda x: x[0])
    
    plt.bar([str(x[0]) for x in pairs], [x[1] for x in pairs])
    plt.show()

def tmp():
    with open("products_in_s12.txt", "r") as f:
        data = f.read()

    d = {}
    for c in data.split(" "):
        c = int(c)
        if c not in d:
            d[c] = 0
        d[c] += 1

    pairs = list(zip(d.keys(), d.values()))
    pairs.sort(key=lambda x: x[0])
    
    plt.bar([str(x[0]) for x in pairs], [x[1] for x in pairs])
    plt.title(f"total: {sum(map(int, data.split(" ")))}")
    plt.xlabel("equation size (products)")
    plt.ylabel("count")
    plt.xticks(rotation=90)
    plt.show()

if __name__ == "__main__":
    tmp()
    # for i in range(9, 10):
    #     stats(i)
    #     save_system(i)