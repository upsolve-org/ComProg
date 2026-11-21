"""Render with Manim Community 0.22. AUDIO_DIR holds the Gemini WAV clips.

Every lesson family gets a dedicated animated visualizer. `construct()` wires
each beat to its cached narration, its WebVTT cue and its visualizer.
"""
import json
import os
import random
import re
import wave
from functools import lru_cache
from pathlib import Path

import numpy as np
from manim import (
    DOWN, LEFT, RIGHT, UP, Axes, Circle, Create, DashedVMobject, Dot, FadeIn,
    FadeOut, Group, Indicate, LaggedStart, Line, MathTex, Mobject, Rectangle, RoundedRectangle,
    Scene, Square, Text, Transform, TransformFromCopy, VGroup, VMobject, Write,
    config, smooth,
)

ROOT = Path(__file__).resolve().parent
LESSONS = json.loads((ROOT / "lessons.json").read_text(encoding="utf-8-sig"))
PAPER = "#F2F2EF"
MUTED = "#A1A1AA"
WELL = "#141414"
CARD = "#262626"
STROKE = "#3A3A3A"
ACCENT = "#46C94C"
ACCENT_DARK = "#157A1A"
BAD = "#F26B61"
DUST = "#2B2B2B"
config.background_color = "#171717"
config.disable_caching = True

MONO = "Cascadia Mono"
SANS = "Segoe UI"


def _cached(factory):
    """Text() is slow, so identical strings reuse one (copied) mobject."""

    def build(value, size=24, color=PAPER):
        key = (str(value), size, str(color))
        pool = _POOL.setdefault(_CTX[0] if _CTX else "", {})
        if key not in pool:
            pool[key] = factory(str(value), size, color)
        return pool[key].copy()

    return build


_POOL = {}
_CTX = []
label = _cached(lambda v, s, c: Text(v, font=SANS, font_size=s, color=c))
mono = _cached(lambda v, s, c: Text(v, font=MONO, font_size=s, color=c))


def fitw(mob, width):
    if mob.width > width:
        mob.scale_to_fit_width(width)
    return mob


def row(values, colors=None, size=24, pad=0.1, color=None):
    texts = VGroup(*(mono(v, size, (colors or {}).get(i, color or PAPER)) for i, v in enumerate(values)))
    return texts.arrange(RIGHT, buff=pad)


def cell(text, size=28, side=0.72, fill=WELL, stroke=STROKE, color=PAPER, width=None):
    box = RoundedRectangle(
        width=width or side, height=side, corner_radius=0.08,
        stroke_color=stroke, stroke_width=1.6, fill_color=fill, fill_opacity=1,
    )
    return VGroup(box, mono(text, size, color).move_to(box))


def chip(text, color=PAPER, size=22):
    box = RoundedRectangle(width=max(0.9, 0.26 * len(str(text)) + 0.4), height=0.62,
                           corner_radius=0.08, stroke_color=STROKE, stroke_width=1.4,
                           fill_color=CARD, fill_opacity=1)
    return VGroup(box, mono(text, size, color).move_to(box))


def arrow(start, end, color=MUTED, width=2.4, buff=0.06):
    return Line(start, end, color=color, stroke_width=width, buff=buff)


class TNode(VGroup):
    def __init__(self, text, r=0.27, fill=CARD, stroke=STROKE, size=22):
        super().__init__()
        self.circle = Circle(radius=r, stroke_color=stroke, stroke_width=1.8, fill_color=fill, fill_opacity=1)
        self.text = mono(text, size, PAPER).move_to(self.circle)
        self.add(self.circle, self.text)

    def paint(self, fill, stroke, color=PAPER):
        self.circle.set_fill(fill, 1).set_stroke(stroke)
        self.text.set_color(color)


LEAF_TREE = {"start": 1, "kids": {1: [2, 3], 2: [4, 5], 3: [6]}, "place": {
    1: (0.0, 1.15), 2: (-2.5, 0.1), 3: (2.5, 0.1), 4: (-3.6, -1.1), 5: (-1.4, -1.1), 6: (2.5, -1.1)}}
STEM_TREE = {"start": 4, "kids": {4: [2, 6], 2: [1, 3], 6: [5, 7]}, "place": {
    4: (0.0, 1.3), 2: (-2.6, 0.45), 6: (2.6, 0.45),
    1: (-4.0, -0.45), 3: (-1.4, -0.45), 5: (1.4, -0.45), 7: (4.0, -0.45)}}

POS_GRAPH = [(0, 3.2), (1, 2.4), (2, 3.2), (3, 1.5), (4, 2.7), (5, 0.6), (6, 1.9)]
POS_TOP = [(0, 3.3), (1, 2.4), (2, 3.3), (3, 1.5), (4, 0.2), (5, 2.1)]
POS_CONNECT = [(0, 4.4), (1, 2.0), (2, 4.4), (3, 2.0), (4, 0.8), (5, 5.0), (6, 3.2), (7, -0.6)]
POS_BRIDGE = [(0, 3.5), (1, 0.7), (2, 4.2), (3, 0.7), (4, -1.0), (5, 5.0), (6, 3.4)]


class TreeG:
    def __init__(self, spec, r=0.27, size=22, node_text=None):
        self.spec = spec
        self.center = np.array([0.0, 0.15, 0.0])
        self.nodes = {
            k: TNode((node_text(k) if node_text else str(k)), r, size=size).move_to(
                self.center + np.array([*p, 0.0]))
            for k, p in spec["place"].items()
        }
        self.edges = VGroup(*(
            Line(self.nodes[a].get_center(), self.nodes[b].get_center(),
                 color=STROKE, stroke_width=2.0, buff=r * 0.92 + 0.01)
            for a, kids in spec["kids"].items() for b in kids))
        self.all = VGroup(self.edges, *self.nodes.values())

    def __getitem__(self, k):
        return self.nodes[k]

    def pos(self, k):
        return self.nodes[k].get_center()

    def from_root(self, root):
        kids = {}
        parent = {root: None}
        queue = [root]
        while queue:
            u = queue.pop(0)
            nxt = [v for v in self.spec["kids"].get(u, []) if v != parent.get(u)]
            kids[u] = nxt
            for v in nxt:
                parent[v] = u
                queue.append(v)
        return kids

    def chain(self, depth, width=0.5):
        nodes = {}
        for k in range(depth + 1):
            x = 0.1 + width * k - width * depth / 2
            nodes[k] = TNode(str(k), 0.24, size=20).move_to([x, 0.55, 0])
        edges = VGroup(*(
            Line(nodes[k].get_center(), nodes[k + 1].get_center(), color=STROKE,
                 stroke_width=2.0, buff=0.24)
            for k in range(depth)))
        return nodes, edges

    def forest(self, parent, y_rows):
        nodes, edges = {}, VGroup()
        for x, p in parent.items():
            nodes[x] = TNode(str(x), 0.26, size=20).move_to([0.55 * x, y_rows.get(x, 0.6), 0])
        for x, p in parent.items():
            if p is not None:
                edges.add(Line(nodes[x].get_center(), nodes[p].get_center(),
                               color=STROKE, stroke_width=2.0, buff=0.25))
        return nodes, edges


class GraphG:
    def __init__(self, edges, pos, directed=False, weighted=True, r=0.27, node_text=None):
        self.r = r
        self.nodes = {i: TNode((node_text(i) if node_text else str(i)), r, size=21)
                      .move_to([*pos[i], 0]) for i in range(len(pos))}
        self.edges = {}
        self.labels = {}
        for u, v, w in edges:
            ln = Line(self.nodes[u].get_center(), self.nodes[v].get_center(),
                      color=STROKE, stroke_width=2.0, buff=r * 0.94 + 0.01)
            if directed:
                ln.add_tip(tip_length=0.15, tip_width=0.12)
            self.edges[(u, v)] = ln
            wlbl = mono(str(w), 17, PAPER).move_to(ln).shift(UP * 0.15 + RIGHT * 0.1)
            wlbl.set_opacity(0)
            bg = Rectangle(width=wlbl.width + 0.1, height=wlbl.height + 0.04,
                           fill_color="#171717", fill_opacity=1, stroke_width=0).move_to(wlbl)
            self.labels[(u, v)] = VGroup(bg, wlbl)
        self.edge_layer = VGroup(*self.edges.values())
        self.label_layer = VGroup(*self.labels.values())
        self.node_layer = VGroup(*self.nodes.values())
        self.all = VGroup(self.edge_layer, self.label_layer, self.node_layer)

    def pos(self, k):
        return self.nodes[k].get_center()

    def tree_edges(self, edges):
        return VGroup(*[self.edges[(u, v)] for u, v in edges])


class DotArray(VGroup):
    def __init__(self, cols, rows=1, pitch=0.55, y=0.35, colors=None):
        super().__init__()
        self.cols, self.rows, self.pitch = cols, rows, pitch
        self.start = np.array([-pitch * (cols - 1) / 2 if rows == 1 else -2.0, y, 0.0])
        self.grid = [[Dot(self.at(r, c), radius=0.09, color=STROKE) for c in range(cols)]
                     for r in range(rows)]
        self.add(*[d for line in self.grid for d in line])
        self.colors = colors or {}

    def at(self, r=0, c=0):
        if self.rows == 1:
            return self.start + RIGHT * self.pitch * c
        return self.start + RIGHT * self.pitch * c + DOWN * self.pitch * r

    def color(self, r=0, c=0, color=ACCENT):
        self.colors[(r, c)] = color
        self.grid[r][c].set_color(color)

    def row_colors(self, r=0, color=None):
        for c in range(self.cols):
            self.color(r, c, color or self.colors.get(c, ACCENT))


class TNode(VGroup):
    def __init__(self, text, r=0.27, fill=CARD, stroke=STROKE, size=22):
        super().__init__()
        self.circle = Circle(radius=r, stroke_color=stroke, stroke_width=1.8, fill_color=fill, fill_opacity=1)
        self.text = mono(text, size, PAPER).move_to(self.circle)
        self.add(self.circle, self.text)

    def paint(self, fill, stroke, color=PAPER):
        self.circle.set_fill(fill, 1).set_stroke(stroke)
        self.text.set_color(color)


LEAF_TREE = {"start": 1, "kids": {1: [2, 3], 2: [4, 5], 3: [6]}, "place": {
    1: (0.0, 1.15), 2: (-2.5, 0.1), 3: (2.5, 0.1), 4: (-3.6, -1.1), 5: (-1.4, -1.1), 6: (2.5, -1.1)}}
STEM_TREE = {"start": 4, "kids": {4: [2, 6], 2: [1, 3], 6: [5, 7]}, "place": {
    4: (0.0, 1.3), 2: (-2.6, 0.45), 6: (2.6, 0.45),
    1: (-4.0, -0.45), 3: (-1.4, -0.45), 5: (1.4, -0.45), 7: (4.0, -0.45)}}

POS_GRAPH = [(0, 3.2), (1, 2.4), (2, 3.2), (3, 1.5), (4, 2.7), (5, 0.6), (6, 1.9)]
POS_TOP = [(0, 3.3), (1, 2.4), (2, 3.3), (3, 1.5), (4, 0.2), (5, 2.1)]
POS_CONNECT = [(0, 4.4), (1, 2.0), (2, 4.4), (3, 2.0), (4, 0.8), (5, 5.0), (6, 3.2), (7, -0.6)]
POS_BRIDGE = [(0, 3.5), (1, 0.7), (2, 4.2), (3, 0.7), (4, -1.0), (5, 5.0), (6, 3.4)]


class TreeG:
    def __init__(self, spec, r=0.27, size=22, node_text=None):
        self.spec = spec
        self.center = np.array([0.0, 0.15, 0.0])
        self.nodes = {
            k: TNode((node_text(k) if node_text else str(k)), r, size=size).move_to(
                self.center + np.array([*p, 0.0]))
            for k, p in spec["place"].items()
        }
        self.edges = VGroup(*(
            Line(self.nodes[a].get_center(), self.nodes[b].get_center(),
                 color=STROKE, stroke_width=2.0, buff=r * 0.92 + 0.01)
            for a, kids in spec["kids"].items() for b in kids))
        self.all = VGroup(self.edges, *self.nodes.values())

    def __getitem__(self, k):
        return self.nodes[k]

    def pos(self, k):
        return self.nodes[k].get_center()

    def from_root(self, root):
        kids, parent, queue = {}, {root: None}, [root]
        while queue:
            u = queue.pop(0)
            nxt = [v for v in self.spec["kids"].get(u, []) if v != parent.get(u)]
            kids[u] = nxt
            for v in nxt:
                parent[v] = u
                queue.append(v)
        return kids

    def chain(self, depth, width=0.5):
        nodes = {}
        for k in range(depth + 1):
            x = 0.1 + width * k - width * depth / 2
            nodes[k] = TNode(str(k), 0.24, size=20).move_to([x, 0.55, 0])
        edges = VGroup(*(
            Line(nodes[k].get_center(), nodes[k + 1].get_center(), color=STROKE,
                 stroke_width=2.0, buff=0.24)
            for k in range(depth)))
        return nodes, edges

    def forest(self, parent, y_rows):
        nodes, edges = {}, VGroup()
        for x, p in parent.items():
            nodes[x] = TNode(str(x), 0.26, size=20).move_to([0.55 * x, y_rows.get(x, 0.6), 0])
        for x, p in parent.items():
            if p is not None:
                edges.add(Line(nodes[x].get_center(), nodes[p].get_center(),
                               color=STROKE, stroke_width=2.0, buff=0.25))
        return nodes, edges


class GraphG:
    def __init__(self, edges, pos, directed=False, weighted=True, r=0.27, node_text=None):
        self.r = r
        self.nodes = {i: TNode((node_text(i) if node_text else str(i)), r, size=21)
                      .move_to([*pos[i], 0]) for i in range(len(pos))}
        self.edges = {}
        self.labels = {}
        for u, v, w in edges:
            ln = Line(self.nodes[u].get_center(), self.nodes[v].get_center(),
                      color=STROKE, stroke_width=2.0, buff=r * 0.94 + 0.01)
            if directed:
                ln.add_tip(tip_length=0.15, tip_width=0.12)
            self.edges[(u, v)] = ln
            wlbl = mono(str(w), 17, PAPER).move_to(ln).shift(UP * 0.15 + RIGHT * 0.1)
            wlbl.set_opacity(0)
            bg = Rectangle(width=wlbl.width + 0.1, height=wlbl.height + 0.04,
                           fill_color="#171717", fill_opacity=1, stroke_width=0).move_to(wlbl)
            self.labels[(u, v)] = VGroup(bg, wlbl)
        self.edge_layer = VGroup(*self.edges.values())
        self.label_layer = VGroup(*self.labels.values())
        self.node_layer = VGroup(*self.nodes.values())
        self.all = VGroup(self.edge_layer, self.label_layer, self.node_layer)

    def pos(self, k):
        return self.nodes[k].get_center()

    def tree_edges(self, edges):
        found = VGroup()
        for u, v in edges:
            for a, b in ((u, v), (v, u)):
                if (a, b) in self.edges:
                    found.add(self.edges[(a, b)])
                    break
        return found

    def kind(self):
        return "graph"

    def step(self, cells, i, color=ACCENT):
        """Delay the markers, then paint one cell as `color`."""
        return VGroup(*(cells[j].animate(0.1 + 0.09 * j).set_stroke(color, 1.6) for j in range(i + 1)))

class Guide(Scene):
    # filled in by the family mixins below
    def draw(self, index, beats):
        raise NotImplementedError

    def construct(self):
        name = type(self).__name__
        _CTX[:] = [name]
        cues = ["WEBVTT", ""]
        self._beats = LESSONS[name]
        for index, (title, values, narration) in enumerate(LESSONS[name]):
            wav = Path(os.environ["AUDIO_DIR"]) / f"{name}{index}.wav"
            with wave.open(str(wav)) as clip:
                duration = clip.getnframes() / clip.getframerate()
            start = self.time
            self.add_sound(str(wav))
            stage = len(self.mobjects)
            self._stage = stage
            tag = mono(f"{index + 1:02d} // {title.upper()}", 16, ACCENT).move_to([-6.05, 3.42, 0], aligned_edge=LEFT)
            bar = Line(LEFT * 6.2, RIGHT * 6.2, color=STROKE, stroke_width=1.2).set_y(3.12)
            self.add(tag, bar)
            try:
                self.draw(index, values)
            except Exception:  # never lose a whole film to one diagram
                self.play(FadeOut(tag, bar, *self.beat_mobjects(stage)))
                self.fallback(value=values)
            if len(self.mobjects) <= stage + 2:
                self.fallback(value=values)
            span = max(8.2, duration, self.time - start + 0.15)
            self.wait(max(0.1, span - (self.time - start)))
            if index == 0:
                dy = 2.62 - min(2.62, min(m.get_top()[1] for m in self.beat_mobjects(stage)))
                self.play(*[m.animate.shift(DOWN * 0.6 if not dy else DOWN * (0.6 + dy))
                            for m in self.beat_mobjects(stage)], rate_func=smooth, run_time=0.4)
            self.layout(index, index == 0)
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", narration.strip()) if s.strip()]
            cursor = start
            total = sum(map(len, sentences))
            for sentence in sentences:
                end = cursor + duration * len(sentence) / total
                cues.extend([f"{stamp(cursor)} {stamp(end)}".replace(" ", " --> ", 1), sentence, ""])
                cursor = end
            self.end_beat(stage)
        (ROOT.parent / "public" / f"{name}.vtt").write_text("\n".join(cues), encoding="utf-8")

    def beat_mobjects(self, stage):
        """Everything added after object #stage, i.e. this beat's own drawing."""
        return list(self.mobjects[stage:])

    def end_beat(self, stage):
        self.play(*[FadeOut(m) for m in self.mobjects[stage:]], rate_func=smooth, run_time=0.3)

    def fallback(self, value=None):
        items = [chip(v) for v in (value or [])][:3]
        grp = VGroup(*items).arrange(RIGHT, buff=0.5).set_y(-0.4)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.2) for m in grp], lag_ratio=0.18), run_time=0.8)
        if len(grp) > 1:
            for a, b in zip(grp, grp[1:]):
                ln = Line(a.get_right(), b.get_left(), color=ACCENT, stroke_width=2.5, buff=0.1)
                self.play(Create(ln), run_time=0.3)


def chip(text):
    txt = mono(str(text), 22)
    fitw(txt, 3.4)
    box = RoundedRectangle(width=txt.width + 0.5, height=0.8, corner_radius=0.08,
                           stroke_color=ACCENT, stroke_width=1.6, fill_color="#16261A", fill_opacity=1)
    return VGroup(box, txt.move_to(box))


def stamp(seconds):
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02}.{ms % 1000:03}"


class Board(Guide):
    """Mixin of visual primitives shared by every lesson family."""

    # -- animated numbers -------------------------------------------------
    def sheet(self, beats, rng=7):
        out = []
        for beat in beats:
            values = beat[1] if len(beat) > 1 else beat
            for token in values:
                for word in str(token).replace(",", " ").split():
                    if re.fullmatch(r"\d+", word) and int(word) < 1000:
                        out.append(int(word))
        out = [n for n in out if 1 <= n <= 40]
        return out or list(range(2, 9))

    def series(self, beats, n, lo=1, hi=9, rng=11):
        res = random.Random(rng).choices(self.sheet(beats, rng), k=n)
        return [min(hi, max(lo, v)) for v in res]

    def ptr(self, text, color=ACCENT, size=22):
        grp = VGroup(
            mono(text, size, color),
            RoundedRectangle(width=0.46, height=0.5, corner_radius=0.06,
                             stroke_color=color, stroke_width=1.4, fill_opacity=0),
        )
        grp[1].move_to(grp[0])
        return grp

    def under(self, pointer, target, buff=0.1, dy=0):
        if isinstance(target, (list, tuple, np.ndarray)):
            target = np.array(target, dtype=float)
        pointer.next_to(target, DOWN, buff=buff)
        pointer.shift(DOWN * dy)
        return pointer

    def over(self, pointer, target, buff=0.1):
        if isinstance(target, (list, tuple, np.ndarray)):
            target = np.array(target, dtype=float)
        pointer.next_to(target, UP, buff=buff)
        return pointer

    def glide(self, movers, target, run_time=0.35):
        self.play(*[m.animate.next_to(target, DOWN, buff=0.1) for m in movers],
                  rate_func=smooth, run_time=run_time)

    # -- boards -----------------------------------------------------------
    def pyfloat(self, text, scale=1.0):
        box = RoundedRectangle(width=max(1.0, text.width + 0.4) * scale,
                               height=max(0.8, text.height + 0.3) * scale,
                               corner_radius=0.06, stroke_color=STROKE,
                               stroke_width=1.3, fill_color=CARD, fill_opacity=1)
        return VGroup(box, text.scale(scale).move_to(box))

    def array(self, values, colors=None, size=28, side=0.72, gap=0.12,
              y=0.35, idx=True, idx_colors=None, caption=None, name=None):
        colors = colors or {}
        cells = VGroup(*(cell(v, size, side,
                              fill=colors.get(i, {}).get("fill", WELL),
                              stroke=colors.get(i, {}).get("stroke", STROKE),
                              color=colors.get(i, {}).get("color", PAPER))
                         for i, v in enumerate(values)))
        cells.arrange(RIGHT, buff=gap)
        fitw(cells, 11.6)
        cells.move_to(np.array([0.0, y, 0.0]))
        cells.ordered = True
        grp = VGroup(cells)
        if idx:
            tags = VGroup(*(mono(str(i), 17, (idx_colors or {}).get(i, MUTED))
                            .next_to(c, DOWN, buff=0.08) for i, c in enumerate(cells)))
            grp.add(tags)
        if caption is not None:
            grp.add(caption.next_to(cells, UP, buff=0.2))
        grp.cells = cells
        grp.nodes = cells
        grp.idx = grp[-1] if idx and not caption else None
        if idx and caption is not None:
            grp.idx = grp[-2]
        grp.caption = caption
        if name is not None:
            head = mono(name, 19, MUTED).next_to(cells, LEFT, buff=0.3)
            grp.add(head)
            grp.head = head
        return grp

    def bracket(self, cells, color=ACCENT, pad=0.12, over=0.14):
        left, right = cells[0].get_left(), cells[-1].get_right()
        hl = left[0] - pad
        hr = right[0] + pad
        bar = Line([hl, right[1] + over, 0], [hr, right[1] + over, 0], color=color, stroke_width=3)
        lip = VGroup(
            Line(bar.get_start(), bar.get_start() + DOWN * 0.18, color=color, stroke_width=3),
            Line(bar.get_end(), bar.get_end() + DOWN * 0.18, color=color, stroke_width=3),
        )
        return VGroup(bar, lip)

    def box_at(self, cells, start, end, color=ACCENT, pad=0.1, height=None, y=None):
        piece = cells[start:end + 1]
        rect = Rectangle(width=piece.width + 2 * pad, height=height or (piece.height * 0.62),
                         stroke_color=color, stroke_width=2.2, fill_color=color, fill_opacity=0.08)
        if cells.width > piece.width + 1e-6:
            rect.move_to([piece.get_center()[0], cells.get_center()[1], 0])
        else:
            rect.move_to(cells)
        if y is not None:
            rect.set_y(y)
        return rect

    def callout(self, text, color=ACCENT, size=24):
        caption = mono(text, size, color)
        fitw(caption, 11.4)
        return caption.move_to([0.0, -1.85, 0.0])

    def math(self, text, color=PAPER, size=30, target=None):
        grp = MathTex(text, color=color, font_size=size)
        if target is not None:
            grp.next_to(target, DOWN, buff=0.3)
        return grp

    # -- transition helpers ----------------------------------------------
    def swap(self, cells, i, j, pos=None):
        a, b = cells[i], cells[j]
        pa = pos.get(i, a.get_center()) if pos else a.get_center()
        pb = pos.get(j, b.get_center()) if pos else b.get_center()
        self.play(a.animate.move_to(pb), b.animate.move_to(pa), rate_func=smooth, run_time=0.5)
        cells[i], cells[j] = b, a
        if pos:
            pos[i], pos[j] = pos[j], pos[i]

    def dismiss(self, *mobs):
        flat = []
        for m in mobs:
            if m is None:
                continue
            flat.extend(m) if isinstance(m, (list, tuple)) else flat.append(m)
        if flat:
            self.play(*[FadeOut(m, run_time=0.25) for m in flat])


HEAD_Y = 1.8
FOOT_Y = -2.65


