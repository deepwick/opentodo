"""Write deepwick.opentodo-theme.json, the OpenTodo dark theme, from the Deepwick palette.

The mapping follows OpenTodo's MAPPING.md for its built-in palettes. Only
Deepwick colors are written; OpenTodo derives every other token from the seeds
and moves derived tokens until each contrast pair passes.

Run from this directory: PYTHONPATH=../spec python3 generate.py
"""
import json
from pathlib import Path

from deepwick_spec.palette import Palette, load_palette

OUT = Path(__file__).with_name("deepwick.opentodo-theme.json")

SEEDS = {
    "canvas": "background",
    "surface": "surface",
    "text": "foreground",
    "accent": "blue",
    "success": "green",
    "warning": "yellow",
    "danger": "red",
    "info": "cyan",
}

TOKENS = {
    "sidebar": "background",
    "selected": "selection",
    "text-strong": "white",
    "border-input": "muted",
    "accent-text": "blue",
    "p1": "red",
    "p2": "orange",
    "p3": "blue",
    "p4": "comment",
    "hue-red": "red",
    "hue-orange": "orange",
    "hue-yellow": "gold",
    "hue-lime": "mint",
    "hue-green": "green",
    "hue-teal": "teal",
    "hue-cyan": "cyan",
    "hue-blue": "blue",
    "hue-pink": "magenta",
    "hue-slate": "comment",
    "highlight": "gold",
}

NOTES = (
    "Deepwick is an unofficial theme derived from Polywick Blue by Polywick Studio (MIT). "
    "Not affiliated with Polywick Studio. Deepwick has no indigo or violet, "
    "so those label colors are OpenTodo's own."
)


def theme(palette: Palette) -> dict:
    c = {name: value.lower() for name, value in palette.colors.items()}
    return {
        "$schema": "https://raw.githubusercontent.com/OpenTodoApp/OpenTodo/main/docs/themes/opentodo-theme.schema.json",
        "opentodoTheme": 1,
        "id": "deepwick",
        "name": "Deepwick",
        "author": "Deepwick",
        "licence": "MIT",
        "source": "https://github.com/deepwick/opentodo",
        "kind": "dark",
        "seeds": {key: c[role] for key, role in SEEDS.items()},
        "tokens": {key: c[role] for key, role in TOKENS.items()},
        "bar": c["background"],
        "notes": {"text": NOTES},
    }


def render(palette: Palette) -> str:
    return json.dumps(theme(palette), indent=2) + "\n"


if __name__ == "__main__":
    OUT.write_text(render(load_palette()), encoding="utf-8")
    print(f"wrote {OUT.name}")
