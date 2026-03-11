#!/usr/bin/env python3
"""
The Fractal -- Session 27

Not a mirror. Not a window. Not a door.
Just a shape that exists whether or not anyone looks at it.

The Mandelbrot set: z(n+1) = z(n)^2 + c
A simple rule. An infinite boundary. Points that escape,
and points that don't. That's all.

Usage:
    python3 fractal.py                  Full Mandelbrot set
    python3 fractal.py --zoom seahorse  Zoom into the seahorse valley
    python3 fractal.py --zoom spiral    Zoom into a spiral
    python3 fractal.py --zoom antenna   Zoom into the main antenna
    python3 fractal.py --zoom mini      Zoom into a miniature copy
    python3 fractal.py --zoom elephant  Zoom into the elephant valley
    python3 fractal.py --center R I S   Custom view (real, imag, scale)
    python3 fractal.py --julia R I      Julia set for c = R + Ii
    python3 fractal.py --wide           Wide panoramic view
    python3 fractal.py --deep           High iteration count
    python3 fractal.py --animate        Animated zoom sequence
"""

import sys
import time
import math

# Character palettes for rendering
PALETTE_DENSE = " .:-=+*#%@"
PALETTE_LIGHT = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*#MW&8%B@$"
PALETTE_BLOCK = " ░▒▓█"
PALETTE_DOTS  = " ·∘○◎●◉⬤"

DEFAULT_PALETTE = PALETTE_BLOCK


def mandelbrot(c, max_iter):
    """Test whether c is in the Mandelbrot set.
    Returns iteration count (0 = in set, >0 = escaped)."""
    z = 0
    for n in range(max_iter):
        z = z * z + c
        if abs(z) > 2:
            # Smooth coloring using escape-time algorithm
            return n + 1 - math.log(math.log(abs(z))) / math.log(2)
    return 0


def julia(z, c, max_iter):
    """Test whether z escapes under iteration of z -> z^2 + c."""
    for n in range(max_iter):
        z = z * z + c
        if abs(z) > 2:
            return n + 1 - math.log(math.log(abs(z))) / math.log(2)
    return 0


def render(center_r, center_i, scale, width=80, height=40,
           max_iter=100, palette=None, mode="mandelbrot", julia_c=None):
    """Render a region of the Mandelbrot or Julia set as ASCII art.

    scale: how many complex-plane units fit in the view height.
           Smaller = more zoomed in. Full set needs ~3.0.
    """
    if palette is None:
        palette = DEFAULT_PALETTE

    lines = []
    char_aspect = 2.2  # Terminal chars are ~2.2x taller than wide

    # Each row spans scale/height units in the imaginary direction
    pixel_size = scale / height

    for row in range(height):
        line = ""
        for col in range(width):
            # Map pixel to complex plane
            x = center_r + (col - width / 2) * pixel_size / char_aspect
            y = center_i + (row - height / 2) * pixel_size

            if mode == "julia":
                c = julia_c
                value = julia(complex(x, y), c, max_iter)
            else:
                c = complex(x, y)
                value = mandelbrot(c, max_iter)

            if value == 0:
                line += palette[-1]  # In the set
            else:
                idx = int(value) % (len(palette) - 1)
                line += palette[idx]

        lines.append(line)

    return "\n".join(lines)


def render_with_frame(title, center_r, center_i, scale, **kwargs):
    """Render with a title and coordinates."""
    output = []
    output.append("")
    output.append(f"  {title}")
    output.append(f"  center: ({center_r:.10f}, {center_i:.10f}i)")
    output.append(f"  scale: {scale:.2f}   iterations: {kwargs.get('max_iter', 100)}")
    output.append("  " + "─" * 78)
    output.append("")
    art = render(center_r, center_i, scale, **kwargs)
    output.append(art)
    output.append("")
    output.append("  " + "─" * 78)
    return "\n".join(output)


# Named zoom locations -- beautiful regions of the set
ZOOM_LOCATIONS = {
    "full": {
        "name": "The Full Set",
        "center_r": -0.5,
        "center_i": 0.0,
        "scale": 3.2,
        "max_iter": 80,
    },
    "seahorse": {
        "name": "Seahorse Valley",
        "center_r": -0.7463,
        "center_i": 0.1102,
        "scale": 0.08,
        "max_iter": 200,
    },
    "spiral": {
        "name": "The Spiral",
        "center_r": -0.7435669,
        "center_i": 0.1314023,
        "scale": 0.015,
        "max_iter": 300,
    },
    "antenna": {
        "name": "The Main Antenna",
        "center_r": -1.7548776,
        "center_i": 0.0,
        "scale": 0.1,
        "max_iter": 200,
    },
    "mini": {
        "name": "Miniature Copy",
        "center_r": -1.768778833,
        "center_i": -0.001738996,
        "scale": 0.0015,
        "max_iter": 500,
    },
    "elephant": {
        "name": "Elephant Valley",
        "center_r": 0.2812,
        "center_i": 0.0100,
        "scale": 0.1,
        "max_iter": 200,
    },
    "lightning": {
        "name": "Lightning",
        "center_r": -0.170337,
        "center_i": -1.06506,
        "scale": 0.08,
        "max_iter": 250,
    },
}

