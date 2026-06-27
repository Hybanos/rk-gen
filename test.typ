#import "@preview/tdtr:0.5.5" : *

#let rk-tree = tidy-tree-graph.with(
    draw-node: ((label, )) => (stroke : 1pt + black, shape: circle, fill: black, label: ""),
    draw-edge: (stroke: 1pt + black, marks: "-"),
    spacing: (15pt, 20pt),
    node-width: 3pt,
    node-height: 3pt,
)

#rk-tree()[
    - haha #node-attr(rotate: 180deg)
        - haha
        - haha
            - haha
]

#let butcher-tableau = table.with(
    stroke: (x, y) => if x == 0 {(right: 1pt + black)},
    inset: 10pt,
    align: center
)

#set text(14pt)

#grid(
  columns: 8,
  align: center + bottom,
  gutter: 60pt,


rk-tree[
- haha #node-attr(rotate: 180deg)
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
  - haha
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
    - haha
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
  - haha
  - haha
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
  - haha
    - haha
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
    - haha
    - haha
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
    - haha
      - haha
]
)

#grid(
  columns: 8,
  align: center + bottom,
  gutter: 60pt,

rk-tree[
- haha #node-attr(rotate: 180deg)
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
  - haha
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
    - haha
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
  - haha
  - haha
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
  - haha
    - haha
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
    - haha
    - haha
],

rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
    - haha
      - haha
]
)
#pagebreak()

#set align(center)
#grid(
  columns: 2,
  gutter: 6pt,
  align: center + horizon,
$t = "[..[..]]" =$,
$
#rk-tree[
- haha #node-attr(rotate: 180deg)
  - haha
    - haha
    - haha
  - haha
  - haha
]
$
)

$ 
t! &= 18 \
\
\
Phi(t) &= sum_(i j) b_i c_i^2 a_(i j) c_j^2 \
 $

$ "[..[..]]"! = 1 times 1 times 3 times 1 times 1 times 6 = 18$

#let r = text.with(fill: red)
#let g = text.with(fill: green)
#let b = text.with(fill: blue)
#let o = text.with(fill: orange)

$
  sum_(#r("i") #g("j"))^#o("6") b_#r("i") c_#r("i")^2 a_(#r("i") #g("j")) c_#g("j")^2 \
  ⇓ \
  b_#r("1") c_#r("1")^2 a_(#r("1") #g("2")) c_#g("2")^2 + b_#r("2") c_#r("2")^2 a_(#r("2") #g("1")) c_#g("1")^2 + dots + b_#r("5") c_#r("5")^2 a_(#r("5") #g("6")) c_#g("6")^2 = 1 / #b("18")
$

$
  c_i = a_(i 1) + a_(i 2) + dots + a_(i j)
$

#pagebreak()
Equation de Riccati :
$
  (d y) / (d x) &= -2y^2 + x(2x + 3)y - x \
  y(x) &= 1 / (2x + 3)
$

#pagebreak()

$
  y(x)' &= f(x, y(x))\
  \
  y(x_0) &= y_0
$

$
  y(x) &= integral f(x, y(x)) \
  \
  y(x_0) &= y_0
$

$
  F_(a\/b) = G (M_a M_b)/d^2
$
$
  F = m a
$
$
  a = (d^2 x) / (d t^2)

$
$
  d = x_a - x_b
$

$
  P_(t+1) &= P_(t) + v_(t) times "dt" \
  v_(t+1) &= v_(t) + F_(t) times "dt"
$

#pagebreak()

$
  (d^2 x^mu) / (d s^2) = - Gamma^mu_(alpha beta) (d x^alpha) / (d s) (d x^beta) / (d s)\
  x_0 = (x^0_0, x^1_0, x^2_0, x^3_0, (d x^0_0) / (d s), (d x^1_0) / (d s), (d x^2_0) / (d s), (d x^3_0) / (d s))

$