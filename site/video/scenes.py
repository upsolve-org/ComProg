"""Render with Manim Community 0.22. AUDIO_DIR holds the Gemini WAV clips."""
import json
import os
import re
import wave
from pathlib import Path

from manim import (
    Arrow, Circle, Create, DOWN, FadeIn, FadeOut, Indicate, LaggedStart,
    LEFT, Line, Rectangle, RIGHT, RoundedRectangle, Scene, Square, Text,
    TransformFromCopy, UP, VGroup, config, smooth,
)

ROOT = Path(__file__).resolve().parent
LESSONS = json.loads((ROOT / "lessons.json").read_text(encoding="utf-8-sig"))
ACCENT = "#46C94C"
ACCENT_DARK = "#157A1A"
PAPER = "#F2F2EF"
MUTED = "#A1A1AA"
WELL = "#141414"
CARD = "#262626"
STROKE = "#3A3A3A"
config.background_color = "#171717"


def label(value, size=28, color=PAPER):
    return Text(str(value), font="Segoe UI", font_size=size, color=color)


def mono(value, size=24, color=ACCENT):
    return Text(str(value), font="Consolas", font_size=size, color=color)


def tile(value, accent=False, width_min=2.5, height=1.1):
    text = label(value, 25, PAPER)
    border = ACCENT if accent else STROKE
    fill = "#1E2B1F" if accent else CARD
    shape = RoundedRectangle(
        width=max(width_min, text.width + 0.65),
        height=height,
        corner_radius=0.06,
        stroke_color=border,
        stroke_width=2.2 if accent else 1.5,
        fill_color=fill,
        fill_opacity=1,
    )
    return VGroup(shape, text)


def badge(step_num, text_val):
    tag = mono(f"0{step_num}", 20, ACCENT)
    tag_box = Rectangle(
        width=0.68, height=0.44,
        stroke_color=ACCENT, stroke_width=1.5,
        fill_color="#152216", fill_opacity=1,
    )
    tag_group = VGroup(tag_box, tag)
    txt = label(text_val, 24, PAPER)
    body = Rectangle(
        width=max(3.2, txt.width + 0.7), height=0.88,
        stroke_color=STROKE, stroke_width=1.5,
        fill_color=CARD, fill_opacity=1,
    )
    txt.move_to(body.get_center())
    tag_group.next_to(body, UP, buff=0.06).align_to(body, LEFT)
    return VGroup(body, txt, tag_group)


def stamp(seconds):
    ms = round(seconds * 1000)
    return f"{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02}.{ms % 1000:03}"


