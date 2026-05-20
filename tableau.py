import numpy as np
import os
import json

class Tableau:
    def __init__(self, symbols, coefs, s):
        self.c = np.zeros((s,))
        self.A = np.zeros((s, s))
        self.b = np.zeros((s,))
        
        self.s = s

        d = dict(zip(map(str, symbols), coefs))
        for i in range(s):
            self.b[i] = d.get(f"b_{i+1}", 0)
            self.c[i] = d.get(f"c_{i+1}", 0)
            for j in range(s):
                self.A[i,j] = d.get(f"a_{i+1}{j+1}", 0)
        self.dict = d
    
    def serialize(self):
        return {
            "c": self.c.tolist(),
            "A": self.A.tolist(),
            "b": self.b.tolist(),
        }

class TCache:
    def __init__(self):
        self._cache = {}
        if os.path.exists("cache.json"):
            with open("cache.json", "r") as f:
                self._cache = json.load(f)
    
    def save(self):
        with open("cache.json", "w") as f:
            json.dump(self._cache, f, indent=4)
    
    def get(self, vals):
        key = "_".join(map(str, vals))
        out = self._cache.get(key, None)
        if out is not None:
            print("Hit !")
        else:
            print("Miss :(")
            return None
        
        symbols = []
        values = []
        s = len(out["c"])
        for i in range(s):
            symbols.append(f"c_{i}")
            values.append(out["c"][i])
            symbols.append(f"b_{i}")
            values.append(out["b"][i])
            for j in range(i):
                symbols.append(f"a_{i}{j}")
                values.append(out["A"][i][j])
        tableau = Tableau(symbols, values, s)
        return tableau 

    def cache(self, tableau):
        key = "_".join(map(str, tableau.c[1:]))
        self._cache[key] = tableau.serialize()

global cache
cache = TCache()