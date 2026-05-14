from treegen import gen, bfs, from_text
from phi_t import label_tree, generate_factors

out_conf = {
    "file": None,
    "trees": {},
    "symbols": [],
    "equations":[],
    "tableaux": []
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
    write_tableaux()
    f.close()

def write_contents():
    out = """
== Contents <contents>
#link(<trees>)[Trees]\n
#link(<equations>)[Equations]\n
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
            header = f"#line(length: 100%)\n=== n={order}"
            last_order = order
        out = f"""{header}
{str(t)}
#rk-tree[{out}]
$Phi(t) = sum {out_conf["trees"][t]["phi"].replace(" * ", " ")} quad
t! = {out_conf['trees'][t]["fact"]}$
#linebreak()
"""
        out_conf["file"].write(out)

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

def write_tableaux():
    out = ""
    for symbols, mat, s in out_conf["tableaux"]:
        out += f"""#table(
    columns: {s + 1},
    inset: 10pt,
    align: horizon,
"""
        out += " [0]," + s * "[], "
        for i in range(1, s):
            out += f"[b_{i+1}], "
            for j in range(s):
                if i > j:
                    out += f"[a_{i+1}{j+1}], "
                else:
                    out += "[], "
        
        out += "[], "
        for j in range(s):
            out += f"[c_{j+1}], "
        out += ")"
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

def add_tableau(symbols, mat, s):
    out_conf["tableaux"].append((symbols, mat, s))

if __name__ == "__main__":
    for i in range(1, 5):
        for t in gen(i):
            add_tree(t)
    
    print(out_conf)
    render()