class Guide(Scene):
    def diagram(self, index, labels):
        name = type(self).__name__
        items = list(labels)[:3]
        while len(items) < 3:
            items.append("")

        if name == "PythonGuide":
            if index == 0:
                source, left, right = (tile(v, accent=(i == 2)) for i, v in enumerate(items))
                source.shift(UP * 0.85)
                left.shift(LEFT * 2.8 + DOWN * 0.95)
                right.shift(RIGHT * 2.8 + DOWN * 0.95)
                arrows = VGroup(*(
                    Arrow(source.get_bottom(), dest.get_top(), buff=0.1, color=ACCENT, stroke_width=3)
                    for dest in (left, right)
                ))
                self.play(FadeIn(source, shift=DOWN * 0.2), rate_func=smooth, run_time=0.55)
                self.play(
                    Create(arrows, rate_func=smooth),
                    FadeIn(left, shift=UP * 0.2),
                    FadeIn(right, shift=UP * 0.2),
                    run_time=0.75,
                )
                self.play(Indicate(right, color=ACCENT, scale_factor=1.05), run_time=0.5)
                return
            if index == 1:
                data = tile("3     7     9", accent=True).shift(UP * 0.95)
                tokens = VGroup(*(tile(v, width_min=1.6) for v in ["3", "7", "9"])).arrange(RIGHT, buff=0.45).shift(DOWN * 0.95)
                rays = VGroup(*(Arrow(data.get_bottom(), t.get_top(), buff=0.1, color=ACCENT) for t in tokens))
                self.play(FadeIn(data, shift=DOWN * 0.2), run_time=0.5)
                self.play(
                    LaggedStart(*(TransformFromCopy(data, t) for t in tokens), lag_ratio=0.18),
                    Create(rays),
                    run_time=0.85,
                )
                return
            if index == 2:
                grid = VGroup(*(Square(0.26, stroke_width=1.2, color=ACCENT) for _ in range(100)))
                grid.arrange_in_grid(rows=10, cols=10, buff=0.03).shift(LEFT * 2.7 + DOWN * 0.2)
                summary = tile("1000 × 1000 = 1,000,000 visits", accent=True).shift(RIGHT * 2.3 + DOWN * 0.2)
                self.play(Create(grid), run_time=0.75)
                self.play(grid[:20].animate.set_fill(ACCENT, opacity=0.75), run_time=0.5)
                self.play(FadeIn(summary, shift=LEFT * 0.25), run_time=0.55)
                return
            cells = VGroup(*(tile(v, accent=(i == 1), width_min=1.9) for i, v in enumerate(["A", "B", "C"]))).arrange(RIGHT, buff=0.35)
            self.play(FadeIn(cells, shift=UP * 0.15), run_time=0.5)
            self.play(FadeOut(cells[0], shift=LEFT * 0.8), Indicate(cells[1], color=ACCENT), run_time=0.65)
            self.play(FadeIn(mono("deque.popleft() -> O(1)", 24, ACCENT).next_to(cells[1], DOWN, buff=0.35)), run_time=0.45)
            return

        variant = (sum(map(ord, name)) + index) % 4

        if variant == 0:
            # Horizontal pipeline with step badges and active pulse
            cards = VGroup(*(badge(i + 1, v) for i, v in enumerate(items))).arrange(RIGHT, buff=0.75)
            if cards.width > 12.2:
                cards.scale_to_fit_width(12.2)
            cards.shift(DOWN * 0.25)
            self.play(FadeIn(cards[0], shift=RIGHT * 0.25), rate_func=smooth, run_time=0.45)
            for a, b in zip(cards, list(cards)[1:]):
                arr = Arrow(a[0].get_right(), b[0].get_left(), buff=0.08, color=ACCENT, stroke_width=3)
                self.play(Create(arr), FadeIn(b, shift=RIGHT * 0.2), rate_func=smooth, run_time=0.55)
            self.play(Indicate(cards[-1][0], color=ACCENT, scale_factor=1.04), run_time=0.45)
            return

        if variant == 1:
            # Top hub branching to two comparison pillars with cross-link
            top = tile(items[0], accent=True, width_min=3.4).shift(UP * 0.85)
            left = tile(items[1], width_min=3.1).shift(LEFT * 3.0 + DOWN * 1.0)
            right = tile(items[2], accent=True, width_min=3.1).shift(RIGHT * 3.0 + DOWN * 1.0)
            for mob in (top, left, right):
                if mob.width > 5.4:
                    mob.scale_to_fit_width(5.4)
            a1 = Arrow(top.get_bottom(), left.get_top(), buff=0.1, color=MUTED, stroke_width=2.5)
            a2 = Arrow(top.get_bottom(), right.get_top(), buff=0.1, color=ACCENT, stroke_width=3)
            bridge = Arrow(left.get_right(), right.get_left(), buff=0.12, color=ACCENT, stroke_width=2.5)
            self.play(FadeIn(top, shift=DOWN * 0.2), rate_func=smooth, run_time=0.45)
            self.play(Create(a1), FadeIn(left, shift=UP * 0.2), Create(a2), FadeIn(right, shift=UP * 0.2), run_time=0.65)
            self.play(Create(bridge), Indicate(right, color=ACCENT, scale_factor=1.04), run_time=0.55)
            return

        if variant == 2:
            # Array / window tape on top with 3 animated inspection cards below
            tape = VGroup(*(
                Square(0.58, stroke_color=ACCENT if i in (2, 3, 4) else STROKE,
                       stroke_width=2.2 if i in (2, 3, 4) else 1.2,
                       fill_color="#1D2D1E" if i in (2, 3, 4) else WELL, fill_opacity=1)
                for i in range(8)
            )).arrange(RIGHT, buff=0.08).shift(UP * 1.0)
            indices = VGroup(*(mono(str(i), 18, ACCENT if i in (2, 3, 4) else MUTED).move_to(tape[i]) for i in range(8)))
            row = VGroup(*(tile(v, accent=(i == 1), width_min=2.8) for i, v in enumerate(items))).arrange(RIGHT, buff=0.45)
            if row.width > 12.2:
                row.scale_to_fit_width(12.2)
            row.shift(DOWN * 0.85)
            self.play(FadeIn(tape, shift=DOWN * 0.15), FadeIn(indices), run_time=0.45)
            self.play(LaggedStart(*(FadeIn(c, shift=UP * 0.2) for c in row), lag_ratio=0.2), run_time=0.75)
            self.play(Indicate(tape[2:5], color=ACCENT, scale_factor=1.06), Indicate(row[1], color=ACCENT), run_time=0.5)
            return

        # Variant 3: Layered vertical stack with right-hand accent callout
        stack = VGroup(*(tile(v, accent=(i == 2), width_min=4.2, height=0.92) for i, v in enumerate(items))).arrange(DOWN, buff=0.32)
        if stack.width > 8.5:
            stack.scale_to_fit_width(8.5)
        stack.shift(DOWN * 0.2)
        rail = Line(stack.get_top() + LEFT * (stack.width / 2 + 0.35),
                    stack.get_bottom() + LEFT * (stack.width / 2 + 0.35),
                    color=ACCENT, stroke_width=4)
        self.play(Create(rail), FadeIn(stack[0], shift=RIGHT * 0.2), run_time=0.45)
        self.play(FadeIn(stack[1], shift=RIGHT * 0.2), run_time=0.4)
        self.play(FadeIn(stack[2], shift=RIGHT * 0.2), Indicate(stack[2], color=ACCENT, scale_factor=1.03), run_time=0.55)

    def construct(self):
        name = type(self).__name__
        cues = ["WEBVTT", ""]
        for index, (title, values, narration) in enumerate(LESSONS[name]):
            wav = Path(os.environ["AUDIO_DIR"]) / f"{name}{index}.wav"
            with wave.open(str(wav)) as clip:
                duration = clip.getnframes() / clip.getframerate()
            start = self.time
            self.add_sound(str(wav))
            bar = Line(LEFT * 6.1, RIGHT * 6.1, color=STROKE, stroke_width=1.2).to_edge(UP, buff=1.18)
            tag = mono(f"STEP 0{index + 1} // {name.upper()}", 16, ACCENT).to_edge(UP, buff=0.28).to_edge(LEFT, buff=0.75)
            heading = label(title, 38).next_to(tag, DOWN, buff=0.12).align_to(tag, LEFT)
            if heading.width > 12.2:
                heading.scale_to_fit_width(12.2).align_to(tag, LEFT)
            self.play(FadeIn(tag), FadeIn(heading, shift=DOWN * 0.1), Create(bar), run_time=0.38)
            self.diagram(index, values)
            beat_span = max(8.2, duration, self.time - start + 0.15)
            self.wait(max(0.1, beat_span - (self.time - start)))
            sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", narration.strip()) if s.strip()]
            cursor = start
            total_chars = sum(map(len, sentences))
            for sentence in sentences:
                end = cursor + duration * len(sentence) / total_chars
                cues.extend([f"{stamp(cursor)} --> {stamp(end)}", sentence, ""])
                cursor = end
            self.play(FadeOut(*self.mobjects, shift=UP * 0.08), run_time=0.32)
        (ROOT.parent / "public" / f"{name}.vtt").write_text("\n".join(cues), encoding="utf-8")


for _scene_name in LESSONS:
    globals()[_scene_name] = type(_scene_name, (Guide,), {})
