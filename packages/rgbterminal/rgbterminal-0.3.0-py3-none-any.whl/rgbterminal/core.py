import numpy as np
import colorsys
import time

class RGBText:
    """
    Represents a piece of text with an associated RGB color.
    Can render itself in either 256-color or truecolor ANSI mode.
    """

    def __init__(self, text: str, rgb: tuple[int, int, int] = None, truecolor: bool = False):
        """
        Parameters
        ----------
        text : str
            The text to colorize.
        rgb : tuple[int, int, int], optional
            RGB color tuple (default: black).
        truecolor : bool, optional
            Whether to use truecolor (24-bit) escape sequences.
        """
        self.truecolor: bool = truecolor
        self.text: str = text
        self.rgb: tuple[int, int, int] = rgb if rgb is not None else (0, 0, 0)

    # Convenient read-only RGB properties
    @property
    def r(self): return self.rgb[0]
    @property
    def g(self): return self.rgb[1]
    @property
    def b(self): return self.rgb[2]

    # Same, but using full color names
    @property
    def red(self): return self.r
    @property
    def green(self): return self.g
    @property
    def blue(self): return self.b

    # 256-color levels (0–5) per channel
    @property
    def r_level(self): return int(self.r / 255 * 5)
    @property
    def g_level(self): return int(self.g / 255 * 5)
    @property
    def b_level(self): return int(self.b / 255 * 5)

    # Aliases for consistency
    @property
    def red_level(self): return self.r_level
    @property
    def green_level(self): return self.g_level
    @property
    def blue_level(self): return self.b_level

    @property
    def code(self):
        """Return the corresponding 256-color code for the RGB value."""
        return 16 + 36 * self.r_level + 6 * self.g_level + self.b_level

    def __repr__(self):
        return str(self)

    def __str__(self):
        """
        Return the text wrapped in ANSI color codes.
        Automatically switches between 256-color and truecolor mode.
        """
        if not self.text:
            return ""

        if self.truecolor:
            # 24-bit color escape sequence
            return f"\033[38;2;{self.r};{self.g};{self.b}m{self.text}\033[0m"
        else:
            # 256-color fallback
            return f"\033[38;5;{self.code}m{self.text}\033[0m"

    @property
    def in_256color(self):
        """Always return the text in 256-color mode (useful for fallback)."""
        return f"\033[38;5;{self.code}m{self.text}\033[0m"


class RGBTextFactory:
    """
    Factory for quickly generating RGBText objects
    with shared base color / mode settings.
    """

    def __init__(self, rgb: tuple[int, int, int] = None, truecolor: bool = False):
        self._template = RGBText(text="", rgb=rgb if rgb else (0, 0, 0), truecolor=truecolor)

    # Pass-through accessors for template values
    @property
    def r(self): return self._template.r
    @property
    def g(self): return self._template.g
    @property
    def b(self): return self._template.b
    @property
    def red(self): return self._template.red
    @property
    def green(self): return self._template.green
    @property
    def blue(self): return self._template.blue
    @property
    def r_level(self): return self._template.r_level
    @property
    def g_level(self): return self._template.g_level
    @property
    def b_level(self): return self._template.b_level
    @property
    def red_level(self): return self._template.red_level
    @property
    def green_level(self): return self._template.green_level
    @property
    def blue_level(self): return self._template.blue_level
    @property
    def code(self): return self._template.code
    @property
    def in_256color(self): return self._template.in_256color

    def text(self, text: str, rgb: tuple[int, int, int] = None, truecolor: bool = None) -> RGBText:
        """
        Create a new RGBText instance.

        Parameters
        ----------
        text : str
            Text to colorize.
        rgb : tuple[int, int, int], optional
            Color override. Defaults to the factory’s color.
        truecolor : bool, optional
            Whether to use 24-bit mode (overrides factory setting).
        """
        color = rgb if rgb is not None else self._template.rgb
        tc = truecolor if truecolor is not None else self._template.truecolor
        return RGBText(text=text, rgb=color, truecolor=tc)

    def t(self, text: str) -> RGBText:
        """Short alias for self.text()."""
        return self.text(text)

    def t_truecolor(self, text: str) -> RGBText:
        """Intended alias for truecolor text (left here for API symmetry)."""
        return self.text_truecolor(text)