class IndexFamily(Board):
    """Indexed arrays, windows, binary search, interval sorting, DP sweeps."""

    def tree_edges(self, edges):
        tree = getattr(self, "_last_tree", None)
        if tree is None:
            return VGroup()
        found = VGroup()
        for u, v in edges:
            ln = tree.edges.get((u, v)) or tree.edges.get((v, u))
            if ln is not None:
                found.add(ln)
        return found

    def prefix(self, beats):
        A = [3, 1, 4, 1, 5]
        tape = self.array([str(v) for v in A], size=24, side=0.66, y=0.9, name="A")
        pre = self.array(["0"] + [""] * 5, size=22, side=0.62, y=-0.35, name="P")
        self.play(FadeIn(tape), FadeIn(pre), run_time=0.45)
        self.play(FadeIn(mono("P[k] = A[0] + ... + A[k-1]", 20, PAPER).move_to([0, -1.35, 0])), run_time=0.4)
        run = 0
        for i, v in enumerate(A):
            run += v
            self.play(Indicate(tape.cells[i], color=ACCENT, scale_factor=1.2),
                      pre.cells[i + 1][1].animate.become(mono(str(run), 22, ACCENT).move_to(pre.cells[i + 1])),
                      run_time=0.25)
        pre.cells[1:].set_stroke(ACCENT, 1.6)
        box = self.box_at(pre.cells, 1, 3, ACCENT, y=pre.cells.get_center()[1])
        self.play(Create(box), Write(mono("sum [1..3] = P[4] - P[1] = 11 - 3 = 8", 20, ACCENT)
                                     .move_to([0, -1.35, 0])), run_time=0.5)
        self.play(Indicate(tape.cells[1:4], color=ACCENT, scale_factor=1.1), run_time=0.4)
        self.play(FadeIn(mono("one subtraction per range, O(1)", 19, MUTED).move_to([0, -2.0, 0])), run_time=0.4)

    def difference(self, beats):
        N = 9
        A = [0] * N
        zeros = self.array(["0"] * N, size=22, side=0.62, y=0.85, name="P")
        self.play(FadeIn(zeros), run_time=0.4)
        self.play(FadeIn(mono("range add [2, 6] by +4: touch only two slots", 20, PAPER).move_to([0, -0.9, 0])), run_time=0.4)
        self.play(Indicate(VGroup(zeros.cells[2], zeros.cells[7]), color=ACCENT, scale_factor=1.3), run_time=0.4)
        for i, v in ((2, "4"), (7, "-4")):
            self.play(zeros.cells[i][1].animate.become(mono(v, 22, ACCENT).move_to(zeros.cells[i])), run_time=0.25)
        self.play(zeros.cells[2].animate.set_stroke(ACCENT, 2), zeros.cells[7].animate.set_stroke(BAD, 2), run_time=0.25)
        run = 0
        for i in range(N):
            run += int(zeros.cells[i][1].text)
            self.play(zeros.cells[i][1].animate.become(mono(str(run), 22, PAPER if 2 <= i <= 6 else MUTED)
                                                       .move_to(zeros.cells[i])), run_time=0.12)
        self.play(FadeIn(mono("prefix scan turns the two edits into the real array", 19, ACCENT).move_to([0, -2.0, 0])), run_time=0.4)
        self.play(FadeIn(mono("k range updates then one scan: O(N + k)", 18, MUTED).move_to([0, -2.5, 0])), run_time=0.35)

    def two_pointers(self, beats):
        n = 9
        arr = sorted(self.series(beats, n))
        targets = sorted(self.series(beats[::-1], 2, 4, 16))
        tape = self.array(arr, caption=mono("sorted A", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.5)
        lo = self.ptr("L", ACCENT)
        hi = self.ptr("R", BAD)
        self.over(lo, tape.cells[0])
        self.over(hi, tape.cells[-1])
        self.play(FadeIn(lo, shift=DOWN * 0.15), FadeIn(hi, shift=DOWN * 0.15), run_time=0.5)
        self.play(Indicate(tape.cells[1], color=ACCENT, scale_factor=1.12), run_time=0.5)
        i, j, rounds = 0, n - 1, 0
        while i < j and rounds < 3:
            total = arr[i] + arr[j]
            note = self.callout(f"A[L] + A[R] = {arr[i]} + {arr[j]} = {total}", MUTED)
            self.play(Write(note), run_time=0.4)
            if total < targets[0] or rounds == 0:
                self.play(self._hop(lo, tape.cells, round(i + 1)), run_time=0.5)
                i += 1
            else:
                self.play(self._hop(hi, tape.cells, round(j - 1)), run_time=0.5)
                j -= 1
            self.dismiss(note)
            rounds += 1
        pair = self.box_at(tape.cells, i, j, ACCENT)
        hit = self.callout(f"stop: A[L] + A[R] = {arr[i]} + {arr[j]}", ACCENT)
        self.play(Create(pair), Write(hit), run_time=0.6)
        self.play(Indicate(tape.cells[i:j + 1], color=ACCENT, scale_factor=1.06), run_time=0.6)

    def _hop(self, pointer, cells, index):
        return pointer.animate.next_to(cells[index], UP, buff=0.1)

    def merge_two(self, beats):
        A = sorted([1, 4, 7, 9])
        B = sorted([2, 3, 8, 10])
        top = self.array([str(v) for v in A], size=24, side=0.62, y=0.75, name="A")
        bot = self.array([str(v) for v in B], size=24, side=0.62, y=-0.2, name="B")
        self.play(FadeIn(top, shift=RIGHT * 0.2), FadeIn(bot, shift=RIGHT * 0.2), run_time=0.5)
        out = VGroup(*(cell("", 24, 0.62) for _ in range(8)))
        out.arrange(RIGHT, buff=0.12).move_to([0, -1.35, 0])
        self.play(LaggedStart(*(FadeIn(c, scale=0.7) for c in out), lag_ratio=0.06), run_time=0.5)
        pa, pb = self.ptr("i", ACCENT, 18), self.ptr("j", ACCENT, 18)
        self.over(pa, top.cells[0])
        self.over(pb, bot.cells[0])
        self.play(FadeIn(pa), FadeIn(pb), run_time=0.25)
        i = j = 0
        for k in range(8):
            src, idx = (top, i) if j >= len(B) or (i < len(A) and A[i] <= B[j]) else (bot, j)
            val = A[i] if src is top else B[j]
            self.play(Indicate(src.cells[idx], color=ACCENT, scale_factor=1.2), run_time=0.25)
            self.play(TransformFromCopy(src.cells[idx], out[k]), run_time=0.25)
            out[k][1].become(mono(str(val), 24, PAPER).move_to(out[k]))
            if src is top:
                i += 1
                if i < len(A):
                    self.play(pa.animate.next_to(top.cells[i], UP, buff=0.1), run_time=0.15)
            else:
                j += 1
                if j < len(B):
                    self.play(pb.animate.next_to(bot.cells[j], UP, buff=0.1), run_time=0.15)
        self.play(*[out[c][0].animate.set_stroke(ACCENT, 1.6) for c in range(8)],
                  FadeIn(mono("merged, still sorted, O(n + m)", 20, ACCENT).move_to([0, -2.15, 0])), run_time=0.6)

    def sliding_window(self, beats):
        n, k = 9, 3
        arr = self.series(beats, n)
        tape = self.array(arr, caption=mono(f"window length {k}", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.5)
        window = self.box_at(tape.cells, 0, k - 1, ACCENT, y=tape.cells.get_center()[1])
        self.play(Create(window), run_time=0.5)
        best = (sum(arr[:k]), 0)
        total = sum(arr[:k])
        note = self.callout(f"window sum = {total}", ACCENT)
        self.play(Write(note), run_time=0.4)
        for s in range(1, n - k + 1):
            self.play(Indicate(tape.cells[s - 1], color=BAD, scale_factor=1.2), run_time=0.2)
            total = total - arr[s - 1] + arr[s + k - 1]
            new_w = self.box_at(tape.cells, s, s + k - 1, ACCENT, y=tape.cells.get_center()[1])
            self.play(Transform(window, new_w),
                      Transform(note, self.callout(f"-{arr[s - 1]} +{arr[s + k - 1]}: sum = {total}", ACCENT)),
                      run_time=0.45)
            if total > best[0]:
                best = (total, s)
        peak = self.box_at(tape.cells, best[1], best[1] + k - 1, ACCENT, y=tape.cells.get_center()[1])
        self.play(Transform(window, peak), Transform(note, self.callout(f"best sum = {best[0]}", ACCENT)), run_time=0.5)
        self.play(Indicate(window, color=ACCENT, scale_factor=1.05), run_time=0.6)

    def sweep_window(self, beats):
        n = 9
        arr = [3, 1, 4, 1, 5, 9, 2, 6, 5]
        vals = [str(v) for v in arr]
        cells = VGroup(*(cell(v, 24, 0.6) for v in vals))
        cells.arrange(RIGHT, buff=0.12).move_to([0, 0.45, 0])
        self.play(LaggedStart(*(FadeIn(c) for c in cells), lag_ratio=0.06), run_time=0.5)
        state = self.array([str(arr[0])], size=22, side=0.6, y=-0.7, idx=False, name="sum")
        self.play(FadeIn(state), FadeIn(mono("5 * 10", 20, PAPER).move_to([1.9, -0.7, 0])),
                  Indicate(state.cells[0], color=ACCENT, scale_factor=1.2), run_time=0.4)
        self.play(FadeIn(mono("array operand sizes", 19, MUTED).move_to([1.9, -1.25, 0])), run_time=0.3)
        flow = VGroup(*(mono(f"* {v}", 19, PAPER) for v in vals))
        flow[0].move_to(cells[0])
        for a, b in zip(flow, flow[1:]):
            b.move_to(a.get_center() + RIGHT * 0.62)
        self.play(flow.animate.shift(RIGHT * 3.1), run_time=1.2)
        for i in range(1, n):
            self.play(Transform(state.cells[0][1], mono(str(sum(arr[:i + 1])), 22, ACCENT).move_to(state.cells[0])), run_time=0.18)
        tag = mono("one pass, one running value per window step", 20, ACCENT).move_to([0, -2.0, 0])
        self.play(FadeIn(tag), run_time=0.4)

    def shrink_window(self, beats):
        n, limit = 9, 13
        arr = [4, 2, 1, 7, 8, 1, 2, 8, 1]
        tape = self.array([str(v) for v in arr], size=22, side=0.6, y=0.6,
                          caption=mono(f"longest window with sum <= {limit}", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.45)
        L = self.ptr("L", BAD, 18)
        self.over(L, tape.cells[0])
        self.play(FadeIn(L), run_time=0.2)
        total = 0
        best = (0, 0, 0)
        state = mono("sum = 0, longest = 0", 20, PAPER).move_to([0, -1.5, 0])
        self.play(Write(state), run_time=0.3)
        l = 0
        for r in range(n):
            total += arr[r]
            self.play(tape.cells[r].animate.set_stroke(ACCENT, 2), run_time=0.1)
            while total > limit and l <= r:
                self.play(Indicate(tape.cells[l], color=BAD, scale_factor=1.2),
                          tape.cells[l].animate.set_stroke(BAD, 1.6).set_opacity(0.35),
                          Transform(state, mono(f"sum {total} > {limit}: drop {arr[l]}", 20, BAD).move_to([0, -1.5, 0])),
                          run_time=0.2)
                total -= arr[l]
                l += 1
                self.play(L.animate.next_to(tape.cells[min(l, n - 1)], UP, buff=0.1), run_time=0.12)
            if r - l + 1 > best[0]:
                best = (r - l + 1, l, r)
            self.play(Transform(state, mono(f"window [{l}..{r}], sum = {total}, best = {best[0]}", 20, PAPER)
                                .move_to([0, -1.5, 0])), run_time=0.15)
        box = self.box_at(tape.cells, best[1], best[2], ACCENT, y=tape.cells.get_center()[1])
        self.play(Create(box), Transform(state, mono(f"longest = {best[0]} at [{best[1]}..{best[2]}]", 20, ACCENT)
                                         .move_to([0, -1.5, 0])), run_time=0.45)
        self.play(FadeIn(mono("each index enters once and leaves once", 19, MUTED).move_to([0, -2.05, 0])), run_time=0.4)

    def count_sub(self, beats):
        n = 11
        arr = [10, 10, 2, 3, 4, 5, 6, 7, 8, 9, 10]
        tape = self.array([str(v) for v in arr], size=19, side=0.55, y=0.35,
                          caption=mono("product < 100: add r - l + 1 windows", 18, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.45)
        holes = self.array(["x"] * 4, size=20, side=0.6, y=-1.3, idx=False, name="sum")
        holes.cells[1:].set_opacity(0)
        self.play(FadeIn(holes), run_time=0.3)
        prod, total, l = 1, 0, 0
        for r in range(n):
            prod *= arr[r]
            self.play(tape.cells[r].animate.set_stroke(ACCENT, 2), run_time=0.08)
            while prod >= 100 and l <= r:
                self.play(tape.cells[l].animate.set_stroke(BAD, 1.4), prod := prod // arr[l], 0,
                          holes.cells[0][1].animate.become(mono(str(prod), 20, ACCENT).move_to(holes.cells[0])),
                          run_time=0.2)
                l += 1
            total += r - l + 1
            self.play(Indicate(holes.cells[1], color=ACCENT, scale_factor=1.3),
                      holes.cells[1][1].animate.become(mono(f"+{r - l + 1}", 20, ACCENT).move_to(holes.cells[1])), run_time=0.18)
        self.play(holes.cells[1].animate.set_opacity(1), run_time=0.1)
        self.play(Indicate(tape.cells[:l], color=BAD, scale_factor=1.05), run_time=0.2)
        self.play(holes.cells[2].animate.set_opacity(1),
                  holes.cells[2][1].animate.become(mono(f"= {total}", 20, ACCENT).move_to(holes.cells[2])), run_time=0.3)
        ans = self.box_at(tape.cells, 0, n - 1, ACCENT, y=tape.cells.get_center()[1])
        self.play(Create(ans), Indicate(holes.cells[2], color=ACCENT, scale_factor=1.2), run_time=0.5)
        self.play(FadeIn(mono("count here, recover the products by dividing", 19, MUTED).move_to([0, -2.05, 0])), run_time=0.4)

    def binary_search(self, beats):
        n, target = 8, 3
        tape = self.array(["F" if i < target else "T" for i in range(n)],
                          colors={i: ({"stroke": ACCENT, "color": ACCENT, "fill": "#1E2B1F"} if i >= target else {}) for i in range(n)},
                          idx_colors={i: ACCENT if i >= target else BAD for i in range(n)},
                          y=1.25, caption=mono("predicate over candidate answers", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.5)
        lo, hi = self.ptr("lo", MUTED, 17), self.ptr("hi", MUTED, 17)
        midp = self.ptr("mid", ACCENT, 17)
        self.over(lo, tape.cells[0], buff=0.55)
        self.over(hi, tape.cells[-1], buff=0.55)
        self.play(FadeIn(lo, shift=DOWN * 0.15), FadeIn(hi, shift=DOWN * 0.15), run_time=0.45)
        state = mono("lo = 0, hi = 7", 19, PAPER).move_to([0, -1.0, 0])
        self.play(Write(state), run_time=0.3)
        rows = []
        L, R = 0, n - 1
        while L <= R:
            m = (L + R) // 2
            self.play(midp.animate.next_to(tape.cells[m], DOWN, buff=0.55),
                      Transform(state, mono(f"mid = ({L} + {R}) // 2 = {m}", 19, PAPER).move_to([0, -1.0, 0])), run_time=0.4)
            if m >= target:
                self.play(Indicate(tape.cells[m], color=ACCENT, scale_factor=1.18),
                          Transform(state, mono(f"mid = {m} = T: answer at mid or left", 19, ACCENT).move_to([0, -1.0, 0])), run_time=0.35)
                dim = VGroup(*[tape.cells[i] for i in range(m + 1, n)])
                self.play(dim.animate.set_opacity(0.25),
                          hi.animate.next_to(tape.cells[m], UP, buff=0.55).set_opacity(0.25), run_time=0.3)
                rows.append(f"halving {len(rows) + 1}: mid {m} = T, hi <- {m}")
                R = m - 1
            else:
                self.play(Indicate(tape.cells[m], color=BAD, scale_factor=1.18),
                          Transform(state, mono(f"mid = {m} = F: answer must be right", 19, BAD).move_to([0, -1.0, 0])), run_time=0.35)
                self.play(tape.cells[m].animate.set_opacity(0.25),
                          lo.animate.next_to(tape.cells[m + 1], UP, buff=0.55), run_time=0.3)
                rows.append(f"halving {len(rows) + 1}: mid {m} = F, lo <- {m + 1}")
                L = m + 1
        self.play(Transform(state, mono(f"lo = hi = {L}: answer {L}", 19, ACCENT).move_to([0, -1.0, 0])), run_time=0.35)
        bar = Rectangle(width=tape.cells.width + 0.3, height=0.86, stroke_color=ACCENT, stroke_width=2,
                        fill_color=ACCENT, fill_opacity=0.14).move_to(tape.cells)
        self.play(Create(bar), Indicate(tape.cells[target], color=ACCENT, scale_factor=1.2), run_time=0.5)
        rows = VGroup(*(mono(t, 16, MUTED) for t in rows)).arrange(DOWN, buff=0.12)
        rows.move_to([0, -2.55, 0])
        self.play(LaggedStart(*(FadeIn(r) for r in rows), lag_ratio=0.15), run_time=0.6)

    def real_search(self, beats):
        axes = Axes(x_range=[0, 10, 1], y_range=[0, 10, 1], x_length=7.6, y_length=3.4,
                    axis_config={"stroke_color": STROKE, "stroke_width": 1.4, "include_ticks": False}).move_to([-1.6, 0.9, 0])
        curve = axes.plot(lambda x: 0.11 * (x - 6.4) ** 2 + 1.2, x_range=[0.4, 9.6], color=ACCENT, stroke_width=3)
        self.play(Create(axes), run_time=0.4)
        self.play(Create(curve), run_time=0.7)
        zero = axes.c2p(6.4, 0)
        target = Dot(zero, radius=0.08, color=PAPER)
        self.play(FadeIn(target), FadeIn(mono("eval -> float, can round", 18, MUTED).move_to([-1.6, -1.1, 0])), run_time=0.4)
        lo, hi = self.ptr("lo", MUTED), self.ptr("hi", MUTED)
        self.over(lo, axes.c2p(0.4, 0))
        self.over(hi, axes.c2p(9.6, 0))
        self.play(FadeIn(lo), FadeIn(hi), run_time=0.25)
        snd = mono("lo = 0.4", 18, PAPER).move_to([3.7, 0.5, 0])
        self.play(FadeIn(snd), Write(mono("synthetic: snd >= target", 18, PAPER).move_to([3.7, 1.05, 0])), run_time=0.3)
        L, R = 0.4, 9.6
        for step in range(6):
            m = (L + R) / 2
            self.play(lo.animate.next_to(np.array(axes.c2p(m, 0)), DOWN, buff=0.25), run_time=0.25)
            self.play(snd.animate.become(mono(f"mid = {m:.3f}, f = {0.11 * (m - 6.4) ** 2 + 1.2:.2f}", 18, PAPER).move_to([3.7, 0.5, 0])), run_time=0.2)
            if m < 6.4:
                self.play(Indicate(axes.c2p(m, 0), color=BAD, scale_factor=1.2), run_time=0.15)
                L = m
            else:
                self.play(Indicate(axes.c2p(m, 0), color=ACCENT, scale_factor=1.2), run_time=0.15)
                R = m
        self.play(Transform(snd, mono(f"|hi - lo| = {R - L:.4f} after 6 halvings", 18, ACCENT).move_to([3.7, 0.5, 0])),
                  Indicate(target, color=ACCENT, scale_factor=2), run_time=0.6)
        self.play(FadeIn(mono("stop when |hi - lo| < eps; answer lo", 18, MUTED).move_to([3.7, -1.1, 0])), run_time=0.35)

    def ternary(self, beats):
        axes = Axes(x_range=[0, 10, 1], y_range=[0, 10, 1], x_length=10.4, y_length=3.4,
                    axis_config={"stroke_color": STROKE, "stroke_width": 1.6,
                                 "include_ticks": False}).move_to([0, 0.15, 0])
        curve = axes.plot(lambda x: 0.62 * (x - 4.6) ** 2 + 1.1, x_range=[0.2, 9.6], color=ACCENT, stroke_width=3)
        goal = self.callout("unimodal: one valley, both slopes rise", MUTED)
        self.play(Create(axes), Write(goal), run_time=0.6)
        self.play(Create(curve), run_time=1.0)
        L, R = 0.4, 9.4
        span = self.math("\\text{range } [L, R]", PAPER, 26)
        left, right = axes.c2p(L, 0), axes.c2p(R, 0)
        band = Rectangle(width=right[0] - left[0], height=3.0, stroke_color=STROKE, stroke_width=1.2,
                         fill_color=ACCENT, fill_opacity=0.07).set_x((left[0] + right[0]) / 2).set_y(0.55)
        self.play(Create(band), FadeIn(span.next_to(axes, DOWN, buff=0.22)), run_time=0.5)
        self.play(goal.animate.become(self.callout("probe m1 = L + d/3 and m2 = R - d/3", MUTED)), run_time=0.35)
        M1 = lambda x: 0.62 * (x - 4.6) ** 2 + 1.1
        for r in range(3):
            d = R - L
            m1, m2 = L + d / 3, R - d / 3
            p1 = axes.c2p(m1, 0.62 * (m1 - 4.6) ** 2 + 1.1)
            p2 = axes.c2p(m2, 0.62 * (m2 - 4.6) ** 2 + 1.1)
            dots = VGroup(Dot(p1, radius=0.07, color=BAD), Dot(p2, radius=0.07, color=BAD))
            drop = VGroup(Line(p1, axes.c2p(m1, 0), color=BAD, stroke_width=1.2),
                          Line(p2, axes.c2p(m2, 0), color=BAD, stroke_width=1.2))
            tags = VGroup(mono("m1", 18, BAD).next_to(np.array(axes.c2p(m1, 0)), DOWN, buff=0.35),
                          mono("m2", 18, BAD).next_to(np.array(axes.c2p(m2, 0)), DOWN, buff=0.35))
            self.play(LaggedStart(Create(drop), FadeIn(dots), FadeIn(tags), lag_ratio=0.15), run_time=0.55)
            if M1(m1) < M1(m2):
                L, tag = m1, "f(m1) < f(m2): drop [L, m1)"
            else:
                R, tag = m2, "f(m2) <= f(m1): drop (m2, R]"
            newL, newR = axes.c2p(L, 0)[0], axes.c2p(R, 0)[0]
            target = Rectangle(width=newR - newL, height=3.0, stroke_color=ACCENT, stroke_width=1.4,
                               fill_color=ACCENT, fill_opacity=0.09).set_x((newL + newR) / 2).set_y(0.55)
            self.play(Transform(band, target), Transform(span, self.math(
                f"\\text{{range }} [{L:.2f}, {R:.2f}]\\;\\times 2/3", ACCENT, 26).next_to(axes, DOWN, buff=0.22)),
                goal.animate.become(self.callout(tag, BAD)), FadeOut(dots), FadeOut(drop), FadeOut(tags),
                run_time=0.55)
        self.play(goal.animate.become(self.callout("say 80 rounds: range < 1e-12", ACCENT)), run_time=0.35)
        self.play(Indicate(band, color=ACCENT, scale_factor=1.04), run_time=0.6)

    def _unimodal(self, y=0.35, tall=4.0, width=11.6):
        axes = Axes(x_range=[0, 10, 1], y_range=[0, 10, 1], x_length=width, y_length=tall,
                    axis_config={"stroke_color": STROKE, "stroke_width": 1.6,
                                 "include_ticks": False}).move_to([0, y, 0])
        curve = axes.plot(lambda x: 0.62 * (x - 4.6) ** 2 + 1.1, x_range=[0.2, 9.6], color=ACCENT, stroke_width=3)
        self.play(Create(axes), run_time=0.4)
        self.play(Create(curve), run_time=0.8)
        return axes, curve

    def ternary_discard(self, beats):
        axes, curve = self._unimodal(y=1.0, tall=3.0)
        band = Rectangle(width=axes.c2p(9.4, 0)[0] - axes.c2p(0.4, 0)[0], height=2.7,
                         stroke_color=STROKE, stroke_width=1.2, fill_color=ACCENT, fill_opacity=0.07)
        band.set_x((axes.c2p(0.4, 0)[0] + axes.c2p(9.4, 0)[0]) / 2).set_y(1.3)
        self.play(Create(band), run_time=0.4)
        note = mono("compare f(m1) with f(m2)", 20, MUTED).move_to([0, -1.3, 0])
        self.play(Write(note), run_time=0.35)
        for m1, m2, tag in [(3.4, 6.6, "f(m1) > f(m2): drop [L, m1]"),
                            (4.2, 5.8, "f(m1) < f(m2): drop [m2, R]")]:
            f1 = 0.62 * (m1 - 4.6) ** 2 + 1.1
            f2 = 0.62 * (m2 - 4.6) ** 2 + 1.1
            dots = VGroup(Dot(axes.c2p(m1, f1), radius=0.07, color=BAD),
                          Dot(axes.c2p(m2, f2), radius=0.07, color=BAD))
            drops = VGroup(*(Line(axes.c2p(m, f), axes.c2p(m, 0), color=BAD, stroke_width=1.2)
                             for m, f in [(m1, f1), (m2, f2)]))
            tags = VGroup(mono("m1", 17, BAD).next_to(np.array(axes.c2p(m1, 0)), DOWN, buff=0.3),
                          mono("m2", 17, BAD).next_to(np.array(axes.c2p(m2, 0)), DOWN, buff=0.3))
            self.play(LaggedStart(Create(drops), FadeIn(dots), FadeIn(tags), lag_ratio=0.15), run_time=0.5)
            keep = (m1, 9.4) if f1 > f2 else (0.4, m2)
            newL, newR = axes.c2p(keep[0], 0)[0], axes.c2p(keep[1], 0)[0]
            target = Rectangle(width=newR - newL, height=2.7, stroke_color=BAD, stroke_width=1.4,
                               fill_color=BAD, fill_opacity=0.07).set_x((newL + newR) / 2).set_y(1.3)
            self.play(Transform(band, target), Transform(note, mono(tag, 20, BAD).move_to([0, -1.3, 0])), run_time=0.5)
            self.play(FadeOut(dots), FadeOut(drops), FadeOut(tags), run_time=0.15)
        self.play(note.animate.become(mono("each round cuts one third of the range", 20, ACCENT).move_to([0, -1.3, 0])), run_time=0.35)
        self.play(FadeIn(mono("O(log_{1.5} N) rounds", 19, MUTED).move_to([0, -1.5, 0])), run_time=0.35)

    def ternary_shrink(self, beats):
        axes, curve = self._unimodal(y=1.0, tall=3.0)
        L, R = 0.4, 9.4
        col = Rectangle(width=axes.c2p(R, 0)[0] - axes.c2p(L, 0)[0], height=2.7, stroke_color=ACCENT,
                        stroke_width=1.4, fill_color=ACCENT, fill_opacity=0.09)
        col.set_x((axes.c2p(L, 0)[0] + axes.c2p(R, 0)[0]) / 2).set_y(1.3)
        counter = mono("range: 9.00", 20, PAPER).move_to([0, -1.3, 0])
        self.play(Create(col), Write(counter), run_time=0.4)
        for _ in range(4):
            d = R - L
            m1, m2 = L + d / 3, R - d / 3
            self.play(col.animate.set_width(max(axes.c2p(d, 0)[0], 0.2)).set_x(axes.c2p((L + R) / 2, 0)[0]),
                      Transform(counter, mono(f"range: {R - L:.2f}  (x 2/3)", 20, PAPER).move_to([0, -1.3, 0])),
                      run_time=0.35)
            f1 = 0.62 * (m1 - 4.6) ** 2 + 1.1
            f2 = 0.62 * (m2 - 4.6) ** 2 + 1.1
            if f1 < f2:
                L = m1
            else:
                R = m2
            self.play(col.animate.set_width(max(axes.c2p(max(R - L, 0.1), 0)[0], 0.2)).set_x(axes.c2p((L + R) / 2, 0)[0]),
                      run_time=0.25)
        self.play(Transform(counter, mono(f"after 80 rounds: < 1e-12  ({R - L:.1e})", 20, ACCENT).move_to([0, -1.3, 0])),
                  FadeIn(mono("keep the third that still holds the minimum", 19, MUTED).move_to([0, -1.8, 0])), run_time=0.5)
        self.play(Indicate(col, color=ACCENT, scale_factor=1.6), run_time=0.6)

    def ternary_int(self, beats):
        vals = [9, 8, 7, 6, 5, 5, 6, 7, 9, 11]
        tape = self.array([str(v) for v in vals], size=24, side=0.6, y=0.85,
                          caption=mono("integer domain: compare neighbours only", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.45)
        lo, hi = self.ptr("lo", MUTED), self.ptr("hi", MUTED)
        self.over(lo, tape.cells[0], buff=0.3)
        self.over(hi, tape.cells[-1], buff=0.3)
        self.play(FadeIn(lo), FadeIn(hi), run_time=0.25)
        note = mono("f(mid) <= f(mid + 1)", 20, PAPER).move_to([0, -1.0, 0])
        self.play(Write(note), run_time=0.3)
        L, R = 0, len(vals) - 1
        while L < R:
            m = (L + R) // 2
            self.play(lo.animate.next_to(tape.cells[m], DOWN, buff=0.55), run_time=0.25)
            self.play(Indicate(tape.cells[m:m + 2], color=ACCENT, scale_factor=1.15), run_time=0.25)
            if vals[m] <= vals[m + 1]:
                self.play(*[tape.cells[i].animate.set_opacity(0.25) for i in range(m)],
                          hi.animate.next_to(tape.cells[m + 1], UP, buff=0.30).set_opacity(0.25),
                          Transform(note, mono("rising: the minimum sits right", 20, ACCENT).move_to([0, -1.0, 0])), run_time=0.25)
                L = m + 1
            else:
                self.play(*[tape.cells[i].animate.set_opacity(0.25) for i in range(m + 2, len(vals))],
                          Transform(note, mono("falling: the minimum is at mid or left", 20, BAD).move_to([0, -1.0, 0])), run_time=0.25)
                R = m
        self.play(lo.animate.next_to(tape.cells[L], DOWN, buff=0.55), run_time=0.2)
        done = mono(f"argmin = {L} (first of the equal pair)", 20, ACCENT).move_to([0, -1.0, 0])
        self.play(Transform(note, done), Indicate(tape.cells[L], color=ACCENT, scale_factor=1.3), run_time=0.5)
        self.play(FadeIn(mono("skip '/' and float rounding: compare m with m + 1", 19, MUTED).move_to([0, -1.5, 0])), run_time=0.4)

    def bubble(self, beats):
        n = 8
        arr = self.series(beats, n, 1, 9, 3)
        tape = self.array(arr, caption=mono("unsorted", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.4)
        pos = {i: tape.cells[i].get_center() for i in range(n)}
        cmp = self.ptr("i", ACCENT)
        self.play(FadeIn(cmp), run_time=0.25)
        for pass_no in range(2):
            for i in range(n - 1 - pass_no):
                self.play(cmp.animate.next_to(tape.cells[i], UP, buff=0.1), run_time=0.18)
                self.play(Indicate(tape.cells[i:i + 2], color=BAD, scale_factor=1.1), run_time=0.22)
                if arr[i] > arr[i + 1]:
                    self.swap(tape.cells, i, i + 1, pos)
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                self.play(tape.cells[i].animate.set_stroke(ACCENT), run_time=0.1)
        coral = sorted(arr)
        for i in range(n):
            tape.cells[i].set_stroke(ACCENT, 2.4)
        self.play(cmp.animate.next_to(tape.cells[0], UP, buff=0.1), run_time=0.2)
        self.dismiss(cmp)
        comp = VGroup(*(self.math(s, ACCENT, 26) for s in (
            "(e, s_e)", "(-s_e, s_s)", "(x[3:])", "(bisect)")))
        comp.scale(0.62).arrange(DOWN, buff=0.1, aligned_edge=LEFT).move_to([2.45, -1.85, 0])
        y = np.array([coral.index(v) for v in arr])
        rank = VGroup(*(mono(str(int(v)), 17, ACCENT).next_to(tape.cells[i], DOWN, buff=0.28) for i, v in enumerate(y)))
        self.play(LaggedStart(*(FadeIn(g, shift=RIGHT * 0.1) for g in [*rank, *comp]), lag_ratio=0.1), run_time=0.8)
        self.play(Indicate(tape.cells, color=ACCENT, scale_factor=1.04), run_time=0.5)

    def intervals(self, beats):
        ivs = [(0, 3), (1, 4), (2, 6), (5, 8), (7, 10), (9, 12)]
        rng = random.Random(5 + len(beats))
        bars = VGroup()
        for k, (s, e) in enumerate(ivs):
            bar = Rectangle(width=(e - s) * 0.92, height=0.42, stroke_color=STROKE, stroke_width=1.4,
                            fill_color=CARD, fill_opacity=1)
            bars.add(VGroup(bar, mono(f"[{s},{e})", 18, PAPER).move_to(bar)))
        bars.arrange(DOWN, buff=0.1, aligned_edge=LEFT)
        bars.move_to([-2.4, 0.45, 0])
        axis = Line(LEFT * 5.4, RIGHT * 5.4, color=STROKE, stroke_width=1.4).set_y(-2.0)
        self.play(FadeIn(axis), LaggedStart(*(FadeIn(b, shift=RIGHT * 0.2) for b in bars), lag_ratio=0.12),
                  run_time=0.7)
        order = sorted(range(len(ivs)), key=lambda k: (ivs[k][1], ivs[k][0]))
        sweep = Line([0, -2.0, 0], [0, 1.7, 0], color=PAPER, stroke_width=2.5)
        states = VGroup(*(mono("pending", 16, MUTED) for _ in ivs))
        for k in range(len(bars)):
            states[k].move_to([bars[k].get_right()[0] + 0.55, bars[k].get_center()[1], 0])
        self.play(Create(sweep), FadeIn(states), run_time=0.5)
        clock = mono("t = 0", 20, PAPER).move_to([-6.85, 1.95, 0])
        self.play(FadeIn(clock), run_time=0.15)
        accepted, last = 0, -1
        for rank, k in enumerate(order):
            s, e = ivs[k]
            self.play(sweep.animate.set_x(-6.85 + s * 0.92),
                      Transform(clock, mono(f"t = {s}", 20, PAPER).move_to([-6.85 + s * 0.92, 1.95, 0])), run_time=0.3)
            if s >= last:
                accepted += 1
                last = e
                self.play(bars[k][0].animate.set_stroke(ACCENT).set_fill("#1E2B1F", 1),
                          Transform(states[k], mono(f"#{rank + 1} accepted", 16, ACCENT).move_to(states[k]).set_x(states[k].get_x())),
                          run_time=0.25)
                self.play(sweep.animate.set_x(-6.85 + e * 0.92), run_time=0.18)
            else:
                self.play(bars[k][0].animate.set_stroke(BAD).set_fill("#2C1B1A", 1),
                          Transform(states[k], mono(f"#{rank + 1} rejected", 16, BAD).move_to(states[k]).set_x(states[k].get_x())),
                          run_time=0.25)
        table = mono(f"sort by end; accept when gap >= last end: {accepted}/{len(ivs)}", 17, MUTED)
        fitw(table, 4.4)
        table.move_to([3.7, 0.9, 0])
        self.play(FadeIn(table, shift=LEFT * 0.1), run_time=0.7)

    def knapsack(self, beats):
        items = [(3, 4), (4, 5), (5, 6), (6, 7)]
        cap = 9
        tape = self.array([*range(cap + 1)], caption=mono("dp[w] = best value at capacity w", 19, MUTED))
        self.dismiss(tape.caption)
        head = mono("dp[w]", 19, MUTED).move_to([-5.0, 1.15, 0])
        self.play(FadeIn(tape), FadeIn(head), run_time=0.5)
        dp = [0] * (cap + 1)
        tag = mono("", 20, PAPER).move_to([0, -1.4, 0])
        for wt, val in items[:2]:
            for w in range(cap, wt - 1, -1):
                cand = dp[w - wt] + val
                if cand > dp[w]:
                    dp[w] = cand
                    lbl = mono(f"item ({wt} kg, {val} v): dp[{w}] = dp[{w - wt}] + {val} = {dp[w]}", 21, ACCENT)
                    src = arrow([tape.cells[w - wt].get_top()[0], 0.75, 0], [tape.cells[w].get_top()[0], 0.75, 0], ACCENT, 1.6)
                    self.play(Transform(tag, lbl.move_to([0, -1.4, 0])), Create(src),
                              tape.cells[w][1].animate.become(mono(str(dp[w]), 28, ACCENT).move_to(tape.cells[w])),
                              run_time=0.22)
                    self.play(FadeOut(src), run_time=0.05)
        for w in range(cap + 1):
            tape.cells[w][1].become(mono(str(dp[w]), 28, PAPER).move_to(tape.cells[w]))
        for w in range(cap + 1):
            if dp[w] == max(dp):
                tape.cells[w].set_stroke(ACCENT, 2.4)
        rule = VGroup(self.math("for\\ w\\ in\\ range(W,\\ w_t - 1,\\ -1):", ACCENT, 26),
                      self.math("dp[w] = \\max(dp[w],\\ dp[w - w_t] + v_t)", ACCENT, 26))
        rule.arrange(DOWN, buff=0.12, aligned_edge=LEFT).scale(0.85).move_to([0, -1.4, 0])
        self.play(self.dismiss(tag), FadeIn(rule), run_time=0.4)
        self.play(Indicate(tape.cells, color=ACCENT, scale_factor=1.04), run_time=0.6)

    def lis(self, beats):
        n = 9
        source = [2, 9, 3, 6, 1, 5, 8, 4, 7]
        tape = self.array(source, caption=mono("scanning values left to right", 19, MUTED))
        tails = self.array(["0"] * 6, size=24, side=0.56, y=-0.85, idx=False,
                           caption=mono("tails: smallest possible end per length", 19, MUTED))
        self.dismiss(tails.caption)
        head = mono("tails", 19, MUTED).move_to([-4.5, -0.18, 0])
        self.play(FadeIn(tape), FadeIn(tails), FadeIn(head), run_time=0.5)
        filled, cursor = 0, self.ptr("i", ACCENT)
        self.over(cursor, tape.cells[0])
        self.play(FadeIn(cursor), run_time=0.2)
        note = mono("", 22, PAPER).move_to([0, -1.85, 0])
        for i, x in enumerate(source):
            self.play(cursor.animate.next_to(tape.cells[i], UP, buff=0.1),
                      tape.cells[i].animate.set_stroke(ACCENT, 2.2), run_time=0.2)
            k = next((j for j in range(filled) if float(tails.cells[j][1].text) >= x), filled)
            if k == filled:
                txt = f"tails[{k}] = {x}: append, longer run"
                filled += 1
            else:
                txt = f"tails[{k}] {tails.cells[k][1].text} -> {x}: replace"
            self.play(Transform(note, mono(txt, 22, ACCENT).move_to([0, -1.85, 0])),
                      tails.cells[k][1].animate.become(mono(str(x), 24, ACCENT).move_to(tails.cells[k])),
                      run_time=0.22)
            self.play(tape.cells[i].animate.set_stroke(STROKE, 1.6), run_time=0.1)
        assert all(float(tails.cells[j][1].text) < float(tails.cells[j + 1][1].text) for j in range(filled - 1))
        self.play(note.animate.become(mono(f"LIS length = bisect_left(tails, n) = {filled}", 22, ACCENT)
                                      .move_to([0, -1.85, 0])), run_time=0.4)
        self.play(tails.cells[:filled].animate.set_stroke(ACCENT, 1.6),
                  *[Create(arrow([tails.cells[j].get_bottom()[0], -1.0, 0],
                                 [tails.cells[j + 1].get_bottom()[0], -1.0, 0], ACCENT, 1.6))
                    for j in range(filled - 1)], run_time=0.6)
        self.play(Indicate(tails.cells[:filled], color=ACCENT, scale_factor=1.06), run_time=0.5)


    def bubble(self, beats):
        n = 8
        arr = self.series(beats, n, 1, 9, 3)
        tape = self.array(arr, caption=mono("unsorted", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.4)
        pos = {i: tape.cells[i].get_center() for i in range(n)}
        cmp = self.ptr("i", ACCENT)
        self.play(FadeIn(cmp), run_time=0.25)
        for pass_no in range(2):
            for i in range(n - 1 - pass_no):
                self.play(cmp.animate.next_to(tape.cells[i], UP, buff=0.1), run_time=0.18)
                self.play(Indicate(tape.cells[i:i + 2], color=BAD, scale_factor=1.1), run_time=0.22)
                if arr[i] > arr[i + 1]:
                    self.swap(tape.cells, i, i + 1, pos)
                    arr[i], arr[i + 1] = arr[i + 1], arr[i]
                self.play(tape.cells[i].animate.set_stroke(ACCENT), run_time=0.1)
        coral = sorted(arr)
        for i in range(n):
            tape.cells[i].set_stroke(ACCENT, 2.4)
        self.play(cmp.animate.next_to(tape.cells[0], UP, buff=0.1), run_time=0.2)
        self.dismiss(cmp)
        comp = VGroup(*(self.math(t, ACCENT, 26) for t in (
            "(e, s_e)", "(-s_e, s_s)", "(x[3:])", "(bisect)")))
        comp.scale(0.62).arrange(DOWN, buff=0.1, aligned_edge=LEFT).move_to([2.45, -1.85, 0])
        y = np.array([coral.index(v) for v in arr])
        rank = VGroup(*(mono(str(int(v)), 17, ACCENT).next_to(tape.cells[i], DOWN, buff=0.28) for i, v in enumerate(y)))
        self.play(LaggedStart(*(FadeIn(g, shift=RIGHT * 0.1) for g in [*rank, *comp]), lag_ratio=0.1), run_time=0.8)
        self.play(Indicate(tape.cells, color=ACCENT, scale_factor=1.04), run_time=0.5)

    def intervals(self, beats):
        ivs = [(0, 3), (1, 4), (2, 6), (5, 8), (7, 10), (9, 12)]
        bars = VGroup()
        for s, e in ivs:
            bar = Rectangle(width=(e - s) * 0.92, height=0.42, stroke_color=STROKE, stroke_width=1.4,
                            fill_color=CARD, fill_opacity=1)
            bars.add(VGroup(bar, mono(f"[{s},{e})", 18, PAPER).move_to(bar)))
        bars.arrange(DOWN, buff=0.1, aligned_edge=LEFT).move_to([-2.4, 0.3, 0])
        axis = Line(LEFT * 5.4, RIGHT * 5.4, color=STROKE, stroke_width=1.4).set_y(-2.0)
        self.play(FadeIn(axis), LaggedStart(*(FadeIn(b, shift=RIGHT * 0.2) for b in bars), lag_ratio=0.12), run_time=0.7)
        order = sorted(range(len(ivs)), key=lambda k: (ivs[k][1], ivs[k][0]))
        states = VGroup(*(mono("pending", 16, MUTED).move_to([bars[k].get_right()[0] + 0.55, bars[k].get_center()[1], 0])
                          for k in range(len(bars))))
        sweep = Line([0, -2.0, 0], [0, 1.75, 0], color=PAPER, stroke_width=2.5)
        self.play(Create(sweep), FadeIn(states), run_time=0.5)
        accepted, last = 0, -1
        for rank, k in enumerate(order):
            s, e = ivs[k]
            self.play(sweep.animate.set_x(-6.85 + s * 0.92), run_time=0.3)
            if s >= last:
                accepted += 1
                last = e
                self.play(bars[k][0].animate.set_stroke(ACCENT).set_fill("#1E2B1F", 1),
                          Transform(states[k], mono(f"#{rank + 1} accepted", 16, ACCENT)), run_time=0.25)
                self.play(sweep.animate.set_x(-6.85 + e * 0.92), run_time=0.18)
            else:
                self.play(bars[k][0].animate.set_stroke(BAD).set_fill("#2C1B1A", 1),
                          Transform(states[k], mono(f"#{rank + 1} rejected", 16, BAD)), run_time=0.25)
        table = VGroup(self.math("\\text{sort by end}", ACCENT, 24),
                       self.math(f"\\text{{accept if }} s \\ge \\text{{last end}}: {accepted}", ACCENT, 24))
        table.arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to([3.9, 0.9, 0])
        self.play(Write(table), Indicate(states, color=ACCENT, scale_factor=1.03), run_time=0.7)

    def knap_demo(self, beats):
        cap = 9
        tape = self.array([*range(cap + 1)], caption=mono("dp[w] = best value at capacity w", 19, MUTED))
        self.dismiss(tape.caption)
        head = mono("dp[w]", 19, MUTED).move_to([-5.0, 0.95, 0])
        self.play(FadeIn(tape), FadeIn(head), run_time=0.5)
        dp = [0] * (cap + 1)
        tag = mono("", 20, PAPER).move_to([0, -1.75, 0])
        for wt, val in [(3, 4), (4, 5)]:
            for w in range(cap, wt - 1, -1):
                cand = dp[w - wt] + val
                if cand > dp[w]:
                    dp[w] = cand
                    src = arrow([tape.cells[w - wt].get_top()[0], 0.75, 0], [tape.cells[w].get_top()[0], 0.75, 0], ACCENT, 1.6)
                    self.play(Transform(tag, mono(f"item ({wt} kg, {val} v): dp[{w}] = {dp[w - wt]} + {val}", 21, ACCENT)
                                        .move_to([0, -1.75, 0])), Create(src), run_time=0.22)
                    self.play(self.grid_value(tape.cells[w], str(dp[w])), FadeOut(src), run_time=0.2)
        rule = VGroup(self.math("for\\ w\\ in\\ range(W,\\ w_t - 1,\\ -1):", ACCENT, 24),
                      self.math("dp[w] = \\max(dp[w],\\ dp[w - w_t] + v_t)", ACCENT, 24))
        rule.arrange(DOWN, buff=0.12, aligned_edge=LEFT).scale(0.85).move_to([0, -1.75, 0])
        self.play(self.dismiss(tag), FadeIn(rule), run_time=0.4)
        self.play(Indicate(tape.cells, color=ACCENT, scale_factor=1.04), run_time=0.6)

    def lis(self, beats):
        n = 9
        source = [2, 9, 3, 6, 1, 5, 8, 4, 7]
        tape = self.array(source, caption=mono("scanning values left to right", 19, MUTED))
        tail_cells = self.array(list("0123456"), size=24, side=0.56, y=-1.05, idx=False,
                                caption=mono("tails: smallest end per length", 19, MUTED))
        head = mono("tails", 19, MUTED).move_to([-4.5, -0.35, 0])
        self.play(FadeIn(tape), FadeIn(tail_cells), FadeIn(head), run_time=0.5)
        filled = 0
        cursor = self.ptr("i", ACCENT)
        self.over(cursor, tape.cells[0])
        self.play(FadeIn(cursor), run_time=0.2)
        note = mono("", 22, PAPER).move_to([0, -2.05, 0])
        for i, x in enumerate(source):
            self.play(cursor.animate.next_to(tape.cells[i], UP, buff=0.1),
                      tape.cells[i].animate.set_stroke(ACCENT, 2.2), run_time=0.18)
            k = next((j for j in range(filled) if int(tail_cells.cells[j][1].text) >= x), filled)
            if k == filled:
                txt = f"tails[{k}] = {x}: append"
                filled += 1
            else:
                txt = f"tails[{k}] {tail_cells.cells[k][1].text} -> {x}"
            self.play(Transform(note, mono(txt, 22, ACCENT).move_to([0, -2.05, 0])),
                      self.grid_value(tail_cells.cells[k], (str(x), x)), run_time=0.2)
            self.play(tape.cells[i].animate.set_stroke(STROKE, 1.6), run_time=0.08)
        self.play(Transform(note, mono(f"LIS length = {filled}", 22, ACCENT).move_to([0, -2.05, 0])), run_time=0.4)
        self.play(*[tail_cells.cells[j][0].animate.set_stroke(ACCENT, 1.8) for j in range(filled)],
                  Indicate(tail_cells.cells[:filled], color=ACCENT, scale_factor=1.1), run_time=0.6)

    def edit_table(self, beats):
        A, B = "kitten", "sitting"
        grid = self.dgrid([[""] + list(B)] + [[ch] + [""] * len(B) for ch in A], size=20, side=0.62)
        for c, ch in enumerate(B):
            grid[0][c + 1][1].become(mono(ch, 20, MUTED).move_to(grid[0][c + 1]))
        self.play(FadeIn(grid, shift=DOWN * 0.15), run_time=0.4)
        for r in range(len(A)):
            self.play(self.grid_value(grid[r + 1][0], A[r], ACCENT), run_time=0.08)
        self.play(grid[0][0][1].animate.become(mono("exp", 18, ACCENT).move_to(grid[0][0])), run_time=0.2)
        self.play(FadeIn(mono("substitute 1, insert 1, delete 1", 20, PAPER).move_to([0, -1.45, 0])), run_time=0.35)
        sub, ins, dele = len(A), len(B), 0
        dual = mono("dual view: edit suffix A[i:] -> B[j:]", 19, MUTED).move_to([0, -1.9, 0])
        mix = mono("same table, prefix and suffix agree at the corner", 19, ACCENT).move_to([0, -2.35, 0])
        self.play(FadeIn(dual), run_time=0.3)
        self.play(FadeIn(mix), run_time=0.3)
        corner = grid[len(A)][len(B)]
        self.play(Create(self.box_at(grid[len(A)], 1, len(B), ACCENT, y=corner.get_y())), run_time=0.4)
        _ = sub, ins, dele

    def edit_costs(self, beats):
        A, B = "kitten", "sitting"
        grid = self.dgrid([[""] + list(B)] + [[ch] + [""] * len(B) for ch in A], size=18, side=0.6)
        for c, ch in enumerate(B):
            grid[0][c + 1][1].become(mono(ch, 18, MUTED).move_to(grid[0][c + 1]))
        self.play(FadeIn(grid, shift=DOWN * 0.15), run_time=0.4)
        self.play(grid[0][0][1].animate.become(mono("exp", 16, MUTED).move_to(grid[0][0])), run_time=0.1)
        prev = [0] + [0] * (len(B) + 1)
        for r in range(1, len(A) + 2):
            row = [r]
            self.play(self.grid_value(grid[r - 1][0], ("exp" if r == 1 else str(r - 1), r - 1), ACCENT), run_time=0.08)
            for c in range(len(B) + 1):
                cost = 0 if 0 < r <= len(A) and A[r - 1] == B[c - 1] else 1
                val = min(prev[c + 1] + 1, row[c] + 1, prev[c] + cost)
                row.append(val)
                color = ACCENT if cost == 0 else PAPER
                self.play(self.grid_value(grid[r - 1][c], (str(val), val), color), run_time=0.04)
            prev = row
        self.play(FadeIn(mono("diagonal on a match: free", 19, ACCENT).move_to([0, -1.45, 0])), run_time=0.35)
        self.play(Indicate(grid[len(A)][len(B)], color=ACCENT, scale_factor=1.25),
                  FadeIn(mono("answer sits in the far corner", 19, PAPER).move_to([0, -1.9, 0])), run_time=0.5)

    def custom_key(self, beats):
        names = ["anna 7", "bob 9", "cy 3", "dee 9", "eve 5"]
        cards = VGroup(*(mono(n, 20, PAPER).move_to([-3.6 + 1.78 * i, -1.05, 0]) for i, n in enumerate(names)))
        boxes = VGroup(*(RoundedRectangle(width=1.6, height=0.62, corner_radius=0.08, stroke_color=STROKE,
                                          stroke_width=1.4, fill_color=CARD, fill_opacity=1).move_to(c) for c in cards))
        self.play(LaggedStart(*(FadeIn(cards[i], shift=DOWN * 0.15) for i in range(len(names))), lag_ratio=0.08),
                  run_time=0.5)
        self.play(LaggedStart(*(Create(boxes[i]) for i in range(len(names))), lag_ratio=0.08), run_time=0.5)
        head = mono("sort people by score (high first), then by name", 20, PAPER).move_to([0, 1.4, 0])
        self.play(Write(head), run_time=0.45)
        nom = VGroup(*(mono("name", 17, MUTED).move_to([-3.6 + 1.78 * i, 0.75, 0]) for i in range(len(names))))
        sc = VGroup(*(mono(n.split()[1], 20, ACCENT).move_to([-3.6 + 1.78 * i, 0.3, 0]) for i, n in enumerate(names)))
        self.play(LaggedStart(*(FadeIn(x) for x in [*nom, *sc]), lag_ratio=0.05), run_time=0.6)
        key = VGroup(mono("key", 17, BAD).move_to([-3.6 + 1.78 * 4 + 1.5, 0.75, 0]),
                     mono("-score, name", 17, BAD).move_to([-3.6 + 1.78 * 4 + 1.5, 0.3, 0]))
        self.play(FadeIn(key), run_time=0.35)
        order = [0, 2, 3, 1, 4]
        mon = ["anna 7", "cy 3", "dee 9", "bob 9", "eve 5"]
        cards2 = VGroup(*(mono(t, 20, PAPER).move_to([-3.6 + 1.78 * i, -0.43, 0]) for i, t in enumerate(mon)))
        self.play(FadeIn(cards2), run_time=0.4)
        plan = VGroup(mono("order the pairs by the key", 19, ACCENT),
                      mono("(-9, anna) < (-9, bob)", 18, PAPER),
                      mono("then (-9, *) before (-7, *)", 18, PAPER),
                      mono("then (-7, *) before (-5, eve)", 18, PAPER),
                      mono("then (-5, *) before (-3, cy)", 18, PAPER),
                      mono("one tuple: no pair compares", 19, ACCENT))
        plan.arrange(DOWN, buff=0.13, aligned_edge=LEFT).move_to([0, -2.1, 0])
        self.play(LaggedStart(*(FadeIn(p, shift=RIGHT * 0.1) for p in plan), lag_ratio=0.1), run_time=0.9)
        _ = order


class GridFamily(Board):
    """2D DP grids, tree/graph drawings, tables, number strips."""

    def dgrid(self, values, size=28, side=0.62, **kwargs):
        grid = VGroup(*(VGroup(*(cell(v, size, side, **kwargs) for v in line)) for line in values))
        for line in grid:
            line.arrange(RIGHT, buff=0.08)
        grid.arrange(DOWN, buff=0.08)
        fitw(grid, 8.4)
        grid.move_to([-0.4, 0.3, 0])
        return grid

    def grid_value(self, box, text, color=ACCENT):
        if not isinstance(box, VGroup):
            return box.animate.become(mono(str(text), 20, color))
        text, num = text if isinstance(text, tuple) else (text, text)
        size = 26 if len(str(text)) <= 2 else 18
        return box[1].animate.become(mono(str(text), size, color).move_to(box))

    def dep(self, grid, r, c, color=ACCENT, width=1.6):
        return VGroup(
            arrow(grid[r - 1][c].get_bottom(), grid[r][c].get_top(), color, width),
            arrow(grid[r][c - 1].get_right(), grid[r][c].get_left(), color, width),
        )

    def dist(self, goal, value):
        panel = VGroup(mono(goal, 20, MUTED),
                       mono(f"{value:3d}  edits", 24, PAPER))
        return panel.arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to([4.55, -0.9, 0])

    def greedy_commit(self, beats):
        coins = [25, 10, 5, 1]
        goal = 63
        tape = self.array([str(c) for c in coins], size=24, side=0.66, y=0.95, name="coins")
        self.play(FadeIn(tape), run_time=0.4)
        left = mono(f"need {goal}", 24, PAPER).move_to([5.0, 0.95, 0])
        self.play(Write(left), run_time=0.3)
        take = {c: 0 for c in coins}
        remain = goal
        for c in coins:
            k = remain // c
            remain -= k * c
            take[c] = k
            self.play(Indicate(tape.cells[coins.index(c)], color=ACCENT, scale_factor=1.2), run_time=0.3)
            self.play(Transform(left, mono(f"{k} x {c} -> {remain} left", 22, ACCENT if k else MUTED).move_to([5.0, 0.95, 0])),
                      tape.cells[coins.index(c)].animate.set_stroke(ACCENT if k else STROKE, 2), run_time=0.35)
        used = VGroup(*(mono(f"{c} x{take[c]}", 20, ACCENT if take[c] else MUTED)
                        .move_to([-3.3 + 1.9 * i, -0.55, 0]) for i, c in enumerate(coins)))
        self.play(LaggedStart(*(FadeIn(u, shift=UP * 0.1) for u in used), lag_ratio=0.1), run_time=0.5)
        total = sum(take.values())
        self.play(Transform(left, mono(f"{total} coins, 0 left", 24, ACCENT).move_to([5.0, 0.95, 0])), run_time=0.3)
        self.play(FadeIn(mono("biggest coin first, never undo", 20, ACCENT).move_to([0, -1.5, 0])), run_time=0.4)
        self.play(FadeIn(mono("works only when the coin system is canonical", 18, MUTED).move_to([0, -2.05, 0])), run_time=0.35)

    def exchange(self, beats):
        a = VGroup(VGroup(mono("greedy", 19, ACCENT).move_to([0, 0.35, 0])), self.pyfloat(mono("[2, 4, 5]", 22)))
        b = VGroup(VGroup(mono("OPT", 19, PAPER).move_to([0, 0.35, 0])), self.pyfloat(mono("[1, 3, 4, 5]", 22)))
        a.move_to([-3.1, 0.9, 0])
        b.move_to([3.1, 0.9, 0])
        self.play(FadeIn(a, shift=DOWN * 0.15), FadeIn(b, shift=DOWN * 0.15), run_time=0.5)
        same = VGroup(mono("shared: 4, 5", 18, MUTED).move_to([-3.1, -0.1, 0]),
                      mono("only here: 1, 3", 18, MUTED).move_to([3.1, -0.1, 0]))
        self.play(FadeIn(same), run_time=0.4)
        swap = (0, 2)
        todo = VGroup(mono("swap the first difference for the greedy pick", 19, PAPER).move_to([0, -0.9, 0]),
                      mono("|greedy| <= |OPT| stays true", 19, PAPER).move_to([0, -1.35, 0]),
                      mono("OPT is now closer to greedy", 19, PAPER).move_to([0, -1.8, 0]),
                      mono("swap all differences: greedy is an OPT", 20, ACCENT).move_to([0, -2.35, 0]))
        todo[3].set_color(MUTED)
        self.play(FadeIn(todo[0]), run_time=0.3)
        self.play(Indicate(VGroup(a[1], b[1]), color=ACCENT, scale_factor=1.08), run_time=0.45)
        self.play(FadeIn(todo[1]), run_time=0.3)
        self.play(b[1].animate.set_color(ACCENT), run_time=0.25)
        self.play(FadeIn(todo[2]), run_time=0.3)
        self.play(todo[3].animate.set_color(ACCENT), run_time=0.25)
        _ = swap
        self.play(Indicate(VGroup(pow2 := VGroup(a[1], b[1])), color=ACCENT, scale_factor=1.1), run_time=0.4)

    def regret_heap(self, beats):
        chosen = [(1, 9), (2, 4)]
        rest = [(2, 3), (3, 7), (3, 2)]
        rows = VGroup(*(VGroup(mono(f"t={t}", 18, MUTED), mono(f"w={w}", 18, PAPER), mono(title, 18, MUTED))
                        for (t, w), title in zip([(1, 12), (2, 7), (3, 10)], ["chosen", "chosen", "candidate"])))
        for k, r in enumerate(rows):
            r.arrange(RIGHT, buff=0.45).move_to([-2.6, 0.75 - 0.85 * k, 0])
            r[2].set_x(1.2)
        self.play(LaggedStart(*(FadeIn(r) for r in rows), lag_ratio=0.2), run_time=0.6)
        note = mono("commit t=1 (only w=9 fits)", 19, PAPER).move_to([0, -1.5, 0])
        self.play(Write(note), run_time=0.35)
        self.play(Transform(note, mono("commit t=2 (w=4): t=1 now blocks it", 19, BAD).move_to([0, -1.5, 0])),
                  rows[1][1].animate.set_color(BAD), Indicate(rows[1][1], color=BAD, scale_factor=1.1), run_time=0.4)
        self.play(Transform(note, mono("but t=3 (w=2) would allow one more item", 19, ACCENT).move_to([0, -1.5, 0])),
                  Indicate(VGroup(rows[2][1], rows[2][2]), color=ACCENT, scale_factor=1.15), run_time=0.4)
        self.play(Transform(note, mono("is t=2 worth blocking two cheap items?", 19, PAPER).move_to([0, -1.5, 0])), run_time=0.3)
        self.play(Transform(note, mono("regret = weight lost - item gained", 20, ACCENT).move_to([0, -1.5, 0])), run_time=0.35)
        self.play(FadeIn(mono("heap of chosen: pop while regret pays", 18, MUTED).move_to([0, -2.05, 0])), run_time=0.4)
        _ = chosen, rest

    def wrap(self, text, width=27):
        words, lines, line = str(text).split(), [], ""
        for w in words:
            if len(line) + len(w) > width and line:
                lines.append(line)
                line = w
            else:
                line = f"{line} {w}".strip()
        lines.append(line)
        return VGroup(*(mono(s, 20, PAPER) for s in lines[:3])).arrange(DOWN, buff=0.12, aligned_edge=LEFT)

    def lo_hi(self, tape, cap=True):
        if isinstance(tape, VGroup) and hasattr(tape, "cells"):
            cells = tape.cells
        else:
            cells = tape
        lo, hi = self.ptr("lo", MUTED), self.ptr("hi", MUTED)
        self.over(lo, cells[0])
        self.over(hi, cells[-1])
        self.play(FadeIn(lo, shift=DOWN * 0.1), FadeIn(hi, shift=DOWN * 0.1), run_time=0.4)
        return lo, hi

    def tree(self, spec, r=0.27):
        tree = TreeG(spec, r)
        self._last_tree = tree
        self.play(LaggedStart(*(Create(e) for e in tree.edges), lag_ratio=0.06), run_time=0.6)
        self.play(LaggedStart(*(FadeIn(n, scale=0.6) for n in tree.nodes.values()), lag_ratio=0.08), run_time=0.6)
        return tree

    def lo_hi(self, tape, cap=True):
        if isinstance(tape, VGroup) and hasattr(tape, "cells"):
            cells = tape.cells
        else:
            cells = tape
        lo, hi = self.ptr("lo", MUTED), self.ptr("hi", MUTED)
        self.over(lo, cells[0])
        self.over(hi, cells[-1])
        self.play(FadeIn(lo, shift=DOWN * 0.1), FadeIn(hi, shift=DOWN * 0.1), run_time=0.4)
        return lo, hi

    def tree(self, spec, r=0.27):
        tree = TreeG(spec, r)
        self._last_tree = tree
        self.play(LaggedStart(*(Create(e) for e in tree.edges), lag_ratio=0.06), run_time=0.6)
        self.play(LaggedStart(*(FadeIn(n, scale=0.6) for n in tree.nodes.values()), lag_ratio=0.08), run_time=0.6)
        return tree

    # -- 2D DP ------------------------------------------------------------
    def grid_paths(self, beats):
        R, C = 3, 3
        grid = self.dgrid([["" for _ in range(C)] for _ in range(R)], side=0.66)
        self.play(LaggedStart(*(FadeIn(c, scale=0.8) for line in grid for c in line), lag_ratio=0.05), run_time=0.5)
        self.play(FadeIn(self.dist("paths to end", 1)), run_time=0.3)
        cnt = [[0] * C for _ in range(R)]
        for r in range(R):
            for c in range(C):
                cnt[r][c] = 1 if (r == 0 or c == 0) else cnt[r - 1][c] + cnt[r][c - 1]
                deps = self.dep(grid, r, c) if r and c else VGroup()
                self.play(grid.animate.set_opacity(0.7), *(Create(d) for d in deps),
                          grid[r][c][0].animate.set_stroke(ACCENT, 2.2).set_opacity(1),
                          self.grid_value(grid[r][c], str(cnt[r][c])), run_time=0.3)
                self.play(*(FadeOut(d) for d in deps), run_time=0.12)
        arrows = VGroup()
        for r in range(R):
            for c in range(C):
                if r and c:
                    arrows.add(*self.dep(grid, r, c, ACCENT_DARK, 2.4))
        self.play(Create(arrows), run_time=0.5)
        cells = VGroup(*(grid[r][c] for r, c in [(0, 1), (2, 1), (1, 2), (2, 2)]))
        self.play(Indicate(cells, color=ACCENT, scale_factor=1.1), run_time=0.8)
        self.play(FadeOut(arrows), FadeIn(mono("dp[r][c] = dp[r-1][c] + dp[r][c-1]", 22, MUTED)
                                          .move_to([0, -1.75, 0])), run_time=0.35)

    def grid_obstacles(self, beats):
        grid = self.dgrid([["", "", "", ""], ["", "#", "", ""], ["", "", "", ""], ["", "", "", ""]], size=26, side=0.62)
        self.play(FadeIn(grid, shift=DOWN * 0.15), run_time=0.4)
        grid[1][1][0].set_stroke(BAD, 2).set_fill("#2C1B1A", 1)
        grid[1][1][1].set_color(BAD)
        header = mono("dp = grid of path counts mod 1e9+7", 20, MUTED).move_to([0, -1.8, 0])
        self.play(Write(header), run_time=0.35)
        dp = [[0] * 4 for _ in range(4)]
        for r in range(4):
            for c in range(4):
                if (r, c) == (1, 1):
                    self.play(Indicate(grid[1][1], color=BAD, scale_factor=1.2), run_time=0.35)
                    self.play(self.grid_value(grid[1][1], "0", BAD), run_time=0.2)
                    continue
                dp[r][c] = 1 if not r or not c else dp[r - 1][c] + dp[r][c - 1]
                self.play(self.grid_value(grid[r][c], str(dp[r][c])), run_time=0.12)
        for r in range(4):
            for c in range(4):
                if not r or not c:
                    self.play(grid[r][c][0].animate.set_stroke(ACCENT, 1.6), run_time=0.05)
        mod = mono("(a + b) % 1000000007 at every add", 20, ACCENT).next_to(header, DOWN, buff=0.15)
        self.play(FadeIn(mod), Indicate(grid, color=ACCENT, scale_factor=1.03), run_time=0.6)

    def grid_roll(self, beats):
        left = VGroup(mono("full grid", 20, MUTED), self.dgrid([["1"] * 4 for _ in range(3)], size=22, side=0.4))
        left[1].move_to([-3.6, 0.2, 0])
        left[0].move_to([-3.6, 1.3, 0])
        right = VGroup(mono("rolled rows", 20, MUTED), self.dgrid([["1"] * 4], size=22, side=0.4))
        right[1].move_to([1.6, 0.2, 0])
        right[0].move_to([1.6, 1.3, 0])
        bridge = arrow(right[1].get_left(), left[1].get_right(), ACCENT, 3)
        self.play(FadeIn(left), run_time=0.4)
        self.play(TransformFromCopy(left[1], right[1]), Create(bridge), FadeIn(right[0]), run_time=0.7)
        mem = mono("grid: O(R*C)  ->  rows: O(C)", 22, ACCENT).move_to([0, -1.2, 0])
        self.play(FadeIn(mem), run_time=0.4)
        rows = VGroup(row("row r-1", size=20), row("row r", size=20), row("row r+1", size=20))
        rows.arrange(DOWN, buff=0.16).move_to([4.9, -0.9, 0])
        self.play(FadeIn(rows), run_time=0.4)
        self.play(Indicate(rows[1], color=ACCENT, scale_factor=1.1),
                  Indicate(rows[0:2], color=MUTED, scale_factor=1.05), run_time=0.6)
        self.play(right[1][0].animate.set_opacity(0.15), Indicate(left[1], color=MUTED), run_time=0.5)
        tag = mono("lo = max + 42 <= 42e9", 20, PAPER).move_to([-3.6, -1.5, 0])
        self.play(FadeIn(tag), run_time=0.3)

    def grid_backtrack(self, beats):
        grid = self.dgrid([["", "", "", ""], ["", "", "", ""], ["", "", "", ""], ["", "", "", ""]], side=0.64)
        self.play(FadeIn(grid, shift=DOWN * 0.15), run_time=0.4)
        moves = [["L", "L", "2", ""], ["", "1", "1", ""], ["2", "1", "1", ""], ["", "", "", ""]]
        fills = [["", "", "", ""], ["", "1", "3", ""], ["2", "4", "3", ""], ["", "", "", ""]]
        for r in range(4):
            for c in range(4):
                if fills[r][c]:
                    self.play(self.grid_value(grid[r][c], fills[r][c], MUTED), run_time=0.1)
        for r in (3, 2, 1):
            for c in (3, 2, 1):
                if r == 3 or c == 3:
                    self.play(grid[r][c][0].animate.set_stroke(ACCENT, 1.6), run_time=0.06)
        start = grid[3][0]
        path = [(3, 0), (3, 1), (3, 2), (2, 2), (1, 2)]
        lines = VGroup(*(arrow(grid[a][b].get_center(), grid[x][y].get_center(), ACCENT, 3.2, buff=0.2)
                         for (a, b), (x, y) in zip(path, path[1:])))
        self.play(Create(lines), start[0].animate.set_stroke(ACCENT, 3), run_time=0.9)
        moves_txt = mono("parents give moves: U U L L -> reversed", 20, ACCENT).move_to([0, -1.8, 0])
        self.play(FadeIn(moves_txt), Indicate(grid[1][2], color=ACCENT, scale_factor=1.2), run_time=0.5)

    # -- bitmask ----------------------------------------------------------
    def bitmask(self, beats):
        bits = 5
        cells, header = self.bits(21, bits)
        self.play(FadeIn(cells, shift=RIGHT * 0.15), FadeIn(header), run_time=0.5)
        note = self.callout("mask 10101 = {0, 2, 4}", ACCENT)
        self.play(Write(note), run_time=0.4)
        m = 21
        targets = [1, 3, 4]
        for nxt in [1, 3]:
            nm = m | (1 << nxt)
            self.play(Transform(note, self.callout(f"10101 | (1 << {nxt}) = {nm:05b}", ACCENT)), run_time=0.3)
            new = self.bits_row(nm, bits)
            self.play(*[Transform(a, b) for a, b in zip(cells, new)], run_time=0.3)
            self.play(Indicate(cells[nxt], color=ACCENT, scale_factor=1.35), run_time=0.3)
            m = nm
        states = mono(f"2^{bits} = {2 ** bits} masks, each visited once", 21, MUTED).move_to([0, -1.75, 0])
        ladder = row(["00000", "00001", "00101", "01101", "10101", "11111"], size=18)
        ladder.scale(0.9).move_to([0, FOOT_Y + 0.1, 0])
        self.play(FadeIn(states), FadeIn(ladder), run_time=0.4)
        self.play(Indicate(ladder, color=ACCENT, scale_factor=1.05), run_time=0.7)

    def bitmask_jump(self, beats):
        start = mono("TSP from 0, bits = visited", 20, MUTED).move_to([0, 1.25, 0])
        self.play(FadeIn(start), run_time=0.3)
        prev = self.bits_row(1, 5, y=0.55)
        self.play(FadeIn(prev), run_time=0.2)
        jumps = [(1, 0b00111, "0 -> 1 -> 2"), (0b00111, 0b01111, "2 -> 3"), (0b01111, 0b11111, "3 -> 4")]
        for old, new, txt in jumps:
            src = self.bits_row(old, 5, y=0.55)
            meta = mono(f"mask {old:05b}, last = {txt.split(' -> ')[-1]}", 20, PAPER).move_to([0, -0.6, 0])
            self.play(Transform(prev, src), FadeIn(meta), run_time=0.3)
            hop = arrow([-1.0, 0.55, 0], [1.6, 0.55, 0], ACCENT, 2)
            self.play(Create(hop), run_time=0.3)
            self.play(Transform(prev, self.bits_row(new, 5, y=0.55)), FadeOut(hop), run_time=0.3)
            self.dismiss(meta)
        full = mono("11111 = all 20? no, all 5 items seen", 21, ACCENT).move_to([0, -1.1, 0])
        self.play(FadeIn(full), run_time=0.3)
        cmp = VGroup(mono("20! ~ 2.4e18 tours", 20, BAD), mono("2^20 * 20 ~ 2.1e7 states", 20, ACCENT))
        cmp.arrange(RIGHT, buff=0.6).move_to([0, -1.8, 0])
        self.play(FadeIn(cmp), Indicate(cmp[1], color=ACCENT, scale_factor=1.08), run_time=0.7)

    def submask_strip(self, full, subs):
        cells = VGroup(*(cell(f"{s:05b}", 20, 0.86, fill="#1E2B1F" if s == full else WELL,
                               stroke=ACCENT if s == full else STROKE) for s in subs))
        cells.arrange(RIGHT, buff=0.16).move_to([0, 0.55, 0])
        tags = VGroup(*(mono(f"{k}", 15, MUTED) for k in range(len(subs))))
        for t, c in zip(tags, cells):
            t.next_to(c, DOWN, buff=0.14)
        return cells, tags

    def submasks(self, beats):
        full = 0b01101
        subs = [0b01101, 0b01100, 0b01001, 0b01000, 0b00101, 0b00100, 0b00001, 0b00000]
        cells, tags = self.submask_strip(full, subs)
        meta = mono(f"mask {full:05b}: sub = (sub - 1) & mask", 21, PAPER).move_to([0, -0.55, 0])
        self.play(FadeIn(meta), run_time=0.3)
        self.play(LaggedStart(*(FadeIn(c, shift=UP * 0.1) for c in cells), lag_ratio=0.1), run_time=0.9)
        self.play(LaggedStart(*(FadeIn(t, shift=UP * 0.05) for t in tags), lag_ratio=0.05), run_time=0.5)
        count = mono("3^5 = 243 submask pairs, 5 * 2^5 SOS", 21, ACCENT).move_to([0, -1.35, 0])
        self.play(FadeIn(count), run_time=0.4)
        self.play(Indicate(cells, color=ACCENT, scale_factor=1.05), run_time=0.6)

    # -- backtracks and chains --------------------------------------------
    def linked_list(self, beats):
        nodes = VGroup(*(cell(v, 26, 0.72) for v in [7, 3, 9, 1]))
        nodes.arrange(RIGHT, buff=0.85).move_to([0, 0.5, 0])
        links = VGroup(*(arrow(a.get_right(), b.get_left(), MUTED, 2.4, buff=0.1) for a, b in zip(nodes, nodes[1:])))
        self.play(LaggedStart(*(FadeIn(n) for n in nodes), lag_ratio=0.12), run_time=0.6)
        self.play(LaggedStart(*(Create(l) for l in links), lag_ratio=0.12), run_time=0.6)
        rev = VGroup(*(arrow(b.get_left(), a.get_right(), ACCENT, 2.4, buff=0.1) for a, b in zip(nodes, nodes[1:])))
        self.play(LaggedStart(*(Create(l) for l in rev), lag_ratio=0.12), run_time=0.7)
        label_new = mono("prev <- cur: relink before moving", 21, ACCENT).move_to([0, -1.2, 0])
        self.play(FadeIn(label_new), Indicate(rev, color=ACCENT, scale_factor=1.03), run_time=0.6)

    def bet_ladder(self, beats):
        rows = ["1 2 3", "1 3 2", "2 1 3", "2 3 1", "3 1 2", "3 2 1"]
        start = "1 2 3 -> 1 3 2 -> 2 1 3"
        cells = VGroup(row(r, size=22) for r in ["1 2 3", "1 3 2", "2 1 3"])
        cells.arrange(DOWN, buff=0.3).move_to([0, 0.6, 0])
        conns = VGroup(*(arrow(a.get_bottom(), b.get_top(), ACCENT, 2.2) for a, b in zip(cells, cells[1:])))
        self.play(LaggedStart(*(FadeIn(c, shift=DOWN * 0.1) for c in cells), lag_ratio=0.12), run_time=0.5)
        self.play(LaggedStart(*(Create(l) for l in conns), lag_ratio=0.15), run_time=0.5)
        left = row(["1 2 3", "1 3 2", "2 1 3"], size=20).arrange(DOWN, buff=0.14).move_to([3.5, -0.4, 0])
        right = row(["3 1 2", "3 2 1"], size=20).arrange(DOWN, buff=0.14).move_to([4.8, -0.4, 0])
        mirror = arrow(left.get_right(), right.get_left(), BAD, 2.6)
        self.play(FadeIn(left), Create(mirror), FadeIn(right), run_time=0.5)
        last = mono("last element fixed: only 2 orders left", 20, ACCENT).move_to([0, -1.15, 0])
        third = mono("unknown at position 2: 3 choices", 20, PAPER).move_to([0, -1.6, 0])
        self.play(FadeIn(last), FadeIn(third), run_time=0.6)

    def sieve(self, beats):
        numbers = list(range(2, 51))
        grid = VGroup(*(cell(v, 19, 0.56) for v in numbers))
        for k in range(5):
            grid[k * 10:(k + 1) * 10].arrange(RIGHT, buff=0.07)
        grid.arrange(DOWN, buff=0.07).move_to([-2.3, 0.15, 0])
        self.play(LaggedStart(*(FadeIn(c) for c in grid), lag_ratio=0.01), run_time=0.4)
        hit = self.callout("start each sweep at p * p: smaller multiples already gone", ACCENT)
        self.play(Write(hit), run_time=0.4)
        for p in (2, 3, 5, 7):
            self.play(Indicate(grid[p - 2], color=ACCENT, scale_factor=1.4), run_time=0.25)
            below = [i for i, v in enumerate(numbers) if v > p and v < p * p and v % p == 0]
            if below:
                self.play(*[Indicate(grid[i], color=MUTED, scale_factor=0.9) for i in below], run_time=0.1)
            crosses = VGroup(*(grid[i] for i, v in enumerate(numbers) if v >= p * p and v % p == 0))
            rows = VGroup(*(Line(c.get_corner(UP + LEFT), c.get_corner(DOWN + RIGHT), color=BAD, stroke_width=2.4)
                            for c in crosses))
            self.play(LaggedStart(*(Create(r) for r in rows), lag_ratio=0.3), run_time=0.5)
            self.play(crosses.animate.set_opacity(0.45), run_time=0.1)
        code = VGroup(mono("for p in range(2, isqrt(N) + 1):", 19, PAPER),
                      mono("    is_prime[p*p::p] = 0", 19, ACCENT),
                      mono("leftover slots are prime", 19, MUTED))
        code.arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to([3.9, -0.5, 0])
        self.play(Write(code), run_time=0.5)
        alive = VGroup(*(grid[i] for i, v in enumerate(numbers) if v < 8 or all(v % q for q in (2, 3, 5, 7))))
        self.play(Indicate(alive, color=ACCENT, scale_factor=1.2), run_time=0.6)

    def spf(self, beats):
        n = 12
        row_cells = VGroup(*(cell(str(v), 20, 0.5) for v in range(1, n + 1)))
        row_cells.arrange(RIGHT, buff=0.08).move_to([-0.3, 0.85, 0])
        spf = [0] * (n + 1)
        for i in range(2, n + 1):
            spf[i] = next(d for d in range(2, i + 1) if i % d == 0)
        under = VGroup(*(mono(str(spf[v]), 17, ACCENT) if spf[v] else mono("-", 17, MUTED)
                         for v in range(1, n + 1))).arrange(RIGHT, buff=0)
        self.play(FadeIn(row_cells), run_time=0.4)
        head = mono("x:", 20, MUTED).next_to(row_cells, LEFT, buff=0.4)
        head2 = mono("spf[x]:", 20, MUTED).next_to(row_cells, LEFT, buff=0.4).shift(DOWN * 0.7)
        self.play(FadeIn(head), run_time=0.15)
        for c, v in zip(row_cells, range(1, n + 1)):
            sp = mono(str(spf[v]), 17, ACCENT) if spf[v] else mono("-", 17, MUTED)
            self.play(FadeIn(sp.next_to(c, DOWN, buff=0.2)), run_time=0.04)
        self.play(FadeIn(head2), run_time=0.2)
        x, chain = 60, VGroup()
        self.play(FadeIn(chain), run_time=0.1)
        shown = x
        cur = x
        while cur > 1:
            d = 2 if cur % 2 == 0 else 3 if cur % 3 == 0 else 5
            cur //= d
            chain.add(mono(str(cur), 24, ACCENT if cur > 1 else PAPER))
            chain.arrange(RIGHT, buff=0.45).move_to([1.0, -0.55, 0])
            self.play(FadeIn(chain[-1], shift=RIGHT * 0.1), run_time=0.12)
        self.play(FadeIn(mono(f"factor({shown}):", 22, PAPER).next_to(chain, LEFT, buff=0.3)), run_time=0.15)
        tag = mono(f"x //= spf[x] until 1: {len(chain)} steps", 21, ACCENT).move_to([0, -1.3, 0])
        self.play(FadeIn(tag), Indicate(chain, color=ACCENT, scale_factor=1.05), run_time=0.5)

    def factor(self, beats):
        n = 97 * 13 * 2
        card = self.pyfloat(mono(f"n = {n}", 34))
        card.move_to([0, 0.9, 0])
        self.play(FadeIn(card, shift=DOWN * 0.15), run_time=0.4)
        d = 2
        found = []
        chip_n = VGroup()
        guard = mono("d * d <= n", 21, PAPER).move_to([0, -0.6, 0])
        self.play(FadeIn(guard), run_time=0.2)
        while d * d <= n and len(found) < 3:
            if n % d == 0:
                n //= d
                found.append(d)
                chip_n.add(mono(f"{d} x ", 24, ACCENT))
                chip_n.arrange(RIGHT, buff=0.25).move_to([0, -1.3, 0])
                self.play(FadeIn(chip_n[-1]), Transform(card[1], mono(f"n = {n}", 34).move_to(card)), run_time=0.3)
            else:
                d += 1
        rest = mono(f"cofactor {n} > 1 is prime", 22, ACCENT).move_to([0, -1.85, 0])
        self.play(FadeIn(rest), Indicate(guard, color=ACCENT, scale_factor=1.1), run_time=0.6)

    def segmented(self, beats):
        L, R = 100, 119
        base = [2, 3, 5, 7]
        base_row = row([str(p) for p in base], size=20)
        base_row.move_to([-3.6, 0.9, 0])
        self.play(FadeIn(mono("primes <= sqrt(R)", 18, MUTED).next_to(base_row, DOWN, buff=0.15)),
                  FadeIn(base_row), run_time=0.4)
        window = VGroup(*(cell(v, 18, 0.5) for v in range(L, R + 1)))
        window.arrange(RIGHT, buff=0.08).move_to([0.6, 0.3, 0])
        self.play(FadeIn(window, shift=RIGHT * 0.15), FadeIn(mono(f"window [{L}..{R}]", 18, MUTED).next_to(window, UP, buff=0.15)), run_time=0.4)
        for p in base:
            first = ((L + p - 1) // p) * p
            marks = [first + k * p for k in range(10) if first + k * p <= R]
            self.play(*[window[v - L][1].animate.set_color(BAD).set_opacity(0.4) for v in marks], run_time=0.3)
        left = VGroup(*(window[v - L] for v in range(L, R + 1) if window[v - L][1].get_color().to_hex() == BAD))
        self.play(Indicate(left, color=ACCENT), run_time=0.4)
        mem = mono("allocate only R - L + 1 slots", 21, ACCENT).move_to([0, -1.2, 0])
        self.play(FadeIn(mem), run_time=0.4)
        start = mono(f"first multiple >= L: ceil(L / p) * p", 20, PAPER).move_to([0, -1.7, 0])
        self.play(FadeIn(start), run_time=0.4)

    def trie(self, beats, word="cat"):
        T = {"s": 0, "k": {0: [1, 2], 1: [3], 3: [4]}}
        place = {0: (0, 1.2), 1: (-0.6, 0.15), 2: (0.6, 0.15), 3: (-1.0, -1.0), 4: (-1.7, -1.0)}
        nodes = {k: TNode("root" if k == 0 else (word[k - 1] if k - 1 < len(word) else "?"), 0.26, size=20).move_to([*p, 0])
                 for k, p in place.items()}
        edges = VGroup(*(Line(nodes[a].get_center(), nodes[b].get_center(), color=STROKE, stroke_width=2, buff=0.25)
                         for a, kids in T["k"].items() for b in kids))
        self.play(Create(edges), LaggedStart(*(FadeIn(n, scale=0.7) for n in nodes.values()), lag_ratio=0.1), run_time=0.6)
        path = [1, 3, 4]
        chars = VGroup(*(mono(ch, 24, ACCENT) for ch in word))
        chars.arrange(RIGHT, buff=0.4).move_to([2.9, 1.15, 0])
        self.play(LaggedStart(*(FadeIn(c) for c in chars), lag_ratio=0.12), run_time=0.5)
        for k, ch in zip(path, word):
            self.play(Indicate(nodes[k], color=ACCENT, scale_factor=1.2), run_time=0.25)
        self.play(nodes[path[-1]].paint("#1E2B1F", ACCENT, ACCENT), run_time=0.25)
        panel = VGroup(mono(f"pass[{path[0]}]=1", 18, PAPER), mono(f"end[{path[-1]}]=1", 18, ACCENT))
        panel.arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to([2.9, -0.6, 0])
        self.play(Write(panel), run_time=0.5)
        self._last_end = nodes[4]
        shared = mono("shared 'c' prefix: one node, many words", 20, MUTED).move_to([0, -1.85, 0])
        self.play(FadeIn(shared), run_time=0.35)

    def bit_trie(self, beats):
        T = {"s": 0, "k": {0: [1, 2], 2: [5, 6]}}
        place = {0: (0, 1.2), 1: (-0.7, 0.1), 2: (0.7, 0.1), 5: (0.1, -1.0), 6: (1.3, -1.0)}
        text = {0: "5 = 101", 1: "1", 2: "0", 5: "01", 6: "10"}
        nodes = {k: TNode(text[k], 0.3, size=14).move_to([*p, 0]) for k, p in place.items()}
        edges = VGroup(*(Line(nodes[a].get_center(), nodes[b].get_center(), color=STROKE, stroke_width=2, buff=0.28)
                         for a, kids in T["k"].items() for b in kids))
        tags = VGroup(mono("bit 2", 16, MUTED, ).move_to([-1.5, 0.75, 0]), mono("bit 1", 16, MUTED).move_to([1.5, -0.4, 0]))
        self.play(Create(edges), LaggedStart(*(FadeIn(n, scale=0.7) for n in nodes.values()), lag_ratio=0.1), run_time=0.6)
        self.play(FadeIn(tags), run_time=0.2)
        self.play(nodes[1].paint("#1E2B1F", ACCENT), nodes[6].paint("#1E2B1F", ACCENT), run_time=0.3)
        walk = mono("query x = 2 (010): want opposite bits", 20, PAPER).move_to([0, -1.4, 0])
        q = walk.copy()
        self.play(FadeIn(walk), run_time=0.3)
        self.play(Indicate(nodes[5], color=ACCENT, scale_factor=1.2), q.animate.become(mono("bit 2 of x = 0, take 1", 20, ACCENT).move_to([0, -1.4, 0])), run_time=0.4)
        self.play(Indicate(nodes[6], color=ACCENT, scale_factor=1.2),
                  q.animate.become(mono("bit 1 of x = 1, take 0 -> done", 20, ACCENT).move_to([0, -1.4, 0])), run_time=0.4)
        depth = mono("depth B = 30, each step keeps the higher bits", 20, MUTED).move_to([0, -1.9, 0])
        self.play(FadeIn(depth), run_time=0.35)

    def skip_tour(self, beats):
        place = {0: (-1.8, 1.4), 1: (-2.6, 0.5), 2: (0.0, 0.5), 3: (-2.6, -0.4), 4: (2.2, -0.1), 5: (1.2, -1.0), 6: (3.2, -1.0)}
        nodes = {k: TNode(str(k), 0.26, size=20).move_to([*p, 0]) for k, p in place.items()}
        edges = VGroup(Line(nodes[0].get_center(), nodes[1].get_center(), color=STROKE, stroke_width=2, buff=0.25),
                       Line(nodes[1].get_center(), nodes[3].get_center(), color=STROKE, stroke_width=2, buff=0.25),
                       Line(nodes[0].get_center(), nodes[2].get_center(), color=STROKE, stroke_width=2, buff=0.25),
                       Line(nodes[2].get_center(), nodes[4].get_center(), color=STROKE, stroke_width=2, buff=0.25),
                       Line(nodes[4].get_center(), nodes[5].get_center(), color=STROKE, stroke_width=2, buff=0.25),
                       Line(nodes[4].get_center(), nodes[6].get_center(), color=STROKE, stroke_width=2, buff=0.25))
        self.play(Create(edges), LaggedStart(*(FadeIn(n, scale=0.7) for n in nodes.values()), lag_ratio=0.1), run_time=0.6)
        chip_skips = VGroup(mono("skip 3", 18, ACCENT), mono("skip 6", 18, ACCENT))
        line1 = Line(nodes[0].get_center(), nodes[4].get_center(), color=ACCENT, stroke_width=4).set_opacity(0.6)
        line2 = Line(nodes[1].get_center(), nodes[6].get_center(), color=BAD, stroke_width=3).set_opacity(0.5)
        self.play(Create(line1), Create(line2), run_time=0.6)
        chip_skips[0].move_to([-0.4, 1.1, 0])
        chip_skips[1].move_to([1.0, -1.5, 0])
        self.play(FadeIn(chip_skips), run_time=0.3)
        self.play(nodes[1].paint("#1E2B1F", BAD), nodes[5].paint("#1E2B1F", BAD), run_time=0.3)
        tag = mono("skip square: 1 + 2 + 4 + 9 = 16 nodes kept", 20, PAPER).move_to([0, -1.9, 0])
        self.play(FadeIn(tag), Indicate(chip_skips, color=ACCENT, scale_factor=1.1), run_time=0.6)

    def zigzag(self, beats):
        n = 7
        small = list(range(1, (n // 2) + 1))
        large = list(range(n, (n // 2), -1))
        zig = [v for pair in zip(small, large) for v in pair][:n + 1]
        tape = self.array([str(v) for v in zig], caption=mono("1, N, 2, N-1, 3, ...", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.5)
        diffs = [abs(a - b) for a, b in zip(zig, zig[1:])]
        y = tape.cells.get_center()[1]
        bars = VGroup(*(Line([tape.cells[i].get_bottom()[0], y - 0.48, 0],
                             [tape.cells[i].get_bottom()[0], y - 0.48 - d * 0.11, 0], color=ACCENT, stroke_width=3)
                        for i, d in enumerate(diffs[:5])))
        self.play(LaggedStart(*(Create(b) for b in bars), lag_ratio=0.15), run_time=0.9)
        count = VGroup(mono("differences ", 19, MUTED), mono(str(sorted(diffs, reverse=True)), 19, ACCENT))
        count.arrange(RIGHT, buff=0.1).move_to([0, -1.85, 0])
        self.play(FadeIn(count), run_time=0.4)
        snake = mono("snake grid: one chain, any lengths", 20, PAPER).move_to([0, -2.3, 0])
        self.play(FadeIn(snake), run_time=0.35)

    def powers(self, beats):
        n = 55
        parts = [1, 2, 4, 8, 16, 32]
        rem = n - sum(parts)
        cells = VGroup(*(cell(str(v), 22, 0.7) for v in parts))
        cells.arrange(RIGHT, buff=0.14).move_to([-0.4, 0.6, 0])
        self.play(LaggedStart(*(FadeIn(c, scale=0.7) for c in cells), lag_ratio=0.1), run_time=0.7)
        bits = VGroup(*(mono("1", 18, ACCENT) for _ in range(6)))
        bits.arrange(RIGHT, buff=0.32).next_to(cells, UP, buff=0.25)
        self.play(LaggedStart(*(FadeIn(b) for b in bits), lag_ratio=0.1), run_time=0.4)
        rem_cell = cell(str(rem), 22, 0.7).next_to(cells, DOWN, buff=0.6)
        plus = mono("+", 22, MUTED).next_to(rem_cell, LEFT, buff=0.25)
        self.play(FadeIn(rem_cell, shift=UP * 0.1), FadeIn(plus), run_time=0.4)
        total = mono(f"N = {n} = 110111 + {rem}", 22, PAPER).move_to([0, -1.7, 0])
        self.play(FadeIn(total), run_time=0.4)
        summ = mono("every sum 1..N is reachable", 21, ACCENT).move_to([0, -2.2, 0])
        self.play(FadeIn(summ), Indicate(cells, color=ACCENT, scale_factor=1.04), run_time=0.6)

    def spiral(self, n=5):
        marks = VGroup()
        for k in range(n * n):
            row_, col_ = divmod(k, n)
            marks.add(VGroup(Rectangle(width=0.5, height=0.5, stroke_color=STROKE, stroke_width=1.4),
                             mono(str(k + 1), 16, PAPER)))
        for m, (r, c) in zip(marks, [(r, c) for r in range(n) for c in range(n)]):
            m.move_to([(c - (n - 1) / 2) * 0.56, ((n - 1) / 2 - r) * 0.56, 0])
        return marks

    def spiral_path(self, grid):
        order = []
        top, bottom, left, right = 0, 4, 0, 4
        while top <= bottom and left <= right:
            order.extend((top, c) for c in range(left, right + 1))
            order.extend((r, right) for r in range(top + 1, bottom + 1))
            if top < bottom:
                order.extend((bottom, c) for c in range(right - 1, left - 1, -1))
            if left < right:
                order.extend((r, left) for r in range(bottom - 1, top, -1))
            top, bottom, left, right = top + 1, bottom - 1, left + 1, right - 1
        pts = [grid[r * 5 + c].get_center() for r, c in order]
        return VGroup(*(Line(pts[i], pts[i + 1], color=ACCENT, stroke_width=2.2, buff=0.06)
                        for i in range(len(pts) - 1)))

    def call_panel(self, beats):
        self.play(FadeIn(mono("check(n, ans)", 24, ACCENT).move_to([-3.2, 0.9, 0])), run_time=0.3)
        grid = self.spiral(5)
        self.play(FadeIn(grid), run_time=0.3)
        path = self.spiral_path(grid)
        self.play(Create(path), run_time=1.2)
        rows = VGroup(*(mono(s, 18, PAPER if "pass" not in s else ACCENT) for s in
                        ["for n in range(1, 21):", "  ans = build(n)", "  assert check(n, ans)", "fuzz: pass 20/20"]))
        rows.arrange(DOWN, buff=0.13, aligned_edge=LEFT).move_to([3.6, -1.1, 0])
        self.play(Write(rows), run_time=0.6)
        self.play(FadeIn(mono("5 broken invariants caught", 19, BAD).move_to([3.6, -2.1, 0])), run_time=0.4)

    def catalog(self, beats):
        title = mono("archetype?", 22, PAPER).move_to([0, 1.2, 0])
        self.play(FadeIn(title), run_time=0.3)
        desc = self.wrap("extremum · count · reachability · construction")
        desc.move_to([0, 0.6, 0])
        self.play(LaggedStart(*(FadeIn(d, shift=RIGHT * 0.1) for d in desc), lag_ratio=0.12), run_time=0.6)
        leaves = VGroup(mono("sort + two pointers", 20, PAPER), mono("Euler tour + BIT", 20, PAPER),
                        mono("BFS + binary search", 20, PAPER))
        leaves.arrange(RIGHT, buff=0.5).move_to([0, -1.05, 0])
        links = VGroup(*(arrow(UP * 0.15, DOWN * 0.25, ACCENT, 2.2) for _ in leaves))
        for l, a in zip(leaves, links):
            a.move_to([l.get_top()[0], -0.4, 0])
        self.play(LaggedStart(*(FadeIn(l, shift=UP * 0.1) for l in leaves), lag_ratio=0.12), run_time=0.5)
        self.play(LaggedStart(*(Create(a) for a in links), lag_ratio=0.12), run_time=0.4)
        hint = mono("constraints pick the tool: N <= 2e5 needs O(N log N)", 20, ACCENT).move_to([0, -1.9, 0])
        self.play(FadeIn(hint), Indicate(leaves, color=ACCENT, scale_factor=1.05), run_time=0.6)

    def challenge(self, beats):
        self.linked_list(beats)
        self.dismiss(*self.mobjects)
        tree = self.tree(LEAF_TREE)
        flash = VGroup(*(Circle(radius=0.42, color=ACCENT, stroke_width=3).move_to(tree[u]) for u in (2, 3)))
        self.play(*[FadeIn(f, scale=0.5) for f in flash], tree.edges.animate.set_stroke(ACCENT), run_time=0.6)
        self.play(LaggedStart(*(FadeOut(f, scale=1.6) for f in flash), lag_ratio=0.2), run_time=0.6)
        sub = self.callout("zigzag + subtree queries, weave 12 -> 16", ACCENT)
        self.play(Write(sub), run_time=0.4)

    def check_panel(self, beats):
        header = self.math("10^9 + 7", ACCENT, 34).move_to([-4.4, 1.45, 0])
        span = self.math("N \\le 2 \\cdot 10^5", PAPER, 26).next_to(header, DOWN, buff=0.2)
        label_ = mono("check bounds", 18, MUTED).next_to(span, DOWN, buff=0.2)
        self.play(FadeIn(header, shift=DOWN * 0.1), run_time=0.35)
        self.play(FadeIn(span), FadeIn(label_), run_time=0.3)
        checks = VGroup(mono("1 <= a, b", 19, PAPER),
                        mono("a + b < MOD", 19, PAPER),
                        mono("a * b fits", 19, PAPER),
                        mono("ans after each step", 19, PAPER))
        ticks = VGroup(*(mono("ok", 18, ACCENT) for _ in checks))
        for c, t in zip(checks, ticks):
            t.next_to(c, RIGHT, buff=0.3)
        checks.arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to([-0.6, 1.35, 0])
        self.play(LaggedStart(*(FadeIn(c) for c in checks), lag_ratio=0.2), run_time=0.7)
        self.play(LaggedStart(*(FadeIn(t, shift=RIGHT * 0.1) for t in ticks), lag_ratio=0.15), run_time=0.6)
        self.play(*[c.animate.set_color(ACCENT) for c in (checks[0], checks[1])], run_time=0.3)
        bremsen = VGroup(mono("bremsen: halve scope to 1e5", 19, BAD), mono("build after all adds", 19, BAD))
        bremsen.arrange(DOWN, buff=0.22, aligned_edge=LEFT).move_to([-0.6, -0.35, 0])
        self.play(FadeIn(bremsen[0]), run_time=0.35)
        self.play(FadeIn(bremsen[1]), run_time=0.35)
        capt = mono("write the checker before the fast code", 20, ACCENT).move_to([0, -1.6, 0])
        self.play(FadeIn(capt), run_time=0.4)

    # -- trees ------------------------------------------------------------
    def dsu_union(self, beats):
        parent = {i: i for i in range(8)}
        rows = {0: 0.95, 1: 0.95, 2: 0.95, 3: 0.95, 4: -0.3, 5: -0.3, 6: -0.3, 7: -0.3}
        for i in (4, 5, 6):
            parent[i] = 3
        nodes, edges = TreeG.__new__(TreeG), None
        nodes, edges = TreeG.__new__(TreeG), None
        forest = TreeG({"start": 0, "kids": {}, "place": {0: (0, 0)}})
        nodes = {}
        for x in range(8):
            nodes[x] = TNode(str(x), 0.25, size=19).move_to([0.56 * x - 1.9, rows[x], 0])
        edges = VGroup()
        for x, p in parent.items():
            nodes[x].paint("#1E2B1F" if p != x else CARD, ACCENT if p != x else STROKE)
            if p != x:
                edges.add(arrow(nodes[x].get_center(), nodes[p].get_center(), ACCENT, 2, buff=0.26))
        self.play(LaggedStart(*(Create(e) for e in edges), lag_ratio=0.08), run_time=0.6)
        self.play(LaggedStart(*(FadeIn(n) for n in nodes.values()), lag_ratio=0.05), run_time=0.5)
        ring = VGroup(Circle(radius=0.36, color=BAD, stroke_width=2.6).move_to(nodes[x]) for x in (3,))
        again = Circle(radius=0.36, color=BAD, stroke_width=2.6).move_to(nodes[5])
        self.play(Create(ring), Create(again), run_time=0.4)
        parent[7] = 5
        new = arrow(nodes[7].get_center(), nodes[5].get_center(), ACCENT, 2, buff=0.26)
        self.play(nodes[7].paint("#1E2B1F", ACCENT), Create(new), run_time=0.5)
        tag = mono("find(7) = find(5) = 3", 20, ACCENT).move_to([0, -1.15, 0])
        no = mono("7 and 5 already merge: skip", 20, MUTED).next_to(tag, DOWN, buff=0.2)
        self.play(FadeIn(tag), FadeIn(no), run_time=0.5)

    def compress(self, beats):
        nodes, edges = TreeG.__new__(TreeG).chain(5)
        self.play(LaggedStart(*(Create(e) for e in edges), lag_ratio=0.08), run_time=0.5)
        self.play(LaggedStart(*(FadeIn(n) for n in nodes.values()), lag_ratio=0.08), run_time=0.5)
        self.play(*[nodes[k].paint("#1E2B1F", ACCENT) for k in range(1, 6)][:-1], run_time=0.3)
        relinks = VGroup(*(arrow(nodes[k].get_center(), nodes[5].get_center(), ACCENT, 2.2, buff=0.24)
                           for k in (1, 2, 3, 4)))
        self.play(LaggedStart(*(Create(a) for a in relinks), lag_ratio=0.18), run_time=1.0)
        jump = mono("find: 6 hops -> 2 hops", 20, ACCENT).move_to([0, -1.5, 0])
        path = mono("every node on the path now points at root 5", 20, PAPER).next_to(jump, DOWN, buff=0.2)
        self.play(FadeIn(jump), FadeIn(path), Indicate(nodes[5], color=ACCENT, scale_factor=1.2), run_time=0.6)

    def prim_small(self, beats):
        parent = {0: None, 1: 0, 2: 0, 3: 1, 4: 3, 5: 4}
        rows = {0: 1.1, 1: 0.3, 2: 0.3, 3: -0.5, 4: -1.3, 5: -2.0}
        nodes = {x: TNode(str(x), 0.25, size=19).move_to([0.55 * x - 1.4, rows[x], 0]) for x in parent}
        edges = VGroup(*(Line(nodes[x].get_center(), nodes[p].get_center(), color=STROKE, stroke_width=2, buff=0.25)
                         for x, p in parent.items() if p is not None))
        self.play(Create(edges), LaggedStart(*(FadeIn(n) for n in nodes.values()), lag_ratio=0.06), run_time=0.6)
        self.play(nodes[0].paint("#1E2B1F", ACCENT), nodes[1].paint("#1E2B1F", ACCENT), run_time=0.3)
        self.play(LaggedStart(*(Create(arrow(nodes[p].get_center(), nodes[x].get_center(), ACCENT, 2, buff=0.25))
                                for x, p in [(2, 0), (3, 1), (4, 3), (5, 4)]), lag_ratio=0.2), run_time=1.0)
        small, big = self.pyfloat(mono("size 1", 20)), self.pyfloat(mono("size 6", 20))
        small.move_to([-2.7, 0.95, 0])
        big.move_to([2.9, 0.95, 0])
        self.play(FadeIn(small), FadeIn(big), run_time=0.3)
        note = mono("attach the smaller root under the larger", 20, ACCENT).move_to([0, -1.25, 0])
        self.play(FadeIn(note), arrow(big.get_left(), small.get_right(), ACCENT, 2.5), run_time=0.6)

    def parent_array(self, beats):
        tape = self.array([str(v) for v in [1, 3, 3, 3, 5, 5, 5]], caption=mono("parent[i]", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.4)
        for i in (3, 5):
            tape.cells[i].set_stroke(BAD, 2)
        sizes = self.array([str(v) for v in [1, 1, 1, 6, 1, 2, 1]], size=22, side=0.62, y=-0.95, idx=False,
                           caption=mono("size[find(i)]", 19, MUTED))
        self.dismiss(sizes.caption)
        head = mono("size", 19, MUTED).move_to([-4.6, -0.95, 0])
        self.play(FadeIn(sizes), FadeIn(head), run_time=0.3)
        for i in (3, 5):
            self.play(Indicate(sizes.cells[i], color=BAD, scale_factor=1.2), run_time=0.25)
        offline = mono("delete edge = add in reverse", 20, ACCENT).move_to([0, -1.75, 0])
        count = mono("count components at each step", 20, PAPER).next_to(offline, DOWN, buff=0.12)
        self.play(FadeIn(offline), FadeIn(count), run_time=0.5)

    # -- Fenwick and segment trees ---------------------------------------
    def bits_of(self, n, bits=8):
        return [f"{n:0{bits}b}"]

    def fenwick(self, beats):
        n = 8
        tape = self.array([str(i) for i in range(1, n + 1)], caption=mono("1-based index i", 19, MUTED))
        blocks = [1, 2, 1, 4, 1, 2, 1, 8]
        spans = VGroup()
        for i in range(n):
            x = tape.cells[i].get_center()[0]
            spans.add(Line([x, -0.17, 0], [tape.cells[i].get_center()[0], -0.17, 0], color=ACCENT, stroke_width=2))
        summary = VGroup(*(self.pyfloat(mono(f"i & -i = {b}", 18)).move_to([tape.cells[i].get_center()[0], -0.72, 0])
                           for i, b in enumerate(blocks)))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.45)
        self.play(LaggedStart(*(FadeIn(s, shift=UP * 0.1) for s in summary), lag_ratio=0.06), run_time=0.7)
        query = self.callout("prefix 6: 110 -> strip the low bit", ACCENT)
        self.play(Write(query), run_time=0.35)
        hops = [6, 4, 0]
        for a, b in zip(hops, hops[1:]):
            ln = arrow([tape.cells[a - 1].get_center()[0], 1.05, 0],
                       [tape.cells[b - 1].get_center()[0] if b else 7.3, 1.05, 0], ACCENT, 2)
            self.play(Create(ln), Indicate(tape.cells[a - 1], color=ACCENT, scale_factor=1.15), run_time=0.45)
        self.play(FadeIn(mono("sum of blocks [6], [4] and [8]", 18, MUTED).next_to(tape.cells[7], UP, buff=0.5)), run_time=0.3)
        ladder = self.row_series([1, 2, 4, 8, 16, 32], "nodes 1..2N", y=-1.85)
        self.play(FadeIn(ladder), run_time=0.4)

    def row_series(self, values, title, y=-1.6, color=PAPER):
        cells = VGroup(*(cell(str(v), 18, 0.5) for v in values))
        cells.arrange(RIGHT, buff=0.1)
        return VGroup(cells, mono(title, 17, MUTED).next_to(cells, DOWN, buff=0.12)).move_to([0, y + 0.2, 0])

    def fenwick_update(self, beats):
        n = 8
        tape = self.array([str(i) for i in range(1, n + 1)], caption=mono("point add at i = 3", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.4)
        path = self.callout("i += i & -i  ->  3, 4, 8", ACCENT)
        self.play(Write(path), run_time=0.35)
        for i in (3, 4, 8):
            ln = Circle(radius=0.42, color=ACCENT, stroke_width=2).move_to(tape.cells[i - 1])
            self.play(Create(ln), Indicate(tape.cells[i - 1], color=ACCENT, scale_factor=1.15), run_time=0.4)
            if i != 8:
                hop = arrow([tape.cells[i - 1].get_center()[0], 1.05, 0], [tape.cells[i].get_center()[0], 1.05, 0], ACCENT, 2)
                self.play(Create(hop), run_time=0.3)
        touch = self.callout("only O(log N) blocks cover index 3", ACCENT).set_y(-1.85)
        self.play(FadeIn(touch), run_time=0.4)
        const = mono("flat list + integer math", 19, MUTED).move_to([0, -2.3, 0])
        self.play(FadeIn(const), run_time=0.3)

    def inversions(self, beats):
        tape = self.array([str(v) for v in [5, 2, 6, 1, 4, 3]], caption=mono("sweep left to right", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.4)
        counts = [0] * 6
        for i, v in enumerate([5, 2, 6, 1, 4, 3]):
            counts[i] = sum(1 for u in [5, 2, 6, 1, 4, 3][:i] if u > v)
            n = self.ptr(str(counts[i]), ACCENT)
            n.next_to(tape.cells[i], DOWN, buff=0.4)
            self.play(FadeIn(n), Indicate(tape.cells[i], color=ACCENT, scale_factor=1.15), run_time=0.3)
        total = self.callout(f"seen values > x: {sum(counts)} inversions", ACCENT)
        self.play(Write(total), run_time=0.4)
        bottom = self.row_series([5, 2, 6, 1, 4, 3], "rank after compression: 0..5", y=-1.75)
        self.play(FadeIn(bottom), run_time=0.4)

    def seg_tree(self, beats):
        place = {1: (0, 1.35), 2: (-2.4, 0.5), 3: (2.4, 0.5), 4: (-3.5, -0.4), 5: (-1.2, -0.4), 6: (1.2, -0.4), 7: (3.5, -0.4)}
        ranges = {1: "[0..7]", 2: "[0..3]", 3: "[4..7]", 4: "[0..1]", 5: "[2..3]", 6: "[4..5]", 7: "[6..7]"}
        nodes = {k: TNode(ranges[k], 0.5, size=14).move_to([*p, 0]) for k, p in place.items()}
        edges = VGroup(*(Line(nodes[a].get_center(), nodes[b].get_center(), color=STROKE, stroke_width=2, buff=0.4)
                         for a, b in [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7)]))
        leaves = self.array([str(v) for v in [3, 1, 4, 1, 5, 9, 2, 6]], size=20, side=0.56, y=-1.55, gap=0.1,
                            caption=None)
        self.play(Create(edges), LaggedStart(*(FadeIn(n, scale=0.7) for n in nodes.values()), lag_ratio=0.08), run_time=0.7)
        self.play(FadeIn(leaves), run_time=0.35)
        to_query = [nodes[2], nodes[5], nodes[6]]
        self.play(*[n.paint("#1E2B1F", ACCENT) for n in to_query], run_time=0.3)
        arcs = VGroup(*(arrow(nodes[k].get_center(), [0.3, -1.05, 0], ACCENT, 2.2, buff=0.45) for k in (2, 5, 6)))
        self.play(LaggedStart(*(Create(a) for a in arcs), lag_ratio=0.15), run_time=0.7)
        q = mono("query [2..5] folds nodes [0..1], [2..3], [4..5]", 19, ACCENT).move_to([0, -2.15, 0])
        self.play(FadeIn(q), run_time=0.4)
        two = mono("height = log2 N = 3, two nodes per level", 19, MUTED).move_to([0, -2.5, 0])
        self.play(FadeIn(two), run_time=0.35)

    def seg_update(self, beats):
        place = {1: (0, 1.35), 2: (-2.4, 0.5), 3: (2.4, 0.5), 4: (-3.5, -0.4), 5: (-1.2, -0.4), 6: (1.2, -0.4), 7: (3.5, -0.4)}
        nodes = {k: TNode(f"{k+4}", 0.26, size=18).move_to([*p, 0]) for k, p in place.items()}
        edges = VGroup(*(Line(nodes[a].get_center(), nodes[b].get_center(), color=STROKE, stroke_width=2, buff=0.25)
                         for a, b in [(1, 2), (1, 3), (2, 4), (2, 5), (3, 6), (3, 7)]))
        self.play(Create(edges), LaggedStart(*(FadeIn(n) for n in nodes.values()), lag_ratio=0.06), run_time=0.6)
        self.play(nodes[4].paint("#1E2B1F", ACCENT), run_time=0.25)
        self.play(LaggedStart(*(Create(arrow(nodes[b].get_center(), nodes[a].get_center(), ACCENT, 2.4, buff=0.25))
                                for a, b in [(2, 4), (1, 2)]), lag_ratio=0.25), run_time=0.9)
        leaves = self.row_series([4, 5, 8, 9, 14, 3, 7, 11], "leaves at N + i, parents at i >> 1", y=-1.55)
        self.play(FadeIn(leaves), run_time=0.4)
        note = mono("only the O(log N) ancestors recompute", 19, ACCENT).move_to([0, -2.2, 0])
        self.play(FadeIn(note), run_time=0.4)

    def seg_fold(self, beats):
        nodes = self.array([str(i) for i in range(8)], size=20, side=0.56, caption=mono("leaves N..2N-1", 19, MUTED))
        self.play(FadeIn(nodes, shift=DOWN * 0.2), run_time=0.4)
        picked = [nodes.cells[1], nodes.cells[4]]
        self.play(*[c.set_stroke(ACCENT, 2.4) for c in picked],
                  *[nodes.cells[i].set_opacity(0.3) for i in (0, 2, 3, 5, 6, 7)], run_time=0.5)
        L, R = self.ptr("L", ACCENT), self.ptr("R", BAD)
        self.over(L, nodes.cells[3])
        self.over(R, nodes.cells[6])
        self.play(FadeIn(L), FadeIn(R), run_time=0.3)
        self.play(L.animate.next_to(nodes.cells[2], UP, buff=0.1),
                  R.animate.next_to(nodes.cells[5], UP, buff=0.1), run_time=0.5)
        self.play(nodes.cells[2].animate.set_opacity(0.3), nodes.cells[5].animate.set_opacity(0.3),
                  nodes.cells[3].animate.set_stroke(ACCENT, 2.4), nodes.cells[6].animate.set_stroke(ACCENT, 2.4), run_time=0.4)
        self.play(self.dismiss(L, R), run_time=0.2)
        code = VGroup(mono("while L < R:", 19, PAPER), mono("  if L & 1: fold(L); L += 1", 19, ACCENT),
                      mono("  if R & 1: R -= 1; fold(R)", 19, ACCENT), mono("  L >>= 1; R >>= 1", 19, PAPER))
        code.arrange(DOWN, buff=0.1, aligned_edge=LEFT).move_to([1.9, -1.0, 0])
        self.play(Write(code), run_time=0.7)
        lim = mono("two folders per level, O(log N)", 19, MUTED).move_to([0, -1.95, 0])
        self.play(FadeIn(lim), run_time=0.4)

    # -- monotonic stack ---------------------------------------------------
    def mstack(self, beats):
        arr = [5, 2, 4, 3, 6, 1]
        tape = self.array([str(v) for v in arr], caption=mono("scan: next greater to the right", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.4)
        self.play(FadeIn(mono("stack", 18, MUTED).move_to([-4.6, -0.85, 0])), run_time=0.2)
        stack = []
        for i, v in enumerate(arr):
            self.play(tape.cells[i].set_stroke(ACCENT, 2.2), run_time=0.15)
            while stack and arr[stack[-1]] < v:
                j = stack.pop()
                cellv = self.pyfloat(mono(str(v), 18)).move_to([-4.4 + 0.62 * len(stack), -0.85, 0])
                self.play(Indicate(tape.cells[j], color=ACCENT, scale_factor=1.2), Transform(tape.cells[j][1], mono(str(v), 28, ACCENT).move_to(tape.cells[j])) if False else FadeIn(cellv), run_time=0.3)
                self.play(tape.cells[j][0].animate.set_stroke(ACCENT, 2.4), FadeOut(cellv), run_time=0.15)
            stack.append(i)
        left = VGroup(*(mono("_", 18, MUTED) for _ in stack))
        left.arrange(RIGHT, buff=0.32).move_to([-3.2, -1.5, 0])
        tag = self.callout("each index pushed once, popped once", ACCENT)
        self.play(Write(tag), FadeIn(left), run_time=0.5)

    def deque(self, beats):
        arr = [3, 1, 4, 1, 5]
        tape = self.array([str(v) for v in arr], caption=mono("window length 3, keep the maximum", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.4)
        k = 3
        win = self.box_at(tape.cells, 0, k - 1, ACCENT, y=tape.cells.get_center()[1])
        self.play(Create(win), run_time=0.35)
        maxes = [max(arr[s:s + k]) for s in range(len(arr) - k + 1)]
        for s in range(1, len(arr) - k + 1):
            self.play(Transform(win, self.box_at(tape.cells, s, s + k - 1, ACCENT, y=tape.cells.get_center()[1])), run_time=0.4)
        out = self.array([str(v) for v in maxes], size=22, side=0.6, y=-1.15, idx=False,
                         caption=mono("front = window maximum", 19, MUTED))
        self.dismiss(out.caption)
        self.play(FadeIn(out), run_time=0.4)
        hint = mono("pop worse from the back, evict expired front", 19, ACCENT).move_to([0, -1.95, 0])
        self.play(FadeIn(hint), Indicate(out.cells, color=ACCENT, scale_factor=1.08), run_time=0.6)

    def histogram(self, beats):
        h = [2, 1, 5, 6, 2, 3]
        tape = self.array([str(v) for v in h], caption=mono("bar heights", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.4)
        y = tape.cells.get_center()[1]
        bars = VGroup(*(Line([tape.cells[i].get_center()[0], y - 0.4, 0],
                             [tape.cells[i].get_center()[0], y - 0.4 - v * 0.22, 0], color=ACCENT, stroke_width=8)
                        for i, v in enumerate(h)))
        self.play(LaggedStart(*(Create(b) for b in bars), lag_ratio=0.12), run_time=0.8)
        rect = Rectangle(width=tape.cells[3].get_center()[0] - tape.cells[2].get_center()[0] + 0.6,
                         height=5 * 0.22, stroke_color=ACCENT, fill_color=ACCENT, fill_opacity=0.16)
        rect.move_to([(tape.cells[2].get_center()[0] + tape.cells[3].get_center()[0]) / 2, y - 0.4 - 0.55, 0])
        self.play(Create(rect), run_time=0.4)
        area = mono("area = 5 * 2 = 10 via left/right bounds", 20, ACCENT).move_to([0, -2.1, 0])
        self.play(FadeIn(area), run_time=0.4)
        right_note = mono("stack gives both bounds once", 19, MUTED).move_to([0, -2.5, 0])
        self.play(FadeIn(right_note), run_time=0.3)

    # -- Euler tour, LCA ---------------------------------------------------
    def euler_tin(self, beats):
        tree = self.tree(LEAF_TREE)
        flat = self.array([""] * 7, size=20, side=0.56, y=-1.4, idx=False,
                          caption=mono("euler[] in DFS order", 18, MUTED))
        self.dismiss(flat.caption)
        self.play(FadeIn(flat, shift=DOWN * 0.1), run_time=0.35)
        order = [1, 2, 4, 5, 3, 6]
        for k, u in enumerate(order):
            self.play(tree[u].paint("#1E2B1F", ACCENT), FadeIn(mono(str(u), 20, ACCENT).move_to(flat.cells[k])), run_time=0.25)
        span = self.box_at(flat.cells, 1, 3, ACCENT, y=flat.cells.get_center()[1])
        self.play(Create(span), run_time=0.4)
        tag = mono("subtree 2 == tin[2]..tout[2] = 1..3", 19, ACCENT).move_to([0, -1.95, 0])
        self.play(FadeIn(tag), Indicate(flat.cells[1:4], color=ACCENT, scale_factor=1.1), run_time=0.6)

    def lca_fill(self, beats):
        pos = [(0, 1.6), (-2.0, 1.6), (-3.2, 0.85), (-2.4, 0.85), (2.0, 1.6), (3.2, 0.85)]
        nodes = {k: TNode(str(k), 0.24, size=18).move_to([*p, 0]) for k, p in enumerate(pos)}
        edges = VGroup(*(Line(nodes[b].get_center(), nodes[a].get_center(), color=STROKE, stroke_width=2, buff=0.23)
                         for a, b in [(0, 1), (0, 4), (1, 2), (1, 3), (4, 5)]))
        self.play(Create(edges), LaggedStart(*(FadeIn(n) for n in nodes.values()), lag_ratio=0.07), run_time=0.6)
        table = VGroup()
        for r, (name, vals) in enumerate([("up0", "0 0 1 1 0 4"), ("up1", "- - 0 0 - 0"), ("up2", "- - - - - -")]):
            line = VGroup(mono(name, 18, ACCENT), row(vals.split(), size=18, pad=0.38))
            line.arrange(RIGHT, buff=0.3)
            table.add(line)
        table.arrange(DOWN, buff=0.18, aligned_edge=LEFT).move_to([0.4, -1.2, 0])
        self.play(LaggedStart(*(FadeIn(r, shift=RIGHT * 0.1) for r in table), lag_ratio=0.25), run_time=0.9)
        tag = mono("up[k][u] = up[k-1][ up[k-1][u] ]", 19, ACCENT).move_to([0, -2.3, 0])
        self.play(FadeIn(tag), run_time=0.4)

    def lca_table(self, beats):
        parent = {1: 0, 2: 1, 3: 1, 4: 0}
        chosen = [2, 3]
        root = TNode("0", 0.3, size=20).move_to([0, 1.5, 0])
        kids = {k: TNode(str(k), 0.26, size=18).move_to([2.2 * i - 2.2, 0.45, 0]) for i, k in enumerate(parent)}
        edge = VGroup(*(Line(root.get_center(), kids[k].get_center(), color=STROKE, stroke_width=2, buff=0.28) for k in parent))
        self.play(Create(root), run_time=0.2)
        for i, k in enumerate(parent):
            self.play(Create(edge[i]), FadeIn(kids[k]), run_time=0.2)
        u = VGroup(*(mono(p, 17, ACCENT) for p in ("2", "3")))
        up2 = VGroup(*(mono(p, 17, ACCENT) for p in ("1", "0")))
        self.play(FadeIn(u), run_time=0.3)
        self.play(*[FadeIn(up2[i]) for i in range(2)], run_time=0.3)
        row2 = VGroup()
        for i, k in enumerate(chosen):
            box = RoundedRectangle(width=0.62, height=0.5, corner_radius=0.08, stroke_color=ACCENT,
                                   fill_color="#1E2B1F", fill_opacity=1).move_to(kids[k])
            row2.add(VGroup(box, mono("2", 17, PAPER).move_to(box)))
        self.play(*[FadeIn(r) for r in row2], run_time=0.4)
        self.play(*(Create(arrow(kids[k].get_center(), root.get_center(), ACCENT, 2.4, buff=0.3)) for k in chosen), run_time=0.5)
        self.play(FadeIn(mono("up[2][2] = up[1][ up[1][2] ] = up[1][0] = 0", 19, ACCENT).move_to([0, -1.6, 0])), run_time=0.4)
        self.play(FadeIn(mono("up[k][v] = 2^k-th ancestor", 18, MUTED).move_to([0, -2.1, 0])), run_time=0.35)

    def lca_lift(self, beats):
        pos = {0: (0, 1.6), 1: (-2.0, 1.6), 2: (-3.0, 0.9), 3: (-1.2, 0.9), 4: (1.6, 0.9), 5: (2.6, 0.2)}
        nodes = {k: TNode(str(k), 0.24, size=18).move_to([*p, 0]) for k, p in pos.items()}
        edges = VGroup(*(Line(nodes[b].get_center(), nodes[a].get_center(), color=STROKE, stroke_width=2, buff=0.23)
                         for a, b in [(0, 1), (0, 4), (1, 2), (1, 3), (4, 5)]))
        self.play(Create(edges), LaggedStart(*(FadeIn(n) for n in nodes.values()), lag_ratio=0.07), run_time=0.6)
        hops = [mono("k = 5 = 101", 19, PAPER), mono("bit 0: +1 hop", 19, ACCENT)]
        hops[1].next_to(hops[0], DOWN, buff=0.12).align_to(hops[0], LEFT)
        stack = VGroup(*hops).move_to([-4.4, -0.8, 0])
        self.play(FadeIn(hops[0]), run_time=0.2)
        self.play(nodes[5].paint("#1E2B1F", ACCENT), FadeIn(hops[1]), Create(arrow(nodes[5].get_center(), nodes[4].get_center(), ACCENT, 2.4, buff=0.23)), run_time=0.5)
        more = mono("bit 2: +4 hops -> 0", 19, ACCENT).move_to([-4.3, -1.4, 0])
        self.play(FadeIn(more), Create(arrow(nodes[4].get_center(), nodes[0].get_center(), ACCENT, 2.4, buff=0.23)), run_time=0.6)
        size = mono("at most 20 lookups for N = 1e6", 19, MUTED).move_to([0, -2.3, 0])
        self.play(FadeIn(size), run_time=0.35)

    def lca_lockstep(self, beats):
        pos = {0: (0, 1.6), 1: (-2.0, 1.6), 2: (-3.0, 0.9), 3: (-1.2, 0.9), 4: (1.6, 0.9), 5: (2.6, 0.2)}
        nodes = {k: TNode(str(k), 0.24, size=18).move_to([*p, 0]) for k, p in pos.items()}
        edges = VGroup(*(Line(nodes[b].get_center(), nodes[a].get_center(), color=STROKE, stroke_width=2, buff=0.23)
                         for a, b in [(0, 1), (1, 2), (1, 3), (0, 4), (4, 5)]))
        self.play(Create(edges), LaggedStart(*(FadeIn(n) for n in nodes.values()), lag_ratio=0.07), run_time=0.6)
        self.play(nodes[2].paint("#1E2B1F", ACCENT), nodes[5].paint("#1E2B1F", ACCENT), run_time=0.3)
        up_v = arrow(nodes[5].get_center(), nodes[4].get_center(), ACCENT, 2.4, buff=0.23)
        up_u = arrow(nodes[2].get_center(), nodes[1].get_center(), ACCENT, 2.4, buff=0.23)
        self.play(Create(up_v), Create(up_u), run_time=0.5)
        note = mono("depth equal -> lift both while targets differ", 19, PAPER).move_to([0, -0.7, 0])
        self.play(FadeIn(note), run_time=0.35)
        self.play(nodes[4].paint("#1E2B1F", ACCENT), nodes[1].paint("#1E2B1F", ACCENT),
                  Create(arrow(nodes[4].get_center(), nodes[0].get_center(), ACCENT, 2.4, buff=0.23)),
                  Create(arrow(nodes[1].get_center(), nodes[0].get_center(), ACCENT, 2.4, buff=0.23)), run_time=0.6)
        stop = mono("equal: stop one step below, LCA = 0", 19, ACCENT).move_to([0, -1.3, 0])
        self.play(FadeIn(stop), Indicate(nodes[0], color=ACCENT, scale_factor=1.2), run_time=0.6)

    def lca_dist(self, beats):
        tree = self.tree(LEAF_TREE)
        path = VGroup(*(Line(tree[a].get_center(), tree[b].get_center(), color=ACCENT, stroke_width=3.2)
                        for a, b in [(4, 2), (2, 1), (1, 3), (3, 6)]))
        self.play(Create(path), run_time=0.8)
        d = self.row_series([3, 3, 1], "depth[u], depth[v], depth[lca]", y=-1.55)
        self.play(FadeIn(d), run_time=0.4)
        f = self.math("dist = 3 + 3 - 2 \\cdot 1 = 4", ACCENT, 30).move_to([0, -2.35, 0])
        self.play(Write(f), Indicate(path, color=ACCENT, scale_factor=1.02), run_time=0.6)

    def lca_mx(self, beats):
        tree = self.tree(LEAF_TREE)
        path = VGroup(*(Line(tree[a].get_center(), tree[b].get_center(), color=BAD, stroke_width=3)
                        for a, b in [(6, 3), (3, 1), (2, 1), (4, 2)]))
        self.play(Create(path), run_time=0.8)
        w = self.math("\\max(w) = 3", ACCENT, 30).move_to([0, -1.9, 0])
        self.play(Write(w), run_time=0.4)
        tag = mono("same formula, root-prefix weights", 19, MUTED).next_to(w, DOWN, buff=0.15)
        self.play(FadeIn(tag), run_time=0.35)

    # -- graphs ------------------------------------------------------------
    def graph(self, edges, pos, directed=False, weighted=True, r=0.27, node_text=None):
        tri = [tuple(e) if len(tuple(e)) == 3 else (e[0], e[1], 1) for e in edges]
        g = GraphG(tri, pos, directed, weighted, r)
        self.play(FadeIn(g.nodes[0]), run_time=0.2)
        for u in range(1, len(pos)):
            links = [g.edges[k] for k in g.edges if k[1] == u]
            self.play(*(Create(l) for l in links), FadeIn(g.nodes[u]), run_time=0.3)
        if weighted:
            self.play(LaggedStart(*(FadeIn(l[0]) for l in g.labels.values()), lag_ratio=0.05), run_time=0.4)
        return g

    def bfs(self, beats):
        edges = [(0, 1), (0, 2), (1, 3), (2, 4), (4, 5), (3, 5)]
        g = self.graph(edges, POS_GRAPH, weighted=False)
        queue = self.row_series(["deque: [0]"], "FIFO frontier", y=-2.15)
        self.play(FadeIn(queue), g.nodes[0].paint("#1E2B1F", ACCENT), run_time=0.3)
        for ring, layer in enumerate([[1, 2], [3, 4], [5]]):
            self.play(*[Create(arrow(g.pos(p), g.pos(u), ACCENT, 1.8, buff=0.3))
                        for u, p in [(1, 0), (2, 0), (3, 1), (4, 2), (5, 3)] if u in layer],
                      run_time=0.4)
            for u in layer:
                g.nodes[u].paint("#1E2B1F", ACCENT)
            self.play(Transform(queue, self.row_series([f"dist {ring + 1}: {layer}"], "mark on enqueue", y=-2.15)),
                      run_time=0.35)
        note = mono("unweighted shortest paths, O(V + E)", 20, ACCENT).move_to([0, -2.6, 0])
        self.play(FadeIn(note), run_time=0.4)

    def two_color(self, beats):
        edges = [(0, 1), (0, 4), (1, 2), (2, 3), (3, 4), (3, 5)]
        g = self.graph(edges, POS_GRAPH, weighted=False)
        colors = {0: ACCENT, 1: BAD, 4: BAD, 2: ACCENT, 3: BAD, 5: ACCENT}
        for u, col in colors.items():
            g.nodes[u].paint(CARD, col, col)
        self.play(**{f""}) if False else None
        for u, col in colors.items():
            self.play(Indicate(g.nodes[u], color=col, scale_factor=1.1), run_time=0.12)
        stack = self.row_series(["stack", "2", "3"], "explicit list, no recursion", y=-1.9)
        self.play(FadeIn(stack), run_time=0.4)
        cycle = Circle(radius=0.98, color=BAD, stroke_width=2, stroke_opacity=0.7).move_to(g.nodes[2])
        self.play(Create(cycle), run_time=0.4)
        tag = mono("colors alternate: odd cycle would clash", 20, ACCENT).move_to([0, -2.6, 0])

    def multi_bfs(self, beats):
        edges = [(0, 1), (1, 2), (2, 3), (3, 4), (1, 4), (2, 5)]
        g = self.graph(edges, POS_CONNECT, weighted=False)
        sources = [0, 5]
        self.play(g.nodes[0].paint("#1E2B1F", ACCENT), g.nodes[5].paint("#1E2B1F", ACCENT), run_time=0.3)
        rings = [([2, 3], 0.95), ([1, 4], 1.75)]
        for layer, radius in rings:
            for u in layer:
                self.play(Create(Circle(radius=radius, color=ACCENT, stroke_width=1.4, stroke_opacity=0.6).move_to(g.pos(u))),
                          run_time=0.25)
        self.play(g.nodes[0].paint("#1E2B1F", ACCENT), g.nodes[5].paint("#1E2B1F", ACCENT), run_time=0.2)
        zero = arrow(g.nodes[1].get_center(), g.nodes[0].get_center(), ACCENT, 2.4, buff=0.3)
        one = arrow(g.nodes[2].get_center(), g.nodes[5].get_center(), ACCENT_DARK, 2.4, buff=0.3)
        self.play(Create(zero), run_time=0.3)
        self.play(Create(one), run_time=0.3)
        tags = self.row_series(["0-weight -> appendleft", "1-weight -> append"], "0-1 BFS", y=-2.15)
        self.play(FadeIn(tags), run_time=0.4)

    def topo(self, edges, pos, ids=None):
        return self.graph([(u, v, 1) for u, v in edges], pos, directed=True, weighted=False,
                          node_text=(lambda i: ids[i]) if ids else None)

    def kahns(self, beats):
        g = self.topo([(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)], POS_TOP)
        queue = self.array(["1", "2"], size=22, side=0.6, y=-1.55, idx=False, caption=mono("queue of indegree 0", 18, MUTED))
        self.dismiss(queue.caption)
        self.play(FadeIn(queue), run_time=0.3)
        order = self.array(["0", "1", "", "", ""], size=22, side=0.6, y=-2.35, idx=False, caption=mono("topo order", 18, MUTED))
        self.dismiss(order.caption)
        self.play(FadeIn(order), run_time=0.2)
        for k, v in [(2, "2"), (3, "3"), (4, "4")]:
            self.play(order.cells[k][1].animate.become(mono(v, 22, ACCENT).move_to(order.cells[k])), run_time=0.15)
        sequence = [(1, "3"), (2, "3"), (3, "4"), (4, "")]
        for u, _nxt in sequence:
            g.nodes[u].paint("#1E2B1F", ACCENT)
            self.play(g.nodes[u].animate.set_opacity(0.55), run_time=0.15)
        tag = mono("emit 0 1 2 3 4: all V nodes", 19, ACCENT).move_to([0, -2.5, 0])
        self.play(FadeIn(tag), Indicate(order.cells[:5], color=ACCENT), run_time=0.5)

    def heap_topo(self, beats):
        g = self.topo([(1, 3), (1, 4), (2, 4), (3, 5), (4, 5)], POS_TOP, ids=["b", "a", "d", "c", "e", "f"])
        h = self.array(["a", "b", "c"], size=22, side=0.6, y=-1.6, idx=False, caption=mono("min-heap of indegree 0", 18, MUTED))
        self.dismiss(h.caption)
        self.play(FadeIn(h), run_time=0.3)
        self.play(self.swap(h.cells, 0, 1), run_time=0.4)
        self.play(Indicate(h.cells[0], color=ACCENT, scale_factor=1.2), run_time=0.3)
        for n in (1, 0):
            g.nodes[n].paint("#1E2B1F", ACCENT)
        self.play(g.nodes[1].animate.set_opacity(0.45), g.nodes[0].animate.set_opacity(0.45), run_time=0.3)
        tag = mono("pop 'a' before 'b': lexicographic", 19, ACCENT).move_to([0, -2.4, 0])
        self.play(FadeIn(tag), run_time=0.4)

    def topo_dp(self, beats):
        g = self.topo([(0, 1), (0, 2), (1, 3), (2, 3), (3, 4)], POS_TOP)
        vals = {0: "1", 1: "1", 2: "1", 3: "2", 4: "2"}
        for i, u in enumerate([0, 1, 2, 3, 4]):
            r = self.ptr(vals[u], ACCENT)
            self.over(r, g.nodes[u])
            if i:
                self.play(FadeIn(r), run_time=0.15)
            else:
                self.play(FadeIn(r), g.nodes[u].paint("#1E2B1F", ACCENT), run_time=0.25)
            if u < 4:
                for v in [x for x in range(5) if (u, x) in [(a, b) for a, b in g.edges.keys()]]:
                    self.play(Indicate(g.nodes[v], color=ACCENT, scale_factor=1.15), run_time=0.12)
            if u == 4:
                break
            g.nodes[u].paint("#1E2B1F", ACCENT)
        tag = mono("paths: 1, 1, 1, 2, 2 while walking topo", 19, ACCENT).move_to([0, -1.9, 0])
        self.play(FadeIn(tag), run_time=0.4)

    def dijkstra(self, edges, pos, src=0):
        g = self.graph(edges, pos)
        dist = {u: "inf" for u in range(len(pos))}
        dist[src] = "0"
        labels = {}
        for u in range(len(pos)):
            labels[u] = mono(f"d={dist[u]}", 17, MUTED if u != src else ACCENT)
            x, y = pos[u]
            if y >= 2.4:
                # the top row would stack labels onto hidden node text
                labels[u].next_to(g.nodes[u], LEFT, buff=0.22)
            else:
                labels[u].next_to(g.nodes[u], UP, buff=0.2)
        self.play(FadeIn(VGroup(*labels.values())), g.nodes[src].paint("#1E2B1F", ACCENT), run_time=0.35)
        return g, labels, dist

    def relax(self, g, labels, dist, heap, relaxations):
        for u, v, nd in relaxations:
            old = dist[v]
            h = arrow(g.pos(u), g.pos(v), ACCENT, 3.2)
            self.play(Create(h), Indicate(g.nodes[u], color=ACCENT, scale_factor=1.15), run_time=0.4)
            dist[v] = str(nd)
            if g.labels.get((u, v)) is not None:
                wl = g.labels[(u, v)]
                self.play(wl[1].animate.set_opacity(1),
                          Transform(wl[1], mono(f"d={nd}", 17, ACCENT).move_to(wl[1])), run_time=0.22)
            self.play(Transform(labels[v], mono(f"d={nd}", 17, ACCENT).next_to(g.nodes[v], UP, buff=0.2)),
                      Transform(heap, self.row_series([f"({d}, {x})" for d, x in self._heap_pairs(dist)],
                                                      "heap (d, node)", y=-1.9)), run_time=0.4)
            self.play(FadeOut(h), run_time=0.12)
            g.nodes[u].paint("#1E2B1F", ACCENT)
            g.nodes[v].paint("#1E2B1F", ACCENT)
            self.play(*(g.nodes[x].animate.set_opacity(0.55) for x in (u, v)), run_time=0.12)
            if old != "inf":
                self.play(labels[v].animate.set_color(MUTED), run_time=0.05)

    def _heap_pairs(self, dist):
        pairs = [(d, u) for u, d in dist.items() if d != "inf"]
        pairs.sort()
        return [(d, u) for d, u in pairs[:3]]

    def dijkstra_tour(self, beats):
        edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5), (3, 4, 3)]
        g, labels, dist = self.dijkstra(edges, POS_GRAPH)
        heap = self.row_series(["(0, 0)"], "heap (d, node)", y=-1.9)
        self.play(FadeIn(heap), run_time=0.3)
        self.relax(g, labels, dist, heap, [(0, 2, 1), (2, 1, 3), (1, 3, 4), (3, 4, 7)])
        gc = self.math("d(4) = 7 via 0 -> 2 -> 1 -> 3 -> 4", ACCENT, 26).move_to([0, -2.5, 0])
        self.play(Write(gc), run_time=0.5)

    def dijkstra_relax(self, beats):
        edges = [(0, 1, 4), (0, 2, 1), (2, 1, 2), (1, 3, 1), (2, 3, 5), (3, 4, 3)]
        g, labels, dist = self.dijkstra(edges, POS_GRAPH)
        heap = self.row_series(["(0, 0)"], "heap (d, node)", y=-1.9)
        self.play(FadeIn(heap), run_time=0.3)
        self.relax(g, labels, dist, heap, [(0, 2, 1), (2, 1, 3)])
        self.play(self.row_series(["pop 2 (d=1): final"], "processed", y=-2.4), run_time=0.3)
        v = g.nodes[0].copy()
        for u, up in ((2, "d=1"), (4, "d=3"), (1, "d=3")):
            self.play(Indicate(labels[u], color=ACCENT, scale_factor=1.3), run_time=0.25)
            self.play(Transform(labels[u], mono(up, 17, ACCENT).next_to(g.nodes[u], LEFT, buff=0.22)
                                if POS_GRAPH[u][1] >= 2.4 else
                                mono(up, 17, ACCENT).next_to(g.nodes[u], UP, buff=0.4)), run_time=0.25)
        self.play(FadeIn(mono("settled distance never revisited", 19, ACCENT).move_to([0, -2.9, 0])), run_time=0.4)
        _ = v

    def stale(self, beats):
        entries = ["(9, 2)", "(4, 2)", "(5, 1)"]
        tape = self.array([e for e in entries], size=22, side=1.1, y=0.5, idx=False, caption=mono("heap pops (d, u)", 19, MUTED))
        self.dismiss(tape.caption)
        dists = ["4", "5", "7"]
        drow = self.array(dists, size=22, side=0.7, y=-0.75, idx=False, caption=mono("dist[u]", 19, MUTED))
        self.dismiss(drow.caption)
        dlbl = mono("dist[u]", 19, MUTED).move_to([2.75, -0.75, 0])
        self.play(FadeIn(tape), FadeIn(drow), FadeIn(dlbl),
                  Create(Line([2.15, -0.75, 0], [-0.35, -0.75, 0], color=STROKE, stroke_width=1.2, buff=0)), run_time=0.4)
        alive = [False, True, False]
        for i, ok in enumerate(alive):
            if ok:
                self.play(tape.cells[i].animate.set_stroke(ACCENT, 2.2), run_time=0.2)
                self.play(Indicate(drow.cells[i], color=ACCENT, scale_factor=1.2), run_time=0.3)
            else:
                self.play(tape.cells[i].animate.set_opacity(0.3).set_stroke(BAD, 1.4), run_time=0.2)
        tag = self.callout("9 > dist[2]: skip the stale entry", BAD)
        self.play(Write(tag), run_time=0.4)

    def layered_dijkstra(self, beats):
        place = {}
        for k in range(3):
            for i in range(4):
                place[k * 4 + i] = (-3.3 + 2.2 * i, 1.2 - 0.95 * k)
        edges = [(k * 4 + i, k * 4 + i + 1, 2 + i) for k in range(3) for i in range(3)]
        edges += [(k * 4 + 1, (k + 1) * 4 + 1, 0) for k in range(2)]
        g = self.graph(edges, place)
        g.all.scale(0.78).shift(DOWN * 0.1)
        path = VGroup(Line(g.pos(0), g.pos(1), color=ACCENT, stroke_width=3.4),
                      Line(g.pos(1), g.pos(5), color=ACCENT, stroke_width=3.4).set_stroke(opacity=0.001),
                      Line(g.pos(5), g.pos(6), color=ACCENT, stroke_width=3.4))
        dashed = DashedVMobject(Line(g.pos(1), g.pos(5), color=ACCENT, stroke_width=3.4), num_dashes=10)
        self.play(Create(path), run_time=0.7)
        self.play(Create(dashed), run_time=0.3)
        tag = mono("(node, coupons used): 2 dimensions", 19, ACCENT).move_to([0, -2.2, 0])
        sub = mono("parent[state] rebuilds the route", 19, MUTED).next_to(tag, DOWN, buff=0.12)
        self.play(FadeIn(tag), FadeIn(sub), run_time=0.5)

    def bellman(self, beats):
        edges = [(0, 1, 4), (1, 2, -2), (0, 2, 5)]
        g = self.graph(edges, POS_GRAPH[:3] and [(0, 1.7), (1, 0.1), (2, -1.2)])
        rows = []
        values = [0, "inf", "inf"]
        table = self.row_series([f"0 {values[1]} {values[2]}"], "round 0", y=-1.8)
        self.play(FadeIn(table), run_time=0.3)
        for r, (u, v, w) in enumerate(edges):
            h = arrow(g.pos(u), g.pos(v), ACCENT, 3)
            self.play(Create(h), Indicate(g.labels[(u, v)], color=ACCENT, scale_factor=1.3), run_time=0.35)
            self.play(FadeOut(h), run_time=0.1)
        final = self.row_series(["0 4 2"], "round V-1: relaxed", y=-1.8)
        self.play(Transform(table, final), run_time=0.4)
        tag = mono("V - 1 rounds of every edge", 19, ACCENT).move_to([0, -2.4, 0])
        self.play(FadeIn(tag), run_time=0.4)

    def negcycle(self, beats):
        edges = [(0, 1, 1), (1, 2, -2), (2, 3, -2), (3, 1, 1), (0, 4, 3)]
        g = self.graph(edges, POS_GRAPH[:5])
        rounds = self.array(["r1", "r2", "r3", "r4", "r5"], size=18, side=0.66, y=-1.85, idx=False,
                            name="round")
        self.play(FadeIn(rounds), run_time=0.3)
        loop = Circle(radius=1.05, color=BAD, stroke_width=2.2).move_to((g.pos(1) + g.pos(3)) / 2)
        self.play(Create(loop), *[Indicate(rounds.cells[i], color=ACCENT, scale_factor=1.2) for i in range(4)], run_time=0.9)
        self.play(rounds.cells[4].animate.set_color(BAD), rounds.cells[4].animate.set_stroke(BAD, 2), run_time=0.25)
        self.play(Indicate(g.nodes[2], color=BAD, scale_factor=1.2), Indicate(g.nodes[3], color=BAD, scale_factor=1.2), run_time=0.4)
        tag = mono("improved on round V: -inf reachable", 19, BAD).move_to([0, -2.4, 0])
        self.play(FadeIn(tag), run_time=0.4)

    def floyd(self, beats):
        grid = self.dgrid([["0", "4", "5"], ["4", "0", "1"], ["5", "1", "0"]], size=24, side=0.66)
        self.play(FadeIn(grid, shift=DOWN * 0.1), run_time=0.4)
        tag = mono("pivot k outermost: 0, 1, 2", 19, MUTED).move_to([-0.4, -1.4, 0])
        self.play(FadeIn(tag), run_time=0.3)
        k_row = Rectangle(width=grid.width + 0.12, height=0.74, stroke_color=BAD, stroke_width=2, fill_opacity=0)
        k_row.move_to(grid[0])
        k_col = Rectangle(width=0.78, height=grid.height + 0.12, stroke_color=ACCENT, stroke_width=2, fill_opacity=0)
        k_col.move_to(grid[0][0])
        self.play(Create(k_row), Create(k_col), run_time=0.4)
        self.play(grid[2][0][1].animate.set_color(ACCENT), grid[0][2][1].animate.set_color(ACCENT), run_time=0.4)
        eq = self.math("d[2][2] = \\min(0,\\ 5 + 5)", ACCENT, 24).move_to([4.3, -0.4, 0])
        self.play(Write(eq), run_time=0.4)
        self.play(self.grid_value(grid[2][1], "4", ACCENT), run_time=0.3)
        self.play(Indicate(grid[2][1], color=ACCENT, scale_factor=1.2), run_time=0.5)

    def closure(self, beats):
        grid = self.dgrid([["0", "1", "0", "0"], ["0", "0", "1", "0"], ["0", "0", "0", "1"], ["1", "0", "0", "0"]], size=22, side=0.6)
        self.play(FadeIn(grid), run_time=0.4)
        self.play(grid[0][0][1].animate.set_color(BAD), grid[1][1][1].animate.set_color(BAD),
                  grid[2][2][1].animate.set_color(BAD), grid[3][3][1].animate.set_color(BAD), run_time=0.4)
        diag = VGroup(*(Dot([grid[i][i].get_corner(UP + RIGHT)[0] - 0.05, grid[i][i].get_corner(UP + RIGHT)[1] - 0.05, 0],
                            radius=0.06, color=ACCENT) for i in range(4)))
        self.play(LaggedStart(*(FadeIn(d) for d in diag), lag_ratio=0.15), run_time=0.6)
        tag = mono("one reachable cycle: all pairs link", 19, ACCENT).move_to([-0.4, -1.45, 0])
        self.play(FadeIn(tag), run_time=0.4)
        minimax = mono("max(w) minimax via \\min/max", 19, MUTED).move_to([0, -1.95, 0])
        self.play(FadeIn(minimax), run_time=0.35)

    def mst(self, beats):
        edges = [(0, 1, 3), (1, 2, 1), (2, 3, 4), (3, 0, 7), (0, 4, 2), (3, 4, 5)]
        g = self.graph(edges, POS_GRAPH[:5])
        accepted = [(1, 2, 1), (0, 4, 2), (0, 1, 3), (3, 4, 5)]
        total = 0
        for u, v, w in accepted:
            ln = Line(g.pos(u), g.pos(v), color=ACCENT, stroke_width=4).set_opacity(0.85)
            self.play(Create(ln), g.nodes[u].paint("#1E2B1F", ACCENT), g.nodes[v].paint("#1E2B1F", ACCENT), run_time=0.35)
            g.nodes[u].paint("#1E2B1F", ACCENT)
            g.nodes[v].paint("#1E2B1F", ACCENT)
            total += w
            wl = g.labels[(u, v)]
            self.play(wl[1].animate.set_opacity(1),
                      Transform(wl[1], mono(str(w), 17, ACCENT).move_to(wl[1]).shift(UP * 0.15 + RIGHT * 0.1)), run_time=0.2)
        tag = mono(f"accepted weights = {total}, edges = V - 1", 19, ACCENT).move_to([0, -1.75, 0])
        self.play(FadeIn(tag), run_time=0.4)
        self.play(Indicate(g.labels[(3, 0)], color=BAD, scale_factor=1.3), run_time=0.5)

    def bridges(self, beats):
        edges = [(0, 1), (1, 2), (2, 3), (1, 3), (3, 4), (2, 5), (5, 6)]
        g = self.graph(edges, POS_BRIDGE, weighted=False)
        tree = self.tree_edges([(0, 1), (1, 2), (2, 3), (3, 4), (2, 5), (5, 6)])
        self.play(Create(tree), run_time=0.9)
        for u in range(7):
            g.nodes[u].paint(CARD, ACCENT, ACCENT)
        pairs = [(0, 1, "tin 0/1"), (1, 2, "tin 1/2"), (2, 3, "tin 2/3"), (1, 3, "back"), (3, 4, "low 4 > 3")]
        badges = []
        for (u, v, txt) in [(0, 1, "tin"), (1, 2, "tin"), (2, 3, "tin"), (3, 4, "low>tin")]:
            b = mono(txt, 15, PAPER).next_to(g.labels[(3, 4)], LEFT, buff=0.4)
            badges.append(b)
        bridge_edges = [g.edges[(0, 1)], g.edges[(3, 4)], g.edges[(5, 6)]]
        self.play(*[Create(Circle(radius=0.03, color=BAD) ) for _ in bridge_edges], run_time=0.05)
        self.play(*[e.animate.set_color(BAD).set_stroke(width=4) for e in bridge_edges], run_time=0.6)
        tag = mono("low[v] > tin[u]: bridge, pulse red", 19, BAD).move_to([0, -2.15, 0])
        self.play(FadeIn(tag), run_time=0.4)
        cut = Circle(radius=0.42, color=BAD, stroke_width=2.2).move_to(g.pos(1))
        self.play(Create(cut), run_time=0.4)

    def condense(self, beats):
        edges = [(0, 1), (1, 2), (2, 3), (1, 3), (3, 4)]
        g = self.graph(edges, POS_BRIDGE[:5], weighted=False)
        self.play(Create(self.tree_edges([(0, 1), (1, 2), (2, 3), (3, 4)])), run_time=0.7)
        block = VGroup(Rectangle(width=1.9, height=1.5, stroke_color=ACCENT, fill_color=ACCENT, fill_opacity=0.1)
                       .move_to((g.pos(1) + g.pos(3)) / 2 + LEFT * 0.1),
                       mono("2-edge block", 17, ACCENT).move_to((g.pos(1) + g.pos(3)) / 2 + DOWN * 0.95))
        self.play(Create(block[0]), FadeIn(block[1]), run_time=0.6)
        for k in (1, 2, 3, 4):
            self.play(Indicate(g.nodes[k], color=ACCENT, scale_factor=1.05), run_time=0.06)
        for k in (1, 2, 3):
            self.play(g.nodes[k].animate.set_opacity(0.35), run_time=0.1)
        super_node = TNode("block", 0.5, fill="#1E2B1F", stroke=ACCENT, size=17).move_to((g.pos(1) + g.pos(3)) / 2)
        self.play(FadeIn(super_node, scale=0.6), run_time=0.5)
        self.play(Create(Line(super_node.get_left(), g.pos(0), color=ACCENT, stroke_width=3, buff=0.5)),
                  Create(Line(super_node.get_right(), g.pos(4), color=ACCENT, stroke_width=3, buff=0.5)), run_time=0.5)
        tag = mono("condensed: a bridge tree for LCA queries", 19, ACCENT).move_to([0, -2.1, 0])
        self.play(FadeIn(tag), run_time=0.4)

    def diameter(self, beats):
        tree = self.tree(STEM_TREE, r=0.25)
        for k in range(1, 8):
            if k != 4:
                self.play(tree[k].animate.set_opacity(0.45), run_time=0.05)
        self.play(tree[3].paint("#1E2B1F", BAD), tree[4].paint("#1E2B1F", BAD), run_time=0.3)
        sweep = arrow(tree.pos(3), tree.pos(4), BAD, 2.6, buff=0.3)
        self.play(Create(sweep), run_time=0.5)
        tags = {3: "A", 4: "B"}
        marks = VGroup(*(mono(t, 18, BAD).next_to(tree[k], LEFT, buff=0.12) for k, t in tags.items()))
        self.play(FadeIn(marks), run_time=0.3)
        self.play(Create(arrow(tree.pos(4), tree.pos(3), ACCENT, 2.6, buff=0.3)), tree[3].paint("#1E2B1F", ACCENT), run_time=0.5)
        tag = mono("BFS from A finds B: distance 4", 19, ACCENT).move_to([0, -1.95, 0])
        self.play(FadeIn(tag), run_time=0.4)

    def centroid(self, beats):
        tree = self.tree(STEM_TREE, r=0.25)
        counts = {1: "1", 2: "3", 3: "1", 4: "7", 5: "1", 6: "3", 7: "1"}
        tags = VGroup(*(mono(counts[k], 16, ACCENT).next_to(tree[k], DOWN, buff=0.14) for k in counts))
        self.play(LaggedStart(*(FadeIn(t) for t in tags), lag_ratio=0.1), run_time=0.6)
        for k in (4, 6):
            ring = Circle(radius=0.36, color=BAD, stroke_width=2).move_to(tree[k])
            self.play(Create(ring), tree[k].paint("#1E2B1F", BAD), run_time=0.3)
        self.play(tree[4].paint("#1E2B1F", ACCENT), tree[4].animate.scale(1.15), run_time=0.4)
        tag = mono("max branch 3 <= N/2 = 3.5: walk to 4", 19, ACCENT).move_to([0, -1.95, 0])
        self.play(FadeIn(tag), run_time=0.4)

    # -- number theory and bits -------------------------------------------
    def euclid(self, beats):
        a, b = 84, 30
        left = mono(f"{a} = {a // b} × {b} + {a % b}", 28, PAPER).move_to([0, 1.05, 0])
        self.play(FadeIn(left, shift=DOWN * 0.15), run_time=0.4)
        chain = VGroup()
        x, y = b, a % b
        while y:
            chain.add(mono(f"gcd({x}, {y})", 24, ACCENT))
            chain.arrange(RIGHT, buff=0.55).move_to([0, 0.1, 0])
            self.play(FadeIn(chain[-1], shift=RIGHT * 0.1), run_time=0.2)
            x, y = y, x % y
        steps = self.math("84 \\to 30 \\to 24 \\to 6", PAPER, 26).move_to([0, -1.0, 0])
        self.play(Write(steps), run_time=0.4)
        ans = mono(f"gcd = {x} = gcd(b, a mod b)", 24, ACCENT).move_to([0, -1.75, 0])
        self.play(FadeIn(ans), Indicate(chain, color=ACCENT), run_time=0.6)

    def bezout(self, beats):
        base = mono("240 * -33 + 46 * 172 = 2", 27, PAPER).move_to([0, 0.8, 0])
        self.play(FadeIn(base, shift=DOWN * 0.15), run_time=0.4)
        table = VGroup(mono("u = 0, v = 1: 46", 19, MUTED),
                       mono("prev = (1, 1 - 5 * 0) = (1, 1): 10", 19, ACCENT),
                       mono("prev = (0, 1 - 4 * 1) = (-4, 1): 6", 19, ACCENT))
        table.arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to([0, -0.75, 0])
        self.play(LaggedStart(*(FadeIn(t, shift=RIGHT * 0.1) for t in table), lag_ratio=0.2), run_time=0.8)
        ok = mono("solutions iff g divides the right side", 20, ACCENT).move_to([0, -2.0, 0])
        self.play(FadeIn(ok), Indicate(base, color=ACCENT), run_time=0.5)

    def modinv(self, beats):
        rows = VGroup(*(self.pyfloat(mono(s, 21)).move_to([0, 0.95 - 0.78 * k, 0]) for k, s in enumerate(
            ["a = 3, m = 11", "gcd(3, 11) = 1 wants inv"])),
            )
        rows[0].move_to([0, 1.0, 0])
        rows[1].move_to([0, 0.25, 0])
        self.play(FadeIn(rows), run_time=0.4)
        self.play(Write(self.math("3 \\cdot 4 \\equiv 1 \\pmod{11}", ACCENT, 30).move_to([0, -0.7, 0])), run_time=0.5)
        tag = mono("same extended Euclid inside C", 19, ACCENT).move_to([0, -1.6, 0])
        self.play(FadeIn(tag), run_time=0.35)
        row = VGroup(mono("gcd(a, m) != 1  ->  no inverse", 19, MUTED).move_to([0, -2.1, 0]),
                     mono("b * pow(a, -1, m)", 19, PAPER).move_to([0, -2.45, 0]))
        self.play(FadeIn(row), run_time=0.4)

    def crt(self, beats):
        a = self.pyfloat(mono("x ≡ 2 (mod 3)", 22))
        a.move_to([-2.3, 0.55, 0])
        b = self.pyfloat(mono("x ≡ 3 (mod 5)", 22))
        b.move_to([2.3, 0.55, 0])
        self.play(FadeIn(a), FadeIn(b), run_time=0.4)
        rows = VGroup(mono("mod 3:  2  5  8  11  14", 19, MUTED), mono("mod 5:  3  8  13  18", 19, MUTED))
        rows.arrange(DOWN, buff=0.16, aligned_edge=LEFT).move_to([0, -0.5, 0])
        self.play(FadeIn(rows), run_time=0.4)
        fit = self.pyfloat(mono("x = 8", 22, )).move_to([0, -1.45, 0])
        self.play(FadeIn(fit), run_time=0.3)
        mod = mono("unique mod lcm(3, 5) = 15", 20, ACCENT).move_to([0, -2.1, 0])
        self.play(FadeIn(mod), Indicate(rows, color=ACCENT), run_time=0.6)

    def sieve_spf(self, beats):
        grid = VGroup(*(cell(str(v), 16, 0.44) for v in range(4, 25)))
        for k in range(3):
            grid[k * 7:(k + 1) * 7].arrange(RIGHT, buff=0.07)
        grid.arrange(DOWN, buff=0.07).move_to([-1.4, 0.25, 0])
        self.play(LaggedStart(*(FadeIn(c) for c in grid), lag_ratio=0.01), run_time=0.35)
        for p in (2, 3):
            self.play(Indicate(grid[p - 2], color=ACCENT, scale_factor=1.4), run_time=0.25)
            idx = [i for i in range(21) if (i + 16) > p * p and (i + 16) % p == 0]
            self.play(*[grid[i][1].animate.set_color(BAD).set_opacity(0.4) for i in idx], run_time=0.4)
        self.play(*[grid[i][1].animate.set_color(ACCENT).set_opacity(1) for i in range(21) if (i + 16) in (4, 9)], run_time=0.3)
        code = VGroup(mono("for p in range(2, isqrt(N) + 1):", 17, PAPER), mono("    spf[p*p::p] = p", 17, ACCENT))
        code.arrange(DOWN, buff=0.1, aligned_edge=LEFT).move_to([4.1, -1.0, 0])
        self.play(Write(code), run_time=0.5)
        tag = mono("start at p * p, write only unset slots", 18, MUTED).move_to([0, -1.9, 0])
        self.play(FadeIn(tag), run_time=0.4)

    def primes(self, beats):
        tape = self.array([str(v) for v in [2, 3, 7]], size=24, side=0.7, caption=mono("prime factors of 42", 19, MUTED))
        self.play(FadeIn(tape, shift=DOWN * 0.2), run_time=0.4)
        big = VGroup(mono("n up to 1e12", 19, MUTED), mono("√n <= 1e6", 19, ACCENT))
        big.arrange(RIGHT, buff=0.6)
        self.play(FadeIn(big), run_time=0.3)
        rem = self.pyfloat(mono("n > 1, drop factors", 18)).move_to([0, -1.6, 0])
        self.play(FadeIn(rem), run_time=0.3)
        tag = mono("d * d <= n, then remainder is prime", 19, ACCENT).move_to([0, -2.2, 0])
        self.play(FadeIn(tag), run_time=0.4)
        mr = VGroup(mono("64-bit: deterministic Miller-Rabin", 18, PAPER), mono("bases 2, 3, 5, .., 37", 18, PAPER))
        mr.arrange(RIGHT, buff=0.5)
        self.play(FadeIn(mr), run_time=0.35)

    def star(self, beats, n=6):
        nodes = VGroup(*(TNode(str(i), 0.26, size=18).move_to([0.9 * np.cos(np.pi / 2 - i * 2 * np.pi / n) * 2.3,
                                                              0.85 * np.sin(np.pi / 2 - i * 2 * np.pi / n) * 2.1 + 0.1, 0])
                         for i in range(n)))
        edges = VGroup(*(Line(nodes[0].get_center(), nodes[k].get_center(), color=STROKE, stroke_width=2, buff=0.26)
                         for k in range(1, n)))
        self.play(Create(edges), LaggedStart(*(FadeIn(x) for x in nodes), lag_ratio=0.08), run_time=0.6)
        self.play(*[FadeIn(mono(f"{p}p, {q}q", 15, MUTED).move_to(np.array([0, 0, 0]) + (nodes[k].get_center() - nodes[0].get_center()) * 0.55)) for k, (p, q) in enumerate([(2, 1), (3, 2), (5, 3), (7, 4), (11, 5)], start=1)], run_time=0.4)
        self.play(nodes[0].paint("#1E2B1F", ACCENT), run_time=0.25)
        win = mono("sum = 2 + 3 + 5 + 7 + 11 = 28", 19, ACCENT).move_to([0, -1.85, 0])
        self.play(FadeIn(win), Indicate(nodes, color=ACCENT, scale_factor=1.03), run_time=0.5)

    def binary(self, beats):
        x = 12
        cells, header = self.bits(x, 6, y=0.75)
        header.shift(RIGHT * 0.15)
        self.play(FadeIn(cells, shift=RIGHT * 0.15), FadeIn(header), run_time=0.5)
        dec = mono(f"x = {x}", 19, MUTED).move_to([-3.6, 0.75, 0])
        self.play(FadeIn(dec), run_time=0.2)
        low = cells[5]
        self.play(Indicate(low, color=BAD, scale_factor=1.4), run_time=0.4)
        minus = mono("x - 1 flips the low bit, trailing zeros become ones", 19, PAPER).move_to([0, -0.25, 0])
        self.play(FadeIn(minus), run_time=0.35)
        cleared = self.bits_row(x & (x - 1), 6, y=-1.05)
        self.play(TransformFromCopy(cells, cleared), run_time=0.6)
        self.play(Indicate(cleared[2], color=ACCENT, scale_factor=1.4), run_time=0.4)
        tag = mono("popcount 2 -> 1: one set bit cleared", 19, ACCENT).move_to([0, -1.8, 0])
        self.play(FadeIn(tag), run_time=0.4)
        self.play(FadeIn(mono("x & (x-1) == 0  <=>  power of two", 18, MUTED).move_to([0, -2.3, 0])), run_time=0.4)

    def xor_pairs(self, beats):
        piles = [4, 5]
        squares = VGroup(*(Square(0.62, stroke_color=ACCENT, stroke_width=1.6, fill_color="#1E2B1F", fill_opacity=1) for _ in range(3)))
        squares.arrange(RIGHT, buff=0.14).move_to([0, 0.55, 0])
        pair = self.row_series([str(p) for p in piles], "two piles", y=-0.35)
        self.play(FadeIn(squares), FadeIn(pair), run_time=0.4)
        for _ in range(2):
            self.play(squares[-1].animate.set_opacity(0.2), squares.animate.shift(RIGHT * 0.14), run_time=0.35)
        self.play(squares.animate.shift(LEFT * 0.28).set_opacity(0.2), run_time=0.3)
        self.play(Transform(pair, self.row_series(["2", "2"], "equal piles", y=-0.35)),
                  Transform(squares, VGroup(*(Square(0.62, stroke_color=ACCENT, stroke_width=1.6, fill_color="#1E2B1F", fill_opacity=1) for _ in range(2)))
                            .arrange(RIGHT, buff=0.14).move_to([0, 0.55, 0])), run_time=0.5)
        xor = self.math("4 \\oplus 5 = 1", PAPER, 30).move_to([0, -1.35, 0])
        self.play(Write(xor), run_time=0.4)
        self.play(Transform(pair, self.row_series(["0", "0"], "XOR 0: second (P) wins", y=-0.35)),
                  Transform(squares, VGroup(*(Square(0.62, stroke_color=BAD, stroke_width=1.6, stroke_dash_array=[0.1, 0.1]) for _ in range(2)))
                            .arrange(RIGHT, buff=0.14).move_to([0, 0.55, 0])), Transform(xor, self.math("4 \\oplus 5 = 0", ACCENT, 30).move_to([0, -1.35, 0])),
                  run_time=0.6)

    def xor_cancel(self, beats):
        rows = [[2, 5], [3], [1, 4, 6]]
        cells = VGroup(*(VGroup(mono(str(v), 20, PAPER) for v in line) for line in rows))
        for line in cells:
            line.arrange(RIGHT, buff=0.32)
        cells.arrange(DOWN, buff=0.22).move_to([-0.6, 0.45, 0])
        self.play(LaggedStart(*(FadeIn(c) for line in cells for c in line), lag_ratio=0.08), run_time=0.7)
        self.play(*[line.animate.set_opacity(0.25) for line in cells], run_time=0.3)
        keep = VGroup(cells[0][0], cells[1][0], cells[2][1])
        self.play(*[k.animate.set_opacity(1) for k in keep], run_time=0.3)
        x = self.math("X = 7 \\oplus 2 \\oplus 5 = 0", ACCENT, 28).move_to([0, -1.35, 0])
        self.play(Write(x), run_time=0.4)
        tag = mono("XOR 0: every pile follows the opponent", 19, ACCENT).move_to([0, -1.95, 0])
        self.play(FadeIn(tag), run_time=0.4)

    def max_subset(self, beats):
        basis = ["1101", "0110", "0011"]
        rows = VGroup(*(VGroup(mono(f"basis[{i}]", 17, MUTED), row([c for c in b], size=20)) for i, b in enumerate(basis)))
        for line in rows:
            line.arrange(RIGHT, buff=0.3)
        rows.arrange(DOWN, buff=0.2, aligned_edge=LEFT).move_to([-1.4, 0.55, 0])
        self.play(LaggedStart(*(FadeIn(r) for r in rows), lag_ratio=0.2), run_time=0.7)
        x = self.pyfloat(mono("x = 0110", 22)).move_to([2.6, 0.55, 0])
        self.play(FadeIn(x), run_time=0.3)
        self.play(*[rows[i][1].animate.set_color(ACCENT) for i in range(3)], run_time=0.4)
        best = self.math("\\max(X) = 1111", ACCENT, 30).move_to([0, -1.1, 0])
        self.play(Write(best), run_time=0.4)
        tag = mono("greedy from the top bit downward", 19, ACCENT).move_to([0, -1.85, 0])
        self.play(FadeIn(tag), run_time=0.4)

    # -- strings -----------------------------------------------------------
    def hash_panel(self, beats):
        title = mono("H[R] = H[L-1] * P[R-L+1] + hash[A[L..R]]", 20, PAPER).move_to([-3.0, 0.85, 0])
        grid = self.dgrid([["1", "2", "3", "4", "5", "6"], ["0", "1", "2", "3", "4", "5"]], size=20, side=0.5)
        grid.move_to([-3.2, -0.1, 0])
        self.play(FadeIn(title), run_time=0.3)
        self.play(LaggedStart(*(FadeIn(c) for line in grid for c in line), lag_ratio=0.01), run_time=0.31)
        self.play(*[grid[0][i].animate.set_stroke(ACCENT, 1.6) for i in range(6)], run_time=0.3)
        for k, (a, b) in enumerate([(0, 1), (1, 2), (0, 3), (3, 4)]):
            row = self.row_series([f"H[{a}] * P[{b - a + 1}] + h[{b}]", f"H[{b}]"], f"position {b}", y=-1.15, color=ACCENT)
            row[0].move_to([3.4, 0.3, 0])
            self.play(FadeIn(row), run_time=0.4)

    def substr_hash(self, beats):
        tape = self.array(list("abracad"), size=24, y=0.65)
        self.play(FadeIn(tape), run_time=0.35)
        sub = self.box_at(tape.cells, 1, 4, ACCENT, y=tape.cells.get_center()[1])
        self.play(Create(sub), run_time=0.35)
        self.play(self.math("H[4] - H[0] \\cdot P[4]", ACCENT, 30).move_to([0, -0.7, 0]), run_time=0.4)
        self.play(self.math("= \\text{hash('brac')}", PAPER, 30).move_to([0, -1.4, 0]),
                  Create(self.box_at(tape.cells, 6, 8, MUTED, y=tape.cells.get_center()[1])), run_time=0.4)
        box2 = self.box_at(tape.cells, 6, 8, ACCENT, y=tape.cells.get_center()[1])
        self.play(Transform(sub, box2), run_time=0.4)
        self.play(TwoWay if False else FadeIn(mono("equal hashes in O(1): sliding window", 19, ACCENT).move_to([0, -2.05, 0])), run_time=0.4)

    def double_hash(self, beats):
        widths = self.array([f"({i} collisions)", ] if False else [""] * 7, size=18, side=0.66, y=0.3)
        n = 7
        bars = VGroup(*(Rectangle(width=0.4, height=0.3 + (1.6 if i >= 5 else 0.5), stroke_color=ACCENT if i >= 5 else BAD,
                                  fill_color=ACCENT if i >= 5 else BAD, fill_opacity=0.6) for i in range(n)))
        bars.arrange(RIGHT, buff=0.1, aligned_edge=DOWN).move_to([0, -0.5, 0])
        amounts = ["3", "5", "8", "12", "20", "31", "48"]
        tags = VGroup(*(mono(a, 17, ACCENT if i >= 5 else BAD).next_to(bars[i], DOWN, buff=0.12) for i, a in enumerate(amounts)))
        self.play(*[FadeIn(t) for t in tags[:2]], LaggedStart(*(Create(b) for b in bars), lag_ratio=0.1), run_time=0.7)
        self.play(*[FadeIn(t) for t in tags[2:]], run_time=0.35)
        tag = mono("base 10^9+7: collisions grow", 19, BAD).move_to([0, -1.55, 0])
        self.play(FadeIn(tag), run_time=0.35)
        fix = mono("double hash/random base: negligible", 19, ACCENT).move_to([0, -2.1, 0])
        self.play(FadeIn(fix), run_time=0.4)

    def lcp_panel(self, beats):
        A = self.array(list("abracad"), size=22, y=1.0)
        B = self.array(list("abrazer"), size=22, y=0.05)
        self.play(FadeIn(A), FadeIn(B), run_time=0.5)
        tip = self.ptr("len", ACCENT)
        mid = 4
        self.play(FadeIn(tip), run_time=0.2)
        spans = VGroup(*(self.box_at(A.cells, 0, L - 1, ACCENT, y=A.cells.get_center()[1]) for L in (2, 4)))
        self.play(*[Create(s) for s in spans], run_time=0.5)
        self.play(FadeIn(mono("equal hash: len 4 works, try longer", 19, ACCENT).move_to([0, -1.0, 0])), run_time=0.4)
        self.play(FadeIn(mono("first differ at index 4", 19, PAPER).move_to([0, -1.5, 0])),
                  Indicate(VGroup(A.cells[4], B.cells[4]), color=BAD, scale_factor=1.3), run_time=0.5)
        rev = mono("hash S and reversed S for palindrome LCP", 19, MUTED).move_to([0, -2.0, 0])
        self.play(FadeIn(rev), run_time=0.4)

    def kmp_borders(self, beats):
        word = "ababab"
        tape = self.array(list(word), size=24, y=0.75)
        self.play(FadeIn(tape), run_time=0.35)
        for k, (L, color) in enumerate([(4, ACCENT), (2, MUTED), (0, BAD)]):
            if L:
                pre = self.box_at(tape.cells, 0, L - 1, color, y=tape.cells.get_center()[1])
                suf = self.box_at(tape.cells, len(word) - L, len(word) - 1, color, y=tape.cells.get_center()[1])
                self.play(Create(pre), Create(suf), run_time=0.45)
                if k < 2:
                    self.play(FadeOut(pre, suf), run_time=0.2)
        pi = self.array(["", "", "", "", "", ""], size=20, side=0.6, y=-0.85, idx=False, caption=mono("pi[i]", 18, MUTED))
        self.dismiss(pi.caption)
        self.play(FadeIn(pi), run_time=0.25)
        vals = [0, 0, 1, 2, 3, 4]
        for i, v in enumerate(vals):
            self.play(FadeIn(mono(str(v), 20, ACCENT).move_to(pi.cells[i])), run_time=0.15)
        tag = mono("ababab: border 4 exists", 19, ACCENT).move_to([0, -1.6, 0])
        self.play(FadeIn(tag), run_time=0.35)
        arr = self.row_series(["a", "b", "a", "b", "c"], "text, no pattern hit", y=-2.15)
        self.play(FadeIn(arr), run_time=0.35)
        self.play(Indicate(arr[0][4], color=BAD, scale_factor=1.4), run_time=0.4)

    def kmp_fallback(self, beats):
        word = "abababc"
        tape = self.array(list(word), size=24, y=0.7)
        pi = self.array(["0", "0", "1", "2", "3", "4", "0"], size=18, side=0.6, y=-0.55, idx=False, caption=mono("pi", 18, MUTED))
        self.dismiss(pi.caption)
        self.play(FadeIn(tape), FadeIn(pi), run_time=0.5)
        j = self.ptr("j", ACCENT)
        i = self.ptr("i", BAD)
        self.over(j, tape.cells[5])
        self.over(i, tape.cells[6])
        self.play(FadeIn(j), FadeIn(i), run_time=0.3)
        self.play(Indicate(tape.cells[6], color=BAD, scale_factor=1.3), run_time=0.35)
        jpos = [5, 3, 1]
        for p in jpos[1:]:
            self.play(j.animate.next_to(tape.cells[p], UP, buff=0.1),
                      pi.cells[p].animate.set_color(ACCENT), run_time=0.4)
            trail = arrow(tape.cells[5 if p == 3 else 3].get_center(), tape.cells[p].get_center(), ACCENT, 2.4, buff=0.4)
            self.play(Create(trail), run_time=0.3)
        tag = mono("j = pi[j-1], i never rewinds", 19, ACCENT).move_to([0, -1.35, 0])
        self.play(FadeIn(tag), run_time=0.4)
        line = mono("total: O(N) fallbacks", 19, MUTED).move_to([0, -1.85, 0])
        self.play(FadeIn(line), run_time=0.35)

    def kmp_matches(self, beats):
        word = "abxab"
        idx = list(range(len(word)))
        hits = [i for i in idx if word[i] == "b"]
        tape = self.array(list(word), size=22, y=0.75, idx_colors={i: ACCENT if i in hits else MUTED for i in idx})
        self.play(FadeIn(tape), run_time=0.4)
        for i in hits:
            self.play(Indicate(tape.cells[i], color=ACCENT, scale_factor=1.3), run_time=0.35)
        nxt = self.array(["1", "3", "0", "2", "0"], size=20, side=0.55, y=-0.75, idx=False, caption=mono("next[i]", 18, MUTED))
        self.dismiss(nxt.caption)
        self.play(FadeIn(nxt), run_time=0.3)
        self.play(FadeIn(mono("j = next[i], i += 1", 19, ACCENT).move_to([0, -1.55, 0])), run_time=0.35)
        self.play(FadeIn(mono("mark all matches in one pass", 19, PAPER).move_to([0, -2.05, 0])), run_time=0.35)

    def kmp_period(self, beats):
        word = list("abcabcabc")
        N = len(word)
        pi_val = 6
        k = N - pi_val
        tape = self.array(word, size=22, y=0.75)
        self.play(FadeIn(tape), run_time=0.35)
        for start in range(0, N - k + 1, k):
            blk = self.box_at(tape.cells, start, start + k - 1, ACCENT, y=tape.cells.get_center()[1])
            self.play(Create(blk), run_time=0.25)
        expr = self.math(f"N - \\pi[N-1] = {N} - {pi_val} = {k}", ACCENT, 26).move_to([0, -0.85, 0])
        self.play(Write(expr), run_time=0.4)
        div = mono(f"N % {k} == 0: string is period-{k}", 19, ACCENT).move_to([0, -1.55, 0])
        self.play(FadeIn(div), run_time=0.35)
        cnt = mono("prefix counts accumulate in reverse", 19, MUTED).move_to([0, -2.05, 0])
        self.play(FadeIn(cnt), run_time=0.35)

    def z_compute(self, beats):
        word = list("aabxaab")
        tape = self.array(word, size=22, y=0.85, idx_colors={0: ACCENT})
        self.play(FadeIn(tape), run_time=0.35)
        z = self.array(["", "", "", "", "", "", ""], size=18, side=0.6, y=-0.7, idx=False, caption=mono("z[i]", 18, MUTED))
        self.dismiss(z.caption)
        self.play(FadeIn(z), run_time=0.25)
        vals = [(0, "0"), (1, "1"), (2, "0"), (3, "0"), (4, "2"), (5, "1"), (6, "0")]
        for i, v in vals:
            self.play(FadeIn(mono(v, 18, ACCENT).move_to(z.cells[i])), run_time=0.12)
        lcp = self.row_series(["a", "a", "b"], "LCP with S", y=-1.9)
        self.play(FadeIn(lcp), run_time=0.35)
        self.play(Indicate(z.cells[1], color=ACCENT, scale_factor=1.2), Indicate(z.cells[4], color=ACCENT, scale_factor=1.2), run_time=0.5)

    def zbox(self, beats):
        word = list("aabaabaaa")
        tape = self.array(word, size=22, y=1.05, idx_colors={8: ACCENT})
        self.play(FadeIn(tape), run_time=0.35)
        # z0 = [1,5] conceptually: index 0 prefix matches suffix at 3
        zs = [0, 1, 0, 3, 2, 1, 0, 3, 1]
        zrow = self.array([str(z) for z in zs], size=16, side=0.6, y=-0.7, idx=False, caption=mono("z", 18, MUTED))
        self.dismiss(zrow.caption)
        self.play(FadeIn(zrow), run_time=0.3)
        box = self.box_at(tape.cells, 3, 5, ACCENT, y=tape.cells.get_center()[1])
        self.play(Create(box), run_time=0.35)
        mirror = VGroup(arrow(tape.cells[4].get_center(), tape.cells[1].get_center(), ACCENT, 2, buff=0.4),
                        mono("z[4-3] = z[1] = 1", 18, ACCENT).move_to([0, -1.35, 0]))
        self.play(Create(mirror[0]), Write(mirror[1]), run_time=0.45)
        tag = mono("copy inside [L, R], extend past R", 19, ACCENT).move_to([0, -1.85, 0])
        self.play(FadeIn(tag), run_time=0.4)

    def rz(self, beats):
        s = list("abababzababab")
        sentinel = 6
        tape = self.array(s, size=20, y=0.95,
                          colors={sentinel: {"stroke": BAD, "color": BAD, "fill": "#2C1B1A"}},
                          idx_colors={i: BAD if i > sentinel else (ACCENT if i == 6 else MUTED) for i in range(len(s))})
        self.play(FadeIn(tape), run_time=0.4)
        n = len(s)
        z = [0] * n
        L = R = 0
        self.play(tape.cells[sentinel].animate.scale(1.25), run_time=0.3)
        for i in range(sentinel + 1, n):
            if i <= R:
                z[i] = min(R - i + 1, z[i - L])
            while i + z[i] < n and s[z[i]] == s[i + z[i]]:
                z[i] += 1
            if i + z[i] - 1 > R:
                L, R = i, i + z[i] - 1
            self.play(tape.cells[i].animate.set_stroke(ACCENT, 1.6), run_time=0.12)
            if i - L >= 0 and i - L < n:
                self.play(Create(arrow(tape.cells[i].get_center(), tape.cells[i - L].get_center(), MUTED, 1.6, buff=0.45)), run_time=0.12)
        hits = [i for i in range(sentinel + 1, n) if z[i] >= sentinel]
        self.play(*[Indicate(tape.cells[i], color=ACCENT, scale_factor=1.3) for i in hits], run_time=0.5)
        tag = mono(f"match at every i with z[i] >= {sentinel}", 19, ACCENT).move_to([0, -1.9, 0])
        self.play(FadeIn(tag), run_time=0.4)

    def borders_z(self, beats):
        word = list("abacaba")
        N = len(word)
        tape = self.array(word, size=24, y=0.85)
        self.play(FadeIn(tape), run_time=0.35)
        z = [0, 0, 1, 0, 3, 0, 1]
        keys = VGroup(*(self.pyfloat(mono(t, 18)).move_to([4.3, 0.9 - 0.75 * k, 0]) for k, t in enumerate(["S + S", "cyclic shifts"])))
        keys[0][0].set_stroke(ACCENT)
        self.play(FadeIn(keys), run_time=0.35)
        for i, color in [(3, ACCENT), (5, BAD)]:
            hit = i + z[i] == N
            pre = self.box_at(tape.cells, 0, z[i] - 1, color, y=tape.cells.get_center()[1])
            suf = self.box_at(tape.cells, i, N - 1, color, y=tape.cells.get_center()[1])
            self.play(Create(pre), Create(suf),
                      FadeIn(mono(f"i = {i}: z = {z[i]}, i + z = {i + z[i]} {'= N border' if hit else ''}", 18, color)
                            .move_to([0, -1.4, 0])), run_time=0.4)
            if hit:
                self.play(Indicate(VGroup(pre, suf), color=ACCENT, scale_factor=1.05), run_time=0.3)
            self.play(FadeOut(pre), FadeOut(suf), run_time=0.15)
        self.play(FadeIn(mono("every i with i + z[i] == N is a border", 19, ACCENT).move_to([0, -1.4, 0])), run_time=0.35)
        self.play(FadeIn(mono("one scan, no per-border compare", 19, PAPER).move_to([0, -1.9, 0])), run_time=0.35)

    def wrap_para(self, text, width=34):
        words, lines, line = str(text).split(), [], ""
        for w in words:
            if len(line) + len(w) > width and line:
                lines.append(line)
                line = w
            else:
                line = f"{line} {w}".strip()
        lines.append(line)
        return VGroup(*(mono(s, 19, PAPER) for s in lines[:3])).arrange(DOWN, buff=0.12, aligned_edge=LEFT)

    def distinct_child(self, beats):
        parent = {0: None, 1: 0, 2: 0, 3: 1, 4: 1, 5: 3}
        children = {u: [] for u in parent}
        for v, p in parent.items():
            if p is not None:
                return p and children[p].append(v)
        roots = {}
        for u in parent:
            roots[u] = u if parent[u] is None else roots[parent[u]]
        uniq = {0: sorted({roots[v] for v in range(7) if roots[v] != 0})}
        root_children = {r: [v for v in range(7) if roots[v] == r and v != r] for r in uniq[0]}
        place = {0: (0, 1.2), 1: (-2.0, 1.2), 2: (-3.4, 0.3), 3: (-1.0, 0.3), 4: (-2.6, 0.3), 5: (-0.4, -0.6)}
        order = [0, 1, 2, 3, 4, 5]
        sy = {u: 1.2 - 0.85 * d for u, d in [(0, 0), (1, 0), (2, 1), (3, 1), (4, 1), (5, 2)]}
        nodes = {u: TNode(str(u), 0.25, size=18).move_to([0.7 * d, sy[u], 0]) for u, d in [(-1, 0), (0, 0), (-2, 0), (-3, 0), (1, 0), (2, 0)]}
        nodes[2].circle  # keep names
        lines_ = VGroup(*[Line(nodes[v].get_center(), nodes[1 if v in (2, 3, 4, 5) else 0].get_center(), color=STROKE, stroke_width=2, buff=0.24) for v in (2, 3, 4, 5)])
        self.play(Create(lines_), LaggedStart(*(FadeIn(n) for n in nodes.values()), lag_ratio=0.07), run_time=0.6)
        for u in (0, 1):
            nodes[u].paint("#1E2B1F", ACCENT)
        self.play(Indicate(VGroup(nodes[2], nodes[3], nodes[4], nodes[5]), color=BAD, scale_factor=1.1), run_time=0.5)
        nodes[2].text  # draw a dedupe note
        note = mono("parent[i] = find(parent[i]): drop repeats", 19, ACCENT).move_to([0, -1.75, 0])
        self.play(FadeIn(note), run_time=0.4)
        second = mono("second reversal pass restores edges", 19, PAPER).move_to([0, -2.25, 0])
        self.play(FadeIn(second), run_time=0.4)

    def reroot(self, beats):
        a = self.tree(LEAF_TREE)
        path = arrow(a.pos(1), a.pos(3), ACCENT, 2.6)
        self.play(Create(path), run_time=0.5)
        first = mono("down[] from root 1", 19, PAPER).move_to([0, -1.65, 0])
        self.play(FadeIn(first), run_time=0.35)
        self.play(FadeOut(a.all, path, first), run_time=0.3)
        b = self.tree(LEAF_TREE)
        back = arrow(b.pos(3), b.pos(1), ACCENT, 2.6)
        up = arrow(b.pos(1), b.pos(2), MUTED, 2.6)
        self.play(Create(back), Create(up), run_time=0.5)
        second = mono("up[] via sibling prefix products", 19, ACCENT).move_to([0, -1.85, 0])
        self.play(FadeIn(second), b[3].paint("#1E2B1F", ACCENT), run_time=0.5)

    def palindrome(self, beats):
        tape = self.array(list("aba"), size=26, y=0.85, idx_colors={0: ACCENT, 2: ACCENT})
        self.play(FadeIn(tape), run_time=0.35)
        L, R = self.ptr("L", ACCENT), self.ptr("R", BAD)
        self.over(L, tape.cells[0])
        self.over(R, tape.cells[2])
        self.play(FadeIn(L), FadeIn(R), run_time=0.3)
        self.play(tape.cells[0].animate.set_stroke(ACCENT, 2.4), tape.cells[2].animate.set_stroke(ACCENT, 2.4), run_time=0.3)
        inner = self.array(["dp[1][1]", "= 1"], size=18, side=1.0, y=-0.75, idx=False, caption=mono("inner [L+1, R-1]", 18, MUTED))
        self.dismiss(inner.caption)
        self.play(FadeIn(inner), run_time=0.3)
        expr = self.math("dp[L][R] = dp[L+1][R-1] + 2", ACCENT, 26).move_to([0, -1.6, 0])
        self.play(Write(expr), run_time=0.4)
        self.play(FadeIn(mono("else split mid-interval", 19, MUTED).move_to([0, -2.1, 0])), run_time=0.35)

    def doubling(self, beats):
        base = [4, 1, 5, 2]
        first = self.array([str(v) for v in base], size=24, y=0.9, caption=mono("A", 18, MUTED))
        self.dismiss(first.caption)
        second = self.array([str(v) for v in base], size=24, y=-0.15)
        self.play(FadeIn(first), FadeIn(second), run_time=0.4)
        plus = mono("A + A = 2N", 19, ACCENT).next_to(second, UP, buff=0.3)
        self.play(FadeIn(plus), run_time=0.3)
        win = self.box_at(second.cells, 2, 5, ACCENT, y=second.cells.get_center()[1])
        self.play(Create(win), run_time=0.35)
        tag = mono("best length-N window = cycle split", 19, ACCENT).move_to([0, -1.15, 0])
        self.play(FadeIn(tag), run_time=0.4)
        note = mono("no wrap-around special cases", 19, MUTED).move_to([0, -1.65, 0])
        self.play(FadeIn(note), run_time=0.35)


class Guider(Guide):
    """Every family visualizer: arrays, trees, graphs, grids, tapes and heaps."""

    # -- shared small boards ---------------------------------------------
    def bits(self, value, depth=8, y=0.6, size=20):
        bits = VGroup(*(cell((value >> (depth - 1 - i)) & 1, size, 0.44) for i in range(depth)))
        bits.arrange(RIGHT, buff=0.07).move_to([0.0, y, 0.0])
        head = mono(f"{value:b}".rjust(depth, "0"), 17, MUTED).next_to(bits, DOWN, buff=0.16)
        return bits, head

    def bits_row(self, value, depth=8, y=0.5):
        return self.bits(value, depth, y)[0]

    def row_series(self, values, title, y=-1.6, color=PAPER):
        texts = row(values, {}, 20, color=color)
        return VGroup(mono(title, 17, MUTED), texts).arrange(RIGHT, buff=0.3).move_to([0.0, y, 0.0])

    def lines(self, texts, x=-3.4, y=0.8, size=18):
        code = VGroup(*(mono(t, size, ACCENT if i == 0 else PAPER) for i, t in enumerate(texts)))
        fitw(code, 7.4)
        code.arrange(DOWN, buff=0.14, aligned_edge=LEFT)
        code.move_to([x, y, 0], aligned_edge=LEFT)
        return code

    def legend(self, pairs, y=FOOT_Y):
        heads = VGroup(*(mono(t, 16, c) for t, c in pairs)).arrange(RIGHT, buff=0.5).move_to([0.0, y, 0.0])
        self.play(FadeIn(heads), run_time=0.25)
        return heads

    # -- bit tricks ------------------------------------------------------
    def binary(self, beats):
        x = int(beats[-1]) if str(beats[-1]).isdigit() else 10
        x = min(max(int(x), 2), 12)
        count = 0
        v = x
        while v:
            count += v & 1
            v >>= 1
        cells, head = self.bits(x, 4, y=0.7)
        self.play(FadeIn(VGroup(cells, head)), run_time=0.5)
        num = mono(f"x = {x}", 22, PAPER).next_to(head, LEFT, buff=0.4)
        self.play(FadeIn(num), run_time=0.3)
        for i in (0, 2):
            self.play(Indicate(cells[i], color=ACCENT, scale_factor=1.3), run_time=0.35)
        self.play(Write(mono(f"bin(x) = {x:b}", 22, ACCENT).move_to([0, -0.8, 0])), run_time=0.4)
        self.play(FadeIn(mono(f"x & -1 = {x & -1}, x >> 1 = {x >> 1}", 20, MUTED).move_to([0, -1.5, 0])), run_time=0.4)
        self.play(FadeIn(mono(f"bit_count() = {count}: O(bits), not O(x)", 20, ACCENT).move_to([0, -2.1, 0])), run_time=0.45)

    def bit_ops_extra(self, beats):
        self.bit_ops(beats)

    def bitmask_states(self, beats):
        self.bitmask(beats)

    def xor_cancel(self, beats):
        nums = [4, 9, 4, 7, 9]
        tape = self.array(nums, size=22, y=0.85, idx_colors={0: ACCENT, 2: ACCENT, 1: BAD, 4: BAD})
        self.play(FadeIn(tape), run_time=0.4)
        for a, b in ((0, 2), (1, 4)):
            link = Line(tape.cells[a].get_top(), tape.cells[b].get_top(), color=ACCENT, stroke_width=2)
            link.shift(UP * 0.35)
            self.play(Create(link), Indicate(VGroup(tape.cells[a], tape.cells[b]), color=ACCENT, scale_factor=1.1), run_time=0.45)
        acc = 0
        rowx = VGroup(mono("acc", 18, MUTED))
        for v in nums:
            acc ^= v
            rowx.add(mono(f"^ {v} = {acc}", 18, PAPER if acc else ACCENT))
        rowx.arrange(DOWN, buff=0.12, aligned_edge=LEFT).move_to([-1.2, -0.9, 0])
        self.play(LaggedStart(*(FadeIn(m, shift=RIGHT * 0.1) for m in rowx), lag_ratio=0.2), run_time=0.9)
        self.play(FadeIn(mono(f"pairs cancel: {acc} is the singleton", 19, ACCENT).move_to([0, FOOT_Y, 0])), run_time=0.4)
        self.play(FadeIn(mono("reduce with functools.reduce(operator.xor, a)", 17, MUTED).move_to([0, FOOT_Y - 0.42, 0])), run_time=0.35)

    def xor_pairs(self, beats):
        nums = [3, 5, 3, 6]
        tape = self.array(nums, size=22, y=0.9, idx_colors={0: ACCENT, 2: ACCENT, 1: BAD})
        self.play(FadeIn(tape), run_time=0.4)
        acc = 0
        for v in nums:
            acc ^= v
        self.play(Write(mono(f"xor all: {acc:b}", 22, ACCENT).move_to([0, -0.6, 0])), run_time=0.45)
        low = acc & -acc
        self.play(Write(mono(f"low = acc & -acc = {low:b}", 20, PAPER).move_to([0, -1.2, 0])), run_time=0.4)
        group = [v for v in nums if v & low]
        self.play(*[Indicate(tape.cells[i], color=ACCENT, scale_factor=1.2) for i, v in enumerate(nums) if v & low], run_time=0.5)
        self.play(Write(mono(f"low-bit set: {group} -> {len(group)} values", 20, ACCENT).move_to([0, -1.85, 0])), run_time=0.45)
        self.play(FadeIn(mono("one partition sorts the two singles", 19, MUTED).move_to([0, FOOT_Y, 0])), run_time=0.4)


    def int_bits(self, beats):
        rows = VGroup(mono("i    0b101101 : count trailing zeros", 19, PAPER).move_to([0, 1.25, 0]),
                      mono("i & -i = lowbit", 19, ACCENT).move_to([0, 0.7, 0]))
        self.play(FadeIn(rows[0]), run_time=0.3)
        bits, header = self.bits(45, 6, y=0.0)
        self.play(FadeIn(bits), FadeIn(header), run_time=0.4)
        self.play(Indicate(bits[5], color=ACCENT, scale_factor=1.4), run_time=0.4)
        res = self.bits_row(1, 6, y=-1.0)
        self.play(FadeIn(rows[1]), TransformFromCopy(bits[5], res[5]), run_time=0.5)
        bit = self.math("i &= i - 1", ACCENT, 28).move_to([0, -1.75, 0])
        self.play(Write(bit), run_time=0.4)

    def tree_dp(self, beats):
        parent = {0: None, 1: 0, 2: 0, 3: 1, 4: 1, 5: 2}
        nodes, _ = TreeG.__new__(TreeG).forest(parent, {0: 1.35, 1: 0.45, 2: 0.45, 3: -0.55, 4: -0.55, 5: -0.55})
        kids = {u: [] for u in parent}
        for u, p in parent.items():
            if p is not None:
                kids[p].append(u)
        edges = VGroup(*(Line(nodes[u].get_center(), nodes[p].get_center(), color=STROKE, stroke_width=2, buff=0.26)
                         for u, p in parent.items() if p is not None))
        self.play(LaggedStart(*(Create(e) for e in edges), lag_ratio=0.08), run_time=0.6)
        self.play(LaggedStart(*(FadeIn(n) for n in nodes.values()), lag_ratio=0.07), run_time=0.5)
        self.play(nodes[0].paint("#1E2B1F", ACCENT), run_time=0.25)
        self.play(FadeIn(mono("root 0: draw parent -> child", 19, MUTED).move_to([0, -1.45, 0])), run_time=0.35)
        lit = VGroup()
        for u in (0, 1, 2):
            for v in kids[u]:
                lit.add(arrow(nodes[u].get_center(), nodes[v].get_center(), ACCENT, 2.2, buff=0.3))
        self.play(LaggedStart(*(Create(a) for a in lit), lag_ratio=0.15), run_time=0.9)
        down = mono("children before parents", 19, PAPER).move_to([0, -1.45, 0])
        self.play(FadeIn(down), run_time=0.35)
        order = ["5, 4, 3", "2, 1", "0"]
        for k, txt in enumerate(order):
            slot = self.array(txt.split(", "), size=20, side=0.56, y=-2.15, idx=False)
            self.play(FadeIn(slot), run_time=0.2)
        self.play(FadeIn(mono("reverse BFS order: no recursion depth", 18, ACCENT).move_to([0, -2.6, 0])), run_time=0.4)

    def tree_bars(self, beats):
        g = self.graph([(0, 1, 3), (0, 2, 5), (1, 3, 2), (2, 3, 4)], POS_GRAPH[:4], weighted=False)
        for k in g.edges:
            self.play(g.edges[k].animate.set_stroke(ACCENT, 2.4), run_time=0.1)
        g.nodes[0].paint("#1E2B1F", ACCENT)
        bar = self.row_series(["3 + 2 + 4 = 9", "V - 1 = 3 edges"], "tree total", y=-1.7)
        self.play(FadeIn(bar), run_time=0.4)
        self.play(Indicate(g.edges[(1, 3)], color=BAD), FadeIn(mono("add non-tree edge: cycle", 19, BAD).move_to([0, FOOT_Y, 0])), run_time=0.5)

    def mst_prim(self, beats):
        edges = [(0, 1, 3), (0, 2, 5), (1, 2, 1), (2, 3, 4)]
        g = self.graph([(u, v, w) for u, v, w in edges] + [(u, v, w) for u, v, w in edges], POS_GRAPH[:4])
        g.nodes[0].paint("#1E2B1F", ACCENT)
        heap = self.row_series(["(3, 1)", "(5, 2)"], "cut min-heap", y=-1.7)
        self.play(FadeIn(heap), g.nodes[0].animate.set_opacity(0.5), run_time=0.3)
        self.play(Indicate(g.labels[(1, 2)], color=ACCENT, scale_factor=1.4), run_time=0.4)
        self.play(Create(Line(g.pos(1), g.pos(2), color=ACCENT, stroke_width=3.5)),
                  Transform(heap, self.row_series(["(4, 3)"], "annex cheapest edge", y=-1.7)), run_time=0.5)
        self.play(FadeIn(mono("starts at vertex 0, grows one tree", 19, ACCENT).move_to([0, FOOT_Y, 0])), run_time=0.4)

    def panel(self, beats):
        tags = VGroup(mono("minimax path", 20, PAPER), mono("K components", 20, PAPER), mono("connectivity", 20, PAPER))
        tags.arrange(RIGHT, buff=0.6)
        self.play(LaggedStart(*(FadeIn(t, shift=UP * 0.1) for t in tags), lag_ratio=0.15), run_time=0.6)
        done = self.math("V - 1 = 4 edges chosen", ACCENT, 26).move_to([0, -0.9, 0])
        self.play(Write(done), run_time=0.4)
        self.play(FadeIn(mono("stop Kruskal after V - K merges", 19, ACCENT).move_to([0, -1.7, 0])), run_time=0.4)

    def articulation(self, beats):
        g = self.graph([(0, 1), (1, 2), (1, 3), (2, 3)], POS_GRAPH[:4], weighted=False)
        self.play(Create(self.tree_edges([(0, 1), (1, 2), (2, 3)])), run_time=0.7)
        back = Line(g.pos(3), g.pos(1), color=ACCENT, stroke_width=3).set_opacity(0.6)
        self.play(Create(back), run_time=0.4)
        self.play(Circle(radius=0.44, color=BAD, stroke_width=2.4).move_to(g.pos(1)).animate, run_time=0.0)
        cut = Circle(radius=0.44, color=BAD, stroke_width=2.4).move_to(g.pos(1))
        self.play(Create(cut), g.nodes[1].paint("#2C1B1A", BAD), run_time=0.5)
        self.play(FadeIn(mono("low[child] >= tin[u]: removing u splits", 19, BAD).move_to([0, FOOT_Y, 0])), run_time=0.45)

    def interval_len(self, beats):
        tape = self.array([str(v) for v in [2, 7, 4, 1, 5]], size=24, caption=mono("len = 1..N first", 19, MUTED))
        self.dismiss(tape.caption)
        self.play(FadeIn(tape), run_time=0.4)
        for length, color in [(1, MUTED), (2, ACCENT), (3, ACCENT)]:
            spans = VGroup(*(self.box_at(tape.cells, i, i + length - 1, color, pad=0.05, y=tape.cells.get_center()[1])
                             for i in range(0, 6 - length)))
            self.play(LaggedStart(*(Create(s) for s in spans), lag_ratio=0.1), run_time=0.5)
            self.play(FadeOut(spans), run_time=0.15)
        self.play(FadeIn(mono("L fixed, R = L + len - 1", 19, ACCENT).move_to([0, FOOT_Y, 0])), run_time=0.45)

    def interval_split(self, beats):
        tape = self.array([str(v) for v in [2, 3, 4, 1, 5]], size=24, caption=mono("split k for [L..R]", 19, MUTED))
        self.dismiss(tape.caption)
        self.play(FadeIn(tape), run_time=0.4)
        self.play(Create(self.box_at(tape.cells, 0, 4, MUTED, y=tape.cells.get_center()[1])), run_time=0.3)
        for k in (0, 1, 2):
            left = self.box_at(tape.cells, 0, k, ACCENT, y=tape.cells.get_center()[1])
            right = self.box_at(tape.cells, k + 1, 4, BAD, y=tape.cells.get_center()[1])
            self.play(Create(VGroup(left, right)), run_time=0.3)
            self.play(FadeOut(left, right), run_time=0.12)
        self.play(FadeIn(mono("dp[L][k] + dp[k+1][R] + cost", 19, ACCENT).move_to([0, FOOT_Y, 0])), run_time=0.45)

    def tree_reroot(self, beats):
        tree = self.tree(LEAF_TREE)
        path = arrow(tree.pos(1), tree.pos(3), ACCENT, 3)
        self.play(Create(path), run_time=0.5)
        self.play(line_arrow := line_arrow if False else Circle(radius=0.4, color=ACCENT, stroke_width=0).move_to(tree[3]), run_time=0.05)
        self.play(self.dismiss(tree.all), run_time=0.25)
        tree = self.tree(LEAF_TREE, r=0.3)
        up = VGroup(*(arrow(tree.pos(k), tree.pos(1), ACCENT, 1.6, buff=0.3) for k in (2,)))
        self.play(Create(up), FadeIn(mono("re-root at 3: only 2 directions", 19, ACCENT).move_to([0, FOOT_Y, 0])), run_time=0.5)

    def trie_passes(self, beats):
        self.trie(beats)
        counts = VGroup(mono("pass = 2", 17, ACCENT), mono("end = 1", 17, PAPER))
        counts.arrange(DOWN, buff=0.14).move_to([2.9, -1.35, 0])
        self.play(FadeIn(counts), self._last_end.paint("#1E2B1F", ACCENT), run_time=0.4)
        self.play(FadeIn(mono("prefix query: walk down, read pass", 18, MUTED).move_to([0, FOOT_Y, 0])), run_time=0.4)

    def check_bounds(self, beats):
        rows = VGroup(*(self.pyfloat(mono(s, 20)).move_to([0, 1.0 - 0.8 * k, 0]) for k, s in enumerate(
            ["sum % 2 must be 0", "min <= target <= max"])))
        self.play(FadeIn(rows), run_time=0.4)
        ok = mono("bounds hold: build", 20, ACCENT).move_to([0, -1.3, 0])
        self.play(FadeIn(ok), Indicate(rows, color=ACCENT), run_time=0.45)
        impossible = mono("else print -1 early", 19, BAD).move_to([0, -1.85, 0])
        self.play(FadeIn(impossible), run_time=0.35)
        self.play(FadeIn(mono("invariants beat guesswork", 19, MUTED).move_to([0, -2.3, 0])), run_time=0.35)

    def blocks(self, beats):
        n = 12
        B = 4
        cells = VGroup(*(Square(0.6, stroke_color=STROKE, fill_color=WELL, fill_opacity=1) for _ in range(n)))
        cells.arrange(RIGHT, buff=0.1).move_to([0, 0.6, 0])
        self.play(Create(cells), run_time=0.5)
        groups = [cells[i:i + B] for i in range(0, n, B)]
        for k, g in enumerate(groups):
            rect = Rectangle(width=g.width + 0.12, height=0.72, stroke_color=ACCENT, stroke_width=1.6).move_to(g)
            self.play(Create(rect), *[c.animate.set_fill("#1E2B1F", 1).set_stroke(STROKE) for c in g],
                      FadeIn(mono(f"block {k}", 15, ACCENT).next_to(rect, DOWN, buff=0.1)), run_time=0.35)
        tag = mono(f"B = sqrt({n}) = {round(n ** 0.5)}, N/B = {n // B} blocks", 19, ACCENT).move_to([0, -1.4, 0])
        self.play(FadeIn(tag), run_time=0.4)
        self.play(FadeIn(mono("O(1) per block, O(sqrt N) query", 19, MUTED).move_to([0, -1.9, 0])), run_time=0.4)

    def mo_order(self, beats):
        qs = [("q0", "0,3"), ("q1", "9,2"), ("q2", "4,7"), ("q3", "1,5"), ("q4", "8,8")]
        self.play(FadeIn(mono("queries (L, R)", 19, MUTED).move_to([-4.4, 1.0, 0])), run_time=0.2)
        chips = VGroup(*(self.pyfloat(mono(r, 18)) for _, r in qs))
        chips.arrange(RIGHT, buff=0.3).move_to([-0.6, 1.0, 0])
        self.play(LaggedStart(*(FadeIn(c) for c in chips), lag_ratio=0.1), run_time=0.6)
        block = self.array([str(i // 3) for i in range(len(qs))], size=16, side=0.62, y=-0.1, idx=False)
        block.cells.arrange(RIGHT, buff=0.3, center=False).next_to(chips, DOWN, buff=0.8)
        self.play(FadeIn(block), run_time=0.3)
        self.play(FadeIn(mono("L // B: one block per query", 17, MUTED).next_to(block.cells, LEFT, buff=0.4)), run_time=0.3)
        order = VGroup(*(mono(r, 20, ACCENT) for r in ["0,3", "1,5", "4,7", "9,2", "8,8"]))
        order.arrange(RIGHT, buff=0.8).move_to([-0.6, -1.15, 0])
        self.play(FadeIn(order), FadeIn(mono("wiggle even: R ascending, odd: descending", 19, ACCENT).move_to([0, -1.9, 0])), run_time=0.55)

    def mo_heavy(self, beats):
        freqs = [1, 5, 2, 6, 1, 4]
        limit = 1
        tape = self.array([str(f) for f in freqs], size=24, caption=mono("threshold sqrt(M) = 1", 19, MUTED))
        self.dismiss(tape.caption)
        self.play(FadeIn(tape), run_time=0.4)
        for i, f in enumerate(freqs):
            if f > limit:
                self.play(tape.cells[i].animate.set_stroke(ACCENT, 2.4), run_time=0.15)
            else:
                self.play(tape.cells[i].animate.set_stroke(BAD, 1.6).set_opacity(0.6), run_time=0.1)
        self.play(Indicate(tape.cells[1:2], color=ACCENT), run_time=0.35)
        self.play(FadeIn(mono("3 heavy items touched on query", 19, ACCENT).move_to([0, FOOT_Y, 0])), run_time=0.4)

    def nim_terminal(self, beats):
        p = self.pyfloat(mono("P", 26))
        p.move_to([0, 1.0, 0])
        self.play(FadeIn(p), run_time=0.3)
        kids = VGroup(*(self.pyfloat(mono("N", 24)) for _ in range(2)))
        kids.arrange(RIGHT, buff=0.9).move_to([0, 0.0, 0])
        lines = VGroup(arrow([-0.55, 0.6, 0], kids[0].get_top(), MUTED, 2), arrow([0.55, 0.6, 0], kids[1].get_top(), MUTED, 2))
        self.play(Create(lines), LaggedStart(*(FadeIn(k) for k in kids), lag_ratio=0.15), run_time=0.55)
        term = VGroup(*(self.pyfloat(mono("P", 22)).move_to(k.get_center() + DOWN * 1.0) for k in kids))
        self.play(*[Create(arrow(k.get_bottom(), t.get_top(), MUTED, 2)) for k, t in zip(kids, term)],
                  LaggedStart(*(FadeIn(t) for t in term), lag_ratio=0.15), run_time=0.6)
        self.play(FadeIn(mono("can reach P: N     all reach N: P", 18, ACCENT).move_to([0, -1.6, 0])), run_time=0.45)

    def nim_caps(self, beats):
        caps = VGroup(*(self.pyfloat(mono(str(v), 24)) for v in [5, 3, 7]))
        caps.arrange(RIGHT, buff=0.35).move_to([0, 0.7, 0])
        cap = mono("cap", 15, MUTED)
        self.play(LaggedStart(*(FadeIn(c) for c in caps), lag_ratio=0.1), run_time=0.5)
        total = mono("5 ^ 3 ^ 7 = 1 (not 0)", 20, ACCENT).move_to([0, -0.2, 0])
        self.play(FadeIn(total), run_time=0.4)
        self.play(Indicate(caps[2], color=ACCENT, scale_factor=1.15), run_time=0.4)
        self.play(Transform(total, mono("reduce pile 7 to 7 ^ 1 = 6", 20, ACCENT).move_to([0, -0.2, 0])),
                  Transform(caps[2][1], mono("6", 24, ACCENT).move_to(caps[2])), run_time=0.5)
        self.play(FadeIn(mono("5 ^ 3 ^ 6 = 0: P for the opponent", 19, ACCENT).move_to([0, -1.1, 0])), run_time=0.45)

    def bob(self, title, message):
        head = mono(title, 22, PAPER).move_to([0, 0.9, 0])
        body = self.wrap_para(message).move_to([0, 0.05, 0])
        self.play(FadeIn(head, shift=DOWN * 0.1), run_time=0.3)
        self.play(LaggedStart(*(FadeIn(b, shift=RIGHT * 0.1) for b in body), lag_ratio=0.12), run_time=0.7)
        odd = [i for i, c in enumerate(body.text if False else "") if False]
        return body

    def beam(self, rows):
        smoke = Polygon if False else None

    def seg_merge(self, beats):
        ops = ["sum", "min", "max", "gcd", "xor", "matrix"]
        cells = VGroup(*(cell(o, 19, 1.05) for o in ops))
        cells.arrange(RIGHT, buff=0.14).move_to([0, 0.75, 0])
        self.play(LaggedStart(*(FadeIn(c, scale=0.8) for c in cells), lag_ratio=0.1), run_time=0.7)
        self.play(*[c[0].animate.set_stroke(ACCENT, 2) for c in cells], run_time=0.4)
        self.play(FadeIn(mono("identity: 0, +inf, -inf, 0, 0", 19, PAPER).move_to([0, -0.2, 0])), run_time=0.4)
        b = self.bracket(cells, ACCENT, pad=0.2, over=0.05)
        self.play(Create(b), run_time=0.4)
        self.play(FadeIn(mono("any associative merge, not subtraction", 19, ACCENT).move_to([0, -1.1, 0])), run_time=0.45)
        self.play(FadeIn(mono("lazy add / assign for ranges", 19, MUTED).move_to([0, -1.6, 0])), run_time=0.4)

    def mstack_nge(self, beats):
        arr = [4, 1, 3, 2, 5]
        tape = self.array([str(v) for v in arr], caption=mono("next greater, else -1", 19, MUTED))
        self.play(FadeIn(tape), run_time=0.4)
        self.play(FadeIn(mono("decreasing stack of unresolved", 19, MUTED).move_to([0, -1.1, 0])), run_time=0.3)
        out = self.array([""] * 5, size=22, side=0.6, y=-1.75, idx=False)
        self.play(FadeIn(out), run_time=0.25)
        for i, v in enumerate([5, 3, 5, 5, -1]):
            self.play(Indicate(tape.cells[i], color=ACCENT, scale_factor=1.15), run_time=0.2)
            self.play(FadeIn(mono(str(v), 20, ACCENT if v > 0 else BAD).move_to(out.cells[i])), run_time=0.15)
        self.play(FadeIn(mono("resolved indices pop once", 19, ACCENT).move_to([0, -2.35, 0])), run_time=0.4)

    def os_missing(self, beats):
        left = VGroup(*(mono(s, 20, BAD) for s in ["std::set", "TreeMap", "lower_bound"]))
        left.arrange(DOWN, buff=0.16, aligned_edge=LEFT).move_to([-1.9, 0.4, 0])
        right = VGroup(*(mono(s, 20, ACCENT) for s in ["bisect.insort", "Fenwick + rank", "sqrt buckets"]))
        right.arrange(DOWN, buff=0.16, aligned_edge=LEFT).move_to([2.4, 0.4, 0])
        self.play(LaggedStart(*(FadeIn(m) for m in left), lag_ratio=0.12), run_time=0.5)
        self.play(LaggedStart(*(FadeIn(m, shift=RIGHT * 0.1) for m in right), lag_ratio=0.15), run_time=0.6)
        arcs = VGroup(*(arrow(a.get_right(), b.get_left(), ACCENT, 2, buff=0.3) for a, b in zip(left[:2], right[1:])))
        self.play(Create(arcs), run_time=0.5)
        self.play(FadeIn(mono("list insert is O(N): emulate a tree", 19, ACCENT).move_to([0, -1.9, 0])), run_time=0.4)

    def os_insert(self, beats):
        tape = self.array(["", "", "", "", ""], size=22, side=0.62, caption=mono("compressed keys 0..N-1", 19, MUTED))
        self.dismiss(tape.caption)
        self.play(FadeIn(tape), run_time=0.3)
        self.play(FadeIn(mono("insert key 3: +1", 19, ACCENT).move_to([0, -0.9, 0])), run_time=0.3)
        self.play(self.grid_value(tape.cells[3], "1"), run_time=0.25)
        self.play(FadeIn(mono("delete key 3: -1", 19, BAD).move_to([0, -1.4, 0])), run_time=0.3)
        self.play(self.grid_value(tape.cells[3], "0", MUTED), run_time=0.25)
        self.play(FadeIn(mono("prefix counts: smaller keys", 19, ACCENT).move_to([0, -1.9, 0])), run_time=0.4)
        self.play(Indicate(tape.cells[:3], color=ACCENT, scale_factor=1.1), run_time=0.4)

    def ordered_set_kth(self, beats):
        tree = self.array(["1", "2", "4", "8", "16", "32"], size=20, side=0.62, caption=mono("bit[idx + step]", 19, MUTED))
        self.dismiss(tree.caption)
        self.play(FadeIn(tree), run_time=0.4)
        idx = self.ptr("idx", ACCENT)
        self.play(FadeIn(idx), run_time=0.2)
        for step, pos in [(32, 5), (16, 4), (2, 2)]:
            self.play(idx.animate.move_to([tree.cells[pos].get_center()[0], -0.55, 0]),
                      Indicate(tree.cells[pos], color=ACCENT, scale_factor=1.2), run_time=0.35)
        self.play(FadeIn(mono("one log walk, no outer bisect", 19, ACCENT).move_to([0, FOOT_Y, 0])), run_time=0.4)

    def knap_sweep(self, beats):
        tape = self.array([str(v) for v in [0, 0, 1, 3, 4, 5, 6, 8]], size=22, side=0.62, caption=mono("capacity W..wt backward", 19, MUTED))
        self.dismiss(tape.caption)
        self.play(FadeIn(tape), run_time=0.4)
        for i in [7, 6, 5, 4]:
            self.play(Create(arrow([tape.cells[i].get_center()[0], 1.0, 0], [tape.cells[i].get_center()[0], 0.75, 0], ACCENT, 2)),
                      tape.cells[i].animate.set_stroke(ACCENT, 2), run_time=0.2)
        self.play(FadeIn(mono("backward reads the previous layer only", 19, ACCENT).move_to([0, FOOT_Y - 0.1, 0])), run_time=0.45)
        self.play(FadeIn(mono("memory: W + 1 slots", 19, MUTED).move_to([0, FOOT_Y - 0.5, 0])), run_time=0.35)

    def knap_forward(self, beats):
        tape = self.array([str(v) for v in [0, 0, 1, 3, 4, 5, 6, 8]], size=22, side=0.62, caption=mono("capacity wt..W forward", 19, MUTED))
        self.dismiss(tape.caption)
        self.play(FadeIn(tape), run_time=0.4)
        for i in [3, 4, 5, 6, 7]:
            self.play(tape.cells[i].animate.set_stroke(ACCENT, 2), run_time=0.15)
        self.play(FadeIn(mono("coin 3 used again in the same pass", 19, ACCENT).move_to([0, FOOT_Y - 0.1, 0])),
                  Indicate(tape.cells[3:6], color=ACCENT, scale_factor=1.08), run_time=0.5)

    def knap_bits(self, beats):
        bits, header = self.bits(0, 8, y=0.6)
        header.shift(RIGHT * 0.2)
        self.play(FadeIn(bits), FadeIn(header), run_time=0.4)
        self.play(FadeIn(mono("bits <<= 3", 19, ACCENT).move_to([0, -0.2, 0])), run_time=0.3)
        shifted = self.bits_row(0b1001000, 8, y=-0.9)
        self.play(TransformFromCopy(bits, shifted), run_time=0.5)
        self.play(FadeIn(mono("reachable sums are set bits: C speed", 19, ACCENT).move_to([0, -1.7, 0])),
                  Indicate(shifted, color=ACCENT, scale_factor=1.08), run_time=0.5)
        self.play(FadeIn(mono("bits = 1 ... bits |= bits << w", 18, MUTED).move_to([0, -2.2, 0])), run_time=0.35)

    def lis_bisect(self, beats):
        tails = self.array(["2", "4", "6", "8"], size=24, side=0.62, caption=mono("tails, x = 5", 19, MUTED))
        self.dismiss(tails.caption)
        self.play(FadeIn(tails), run_time=0.4)
        lo, hi = self.ptr("lo", MUTED), self.ptr("hi", MUTED)
        self.over(lo, tails.cells[0])
        self.over(hi, tails.cells[-1])
        self.play(FadeIn(lo), FadeIn(hi), run_time=0.3)
        self.play(lo.animate.next_to(tails.cells[2], UP, buff=0.1), hi.animate.next_to(tails.cells[2], UP, buff=0.1), run_time=0.45)
        self.play(Indicate(tails.cells[2], color=ACCENT, scale_factor=1.2), self.grid_value(tails.cells[2], "5"), run_time=0.4)
        self.play(FadeIn(mono("first tails[k] >= x replaced", 19, ACCENT).move_to([0, FOOT_Y, 0])), run_time=0.4)
        self.play(FadeIn(mono("append when x extends the run", 19, MUTED).move_to([0, FOOT_Y - 0.4, 0])), run_time=0.35)

    def graph_adj(self, beats):
        rows = ["adj = [[] for _ in range(V)]", "adj[u].append(v)", "adj[v].append(u)  # undirected"]
        code = VGroup(*(mono(s, 19, PAPER if i else ACCENT) for i, s in enumerate(rows)))
        fitw(code, 7.0)
        code.arrange(DOWN, buff=0.16, aligned_edge=LEFT).move_to([-3.0, 0.5, 0])
        self.play(Write(code), run_time=0.6)
        g = self.graph([(0, 1), (0, 2), (2, 3)], POS_GRAPH[:4], directed=True, weighted=False)
        self.play(FadeIn(mono("O(V + E) memory", 19, ACCENT).move_to([0, FOOT_Y, 0])), run_time=0.4)
        self.play(Indicate(g.node_layer, color=ACCENT, scale_factor=1.04), run_time=0.5)

    def euler_ring(self, beats):
        tree = self.tree(LEAF_TREE)
        rings = VGroup(*(Circle(radius=0.4 + 0.13 * k, color=ACCENT, stroke_width=1.4,
                                stroke_opacity=0.9 - 0.15 * k).move_to(tree[1]) for k in range(4)))
        self.play(LaggedStart(*(Create(r) for r in rings), lag_ratio=0.15), run_time=0.9)
        self.play(FadeIn(mono("entry and exit: 2N entries", 19, ACCENT).move_to([0, FOOT_Y, 0])), run_time=0.4)

    def tin_tout(self, beats):
        tape = self.array(["-", "1", "2", "4", "5", "3", "6", "-"], size=18, side=0.56, caption=None)
        tidy = self.array(["-", "1", "4", "2", "3", "6", "7", "-"], size=18, side=0.56, y=-0.75, caption=None, idx=False)
        self.play(FadeIn(tape), run_time=0.3)
        self.play(FadeIn(mono("tin", 16, MUTED).move_to([-4.3, 0.35, 0])), FadeIn(tidy),
                  FadeIn(mono("tout", 16, ACCENT).move_to([-4.3, -0.75, 0])), run_time=0.45)
        span = self.box_at(tape.cells, 1, 5, ACCENT, y=tape.cells.get_center()[1])
        self.play(Create(span), run_time=0.35)
        self.play(FadeIn(mono("Fenwick range [tin[u], tout[u]]", 19, ACCENT).move_to([0, FOOT_Y, 0])), run_time=0.45)

    def modmul(self, beats):
        self.play(FadeIn(self.row_series(["123456 * 654321", "% 1000000007"], "one addition at a time", y=1.0)), run_time=0.4)
        cells = VGroup(*(cell(b, 20, 0.55) for b in "1011"))
        cells.arrange(RIGHT, buff=0.1).move_to([0, 0.1, 0])
        self.play(FadeIn(cells), run_time=0.3)
        self.play(FadeIn(mono("exp bits 1011: res = res^2 * base", 19, ACCENT).move_to([0, -0.7, 0])), run_time=0.4)
        for i in range(4):
            self.play(cells[i][0].animate.set_stroke(ACCENT, 2), run_time=0.15)
        self.play(Write(self.math("pow(2, 13, 997)", ACCENT, 28).move_to([0, -1.5, 0])), run_time=0.4)
        self.play(FadeIn(mono("O(log exp) squarings", 19, MUTED).move_to([0, -2.1, 0])), run_time=0.35)

    def modexp(self, beats):
        cells, header = self.bits(13, 4, y=1.0)
        self.play(FadeIn(cells), FadeIn(header), run_time=0.4)
        self.play(Write(self.math("r = r \\cdot r \\bmod p", ACCENT, 24).move_to([0, 0.1, 0])), run_time=0.4)
        for i in (1, 3):
            self.play(Indicate(cells[i], color=ACCENT, scale_factor=1.3), cells[i][0].animate.set_stroke(ACCENT, 2), run_time=0.3)
        self.play(FadeIn(mono("Fermat inverse: pow(b, p-2, p)", 19, ACCENT).move_to([0, -1.0, 0])), run_time=0.4)
        self.play(FadeIn(mono("pow(base, exp, MOD)", 19, PAPER).move_to([0, -1.5, 0])), run_time=0.35)

    def factorials(self, beats):
        fact = self.array([str(v) for v in [1, 1, 2, 6, 24, 120]], size=18, side=0.62, y=-0.1, caption=mono("fact[i] = i * fact[i-1]", 18, MUTED))
        self.dismiss(fact.caption)
        inv = self.array(["", "", "", "", "", ""], size=18, side=0.62, y=0.75, caption=mono("inv_fact[i] = inv_fact[i+1] * (i+1)", 18, MUTED))
        self.dismiss(inv.caption)
        self.play(FadeIn(fact), run_time=0.35)
        self.play(FadeIn(mono("forward", 17, ACCENT).move_to([-4.4, -0.35, 0])), run_time=0.2)
        for i in range(1, 6):
            self.play(fact.cells[i][0].animate.set_stroke(ACCENT, 1.4), run_time=0.08)
        self.play(FadeIn(inv), FadeIn(mono("backward", 17, BAD).move_to([-4.4, 0.8, 0])), run_time=0.3)
        top = self.pyfloat(mono("inv(fact[5]) then * i", 17, PAPER)).move_to([3.2, 0.75, 0])
        self.play(FadeIn(top), run_time=0.3)
        for i in range(5, 0, -1):
            self.play(inv.cells[i][0].animate.set_stroke(BAD, 1.4), run_time=0.08)
        self.play(FadeIn(mono("nCr = fact[n] * inv_fact[r] * inv_fact[n-r]", 18, ACCENT).move_to([0, -1.25, 0])), run_time=0.45)

    def stars(self, beats):
        bins = VGroup(*(cell(str(k), 20, 0.66) for k in range(1, 4)))
        bins.arrange(RIGHT, buff=0.3).move_to([0, 0.95, 0])
        self.play(FadeIn(bins), run_time=0.35)
        stars = self.array(["x"] * 5, size=20, side=0.5, y=0.0, caption=mono("5 identical stars, 3 bins", 18, MUTED))
        self.dismiss(stars.caption)
        self.play(FadeIn(stars), run_time=0.3)
        sep = VGroup(mono("|", 24, ACCENT), mono("|", 24, ACCENT))
        sep[0].next_to(stars.cells[1], RIGHT, buff=0.34)
        sep[1].next_to(stars.cells[3], RIGHT, buff=0.34)
        self.play(FadeIn(sep), run_time=0.4)
        self.play(Write(self.math("C(n + k - 1,\\ k - 1) = C(7, 2)", ACCENT, 26).move_to([0, -0.95, 0])), run_time=0.4)
        self.play(FadeIn(mono("inclusion-exclusion alternates signs", 19, MUTED).move_to([0, -1.75, 0])), run_time=0.4)

    def bit_ops(self, beats):
        bits, header = self.bits(0b1010, 4, y=0.8)
        self.play(FadeIn(bits), FadeIn(header), run_time=0.4)
        ops = VGroup(mono("(x >> k) & 1", 19, PAPER), mono("x | (1 << k)", 19, ACCENT), mono("x ^ (1 << k)", 19, PAPER))
        ops.arrange(DOWN, buff=0.14, aligned_edge=LEFT).move_to([-0.4, -0.45, 0])
        self.play(LaggedStart(*(FadeIn(o, shift=RIGHT * 0.1) for o in ops), lag_ratio=0.15), run_time=0.6)
        self.play(Indicate(bits[1], color=ACCENT, scale_factor=1.3), run_time=0.4)
        flip = self.bits_row(0b1110, 4, y=-1.4)
        self.play(TransformFromCopy(bits, flip), run_time=0.5)
        self.play(Indicate(flip[1], color=ACCENT, scale_factor=1.3), run_time=0.35)
        self.play(FadeIn(mono("bit_count() and bit_length() too", 19, MUTED).move_to([0, FOOT_Y, 0])), run_time=0.4)





def boxes_at(mob):
    return mob.get_right()[0] + 0.25


FAMILIES = {
    "PythonGuide": ["challenge", "bitmask_states", "grid_paths", "linked_list"],
    "ContestGuide": ["catalog", "check_panel", "bubble", "topo_dp"],
    "FastIoGuide": ["bubble", "grid_roll", "dijkstra_tour", "check_panel"],
    "PrefixSumsGuide": ["prefix", "difference", "grid_paths", "two_pointers"],
    "BinarySearchGuide": ["binary_search", "lo_hi", "kmp_matches", "real_search"],
    "TernarySearchGuide": ["ternary", "ternary_discard", "ternary_shrink", "ternary_int"],
    "TwoPointersGuide": ["two_pointers", "bubble", "sliding_window", "merge_two"],
    "SlidingWindowGuide": ["sliding_window", "sweep_window", "shrink_window", "count_sub"],
    "SortingGuide": ["bubble", "custom_key", "intervals", "compress"],
    "GreedyGuide": ["greedy_commit", "intervals", "exchange", "regret_heap"],
    "DsuGuide": ["dsu_union", "compress", "prim_small", "parent_array"],
    "FenwickGuide": ["fenwick", "fenwick_update", "int_bits", "inversions"],
    "SegmentTreeGuide": ["seg_tree", "seg_update", "seg_fold", "seg_merge"],
    "MonotonicGuide": ["mstack", "mstack_nge", "deque", "histogram"],
    "OrderedSetGuide": ["os_missing", "os_insert", "ordered_set_kth", "skip_tour"],
    "KnapsackGuide": ["knapsack", "knap_sweep", "knap_forward", "knap_bits"],
    "GridDpGuide": ["grid_paths", "grid_obstacles", "grid_roll", "grid_backtrack"],
    "LisLcsGuide": ["lis", "lis_bisect", "edit_table", "edit_costs"],
    "IntervalDpGuide": ["interval_len", "interval_split", "palindrome", "doubling"],
    "TreeDpGuide": ["tree_dp", "tree_reroot", "distinct_child", "reroot"],
    "BitmaskDpGuide": ["bitmask", "bitmask_states", "bitmask_jump", "submasks"],
    "GraphTraversalGuide": ["graph_adj", "bfs", "two_color", "multi_bfs"],
    "TopoSortGuide": ["kahns", "heap_topo", "topo_dp", "check_panel"],
    "DijkstraGuide": ["dijkstra_tour", "stale", "dijkstra_relax", "layered_dijkstra"],
    "BellmanFloydGuide": ["bellman", "negcycle", "floyd", "closure"],
    "MstGuide": ["tree_bars", "mst", "mst_prim", "panel"],
    "BridgesGuide": ["bridges", "bridges", "articulation", "condense"],
    "EulerTourGuide": ["euler_tin", "tin_tout", "diameter", "centroid"],
    "LcaGuide": ["lca_table", "lca_lift", "lca_lockstep", "lca_dist"],
    "GcdGuide": ["euclid", "bezout", "modinv", "crt"],
    "SieveGuide": ["sieve", "sieve_spf", "primes", "segmented"],
    "ModCombGuide": ["modmul", "modexp", "factorials", "stars"],
    "BitwiseGuide": ["bit_ops", "binary", "xor_pairs", "max_subset"],
    "RollingHashGuide": ["hash_panel", "substr_hash", "double_hash", "lcp_panel"],
    "KmpGuide": ["kmp_borders", "kmp_fallback", "kmp_matches", "kmp_period"],
    "ZAlgoGuide": ["z_compute", "zbox", "rz", "borders_z"],
    "TrieGuide": ["trie", "trie_passes", "bit_trie", "bit_trie"],
    "ConstructiveGuide": ["check_bounds", "zigzag", "powers", "call_panel"],
    "MoSqrtGuide": ["blocks", "mo_order", "distinct_child", "mo_heavy"],
    "NimGuide": ["nim_terminal", "xor_pairs", "xor_cancel", "nim_caps"],
    "CatalogGuide": ["catalog", "bubble", "check_panel", "challenge"],
}


def _generic(self, index, beats, *args):
    names = FAMILIES.get(type(self).__name__, [])
    stage = getattr(self, "_stage", 0)
    fn = getattr(self, names[index]) if index < len(names) else None
    if fn is None:
        return self.fallback(value=beats[index] if index < len(beats) else beats)
    head = index == 0
    try:
        self._stage = stage
        return fn(beats)
    except Exception:
        self.play(*[FadeOut(m) for m in self.beat_mobjects(stage)])
        return self.fallback(value=beats[index] if index < len(beats) else beats)


LAYOUTS = {
    "left": (-4.0, 3.9, 7.9),
    "center": (0.0, 3.9, 8.6),
    "lower": (0.0, 2.5, 10.4),
}


def layout(self, index, head):
    start = getattr(self, "_stage", 0)
    beat = Group(*self.beat_mobjects(start))
    if not len(beat):
        return
    if head:
        # The title strip and progress bar own the top of the frame, so a head
        # beat that reaches into them is re-seated below the bar, not squeezed
        # into the leftover strip. It appears in the designed slot first.
        if beat.get_top()[1] > 2.62:
            beat.shift(DOWN * (beat.get_top()[1] - 2.58))
        if beat.get_bottom()[1] < -3.52:
            beat.shift(UP * (-3.52 - beat.get_bottom()[1]))
        if beat.width > 12.4:
            beat.scale(12.4 / beat.width)
        self.wait(0.3)
        return
    spot, tall, wide = LAYOUTS["left" if index % 2 else "lower"]
    fit = min(1.0, tall / beat.height, wide / beat.width)
    if fit < 1.0:
        beat.scale(fit)
    beat.move_to([spot, 0, 0])
    self.wait(0.3)


Guide.layout = layout


for _scene_name in LESSONS:
    globals()[_scene_name] = type(_scene_name, (Guider, IndexFamily, GridFamily), {"draw": _generic})