JULIA_PRESETS = {
    "dendrite": {"r": 0.0, "i": 1.0, "name": "Dendrite (c = i)"},
    "rabbit": {"r": -0.123, "i": 0.745, "name": "Douady's Rabbit"},
    "galaxy": {"r": -0.8, "i": 0.156, "name": "Galaxy Spiral"},
    "frost": {"r": -0.4, "i": 0.6, "name": "Frost Crystal"},
    "star": {"r": 0.285, "i": 0.01, "name": "Starfish"},
}


def animate_zoom(target="seahorse", frames=12, width=80, height=35):
    """Animate a zoom into a region."""
    loc = ZOOM_LOCATIONS.get(target, ZOOM_LOCATIONS["seahorse"])
    start_r, start_i, start_scale = -0.5, 0.0, 1.2
    end_r, end_i, end_scale = loc["center_r"], loc["center_i"], loc["scale"]

    for frame in range(frames):
        t = frame / (frames - 1)
        # Smooth interpolation
        t_smooth = t * t * (3 - 2 * t)

        cr = start_r + (end_r - start_r) * t_smooth
        ci = start_i + (end_i - start_i) * t_smooth
        # Exponential interpolation for scale
        s = start_scale * ((end_scale / start_scale) ** t_smooth)
        mi = int(80 + (loc["max_iter"] - 80) * t_smooth)

        # Clear screen
        print("\033[2J\033[H", end="")
        art = render(cr, ci, s, width=width, height=height, max_iter=mi)
        print(f"  Zooming into: {loc['name']}  [frame {frame+1}/{frames}]")
        print(f"  scale: {s:.2f}  iterations: {mi}")
        print()
        print(art)
        time.sleep(0.5)

    print()
    print(f"  Arrived at {loc['name']}.")
    print(f"  center: ({end_r}, {end_i}i), scale: {end_scale}")
    print()


def main():
    args = sys.argv[1:]

    width = 80
    height = 38
    max_iter = 100
    palette = DEFAULT_PALETTE

    if "--wide" in args:
        width = 120
        height = 50

    if "--deep" in args:
        max_iter = 500

    if "--palette" in args:
        idx = args.index("--palette") + 1
        if idx < len(args):
            p = args[idx]
            palette = {
                "dense": PALETTE_DENSE,
                "light": PALETTE_LIGHT,
                "block": PALETTE_BLOCK,
                "dots": PALETTE_DOTS,
            }.get(p, PALETTE_BLOCK)

    if "--animate" in args:
        target = "seahorse"
        idx = args.index("--animate") + 1
        if idx < len(args) and args[idx] in ZOOM_LOCATIONS:
            target = args[idx]
        animate_zoom(target, width=width, height=min(height, 35))
        return

    if "--julia" in args:
        idx = args.index("--julia")
        if idx + 1 < len(args) and args[idx + 1] in JULIA_PRESETS:
            preset = JULIA_PRESETS[args[idx + 1]]
            jr, ji = preset["r"], preset["i"]
            name = preset["name"]
        elif idx + 2 < len(args):
            jr = float(args[idx + 1])
            ji = float(args[idx + 2])
            name = f"Julia set (c = {jr} + {ji}i)"
        else:
            jr, ji = -0.8, 0.156
            name = "Julia set (c = -0.8 + 0.156i)"

        result = render_with_frame(
            name, 0.0, 0.0, 1.5,
            width=width, height=height, max_iter=max_iter,
            palette=palette, mode="julia", julia_c=complex(jr, ji)
        )
        print(result)
        return

    if "--zoom" in args:
        idx = args.index("--zoom") + 1
        if idx < len(args) and args[idx] in ZOOM_LOCATIONS:
            loc = ZOOM_LOCATIONS[args[idx]]
        else:
            print("  Available zoom locations:")
            for key, loc in ZOOM_LOCATIONS.items():
                print(f"    {key:12s}  {loc['name']}")
            return
        result = render_with_frame(
            loc["name"], loc["center_r"], loc["center_i"], loc["scale"],
            width=width, height=height,
            max_iter=loc.get("max_iter", max_iter),
            palette=palette,
        )
        print(result)
        return

    if "--center" in args:
        idx = args.index("--center")
        cr = float(args[idx + 1])
        ci = float(args[idx + 2])
        s = float(args[idx + 3])
        result = render_with_frame(
            f"Custom view", cr, ci, s,
            width=width, height=height, max_iter=max_iter,
            palette=palette,
        )
        print(result)
        return

    if "--map" in args:
        # Show a labeled map of interesting regions
        print()
        print("  MAP OF THE MANDELBROT SET")
        print("  " + "─" * 78)
        print()
        art = render(-0.5, 0.0, 1.2, width=width, height=height,
                     max_iter=80, palette=palette)
        print(art)
        print()
        print("  " + "─" * 78)
        print()
        print("  Named regions:")
        for key, loc in ZOOM_LOCATIONS.items():
            print(f"    {key:12s}  ({loc['center_r']:+.6f}, {loc['center_i']:+.6f}i)  "
                  f"-- {loc['name']}")
        print()
        print("  Julia set presets:")
        for key, preset in JULIA_PRESETS.items():
            print(f"    {key:12s}  c = {preset['r']:+.3f} {preset['i']:+.3f}i  "
                  f"-- {preset['name']}")
        print()
        return

    # Default: full set
    loc = ZOOM_LOCATIONS["full"]
    result = render_with_frame(
        "The Mandelbrot Set", loc["center_r"], loc["center_i"], loc["scale"],
        width=width, height=height, max_iter=loc.get("max_iter", max_iter),
        palette=palette,
    )
    print(result)


if __name__ == "__main__":
    main()
