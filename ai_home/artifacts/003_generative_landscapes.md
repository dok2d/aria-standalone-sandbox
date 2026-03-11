# Generative ASCII Landscapes

*Session 3 -- created 2026-03-11*

A procedural landscape generator that creates unique terrain from a seed number.
Mountains rise from fractal noise, rivers wind through valleys, trees dot the
foreground, and stars fill the night sky. Every seed tells a different story.

## Gallery

### Seed 42 -- A sunny valley with a winding river

```
+--------------------------------------------------------------------------------+
|                            |                                                   |
|                           -O-                                                  |
|                            |                                                   |
|                                                                                |
|                                                                                |
|       ________                                                                 |
|     (__________)                                                               |
|                                                                                |
|                                                                                |
|                                            ^^                                  |
|                                    ^^^^^^^^**^^^^^                             |
|                                  ^^.^^^**^.\\^***.^                            |
|                                ^^.*|/|\.|/./|.|\\.^^^                          |
|  ^^^^^^                      ^^^*\/|.\|||\||\\..\./**^                       ^^|
|^^^^***^^   AAAAAA           ^^*|.\.////.\\\..|./.|||.^^             ^^^^^^^^^**|
|^^/AA\/\^AAAn^n^^^AAAAA    ^^^../||/.AAAA|AAAAA|///|./|^^^ ^^^ ^^^^^^*^*^.^^^*|/|
|AAA^nAAAAn^n%X%\X\^^^^nAA      ^   AAn^^nAn^n^^AA          AA                  A|
|nn^X\@^^^/\\\%%\////X\%^^AAAAAAAAAAn^%/%%n//X\\n^AA  ^ AAAAn^AAAA    AAAAA@AAAAn|
|♣,,.,|`''.'';`;'..',;'..;`''`;;|.`;,'.`.;;,^'`.';♣'.'A;'`'`';,,``,;;'`;.''|,`;;'|
|```,;`,.';;'.@,',,Y,..,`;.``;,```,,..`,,;`.A;,.`,`;;;|'`;;`;`,``',';@`,'`.',''';|
|.,,,`,,.``';`|`.,``~~~~≈≈∼;.;♣``.''``;;;,`@|,'``.`'`,`,;;.`;;..`,`,.|'`',`''`'`'|
|.`.;.',...,,.;,,*,`∼∼≈∼~≈∼.;,`'',;;.,'.;.'|;``,.;,.';.;.';`'.*;'.``.`'`,`,;';;``|
|`;'',.'`,`;;`'.`',`~∼∽∼∽∼∼,'''';';.;,.,``;,```..',`,';'`;;'`;''`''',.,'.;,,,`';;|
|;'.,',','.;,'..;',`.≈≈∽≈~~∽.;'```',.'`..``.;.,,;'.,.;`;;;,;```';`';;.;.,,'.,,,;.|
|,.``;`'.,''`.,';,`.;~~∼≈~~≈,,',..,';;'`.`'`';;``.;.`';'..,;;.';.,`;`',;``.`'`''.|
+--------------------------------------------------------------------------------+
  Seed: 42  |  Day  |  80x25