class GradientText:
    """
    Renders text with a smooth gradient between multiple RGB stops.
    Supports both 256-color and truecolor output.
    """

    def __init__(self, text: str, rgb_stops: list[tuple[int, int, int]], truecolor: bool = False):
        """
        Parameters
        ----------
        text : str
            Text to render with gradient.
        rgb_stops : list[tuple[int,int,int]]
            List of color stops along the gradient.
        truecolor : bool, optional
            Use 24-bit ANSI if True, else 256-color approximation.
        """
        self.text = text
        self.rgb_stops = rgb_stops
        self.truecolor = truecolor

    def __str__(self):
        """Return the text string with interpolated gradient colors."""
        if not self.text:
            return ""

        n = len(self.text)
        num_stops = len(self.rgb_stops)
        stop_indices = np.linspace(0, n - 1, num=num_stops, dtype=int)

        # Convert stops to HLS space for smoother color interpolation
        hls_stops = [colorsys.rgb_to_hls(r / 255, g / 255, b / 255) for r, g, b in self.rgb_stops]

        # Initialize arrays for interpolation
        hs, ls, ss = np.zeros(n), np.zeros(n), np.zeros(n)

        for i in range(num_stops - 1):
            start_idx, end_idx = stop_indices[i], stop_indices[i + 1]
            h1, l1, s1 = hls_stops[i]
            h2, l2, s2 = hls_stops[i + 1]

            # Fix hue wrapping around 0/1 boundary for continuity
            dh = h2 - h1
            if abs(dh) > 0.5:
                if dh > 0:
                    h1 += 1
                else:
                    h2 += 1

            seg_len = end_idx - start_idx + 1
            hs[start_idx:end_idx + 1] = np.mod(np.linspace(h1, h2, seg_len), 1.0)
            ls[start_idx:end_idx + 1] = np.linspace(l1, l2, seg_len)
            ss[start_idx:end_idx + 1] = np.linspace(s1, s2, seg_len)

        # Convert back to RGB for each character
        rgb_list = [
            tuple(int(c * 255) for c in colorsys.hls_to_rgb(h, l, s))
            for h, l, s in zip(hs, ls, ss)
        ]

        # Join the colorized characters
        out = ''.join(
            f"\033[38;2;{rgb[0]};{rgb[1]};{rgb[2]}m{c}\033[0m"
            if self.truecolor else self._to_256(c, rgb)
            for c, rgb in zip(self.text, rgb_list)
        )
        return out

    def _to_256(self, char, rgb):
        """Internal helper to convert RGB to nearest 256-color code."""
        r, g, b = rgb
        r_level = int(r / 255 * 5)
        g_level = int(g / 255 * 5)
        b_level = int(b / 255 * 5)
        code = 16 + 36 * r_level + 6 * g_level + b_level
        return f"\033[38;5;{code}m{char}\033[0m"


class GradientTextFactory:
    """
    Factory for creating gradient text objects with preset color stops.
    """

    def __init__(self, rgb_stops: list[tuple[int, int, int]] = None, truecolor: bool = False):
        """
        Parameters
        ----------
        rgb_stops : list[tuple[int,int,int]], optional
            Default gradient color stops.
        truecolor : bool, optional
            Default rendering mode.
        """
        self.rgb_stops = rgb_stops if rgb_stops is not None else [(255, 255, 255), (0, 0, 0)]
        self.truecolor = truecolor

    def text(self, text: str, rgb_stops: list[tuple[int, int, int]] = None, truecolor: bool = None) -> GradientText:
        """
        Create a new GradientText with the given stops and mode.
        """
        stops = rgb_stops if rgb_stops is not None else self.rgb_stops
        tc = truecolor if truecolor is not None else self.truecolor
        return GradientText(text=text, rgb_stops=stops, truecolor=tc)

    def t(self, text: str, rgb_stops: list[tuple[int, int, int]] = None, truecolor: bool = None) -> GradientText:
        """Short alias for self.text()."""
        return self.text(text, rgb_stops, truecolor)
    
    
def _lerp(a: float, b: float, t: float) -> float:
    return a + (b - a) * t

def _lerp_color(c1: tuple[int,int,int], c2: tuple[int,int,int], t: float) -> tuple[int,int,int]:
    return (
        int(_lerp(c1[0], c2[0], t)),
        int(_lerp(c1[1], c2[1], t)),
        int(_lerp(c1[2], c2[2], t)),
    )

def animated_gradient_print(gradient_text: "GradientText",
                     duration: float,
                     fps: int = 30,
                     speed: float = 2.0,
                     resolution: int = 10):
    """
    Smooth, perfectly-periodic sliding gradient.

    - resolution: total number of sampled colors around the circular gradient.
    - speed: number of full cycles per `duration` (1.0 = one full loop in duration).
    """
    frames = max(1, int(duration * fps))

    base = gradient_text.rgb_stops[:]  # original (sparse) stops
    m = len(base)
    if m == 0:
        return

    # --- Create a periodic dense sampling of the circular gradient ---
    # sample at `resolution` uniformly spaced positions around the loop
    dense: list[tuple[int, int, int]] = []
    for k in range(resolution):
        # position in "stop space" (0..m)
        pos = (k / resolution) * m
        i0 = int(pos) % m
        i1 = (i0 + 1) % m
        frac = pos - int(pos)
        c = _lerp_color(base[i0], base[i1], frac)
        dense.append(c)

    # keep a copy to restore at the end
    original_dense = dense[:]

    # --- Animate by sampling dense at fractional offsets (wraps smoothly) ---
    for frame in range(frames):
        # fractional offset in dense-space
        offset = (frame / frames) * speed * resolution  # float in [0, speed*resolution)
        offset %= resolution  # wrap to [0, resolution)
        shifted: list[tuple[int, int, int]] = []

        # sample dense at fractional positions (i + offset)
        for i in range(resolution):
            sample_pos = (i + offset) % resolution
            s0 = int(sample_pos)
            s1 = (s0 + 1) % resolution
            t = sample_pos - s0
            color = _lerp_color(dense[s0], dense[s1], t)
            shifted.append(color)

        gradient_text.rgb_stops = shifted
        print(gradient_text, end="\r", flush=True)
        time.sleep(1 / fps)

    # --- Restore original dense gradient so final state equals initial ---
    gradient_text.rgb_stops = original_dense
    print(gradient_text)  # final newline/print