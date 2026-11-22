"""Render with Manim Community 0.22. AUDIO_DIR holds the Gemini WAV clips.

Each algorithm family uses its own distinct visual format, and each of the 4
beats (index 0..3) animates that beat's specific sub-concept and values.
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
    if cells.width > 11.2:
        cells.scale_to_fit_width(11.2)
    cells.move_to([0.2 if name else 0.0, y, 0])
    grp = VGroup(cells)
    if show_idx:
        idxs = VGroup(*(code(i, size=15, color=MUTED).next_to(c, DOWN, buff=0.08) for i, c in enumerate(cells)))
        grp.add(idxs)
    if name:
        lbl = code(name, size=20, color=ACCENT).next_to(cells, LEFT, buff=0.28)
        grp.add(lbl)
    return cells, grp


def pointer_pin(name, target_cell, direction=UP, color=ACCENT):
    tri = Polygon(
        [-0.14, 0, 0], [0.14, 0, 0], [0, -0.22 if direction is UP else 0.22, 0],
        stroke_color=color, fill_color=color, fill_opacity=1, stroke_width=1,
    )
    lbl = code(name, size=18, color=color)
    if direction is UP:
        tri.next_to(target_cell, UP, buff=0.1)
        lbl.next_to(tri, UP, buff=0.06)
    else:
        tri.next_to(target_cell, DOWN, buff=0.28)
        lbl.next_to(tri, DOWN, buff=0.06)
    return VGroup(tri, lbl)


def gnode(label_str, pos, r=0.33, stroke=STROKE, fill=CARD, color=PAPER):
    c = Circle(radius=r, stroke_color=stroke, stroke_width=2.2, fill_color=fill, fill_opacity=1)
    t = code(label_str, size=20, color=color, width=r * 1.6).move_to(c)
    return VGroup(c, t).move_to([pos[0], pos[1], 0])


def gedge(n1, n2, directed=False, color=STROKE, weight=None, r=0.34):
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
        bg = RoundedRectangle(width=0.42, height=0.32, corner_radius=0.04,
                              fill_color="#171717", fill_opacity=1, stroke_width=0).move_to(mid)
        wt = code(weight, size=16, color=AMBER).move_to(mid)
        return ln, VGroup(bg, wt)
    return ln, None


def footer_chips(values):
    chips = VGroup(*(
        box_cell(v, w=3.4, h=0.54, stroke=ACCENT if i == 2 else STROKE,
                 fill=ACCENT_FILL if i == 2 else WELL,
                 color=ACCENT if i == 2 else PAPER, size=17)
        for i, v in enumerate(list(values)[:3])
    )).arrange(RIGHT, buff=0.35).move_to([0, -2.35, 0])
    return chips


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

            bar = Line(LEFT * 6.2, RIGHT * 6.2, color=STROKE, stroke_width=1.2).set_y(2.72)
            tag = code(f"STEP 0{index + 1} // {name.upper()}", 15, ACCENT).move_to([-6.1, 3.45, 0], aligned_edge=LEFT)
            heading = txt(title, 31, PAPER, width=12.0).move_to([-6.1, 3.04, 0], aligned_edge=LEFT)
            foot = footer_chips(values)
            self.play(FadeIn(tag), FadeIn(heading, shift=DOWN * 0.08), Create(bar), FadeIn(foot), run_time=0.35)

            self.animate_family(name, index, values)

            beat_span = max(8.2, duration, self.time - start + 0.15)
            self.wait(max(0.1, beat_span - (self.time - start)))
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", narration.strip()) if s.strip()]
            cursor = start
            total_chars = sum(map(len, sentences))
            for sentence in sentences:
                end = cursor + duration * len(sentence) / total_chars
                cues.extend([f"{stamp(cursor)} --> {stamp(end)}", sentence, ""])
                cursor = end
            self.play(FadeOut(*self.mobjects, shift=UP * 0.06), run_time=0.3)
        (ROOT.parent / "public" / f"{name}.vtt").write_text("\n".join(cues), encoding="utf-8")

    def animate_family(self, name, index, values):
        # =====================================================================
        # 1. SLIDING WINDOW: Translucent frame gliding / resizing over array
        # =====================================================================
        if name == "SlidingWindowGuide":
            arr = [2, 5, 1, 8, 2, 9, 1, 3]
            cells, grp = array_row(arr, y=0.55, name="A")
            self.play(FadeIn(grp), run_time=0.35)
            if index == 2:
                # Variable window expanding R then shrinking L when sum > 10
                span = VGroup(*cells[0:2])
                frame = RoundedRectangle(width=span.width + 0.16, height=0.98, corner_radius=0.08,
                                         stroke_color=ACCENT, stroke_width=3.0, fill_color=ACCENT, fill_opacity=0.14).move_to(span)
                badge = code("expand R while sum <= 10:  [0..1] sum = 7", 19, ACCENT).move_to([0, 1.85, 0])
                self.play(Create(frame), FadeIn(badge), run_time=0.35)
                for l_i, r_i, msg, col in [
                    (0, 2, "expand R=2 -> [0..2] sum = 8 <= 10 (valid)", ACCENT),
                    (0, 3, "expand R=3 -> [0..3] sum = 16 > 10 (violates limit!)", BAD),
                    (2, 3, "shrink L=2 -> [2..3] sum = 9 <= 10 (invariant restored)", ACCENT),
                    (2, 4, "expand R=4 -> [2..4] sum = 11 > 10 -> shrink L", AMBER),
                ]:
                    sub = VGroup(*cells[l_i:r_i + 1])
                    new_f = RoundedRectangle(width=sub.width + 0.16, height=0.98, corner_radius=0.08,
                                             stroke_color=col, stroke_width=3.0, fill_color=col, fill_opacity=0.14).move_to(sub)
                    self.play(Transform(frame, new_f), Transform(badge, code(msg, 19, col).move_to([0, 1.85, 0])),
                              rate_func=smooth, run_time=0.5)
                return
            win_len = 3
            span = VGroup(*cells[0:win_len])
            frame = RoundedRectangle(width=span.width + 0.18, height=1.02, corner_radius=0.08,
                                     stroke_color=ACCENT, stroke_width=3.0, fill_color=ACCENT, fill_opacity=0.14).move_to(span)
            cur_sum = sum(arr[0:win_len])
            badge = code(f"window [0..2]  sum = {cur_sum}", 20, ACCENT).move_to([0, 1.85, 0])
            self.play(Create(frame), FadeIn(badge), run_time=0.35)
            for s in range(1, 5):
                nxt_span = VGroup(*cells[s:s + win_len])
                cur_sum = sum(arr[s:s + win_len])
                msg = (
                    f"+enter A[{s+2}]={arr[s+2]}   -leave A[{s-1}]={arr[s-1]}   ->   sum = {cur_sum}"
                    if index < 2 else f"right endpoint R={s+2}: adds R - L + 1 = {win_len} valid subarrays"
                )
                self.play(
                    cells[s - 1][0].animate.set_stroke(BAD, 2.2),
                    cells[s + win_len - 1][0].animate.set_stroke(ACCENT, 2.5),
                    frame.animate.move_to(nxt_span),
                    Transform(badge, code(msg, 19, ACCENT).move_to([0, 1.85, 0])),
                    rate_func=smooth, run_time=0.5,
                )
            return

        # =====================================================================
        # 2. TWO POINTERS: Converging L/R, Same-Direction Chase, Two-Stream Merge
        # =====================================================================
        if name == "TwoPointersGuide":
            if index == 3:
                c1, g1 = array_row([1, 4, 7, 10], y=1.35, w=0.75, h=0.62, show_idx=False, name="A")
                c2, g2 = array_row([2, 3, 8, 12], y=0.35, w=0.75, h=0.62, show_idx=False, name="B")
                co, go = array_row(["", "", "", "", "", ""], y=-0.8, w=0.75, h=0.62, show_idx=False, name="M")
                self.play(FadeIn(g1), FadeIn(g2), FadeIn(go), run_time=0.4)
                for k, (src, val) in enumerate([(c1[0], "1"), (c2[0], "2"), (c2[1], "3"), (c1[1], "4"), (c1[2], "7"), (c2[2], "8")]):
                    self.play(
                        src[0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1),
                        Transform(co[k][1], code(val, 20, ACCENT).move_to(co[k])),
                        co[k][0].animate.set_stroke(ACCENT, 2.0),
                        run_time=0.32,
                    )
                return
            arr = [1, 3, 4, 6, 8, 11, 14]
            cells, grp = array_row(arr, y=0.45, name="A")
            if index == 2:
                L = pointer_pin("L", cells[0], DOWN, ACCENT)
                R = pointer_pin("R", cells[0], UP, AMBER)
                status = code("Same-direction chase: both L and R move strictly right", 19, ACCENT).move_to([0, 1.9, 0])
                self.play(FadeIn(grp), FadeIn(L), FadeIn(R), FadeIn(status), run_time=0.4)
                for li, ri in [(0, 2), (1, 3), (2, 5), (3, 6)]:
                    self.play(
                        L.animate.next_to(cells[li], DOWN, buff=0.28),
                        R.animate.next_to(cells[ri], UP, buff=0.1),
                        cells[ri][0].animate.set_stroke(AMBER, 2.3),
                        cells[li][0].animate.set_stroke(ACCENT, 2.3),
                        rate_func=smooth, run_time=0.45,
                    )
                return
            L = pointer_pin("L", cells[0], UP, ACCENT)
            R = pointer_pin("R", cells[6], UP, AMBER)
            status = code("target = 14   |   A[0] + A[6] = 1 + 14 = 15 > 14  (step R left)", 19, PAPER).move_to([0, -1.1, 0])
            self.play(FadeIn(grp), FadeIn(L), FadeIn(R), FadeIn(status), run_time=0.4)
            for li, ri, msg, col in [
                (0, 5, "A[0] + A[5] = 1 + 11 = 12 < 14  (step L right)", AMBER),
                (1, 5, "A[1] + A[5] = 3 + 11 = 14 == target  (O(N) monotonic scan!)", ACCENT),
            ]:
                self.play(
                    L.animate.next_to(cells[li], UP, buff=0.1),
                    R.animate.next_to(cells[ri], UP, buff=0.1),
                    cells[li][0].animate.set_stroke(ACCENT, 2.4),
                    cells[ri][0].animate.set_stroke(col, 2.4),
                    Transform(status, code(msg, 19, col).move_to([0, -1.1, 0])),
                    rate_func=smooth, run_time=0.75,
                )
            return

        # =====================================================================
        # 3. SORTING & GREEDY: Bar Chart Swaps, Custom Keys, Sweep Line, Heap
        # =====================================================================
        if name == "SortingGuide":
            if index == 0:
                heights = [5, 2, 8, 1, 6, 3, 7]
                bars = VGroup()
                for i, v in enumerate(heights):
                    h = 0.27 * v + 0.3
                    b = RoundedRectangle(width=0.72, height=h, corner_radius=0.05,
                                         stroke_color=STROKE, stroke_width=1.8, fill_color=CARD, fill_opacity=1)
                    b.move_to([-2.7 + i * 0.9, -1.15 + h / 2, 0])
                    t = code(v, 19, PAPER).move_to(b.get_top() + DOWN * 0.22)
                    bars.add(VGroup(b, t))
                self.play(LaggedStart(*(FadeIn(b, shift=UP * 0.15) for b in bars), lag_ratio=0.08), run_time=0.45)
                order = sorted(range(len(heights)), key=lambda k: heights[k])
                targets = [-2.7 + k * 0.9 for k in range(len(heights))]
                self.play(
                    *(bars[idx].animate.set_x(targets[rank]) for rank, idx in enumerate(order)),
                    rate_func=smooth, run_time=0.9,
                )
                self.play(
                    *(bars[idx][0].animate.set_stroke(ACCENT, 2.2).set_fill(ACCENT_FILL, 1) for idx in order),
                    run_time=0.35,
                )
                return
            if index == 1:
                tuples = ["(2, 9)", "(1, 4)", "(2, 3)", "(1, 8)"]
                sorted_t = ["(1, 8)", "(1, 4)", "(2, 9)", "(2, 3)"]
                c1, g1 = array_row(tuples, y=1.0, w=1.7, h=0.72, show_idx=False, name="raw ")
                c2, g2 = array_row(sorted_t, y=-0.4, w=1.7, h=0.72, show_idx=False, name="key ")
                lbl = code("key = lambda x: (x[0], -x[1])   # asc primary, desc tie-break", 18, ACCENT).move_to([0, 1.95, 0])
                self.play(FadeIn(g1), FadeIn(lbl), run_time=0.4)
                self.play(
                    FadeIn(g2, shift=DOWN * 0.2),
                    *(c[0].animate.set_stroke(ACCENT, 2.2).set_fill(ACCENT_FILL, 1) for c in c2),
                    run_time=0.85,
                )
                return
            if index == 3:
                raw_v = ["10", "10^9", "42", "10^9", "5"]
                comp_v = ["1", "3", "2", "3", "0"]
                c1, g1 = array_row(raw_v, y=1.05, w=1.35, h=0.7, show_idx=False, name="sparse")
                c2, g2 = array_row(comp_v, y=-0.45, w=1.35, h=0.7, show_idx=False, name="rank  ")
                arrows = VGroup(*(Arrow(c1[k].get_bottom(), c2[k].get_top(), buff=0.08, color=ACCENT, stroke_width=2.2) for k in range(5)))
                self.play(FadeIn(g1), run_time=0.35)
                self.play(Create(arrows), FadeIn(g2), *(c[0].animate.set_stroke(ACCENT, 2.2) for c in c2), run_time=0.85)
                return

        if name in ("SortingGuide", "GreedyGuide"):
            if name == "GreedyGuide" and index == 3:
                # Regret greedy min-heap swap
                h_pos = {1: (0, 1.55), 2: (-1.8, 0.2), 3: (1.8, 0.2)}
                h_nodes = {1: gnode("2", h_pos[1], stroke=BAD, fill=BAD_FILL),
                           2: gnode("7", h_pos[2], stroke=ACCENT, fill=ACCENT_FILL),
                           3: gnode("9", h_pos[3], stroke=ACCENT, fill=ACCENT_FILL)}
                h_edges = VGroup(Line(h_nodes[1].get_bottom(), h_nodes[2].get_top(), color=STROKE),
                                 Line(h_nodes[1].get_bottom(), h_nodes[3].get_top(), color=STROKE))
                cand = box_cell("candidate = 12 > root(2)", w=3.6, h=0.68, stroke=ACCENT, fill=ACCENT_FILL, size=18).move_to([0, -1.05, 0])
                self.play(Create(h_edges), FadeIn(VGroup(*h_nodes.values())), FadeIn(cand), run_time=0.5)
                self.play(
                    Transform(h_nodes[1][1], code("7", 20, ACCENT).move_to(h_nodes[1])),
                    h_nodes[1][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1),
                    Transform(h_nodes[2][1], code("12", 20, ACCENT).move_to(h_nodes[2])),
                    run_time=0.8,
                )
                return
            # 2D Interval Timeline with sweeping vertical scan-line
            axis = Line([-5.2, -1.3, 0], [5.2, -1.3, 0], color=MUTED, stroke_width=1.8)
            ticks = VGroup(*(
                VGroup(
                    Line([-5.0 + t * 1.0, -1.22, 0], [-5.0 + t * 1.0, -1.38, 0], color=MUTED),
                    code(t, 15, MUTED).move_to([-5.0 + t * 1.0, -1.6, 0]),
                ) for t in range(11)
            ))
            intervals = [(0, 3, True, 1.5), (1, 6, False, 0.85), (3, 6, True, 0.2), (5, 9, False, -0.45), (6, 10, True, -1.0)]
            iv_mobs = VGroup()
            for s, e, ok, y in intervals:
                bar = RoundedRectangle(width=(e - s) * 1.0, height=0.45, corner_radius=0.06,
                                       stroke_color=STROKE, stroke_width=1.8, fill_color=CARD, fill_opacity=1)
                bar.move_to([-5.0 + (s + e) * 0.5, y, 0])
                lbl = code(f"[{s}, {e}]", 16, PAPER).move_to(bar)
                iv_mobs.add(VGroup(bar, lbl))
            sweep = Line([-5.0, -1.3, 0], [-5.0, 2.0, 0], color=ACCENT, stroke_width=2.8)
            self.play(Create(axis), FadeIn(ticks), FadeIn(iv_mobs), Create(sweep), run_time=0.45)
            for (s, e, ok, _), mob in zip(intervals, iv_mobs):
                col = ACCENT if ok else BAD
                fill = ACCENT_FILL if ok else BAD_FILL
                self.play(
                    sweep.animate.set_x(-5.0 + e * 1.0),
                    mob[0].animate.set_stroke(col, 2.4).set_fill(fill, 1),
                    mob[1].animate.set_color(col),
                    rate_func=smooth, run_time=0.4,
                )
            return

        # =====================================================================
        # 4. BINARY & TERNARY SEARCH: Predicate Step Chart & Unimodal Curve
        # =====================================================================
        if name == "BinarySearchGuide":
            if index == 2:
                arr = [1, 4, 4, 4, 7, 9]
                cells, grp = array_row(arr, y=0.4, w=0.95, h=0.82, name="A")
                p_left = pointer_pin("bisect_left(4)=1", cells[1], UP, ACCENT)
                p_right = pointer_pin("bisect_right(4)=4", cells[4], DOWN, AMBER)
                span = RoundedRectangle(width=VGroup(*cells[1:4]).width + 0.14, height=0.96, corner_radius=0.06,
                                        stroke_color=ACCENT, stroke_width=2.6, fill_color=ACCENT, fill_opacity=0.14).move_to(VGroup(*cells[1:4]))
                self.play(FadeIn(grp), run_time=0.35)
                self.play(FadeIn(p_left), FadeIn(p_right), Create(span), run_time=0.8)
                return
            preds = ["F", "F", "F", "F", "T", "T", "T", "T"]
            vals = [2, 5, 8, 11, 15, 19, 23, 28]
            cells = VGroup(*(
                box_cell(f"{v}\n{p}", w=1.05, h=0.95, stroke=ACCENT if p == "T" else BAD,
                         fill=ACCENT_FILL if p == "T" else BAD_FILL, color=ACCENT if p == "T" else BAD, size=18)
                for p, v in zip(preds, vals)
            )).arrange(RIGHT, buff=0.12).move_to([0, 0.45, 0])
            lo = pointer_pin("lo", cells[0], DOWN, BAD)
            hi = pointer_pin("hi", cells[7], DOWN, ACCENT)
            mid = pointer_pin("mid", cells[3], UP, AMBER)
            info = code("check(mid=3) is False  ->  lo = mid + 1 (discard [0..3])", 19, AMBER).move_to([0, 1.9, 0])
            self.play(FadeIn(cells), FadeIn(lo), FadeIn(hi), FadeIn(mid), FadeIn(info), run_time=0.45)
            self.play(
                *(cells[k].animate.set_opacity(0.22) for k in range(4)),
                lo.animate.next_to(cells[4], DOWN, buff=0.28),
                mid.animate.next_to(cells[5], UP, buff=0.1),
                Transform(info, code("check(mid=5) is True  ->  hi = mid (discard [6..7])", 19, ACCENT).move_to([0, 1.9, 0])),
                rate_func=smooth, run_time=0.75,
            )
            self.play(
                *(cells[k].animate.set_opacity(0.22) for k in range(6, 8)),
                lo.animate.next_to(cells[4], DOWN, buff=0.28).shift(LEFT * 0.28),
                hi.animate.next_to(cells[4], DOWN, buff=0.28).shift(RIGHT * 0.28),
                mid.animate.next_to(cells[4], UP, buff=0.1),
                cells[4][0].animate.set_stroke(AMBER, 3.2),
                Transform(info, code("First True boundary locked at index 4 (value 15)", 20, ACCENT).move_to([0, 1.9, 0])),
                rate_func=smooth, run_time=0.7,
            )
            return

        if name == "TernarySearchGuide":
            ax_x = Line([-4.6, -1.25, 0], [4.6, -1.25, 0], color=MUTED, stroke_width=2)
            ax_y = Line([-4.6, -1.25, 0], [-4.6, 2.0, 0], color=MUTED, stroke_width=2)
            xs = np.linspace(-3.6, 4.0, 80)
            pts = [[x, 0.12 * (x - 0.5) ** 2 - 0.85, 0] for x in xs]
            curve = VMobject(color=ACCENT, stroke_width=3.2).set_points_smoothly(pts)
            self.play(Create(ax_x), Create(ax_y), Create(curve), run_time=0.45)
            x1, x2 = -1.6, 1.8
            y1, y2 = 0.12 * (x1 - 0.5) ** 2 - 0.85, 0.12 * (x2 - 0.5) ** 2 - 0.85
            l1 = Line([x1, -1.25, 0], [x1, y1, 0], color=BAD, stroke_width=2.4)
            l2 = Line([x2, -1.25, 0], [x2, y2, 0], color=AMBER, stroke_width=2.4)
            d1, d2 = Dot([x1, y1, 0], color=BAD, radius=0.09), Dot([x2, y2, 0], color=AMBER, radius=0.09)
            t1, t2 = code("m1", 17, BAD).next_to(l1, DOWN, buff=0.1), code("m2", 17, AMBER).next_to(l2, DOWN, buff=0.1)
            shade = Rectangle(width=2.5, height=2.9, stroke_width=0, fill_color=BAD, fill_opacity=0.15).move_to([-2.85, 0.25, 0])
            msg = code("f(m1) > f(m2)  ->  eliminate outer third [L, m1]", 19, ACCENT).move_to([0.4, 1.95, 0])
            self.play(Create(l1), Create(l2), FadeIn(d1), FadeIn(d2), FadeIn(t1), FadeIn(t2), run_time=0.4)
            self.play(FadeIn(shade), FadeIn(msg), run_time=0.4)
            opt_dot = Dot([0.5, -0.85, 0], color=ACCENT, radius=0.11)
            opt_lbl = code("minimum x*", 18, ACCENT).next_to(opt_dot, UP, buff=0.25)
            self.play(
                FadeIn(opt_dot, scale=1.4), FadeIn(opt_lbl),
                rate_func=smooth, run_time=0.7,
            )
            return

        # =====================================================================
        # 5. GRAPHS: 2D Vertex-Edge Networks (BFS/DFS, Topo, Dijkstra, BF/FW, MST, Bridges)
        # =====================================================================
        if name in ("GraphTraversalGuide", "TopoSortGuide", "DijkstraGuide", "BellmanFloydGuide", "MstGuide", "BridgesGuide"):
            coords = {
                0: (-4.0, 0.4),
                1: (-1.5, 1.55),
                2: (-1.5, -0.75),
                3: (1.4, 1.55),
                4: (1.4, -0.75),
                5: (3.9, 0.4),
            }
            directed = name in ("TopoSortGuide", "DijkstraGuide", "BellmanFloydGuide")
            weighted = name in ("DijkstraGuide", "BellmanFloydGuide", "MstGuide")
            edge_specs = [
                (0, 1, 2), (0, 2, 5), (1, 2, 1),
                (1, 3, 4), (2, 4, -3 if name == "BellmanFloydGuide" else 2),
                (3, 4, 1), (3, 5, 3), (4, 5, 2),
            ]
            nodes = {u: gnode(str(u), pos) for u, pos in coords.items()}
            edge_lines = {}
            wt_labels = VGroup()
            for u, v, w in edge_specs:
                ln, wlbl = gedge(nodes[u], nodes[v], directed=directed, weight=(w if weighted else None))
                edge_lines[(u, v)] = ln
                if wlbl:
                    wt_labels.add(wlbl)
            self.play(Create(VGroup(*edge_lines.values())), FadeIn(wt_labels), FadeIn(VGroup(*nodes.values())), run_time=0.45)

            if name in ("DijkstraGuide", "BellmanFloydGuide"):
                badges = {u: code(f"d={'0' if u == 0 else '∞'}", 16, ACCENT if u == 0 else MUTED)
                          .next_to(nodes[u], UP if coords[u][1] >= 0 else DOWN, buff=0.12)
                          for u in nodes}
                self.play(FadeIn(VGroup(*badges.values())), nodes[0][0].animate.set_stroke(ACCENT, 2.6), run_time=0.3)
                relax_order = [(0, 1, "2"), (1, 2, "3"), (2, 4, "0" if name == "BellmanFloydGuide" else "5"), (1, 3, "6"), (4, 5, "7")]
                for u, v, new_d in relax_order:
                    col = BAD if (name == "BellmanFloydGuide" and u == 2 and v == 4) else ACCENT
                    self.play(
                        edge_lines[(u, v)].animate.set_color(col).set_stroke(width=3.4),
                        nodes[v][0].animate.set_stroke(col, 2.6).set_fill(ACCENT_FILL if col == ACCENT else BAD_FILL, 1),
                        Transform(badges[v], code(f"d={new_d}", 17, col).move_to(badges[v])),
                        rate_func=smooth, run_time=0.35,
                    )
                return
            if name == "BridgesGuide":
                bridge_edge = edge_lines[(1, 3)]
                lbl = code("Tarjan Bridge: low[3] > tin[1]  (removal splits components)", 18, BAD).move_to([0, 2.2, 0])
                self.play(
                    *(nodes[u][0].animate.set_stroke(ACCENT, 2.3).set_fill(ACCENT_FILL, 1) for u in (0, 1, 2)),
                    *(nodes[u][0].animate.set_stroke(AMBER, 2.3).set_fill(AMBER_FILL, 1) for u in (3, 4, 5)),
                    bridge_edge.animate.set_color(BAD).set_stroke(width=4.2),
                    FadeIn(lbl),
                    run_time=0.65,
                )
                self.play(Indicate(bridge_edge, color=BAD, scale_factor=1.18), run_time=0.55)
                return
            if name == "MstGuide":
                for u, v in [(1, 2), (3, 4), (0, 1), (2, 4), (4, 5)]:
                    self.play(
                        edge_lines[(u, v)].animate.set_color(ACCENT).set_stroke(width=3.6),
                        nodes[u][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1),
                        nodes[v][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1),
                        run_time=0.32,
                    )
                self.play(edge_lines[(0, 2)].animate.set_color(BAD).set_opacity(0.28),
                          edge_lines[(1, 3)].animate.set_color(BAD).set_opacity(0.28), run_time=0.35)
                return
            for layer in [[0], [1, 2], [3, 4], [5]]:
                rings = VGroup(*(Circle(radius=0.46, stroke_color=ACCENT, stroke_width=2.2).move_to(nodes[u]) for u in layer))
                self.play(
                    *(nodes[u][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1) for u in layer),
                    Create(rings),
                    run_time=0.35,
                )
                self.play(FadeOut(rings), run_time=0.14)
            return

        # =====================================================================
        # 6. DATA STRUCTURES: DSU Forest, Fenwick BIT Bars, Segment Tree, Monotonic Stack
        # =====================================================================
        if name == "DsuGuide":
            chain_pos = {0: (-2.5, 1.7), 1: (-3.6, 0.7), 2: (-3.6, -0.35), 3: (-3.6, -1.4)}
            star_pos = {0: (2.2, 1.45), 1: (0.6, -0.45), 2: (2.2, -0.45), 3: (3.8, -0.45)}
            cnodes = {k: gnode(str(k), p, r=0.29) for k, p in chain_pos.items()}
            cedges = VGroup(*(gedge(cnodes[k], cnodes[k - 1], directed=True, r=0.3)[0] for k in (1, 2, 3)))
            lbl1 = code("Uncompressed chain", 17, BAD).move_to([-3.0, 2.28, 0])
            self.play(FadeIn(VGroup(*cnodes.values())), Create(cedges), FadeIn(lbl1), run_time=0.45)
            snodes = {k: gnode(str(k), p, r=0.29, stroke=ACCENT, fill=ACCENT_FILL) for k, p in star_pos.items()}
            sedges = VGroup(*(gedge(snodes[k], snodes[0], directed=True, color=ACCENT, r=0.3)[0] for k in (1, 2, 3)))
            lbl2 = code("Path compression + union by size -> O(α(N))", 17, ACCENT).move_to([2.2, 2.28, 0])
            arrow_mid = Arrow([-1.3, 0.4, 0], [0.1, 0.4, 0], color=ACCENT, stroke_width=3.0)
            self.play(Create(arrow_mid), FadeIn(VGroup(*snodes.values())), Create(sedges), FadeIn(lbl2), run_time=0.85)
            return

        if name in ("FenwickGuide", "OrderedSetGuide"):
            cells, grp = array_row([3, 1, 4, 1, 5, 9, 2, 6], y=1.4, w=0.82, h=0.62, show_idx=False, name="A")
            self.play(FadeIn(grp), run_time=0.35)
            bars = VGroup()
            specs = [
                (1, 0, 0, 0.42), (2, 0, 1, -0.08), (3, 2, 2, 0.42), (4, 0, 3, -0.58),
                (5, 4, 4, 0.42), (6, 4, 5, -0.08), (7, 6, 6, 0.42), (8, 0, 7, -1.08),
            ]
            for idx_1, l_i, r_i, y_pos in specs:
                span = VGroup(*cells[l_i:r_i + 1])
                b = RoundedRectangle(width=span.width, height=0.36, corner_radius=0.05,
                                     stroke_color=STROKE, stroke_width=1.6, fill_color=CARD, fill_opacity=1)
                b.move_to([span.get_center()[0], y_pos, 0])
                t = code(f"bit[{idx_1}] (len={idx_1 & -idx_1})", 14, PAPER).move_to(b)
                bars.add(VGroup(b, t))
            self.play(LaggedStart(*(FadeIn(b) for b in bars), lag_ratio=0.07), run_time=0.55)
            for active_i in (6, 5, 3):  # 7 -> 6 -> 4 via i -= i & -i
                self.play(
                    bars[active_i][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1),
                    bars[active_i][1].animate.set_color(ACCENT),
                    run_time=0.35,
                )
            return

        if name in ("SegmentTreeGuide", "EulerTourGuide", "LcaGuide", "TreeDpGuide", "TrieGuide"):
            tree_pos = {
                1: (0.0, 1.75),
                2: (-2.7, 0.55), 3: (2.7, 0.55),
                4: (-4.1, -0.75), 5: (-1.3, -0.75), 6: (1.3, -0.75), 7: (4.1, -0.75),
            }
            labels_map = {
                1: "[0..3]=19" if name == "SegmentTreeGuide" else ("root" if name == "TrieGuide" else "1"),
                2: "[0..1]=8" if name == "SegmentTreeGuide" else ("0" if name == "TrieGuide" else "2"),
                3: "[2..3]=11" if name == "SegmentTreeGuide" else ("1" if name == "TrieGuide" else "3"),
                4: "A[0]=3" if name == "SegmentTreeGuide" else "4",
                5: "A[1]=5" if name == "SegmentTreeGuide" else "5",
                6: "A[2]=4" if name == "SegmentTreeGuide" else "6",
                7: "A[3]=7" if name == "SegmentTreeGuide" else "7",
            }
            tnodes = {
                k: box_cell(labels_map[k], w=1.45, h=0.62, size=17).move_to([p[0], p[1], 0])
                if name == "SegmentTreeGuide" else gnode(labels_map[k], p, r=0.32)
                for k, p in tree_pos.items()
            }
            pairs = [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7)]
            tedges = VGroup(*(Line(tnodes[a].get_bottom(), tnodes[b].get_top(), color=STROKE, stroke_width=2.0)
                              for a, b in pairs))
            self.play(Create(tedges), FadeIn(VGroup(*tnodes.values())), run_time=0.45)
            if name == "LcaGuide":
                arc1 = ArcBetweenPoints(tnodes[4].get_center(), tnodes[1].get_center(), angle=-1.1, color=ACCENT, stroke_width=3.0)
                arc2 = ArcBetweenPoints(tnodes[6].get_center(), tnodes[1].get_center(), angle=1.1, color=AMBER, stroke_width=3.0)
                lbl = code("Binary lifting 2^k jumps -> LCA(4, 6) = 1 in O(log N)", 18, ACCENT).move_to([0, -1.6, 0])
                self.play(Create(arc1), Create(arc2), tnodes[1][0].animate.set_stroke(ACCENT, 3.0), FadeIn(lbl), run_time=0.8)
                return
            if name == "EulerTourGuide":
                t_cells, t_grp = array_row([1, 2, 4, 5, 3, 6, 7], y=-1.55, w=0.68, h=0.52, show_idx=False, name="tin")
                self.play(FadeIn(t_grp), run_time=0.3)
                for idx_t, node_id in enumerate((1, 2, 4, 5, 3, 6, 7)):
                    self.play(
                        tnodes[node_id][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1),
                        t_cells[idx_t][0].animate.set_stroke(ACCENT, 2.3).set_fill(ACCENT_FILL, 1),
                        run_time=0.18,
                    )
                return
            for k in (4, 5, 2, 6, 7, 3, 1):
                self.play(tnodes[k][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1), run_time=0.2)
            return

        if name == "MonotonicGuide":
            heights = [2, 1, 5, 6, 2, 3]
            hist = VGroup()
            for i, h_val in enumerate(heights):
                h = 0.33 * h_val
                b = Rectangle(width=0.68, height=h, stroke_color=STROKE, stroke_width=1.8, fill_color=CARD, fill_opacity=1)
                b.move_to([-3.8 + i * 0.76, -1.2 + h / 2, 0])
                t = code(h_val, 17, PAPER).move_to(b.get_top() + DOWN * 0.2)
                hist.add(VGroup(b, t))
            well = VGroup(
                Line([1.5, 1.6, 0], [1.5, -1.2, 0], color=ACCENT, stroke_width=2.4),
                Line([1.5, -1.2, 0], [4.2, -1.2, 0], color=ACCENT, stroke_width=2.4),
                Line([4.2, -1.2, 0], [4.2, 1.6, 0], color=ACCENT, stroke_width=2.4),
                code("MONOTONIC STACK", 16, ACCENT).move_to([2.85, 1.9, 0]),
            )
            self.play(FadeIn(hist), Create(well), run_time=0.45)
            s_items = VGroup(
                box_cell("idx 1 (h=1)", w=2.2, h=0.52, stroke=ACCENT, fill=ACCENT_FILL, size=17).move_to([2.85, -0.85, 0]),
                box_cell("idx 2 (h=5)", w=2.2, h=0.52, stroke=ACCENT, fill=ACCENT_FILL, size=17).move_to([2.85, -0.25, 0]),
                box_cell("idx 3 (h=6)", w=2.2, h=0.52, stroke=ACCENT, fill=ACCENT_FILL, size=17).move_to([2.85, 0.35, 0]),
            )
            for k, item in zip((1, 2, 3), s_items):
                self.play(hist[k][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1), FadeIn(item, shift=DOWN * 0.2), run_time=0.32)
            self.play(
                hist[4][0].animate.set_stroke(BAD, 2.4),
                FadeOut(s_items[2], shift=UP * 0.3),
                FadeOut(s_items[1], shift=UP * 0.3),
                run_time=0.5,
            )
            return

        # =====================================================================
        # 7. DYNAMIC PROGRAMMING: 1D Capacity Sweeps & 2D DP Matrices
        # =====================================================================
        if name in ("KnapsackGuide", "GridDpGuide", "LisLcsGuide", "IntervalDpGuide", "BitmaskDpGuide"):
            if name == "KnapsackGuide":
                vals = [0, 0, 0, 5, 6, 8, 11, 14]
                cells, grp = array_row(vals, y=0.45, name="dp")
                dir_lbl = code(
                    "0/1 Knapsack: sweep capacity W -> wt BACKWARD (single use)" if index != 2
                    else "Unbounded Knapsack: sweep wt -> W FORWARD (unlimited reuse)",
                    19, ACCENT if index != 2 else AMBER,
                ).move_to([0, 1.85, 0])
                self.play(FadeIn(grp), FadeIn(dir_lbl), run_time=0.4)
                indices = [7, 6, 5, 4, 3] if index != 2 else [3, 4, 5, 6, 7]
                for idx_w in indices:
                    src_w = idx_w - 3
                    arc = ArcBetweenPoints(cells[src_w].get_top(), cells[idx_w].get_top(), angle=-0.85, color=ACCENT, stroke_width=2.5)
                    self.play(Create(arc), cells[idx_w][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1), run_time=0.28)
                    self.play(FadeOut(arc), run_time=0.1)
                return
            mat_vals = [
                ["1", "1", "1", "1"],
                ["1", "#" if name == "GridDpGuide" else "2", "1" if name == "GridDpGuide" else "3", "2" if name == "GridDpGuide" else "4"],
                ["1", "1" if name == "GridDpGuide" else "3", "2" if name == "GridDpGuide" else "6", "4" if name == "GridDpGuide" else "10"],
            ]
            grid_cells = []
            grid_grp = VGroup()
            for r in range(3):
                row_list = []
                for c in range(4):
                    v = mat_vals[r][c]
                    is_wall = v == "#"
                    cell_m = box_cell(
                        v, w=0.95, h=0.78,
                        stroke=BAD if is_wall else STROKE,
                        fill=BAD_FILL if is_wall else CARD,
                        color=BAD if is_wall else PAPER,
                    ).move_to([-1.6 + c * 1.08, 1.25 - r * 0.9, 0])
                    row_list.append(cell_m)
                    grid_grp.add(cell_m)
                grid_cells.append(row_list)
            self.play(FadeIn(grid_grp), run_time=0.4)
            for r in range(3):
                for c in range(4):
                    if mat_vals[r][c] == "#":
                        continue
                    self.play(grid_cells[r][c][0].animate.set_stroke(ACCENT, 2.4).set_fill(ACCENT_FILL, 1), run_time=0.13)
            return

        # =====================================================================
        # 8. MATH, SIEVE, BITWISE, GCD, MODCOMB & NIM
        # =====================================================================
        if name == "SieveGuide":
            grid = VGroup()
            cell_map = {}
            for k, n_val in enumerate(range(2, 26)):
                r, c = divmod(k, 8)
                m = box_cell(n_val, w=0.82, h=0.68, size=19).move_to([-3.2 + c * 0.92, 1.35 - r * 0.82, 0])
                cell_map[n_val] = m
                grid.add(m)
            self.play(FadeIn(grid), run_time=0.4)
            for p in (2, 3, 5):
                self.play(cell_map[p][0].animate.set_stroke(ACCENT, 2.8).set_fill(ACCENT_FILL, 1), run_time=0.22)
                mults = [m for m in range(p * p, 26, p)]
                if mults:
                    self.play(
                        *(cell_map[m][0].animate.set_stroke(BAD, 2.0).set_fill(BAD_FILL, 1) for m in mults),
                        *(cell_map[m][1].animate.set_color(BAD) for m in mults),
                        run_time=0.38,
                    )
            return

        if name in ("BitwiseGuide", "NimGuide"):
            if name == "NimGuide":
                piles = VGroup()
                for idx_p, (cnt, bin_s) in enumerate([(3, "011"), (5, "101"), (7, "111")]):
                    x_pos = -4.8 + idx_p * 1.95
                    stones = VGroup(*(
                        Circle(radius=0.16, stroke_color=ACCENT, fill_color=ACCENT, fill_opacity=0.35)
                        .move_to([x_pos + (s % 2) * 0.4, -0.5 + (s // 2) * 0.4, 0])
                        for s in range(cnt)
                    ))
                    lbl = code(f"pile={cnt} ({bin_s})", 15, PAPER).move_to([x_pos + 0.2, -1.1, 0])
                    piles.add(VGroup(stones, lbl))
                xor_box = box_cell("3 ^ 5 ^ 7 = 1 != 0 (N-state)", w=4.8, h=0.86,
                                   stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=17).move_to([3.1, 0.35, 0])
                self.play(FadeIn(piles), FadeIn(xor_box), run_time=0.5)
                self.play(
                    FadeOut(piles[0][0][-1], shift=UP * 0.3),
                    Transform(xor_box[1], code("3->2:  2 ^ 5 ^ 7 = 0 (P-state)", 17, AMBER, width=4.4).move_to(xor_box)),
                    run_time=0.75,
                )
                return
            b1, g1 = array_row(list("00101100"), y=1.15, w=0.68, h=0.62, show_idx=False, name="x    ")
            b2, g2 = array_row(list("00101011"), y=0.25, w=0.68, h=0.62, show_idx=False, name="x - 1")
            b3, g3 = array_row(list("00101000"), y=-0.65, w=0.68, h=0.62, show_idx=False, name="x&x-1")
            self.play(FadeIn(g1), FadeIn(g2), FadeIn(g3), run_time=0.45)
            self.play(
                b1[5][0].animate.set_stroke(BAD, 2.6).set_fill(BAD_FILL, 1),
                b3[5][0].animate.set_stroke(ACCENT, 2.6).set_fill(ACCENT_FILL, 1),
                *(b3[k][0].animate.set_stroke(ACCENT, 2.2) for k in (2, 4)),
                run_time=0.8,
            )
            return

        if name in ("GcdGuide", "ModCombGuide"):
            steps_txt = [
                ("gcd(48, 18)", "48 = 2 * 18 + 12", ACCENT),
                ("gcd(18, 12)", "18 = 1 * 12 + 6", AMBER),
                ("gcd(12, 6)", "12 = 2 * 6 + 0  ->  gcd = 6", ACCENT),
            ] if name == "GcdGuide" else [
                ("fact[i] = i * fact[i-1] % MOD", "O(N) forward table", ACCENT),
                ("inv_fact[N] = pow(fact[N], MOD-2, MOD)", "Fermat inverse at top", AMBER),
                ("nCr = fact[n] * inv_fact[r] % MOD * inv_fact[n-r] % MOD", "O(1) per query", ACCENT),
            ]
            rows = VGroup(*(
                box_cell(f"{lhs}    |    {rhs}", w=9.8, h=0.72, stroke=col,
                         fill=ACCENT_FILL if col == ACCENT else AMBER_FILL, color=col, size=18)
                for lhs, rhs, col in steps_txt
            )).arrange(DOWN, buff=0.25).move_to([0, 0.4, 0])
            for r_mob in rows:
                self.play(FadeIn(r_mob, shift=RIGHT * 0.2), run_time=0.42)
            return

        # =====================================================================
        # 9. STRINGS: Dual Aligned Text/Pattern Tapes & Z-Box Window
        # =====================================================================
        if name in ("RollingHashGuide", "KmpGuide", "ZAlgoGuide"):
            t_chars, g_t = array_row(list("ABABACAB"), y=1.1, w=0.76, h=0.68, name="T")
            p_chars, g_p = array_row(list("ABAC"), y=-0.1, w=0.76, h=0.68, show_idx=False, name="P")
            g_p.align_to(t_chars[0], LEFT).shift(LEFT * 0.72)
            self.play(FadeIn(g_t), FadeIn(g_p), run_time=0.4)
            for k in range(3):
                self.play(
                    t_chars[k][0].animate.set_stroke(ACCENT, 2.3).set_fill(ACCENT_FILL, 1),
                    p_chars[k][0].animate.set_stroke(ACCENT, 2.3).set_fill(ACCENT_FILL, 1),
                    run_time=0.2,
                )
            self.play(t_chars[3][0].animate.set_stroke(BAD, 2.4), p_chars[3][0].animate.set_stroke(BAD, 2.4), run_time=0.28)
            shift_dx = t_chars[2].get_center()[0] - t_chars[0].get_center()[0]
            self.play(
                g_p.animate.shift(RIGHT * shift_dx),
                *(t_chars[k][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1) for k in range(2, 6)),
                *(p_chars[k][0].animate.set_stroke(ACCENT, 2.5).set_fill(ACCENT_FILL, 1) for k in range(4)),
                rate_func=smooth, run_time=0.75,
            )
            return

        # =====================================================================
        # 10. PREFIX SUMS, MO'S SQRT BLOCKS & CONSTRUCTIVE
        # =====================================================================
        if name in ("PrefixSumsGuide", "MoSqrtGuide", "ConstructiveGuide"):
            arr = [3, 1, 4, 1, 5, 9, 2, 6]
            c1, g1 = array_row(arr, y=1.15, w=0.78, h=0.66, name="A")
            second = [0, 3, 4, 8, 9, 14, 23, 25] if name == "PrefixSumsGuide" else (
                [0, 0, 0, 1, 1, 1, 2, 2] if name == "MoSqrtGuide" else [1, 8, 2, 7, 3, 6, 4, 5]
            )
            sec_name = "P" if name == "PrefixSumsGuide" else ("blk" if name == "MoSqrtGuide" else "zig")
            c2, g2 = array_row(second, y=-0.25, w=0.78, h=0.66, name=sec_name)
            self.play(FadeIn(g1), FadeIn(g2), run_time=0.4)
            for k in range(1, 6):
                self.play(
                    c1[k][0].animate.set_stroke(ACCENT, 2.3).set_fill(ACCENT_FILL, 1),
                    c2[k][0].animate.set_stroke(AMBER, 2.3).set_fill(AMBER_FILL, 1),
                    run_time=0.24,
                )
            return

        # =====================================================================
        # 11. GENERAL GUIDES (PythonGuide, ContestGuide, FastIoGuide, CatalogGuide)
        # =====================================================================
        if name == "PythonGuide" and index == 2:
            grid = VGroup(*(Square(0.24, stroke_width=1.2, color=ACCENT) for _ in range(64)))
            grid.arrange_in_grid(rows=8, cols=8, buff=0.03).move_to([-2.4, 0.35, 0])
            summary = box_cell("1,000 x 1,000 = 1,000,000 visits", w=5.2, h=0.95,
                               stroke=ACCENT, fill=ACCENT_FILL, color=ACCENT, size=19).move_to([2.2, 0.35, 0])
            self.play(Create(grid), run_time=0.55)
            self.play(grid[:16].animate.set_fill(ACCENT, opacity=0.75), FadeIn(summary, shift=LEFT * 0.2), run_time=0.6)
            return

        cards = VGroup(*(
            box_cell(v, w=3.3, h=1.05, stroke=ACCENT if i == 2 else STROKE,
                     fill=ACCENT_FILL if i == 2 else CARD,
                     color=ACCENT if i == 2 else PAPER, size=20)
            for i, v in enumerate(list(values)[:3])
        )).arrange(RIGHT, buff=0.65).move_to([0, 0.35, 0])
        self.play(FadeIn(cards[0], shift=RIGHT * 0.2), run_time=0.32)
        for a, b in zip(cards, cards[1:]):
            arr_ln = Arrow(a.get_right(), b.get_left(), buff=0.08, color=ACCENT, stroke_width=2.6)
            self.play(Create(arr_ln), FadeIn(b, shift=RIGHT * 0.2), run_time=0.38)
        self.play(Indicate(cards[-1], color=ACCENT, scale_factor=1.04), run_time=0.35)


for _scene_name in LESSONS:
    globals()[_scene_name] = type(_scene_name, (Guide,), {})
