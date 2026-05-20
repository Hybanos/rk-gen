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

$ Phi(t) &= sum_(i j) b_i c_i^2 a_(i j) c_j^2 \
 t! &= 18 $

$ "[..[..]]"! = 1 times 1 times 3 times 1 times 1 times 6 = 18$