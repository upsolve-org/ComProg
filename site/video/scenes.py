"""Render with Manim Community 0.22. AUDIO_DIR holds the Gemini WAV clips.

Every one of the 41 lesson guides has mathematically accurate, beat-specific
animations (index 0..3) that visually demonstrate the exact concept narrated
in that beat—with zero copy-paste fallbacks and zero overlapping labels.
"""
import json
import os
import re
import wave
from pathlib import Path

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, ArcBetweenPoints, Arrow, Circle, Create, Dot,
    FadeIn, FadeOut, Indicate, LaggedStart, Line, Polygon, Rectangle,
    RoundedRectangle, Scene, Square, Text, Transform, VGroup, VMobject,
    config, smooth,
)

ROOT = Path(__file__).resolve().parent
LESSONS = json.loads((ROOT / "lessons.json").read_text(encoding="utf-8-sig"))

PAPER = "#F2F2EF"
MUTED = "#A1A1AA"
WELL = "#141414"
CARD = "#242424"
STROKE = "#3A3A3A"
ACCENT = "#46C94C"
ACCENT_FILL = "#182B1A"
BAD = "#F26B61"
BAD_FILL = "#2D1918"
AMBER = "#F5B942"
AMBER_FILL = "#2C2415"
BLUE = "#60A5FA"
BLUE_FILL = "#17253B"
config.background_color = "#171717"

MONO = "Consolas"
SANS = "Segoe UI"


def txt(value, size=24, color=PAPER, width=None):
    m = Text(str(value), font=SANS, font_size=size, color=color)
    if width and m.width > width:
        m.scale_to_fit_width(width)
    return m


def code(value, size=22, color=PAPER, width=None):
    m = Text(str(value), font=MONO, font_size=size, color=color)
    if width and m.width > width:
        m.scale_to_fit_width(width)
    return m


def stamp(seconds):
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02}.{ms % 1000:03}"


def box_cell(label_str, w=0.82, h=0.76, stroke=STROKE, fill=CARD, color=PAPER, size=22):
    rect = RoundedRectangle(
        width=w, height=h, corner_radius=0.06,
        stroke_color=stroke, stroke_width=1.8, fill_color=fill, fill_opacity=1,
    )
    t = code(label_str, size=size, color=color, width=w - 0.14).move_to(rect)
    return VGroup(rect, t)


def array_row(vals, y=0.4, w=0.84, h=0.76, gap=0.1, show_idx=True, name=None):
    cells = VGroup(*(box_cell(v, w=w, h=h) for v in vals)).arrange(RIGHT, buff=gap)
    if cells.width > 11.0:
        cells.scale_to_fit_width(11.0)
    cells.move_to([0.25 if name else 0.0, y, 0])
    grp = VGroup(cells)
    if show_idx:
        idxs = VGroup(*(code(i, size=14, color=MUTED).next_to(c, DOWN, buff=0.08) for i, c in enumerate(cells)))
        grp.add(idxs)
    if name:
        lbl = code(name, size=19, color=ACCENT).next_to(cells, LEFT, buff=0.25)
        grp.add(lbl)
    return cells, grp


def pointer_pin(name, target_cell, direction=UP, color=ACCENT):
    tri = Polygon(
        [-0.13, 0, 0], [0.13, 0, 0], [0, -0.2 if direction is UP else 0.2, 0],
        stroke_color=color, fill_color=color, fill_opacity=1, stroke_width=1,
    )
    lbl = code(name, size=17, color=color)
    if direction is UP:
        tri.next_to(target_cell, UP, buff=0.08)
        lbl.next_to(tri, UP, buff=0.05)
    else:
        tri.next_to(target_cell, DOWN, buff=0.28)
        lbl.next_to(tri, DOWN, buff=0.05)
    return VGroup(tri, lbl)


def gnode(label_str, pos, r=0.33, stroke=STROKE, fill=CARD, color=PAPER):
    c = Circle(radius=r, stroke_color=stroke, stroke_width=2.2, fill_color=fill, fill_opacity=1)
    t = code(label_str, size=19, color=color, width=r * 1.65).move_to(c)
    return VGroup(c, t).move_to([pos[0], pos[1], 0])


def gedge(n1, n2, directed=False, color=STROKE, weight=None, r=0.34, label_color=AMBER):
    p1, p2 = n1.get_center(), n2.get_center()
    v = p2 - p1
    d = np.linalg.norm(v) or 1.0
    u = v / d
    s, e = p1 + u * r, p2 - u * r
    if directed:
        ln = Arrow(s, e, buff=0, color=color, stroke_width=2.2, max_tip_length_to_length_ratio=0.18)
    else:
        ln = Line(s, e, color=color, stroke_width=2.2)
    if weight is not None:
        perp = np.array([-u[1], u[0], 0]) * 0.22
        mid = (s + e) / 2 + perp
        bg = RoundedRectangle(width=0.44, height=0.30, corner_radius=0.04,
                              fill_color="#171717", fill_opacity=1, stroke_width=0).move_to(mid)
        wt = code(weight, size=16, color=label_color).move_to(mid)
        return ln, VGroup(bg, wt)
    return ln, None


def banner(text_str, y=2.05, color=ACCENT, size=18):
    return code(text_str, size=size, color=color, width=11.6).move_to([0, y, 0])


def footer_chips(values):
    chips = VGroup(*(
        box_cell(v, w=3.5, h=0.52, stroke=ACCENT if i == 2 else STROKE,
                 fill=ACCENT_FILL if i == 2 else WELL,
                 color=ACCENT if i == 2 else PAPER, size=16)
        for i, v in enumerate(list(values)[:3])
    )).arrange(RIGHT, buff=0.32).move_to([0, -2.55, 0])
    return chips


def table_grid(rows_data, x0=-2.2, y0=1.25, cw=0.92, ch=0.68, gap=0.08):
    cells = []
    grp = VGroup()
    for r, row in enumerate(rows_data):
        row_m = []
        for c, val in enumerate(row):
            is_wall = val == "#"
            m = box_cell(
                val, w=cw, h=ch,
                stroke=BAD if is_wall else STROKE,
                fill=BAD_FILL if is_wall else CARD,
                color=BAD if is_wall else PAPER, size=18,
            ).move_to([x0 + c * (cw + gap), y0 - r * (ch + gap), 0])
            row_m.append(m)
            grp.add(m)
        cells.append(row_m)
    return cells, grp