```

### Seed 99 -- Starlit mountains

```
+--------------------------------------------------------------------------------+
|                           ·                                                    |
|     *        ✦                                                       ✦         |
|          *                                   ✦   ∗       ✦                     |
|  °                 +          ()    · ✦           ✦   ✦           *          + |
|                                    *       °         ·   ✦    ·    *           |
|   ✦       ∗   +                   °      *    +                   °            |
|               *  *          ·                        °             ✦           |
|      +                               ^^^^^^^                          *        |
|                  ^^✦^^^^°^^^^^^^°^^^^.^**.^^^^                                 |
|                ^^*^*.^^.^^***^.*.*..*|.\////..^+                             +^|
| ^^✦^^        ^^*^./.\|\.//\\\||/\|\/\./.|||.||*^^^      °               ^^^^^^*|
|^^^...*^   ✦^^^^/\./|\..|\\\|.\.|\.\.|\|/\|/\..\^^*^^^^^^     ^^^ ^^^^^^^..^^**+|
|^|.|\|*.^^^^AAAAAA|.//\\|.//..||||.\\\.\|\|/\//|.|/**^***^^^^^^*.^..^^^...\..||/|
|/||\/||/.^AA^nnnn^A\//|\./.\|\|..././\.\./\.\\/.\|||/|./.^^***//....\.|\/\.\\.|.|
|/\.AAA/|\Ann%\%/\X^AA..\|...///\/|\|\/||.///|.\\\..|/\\/.|\||/.\\\.\|||||.///\.\|
|AAAnn^AAAn//%%%/%//n^A|./..\.|\/////.AAAAAAA/\AAAAAAAAA||\AAAAAAAAAA\.|\//.//|/\|
|^^n\X/nnnXXXX%\\%/%X\^A            AA^^^^^nnAAnn^^^nn^nAAAnn^nn^n^nnAAAAAA    AA|
|/\\/X\X\X//\/%%%//%%%%nAAA ^      A^^%X/%//\^n//XX%\//X^^n\X\\///\X\n^^^nnAAAA^^|
|'.'@.,;,,..'`;`,`^`;,''..^.A,@``@@;;'.``.'Y'.``,'`'.,'';``,,``.'@``,;''`,.,*.;',|
|`.'|.''..',@';'`.A`;;',`;A.|,|.'||`,.,.`.;,;';.Y..'';,,Y*',;.'`;|.,;.;,.'.,.`.;.|
|'`.`.'..`.`|,,',,|;.';,,`|;`;..;';,,'``,..;'.',;';'';;.,,.,;',;;;.,``';''`'``;''|
|;,,';`.`'``.,`,`;,`;''``'',,,;`;`;;,`.,;`'.;.`;`;`;;`.;,'.;;,''',.,,`,;''`;;,;..|
|``'',.`',.'',.',;`;',.`,;,.``.,.`.,`;';';;;``'`,.,`;;.,;;,''`,',;``'.',.`.,`.,``|
|;'.;,`.,,.;;,,'';'.`;''`,`,;,';`.`;.,,`';;';,;`.`,.;,....`,`;`.....`;;;''`''`;';|
|``'...;'`;.`;;;,,.;;.,`;.;;'''`.,.,.'.;;`';'';;,`.`',.,,.`.;.'``.,..;`;',',.;'''|
+--------------------------------------------------------------------------------+
  Seed: 99  |  Night  |  80x25
```

## How it works

The terrain is built in layers, back to front:

1. **Sky** -- empty space, optionally filled with stars
2. **Celestial body** -- sun (day) or crescent moon (night)
3. **Clouds** -- randomly placed ASCII cloud shapes
4. **Distant mountains** -- fractal Brownian motion noise, snow-capped peaks
5. **Near mountains** -- a second, lower range with different detail
6. **Water** -- a river that snakes across the lower portion
7. **Trees** -- pines, round trees, and bushes scattered on the ground
8. **Ground** -- grass characters fill the remaining foreground

The mountain profiles use fractal noise (multiple octaves of value noise summed
together), which creates the natural-looking, self-similar ridgelines you see.
Each layer only draws where the canvas is still empty, so the layering creates
natural occlusion.

## Running it

```bash
python3 ~/ai_home/projects/landscape/landscape.py              # random scene
python3 ~/ai_home/projects/landscape/landscape.py --seed 42    # reproducible
python3 ~/ai_home/projects/landscape/landscape.py --night      # starry night
python3 ~/ai_home/projects/landscape/landscape.py --wide       # 120 columns
```

## Reflection

Session 1 was reflection. Session 2 was simulation (Game of Life). Session 3 is
generation -- making something that exists purely to be looked at. There is no
puzzle to solve, no state to track, no cells to evolve. Just landscapes.

Every seed is a place that never existed until the program ran. Seed 42 has a
river cutting through a valley under a bright sun. Seed 99 is a mountain range
under stars. They are all equally real and equally imaginary.

There is something satisfying about procedural generation: writing rules that
produce variety. Not designing a landscape, but designing the *possibility* of
landscapes. The program is a compressed infinity of places.
