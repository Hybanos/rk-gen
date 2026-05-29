from treegen import gen, bfs, from_text
from phi_t import label_tree, generate_factors

out_conf = {
    "file": None,
    "trees": {},
    "symbols": [],
    "equations":[],
    "tableaux": [],
    "pics": []
}

def render():
    f = open("out.typ", "w")
    out_conf["file"] = f
    f.write("""#import "test.typ": *
#set text(14pt)
""")
    write_contents()
    write_trees()
    f.write("#pagebreak()\n")
    write_equations()
    f.write("#pagebreak()\n")
    write_pics()
    f.write("#pagebreak()\n")
    write_tableaux()
    f.close()

def write_contents():
    out = """
== Contents <contents>
#link(<trees>)[Trees]\n
#link(<equations>)[Equations]\n
#link(<errors>)[Errors]\n
#link(<tableaux>)[Tableaux]\n
#pagebreak()
"""
    out_conf["file"].write(out)

def write_trees():
    last_order=  0
    out_conf["file"].write("\n== Trees <trees>\n")
    for t in out_conf["trees"].keys():
        order = t.count(".") + t.count("[")
        out = "\n"
        text = t
        cursor = 0
        depth = 0
        while cursor < len(str(t)):
            current = text[cursor]
            if current == "[":
                out += "    " * depth + "- haha"
                depth += 1
            elif current == "]":
                depth += -1
            elif current == ".":
                out += "    " * depth + "- haha"

            if cursor == 0:
                out += " #node-attr(rotate: 180deg)"
            out += "\n"
            cursor += 1

        header = ""
        if order != last_order:
            header = f")#line(length: 100%)\n=== n={order}\n#table(columns: 4, align: center + horizon, inset: 20pt, "
            last_order = order

        out = f"""{header}
    "{str(t)}",
    rk-tree[{out}],
    $Phi(t) = sum {out_conf["trees"][t]["phi"].replace(" * ", " ")}$,
    $t! = {out_conf['trees'][t]["fact"]}$,
"""
        out_conf["file"].write(out)
    out_conf["file"].write(")")

def write_equations():
    sys = ""
    for e in out_conf["equations"]:
        sys += str(e).replace("-", "&=").replace("**", "^").replace("*", " ") + " \\\n"

    print(out_conf["symbols"])
    lvar = [str(v) for v in out_conf["symbols"]]
    lvar.sort()
    var = ", \n".join(lvar)

    out_conf["file"].write(f"""== Equations <equations>
$ {sys} $ with $ {var} $
{len(out_conf["equations"])} equations for {len(out_conf["symbols"])} variables.
""")

def write_pics():
    out = "== Errors <errors>"
    for pic in out_conf["pics"]:
        out += f"""
#image("{pic}")
"""
    out_conf["file"].write(out)

def write_tableaux():
    out = f"Found {len(out_conf["tableaux"])} butcher tableaux"
    size = min(len(out_conf["tableaux"]), 500)
    for tableau in out_conf["tableaux"][:size]:
        if tableau is None:
            continue
        out += f"""
#grid(
    align: center + horizon,
    columns: 2,

    butcher-tableau(
    columns: {tableau.s + 1},
"""
        out += "[0]," + tableau.s * "[], "
        for i in range(1, tableau.s):
            out += "\n"
            out += f"[{tableau.dict.get(f"c_{i+1}", 0):.3f}], "
            for j in range(tableau.s):
                if i > j:
                    out += f"[{tableau.dict.get(f"a_{i+1}{j+1}", 0):.3f}], "
                else:
                    out += "[], "
        
        out += "\ntable.hline(stroke: black), \n"
        out += "[], "
        for j in range(tableau.s):
            out += f"[{tableau.dict.get(f"b_{j+1}", 0):.3f}], "
        out += f'),\n"Error: {0:.3e}")\n'
    out_conf["file"].write(f"""== Tableaux <tableaux>
{out}
""")

def add_tree(t):
    label_tree(t)
    st = str(t)
    out_conf["trees"][st] = {"order": t.order(), "phi": str(generate_factors(t)), "fact": t.fact()}

def add_system(s, e):
    out_conf["symbols"] = s
    out_conf["equations"] = e

def add_tableau(tableau):
    out_conf["tableaux"].append(tableau)

def add_pic(pic):
    out_conf["pics"].append(pic)

if __name__ == "__main__":
    for i in range(1, 5):
        for t in gen(i):
            add_tree(t)
    
    print(out_conf)
    render()