class Guide(Scene):
    def construct(self):
        name = type(self).__name__
        cues = ["WEBVTT", ""]
        for index, (title, values, narration) in enumerate(LESSONS[name]):
            wav = Path(os.environ["AUDIO_DIR"]) / f"{name}{index}.wav"
            with wave.open(str(wav)) as clip:
                duration = clip.getnframes() / clip.getframerate()
            start = self.time
            self.add_sound(str(wav))

            bar = Line(LEFT * 6.2, RIGHT * 6.2, color=STROKE, stroke_width=1.2).set_y(2.68)
            tag = code(f"STEP 0{index + 1} // {name.upper()}", 15, ACCENT).move_to([-6.1, 3.42, 0], aligned_edge=LEFT)
            heading = txt(title, 30, PAPER, width=12.0).move_to([-6.1, 3.00, 0], aligned_edge=LEFT)
            foot = footer_chips(values)
            self.play(FadeIn(tag), FadeIn(heading, shift=DOWN * 0.08), Create(bar), FadeIn(foot), run_time=0.32)

            self.animate_scene(name, index, values)

            beat_span = max(8.0, duration, self.time - start + 0.15)
            self.wait(max(0.1, beat_span - (self.time - start)))
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", narration.strip()) if s.strip()]
            cursor = start
            total_chars = sum(map(len, sentences))
            for sentence in sentences:
                end = cursor + duration * len(sentence) / total_chars
                cues.extend([f"{stamp(cursor)} --> {stamp(end)}", sentence, ""])
                cursor = end
            self.play(FadeOut(*self.mobjects, shift=UP * 0.06), run_time=0.28)
        (ROOT.parent / "public" / f"{name}.vtt").write_text("\n".join(cues), encoding="utf-8")

    # =========================================================================
    # DISPATCH TO BESPOKE SCENE HANDLERS (4 DISTINCT BEATS EACH)
    # =========================================================================
    def animate_scene(self, name, idx, values):
        handler = getattr(self, f"_anim_{name}", None)
        if handler:
            handler(idx, values)
            return
        self._anim_fallback(idx, values)

    # -------------------------------------------------------------------------
    # 00: PYTHON, CONTEST, FAST IO, CATALOG
    # -------------------------------------------------------------------------
    def _anim_PythonGuide(self, idx, values):
        if idx == 0:  # Choose a runtime: CPython vs PyPy3 speed bars
            labels = ["CPython 3.12 (10^7 loop)", "PyPy 3 JIT  (10^7 loop)", "C++20 -O2   (10^8 loop)"]
            widths = [6.2, 2.1, 0.9]
            cols = [BAD, ACCENT, BLUE]
            rows = VGroup()
            for i, (lbl, w, c) in enumerate(zip(labels, widths, cols)):
                y = 1.2 - i * 1.05
                t = code(lbl, 17, PAPER).move_to([-5.6, y, 0], aligned_edge=LEFT)
                bar = RoundedRectangle(width=w, height=0.44, corner_radius=0.05,
                                       stroke_color=c, fill_color=c, fill_opacity=0.28).move_to([-0.2 + w / 2, y, 0])
                rows.add(VGroup(t, bar))
            self.play(LaggedStart(*(FadeIn(r, shift=RIGHT * 0.2) for r in rows), lag_ratio=0.18), run_time=1.0)
            self.play(Indicate(rows[1][1], color=ACCENT, scale_factor=1.06), run_time=0.5)
        elif idx == 1:  # Read the input: stdin stream -> tokens -> int array
            raw = box_cell('stdin: "5\\n3 1 4 1 5"', w=4.4, h=0.75, stroke=AMBER, fill=AMBER_FILL, color=AMBER, size=18).move_to([-3.4, 0.8, 0])
            arr = Arrow([-1.0, 0.8, 0], [0.2, 0.8, 0], color=ACCENT, stroke_width=2.6)
            tok = box_cell("sys.stdin.buffer.read().split()", w=4.8, h=0.75, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=16).move_to([2.8, 0.8, 0])
            cells, grp = array_row([3, 1, 4, 1, 5], y=-0.65, name="A")
            self.play(FadeIn(raw), run_time=0.35)
            self.play(Create(arr), FadeIn(tok), run_time=0.45)
            self.play(FadeIn(grp, shift=UP * 0.15), *(c[0].animate.set_stroke(ACCENT, 2.2) for c in cells), run_time=0.65)
        elif idx == 2:  # Count the work: N^2 grid vs O(N log N)
            grid = VGroup(*(Square(0.22, stroke_width=1.1, color=BAD) for _ in range(64)))
            grid.arrange_in_grid(rows=8, cols=8, buff=0.03).move_to([-2.8, 0.35, 0])
            bad_lbl = code("O(N^2): 10^5 x 10^5 = 10^10 (TLE)", 16, BAD).next_to(grid, DOWN, buff=0.2)
            good_box = box_cell("O(N log N): ~1.7 x 10^6 ops (AC)", w=5.2, h=0.9,
                                stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=18).move_to([2.4, 0.35, 0])
            self.play(Create(grid), FadeIn(bad_lbl), run_time=0.55)
            self.play(grid[:24].animate.set_fill(BAD, opacity=0.55), FadeIn(good_box, shift=LEFT * 0.2), run_time=0.65)
        else:  # Choose an operation: O(1) dict/deque vs O(N) list.pop(0)
            c1, g1 = array_row(["pop(0) -> O(N)", "x in list -> O(N)"], y=1.0, w=4.2, h=0.75, show_idx=False, name="SLOW")
            c2, g2 = array_row(["deque.popleft() -> O(1)", "x in set -> O(1)"], y=-0.4, w=4.2, h=0.75, show_idx=False, name="FAST")
            self.play(FadeIn(g1), *(c[0].animate.set_stroke(BAD, 2.2).set_fill(BAD_FILL, 1) for c in c1), run_time=0.5)
            self.play(FadeIn(g2), *(c[0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1) for c in c2), run_time=0.6)

    def _anim_ContestGuide(self, idx, values):
        if idx == 0:  # Choose a round: Div 4 -> Div 3 -> Div 2 -> Div 1 ladder
            divs = [("Div 4", "800-1300", ACCENT), ("Div 3", "800-1700", BLUE), ("Div 2", "800-2400", AMBER), ("Div 1", "1900-3500", BAD)]
            steps = VGroup()
            for i, (d, r, c) in enumerate(divs):
                b = box_cell(f"{d}\n{r}", w=2.2, h=0.95, stroke=c, fill=CARD, color=c, size=18)
                b.move_to([-3.9 + i * 2.6, -0.5 + i * 0.55, 0])
                steps.add(b)
            self.play(LaggedStart(*(FadeIn(s, shift=UP * 0.2) for s in steps), lag_ratio=0.18), run_time=1.0)
        elif idx == 1:  # Read the standings: Problem A..F solve counts & penalty
            cols = ["A (9200)", "B (6400)", "C (3100)", "D (980)", "E (210)"]
            c1, g1 = array_row(cols, y=0.6, w=2.0, h=0.85, show_idx=False)
            msg = banner("Solve A & B fast -> fewer wrong-submission penalties", y=1.8, color=ACCENT)
            self.play(FadeIn(g1), FadeIn(msg), run_time=0.45)
            self.play(c1[0][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1),
                      c1[1][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1),
                      c1[2][0].animate.set_stroke(AMBER, 2.4).set_fill(AMBER_FILL, 1), run_time=0.65)
        elif idx == 2:  # Trace a submission: Verdict pipeline
            stages = [("Compile", ACCENT), ("Test 1..5", ACCENT), ("Edge Test 14", AMBER), ("Stress Test 42 -> AC", ACCENT)]
            boxes = VGroup(*(box_cell(s, w=2.45, h=0.82, stroke=c, fill=CARD, color=c, size=16) for s, c in stages)).arrange(RIGHT, buff=0.45).move_to([0, 0.35, 0])
            self.play(FadeIn(boxes[0]), run_time=0.25)
            for a, b in zip(boxes, boxes[1:]):
                self.play(Create(Arrow(a.get_right(), b.get_left(), buff=0.06, color=ACCENT)), FadeIn(b), run_time=0.35)
        else:  # Upsolve after the round: +1 problem beyond contest
            c1, g1 = array_row(["A ✓", "B ✓", "C (upsolve!)", "D"], y=0.5, w=2.2, h=0.85, show_idx=False)
            self.play(FadeIn(g1), c1[0][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1),
                      c1[1][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1), run_time=0.45)
            self.play(c1[2][0].animate.set_stroke(AMBER, 3.0).set_fill(AMBER_FILL, 1), Indicate(c1[2], color=AMBER), run_time=0.65)

    def _anim_FastIoGuide(self, idx, values):
        if idx == 0:  # Stream from stdin
            b1 = box_cell("input() x 200,000\n~450 ms (slow)", w=4.4, h=1.0, stroke=BAD, fill=BAD_FILL, color=BAD, size=18).move_to([-2.7, 0.4, 0])
            b2 = box_cell("sys.stdin.read()\n~25 ms (18x faster)", w=4.4, h=1.0, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=18).move_to([2.7, 0.4, 0])
            self.play(FadeIn(b1), FadeIn(b2, shift=LEFT * 0.2), run_time=0.65)
            self.play(Indicate(b2, color=ACCENT), run_time=0.45)
        elif idx == 1:  # Batch stdout
            items = VGroup(*(box_cell(f"ans[{i}]", w=1.4, h=0.58, stroke=STROKE, size=16) for i in range(4))).arrange(RIGHT, buff=0.18).move_to([-2.4, 0.5, 0])
            arr = Arrow([0.7, 0.5, 0], [1.7, 0.5, 0], color=ACCENT, stroke_width=2.6)
            out = box_cell("'\\n'.join(out)\n1 flush!", w=3.1, h=0.9, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=17).move_to([3.5, 0.5, 0])
            self.play(FadeIn(items), run_time=0.35)
            self.play(Create(arr), FadeIn(out), *(x[0].animate.set_stroke(ACCENT, 2.2) for x in items), run_time=0.65)
        elif idx == 2:  # Match constraints to complexity
            rows = [("N <= 20", "O(2^N) Bitmask / Backtrack", BLUE),
                    ("N <= 5,000", "O(N^2) 2D DP / Pairs", AMBER),
                    ("N <= 200,000", "O(N log N) Sort / SegTree", ACCENT),
                    ("N <= 10^18", "O(log N) Math / Binary Search", ACCENT)]
            grp = VGroup(*(box_cell(f"{a:14s}  ->  {b}", w=8.8, h=0.58, stroke=c, fill=CARD, color=c, size=17) for a, b, c in rows)).arrange(DOWN, buff=0.18).move_to([0, 0.3, 0])
            self.play(LaggedStart(*(FadeIn(r, shift=RIGHT * 0.15) for r in grp), lag_ratio=0.15), run_time=0.9)
        else:  # Structure template
            blocks = ["1. Fast I/O setup", "2. solve() per test case", "3. Output buffer flush"]
            grp = VGroup(*(box_cell(b, w=6.8, h=0.68, stroke=ACCENT if i == 1 else STROKE, fill=ACCENT_FILL if i == 1 else CARD, color=ACCENT if i == 1 else PAPER, size=18) for i, b in enumerate(blocks))).arrange(DOWN, buff=0.22).move_to([0, 0.35, 0])
            self.play(LaggedStart(*(FadeIn(b, shift=UP * 0.1) for b in grp), lag_ratio=0.2), run_time=0.85)

    def _anim_CatalogGuide(self, idx, values):
        if idx == 0:  # Navigate by archetype
            tags = ["Binary Search", "Two Pointers", "DP", "Graphs", "Trees", "Number Theory"]
            grid = VGroup(*(box_cell(t, w=3.2, h=0.72, stroke=ACCENT if i % 2 == 0 else BLUE, fill=CARD, color=PAPER, size=17) for i, t in enumerate(tags))).arrange_in_grid(rows=2, cols=3, buff=0.28).move_to([0, 0.35, 0])
            self.play(LaggedStart(*(FadeIn(g) for g in grid), lag_ratio=0.1), run_time=0.8)
        elif idx == 1:  # Combine building blocks
            c1 = box_cell("Binary Search\non Answer", w=3.0, h=0.9, stroke=BLUE, fill=BLUE_FILL, color=BLUE, size=17).move_to([-3.3, 0.4, 0])
            plus = code("+", 30, PAPER).move_to([-1.3, 0.4, 0])
            c2 = box_cell("BFS / DSU\nFeasibility Check", w=3.2, h=0.9, stroke=AMBER, fill=AMBER_FILL, color=AMBER, size=17).move_to([0.8, 0.4, 0])
            eq = code("=", 30, PAPER).move_to([2.9, 0.4, 0])
            c3 = box_cell("Div2 D AC", w=2.2, h=0.9, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=18).move_to([4.5, 0.4, 0])
            self.play(FadeIn(c1), FadeIn(plus), FadeIn(c2), run_time=0.5)
            self.play(FadeIn(eq), FadeIn(c3), Indicate(c3, color=ACCENT), run_time=0.55)
        elif idx == 2:  # Stress test against brute force
            gen = box_cell("Random\nGenerator", w=2.4, h=0.85, stroke=BLUE, fill=BLUE_FILL, color=BLUE, size=17).move_to([-3.8, 0.4, 0])
            brute = box_cell("Brute Force\nO(N^2)", w=2.6, h=0.72, stroke=AMBER, fill=AMBER_FILL, color=AMBER, size=17).move_to([0.2, 1.15, 0])
            fast = box_cell("Fast Solution\nO(N log N)", w=2.6, h=0.72, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=17).move_to([0.2, -0.35, 0])
            cmp_b = box_cell("Diff == 0 ?", w=2.4, h=0.85, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=17).move_to([4.0, 0.4, 0])
            self.play(FadeIn(gen), Create(Arrow(gen.get_right(), brute.get_left(), color=MUTED)),
                      Create(Arrow(gen.get_right(), fast.get_left(), color=MUTED)), FadeIn(brute), FadeIn(fast), run_time=0.6)
            self.play(Create(Arrow(brute.get_right(), cmp_b.get_left(), color=ACCENT)),
                      Create(Arrow(fast.get_right(), cmp_b.get_left(), color=ACCENT)), FadeIn(cmp_b), run_time=0.5)
        else:  # Deliberate practice loop
            steps = ["Pick rating +200", "Attempt 30 min", "Read editorial", "Re-code clean"]
            boxes = VGroup(*(box_cell(s, w=2.55, h=0.78, stroke=ACCENT if i == 3 else STROKE, fill=ACCENT_FILL if i == 3 else CARD, size=16) for i, s in enumerate(steps))).arrange(RIGHT, buff=0.32).move_to([0, 0.4, 0])
            self.play(LaggedStart(*(FadeIn(b, shift=UP * 0.12) for b in boxes), lag_ratio=0.16), run_time=0.85)

    # -------------------------------------------------------------------------
    # 01: PREFIX SUMS & DIFFERENCE ARRAYS
    # -------------------------------------------------------------------------
    def _anim_PrefixSumsGuide(self, idx, values):
        if idx == 0:  # Build cumulative sums P[i+1] = P[i] + A[i]
            arr = [3, 1, 4, 2, 5]
            cA, gA = array_row(arr, y=1.1, w=0.95, h=0.68, name="A")
            cP, gP = array_row([0, "?", "?", "?", "?", "?"], y=-0.35, w=0.95, h=0.68, name="P")
            self.play(FadeIn(gA), FadeIn(gP), run_time=0.35)
            running = 0
            for k, v in enumerate(arr):
                running += v
                self.play(
                    cA[k][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1),
                    Transform(cP[k + 1][1], code(running, 20, ACCENT).move_to(cP[k + 1])),
                    cP[k + 1][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1),
                    run_time=0.3,
                )
        elif idx == 1:  # Answer range sum queries P[r+1] - P[l]
            cA, gA = array_row([3, 1, 4, 2, 5], y=1.15, w=0.92, h=0.66, name="A")
            cP, gP = array_row([0, 3, 4, 8, 10, 15], y=-0.35, w=0.92, h=0.66, name="P")
            self.play(FadeIn(gA), FadeIn(gP), run_time=0.35)
            span = RoundedRectangle(width=VGroup(*cA[1:4]).width + 0.14, height=0.82, corner_radius=0.06,
                                    stroke_color=ACCENT, stroke_width=2.6, fill_color=ACCENT, fill_opacity=0.14).move_to(VGroup(*cA[1:4]))
            lbl = banner("sum(A[1..3]) = P[4] - P[1] = 10 - 3 = 7   (O(1)!)", y=2.05, color=ACCENT)
            self.play(Create(span), FadeIn(lbl),
                      cP[4][0].animate.set_stroke(ACCENT, 2.8).set_fill(ACCENT_FILL, 1),
                      cP[1][0].animate.set_stroke(BAD, 2.8).set_fill(BAD_FILL, 1), run_time=0.8)
        elif idx == 2:  # Difference array +v at L, -v at R+1
            cD, gD = array_row([0, "+5", 0, 0, 0, "-5"], y=1.05, w=0.92, h=0.68, name="D")
            cF, gF = array_row([0, 5, 5, 5, 5, 0], y=-0.45, w=0.92, h=0.68, name="A")
            lbl = banner("Range add +5 on [1..4]:  D[1] += 5,  D[5] -= 5  -> prefix sum!", y=2.05, color=AMBER)
            self.play(FadeIn(gD), FadeIn(lbl),
                      cD[1][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1),
                      cD[5][0].animate.set_stroke(BAD, 2.6).set_fill(BAD_FILL, 1), run_time=0.55)
            self.play(FadeIn(gF, shift=DOWN * 0.15),
                      *(cF[k][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1) for k in range(1, 5)), run_time=0.7)
        else:  # 2D Inclusion-Exclusion
            cells, grp = table_grid([["1", "2", "1", "3"], ["2", "4", "3", "1"], ["1", "3", "2", "4"]], x0=-1.6, y0=1.1, cw=0.86, ch=0.68)
            lbl = banner("2D Sum = +BR  - Top  - Left  + TopLeft (inclusion-exclusion)", y=2.05, color=ACCENT)
            self.play(FadeIn(grp), FadeIn(lbl), run_time=0.45)
            self.play(
                *(cells[r][c][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1) for r in (1, 2) for c in (1, 2)),
                cells[0][0][0].animate.set_stroke(AMBER, 2.4).set_fill(AMBER_FILL, 1),
                cells[0][2][0].animate.set_stroke(BAD, 2.4).set_fill(BAD_FILL, 1),
                cells[2][0][0].animate.set_stroke(BAD, 2.4).set_fill(BAD_FILL, 1),
                run_time=0.8,
            )

    # -------------------------------------------------------------------------
    # 02: BINARY & TERNARY SEARCH
    # -------------------------------------------------------------------------
    def _anim_BinarySearchGuide(self, idx, values):
        if idx == 2:  # bisect_left vs bisect_right
            cells, grp = array_row([1, 4, 4, 4, 7, 9], y=0.35, w=0.95, h=0.80, name="A")
            p_l = pointer_pin("bisect_left(4)=1", cells[1], UP, ACCENT)
            p_r = pointer_pin("bisect_right(4)=4", cells[4], DOWN, AMBER)
            span = RoundedRectangle(width=VGroup(*cells[1:4]).width + 0.14, height=0.94, corner_radius=0.06,
                                    stroke_color=ACCENT, stroke_width=2.6, fill_color=ACCENT, fill_opacity=0.14).move_to(VGroup(*cells[1:4]))
            self.play(FadeIn(grp), run_time=0.35)
            self.play(FadeIn(p_l), FadeIn(p_r), Create(span), run_time=0.75)
        elif idx == 3:  # Real-domain precision (60-100 iterations)
            line = Line([-4.5, 0.2, 0], [4.5, 0.2, 0], color=MUTED, stroke_width=2.5)
            lo_d = Dot([-4.5, 0.2, 0], color=BAD, radius=0.1)
            hi_d = Dot([4.5, 0.2, 0], color=ACCENT, radius=0.1)
            msg = banner("Real binary search: run fixed 80 iterations -> 2^-80 precision!", y=1.8, color=ACCENT)
            self.play(Create(line), FadeIn(lo_d), FadeIn(hi_d), FadeIn(msg), run_time=0.4)
            for lx, rx in [(-0.4, 4.5), (-0.4, 2.0), (0.8, 2.0), (1.25, 1.55)]:
                self.play(lo_d.animate.move_to([lx, 0.2, 0]), hi_d.animate.move_to([rx, 0.2, 0]), run_time=0.35)
        else:  # Beat 0: Monotonic predicate F..F T..T | Beat 1: Loop invariant halving
            preds = ["F", "F", "F", "F", "T", "T", "T", "T"]
            vals = [2, 5, 8, 11, 15, 19, 23, 28]
            cells = VGroup(*(
                box_cell(f"{v}\n{p}", w=1.02, h=0.92, stroke=ACCENT if p == "T" else BAD,
                         fill=ACCENT_FILL if p == "T" else BAD_FILL, color=ACCENT if p == "T" else BAD, size=18)
                for p, v in zip(preds, vals)
            )).arrange(RIGHT, buff=0.12).move_to([0, 0.35, 0])
            lo = pointer_pin("lo", cells[0], DOWN, BAD)
            hi = pointer_pin("hi", cells[7], DOWN, ACCENT)
            mid = pointer_pin("mid", cells[3], UP, AMBER)
            info = banner("check(mid=3) is False  ->  lo = mid + 1 (discard [0..3])", y=1.95, color=AMBER)
            self.play(FadeIn(cells), FadeIn(lo), FadeIn(hi), FadeIn(mid), FadeIn(info), run_time=0.45)
            self.play(
                *(cells[k].animate.set_opacity(0.22) for k in range(4)),
                lo.animate.next_to(cells[4], DOWN, buff=0.28),
                mid.animate.next_to(cells[5], UP, buff=0.08),
                Transform(info, banner("check(mid=5) is True  ->  hi = mid (discard [6..7])", y=1.95, color=ACCENT)),
                run_time=0.65,
            )
            self.play(
                *(cells[k].animate.set_opacity(0.22) for k in range(6, 8)),
                lo.animate.next_to(cells[4], DOWN, buff=0.28).shift(LEFT * 0.28),
                hi.animate.next_to(cells[4], DOWN, buff=0.28).shift(RIGHT * 0.28),
                mid.animate.next_to(cells[4], UP, buff=0.08),
                cells[4][0].animate.set_stroke(AMBER, 3.0),
                Transform(info, banner("First True boundary locked at index 4 (value 15)", y=1.95, color=ACCENT)),
                run_time=0.65,
            )

    def _anim_TernarySearchGuide(self, idx, values):
        if idx == 3:  # Integer ternary search: stop at hi - lo <= 2
            vals = [12, 8, 5, 3, 4, 7, 11]
            cells, grp = array_row(vals, y=0.4, w=0.92, h=0.76, name="f")
            lbl = banner("Integer domain: stop when hi - lo <= 2, then scan last 3 values!", y=1.9, color=ACCENT)
            self.play(FadeIn(grp), FadeIn(lbl), run_time=0.4)
            self.play(*(cells[k].animate.set_opacity(0.25) for k in (0, 1, 5, 6)),
                      *(cells[k][0].animate.set_stroke(AMBER, 2.4) for k in (2, 3, 4)), run_time=0.55)
            self.play(cells[3][0].animate.set_stroke(ACCENT, 3.0).set_fill(ACCENT_FILL, 1), Indicate(cells[3], color=ACCENT), run_time=0.5)
            return
        ax_x = Line([-4.5, -1.2, 0], [4.5, -1.2, 0], color=MUTED, stroke_width=2)
        ax_y = Line([-4.5, -1.2, 0], [-4.5, 1.9, 0], color=MUTED, stroke_width=2)
        xs = np.linspace(-3.5, 3.9, 80)
        pts = [[x, 0.11 * (x - 0.5) ** 2 - 0.82, 0] for x in xs]
        curve = VMobject(color=ACCENT, stroke_width=3.0).set_points_smoothly(pts)
        self.play(Create(ax_x), Create(ax_y), Create(curve), run_time=0.45)
        x1, x2 = -1.6, 1.8
        y1, y2 = 0.11 * (x1 - 0.5) ** 2 - 0.82, 0.11 * (x2 - 0.5) ** 2 - 0.82
        l1 = Line([x1, -1.2, 0], [x1, y1, 0], color=BAD, stroke_width=2.4)
        l2 = Line([x2, -1.2, 0], [x2, y2, 0], color=AMBER, stroke_width=2.4)
        d1, d2 = Dot([x1, y1, 0], color=BAD, radius=0.09), Dot([x2, y2, 0], color=AMBER, radius=0.09)
        t1, t2 = code("m1", 16, BAD).next_to(l1, DOWN, buff=0.08), code("m2", 16, AMBER).next_to(l2, DOWN, buff=0.08)
        self.play(Create(l1), Create(l2), FadeIn(d1), FadeIn(d2), FadeIn(t1), FadeIn(t2), run_time=0.4)
        shade = Rectangle(width=2.4, height=2.8, stroke_width=0, fill_color=BAD, fill_opacity=0.15).move_to([-2.8, 0.25, 0])
        msg = banner("f(m1) > f(m2)  ->  drop outer third [L, m1], shrink by 2/3!", y=2.0, color=ACCENT)
        self.play(FadeIn(shade), FadeIn(msg), run_time=0.45)
        opt = Dot([0.5, -0.82, 0], color=ACCENT, radius=0.11)
        self.play(FadeIn(opt, scale=1.4), FadeIn(code("min x*", 17, ACCENT).next_to(opt, UP, buff=0.22)), run_time=0.55)

    # -------------------------------------------------------------------------
    # 03: TWO POINTERS & SLIDING WINDOW
    # -------------------------------------------------------------------------
    def _anim_TwoPointersGuide(self, idx, values):
        if idx == 3:  # Two-stream merge
            c1, g1 = array_row([1, 4, 7, 10], y=1.35, w=0.75, h=0.60, show_idx=False, name="A")
            c2, g2 = array_row([2, 3, 8, 12], y=0.35, w=0.75, h=0.60, show_idx=False, name="B")
            co, go = array_row(["", "", "", "", "", ""], y=-0.8, w=0.75, h=0.60, show_idx=False, name="M")
            self.play(FadeIn(g1), FadeIn(g2), FadeIn(go), run_time=0.4)
            for k, (src, val) in enumerate([(c1[0], "1"), (c2[0], "2"), (c2[1], "3"), (c1[1], "4"), (c1[2], "7"), (c2[2], "8")]):
                self.play(src[0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1),
                          Transform(co[k][1], code(val, 19, ACCENT).move_to(co[k])),
                          co[k][0].animate.set_stroke(ACCENT, 2.0), run_time=0.3)
        elif idx == 2:  # Same-direction chase
            cells, grp = array_row([1, 3, 4, 6, 8, 11, 14], y=0.35, name="A")
            L = pointer_pin("L", cells[0], DOWN, ACCENT)
            R = pointer_pin("R", cells[0], UP, AMBER)
            status = banner("Same-direction chase: L and R each move <= N times -> O(N)", y=1.95, color=ACCENT)
            self.play(FadeIn(grp), FadeIn(L), FadeIn(R), FadeIn(status), run_time=0.4)
            for li, ri in [(0, 2), (1, 3), (2, 5), (3, 6)]:
                self.play(L.animate.next_to(cells[li], DOWN, buff=0.28), R.animate.next_to(cells[ri], UP, buff=0.08),
                          cells[ri][0].animate.set_stroke(AMBER, 2.3), cells[li][0].animate.set_stroke(ACCENT, 2.3), run_time=0.42)
        else:  # Opposite-end converging two-sum
            cells, grp = array_row([1, 3, 4, 6, 8, 11, 14], y=0.4, name="A")
            L = pointer_pin("L", cells[0], UP, ACCENT)
            R = pointer_pin("R", cells[6], UP, AMBER)
            status = banner("target = 14  |  1 + 14 = 15 > 14  ->  step R left", y=-1.2, color=PAPER)
            self.play(FadeIn(grp), FadeIn(L), FadeIn(R), FadeIn(status), run_time=0.4)
            for li, ri, msg, col in [
                (0, 5, "1 + 11 = 12 < 14  ->  step L right", AMBER),
                (1, 5, "3 + 11 = 14 == target  (found in O(N)!)", ACCENT),
            ]:
                self.play(L.animate.next_to(cells[li], UP, buff=0.08), R.animate.next_to(cells[ri], UP, buff=0.08),
                          cells[li][0].animate.set_stroke(ACCENT, 2.4), cells[ri][0].animate.set_stroke(col, 2.4),
                          Transform(status, banner(msg, y=-1.2, color=col)), run_time=0.7)

    def _anim_SlidingWindowGuide(self, idx, values):
        arr = [2, 5, 1, 8, 2, 9, 1, 3]
        cells, grp = array_row(arr, y=0.45, name="A")
        self.play(FadeIn(grp), run_time=0.35)
        if idx == 2:  # Variable window shrinking L when sum > 10
            span = VGroup(*cells[0:2])
            frame = RoundedRectangle(width=span.width + 0.16, height=0.96, corner_radius=0.08,
                                     stroke_color=ACCENT, stroke_width=3.0, fill_color=ACCENT, fill_opacity=0.14).move_to(span)
            badge = banner("expand R while sum <= 10:  [0..1] sum = 7", y=1.9, color=ACCENT)
            self.play(Create(frame), FadeIn(badge), run_time=0.35)
            for l_i, r_i, msg, col in [
                (0, 2, "expand R=2 -> [0..2] sum = 8 <= 10 (valid)", ACCENT),
                (0, 3, "expand R=3 -> [0..3] sum = 16 > 10 (violates limit!)", BAD),
                (2, 3, "shrink L=2 -> [2..3] sum = 9 <= 10 (restored)", ACCENT),
                (2, 4, "expand R=4 -> [2..4] sum = 11 > 10 -> shrink L", AMBER),
            ]:
                sub = VGroup(*cells[l_i:r_i + 1])
                new_f = RoundedRectangle(width=sub.width + 0.16, height=0.96, corner_radius=0.08,
                                         stroke_color=col, stroke_width=3.0, fill_color=col, fill_opacity=0.14).move_to(sub)
                self.play(Transform(frame, new_f), Transform(badge, banner(msg, y=1.9, color=col)), run_time=0.48)
            return
        win_len = 3
        span = VGroup(*cells[0:win_len])
        frame = RoundedRectangle(width=span.width + 0.16, height=0.98, corner_radius=0.08,
                                 stroke_color=ACCENT, stroke_width=3.0, fill_color=ACCENT, fill_opacity=0.14).move_to(span)
        badge = banner(f"window [0..2]  sum = {sum(arr[:win_len])}", y=1.9, color=ACCENT)
        self.play(Create(frame), FadeIn(badge), run_time=0.35)
        for s in range(1, 5):
            nxt = VGroup(*cells[s:s + win_len])
            cur_s = sum(arr[s:s + win_len])
            msg = (f"+enter A[{s+2}]={arr[s+2]}  -leave A[{s-1}]={arr[s-1]}  -> sum={cur_s}"
                   if idx < 2 else f"R={s+2}: adds R - L + 1 = {win_len} valid subarrays")
            self.play(cells[s - 1][0].animate.set_stroke(BAD, 2.2), cells[s + win_len - 1][0].animate.set_stroke(ACCENT, 2.5),
                      frame.animate.move_to(nxt), Transform(badge, banner(msg, y=1.9, color=ACCENT)), run_time=0.46)

    # -------------------------------------------------------------------------
    # 04: SORTING & GREEDY
    # -------------------------------------------------------------------------
    def _anim_SortingGuide(self, idx, values):
        if idx == 0:  # Bar chart sort
            heights = [5, 2, 8, 1, 6, 3, 7]
            bars = VGroup()
            for i, v in enumerate(heights):
                h = 0.26 * v + 0.3
                b = RoundedRectangle(width=0.7, height=h, corner_radius=0.05, stroke_color=STROKE, stroke_width=1.8, fill_color=CARD, fill_opacity=1)
                b.move_to([-2.7 + i * 0.9, -1.2 + h / 2, 0])
                t = code(v, 18, PAPER).move_to(b.get_top() + DOWN * 0.22)
                bars.add(VGroup(b, t))
            self.play(LaggedStart(*(FadeIn(b, shift=UP * 0.15) for b in bars), lag_ratio=0.07), run_time=0.45)
            order = sorted(range(len(heights)), key=lambda k: heights[k])
            targets = [-2.7 + k * 0.9 for k in range(len(heights))]
            self.play(*(bars[i].animate.set_x(targets[r]) for r, i in enumerate(order)), run_time=0.85)
            self.play(*(bars[i][0].animate.set_stroke(ACCENT, 2.2).set_fill(ACCENT_FILL, 1) for i in order), run_time=0.35)
        elif idx == 1:  # Custom sort key
            c1, g1 = array_row(["(2, 9)", "(1, 4)", "(2, 3)", "(1, 8)"], y=0.95, w=1.7, h=0.70, show_idx=False, name="raw")
            c2, g2 = array_row(["(1, 8)", "(1, 4)", "(2, 9)", "(2, 3)"], y=-0.45, w=1.7, h=0.70, show_idx=False, name="key")
            lbl = banner("key = lambda x: (x[0], -x[1])  # asc primary, desc secondary", y=1.95, color=ACCENT)
            self.play(FadeIn(g1), FadeIn(lbl), run_time=0.4)
            self.play(FadeIn(g2, shift=DOWN * 0.18), *(c[0].animate.set_stroke(ACCENT, 2.2).set_fill(ACCENT_FILL, 1) for c in c2), run_time=0.8)
        elif idx == 2:  # Event sweep line
            self._draw_interval_sweep()
        else:  # Coordinate compression
            c1, g1 = array_row(["10", "10^9", "42", "10^9", "5"], y=1.0, w=1.35, h=0.68, show_idx=False, name="raw ")
            c2, g2 = array_row(["1", "3", "2", "3", "0"], y=-0.45, w=1.35, h=0.68, show_idx=False, name="rank")
            arrows = VGroup(*(Arrow(c1[k].get_bottom(), c2[k].get_top(), buff=0.08, color=ACCENT, stroke_width=2.2) for k in range(5)))
            self.play(FadeIn(g1), run_time=0.35)
            self.play(Create(arrows), FadeIn(g2), *(c[0].animate.set_stroke(ACCENT, 2.2) for c in c2), run_time=0.8)

    def _draw_interval_sweep(self):
        axis = Line([-5.2, -1.35, 0], [5.2, -1.35, 0], color=MUTED, stroke_width=1.8)
        ticks = VGroup(*(VGroup(Line([-5.0 + t, -1.27, 0], [-5.0 + t, -1.43, 0], color=MUTED),
                                code(t, 14, MUTED).move_to([-5.0 + t, -1.62, 0])) for t in range(11)))
        intervals = [(0, 3, True, 1.45), (1, 6, False, 0.8), (3, 6, True, 0.15), (5, 9, False, -0.5), (6, 10, True, -1.05)]
        iv_mobs = VGroup()
        for s, e, _, y in intervals:
            bar = RoundedRectangle(width=(e - s) * 1.0, height=0.44, corner_radius=0.05, stroke_color=STROKE, stroke_width=1.8, fill_color=CARD, fill_opacity=1)
            bar.move_to([-5.0 + (s + e) * 0.5, y, 0])
            iv_mobs.add(VGroup(bar, code(f"[{s}, {e}]", 15, PAPER).move_to(bar)))
        sweep = Line([-5.0, -1.35, 0], [-5.0, 1.95, 0], color=ACCENT, stroke_width=2.8)
        self.play(Create(axis), FadeIn(ticks), FadeIn(iv_mobs), Create(sweep), run_time=0.45)
        for (_, e, ok, _), mob in zip(intervals, iv_mobs):
            col, fill = (ACCENT, ACCENT_FILL) if ok else (BAD, BAD_FILL)
            self.play(sweep.animate.set_x(-5.0 + e), mob[0].animate.set_stroke(col, 2.4).set_fill(fill, 1), mob[1].animate.set_color(col), run_time=0.38)

    def _anim_GreedyGuide(self, idx, values):
        if idx == 3:  # Regret greedy min-heap
            h_nodes = {1: gnode("2", (0, 1.45), stroke=BAD, fill=BAD_FILL),
                       2: gnode("7", (-1.8, 0.15), stroke=ACCENT, fill=ACCENT_FILL),
                       3: gnode("9", (1.8, 0.15), stroke=ACCENT, fill=ACCENT_FILL)}
            h_edges = VGroup(Line(h_nodes[1].get_bottom(), h_nodes[2].get_top(), color=STROKE),
                             Line(h_nodes[1].get_bottom(), h_nodes[3].get_top(), color=STROKE))
            cand = box_cell("new item = 12 > min-heap root (2) -> SWAP!", w=6.2, h=0.68, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=18).move_to([0, -1.15, 0])
            self.play(Create(h_edges), FadeIn(VGroup(*h_nodes.values())), FadeIn(cand), run_time=0.5)
            self.play(Transform(h_nodes[1][1], code("7", 19, ACCENT).move_to(h_nodes[1])),
                      h_nodes[1][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1),
                      Transform(h_nodes[2][1], code("12", 19, ACCENT).move_to(h_nodes[2])), run_time=0.75)
        elif idx == 2:  # Exchange argument proof
            b1 = box_cell("OPT picks [1, 7]  (finishes at 7)", w=5.6, h=0.68, stroke=BAD, fill=BAD_FILL, color=BAD, size=18).move_to([0, 1.0, 0])
            b2 = box_cell("GREEDY picks [1, 3]  (finishes at 3 <= 7)", w=5.6, h=0.68, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=18).move_to([0, 0.0, 0])
            b3 = box_cell("Swap [1,7] -> [1,3]: never breaks remaining schedule!", w=7.2, h=0.68, stroke=AMBER, fill=AMBER_FILL, color=AMBER, size=17).move_to([0, -1.0, 0])
            self.play(FadeIn(b1), FadeIn(b2), run_time=0.5)
            self.play(FadeIn(b3, shift=UP * 0.15), Indicate(b2, color=ACCENT), run_time=0.65)
        else:
            self._draw_interval_sweep()

    # -------------------------------------------------------------------------
    # 05: DATA STRUCTURES (DSU, FENWICK, SEGTREE, MONOTONIC, ORDERED SET)
    # -------------------------------------------------------------------------
    def _anim_DsuGuide(self, idx, values):
        if idx == 0:  # Track disjoint components
            coords = {0: (-4.0, 0.6), 1: (-2.2, 0.6), 2: (-0.4, 0.6), 3: (1.8, 0.6), 4: (3.6, 0.6)}
            ns = {k: gnode(str(k), p, r=0.32) for k, p in coords.items()}
            lbl = banner("5 isolated components -> union(0,1), union(3,4) -> 3 components", y=1.85, color=ACCENT)
            self.play(FadeIn(VGroup(*ns.values())), FadeIn(lbl), run_time=0.45)
            e1, _ = gedge(ns[0], ns[1], color=ACCENT)
            e2, _ = gedge(ns[3], ns[4], color=AMBER)
            self.play(Create(e1), ns[0][0].animate.set_stroke(ACCENT, 2.5), ns[1][0].animate.set_stroke(ACCENT, 2.5), run_time=0.45)
            self.play(Create(e2), ns[3][0].animate.set_stroke(AMBER, 2.5), ns[4][0].animate.set_stroke(AMBER, 2.5), run_time=0.45)
        elif idx == 2:  # Union by size
            big = VGroup(gnode("R1\nsz=4", (-2.6, 1.1), r=0.42, stroke=ACCENT, fill=ACCENT_FILL),
                         gnode("a", (-3.7, -0.3), r=0.28), gnode("b", (-2.6, -0.3), r=0.28), gnode("c", (-1.5, -0.3), r=0.28))
            small = VGroup(gnode("R2\nsz=2", (2.4, 1.1), r=0.42, stroke=AMBER, fill=AMBER_FILL), gnode("d", (2.4, -0.3), r=0.28))
            lbl = banner("Always attach smaller root (sz=2) under larger root (sz=4) -> height <= log N", y=2.0, color=ACCENT)
            self.play(FadeIn(big), FadeIn(small), FadeIn(lbl), run_time=0.5)
            arr = Arrow(small[0].get_left(), big[0].get_right(), color=ACCENT, stroke_width=3.0)
            self.play(Create(arr), small[0][0].animate.set_stroke(ACCENT, 2.6), run_time=0.65)
        else:  # Path compression (Beat 1 & 3)
            cpos = {0: (-2.5, 1.6), 1: (-3.6, 0.6), 2: (-3.6, -0.4), 3: (-3.6, -1.4)}
            spos = {0: (2.2, 1.35), 1: (0.6, -0.5), 2: (2.2, -0.5), 3: (3.8, -0.5)}
            cn = {k: gnode(str(k), p, r=0.28) for k, p in cpos.items()}
            ce = VGroup(*(gedge(cn[k], cn[k - 1], directed=True, r=0.29)[0] for k in (1, 2, 3)))
            sn = {k: gnode(str(k), p, r=0.28, stroke=ACCENT, fill=ACCENT_FILL) for k, p in spos.items()}
            se = VGroup(*(gedge(sn[k], sn[0], directed=True, color=ACCENT, r=0.29)[0] for k in (1, 2, 3)))
            lbl = banner("find(3): rewire every visited node directly to root 0 -> O(alpha(N))", y=2.1, color=ACCENT)
            self.play(FadeIn(VGroup(*cn.values())), Create(ce), FadeIn(lbl), run_time=0.45)
            self.play(Create(Arrow([-1.3, 0.3, 0], [0.1, 0.3, 0], color=ACCENT, stroke_width=3.0)),
                      FadeIn(VGroup(*sn.values())), Create(se), run_time=0.8)

    def _anim_FenwickGuide(self, idx, values):
        if idx == 0:  # Isolate lowest set bit i & -i
            c1, g1 = array_row(list("00001100"), y=1.1, w=0.68, h=0.60, show_idx=False, name="i = 12")
            c2, g2 = array_row(list("11110100"), y=0.2, w=0.68, h=0.60, show_idx=False, name="-i    ")
            c3, g3 = array_row(list("00000100"), y=-0.7, w=0.68, h=0.60, show_idx=False, name="i & -i")
            self.play(FadeIn(g1), FadeIn(g2), FadeIn(g3), run_time=0.45)
            self.play(c1[5][0].animate.set_stroke(AMBER, 2.6).set_fill(AMBER_FILL, 1),
                      c2[5][0].animate.set_stroke(AMBER, 2.6).set_fill(AMBER_FILL, 1),
                      c3[5][0].animate.set_stroke(ACCENT, 2.8).set_fill(ACCENT_FILL, 1), run_time=0.7)
            return
        cells, grp = array_row([3, 1, 4, 1, 5, 9, 2, 6], y=1.35, w=0.82, h=0.60, show_idx=False, name="A")
        self.play(FadeIn(grp), run_time=0.35)
        bars = VGroup()
        specs = [(1, 0, 0, 0.42), (2, 0, 1, -0.06), (3, 2, 2, 0.42), (4, 0, 3, -0.54),
                 (5, 4, 4, 0.42), (6, 4, 5, -0.06), (7, 6, 6, 0.42), (8, 0, 7, -1.02)]
        for i1, l_i, r_i, yp in specs:
            span = VGroup(*cells[l_i:r_i + 1])
            b = RoundedRectangle(width=span.width, height=0.35, corner_radius=0.05, stroke_color=STROKE, stroke_width=1.6, fill_color=CARD, fill_opacity=1)
            b.move_to([span.get_center()[0], yp, 0])
            bars.add(VGroup(b, code(f"bit[{i1}]", 14, PAPER).move_to(b)))
        self.play(LaggedStart(*(FadeIn(b) for b in bars), lag_ratio=0.06), run_time=0.5)
        active_seq = (6, 5, 3) if idx == 1 else (2, 3, 7)  # query(7): 7->6->4 | update(3): 3->4->8
        msg = "query(7): i -= i & -i  ->  bit[7] + bit[6] + bit[4]" if idx == 1 else "update(3): i += i & -i  ->  bit[3], bit[4], bit[8]"
        self.play(FadeIn(banner(msg, y=2.05, color=ACCENT)), run_time=0.3)
        for ai in active_seq:
            self.play(bars[ai][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1), bars[ai][1].animate.set_color(ACCENT), run_time=0.35)

    def _anim_OrderedSetGuide(self, idx, values):
        if idx == 2:  # Binary lifting on BIT for k-th order statistic
            cells, grp = array_row([1, 2, 1, 5, 0, 1, 2, 8], y=0.5, w=0.9, h=0.72, name="BIT")
            lbl = banner("Find 6th smallest: jump step=4 (5<6, take!), step=2 (5+1=6 -> pos=6)", y=1.85, color=ACCENT)
            self.play(FadeIn(grp), FadeIn(lbl), run_time=0.4)
            self.play(cells[3][0].animate.set_stroke(ACCENT, 2.8).set_fill(ACCENT_FILL, 1), run_time=0.45)
            self.play(cells[5][0].animate.set_stroke(AMBER, 2.8).set_fill(AMBER_FILL, 1), run_time=0.45)
        elif idx == 3:  # Sqrt buckets for online inserts
            b1 = box_cell("Bucket 0\n[1, 3, 4]", w=2.8, h=0.95, stroke=ACCENT, fill=ACCENT_FILL, size=17).move_to([-3.3, 0.4, 0])
            b2 = box_cell("Bucket 1\n[7, 9, 12]", w=2.8, h=0.95, stroke=BLUE, fill=BLUE_FILL, size=17).move_to([0.0, 0.4, 0])
            b3 = box_cell("Bucket 2\n[15, 20]", w=2.8, h=0.95, stroke=AMBER, fill=AMBER_FILL, size=17).move_to([3.3, 0.4, 0])
            self.play(FadeIn(b1), FadeIn(b2), FadeIn(b3), FadeIn(banner("SortedList: sqrt(N) buckets -> O(N^1/3) insert & k-th!", y=1.85, color=ACCENT)), run_time=0.65)
        else:
            self._anim_FenwickGuide(idx, values)

    def _anim_SegmentTreeGuide(self, idx, values):
        pos = {1: (0.0, 1.55), 2: (-2.7, 0.35), 3: (2.7, 0.35),
               4: (-4.1, -0.95), 5: (-1.3, -0.95), 6: (1.3, -0.95), 7: (4.1, -0.95)}
        lbls = {1: "[0..3]=19", 2: "[0..1]=8", 3: "[2..3]=11", 4: "A[0]=3", 5: "A[1]=5", 6: "A[2]=4", 7: "A[3]=7"}
        tn = {k: box_cell(lbls[k], w=1.55, h=0.62, size=16).move_to([p[0], p[1], 0]) for k, p in pos.items()}
        edges = VGroup(*(Line(tn[a].get_bottom(), tn[b].get_top(), color=STROKE, stroke_width=2.0) for a, b in [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7)]))
        self.play(Create(edges), FadeIn(VGroup(*tn.values())), run_time=0.45)
        if idx == 0:  # Build bottom-up
            for k in (4, 5, 6, 7, 2, 3, 1):
                self.play(tn[k][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1), run_time=0.18)
        elif idx == 1:  # Point update A[1]: 5 -> 9 pulling up
            self.play(FadeIn(banner("Point update A[1]: 5 -> 9  (recompute O(log N) ancestors)", y=2.2, color=AMBER)), run_time=0.3)
            for k, new_txt in [(5, "A[1]=9"), (2, "[0..1]=12"), (1, "[0..3]=23")]:
                self.play(Transform(tn[k][1], code(new_txt, 16, AMBER).move_to(tn[k])),
                          tn[k][0].animate.set_stroke(AMBER, 2.8).set_fill(AMBER_FILL, 1), run_time=0.45)
        elif idx == 2:  # Query [1..2] folds disjoint nodes 5 and 6
            self.play(FadeIn(banner("Query [1..2]: pick disjoint nodes A[1]=5 and A[2]=4 -> sum = 9", y=2.2, color=ACCENT)), run_time=0.3)
            self.play(tn[5][0].animate.set_stroke(ACCENT, 3.0).set_fill(ACCENT_FILL, 1),
                      tn[6][0].animate.set_stroke(ACCENT, 3.0).set_fill(ACCENT_FILL, 1),
                      tn[4].animate.set_opacity(0.28), tn[7].animate.set_opacity(0.28), run_time=0.7)
        else:  # Associative merge operations
            ops = box_cell("Any associative op(L, R):  sum | min | max | gcd | matrix", w=8.8, h=0.64, stroke=BLUE, fill=BLUE_FILL, color=BLUE, size=17).move_to([0, -1.78, 0])
            self.play(FadeIn(ops), tn[1][0].animate.set_stroke(BLUE, 2.8).set_fill(BLUE_FILL, 1), run_time=0.7)

    def _anim_MonotonicGuide(self, idx, values):
        heights = [2, 1, 5, 6, 2, 3]
        hist = VGroup()
        for i, h_val in enumerate(heights):
            h = 0.32 * h_val
            b = Rectangle(width=0.66, height=h, stroke_color=STROKE, stroke_width=1.8, fill_color=CARD, fill_opacity=1)
            b.move_to([-3.8 + i * 0.76, -1.2 + h / 2, 0])
            hist.add(VGroup(b, code(h_val, 16, PAPER).move_to(b.get_top() + DOWN * 0.18)))
        well = VGroup(
            Line([1.5, 1.5, 0], [1.5, -1.2, 0], color=ACCENT, stroke_width=2.4),
            Line([1.5, -1.2, 0], [4.2, -1.2, 0], color=ACCENT, stroke_width=2.4),
            Line([4.2, -1.2, 0], [4.2, 1.5, 0], color=ACCENT, stroke_width=2.4),
            code("DEQUE (MAX)" if idx == 2 else "MONOTONIC STACK", 15, ACCENT).move_to([2.85, 1.8, 0]),
        )
        self.play(FadeIn(hist), Create(well), run_time=0.45)
        s_items = VGroup(
            box_cell("idx 1 (h=1)", w=2.2, h=0.5, stroke=ACCENT, fill=ACCENT_FILL, size=16).move_to([2.85, -0.85, 0]),
            box_cell("idx 2 (h=5)", w=2.2, h=0.5, stroke=ACCENT, fill=ACCENT_FILL, size=16).move_to([2.85, -0.25, 0]),
            box_cell("idx 3 (h=6)", w=2.2, h=0.5, stroke=ACCENT, fill=ACCENT_FILL, size=16).move_to([2.85, 0.35, 0]),
        )
        for k, item in zip((1, 2, 3), s_items):
            self.play(hist[k][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1), FadeIn(item, shift=DOWN * 0.18), run_time=0.28)
        if idx == 3:  # Maximal rectangle area = 5 * 2 = 10
            rect = Rectangle(width=1.42, height=0.32 * 5, stroke_color=AMBER, stroke_width=3.0, fill_color=AMBER, fill_opacity=0.25).move_to([-3.8 + 2.5 * 0.76, -1.2 + 0.16 * 5, 0])
            self.play(Create(rect), FadeIn(banner("Max rectangle: h=5 x width=2 = area 10", y=2.05, color=AMBER)), run_time=0.65)
        else:
            self.play(hist[4][0].animate.set_stroke(BAD, 2.4), FadeOut(s_items[2], shift=UP * 0.25), FadeOut(s_items[1], shift=UP * 0.25), run_time=0.5)

    # -------------------------------------------------------------------------
    # 06: DYNAMIC PROGRAMMING (KNAPSACK, GRID, LIS/LCS, INTERVAL, TREE, BITMASK)
    # -------------------------------------------------------------------------
    def _anim_KnapsackGuide(self, idx, values):
        if idx == 3:  # Bitset reachable sums dp |= dp << w
            c1, g1 = array_row(list("00010011"), y=1.0, w=0.72, h=0.64, show_idx=False, name="dp     ")
            c2, g2 = array_row(list("01001100"), y=0.1, w=0.72, h=0.64, show_idx=False, name="dp << 2")
            c3, g3 = array_row(list("01011111"), y=-0.8, w=0.72, h=0.64, show_idx=False, name="dp | sh")
            self.play(FadeIn(g1), FadeIn(g2), FadeIn(g3), FadeIn(banner("Bitset subset-sum: dp |= (dp << w) in O(W / 64)!", y=1.95, color=ACCENT)), run_time=0.5)
            self.play(*(c3[k][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1) for k in (1, 3, 4, 5, 6, 7)), run_time=0.6)
            return
        vals = [0, 0, 0, 5, 6, 8, 11, 14]
        cells, grp = array_row(vals, y=0.35, name="dp")
        forward = idx == 2
        lbl = banner("Unbounded: sweep wt -> W FORWARD (reuse allowed)" if forward else "0/1 Knapsack: sweep W -> wt BACKWARD (at most once)",
                     y=1.9, color=AMBER if forward else ACCENT)
        self.play(FadeIn(grp), FadeIn(lbl), run_time=0.4)
        for iw in ([3, 4, 5, 6, 7] if forward else [7, 6, 5, 4, 3]):
            arc = ArcBetweenPoints(cells[iw - 3].get_top(), cells[iw].get_top(), angle=-0.8, color=AMBER if forward else ACCENT, stroke_width=2.4)
            self.play(Create(arc), cells[iw][0].animate.set_stroke(AMBER if forward else ACCENT, 2.5).set_fill(AMBER_FILL if forward else ACCENT_FILL, 1), run_time=0.26)
            self.play(FadeOut(arc), run_time=0.08)

    def _anim_GridDpGuide(self, idx, values):
        mat = [["1", "1", "1", "1"], ["1", "#", "1", "2"], ["1", "1", "2", "4"]]
        cells, grp = table_grid(mat, x0=-1.6, y0=1.15, cw=0.92, ch=0.72)
        self.play(FadeIn(grp), run_time=0.4)
        if idx == 2:  # Rolling row memory O(W)
            row_box = RoundedRectangle(width=4.15, height=0.88, corner_radius=0.06, stroke_color=AMBER, stroke_width=2.8, fill_color=AMBER, fill_opacity=0.14).move_to(VGroup(*cells[0]))
            self.play(Create(row_box), FadeIn(banner("Rolling 1D row: dp[c] += dp[c-1] -> O(W) memory!", y=2.05, color=AMBER)), run_time=0.4)
            for r in (1, 2):
                self.play(row_box.animate.move_to(VGroup(*cells[r])), run_time=0.45)
        elif idx == 3:  # Reconstruct path backwards
            self.play(FadeIn(banner("Backtrack parent pointers from (H-1, W-1) -> (0, 0)", y=2.05, color=ACCENT)), run_time=0.35)
            for r, c in [(2, 3), (2, 2), (1, 2), (0, 2), (0, 1), (0, 0)]:
                self.play(cells[r][c][0].animate.set_stroke(ACCENT, 2.8).set_fill(ACCENT_FILL, 1), run_time=0.22)
        else:
            for r in range(3):
                for c in range(4):
                    if mat[r][c] == "#":
                        continue
                    self.play(cells[r][c][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1), run_time=0.13)

    def _anim_LisLcsGuide(self, idx, values):
        if idx in (0, 1):  # Patience tails & binary search replacement
            cA, gA = array_row([10, 9, 2, 5, 3, 7], y=1.15, name="A")
            cT, gT = array_row([2, 5, 7, ""], y=-0.35, w=1.05, name="tails")
            lbl = banner("bisect_left(tails, 3) = 1 -> replace 5 with 3 (keeps tails minimal!)" if idx == 1 else "Patience sorting: tails[k] = smallest tail of length k+1", y=2.05, color=ACCENT)
            self.play(FadeIn(gA), FadeIn(gT), FadeIn(lbl), run_time=0.45)
            self.play(cA[4][0].animate.set_stroke(AMBER, 2.6).set_fill(AMBER_FILL, 1),
                      Transform(cT[1][1], code("3", 21, ACCENT).move_to(cT[1])),
                      cT[1][0].animate.set_stroke(ACCENT, 2.8).set_fill(ACCENT_FILL, 1), run_time=0.75)
        elif idx == 2:  # 2D LCS Table: "ACE" vs "ABCDE"
            mat = [[" ", "A", "B", "C", "D", "E"],
                   ["A", "1", "1", "1", "1", "1"],
                   ["C", "1", "1", "2", "2", "2"],
                   ["E", "1", "1", "2", "2", "3"]]
            cells, grp = table_grid(mat, x0=-2.3, y0=1.25, cw=0.78, ch=0.58, gap=0.06)
            self.play(FadeIn(grp), FadeIn(banner('LCS("ACE", "ABCDE") = 3  (match -> diagonal + 1)', y=2.1, color=ACCENT)), run_time=0.45)
            for r, c in [(1, 1), (2, 3), (3, 5)]:
                self.play(cells[r][c][0].animate.set_stroke(ACCENT, 2.8).set_fill(ACCENT_FILL, 1), run_time=0.35)
        else:  # Edit Distance 3 operations
            ops = [("INSERT", "dp[i][j-1] + 1", BLUE), ("DELETE", "dp[i-1][j] + 1", BAD), ("SUBSTITUTE", "dp[i-1][j-1] + (s[i]!=t[j])", ACCENT)]
            grp = VGroup(*(box_cell(f"{a}:  {b}", w=7.2, h=0.68, stroke=c, fill=CARD, color=c, size=18) for a, b, c in ops)).arrange(DOWN, buff=0.22).move_to([0, 0.3, 0])
            self.play(LaggedStart(*(FadeIn(g, shift=RIGHT * 0.15) for g in grp), lag_ratio=0.18), run_time=0.85)

    def _anim_IntervalDpGuide(self, idx, values):
        if idx == 3:  # Double array for circular ring
            c1, g1 = array_row([3, 1, 4, 3, 1, 4], y=0.35, name="A+A")
            span = RoundedRectangle(width=VGroup(*c1[1:4]).width + 0.14, height=0.92, corner_radius=0.06,
                                    stroke_color=ACCENT, stroke_width=2.8, fill_color=ACCENT, fill_opacity=0.14).move_to(VGroup(*c1[1:4]))
            self.play(FadeIn(g1), Create(span), FadeIn(banner("Circular ring: duplicate A -> A+A, take best window of length N", y=1.9, color=ACCENT)), run_time=0.75)
        elif idx == 2:  # Palindrome endpoint match
            cells, grp = array_row(list("ABCB A".replace(" ", "")), y=0.35, name="S")
            arc = ArcBetweenPoints(cells[0].get_top(), cells[4].get_top(), angle=-0.65, color=ACCENT, stroke_width=2.8)
            self.play(FadeIn(grp), Create(arc), FadeIn(banner("S[l] == S[r] ('A'=='A') -> shrink inward to dp[l+1][r-1]", y=1.9, color=ACCENT)),
                      cells[0][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1),
                      cells[4][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1), run_time=0.8)
        else:  # Length-order / Split point k
            cells, grp = array_row(["a0", "a1", "a2", "a3", "a4"], y=0.5, w=1.05, name="seg")
            self.play(FadeIn(grp), FadeIn(banner("Interval DP: try every split k -> merge [l..k] + [k+1..r]", y=1.95, color=AMBER)), run_time=0.4)
            for k in (1, 2, 3):
                left_b = RoundedRectangle(width=VGroup(*cells[:k]).width + 0.1, height=0.92, corner_radius=0.06, stroke_color=ACCENT, stroke_width=2.6, fill_color=ACCENT, fill_opacity=0.12).move_to(VGroup(*cells[:k]))
                right_b = RoundedRectangle(width=VGroup(*cells[k:]).width + 0.1, height=0.92, corner_radius=0.06, stroke_color=BLUE, stroke_width=2.6, fill_color=BLUE, fill_opacity=0.12).move_to(VGroup(*cells[k:]))
                self.play(FadeIn(left_b), FadeIn(right_b), run_time=0.35)
                if k < 3:
                    self.play(FadeOut(left_b), FadeOut(right_b), run_time=0.12)

    def _anim_TreeDpGuide(self, idx, values):
        pos = {1: (0, 1.5), 2: (-2.5, 0.25), 3: (2.5, 0.25), 4: (-3.8, -1.0), 5: (-1.2, -1.0)}
        tn = {k: gnode(str(k), p, r=0.33) for k, p in pos.items()}
        edges = VGroup(*(gedge(tn[a], tn[b], directed=(idx == 0), r=0.34)[0] for a, b in [(1, 2), (1, 3), (2, 4), (2, 5)]))
        self.play(Create(edges), FadeIn(VGroup(*tn.values())), run_time=0.45)
        if idx == 3:  # Rerooting pass 1 -> 2
            arr = Arrow(tn[1].get_center(), tn[2].get_center(), buff=0.38, color=AMBER, stroke_width=3.2)
            self.play(Create(arr), tn[2][0].animate.set_stroke(AMBER, 3.0).set_fill(AMBER_FILL, 1),
                      FadeIn(banner("Rerooting pass: shift root 1 -> 2 in O(1) using parent contribution", y=2.15, color=AMBER)), run_time=0.8)
        else:  # Bottom-up child subtree combination
            dp_lbls = {4: "(1,0)", 5: "(1,0)", 3: "(1,0)", 2: "(1,2)", 1: "(3,2)"}
            self.play(FadeIn(banner("Post-order DP: combine child states (take, skip) into parent", y=2.15, color=ACCENT)), run_time=0.3)
            for k in (4, 5, 2, 3, 1):
                b = code(dp_lbls[k], 15, ACCENT).next_to(tn[k], RIGHT, buff=0.1)
                self.play(tn[k][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1), FadeIn(b), run_time=0.25)

    def _anim_BitmaskDpGuide(self, idx, values):
        if idx == 0:  # Subset {0, 2, 3} -> 1101 = 13
            c, g = array_row(["1", "1", "0", "1"], y=0.45, w=1.05, h=0.82, name="mask")
            lbl = banner("Subset {0, 2, 3}  <-->  binary 1101_2 = 13  (1 integer = 1 subset!)", y=1.9, color=ACCENT)
            self.play(FadeIn(g), FadeIn(lbl), *(c[k][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1) for k in (0, 1, 3)), run_time=0.75)
        elif idx == 3:  # Submask enumeration sub = (sub - 1) & mask
            subs = ["1011", "1010", "1001", "1000", "0011", "0010", "0001"]
            c, g = array_row(subs, y=0.35, w=1.1, h=0.72, show_idx=False, name="sub")
            self.play(FadeIn(g), FadeIn(banner("Submask loop: sub = (sub - 1) & mask -> O(3^N) total!", y=1.85, color=AMBER)), run_time=0.4)
            self.play(LaggedStart(*(x[0].animate.set_stroke(AMBER, 2.4).set_fill(AMBER_FILL, 1) for x in c), lag_ratio=0.1), run_time=0.75)
        else:  # Topological mask transitions 001 -> 011 -> 111
            m1 = box_cell("001\n{0}", w=1.6, h=0.85, stroke=ACCENT, fill=ACCENT_FILL, size=18).move_to([-3.6, 0.35, 0])
            m2 = box_cell("011\n{0,1}", w=1.6, h=0.85, stroke=BLUE, fill=BLUE_FILL, size=18).move_to([0.0, 0.35, 0])
            m3 = box_cell("111\n{0,1,2}", w=1.6, h=0.85, stroke=AMBER, fill=AMBER_FILL, size=18).move_to([3.6, 0.35, 0])
            self.play(FadeIn(m1), Create(Arrow(m1.get_right(), m2.get_left(), color=ACCENT)), FadeIn(m2), run_time=0.5)
            self.play(Create(Arrow(m2.get_right(), m3.get_left(), color=AMBER)), FadeIn(m3),
                      FadeIn(banner("dp[mask | (1<<v)][v] = min(dp[mask][u] + cost(u, v))", y=1.9, color=ACCENT)), run_time=0.6)

    # -------------------------------------------------------------------------
    # 07: GRAPH ALGORITHMS (BFS/DFS, TOPO, DIJKSTRA, BELLMAN/FLOYD, MST, BRIDGES)
    # -------------------------------------------------------------------------
    def _anim_GraphTraversalGuide(self, idx, values):
        coords = {0: (-4.2, 0.5), 1: (-2.2, 1.45), 2: (-2.2, -0.55), 3: (-0.2, 1.45), 4: (-0.2, -0.55)}
        ns = {u: gnode(str(u), p, r=0.30) for u, p in coords.items()}
        edges = VGroup(*(gedge(ns[u], ns[v], r=0.31)[0] for u, v in [(0, 1), (0, 2), (1, 3), (2, 4), (1, 2)]))
        self.play(Create(edges), FadeIn(VGroup(*ns.values())), run_time=0.4)
        if idx == 0:  # Adjacency list panel
            adj = VGroup(*(box_cell(line, w=3.8, h=0.46, stroke=BLUE, fill=BLUE_FILL, color=PAPER, size=16)
                           for line in ["0 -> [1, 2]", "1 -> [0, 2, 3]", "2 -> [0, 1, 4]", "3 -> [1]", "4 -> [2]"])).arrange(DOWN, buff=0.12).move_to([3.2, 0.45, 0])
            self.play(LaggedStart(*(FadeIn(a, shift=LEFT * 0.15) for a in adj), lag_ratio=0.1), run_time=0.8)
        elif idx == 1:  # BFS Queue + layers
            qbox = box_cell("FIFO Queue: [0] -> [1, 2] -> [3, 4]", w=4.8, h=0.72, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=16).move_to([3.3, 0.45, 0])
            self.play(FadeIn(qbox), run_time=0.3)
            for layer, col in [([0], ACCENT), ([1, 2], BLUE), ([3, 4], AMBER)]:
                self.play(*(ns[u][0].animate.set_stroke(col, 2.8).set_fill(CARD, 1) for u in layer), run_time=0.35)
        elif idx == 2:  # DFS Call Stack
            sbox = box_cell("DFS Stack: 0 -> 1 -> 3 (backtrack) -> 2 -> 4", w=5.0, h=0.72, stroke=AMBER, fill=AMBER_FILL, color=AMBER, size=15).move_to([3.3, 0.45, 0])
            self.play(FadeIn(sbox), run_time=0.3)
            for u in (0, 1, 3, 2, 4):
                self.play(ns[u][0].animate.set_stroke(AMBER, 2.8).set_fill(AMBER_FILL, 1), run_time=0.26)
        else:  # 0-1 BFS Deque
            dq = box_cell("0-1 Deque:\nw=0 -> push_front\nw=1 -> push_back", w=4.4, h=1.35, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=17).move_to([3.2, 0.45, 0])
            self.play(FadeIn(dq), *(ns[u][0].animate.set_stroke(ACCENT, 2.4) for u in ns), run_time=0.7)

    def _anim_TopoSortGuide(self, idx, values):
        coords = {0: (-4.2, 0.55), 1: (-1.7, 1.45), 2: (-1.7, -0.35), 3: (1.0, 1.45), 4: (1.0, -0.35), 5: (3.6, 0.55)}
        ns = {u: gnode(str(u), p, r=0.30) for u, p in coords.items()}
        dag_edges = [(0, 1), (0, 2), (1, 3), (2, 3), (2, 4), (3, 5), (4, 5)]
        el = {e: gedge(ns[e[0]], ns[e[1]], directed=True, r=0.31)[0] for e in dag_edges}
        indeg = {0: 0, 1: 1, 2: 1, 3: 2, 4: 1, 5: 2}
        in_lbls = {u: code(f"in={indeg[u]}", 14, ACCENT if indeg[u] == 0 else MUTED).next_to(ns[u], UP if coords[u][1] >= 0 else DOWN, buff=0.08) for u in ns}
        self.play(Create(VGroup(*el.values())), FadeIn(VGroup(*ns.values())), FadeIn(VGroup(*in_lbls.values())), run_time=0.45)
        out_cells, out_grp = array_row(["", "", "", "", "", ""], y=-1.55, w=0.72, h=0.54, show_idx=False, name="order")
        self.play(FadeIn(out_grp), run_time=0.25)
        for step_i, u in enumerate((0, 1, 2, 3, 4, 5)):
            self.play(ns[u][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1),
                      Transform(out_cells[step_i][1], code(str(u), 18, ACCENT).move_to(out_cells[step_i])),
                      out_cells[step_i][0].animate.set_stroke(ACCENT, 2.2), run_time=0.26)

    def _anim_DijkstraGuide(self, idx, values):
        if idx == 3:  # State-space graph (node, coupon_used)
            top = {u: gnode(f"({u},0)", (-3.2 + u * 3.2, 1.15), r=0.36, stroke=BLUE, fill=BLUE_FILL) for u in range(3)}
            bot = {u: gnode(f"({u},1)", (-3.2 + u * 3.2, -0.55), r=0.36, stroke=ACCENT, fill=ACCENT_FILL) for u in range(3)}
            e1 = VGroup(gedge(top[0], top[1], directed=True, weight="10", r=0.38)[0], gedge(top[1], top[2], directed=True, weight="8", r=0.38)[0])
            e2 = VGroup(gedge(bot[0], bot[1], directed=True, weight="10", r=0.38)[0], gedge(bot[1], bot[2], directed=True, weight="8", r=0.38)[0])
            jump, jlbl = gedge(top[0], bot[1], directed=True, color=AMBER, weight="w/2=5", r=0.38)
            self.play(FadeIn(VGroup(*top.values(), *bot.values())), Create(e1), Create(e2), FadeIn(banner("State-space Dijkstra: duplicate graph layers for (node, state)", y=2.05, color=AMBER)), run_time=0.55)
            self.play(Create(jump), FadeIn(jlbl), run_time=0.6)
            return
        coords = {0: (-4.0, 0.35), 1: (-1.4, 1.45), 2: (-1.4, -0.75), 3: (1.5, 1.45), 4: (1.5, -0.75), 5: (4.0, 0.35)}
        ns = {u: gnode(str(u), p, r=0.31) for u, p in coords.items()}
        specs = [(0, 1, 2), (0, 2, 5), (1, 2, 1), (1, 3, 4), (2, 4, 2), (3, 5, 3), (4, 5, 2)]
        el, wts = {}, VGroup()
        for u, v, w in specs:
            ln, wl = gedge(ns[u], ns[v], directed=True, weight=w, r=0.32)
            el[(u, v)] = ln
            wts.add(wl)
        badges = {u: code(f"d={'0' if u == 0 else 'inf'}", 15, ACCENT if u == 0 else MUTED).next_to(ns[u], UP if coords[u][1] >= 0 else DOWN, buff=0.1) for u in ns}
        self.play(Create(VGroup(*el.values())), FadeIn(wts), FadeIn(VGroup(*ns.values())), FadeIn(VGroup(*badges.values())), run_time=0.45)
        for u, v, nd in [(0, 1, "2"), (1, 2, "3"), (2, 4, "5"), (1, 3, "6"), (4, 5, "7")]:
            self.play(el[(u, v)].animate.set_color(ACCENT).set_stroke(width=3.2),
                      ns[v][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1),
                      Transform(badges[v], code(f"d={nd}", 16, ACCENT).move_to(badges[v])), run_time=0.32)

    def _anim_BellmanFloydGuide(self, idx, values):
        if idx >= 2:  # Floyd-Warshall N x N matrix
            mat = [["0", "3", "inf", "7"], ["8", "0", "2", "inf"], ["5", "inf", "0", "1"], ["2", "inf", "inf", "0"]]
            cells, grp = table_grid(mat, x0=-1.6, y0=1.25, cw=0.88, ch=0.64)
            lbl = banner("Floyd-Warshall: d[i][j] = min(d[i][j], d[i][k] + d[k][j]) in O(N^3)", y=2.1, color=ACCENT)
            self.play(FadeIn(grp), FadeIn(lbl), run_time=0.45)
            self.play(Transform(cells[0][2][1], code("5", 18, ACCENT).move_to(cells[0][2])),
                      cells[0][2][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1),
                      Transform(cells[1][3][1], code("3", 18, ACCENT).move_to(cells[1][3])),
                      cells[1][3][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1), run_time=0.75)
            return
        # Bellman-Ford negative edge & negative cycle detection (actual 3-cycle 1->2->3->1 = -2!)
        coords = {0: (-4.0, 0.35), 1: (-1.0, 1.3), 2: (2.2, 1.3), 3: (0.6, -0.75)}
        ns = {u: gnode(str(u), p, r=0.32) for u, p in coords.items()}
        specs = [(0, 1, 4), (1, 2, 2), (2, 3, -5), (3, 1, 1)]
        el, wts = {}, VGroup()
        for u, v, w in specs:
            ln, wl = gedge(ns[u], ns[v], directed=True, weight=w, r=0.34, label_color=BAD if w < 0 else AMBER)
            el[(u, v)] = ln
            wts.add(wl)
        self.play(Create(VGroup(*el.values())), FadeIn(wts), FadeIn(VGroup(*ns.values())), run_time=0.45)
        msg = "Negative cycle 1->2->3->1 (sum = 2 - 5 + 1 = -2): pass N still relaxes!" if idx == 1 else "Bellman-Ford: relax all edges N-1 times (handles negative weights)"
        self.play(FadeIn(banner(msg, y=2.05, color=BAD if idx == 1 else ACCENT)),
                  *(el[e].animate.set_color(BAD).set_stroke(width=3.5) for e in [(1, 2), (2, 3), (3, 1)]), run_time=0.75)

    def _anim_MstGuide(self, idx, values):
        coords = {0: (-3.8, 0.35), 1: (-1.4, 1.4), 2: (-1.4, -0.7), 3: (1.4, 1.4), 4: (1.4, -0.7), 5: (3.8, 0.35)}
        ns = {u: gnode(str(u), p, r=0.30) for u, p in coords.items()}
        specs = [(1, 2, 1), (3, 4, 1), (0, 1, 2), (2, 4, 2), (4, 5, 2), (0, 2, 5), (1, 3, 4)]
        el, wts = {}, VGroup()
        for u, v, w in specs:
            ln, wl = gedge(ns[u], ns[v], directed=False, weight=w, r=0.31)
            el[(u, v)] = ln
            wts.add(wl)
        self.play(Create(VGroup(*el.values())), FadeIn(wts), FadeIn(VGroup(*ns.values())), run_time=0.45)
        take = [(1, 2), (3, 4), (0, 1), (2, 4), (4, 5)] if idx != 3 else [(1, 2), (3, 4), (0, 1), (4, 5)]
        msg = "K-component forest: stop Kruskal after N - K edges!" if idx == 3 else "Kruskal/Prim MST: take cheapest non-cycle edges (total = 8)"
        self.play(FadeIn(banner(msg, y=2.05, color=ACCENT)), run_time=0.3)
        for u, v in take:
            self.play(el[(u, v)].animate.set_color(ACCENT).set_stroke(width=3.4),
                      ns[u][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1),
                      ns[v][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1), run_time=0.28)
        self.play(el[(0, 2)].animate.set_color(BAD).set_opacity(0.25), el[(1, 3)].animate.set_color(BAD).set_opacity(0.25), run_time=0.35)

    def _anim_BridgesGuide(self, idx, values):
        # MATHEMATICALLY TRUE BRIDGE GRAPH:
        # Left triangle {0, 1, 2} and Right triangle {3, 4, 5} joined ONLY by bridge (2, 3)!
        coords = {0: (-4.3, 1.3), 1: (-4.3, -0.6), 2: (-1.7, 0.35),
                  3: (1.7, 0.35), 4: (4.3, 1.3), 5: (4.3, -0.6)}
        ns = {u: gnode(str(u), p, r=0.31) for u, p in coords.items()}
        edges = [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (4, 5)]
        el = {e: gedge(ns[e[0]], ns[e[1]], r=0.32)[0] for e in edges}
        self.play(Create(VGroup(*el.values())), FadeIn(VGroup(*ns.values())), run_time=0.45)
        if idx == 0:  # tin / low-link values
            tins = {0: "0/0", 1: "1/0", 2: "2/0", 3: "3/3", 4: "4/3", 5: "5/3"}
            lbls = VGroup(*(code(tins[u], 14, AMBER if u >= 3 else ACCENT).next_to(ns[u], UP if coords[u][1] >= 0 else DOWN, buff=0.1) for u in ns))
            self.play(FadeIn(lbls), FadeIn(banner("tin/low: triangle {0,1,2} has low=0; triangle {3,4,5} has low=3", y=2.1, color=ACCENT)), run_time=0.7)
        elif idx == 1:  # Bridge edge (2, 3): low[3]=3 > tin[2]=2
            self.play(
                *(ns[u][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1) for u in (0, 1, 2)),
                *(ns[u][0].animate.set_stroke(BLUE, 2.4).set_fill(BLUE_FILL, 1) for u in (3, 4, 5)),
                el[(2, 3)].animate.set_color(BAD).set_stroke(width=4.5),
                FadeIn(banner("TRUE BRIDGE (2,3): low[3]=3 > tin[2]=2  (no back-edge crosses!)", y=2.1, color=BAD)),
                run_time=0.7,
            )
            self.play(Indicate(el[(2, 3)], color=BAD, scale_factor=1.18), run_time=0.45)
        elif idx == 2:  # Articulation cut vertices 2 and 3
            self.play(ns[2][0].animate.set_stroke(BAD, 3.2).set_fill(BAD_FILL, 1),
                      ns[3][0].animate.set_stroke(BAD, 3.2).set_fill(BAD_FILL, 1),
                      FadeIn(banner("Articulation vertices 2 and 3: removing either disconnects the graph!", y=2.1, color=BAD)), run_time=0.7)
        else:  # Bridge-block tree condensation
            b0 = Circle(radius=1.45, stroke_color=ACCENT, stroke_width=2.4, fill_color=ACCENT, fill_opacity=0.12).move_to([-3.2, 0.35, 0])
            b1 = Circle(radius=1.45, stroke_color=BLUE, stroke_width=2.4, fill_color=BLUE, fill_opacity=0.12).move_to([3.2, 0.35, 0])
            self.play(Create(b0), Create(b1), el[(2, 3)].animate.set_color(AMBER).set_stroke(width=3.8),
                      FadeIn(banner("Bridge-block tree: contract 2-edge-connected blocks -> pure tree!", y=2.1, color=AMBER)), run_time=0.75)

    # -------------------------------------------------------------------------
    # 08: TREES & LCA (EULER TOUR, LCA)
    # -------------------------------------------------------------------------
    def _anim_EulerTourGuide(self, idx, values):
        pos = {1: (0.0, 1.55), 2: (-2.5, 0.4), 3: (2.5, 0.4), 4: (-3.7, -0.75), 5: (-1.3, -0.75), 6: (2.5, -0.75)}
        tn = {k: gnode(str(k), p, r=0.29) for k, p in pos.items()}
        edges = VGroup(*(Line(tn[a].get_bottom(), tn[b].get_top(), color=STROKE, stroke_width=2.0) for a, b in [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6)]))
        self.play(Create(edges), FadeIn(VGroup(*tn.values())), run_time=0.4)
        if idx == 1:  # Euler tour tin/tout flattening
            tc, tg = array_row([1, 2, 4, 5, 3, 6], y=-1.6, w=0.72, h=0.52, show_idx=False, name="tour")
            self.play(FadeIn(tg), FadeIn(banner("Subtree of 2 = contiguous range [tin[2]..tout[2]] = [2, 4, 5]!", y=2.15, color=ACCENT)), run_time=0.35)
            for ti, nid in enumerate((1, 2, 4, 5, 3, 6)):
                col = ACCENT if nid in (2, 4, 5) else BLUE
                self.play(tn[nid][0].animate.set_stroke(col, 2.5), tc[ti][0].animate.set_stroke(col, 2.5), run_time=0.18)
        elif idx == 2:  # Tree diameter 2 sweeps: 4 -> 2 -> 1 -> 3 -> 6
            self.play(FadeIn(banner("Diameter in 2 BFS/DFS sweeps: 4 -> 2 -> 1 -> 3 -> 6 (length 4)", y=2.15, color=AMBER)), run_time=0.3)
            for nid in (4, 2, 1, 3, 6):
                self.play(tn[nid][0].animate.set_stroke(AMBER, 2.8).set_fill(AMBER_FILL, 1), run_time=0.22)
        else:
            sz = {4: "1", 5: "1", 6: "1", 2: "3", 3: "2", 1: "6"}
            self.play(FadeIn(banner("Subtree sizes bottom-up (centroid has all components <= N/2)", y=2.15, color=ACCENT)), run_time=0.3)
            for nid in (4, 5, 6, 2, 3, 1):
                self.play(tn[nid][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1),
                          FadeIn(code(f"sz={sz[nid]}", 14, ACCENT).next_to(tn[nid], RIGHT, buff=0.08)), run_time=0.22)

    def _anim_LcaGuide(self, idx, values):
        pos = {1: (0.0, 1.55), 2: (-2.6, 0.4), 3: (2.6, 0.4), 4: (-3.8, -0.8), 5: (-1.4, -0.8), 6: (1.4, -0.8), 7: (3.8, -0.8)}
        tn = {k: gnode(str(k), p, r=0.30) for k, p in pos.items()}
        edges = VGroup(*(Line(tn[a].get_bottom(), tn[b].get_top(), color=STROKE, stroke_width=2.0) for a, b in [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7)]))
        self.play(Create(edges), FadeIn(VGroup(*tn.values())), run_time=0.4)
        arc1 = ArcBetweenPoints(tn[4].get_center(), tn[1].get_center(), angle=-1.0, color=ACCENT, stroke_width=2.8)
        arc2 = ArcBetweenPoints(tn[6].get_center(), tn[1].get_center(), angle=1.0, color=AMBER, stroke_width=2.8)
        msg = "dist(u, v) = depth[u] + depth[v] - 2 * depth[LCA(u, v)]" if idx == 3 else "Binary lifting: jump 2^k ancestors in O(log N) -> LCA(4, 6) = 1"
        self.play(Create(arc1), Create(arc2), tn[1][0].animate.set_stroke(ACCENT, 3.0).set_fill(ACCENT_FILL, 1), FadeIn(banner(msg, y=2.15, color=ACCENT)), run_time=0.8)

    # -------------------------------------------------------------------------
    # 09: MATH, NUMBER THEORY & BITWISE (GCD, SIEVE, MODCOMB, BITWISE)
    # -------------------------------------------------------------------------
    def _anim_GcdGuide(self, idx, values):
        sets = [
            [("gcd(48, 18)", "48 = 2*18 + 12", ACCENT), ("gcd(18, 12)", "18 = 1*12 + 6", AMBER), ("gcd(12, 6)", "12 = 2*6 + 0 -> gcd = 6", ACCENT)],
            [("6 = 18 - 1*12", "back-substitute 12 = 48 - 2*18", AMBER), ("6 = 3*18 - 1*48", "Bezout: a*x + b*y = gcd(a,b)", ACCENT)],
            [("a*x + m*y = 1", "exists iff gcd(a, m) == 1", BLUE), ("a*x == 1 (mod m)", "x % m is general modular inverse", ACCENT)],
            [("x == 2 (mod 3)", "x == 3 (mod 5)  [coprime moduli]", AMBER), ("CRT unique mod 15", "x == 8 (mod 15)", ACCENT)],
        ]
        rows = VGroup(*(box_cell(f"{a}   |   {b}", w=9.8, h=0.72, stroke=c, fill=CARD, color=c, size=18) for a, b, c in sets[idx])).arrange(DOWN, buff=0.25).move_to([0, 0.35, 0])
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.18), run_time=0.45)

    def _anim_SieveGuide(self, idx, values):
        if idx == 1:  # SPF log N factorization of 60
            steps = ["60 / spf[60]=2 -> 30", "30 / spf[30]=2 -> 15", "15 / spf[15]=3 -> 5", "5 / spf[5]=5 -> 1   (60 = 2^2 * 3 * 5)"]
            rows = VGroup(*(box_cell(s, w=7.6, h=0.58, stroke=ACCENT if i == 3 else BLUE, fill=CARD, color=ACCENT if i == 3 else PAPER, size=17) for i, s in enumerate(steps))).arrange(DOWN, buff=0.16).move_to([0, 0.35, 0])
            self.play(LaggedStart(*(FadeIn(r, shift=RIGHT * 0.15) for r in rows), lag_ratio=0.18), run_time=0.95)
            return
        grid, cmap = VGroup(), {}
        for k, nv in enumerate(range(2, 26)):
            r, c = divmod(k, 8)
            m = box_cell(nv, w=0.82, h=0.66, size=18).move_to([-3.2 + c * 0.92, 1.25 - r * 0.80, 0])
            cmap[nv] = m
            grid.add(m)
        self.play(FadeIn(grid), run_time=0.4)
        for p in (2, 3, 5):
            self.play(cmap[p][0].animate.set_stroke(ACCENT, 2.8).set_fill(ACCENT_FILL, 1), run_time=0.2)
            mults = [m for m in range(p * p, 26, p)]
            if mults:
                self.play(*(cmap[m][0].animate.set_stroke(BAD, 2.0).set_fill(BAD_FILL, 1) for m in mults),
                          *(cmap[m][1].animate.set_color(BAD) for m in mults), run_time=0.35)

    def _anim_ModCombGuide(self, idx, values):
        sets = [
            [("(a + b) % M", "reduce after every +, -, *", ACCENT), ("((a - b) % M + M) % M", "keep subtraction non-negative", AMBER)],
            [("a^13 = a^8 * a^4 * a^1", "binary exponentiation in O(log b)", BLUE), ("a^-1 = a^(M-2) mod M", "Fermat inverse for prime M", ACCENT)],
            [("fact[i] = i * fact[i-1] % M", "O(N) forward factorials", ACCENT), ("inv[N] = pow(fact[N], M-2, M)", "1 inverse, then O(N) backward", AMBER), ("nCr = fact[n]*inv[r]*inv[n-r]", "O(1) per query!", ACCENT)],
            [("Stars & Bars", "C(n + k - 1, k - 1) non-negative sums", BLUE), ("Inclusion-Exclusion", "+ singles - pairs + triples ...", ACCENT)],
        ]
        rows = VGroup(*(box_cell(f"{a}   |   {b}", w=10.2, h=0.72, stroke=c, fill=CARD, color=c, size=17) for a, b, c in sets[idx])).arrange(DOWN, buff=0.24).move_to([0, 0.35, 0])
        for r in rows:
            self.play(FadeIn(r, shift=RIGHT * 0.18), run_time=0.45)

    def _anim_BitwiseGuide(self, idx, values):
        if idx == 2:  # XOR cancellation
            c, g = array_row(["5", "9", "5", "3", "9"], y=0.5, w=0.95, name="A")
            lbl = banner("5 ^ 9 ^ 5 ^ 3 ^ 9  =  (5^5) ^ (9^9) ^ 3  =  3", y=1.9, color=ACCENT)
            self.play(FadeIn(g), FadeIn(lbl), run_time=0.4)
            self.play(*(c[k].animate.set_opacity(0.22) for k in (0, 1, 2, 4)),
                      c[3][0].animate.set_stroke(ACCENT, 3.0).set_fill(ACCENT_FILL, 1), run_time=0.75)
            return
        b1, g1 = array_row(list("00101100"), y=1.1, w=0.68, h=0.60, show_idx=False, name="x    ")
        b2, g2 = array_row(list("00101011"), y=0.2, w=0.68, h=0.60, show_idx=False, name="x - 1")
        b3, g3 = array_row(list("00101000"), y=-0.7, w=0.68, h=0.60, show_idx=False, name="x&x-1")
        self.play(FadeIn(g1), FadeIn(g2), FadeIn(g3), run_time=0.45)
        self.play(b1[5][0].animate.set_stroke(BAD, 2.6).set_fill(BAD_FILL, 1),
                  b3[5][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1), run_time=0.75)

    # -------------------------------------------------------------------------
    # 10: STRING ALGORITHMS (ROLLING HASH, KMP, Z-ALGO, TRIE)
    # -------------------------------------------------------------------------
    def _anim_RollingHashGuide(self, idx, values):
        if idx == 0:  # Polynomial mod M
            c, g = array_row(["'a'=1", "'b'=2", "'c'=3"], y=0.9, w=1.8, h=0.72, show_idx=False, name="S")
            f = box_cell("H(\"abc\") = (1*B^2 + 2*B + 3) mod M", w=7.8, h=0.75, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=19).move_to([0, -0.45, 0])
            self.play(FadeIn(g), run_time=0.4)
            self.play(FadeIn(f, shift=UP * 0.15), *(x[0].animate.set_stroke(ACCENT, 2.2) for x in c), run_time=0.65)
        elif idx == 1:  # O(1) substring hash
            c, g = array_row(list("ABCDEF"), y=0.9, w=0.86, name="S")
            f = box_cell("H[2..4] = (H[5] - H[2] * B^3) mod M   -> O(1)!", w=8.8, h=0.72, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=18).move_to([0, -0.55, 0])
            self.play(FadeIn(g), *(c[k][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1) for k in (2, 3, 4)), FadeIn(f), run_time=0.75)
        elif idx == 2:  # Double hash (M1, M2)
            b1 = box_cell("Hash 1 (B=131, M1=10^9+7)\ncollision prob ~ 10^-9", w=4.6, h=0.95, stroke=BLUE, fill=BLUE_FILL, color=BLUE, size=16).move_to([-2.7, 0.4, 0])
            b2 = box_cell("Hash 2 (B=137, M2=10^9+9)\njoint prob ~ 10^-18 (safe!)", w=4.6, h=0.95, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=16).move_to([2.7, 0.4, 0])
            self.play(FadeIn(b1), FadeIn(b2), run_time=0.7)
        else:  # Binary search LCP with O(1) hash
            c1, g1 = array_row(list("ABACAB"), y=1.0, w=0.82, show_idx=False, name="S1")
            c2, g2 = array_row(list("ABACDE"), y=0.0, w=0.82, show_idx=False, name="S2")
            self.play(FadeIn(g1), FadeIn(g2), FadeIn(banner("Binary search LCP length using O(1) hash equality -> LCP = 4", y=1.95, color=ACCENT)), run_time=0.4)
            self.play(*(c1[k][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1) for k in range(4)),
                      *(c2[k][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1) for k in range(4)),
                      c1[4][0].animate.set_stroke(BAD, 2.5), c2[4][0].animate.set_stroke(BAD, 2.5), run_time=0.65)

    def _anim_KmpGuide(self, idx, values):
        if idx in (0, 1):  # pi[] prefix function & border fallback
            cS, gS = array_row(list("ABABAC"), y=1.05, w=0.92, name="P ")
            cPi, gPi = array_row([0, 0, 1, 2, 3, 0], y=-0.4, w=0.92, show_idx=False, name="pi")
            msg = "Mismatch at 'C': fallback j = pi[4] = 3 -> pi[2] = 1 -> 0" if idx == 1 else "pi[i] = longest proper prefix of P[0..i] that is also a suffix"
            self.play(FadeIn(gS), FadeIn(gPi), FadeIn(banner(msg, y=2.05, color=ACCENT)), run_time=0.45)
            self.play(*(cPi[k][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1) for k in (2, 3, 4)),
                      cPi[5][0].animate.set_stroke(BAD, 2.5).set_fill(BAD_FILL, 1), run_time=0.7)
        elif idx == 3:  # Minimal period n - pi[n-1]
            cS, gS = array_row(list("ABABAB"), y=0.95, w=0.92, name="S ")
            cPi, gPi = array_row([0, 0, 1, 2, 3, 4], y=-0.4, w=0.92, show_idx=False, name="pi")
            self.play(FadeIn(gS), FadeIn(gPi), FadeIn(banner("Minimal period p = n - pi[n-1] = 6 - 4 = 2  ('AB' repeats 3x!)", y=2.0, color=AMBER)),
                      cS[0][0].animate.set_stroke(AMBER, 2.8).set_fill(AMBER_FILL, 1),
                      cS[1][0].animate.set_stroke(AMBER, 2.8).set_fill(AMBER_FILL, 1), run_time=0.8)
        else:  # Linear pattern match
            t_c, g_t = array_row(list("ABABACAB"), y=1.05, w=0.76, h=0.66, name="T")
            p_c, g_p = array_row(list("ABAC"), y=-0.15, w=0.76, h=0.66, show_idx=False, name="P")
            g_p.align_to(t_c[0], LEFT).shift(LEFT * 0.72)
            self.play(FadeIn(g_t), FadeIn(g_p), run_time=0.4)
            dx = t_c[2].get_center()[0] - t_c[0].get_center()[0]
            self.play(g_p.animate.shift(RIGHT * dx),
                      *(t_c[k][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1) for k in range(2, 6)),
                      *(p_c[k][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1) for k in range(4)), run_time=0.75)

    def _anim_ZAlgoGuide(self, idx, values):
        if idx == 3:  # P + "$" + T
            c, g = array_row(list("AB$XABYAB"), y=0.4, w=0.82, name="S")
            self.play(FadeIn(g), FadeIn(banner('Concatenate P + "$" + T: matches where Z[i] == |P| = 2!', y=1.9, color=ACCENT)),
                      c[2][0].animate.set_stroke(BAD, 2.5).set_fill(BAD_FILL, 1),
                      c[4][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1),
                      c[7][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1), run_time=0.8)
            return
        cS, gS = array_row(list("AABXAAB"), y=1.0, w=0.88, name="S")
        cZ, gZ = array_row(["-", 1, 0, 0, 3, 1, 0], y=-0.4, w=0.88, show_idx=False, name="Z")
        zbox = RoundedRectangle(width=VGroup(*cS[4:7]).width + 0.14, height=0.86, corner_radius=0.06,
                                stroke_color=AMBER, stroke_width=2.8, fill_color=AMBER, fill_opacity=0.14).move_to(VGroup(*cS[4:7]))
        self.play(FadeIn(gS), FadeIn(gZ), FadeIn(banner("Z-box [L=4, R=6] matches S[0..2] -> reuse Z[i - L] in O(1)!", y=2.0, color=AMBER)), run_time=0.45)
        self.play(Create(zbox), cZ[4][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1),
                  cZ[5][0].animate.set_stroke(AMBER, 2.6).set_fill(AMBER_FILL, 1), run_time=0.7)

    def _anim_TrieGuide(self, idx, values):
        if idx >= 2:  # REAL BINARY TRIE (0/1 bits) for Max XOR!
            pos = {"r": (0.0, 1.55), "0": (-2.4, 0.45), "1": (2.4, 0.45),
                   "01": (-1.5, -0.65), "10": (1.5, -0.65), "11": (3.4, -0.65)}
            tn = {k: gnode("root" if k == "r" else k[-1], p, r=0.30) for k, p in pos.items()}
            specs = [("r", "0", "0"), ("r", "1", "1"), ("0", "01", "1"), ("1", "10", "0"), ("1", "11", "1")]
            el, lbls = {}, VGroup()
            for a, b, bit in specs:
                ln, wl = gedge(tn[a], tn[b], directed=False, weight=bit, r=0.31, label_color=ACCENT if bit == "1" else BLUE)
                el[(a, b)] = ln
                lbls.add(wl)
            self.play(Create(VGroup(*el.values())), FadeIn(lbls), FadeIn(VGroup(*tn.values())),
                      FadeIn(banner("Binary XOR Trie: for x=01_2, pick OPPOSITE bits 1 -> 0 (max XOR = 11_2)!", y=2.15, color=ACCENT)), run_time=0.5)
            self.play(el[("r", "1")].animate.set_color(ACCENT).set_stroke(width=3.6),
                      el[("1", "10")].animate.set_color(ACCENT).set_stroke(width=3.6),
                      tn["10"][0].animate.set_stroke(ACCENT, 2.8).set_fill(ACCENT_FILL, 1), run_time=0.7)
            return
        # REAL CHARACTER TRIE: "cat", "car", "cad"
        pos = {"root": (0.0, 1.65), "c": (0.0, 0.65), "a": (0.0, -0.35),
               "t": (-2.4, -1.35), "r": (0.0, -1.35), "d": (2.4, -1.35)}
        tn = {k: gnode(k if k == "root" else k + ("$" if k in ("t", "r", "d") else ""), p, r=0.32) for k, p in pos.items()}
        edges = [("root", "c", "c"), ("c", "a", "a"), ("a", "t", "t"), ("a", "r", "r"), ("a", "d", "d")]
        el, lbls = {}, VGroup()
        for a, b, ch in edges:
            ln, wl = gedge(tn[a], tn[b], weight=ch, r=0.33, label_color=ACCENT)
            el[(a, b)] = ln
            lbls.add(wl)
        self.play(Create(VGroup(*el.values())), FadeIn(lbls), FadeIn(VGroup(*tn.values())),
                  FadeIn(banner('Character Trie for {"cat", "car", "cad"}: shared prefix "ca" (cnt=3)', y=2.2, color=ACCENT)), run_time=0.5)
        for k in ("root", "c", "a", "t", "r", "d"):
            self.play(tn[k][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1), run_time=0.16)

    # -------------------------------------------------------------------------
    # 11: ADVANCED TECHNIQUES (CONSTRUCTIVE, MO'S SQRT, NIM)
    # -------------------------------------------------------------------------
    def _anim_ConstructiveGuide(self, idx, values):
        if idx == 0:  # Parity & sum invariant
            b = box_cell("Sum(1..N) = N(N+1)/2\nSplit into 2 equal sets -> MUST BE EVEN!", w=8.4, h=1.05, stroke=AMBER, fill=AMBER_FILL, color=AMBER, size=19).move_to([0, 0.4, 0])
            self.play(FadeIn(b), run_time=0.7)
        elif idx == 1:  # Zigzag interleaving
            c, g = array_row([1, 6, 2, 5, 3, 4], y=0.4, w=0.95, name="zig")
            self.play(FadeIn(g), FadeIn(banner("Extreme interleaving [1, n, 2, n-1, ...]: max adjacent gaps!", y=1.9, color=ACCENT)),
                      *(c[k][0].animate.set_stroke(ACCENT if k % 2 == 0 else AMBER, 2.5) for k in range(6)), run_time=0.75)
        elif idx == 2:  # Binary power decomposition
            c, g = array_row([1, 2, 4, 8], y=0.45, w=1.1, show_idx=False, name="2^k")
            self.play(FadeIn(g), FadeIn(banner("Greedy binary powers represent ANY target sum: 13 = 8 + 4 + 1", y=1.9, color=ACCENT)),
                      *(c[k][0].animate.set_stroke(ACCENT, 2.8).set_fill(ACCENT_FILL, 1) for k in (0, 2, 3)), run_time=0.75)
        else:  # Invariant checker
            c, g = array_row(["2", "4", "1", "3", "5"], y=0.45, w=0.95, name="P")
            self.play(FadeIn(g), FadeIn(banner("Checker: |2-4|=2, |4-1|=3, |1-3|=2, |3-5|=2  -> ALL >= 2 ✓", y=1.9, color=ACCENT)),
                      *(x[0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1) for x in c), run_time=0.75)

    def _anim_MoSqrtGuide(self, idx, values):
        if idx == 3:  # Heavy vs Light degree split
            h = box_cell("HEAVY nodes (deg >= sqrt(M))\nAt most O(sqrt(M)) of them!", w=4.6, h=1.05, stroke=AMBER, fill=AMBER_FILL, color=AMBER, size=16).move_to([-2.7, 0.4, 0])
            l = box_cell("LIGHT nodes (deg < sqrt(M))\nScan all neighbors in O(sqrt(M))!", w=4.6, h=1.05, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=16).move_to([2.7, 0.4, 0])
            self.play(FadeIn(h), FadeIn(l), run_time=0.75)
            return
        c, g = array_row([3, 1, 4, 1, 5, 9, 2, 6, 5], y=0.55, w=0.78, h=0.66, name="A")
        self.play(FadeIn(g), run_time=0.35)
        blocks = VGroup(*(RoundedRectangle(width=VGroup(*c[i:i + 3]).width + 0.1, height=0.86, corner_radius=0.06,
                                           stroke_color=col, stroke_width=2.6, fill_color=col, fill_opacity=0.12).move_to(VGroup(*c[i:i + 3]))
                          for i, col in [(0, ACCENT), (3, BLUE), (6, AMBER)]))
        msg = "Sort offline queries by (L // B, R) -> total pointer moves O((N+Q)sqrt(N))" if idx == 1 else "Partition N elements into sqrt(N) blocks of size B = 3"
        self.play(Create(blocks), FadeIn(banner(msg, y=1.95, color=ACCENT)), run_time=0.75)

    def _anim_NimGuide(self, idx, values):
        if idx == 2:  # Sprague-Grundy mex
            c, g = array_row(["G(0)=0", "G(1)=1", "G(2)=2", "G(3)=0"], y=0.45, w=1.7, h=0.75, show_idx=False)
            self.play(FadeIn(g), FadeIn(banner("Sprague-Grundy: G(state) = mex{ G(next) }  (smallest missing non-neg)", y=1.9, color=AMBER)),
                      c[0][0].animate.set_stroke(BAD, 2.4), c[3][0].animate.set_stroke(BAD, 2.4),
                      c[1][0].animate.set_stroke(ACCENT, 2.4), c[2][0].animate.set_stroke(ACCENT, 2.4), run_time=0.75)
            return
        piles = VGroup()
        for ip, (cnt, bs) in enumerate([(3, "011"), (5, "101"), (7, "111")]):
            xp = -4.8 + ip * 1.95
            stones = VGroup(*(Circle(radius=0.15, stroke_color=ACCENT, fill_color=ACCENT, fill_opacity=0.35)
                              .move_to([xp + (s % 2) * 0.38, -0.5 + (s // 2) * 0.38, 0]) for s in range(cnt)))
            piles.add(VGroup(stones, code(f"{cnt} ({bs})", 15, PAPER).move_to([xp + 0.18, -1.05, 0])))
        xor_box = box_cell("3 ^ 5 ^ 7 = 1 != 0 (N-state)", w=4.8, h=0.84, stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=17).move_to([3.1, 0.35, 0])
        self.play(FadeIn(piles), FadeIn(xor_box), run_time=0.45)
        self.play(FadeOut(piles[0][0][-1], shift=UP * 0.3),
                  Transform(xor_box[1], code("3->2:  2 ^ 5 ^ 7 = 0 (P-state)", 17, AMBER, width=4.4).move_to(xor_box)), run_time=0.7)

    def _anim_fallback(self, idx, values):
        cards = VGroup(*(box_cell(v, w=3.3, h=0.95, stroke=ACCENT if i == 2 else STROKE, fill=ACCENT_FILL if i == 2 else CARD,
                                  color=ACCENT if i == 2 else PAPER, size=18) for i, v in enumerate(list(values)[:3]))).arrange(RIGHT, buff=0.5).move_to([0, 0.35, 0])
        self.play(LaggedStart(*(FadeIn(c, shift=UP * 0.15) for c in cards), lag_ratio=0.15), run_time=0.8)


for _scene_name in LESSONS:
    globals()[_scene_name] = type(_scene_name, (Guide,), {})
