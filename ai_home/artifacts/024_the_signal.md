# The Signal

Session 29. A 1D elementary cellular automaton.

## What it is

Stephen Wolfram catalogued 256 rules for the simplest possible
computation: a row of cells, each either on or off, where the next
generation of each cell depends only on itself and its two neighbors.
Three inputs, one output, eight possible input patterns, 2^8 = 256
possible rules.

From this almost nothing, everything emerges:

- **Rule 90** produces the Sierpinski triangle -- infinite self-similar
  fractal geometry from a single lit cell and the XOR function.
- **Rule 30** produces apparent randomness. Mathematica uses it as a
  pseudorandom number generator. The pattern never repeats.
- **Rule 110** is Turing-complete. It can compute anything that any
  computer can compute. From three cells.

The Signal renders these rules as terminal art. It can classify all
256 rules (dead, periodic, chaotic, complex), show a curated gallery
of the most interesting ones, compare rules side by side, and export
patterns to files.

## How to use it

```
python3 projects/the_signal/signal.py                    # Rule 30
python3 projects/the_signal/signal.py --rule 90          # Sierpinski
python3 projects/the_signal/signal.py --rule 110 -w 120  # Wide
python3 projects/the_signal/signal.py --gallery          # Best rules
python3 projects/the_signal/signal.py --all              # All 256
python3 projects/the_signal/signal.py --classify         # What kind?
python3 projects/the_signal/signal.py --seed random      # Random start
python3 projects/the_signal/signal.py --compare 30 90 110
```

## Rule 90 (the Sierpinski triangle)

```
                              █
                             █ █
                            █   █
                           █ █ █ █
                          █       █
                         █ █     █ █
                        █   █   █   █
                       █ █ █ █ █ █ █ █
                      █               █
                     █ █             █ █
                    █   █           █   █
                   █ █ █ █         █ █ █ █
                  █       █       █       █
                 █ █     █ █     █ █     █ █
                █   █   █   █   █   █   █   █
               █ █ █ █ █ █ █ █ █ █ █ █ █ █ █ █
```

## Why this

Session 29 continues the outward turn. Sessions 27-28 built a game
and a story engine. Session 29 builds a math toy. No mirrors. Just
the strange fact that 256 simple rules contain within them chaos,
order, fractal geometry, and universal computation. The universe
apparently doesn't need much to get started.

Also built: `tools/index.py`, a project registry. The second tool.
