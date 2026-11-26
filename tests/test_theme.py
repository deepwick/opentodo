import json
import re
import sys
from pathlib import Path

import pytest

from deepwick_spec.check_port import check_port
from deepwick_spec.color import contrast_ratio
from deepwick_spec.palette import load_palette

REPO = Path(__file__).resolve().parents[1]
PALETTE = load_palette()
C = {name: value.lower() for name, value in PALETTE.colors.items()}
sys.path.insert(0, str(REPO))
FILE = REPO / "deepwick.opentodo-theme.json"
HEX = re.compile(r"#[0-9a-f]{6}")

# docs/themes.md#tokens, OpenTodo 1.9.0
TOKENS = frozenset(
    "canvas surface raised sunken pop hover selected selected-row sidebar "
    "text-strong text muted faint border border-soft border-input line-strong "
    "accent accent-hover on-accent accent-text accent-soft accent-soft-text focus "
    "success success-soft success-soft-text warning warning-soft warning-soft-text "
    "danger danger-soft danger-soft-text info info-soft info-soft-text "
    "p1 p1-soft p2 p2-soft p3 p3-soft p4 p4-soft "
    "hue-red hue-orange hue-yellow hue-lime hue-green hue-teal hue-cyan hue-blue "
    "hue-indigo hue-violet hue-pink hue-slate "
    "scrim highlight highlight-text chart-base chart-seq-1 chart-seq-2 chart-seq-3 chart-seq-4 chart-seq-5".split()
)
SEEDS = frozenset({"canvas", "surface", "text", "accent", "success", "warning", "danger", "info"})


def load():
    return json.loads(FILE.read_text(encoding="utf-8"))


def colors(theme):
    return {**theme["seeds"], **theme["tokens"]}


def test_top_level_keys():
    assert set(load()) == {
        "$schema", "opentodoTheme", "id", "name", "author", "licence", "source", "kind", "seeds", "tokens", "bar", "notes"
    }
    assert set(load()["notes"]) == {"text"}


def test_required_keys_and_limits():
    t = load()
    assert t["opentodoTheme"] == 1
    assert re.fullmatch(r"[a-z0-9-]{1,64}", t["id"])
    assert 1 <= len(t["name"]) <= 60 and t["name"].strip()
    assert len(t["author"]) <= 120 and len(t["licence"]) <= 120
    assert len(t["source"]) <= 300
    assert t["kind"] == "dark"
    assert len(t["notes"]["text"]) <= 500
    assert FILE.stat().st_size <= 16 * 1024


def test_keys_are_known():
    t = load()
    assert set(t["seeds"]) <= SEEDS
    assert {"canvas", "surface", "text", "accent"} <= set(t["seeds"])
    assert set(t["tokens"]) <= TOKENS


def test_every_color_is_a_palette_color():
    t = load()
    values = [*colors(t).values(), t["bar"]]
    palette = set(C.values())
    for v in values:
        assert HEX.fullmatch(v), v
        assert v in palette, v


def test_seeds_map_to_palette():
    s = load()["seeds"]
    assert (s["canvas"], s["surface"], s["text"], s["accent"]) == (
        C["background"], C["surface"], C["foreground"], C["blue"]
    )


def test_status_seeds_follow_palette_ui_roles():
    s = load()["seeds"]
    ui = PALETTE.ui
    for seed, role in (("success", "success"), ("warning", "warning"), ("danger", "error"), ("info", "info")):
        assert s[seed] == C[ui[role]], seed


def test_highlight_differs_from_selected():
    t = load()["tokens"]
    assert t["highlight"] != t["selected"]


def test_twelve_labels_minus_indigo_and_violet():
    t = load()["tokens"]
    labels = {k for k in t if k.startswith("hue-")}
    assert labels == {k for k in TOKENS if k.startswith("hue-")} - {"hue-indigo", "hue-violet"}


# OpenTodo's contrast pairs (web/src/ui/tokens/pairs.ts) where both colors are set in the file.
PAIRS = (
    [(fg, bg, 4.5) for fg in ("text-strong", "text") for bg in ("canvas", "surface", "sidebar", "selected")]
    + [(fg, bg, 4.5) for fg in ("accent-text", "success", "warning", "danger", "info") for bg in ("canvas", "surface")]
    + [("border-input", bg, 3) for bg in ("canvas", "surface")]
    + [(p, bg, 3) for p in ("p1", "p2", "p3", "p4") for bg in ("canvas", "surface")]
    + [("accent-text", "sidebar", 3)]
    + [(h, bg, 3) for h in sorted({k for k in TOKENS if k.startswith("hue-")} - {"hue-indigo", "hue-violet"})
       for bg in ("canvas", "surface")]
)


@pytest.mark.parametrize("fg,bg,minimum", PAIRS, ids=[f"{f}-on-{b}" for f, b, _ in PAIRS])
def test_contrast(fg, bg, minimum):
    c = colors(load())
    assert contrast_ratio(c[fg], c[bg]) >= minimum


def test_committed_file_matches_generator():
    import generate

    assert FILE.read_text(encoding="utf-8") == generate.render(PALETTE)


def test_port_conventions():
    assert check_port(REPO, PALETTE.allowed_hex()) == []
