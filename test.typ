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