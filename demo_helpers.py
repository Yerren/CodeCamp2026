"""Shared code for the demo notebooks: the valid applications and probability charts."""

import math

import matplotlib.pyplot as plt

VALID_APPLICATIONS: dict[str, dict] = {
    "maps": {
        "description": "Navigation and location search",
        "actions": {
            "navigate": {
                "destination": "str",
                "mode": "driving | walking | cycling | transit",
            },
            "search_nearby": {"query": "str", "radius_km": "float"},
            "show_traffic": {},
        },
    },
    "music": {
        "description": "Music streaming and playback",
        "actions": {
            "play": {"song": "str", "artist": "str", "playlist": "str"},
            "pause": {},
            "skip": {},
            "set_volume": {"level": "int (0-100)"},
        },
    },
    "messages": {
        "description": "Send and read text messages",
        "actions": {
            "send_message": {"recipient": "str", "body": "str"},
            "read_latest": {"sender": "str"},
        },
    },
    "calendar": {
        "description": "Manage events and reminders",
        "actions": {
            "create_event": {
                "title": "str",
                "date": "YYYY-MM-DD",
                "time": "HH:MM",
                "duration_minutes": "int",
            },
            "list_events": {"date": "YYYY-MM-DD"},
            "set_reminder": {"text": "str", "time": "HH:MM"},
        },
    },
    "weather": {
        "description": "Weather forecasts and conditions",
        "actions": {
            "current_conditions": {"location": "str"},
            "forecast": {"location": "str", "days": "int"},
        },
    },
}


ACCENT = "#2a6fdb"  # the chosen option
MUTED = "#b8c4d6"  # the alternatives
INK = "#333333"


def _draw(ax, title: str, answer, display_names: dict[str, str]) -> None:
    probs = sorted(answer.probabilities.items(), key=lambda kv: kv[1])
    labels = [k for k, _ in probs]
    values = [v for _, v in probs]
    colors = [ACCENT if k == answer.choice else MUTED for k in labels]

    bars = ax.barh(range(len(labels)), values, color=colors, height=0.7)
    ax.set_yticks(range(len(labels)), [display_names.get(k, k) for k in labels])
    ax.set_xlim(0, 1.12)
    ax.set_title(title, loc="left", fontsize=11, color=INK)
    ax.set_xlabel("probability", color=INK)
    ax.grid(axis="x", color="#e5e5e5", linewidth=0.8)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left"):
        ax.spines[side].set_visible(False)
    ax.tick_params(colors=INK, length=0)

    # Label only the chosen option, to keep the chart readable
    chosen = labels.index(answer.choice)
    ax.annotate(
        f"{values[chosen]:.2f}",
        (values[chosen], bars[chosen].get_y() + bars[chosen].get_height() / 2),
        xytext=(4, 0),
        textcoords="offset points",
        va="center",
        color=INK,
        fontweight="bold",
    )


def plot_probabilities(
    answers: dict, cols: int = 2, display_names: dict[str, str] | None = None
) -> None:
    """Plot one horizontal bar chart per answer, e.g. `response.answers`.

    `display_names` optionally maps option names to the labels shown on the chart.
    """
    display_names = display_names or {}
    items = list(answers.items())
    cols = min(cols, len(items))
    rows = math.ceil(len(items) / cols)
    n_bars = max(len(a.probabilities) for _, a in items)
    fig, axes = plt.subplots(
        rows, cols, figsize=(6 * cols, rows * (0.35 * n_bars + 1.2)), squeeze=False
    )
    for ax, (name, answer) in zip(axes.flat, items):
        _draw(ax, name, answer, display_names)
    for ax in list(axes.flat)[len(items) :]:
        ax.axis("off")
    fig.tight_layout()
    plt.show()
