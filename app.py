
import base64
import json
import math
import random
import re
from fractions import Fraction
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Polygon
import numpy as np
import streamlit as st
import sympy as sp


st.set_page_config(
    page_title="MathQuest",
    page_icon="➗",
    layout="wide",
    initial_sidebar_state="expanded",
)

APP_DIR = Path(__file__).resolve().parent
LOGO_PATH = APP_DIR / "assets" / "jcu_logo.png"
LOGO_B64 = (
    base64.b64encode(LOGO_PATH.read_bytes()).decode("ascii")
    if LOGO_PATH.is_file() else ""
)

SEED_RNG = random.SystemRandom()
RNG = SEED_RNG
x = sp.symbols("x", real=True)
t = sp.symbols("t", real=True)

st.markdown(
    """
    <style>
      /*
       * Keep MathQuest readable regardless of the Streamlit/browser theme.
       * Previously only the backgrounds were forced to light colours. A user
       * with Streamlit's dark theme therefore received white text on a white
       * page. These variables and selectors make the whole app consistently
       * high contrast.
       */
      :root {
        color-scheme: light;
        --mq-text: #172033;
        --mq-muted: #526174;
        --mq-border: #cbd5e1;
        --mq-sidebar: #eef1f5;
        --mq-white: #ffffff;
        --mq-accent: #c8102e;
      }

      html, body, [data-testid="stAppViewContainer"], .stApp {
        background:#ffffff !important;
        color:var(--mq-text) !important;
      }

      /* Native Streamlit text, Markdown and KaTeX inherit the same dark text. */
      .stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5,
      .stApp h6, .stApp p, .stApp li, .stApp label,
      .stApp [data-testid="stMarkdownContainer"],
      .stApp [data-testid="stCaptionContainer"],
      .stApp [data-testid="stText"],
      .stApp .katex, .stApp .katex-display {
        color:var(--mq-text) !important;
      }

      .stApp [data-testid="stCaptionContainer"],
      .stApp small {
        color:var(--mq-muted) !important;
      }

      .block-container {
        max-width:1450px;
        padding-top:1.1rem;
        padding-bottom:2.2rem;
      }

      [data-testid="stSidebar"] {
        background:var(--mq-sidebar) !important;
        border-right:1px solid #dde2e8;
      }

      [data-testid="stSidebar"] > div {
        background:var(--mq-sidebar) !important;
      }

      [data-testid="stSidebar"] h1,
      [data-testid="stSidebar"] h2,
      [data-testid="stSidebar"] h3,
      [data-testid="stSidebar"] p,
      [data-testid="stSidebar"] label,
      [data-testid="stSidebar"] span,
      [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color:var(--mq-text) !important;
      }

      /* Radio controls: visible labels and borders in either system theme. */
      [data-testid="stRadio"] label,
      [data-testid="stRadio"] label p {
        color:var(--mq-text) !important;
      }

      [data-testid="stRadio"] [role="radiogroup"] label > div:first-child {
        border-color:#475569 !important;
      }

      /* Select boxes and number inputs. */
      [data-baseweb="select"] > div,
      [data-testid="stNumberInput"] input {
        background:var(--mq-white) !important;
        color:var(--mq-text) !important;
        border-color:var(--mq-border) !important;
      }

      [data-baseweb="select"] *,
      [data-testid="stNumberInput"] input,
      [data-testid="stNumberInput"] button,
      [data-testid="stNumberInput"] button * {
        color:var(--mq-text) !important;
      }

      [data-baseweb="popover"],
      [data-baseweb="menu"],
      [role="listbox"],
      [role="option"] {
        background:var(--mq-white) !important;
        color:var(--mq-text) !important;
      }

      /* Tabs need explicit colours because Streamlit theme values vary by user. */
      [data-baseweb="tab-list"] {
        border-bottom-color:var(--mq-border) !important;
      }

      [data-baseweb="tab"] p {
        color:#475569 !important;
      }

      [data-baseweb="tab"][aria-selected="true"] p {
        color:var(--mq-accent) !important;
        font-weight:700;
      }

      [data-baseweb="tab-highlight"] {
        background-color:var(--mq-accent) !important;
      }

      /* Stable high-contrast button styling. */
      .stButton > button {
        background:#ffffff !important;
        color:#172033 !important;
        border:1px solid #64748b !important;
      }

      .stButton > button p,
      .stButton > button span {
        color:inherit !important;
      }

      .stButton > button:hover {
        background:#f1f5f9 !important;
        border-color:#334155 !important;
      }

      .stButton > button[kind="primary"] {
        background:#b91c1c !important;
        color:#ffffff !important;
        border-color:#991b1b !important;
      }

      .stButton > button[kind="primary"]:hover {
        background:#991b1b !important;
      }

      /* Streamlit success/warning/error/info components. */
      [data-testid="stAlert"] {
        color:var(--mq-text) !important;
      }

      [data-testid="stAlert"] p,
      [data-testid="stAlert"] span {
        color:inherit !important;
      }

      [data-testid="stSidebar"] .block-container {
        padding-top:3rem;
      }

      header[data-testid="stHeader"] { background:transparent; }
      #MainMenu, footer { visibility:hidden; }

      .app-header {
        display:grid;
        grid-template-columns:230px 1fr 190px;
        gap:24px;
        align-items:center;
        padding:16px 10px 20px;
      }

      .app-header-logo {
        display:flex;
        justify-content:center;
        align-items:center;
      }

      .app-header-logo img {
        width:210px;
        max-height:92px;
        object-fit:contain;
      }

      .app-header-title h1 {
        margin:0;
        font-size:34px;
        line-height:1.05;
        color:#0f172a;
      }

      .app-header-title p {
        margin:7px 0 0;
        color:#334155;
        line-height:1.45;
        font-size:15px;
      }

      .app-header-author {
        text-align:right;
        color:#334155;
        font-size:13px;
        line-height:1.5;
      }

      .app-divider {
        height:1px;
        background:#d9dee5;
        margin:2px 0 18px;
      }

      .info {
        background:#e8f2ff;
        border-radius:10px;
        padding:13px 15px;
        color:#0f4c81;
        margin:8px 0 16px;
      }

      .hint {
        background:#ecfdf3;
        border:1px solid #bbf7d0;
        border-radius:10px;
        padding:11px 13px;
        color:#166534;
        margin:8px 0 14px;
      }

      .warning {
        background:#fff8e8;
        border:1px solid #f3d69b;
        border-radius:10px;
        padding:11px 13px;
        color:#7c4a03;
        margin:8px 0 14px;
      }

      .good {
        background:#ecfdf3;
        border:1px solid #bbf7d0;
        color:#166534;
        border-radius:9px;
        padding:10px 12px;
        margin:6px 0;
      }

      .bad {
        background:#fff1f2;
        border:1px solid #fecdd3;
        color:#9f1239;
        border-radius:9px;
        padding:10px 12px;
        margin:6px 0;
      }

      .card {
        border:1px solid #dfe4ea;
        border-radius:10px;
        padding:14px 16px;
        margin-bottom:14px;
        background:#fff;
      }

      .skill {
        color:#7c8798;
        font-size:13px;
        margin-top:10px;
      }

      @media (max-width:980px) {
        .app-header {
          grid-template-columns:1fr;
          text-align:center;
        }

        .app-header-author { text-align:center; }
        .app-header-logo img { width:190px; }
      }
    </style>
    """,
    unsafe_allow_html=True,
)


TOPICS = {
    "Linear equations": [1, 2, 3, 4],
    "Trigonometry": [1, 2, 3],
    "Vector components": [1, 2, 3, 4],
    "Differentiation": [1, 2, 3, 4, 5],
    "Integration": [1, 2, 3, 4, 5, 6],
    # Append new topics: existing saved URLs use the original topic indices.
    "Straight-line equations": list(range(1, 10)),
}

LINE_LEVELS = {
    1: "Read a graph",
    2: "Two known points",
    3: "One point and a gradient",
    4: "Axis intercepts",
    5: "A table of values",
    6: "Parallel and perpendicular lines",
    7: "Horizontal and vertical lines",
    8: "Rearrange a general equation",
    9: "Engineering graphs and units",
}


def fmt(value, decimals=4):
    if isinstance(value, sp.Basic):
        value = float(value)
    if abs(float(value) - round(float(value))) < 1e-10:
        return str(int(round(float(value))))
    return f"{float(value):.{decimals}f}".rstrip("0").rstrip(".")


def render_header():
    logo_html = (
        f'<img src="data:image/png;base64,{LOGO_B64}" alt="James Cook University">'
        if LOGO_B64 else '<span style="font-size:30px;font-weight:800;color:#b91c1c">MathQuest</span>'
    )
    st.markdown(
        f"""
        <div class="app-header">
          <div class="app-header-logo">
            {logo_html}
          </div>
          <div class="app-header-title">
            <h1>MathQuest</h1>
            <p>
              Foundation mathematics practice for EG1011 Statics and Dynamics:
              equations, straight-line graphs, trigonometry, vectors,
              differentiation and integration.
            </p>
          </div>
          <div class="app-header-author">
            Designed for EG1011<br>
            <b>Dr. Mehdi Khatamifar</b><br>
            James Cook University
          </div>
        </div>
        <div class="app-divider"></div>
        """,
        unsafe_allow_html=True,
    )


def make_answer(label, value, unit="", tolerance=0.015):
    return {
        "label": label,
        "value": float(value),
        "unit": unit,
        "tolerance": max(tolerance, 0.01 * max(1.0, abs(float(value)))),
    }


def close_enough(user_value, answer):
    return abs(float(user_value) - answer["value"]) <= answer["tolerance"]


def unique_problem(generator, topic, level):
    seen = st.session_state.setdefault("seen_problem_signatures", set())

    for _ in range(500):
        problem = generator(level)
        signature = f"{topic}|{level}|{problem['signature']}"
        if signature not in seen:
            seen.add(signature)
            problem["uid"] = f"{topic}_{level}_{len(seen)}"
            return problem

    # Very unlikely fallback.
    problem = generator(level)
    problem["uid"] = f"{topic}_{level}_{RNG.randrange(10**9)}"
    return problem


def generate_linear(level):
    if level == 1:
        a = RNG.choice([i for i in range(-9, 10) if i not in (0, 1, -1)])
        x_sol = RNG.randint(-12, 12)
        b = RNG.randint(-15, 15)
        c = a * x_sol + b

        equation = sp.Eq(a * x + b, c)

        return {
            "title": "One-step linear equation",
            "difficulty": "Foundation",
            "prompt": "Solve the following equation for x.",
            "display_equation": sp.latex(equation),
            "formula_question": {
                "question": "What should be done first?",
                "options": [
                    f"Subtract {b} from both sides",
                    f"Divide both sides by {a} immediately",
                    "Square both sides",
                    "Differentiate both sides",
                ],
                "correct": f"Subtract {b} from both sides",
                "explanation": "Undo the added constant first, then divide by the coefficient of x.",
            },
            "answers": [make_answer("x", x_sol)],
            "solution": [
                ("text", "Start with the original equation."),
                ("latex", sp.latex(equation)),
                ("text", f"Subtract {b} from both sides so that the x-term is isolated."),
                ("latex", sp.latex(sp.Eq(a * x, c - b))),
                ("text", f"Divide both sides by {a}."),
                ("latex", sp.latex(sp.Eq(x, sp.Rational(c - b, a)))),
                ("text", f"Therefore x = {x_sol}."),
            ],
            "signature": f"L1:{a}:{b}:{c}",
            "diagram": None,
            "teaching_point": "Whatever operation is performed on one side of an equation must also be performed on the other side.",
        }

    if level == 2:
        a = RNG.choice([2, 3, 4, 5, 6, -2, -3, -4])
        shift = RNG.randint(-8, 8)
        x_sol = RNG.randint(-10, 10)
        c = a * (x_sol + shift)

        equation = sp.Eq(a * (x + shift), c)

        return {
            "title": "Equation with brackets",
            "difficulty": "Easy",
            "prompt": "Solve the following equation for x.",
            "display_equation": sp.latex(equation),
            "formula_question": {
                "question": "Which method is cleanest here?",
                "options": [
                    f"Divide both sides by {a}, then remove the shift",
                    "Differentiate the brackets",
                    "Take the square root of both sides",
                    "Convert the equation into a triangle",
                ],
                "correct": f"Divide both sides by {a}, then remove the shift",
                "explanation": "The entire bracket is multiplied by a, so undo that multiplication first.",
            },
            "answers": [make_answer("x", x_sol)],
            "solution": [
                ("text", "The whole bracket is multiplied by the outside coefficient."),
                ("latex", sp.latex(equation)),
                ("text", f"Divide both sides by {a}."),
                ("latex", sp.latex(sp.Eq(x + shift, sp.Rational(c, a)))),
                ("text", f"Now subtract {shift} from both sides."),
                ("latex", sp.latex(sp.Eq(x, sp.Rational(c, a) - shift))),
                ("text", f"Therefore x = {x_sol}."),
            ],
            "signature": f"L2:{a}:{shift}:{c}",
            "diagram": None,
            "teaching_point": "Treat the bracket as one object until the outside multiplication has been removed.",
        }

    if level == 3:
        a = RNG.choice([i for i in range(-8, 9) if i not in (0,)])
        ccoef = RNG.choice([i for i in range(-8, 9) if i not in (0, a)])
        x_sol = RNG.randint(-10, 10)
        b = RNG.randint(-12, 12)
        d = a * x_sol + b - ccoef * x_sol

        equation = sp.Eq(a * x + b, ccoef * x + d)

        return {
            "title": "Variables on both sides",
            "difficulty": "Moderate",
            "prompt": "Solve the following equation for x.",
            "display_equation": sp.latex(equation),
            "formula_question": {
                "question": "What is the key first step?",
                "options": [
                    "Bring all x-terms to one side and constants to the other",
                    "Multiply both sides by x",
                    "Use sine and cosine",
                    "Integrate both sides",
                ],
                "correct": "Bring all x-terms to one side and constants to the other",
                "explanation": "Collect like terms before dividing by the final coefficient of x.",
            },
            "answers": [make_answer("x", x_sol)],
            "solution": [
                ("text", "Start by collecting all x-terms on the left."),
                ("latex", sp.latex(equation)),
                ("latex", sp.latex(sp.Eq((a - ccoef) * x + b, d))),
                ("text", f"Move the constant {b} to the right side."),
                ("latex", sp.latex(sp.Eq((a - ccoef) * x, d - b))),
                ("text", f"Divide by the coefficient {a - ccoef}."),
                ("latex", sp.latex(sp.Eq(x, sp.Rational(d - b, a - ccoef)))),
                ("text", f"Therefore x = {x_sol}."),
            ],
            "signature": f"L3:{a}:{b}:{ccoef}:{d}",
            "diagram": None,
            "teaching_point": "Collect like terms before dividing. Do not divide until only one x-term remains.",
        }

    # Level 4: simultaneous equations
    while True:
        a, b, c, d = [RNG.choice([i for i in range(-6, 7) if i != 0]) for _ in range(4)]
        determinant = a * d - b * c
        if determinant != 0:
            break

    x_sol = RNG.randint(-6, 6)
    y_sol = RNG.randint(-6, 6)
    e = a * x_sol + b * y_sol
    f = c * x_sol + d * y_sol

    return {
        "title": "Two simultaneous linear equations",
        "difficulty": "Challenging",
        "prompt": "Solve the two equations for x and y.",
        "display_equation": (
            r"\begin{cases}"
            + sp.latex(a * x + b * sp.Symbol("y"))
            + "="
            + sp.latex(e)
            + r"\\"
            + sp.latex(c * x + d * sp.Symbol("y"))
            + "="
            + sp.latex(f)
            + r"\end{cases}"
        ),
        "formula_question": {
            "question": "Which method is appropriate?",
            "options": [
                "Elimination or substitution",
                "Differentiate both equations",
                "Use the Pythagorean theorem",
                "Take inverse sine",
            ],
            "correct": "Elimination or substitution",
            "explanation": "Two unknowns require two independent equations. Elimination removes one unknown first.",
        },
        "answers": [
            make_answer("x", x_sol),
            make_answer("y", y_sol),
        ],
        "solution": [
            ("text", "Write the two equations clearly."),
            (
                "latex",
                r"\begin{aligned}"
                + sp.latex(a * x + b * sp.Symbol("y"))
                + "&="
                + sp.latex(e)
                + r"\\"
                + sp.latex(c * x + d * sp.Symbol("y"))
                + "&="
                + sp.latex(f)
                + r"\end{aligned}",
            ),
            ("text", f"Multiply the first equation by {c} and the second equation by {a}, so the x-terms become equal."),
            (
                "latex",
                r"\begin{aligned}"
                + sp.latex(a * c * x + b * c * sp.Symbol("y"))
                + "&="
                + sp.latex(c * e)
                + r"\\"
                + sp.latex(a * c * x + a * d * sp.Symbol("y"))
                + "&="
                + sp.latex(a * f)
                + r"\end{aligned}",
            ),
            ("text", "Subtract the second new equation from the first."),
            (
                "latex",
                sp.latex((b * c - a * d) * sp.Symbol("y"))
                + "="
                + sp.latex(c * e - a * f),
            ),
            (
                "latex",
                sp.latex(
                    sp.Eq(
                        sp.Symbol("y"),
                        sp.Rational(c * e - a * f, b * c - a * d),
                    )
                ),
            ),
            ("text", f"Therefore y = {y_sol}. Substitute this into the first original equation."),
            (
                "latex",
                sp.latex(sp.Eq(a * x + b * y_sol, e)),
            ),
            (
                "latex",
                sp.latex(sp.Eq(x, sp.Rational(e - b * y_sol, a))),
            ),
            ("text", f"Therefore x = {x_sol} and y = {y_sol}."),
        ],
        "signature": f"L4:{a}:{b}:{c}:{d}:{e}:{f}",
        "diagram": None,
        "teaching_point": "Two independent equations are needed to solve two unknowns. Eliminate one variable first.",
    }


def trig_triangle_figure(data):
    fig, ax = plt.subplots(figsize=(6.4, 4.0))
    A = np.array([0.8, 0.6])
    B = np.array([5.2, 0.6])
    C = np.array([5.2, 3.4])

    ax.add_patch(
        Polygon([A, B, C], closed=True, fill=False, linewidth=2.2)
    )
    ax.plot([B[0] - 0.3, B[0] - 0.3, B[0]], [B[1], B[1] + 0.3, B[1] + 0.3], linewidth=1.2)

    ax.text(3.0, 0.25, data.get("adj_label", "Adjacent"), ha="center")
    ax.text(5.55, 2.0, data.get("opp_label", "Opposite"), va="center", rotation=90)
    ax.text(2.9, 2.2, data.get("hyp_label", "Hypotenuse"), rotation=32, ha="center")
    ax.text(1.15, 0.78, rf"$\theta={data['theta']}^\circ$")

    ax.set_xlim(0.2, 6.2)
    ax.set_ylim(0.0, 4.0)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    return fig


def generate_trigonometry(level):
    angle = RNG.choice([20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70])
    rad = math.radians(angle)

    if level == 1:
        hyp = RNG.choice([8, 10, 12, 15, 18, 20, 24])
        opp = hyp * math.sin(rad)
        adj = hyp * math.cos(rad)

        return {
            "title": "Find sides using sine and cosine",
            "difficulty": "Foundation",
            "prompt": "A right triangle has the angle and hypotenuse shown. Find the opposite and adjacent sides.",
            "display_equation": None,
            "formula_question": {
                "question": "Which formulas should be used?",
                "options": [
                    "Opposite = H sin θ and Adjacent = H cos θ",
                    "Opposite = H cos θ and Adjacent = H sin θ",
                    "Opposite = H tan θ and Adjacent = H/tan θ",
                    "Use differentiation",
                ],
                "correct": "Opposite = H sin θ and Adjacent = H cos θ",
                "explanation": "SOH gives sin θ = O/H and CAH gives cos θ = A/H.",
            },
            "answers": [
                make_answer("Opposite side", opp, "units", 0.03),
                make_answer("Adjacent side", adj, "units", 0.03),
            ],
            "solution": [
                ("text", "Use SOH and CAH."),
                ("latex", r"\sin\theta=\frac{\text{opposite}}{\text{hypotenuse}}"),
                ("latex", r"\cos\theta=\frac{\text{adjacent}}{\text{hypotenuse}}"),
                ("text", "Rearrange each equation."),
                ("latex", rf"\text{{opposite}}=({hyp})\sin({angle}^\circ)={opp:.4f}"),
                ("latex", rf"\text{{adjacent}}=({hyp})\cos({angle}^\circ)={adj:.4f}"),
                ("text", "Round only at the end."),
            ],
            "signature": f"T1:{angle}:{hyp}",
            "diagram": ("trig", {
                "theta": angle,
                "hyp_label": f"H = {hyp}",
                "opp_label": "Opposite = ?",
                "adj_label": "Adjacent = ?",
            }),
            "teaching_point": "Identify opposite, adjacent and hypotenuse relative to the stated angle before choosing a formula.",
        }

    if level == 2:
        adjacent = RNG.choice([5, 7, 9, 12, 14, 16, 20])
        opposite = adjacent * math.tan(rad)
        hyp = adjacent / math.cos(rad)

        return {
            "title": "Find an unknown side using tangent",
            "difficulty": "Easy",
            "prompt": "A right triangle has the angle and adjacent side shown. Find the opposite side and the hypotenuse.",
            "display_equation": None,
            "formula_question": {
                "question": "Which ratio directly connects opposite and adjacent?",
                "options": [
                    "tan θ = opposite/adjacent",
                    "sin θ = adjacent/hypotenuse",
                    "cos θ = opposite/hypotenuse",
                    "tan θ = hypotenuse/opposite",
                ],
                "correct": "tan θ = opposite/adjacent",
                "explanation": "TOA gives tangent as opposite divided by adjacent.",
            },
            "answers": [
                make_answer("Opposite side", opposite, "units", 0.03),
                make_answer("Hypotenuse", hyp, "units", 0.03),
            ],
            "solution": [
                ("latex", r"\tan\theta=\frac{\text{opposite}}{\text{adjacent}}"),
                ("latex", rf"\text{{opposite}}=({adjacent})\tan({angle}^\circ)={opposite:.4f}"),
                ("text", "Now use cosine to find the hypotenuse."),
                ("latex", r"\cos\theta=\frac{\text{adjacent}}{\text{hypotenuse}}"),
                ("latex", rf"\text{{hypotenuse}}=\frac{{{adjacent}}}{{\cos({angle}^\circ)}}={hyp:.4f}"),
            ],
            "signature": f"T2:{angle}:{adjacent}",
            "diagram": ("trig", {
                "theta": angle,
                "hyp_label": "H = ?",
                "opp_label": "Opposite = ?",
                "adj_label": f"Adjacent = {adjacent}",
            }),
            "teaching_point": "Use the ratio containing the known side and the required side. Avoid introducing unnecessary unknowns.",
        }

    # Level 3: inverse trig
    adjacent = RNG.choice([4, 5, 6, 8, 10, 12, 15])
    opposite = RNG.choice([3, 4, 5, 7, 9, 11, 13])
    theta = math.degrees(math.atan2(opposite, adjacent))
    hyp = math.hypot(opposite, adjacent)

    return {
        "title": "Find an angle using inverse tangent",
        "difficulty": "Moderate",
        "prompt": "The opposite and adjacent sides are given. Find the angle θ and the hypotenuse.",
        "display_equation": None,
        "formula_question": {
            "question": "How should the angle be found?",
            "options": [
                "θ = tan⁻¹(opposite/adjacent)",
                "θ = tan(opposite/adjacent)",
                "θ = opposite × adjacent",
                "θ = sin⁻¹(adjacent/opposite)",
            ],
            "correct": "θ = tan⁻¹(opposite/adjacent)",
            "explanation": "The inverse tangent converts a side ratio into an angle.",
        },
        "answers": [
            make_answer("Angle θ", theta, "degrees", 0.05),
            make_answer("Hypotenuse", hyp, "units", 0.03),
        ],
        "solution": [
            ("latex", r"\tan\theta=\frac{\text{opposite}}{\text{adjacent}}"),
            ("latex", rf"\tan\theta=\frac{{{opposite}}}{{{adjacent}}}"),
            ("latex", rf"\theta=\tan^{{-1}}\left(\frac{{{opposite}}}{{{adjacent}}}\right)={theta:.4f}^\circ"),
            ("text", "Use Pythagoras for the hypotenuse."),
            ("latex", r"H^2=O^2+A^2"),
            ("latex", rf"H=\sqrt{{{opposite}^2+{adjacent}^2}}={hyp:.4f}"),
            ("text", "Make sure the calculator is in degree mode."),
        ],
        "signature": f"T3:{opposite}:{adjacent}",
        "diagram": ("trig", {
            "theta": round(theta, 1),
            "hyp_label": "H = ?",
            "opp_label": f"Opposite = {opposite}",
            "adj_label": f"Adjacent = {adjacent}",
        }),
        "teaching_point": "Use an inverse trigonometric function when the angle is unknown.",
    }


def vector_figure(data):
    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    origin = np.array([0.8, 0.8])
    theta = math.radians(data["angle_from_x"])
    length = 3.5
    end = origin + length * np.array([math.cos(theta), math.sin(theta)])

    arrow = FancyArrowPatch(
        origin,
        end,
        arrowstyle="->",
        mutation_scale=18,
        linewidth=2.2,
    )
    ax.add_patch(arrow)

    ax.plot([origin[0], end[0]], [origin[1], origin[1]], linestyle="--", linewidth=1.2)
    ax.plot([end[0], end[0]], [origin[1], end[1]], linestyle="--", linewidth=1.2)

    ax.text((origin[0] + end[0]) / 2, origin[1] - 0.28, data["x_label"], ha="center")
    ax.text(end[0] + 0.18, (origin[1] + end[1]) / 2, data["y_label"], va="center")
    ax.text((origin[0] + end[0]) / 2, (origin[1] + end[1]) / 2 + 0.25, data["vector_label"], ha="center")
    ax.text(origin[0] + 0.55, origin[1] + 0.18, data["angle_label"])

    ax.axhline(0, linewidth=0.8)
    ax.axvline(0, linewidth=0.8)
    ax.set_xlim(-0.5, 5.3)
    ax.set_ylim(-0.3, 4.7)
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    return fig


def direction_triangle_figure(data):
    """
    Draw a force vector with:
    - dashed rectangular x/y component construction;
    - a small rise-run-hypotenuse triangle placed on the force vector;
    - clear labels that match the calculation F_x=F(run/L), F_y=F(rise/L).
    """
    fig, ax = plt.subplots(figsize=(7.2, 4.5))

    run = float(data["run"])
    rise = float(data["rise"])
    magnitude = float(data["magnitude"])

    direction_length = math.hypot(run, rise)
    ux = run / direction_length
    uy = rise / direction_length

    origin = np.array([0.75, 0.65])
    force_draw_length = 4.35
    end = origin + force_draw_length * np.array([ux, uy])
    x_corner = np.array([end[0], origin[1]])

    force_colour = "#ef4444"
    triangle_colour = "#2563eb"
    angle_colour = "#16a34a"

    # Main force vector.
    force_arrow = FancyArrowPatch(
        origin,
        end,
        arrowstyle="->",
        mutation_scale=18,
        linewidth=2.8,
        color=force_colour,
    )
    ax.add_patch(force_arrow)

    # Dashed component construction.
    x_arrow = FancyArrowPatch(
        origin,
        x_corner,
        arrowstyle="->",
        mutation_scale=15,
        linewidth=1.9,
        linestyle="--",
        color=force_colour,
    )
    y_arrow = FancyArrowPatch(
        x_corner,
        end,
        arrowstyle="->",
        mutation_scale=15,
        linewidth=1.9,
        linestyle="--",
        color=force_colour,
    )
    ax.add_patch(x_arrow)
    ax.add_patch(y_arrow)

    # Main vector and component labels.
    ax.text(
        end[0] + 0.08,
        end[1] + 0.10,
        rf"$F={fmt(magnitude)}\ \mathrm{{N}}$",
        color=force_colour,
        fontsize=11,
        weight="bold",
    )
    ax.text(
        (origin[0] + x_corner[0]) / 2,
        origin[1] - 0.38,
        r"$F_x$",
        color=force_colour,
        fontsize=11,
        ha="center",
    )
    ax.text(
        x_corner[0] + 0.18,
        (origin[1] + end[1]) / 2,
        r"$F_y$",
        color=force_colour,
        fontsize=11,
        va="center",
    )

    # Small direction triangle placed on the vector.
    scale = 1.15 / direction_length
    small_run = run * scale
    small_rise = rise * scale

    tri_start = origin + 0.50 * (end - origin)
    tri_horizontal_end = tri_start + np.array([small_run, 0.0])
    tri_end = tri_horizontal_end + np.array([0.0, small_rise])

    ax.plot(
        [tri_start[0], tri_horizontal_end[0]],
        [tri_start[1], tri_horizontal_end[1]],
        color=triangle_colour,
        linewidth=2.0,
    )
    ax.plot(
        [tri_horizontal_end[0], tri_end[0]],
        [tri_horizontal_end[1], tri_end[1]],
        color=triangle_colour,
        linewidth=2.0,
    )
    ax.plot(
        [tri_start[0], tri_end[0]],
        [tri_start[1], tri_end[1]],
        color=triangle_colour,
        linewidth=2.0,
    )

    ax.text(
        (tri_start[0] + tri_horizontal_end[0]) / 2,
        tri_start[1] - 0.22,
        fmt(run),
        color=triangle_colour,
        fontsize=10,
        ha="center",
        weight="bold",
    )
    ax.text(
        tri_horizontal_end[0] + 0.12,
        (tri_horizontal_end[1] + tri_end[1]) / 2,
        fmt(rise),
        color=triangle_colour,
        fontsize=10,
        va="center",
        weight="bold",
    )
    ax.text(
        (tri_start[0] + tri_end[0]) / 2 - 0.02,
        (tri_start[1] + tri_end[1]) / 2 + 0.17,
        rf"$L=\sqrt{{{fmt(run)}^2+{fmt(rise)}^2}}$",
        color=triangle_colour,
        fontsize=9,
        ha="center",
        rotation=math.degrees(math.atan2(rise, run)),
    )

    # Angle arc at the origin.
    theta = math.atan2(rise, run)
    arc_angles = np.linspace(0.0, theta, 60)
    arc_radius = 0.58
    ax.plot(
        origin[0] + arc_radius * np.cos(arc_angles),
        origin[1] + arc_radius * np.sin(arc_angles),
        color=angle_colour,
        linewidth=1.8,
    )
    ax.text(
        origin[0] + 0.68 * math.cos(theta / 2),
        origin[1] + 0.68 * math.sin(theta / 2),
        r"$\theta$",
        color=angle_colour,
        fontsize=10,
        weight="bold",
    )

    # Light axes for orientation.
    ax.plot(
        [origin[0] - 0.2, end[0] + 0.75],
        [origin[1], origin[1]],
        color="#cbd5e1",
        linewidth=0.9,
    )
    ax.plot(
        [origin[0], origin[0]],
        [origin[1] - 0.2, end[1] + 0.65],
        color="#cbd5e1",
        linewidth=0.9,
    )

    ax.set_xlim(0.1, max(6.1, end[0] + 1.1))
    ax.set_ylim(0.05, max(4.5, end[1] + 0.9))
    ax.set_aspect("equal")
    ax.axis("off")
    fig.tight_layout()
    return fig


def generate_vector(level):
    magnitude = RNG.choice([40, 50, 60, 75, 80, 90, 100, 120, 150])
    angle = RNG.choice([20, 25, 30, 35, 40, 45, 50, 55, 60])

    if level == 1:
        fx = magnitude * math.cos(math.radians(angle))
        fy = magnitude * math.sin(math.radians(angle))

        return {
            "title": "Vector components from an angle above +x",
            "difficulty": "Foundation",
            "prompt": "Resolve the vector into x- and y-components.",
            "display_equation": None,
            "formula_question": {
                "question": "Which component equations are correct?",
                "options": [
                    "Fₓ = F cos θ, Fᵧ = F sin θ",
                    "Fₓ = F sin θ, Fᵧ = F cos θ",
                    "Fₓ = F tan θ, Fᵧ = F/tan θ",
                    "Fₓ = F + θ, Fᵧ = F - θ",
                ],
                "correct": "Fₓ = F cos θ, Fᵧ = F sin θ",
                "explanation": "The angle is measured from the x-axis, so x is adjacent and y is opposite.",
            },
            "answers": [
                make_answer("Fₓ", fx, "N", 0.05),
                make_answer("Fᵧ", fy, "N", 0.05),
            ],
            "solution": [
                ("text", "The angle is measured from the positive x-axis."),
                ("latex", rf"F_x=F\cos\theta=({magnitude})\cos({angle}^\circ)={fx:.4f}\ \text{{N}}"),
                ("latex", rf"F_y=F\sin\theta=({magnitude})\sin({angle}^\circ)={fy:.4f}\ \text{{N}}"),
                ("text", "Both components are positive because the vector is in the first quadrant."),
                ("latex", rf"\mathbf F=({fx:.4f})\mathbf i+({fy:.4f})\mathbf j\ \text{{N}}"),
            ],
            "signature": f"V1:{magnitude}:{angle}",
            "diagram": ("vector", {
                "angle_from_x": angle,
                "x_label": r"$F_x$",
                "y_label": r"$F_y$",
                "vector_label": f"F = {magnitude} N",
                "angle_label": rf"${angle}^\circ$",
            }),
            "teaching_point": "When the angle is measured from x, cosine belongs to x and sine belongs to y.",
        }

    if level == 2:
        # Angle from vertical, first quadrant.
        fx = magnitude * math.sin(math.radians(angle))
        fy = magnitude * math.cos(math.radians(angle))
        angle_from_x = 90 - angle

        return {
            "title": "Vector components when angle is measured from vertical",
            "difficulty": "Easy",
            "prompt": "The angle is measured from the positive y-axis. Resolve the vector into x- and y-components.",
            "display_equation": None,
            "formula_question": {
                "question": "Which equations are correct when θ is measured from y?",
                "options": [
                    "Fₓ = F sin θ, Fᵧ = F cos θ",
                    "Fₓ = F cos θ, Fᵧ = F sin θ",
                    "Fₓ = F tan θ, Fᵧ = F",
                    "Fₓ = F/θ, Fᵧ = Fθ",
                ],
                "correct": "Fₓ = F sin θ, Fᵧ = F cos θ",
                "explanation": "Relative to the angle from y, the y-component is adjacent and the x-component is opposite.",
            },
            "answers": [
                make_answer("Fₓ", fx, "N", 0.05),
                make_answer("Fᵧ", fy, "N", 0.05),
            ],
            "solution": [
                ("text", "Because the angle is measured from the y-axis, the roles of sine and cosine swap."),
                ("latex", rf"F_x=F\sin\theta=({magnitude})\sin({angle}^\circ)={fx:.4f}\ \text{{N}}"),
                ("latex", rf"F_y=F\cos\theta=({magnitude})\cos({angle}^\circ)={fy:.4f}\ \text{{N}}"),
                ("latex", rf"\mathbf F=({fx:.4f})\mathbf i+({fy:.4f})\mathbf j\ \text{{N}}"),
            ],
            "signature": f"V2:{magnitude}:{angle}",
            "diagram": ("vector", {
                "angle_from_x": angle_from_x,
                "x_label": r"$F_x$",
                "y_label": r"$F_y$",
                "vector_label": f"F = {magnitude} N",
                "angle_label": rf"${angle}^\circ$ from +y",
            }),
            "teaching_point": "Always identify the axis from which the angle is measured before assigning sine and cosine.",
        }

    if level == 3:
        # Quadrant II or IV.
        quadrant = RNG.choice([2, 4])

        if quadrant == 2:
            angle_from_x = 180 - angle
            fx = -magnitude * math.cos(math.radians(angle))
            fy = magnitude * math.sin(math.radians(angle))
            direction_text = f"{angle}° above the negative x-axis"
            sign_note = "x is negative and y is positive."
        else:
            angle_from_x = 360 - angle
            fx = magnitude * math.cos(math.radians(angle))
            fy = -magnitude * math.sin(math.radians(angle))
            direction_text = f"{angle}° below the positive x-axis"
            sign_note = "x is positive and y is negative."

        return {
            "title": "Vector components with signs",
            "difficulty": "Moderate",
            "prompt": f"A vector of magnitude {magnitude} N acts {direction_text}. Find its signed components.",
            "display_equation": None,
            "formula_question": {
                "question": "What determines the component signs?",
                "options": [
                    "The quadrant and actual vector direction",
                    "The vector magnitude only",
                    "Sine is always negative",
                    "Cosine is always positive",
                ],
                "correct": "The quadrant and actual vector direction",
                "explanation": "First calculate component magnitudes, then assign signs from the direction.",
            },
            "answers": [
                make_answer("Fₓ", fx, "N", 0.05),
                make_answer("Fᵧ", fy, "N", 0.05),
            ],
            "solution": [
                ("text", "Calculate the component magnitudes using the acute reference angle."),
                ("latex", rf"|F_x|=({magnitude})\cos({angle}^\circ)={abs(fx):.4f}\ \text{{N}}"),
                ("latex", rf"|F_y|=({magnitude})\sin({angle}^\circ)={abs(fy):.4f}\ \text{{N}}"),
                ("text", f"From the direction, {sign_note}"),
                ("latex", rf"\mathbf F=({fx:.4f})\mathbf i+({fy:.4f})\mathbf j\ \text{{N}}"),
            ],
            "signature": f"V3:{magnitude}:{angle}:{quadrant}",
            "diagram": ("vector", {
                "angle_from_x": angle_from_x,
                "x_label": r"$F_x$",
                "y_label": r"$F_y$",
                "vector_label": f"F = {magnitude} N",
                "angle_label": direction_text,
            }),
            "teaching_point": "Trigonometry gives magnitudes. The diagram and quadrant determine signs.",
        }

    # Level 4: direction triangle shown directly on the vector.
    run, rise = RNG.choice(
        [
            (3, 4),
            (4, 3),
            (5, 2),
            (5, 3),
            (7, 4),
            (8, 5),
        ]
    )
    hyp = math.hypot(run, rise)
    fx = magnitude * run / hyp
    fy = magnitude * rise / hyp
    theta = math.degrees(math.atan2(rise, run))

    return {
        "title": "Force components from a small direction triangle",
        "difficulty": "Challenging",
        "prompt": (
            "The small triangle drawn on the force vector gives its direction. "
            "Use the triangle ratios to calculate the x- and y-components."
        ),
        "display_equation": None,
        "formula_question": {
            "question": "What do the numbers in the small triangle represent?",
            "options": [
                "Direction ratios used to form a unit vector",
                "The actual force components in newtons",
                "The x- and y-coordinates of the force application point",
                "The force magnitude and moment",
            ],
            "correct": "Direction ratios used to form a unit vector",
            "explanation": (
                "The small triangle describes direction only. Divide its horizontal "
                "and vertical sides by its hypotenuse, then multiply by F."
            ),
        },
        "answers": [
            make_answer("Fₓ", fx, "N", 0.05),
            make_answer("Fᵧ", fy, "N", 0.05),
        ],
        "solution": [
            (
                "text",
                "The small triangle is similar to the large component triangle. "
                "Its sides give the direction ratios.",
            ),
            (
                "latex",
                rf"L=\sqrt{{({run})^2+({rise})^2}}={hyp:.4f}",
            ),
            (
                "text",
                "The horizontal direction ratio is run/L and the vertical direction "
                "ratio is rise/L.",
            ),
            (
                "latex",
                rf"\cos\theta=\frac{{{run}}}{{{hyp:.4f}}},"
                rf"\qquad \sin\theta=\frac{{{rise}}}{{{hyp:.4f}}}",
            ),
            (
                "latex",
                rf"F_x=F\frac{{{run}}}{{L}}"
                rf"=({magnitude})\frac{{{run}}}{{{hyp:.4f}}}"
                rf"={fx:.4f}\ \text{{N}}",
            ),
            (
                "latex",
                rf"F_y=F\frac{{{rise}}}{{L}}"
                rf"=({magnitude})\frac{{{rise}}}{{{hyp:.4f}}}"
                rf"={fy:.4f}\ \text{{N}}",
            ),
            (
                "text",
                "This is equivalent to using cosine and sine with the angle shown.",
            ),
            (
                "latex",
                rf"\theta=\tan^{{-1}}\left(\frac{{{rise}}}{{{run}}}\right)"
                rf"={theta:.4f}^\circ",
            ),
            (
                "latex",
                rf"\mathbf F=({fx:.4f})\mathbf i+({fy:.4f})\mathbf j\ \text{{N}}",
            ),
        ],
        "signature": f"V4:{magnitude}:{run}:{rise}",
        "diagram": (
            "direction_triangle",
            {
                "magnitude": magnitude,
                "run": run,
                "rise": rise,
            },
        ),
        "teaching_point": (
            "The small triangle gives direction ratios. Its side numbers are not "
            "the force components until they are divided by the triangle hypotenuse "
            "and multiplied by the force magnitude."
        ),
    }



def generate_differentiation(level):
    if level == 1:
        coefficient = RNG.choice([2, 3, 4, 5, 6, -2, -3, -4])
        power = RNG.randint(2, 6)
        expr = coefficient * x**power
        derivative = sp.diff(expr, x)
        x_value = RNG.randint(1, 4)
        answer_value = derivative.subs(x, x_value)

        return {
            "title": "Power-rule differentiation",
            "difficulty": "Foundation",
            "prompt": f"Differentiate the function, then evaluate the derivative at x = {x_value}.",
            "display_equation": rf"y={sp.latex(expr)}",
            "formula_question": {
                "question": "Which rule is required?",
                "options": [
                    "d(xⁿ)/dx = n xⁿ⁻¹",
                    "∫xⁿdx = xⁿ⁺¹/(n+1)",
                    "sin θ = opposite/hypotenuse",
                    "ax + b = c",
                ],
                "correct": "d(xⁿ)/dx = n xⁿ⁻¹",
                "explanation": "Multiply by the power and reduce the power by one.",
            },
            "answers": [
                make_answer(f"dy/dx at x = {x_value}", answer_value),
            ],
            "solution": [
                ("latex", rf"y={sp.latex(expr)}"),
                ("latex", r"\frac{d}{dx}\left(ax^n\right)=anx^{n-1}"),
                ("latex", rf"\frac{{dy}}{{dx}}={sp.latex(derivative)}"),
                ("latex", rf"\left.\frac{{dy}}{{dx}}\right|_{{x={x_value}}}={sp.latex(derivative.subs(x, x_value))}"),
            ],
            "signature": f"D1:{coefficient}:{power}:{x_value}",
            "diagram": None,
            "teaching_point": "The derivative gives the rate of change or slope of a function.",
        }

    if level == 2:
        a = RNG.choice([2, 3, 4, -2, -3])
        b = RNG.choice([2, 3, 5, -2, -4])
        n = RNG.randint(3, 5)
        m = RNG.randint(1, n - 1)
        c = RNG.randint(-8, 8)
        expr = a * x**n + b * x**m + c
        derivative = sp.diff(expr, x)
        x_value = RNG.randint(1, 3)
        answer_value = derivative.subs(x, x_value)

        return {
            "title": "Differentiate a polynomial",
            "difficulty": "Easy",
            "prompt": f"Differentiate term-by-term, then evaluate at x = {x_value}.",
            "display_equation": rf"y={sp.latex(expr)}",
            "formula_question": {
                "question": "What happens to a constant during differentiation?",
                "options": [
                    "Its derivative is zero",
                    "It remains unchanged",
                    "It becomes x",
                    "It becomes infinity",
                ],
                "correct": "Its derivative is zero",
                "explanation": "A constant does not change with x, so its rate of change is zero.",
            },
            "answers": [
                make_answer(f"dy/dx at x = {x_value}", answer_value),
            ],
            "solution": [
                ("text", "Differentiate each term separately."),
                ("latex", rf"y={sp.latex(expr)}"),
                ("latex", rf"\frac{{dy}}{{dx}}={sp.latex(derivative)}"),
                ("text", "The constant term disappears because its derivative is zero."),
                ("latex", rf"\left.\frac{{dy}}{{dx}}\right|_{{x={x_value}}}={sp.latex(answer_value)}"),
            ],
            "signature": f"D2:{a}:{n}:{b}:{m}:{c}:{x_value}",
            "diagram": None,
            "teaching_point": "Differentiate one term at a time. Constants differentiate to zero.",
        }

    if level == 3:
        a = RNG.choice([1, 2, 3])
        b = RNG.choice([-4, -3, -2, 2, 3, 4])
        c = RNG.choice([-5, -3, 2, 4, 6])
        d = RNG.randint(-5, 5)
        s_expr = a * t**3 + b * t**2 + c * t + d
        v_expr = sp.diff(s_expr, t)
        acc_expr = sp.diff(v_expr, t)
        time_value = RNG.randint(1, 4)
        v_value = v_expr.subs(t, time_value)
        acc_value = acc_expr.subs(t, time_value)

        return {
            "title": "Position → velocity → acceleration",
            "difficulty": "Moderate",
            "prompt": f"The position function is given. Find velocity and acceleration at t = {time_value} s.",
            "display_equation": rf"s(t)={sp.latex(s_expr)}",
            "formula_question": {
                "question": "Which relationships are correct?",
                "options": [
                    "v = ds/dt and a = dv/dt",
                    "v = ∫s dt and a = ∫v dt",
                    "v = s/t and a = v/t for every problem",
                    "v = sin s and a = cos v",
                ],
                "correct": "v = ds/dt and a = dv/dt",
                "explanation": "Velocity is the time derivative of position, and acceleration is the time derivative of velocity.",
            },
            "answers": [
                make_answer(f"Velocity at t = {time_value}", v_value, "m/s"),
                make_answer(f"Acceleration at t = {time_value}", acc_value, "m/s²"),
            ],
            "solution": [
                ("latex", rf"s(t)={sp.latex(s_expr)}"),
                ("latex", r"v(t)=\frac{ds}{dt}"),
                ("latex", rf"v(t)={sp.latex(v_expr)}"),
                ("latex", r"a(t)=\frac{dv}{dt}"),
                ("latex", rf"a(t)={sp.latex(acc_expr)}"),
                ("latex", rf"v({time_value})={sp.latex(v_value)}\ \text{{m/s}}"),
                ("latex", rf"a({time_value})={sp.latex(acc_value)}\ \text{{m/s}}^2"),
            ],
            "signature": f"D3:{a}:{b}:{c}:{d}:{time_value}",
            "diagram": None,
            "teaching_point": "In kinematics, differentiate position once for velocity and twice for acceleration.",
        }


    if level == 4:
        trig_kind = RNG.choice(["sin", "cos"])
        amplitude = RNG.choice([2, 3, 4, 5, 6])
        frequency = RNG.choice([1, 2, 3, 4])
        target_angle = RNG.choice(
            [
                sp.Integer(0),
                sp.pi / 6,
                sp.pi / 4,
                sp.pi / 3,
            ]
        )
        x_value = sp.simplify(target_angle / frequency)

        if trig_kind == "sin":
            expr = amplitude * sp.sin(frequency * x)
            derivative = amplitude * frequency * sp.cos(frequency * x)
            rule_text = r"\frac{d}{dx}\sin(kx)=k\cos(kx)"
            correct_option = "d[sin(kx)]/dx = k cos(kx)"
            options = [
                correct_option,
                "d[sin(kx)]/dx = -k cos(kx)",
                "d[sin(kx)]/dx = cos(kx)/k",
                "d[sin(kx)]/dx = k sin(kx)",
            ]
        elif trig_kind == "cos":
            expr = amplitude * sp.cos(frequency * x)
            derivative = -amplitude * frequency * sp.sin(frequency * x)
            rule_text = r"\frac{d}{dx}\cos(kx)=-k\sin(kx)"
            correct_option = "d[cos(kx)]/dx = -k sin(kx)"
            options = [
                "d[cos(kx)]/dx = k sin(kx)",
                correct_option,
                "d[cos(kx)]/dx = sin(kx)/k",
                "d[cos(kx)]/dx = -cos(kx)/k",
            ]

        derivative_value = sp.simplify(derivative.subs(x, x_value))

        return {
            "title": "Differentiate sine or cosine",
            "difficulty": "Moderate",
            "prompt": (
                "Differentiate the trigonometric function and evaluate the "
                "derivative at the stated x-value."
            ),
            "display_equation": (
                rf"y={sp.latex(expr)},"
                rf"\qquad x={sp.latex(x_value)}\ \text{{rad}}"
            ),
            "formula_question": {
                "question": "Which derivative rule is correct for this function?",
                "options": options,
                "correct": correct_option,
                "explanation": (
                    "Use the trigonometric derivative and multiply by the derivative "
                    "of the inside function kx. This is the chain rule."
                ),
            },
            "answers": [
                make_answer(
                    f"dy/dx at x = {sp.latex(x_value)} rad",
                    derivative_value,
                ),
            ],
            "solution": [
                (
                    "text",
                    "Trigonometric differentiation uses radians. First identify the "
                    "outer trigonometric function and the inside function.",
                ),
                ("latex", rf"y={sp.latex(expr)}"),
                ("latex", rule_text),
                (
                    "text",
                    f"The derivative of the inside function {frequency}x is "
                    f"{frequency}.",
                ),
                ("latex", rf"\frac{{dy}}{{dx}}={sp.latex(derivative)}"),
                (
                    "latex",
                    rf"\left.\frac{{dy}}{{dx}}\right|_{{x={sp.latex(x_value)}}}"
                    rf"={sp.latex(derivative_value)}"
                    rf"\approx {float(derivative_value):.5f}",
                ),
            ],
            "signature": (
                f"D4:{trig_kind}:{amplitude}:{frequency}:"
                f"{sp.srepr(target_angle)}"
            ),
            "diagram": None,
            "teaching_point": (
                "For sin(kx) and cos(kx), the factor k appears because of the "
                "chain rule. Calculus trigonometric formulas assume radians."
            ),
        }

    # Level 5: sinusoidal motion.
    motion_kind = RNG.choice(["sin", "cos"])
    amplitude = RNG.choice([2, 3, 4, 5])
    omega = RNG.choice([1, 2, 3, 4])
    target_angle = RNG.choice(
        [
            sp.Integer(0),
            sp.pi / 6,
            sp.pi / 4,
            sp.pi / 3,
            sp.pi / 2,
        ]
    )
    time_value = sp.simplify(target_angle / omega)

    if motion_kind == "sin":
        s_expr = amplitude * sp.sin(omega * t)
    else:
        s_expr = amplitude * sp.cos(omega * t)

    v_expr = sp.diff(s_expr, t)
    a_expr = sp.diff(v_expr, t)
    v_value = sp.simplify(v_expr.subs(t, time_value))
    a_value = sp.simplify(a_expr.subs(t, time_value))

    return {
        "title": "Differentiate sinusoidal motion",
        "difficulty": "Challenging",
        "prompt": (
            "The particle position is sinusoidal. Find the velocity and "
            "acceleration at the stated time."
        ),
        "display_equation": (
            rf"s(t)={sp.latex(s_expr)}\ \text{{m}},"
            rf"\qquad t={sp.latex(time_value)}\ \text{{s}}"
        ),
        "formula_question": {
            "question": "Which kinematic relationships are required?",
            "options": [
                "v = ds/dt and a = d²s/dt²",
                "v = ∫s dt and a = ∫v dt",
                "v = s/t and a = v/t in every case",
                "v = d²s/dt² and a = ds/dt",
            ],
            "correct": "v = ds/dt and a = d²s/dt²",
            "explanation": (
                "Differentiate position once for velocity and twice for acceleration."
            ),
        },
        "answers": [
            make_answer(
                f"Velocity at t = {sp.latex(time_value)}",
                v_value,
                "m/s",
            ),
            make_answer(
                f"Acceleration at t = {sp.latex(time_value)}",
                a_value,
                "m/s²",
            ),
        ],
        "solution": [
            (
                "text",
                "The angular argument is in radians. Differentiate the position "
                "function using the chain rule.",
            ),
            ("latex", rf"s(t)={sp.latex(s_expr)}"),
            ("latex", r"v(t)=\frac{ds}{dt}"),
            ("latex", rf"v(t)={sp.latex(v_expr)}"),
            ("latex", r"a(t)=\frac{dv}{dt}=\frac{d^2s}{dt^2}"),
            ("latex", rf"a(t)={sp.latex(a_expr)}"),
            (
                "text",
                "The answer has been obtained by differentiating twice. "
                "For this sinusoidal function only, we can now check that "
                "a(t)=-ω²s(t).",
            ),
            (
                "latex",
                rf"a(t)=-({omega})^2s(t)=-{omega**2}s(t)",
            ),
            (
                "latex",
                rf"({sp.latex(a_expr)})+({omega})^2"
                rf"({sp.latex(s_expr)})=0",
            ),
            (
                "latex",
                rf"v({sp.latex(time_value)})={sp.latex(v_value)}"
                rf"\approx {float(v_value):.5f}\ \text{{m/s}}",
            ),
            (
                "latex",
                rf"a({sp.latex(time_value)})={sp.latex(a_value)}"
                rf"\approx {float(a_value):.5f}\ \text{{m/s}}^2",
            ),
        ],
        "signature": (
            f"D5:{motion_kind}:{amplitude}:{omega}:"
            f"{sp.srepr(target_angle)}"
        ),
        "diagram": None,
        "teaching_point": (
            "For s=A sin(ωt) or A cos(ωt), each differentiation introduces a "
            "factor ω. The acceleration is opposite in sign to displacement: "
            "a=-ω²s."
        ),
    }



def generate_integration(level):
    if level == 1:
        coefficient = RNG.choice([2, 3, 4, 5, 6, -2, -3])
        power = RNG.randint(1, 5)
        upper = RNG.randint(2, 5)
        expr = coefficient * x**power
        antiderivative = sp.integrate(expr, x)
        value = sp.integrate(expr, (x, 0, upper))

        return {
            "title": "Basic definite integration",
            "difficulty": "Foundation",
            "prompt": f"Evaluate the definite integral from x = 0 to x = {upper}.",
            "display_equation": rf"\int_0^{{{upper}}}{sp.latex(expr)}\,dx",
            "formula_question": {
                "question": "Which integration rule is required?",
                "options": [
                    "∫xⁿdx = xⁿ⁺¹/(n+1)",
                    "d(xⁿ)/dx = n xⁿ⁻¹",
                    "Differentiate xⁿ using the power rule",
                    "Add the upper and lower limits directly",
                ],
                "correct": "∫xⁿdx = xⁿ⁺¹/(n+1)",
                "explanation": "Increase the power by one, then divide by the new power.",
            },
            "answers": [
                make_answer("Integral value", value),
            ],
            "solution": [
                ("latex", rf"\int {sp.latex(expr)}\,dx={sp.latex(antiderivative)}+C"),
                ("text", "For a definite integral, evaluate the antiderivative at the upper and lower limits."),
                ("latex", rf"\left[{sp.latex(antiderivative)}\right]_0^{{{upper}}}"),
                ("latex", rf"{sp.latex(antiderivative.subs(x, upper))}-{sp.latex(antiderivative.subs(x, 0))}={sp.latex(value)}"),
            ],
            "signature": f"I1:{coefficient}:{power}:{upper}",
            "diagram": None,
            "teaching_point": "Integration reverses differentiation. For definite integrals, subtract the lower-limit value from the upper-limit value.",
        }

    if level == 2:
        a = RNG.choice([1, 2, 3, -1, -2])
        b = RNG.choice([2, 3, 4, -2, -3])
        c = RNG.randint(-5, 5)
        lower = RNG.randint(0, 2)
        upper = RNG.randint(lower + 2, lower + 5)
        expr = a * x**2 + b * x + c
        antiderivative = sp.integrate(expr, x)
        value = sp.integrate(expr, (x, lower, upper))

        return {
            "title": "Integrate a polynomial",
            "difficulty": "Easy",
            "prompt": f"Evaluate the polynomial integral from x = {lower} to x = {upper}.",
            "display_equation": rf"\int_{{{lower}}}^{{{upper}}}\left({sp.latex(expr)}\right)\,dx",
            "formula_question": {
                "question": "How should a polynomial be integrated?",
                "options": [
                    "Integrate each term separately",
                    "Multiply all powers together",
                    "Differentiate the entire expression",
                    "Use the Pythagorean theorem",
                ],
                "correct": "Integrate each term separately",
                "explanation": "Integration distributes across sums and differences.",
            },
            "answers": [
                make_answer("Integral value", value),
            ],
            "solution": [
                ("text", "Integrate every term separately."),
                ("latex", rf"\int\left({sp.latex(expr)}\right)\,dx={sp.latex(antiderivative)}+C"),
                ("latex", rf"\left[{sp.latex(antiderivative)}\right]_{{{lower}}}^{{{upper}}}"),
                ("latex", rf"{sp.latex(antiderivative.subs(x, upper))}-{sp.latex(antiderivative.subs(x, lower))}={sp.latex(value)}"),
            ],
            "signature": f"I2:{a}:{b}:{c}:{lower}:{upper}",
            "diagram": None,
            "teaching_point": "Integrate term-by-term and apply the limits only after obtaining the antiderivative.",
        }

    if level == 3:
        a = RNG.choice([1, 2, 3, 4])
        b = RNG.choice([-3, -2, 0, 2, 3])
        v0 = RNG.randint(-5, 8)
        time_value = RNG.randint(2, 5)
        acc_expr = a * t + b
        v_expr = sp.integrate(acc_expr, t) + sp.Symbol("C")
        constant = v0
        v_exact = sp.integrate(acc_expr, (t, 0, t)) + v0
        answer_value = v_exact.subs(t, time_value)

        return {
            "title": "Acceleration → velocity using an initial condition",
            "difficulty": "Moderate",
            "prompt": f"Acceleration is given and v(0) = {v0} m/s. Find v({time_value}).",
            "display_equation": rf"a(t)={sp.latex(acc_expr)}",
            "formula_question": {
                "question": "Which relationship should be used?",
                "options": [
                    "v(t) = v₀ + ∫₀ᵗ a(τ)dτ",
                    "v(t) = da/dt",
                    "v(t) = a(t)/t",
                    "v(t) = sin a",
                ],
                "correct": "v(t) = v₀ + ∫₀ᵗ a(τ)dτ",
                "explanation": "Velocity change equals the time integral of acceleration.",
            },
            "answers": [
                make_answer(f"v({time_value})", answer_value, "m/s"),
            ],
            "solution": [
                ("latex", r"v(t)=v_0+\int_0^t a(\tau)\,d\tau"),
                ("latex", rf"v(t)={v0}+\int_0^t\left({sp.latex(acc_expr.subs(t, sp.Symbol('tau')))}\right)\,d\tau"),
                ("latex", rf"v(t)={sp.latex(v_exact)}"),
                ("latex", rf"v({time_value})={sp.latex(answer_value)}\ \text{{m/s}}"),
                ("text", "The initial velocity determines the integration constant."),
            ],
            "signature": f"I3:{a}:{b}:{v0}:{time_value}",
            "diagram": None,
            "teaching_point": "An indefinite integral needs a constant. An initial condition determines that constant.",
        }

    if level == 4:
        a = RNG.choice([1, 2, 3])
        b = RNG.choice([-4, -2, 1, 3, 5])
        s0 = RNG.randint(-5, 10)
        time_value = RNG.randint(2, 5)
        velocity = a * t**2 + b
        position = sp.integrate(velocity, (t, 0, t)) + s0
        answer_value = position.subs(t, time_value)

        return {
            "title": "Velocity → position using an initial condition",
            "difficulty": "Challenging",
            "prompt": f"Velocity is given and s(0) = {s0} m. Find s({time_value}).",
            "display_equation": rf"v(t)={sp.latex(velocity)}",
            "formula_question": {
                "question": "Which relationship should be used?",
                "options": [
                    "s(t) = s₀ + ∫₀ᵗ v(τ)dτ",
                    "s(t) = dv/dt",
                    "s(t) = v(t)/t",
                    "s(t) = cos v",
                ],
                "correct": "s(t) = s₀ + ∫₀ᵗ v(τ)dτ",
                "explanation": "Position change equals the time integral of velocity.",
            },
            "answers": [
                make_answer(f"s({time_value})", answer_value, "m"),
            ],
            "solution": [
                ("latex", r"s(t)=s_0+\int_0^t v(\tau)\,d\tau"),
                ("latex", rf"s(t)={s0}+\int_0^t\left({sp.latex(velocity.subs(t, sp.Symbol('tau')))}\right)\,d\tau"),
                ("latex", rf"s(t)={sp.latex(position)}"),
                ("latex", rf"s({time_value})={sp.latex(answer_value)}\ \text{{m}}"),
                ("text", "The initial position supplies the integration constant."),
            ],
            "signature": f"I4:{a}:{b}:{s0}:{time_value}",
            "diagram": None,
            "teaching_point": "Integrating velocity gives displacement. Add the initial position to obtain absolute position.",
        }


    if level == 5:
        trig_kind = RNG.choice(["sin", "cos"])
        amplitude = RNG.choice([2, 3, 4, 5, 6])
        frequency = RNG.choice([1, 2, 3, 4])

        target_angle = RNG.choice(
            [
                sp.pi / 6,
                sp.pi / 4,
                sp.pi / 3,
                sp.pi / 2,
            ]
        )

        upper = sp.simplify(target_angle / frequency)

        if trig_kind == "sin":
            expr = amplitude * sp.sin(frequency * x)
            antiderivative = -sp.Rational(amplitude, frequency) * sp.cos(
                frequency * x
            )
            rule_text = (
                r"\int A\sin(kx)\,dx="
                r"-\frac{A}{k}\cos(kx)+C"
            )
            correct_option = "∫A sin(kx)dx = -(A/k) cos(kx) + C"
            options = [
                correct_option,
                "∫A sin(kx)dx = A k cos(kx) + C",
                "∫A sin(kx)dx = (A/k) sin(kx) + C",
                "∫A sin(kx)dx = A sec²(kx) + C",
            ]
        elif trig_kind == "cos":
            expr = amplitude * sp.cos(frequency * x)
            antiderivative = sp.Rational(amplitude, frequency) * sp.sin(
                frequency * x
            )
            rule_text = (
                r"\int A\cos(kx)\,dx="
                r"\frac{A}{k}\sin(kx)+C"
            )
            correct_option = "∫A cos(kx)dx = (A/k) sin(kx) + C"
            options = [
                "∫A cos(kx)dx = -(A/k) cos(kx) + C",
                correct_option,
                "∫A cos(kx)dx = A k sin(kx) + C",
                "∫A cos(kx)dx = -(A/k) ln|cos(kx)| + C",
            ]

        exact_value = sp.simplify(
            antiderivative.subs(x, upper) - antiderivative.subs(x, 0)
        )

        return {
            "title": "Integrate sine or cosine",
            "difficulty": "Moderate",
            "prompt": (
                "Evaluate the definite trigonometric integral. The angle "
                "arguments are in radians."
            ),
            "display_equation": (
                rf"\int_0^{{{sp.latex(upper)}}}"
                rf"\left({sp.latex(expr)}\right)\,dx"
            ),
            "formula_question": {
                "question": "Which antiderivative is correct for this function?",
                "options": options,
                "correct": correct_option,
                "explanation": (
                    "Use the trigonometric antiderivative and divide by the "
                    "inside coefficient k. This reverses the chain rule."
                ),
            },
            "answers": [
                make_answer("Integral value", exact_value),
            ],
            "solution": [
                (
                    "text",
                    "Trigonometric integration uses radians. The inside function is "
                    f"{frequency}x, so the antiderivative contains a factor "
                    f"1/{frequency}.",
                ),
                ("latex", rule_text),
                (
                    "latex",
                    rf"\int\left({sp.latex(expr)}\right)\,dx"
                    rf"={sp.latex(antiderivative)}+C",
                ),
                (
                    "latex",
                    rf"\left[{sp.latex(antiderivative)}\right]_0^"
                    rf"{{{sp.latex(upper)}}}",
                ),
                (
                    "latex",
                    rf"={sp.latex(exact_value)}"
                    rf"\approx {float(exact_value):.5f}",
                ),
            ],
            "signature": (
                f"I5:{trig_kind}:{amplitude}:{frequency}:"
                f"{sp.srepr(target_angle)}"
            ),
            "diagram": None,
            "teaching_point": (
                "Integration reverses the chain rule: a function of kx normally "
                "introduces a factor 1/k in the antiderivative."
            ),
        }

    # Level 6: integrate sinusoidal acceleration to velocity.
    motion_kind = RNG.choice(["sin", "cos"])
    amplitude = RNG.choice([2, 3, 4, 5])
    omega = RNG.choice([1, 2, 3, 4])
    v0 = RNG.randint(-4, 6)
    target_angle = RNG.choice(
        [
            sp.pi / 6,
            sp.pi / 4,
            sp.pi / 3,
            sp.pi / 2,
        ]
    )
    time_value = sp.simplify(target_angle / omega)

    if motion_kind == "sin":
        acceleration = amplitude * sp.sin(omega * t)
    else:
        acceleration = amplitude * sp.cos(omega * t)

    tau = sp.symbols("tau", real=True)
    velocity = sp.simplify(
        v0
        + sp.integrate(
            acceleration.subs(t, tau),
            (tau, 0, t),
        )
    )
    velocity_value = sp.simplify(velocity.subs(t, time_value))

    return {
        "title": "Integrate sinusoidal acceleration",
        "difficulty": "Challenging",
        "prompt": (
            f"The acceleration function is given and v(0) = {v0} m/s. "
            "Find the velocity at the stated time."
        ),
        "display_equation": (
            rf"a(t)={sp.latex(acceleration)}\ \text{{m/s}}^2,"
            rf"\qquad t={sp.latex(time_value)}\ \text{{s}}"
        ),
        "formula_question": {
            "question": "Which initial-condition form should be used?",
            "options": [
                "v(t) = v₀ + ∫₀ᵗ a(τ)dτ",
                "v(t) = da/dt",
                "v(t) = a(t)/t",
                "v(t) = ∫₀ᵗ v(τ)dτ",
            ],
            "correct": "v(t) = v₀ + ∫₀ᵗ a(τ)dτ",
            "explanation": (
                "The velocity change is the integral of acceleration. Add the "
                "known initial velocity."
            ),
        },
        "answers": [
            make_answer(
                f"Velocity at t = {sp.latex(time_value)}",
                velocity_value,
                "m/s",
            ),
        ],
        "solution": [
            (
                "text",
                "Use a dummy integration variable τ so the upper limit can remain t.",
            ),
            ("latex", r"v(t)=v_0+\int_0^t a(\tau)\,d\tau"),
            (
                "latex",
                rf"v(t)={v0}+\int_0^t"
                rf"\left({sp.latex(acceleration.subs(t, tau))}\right)d\tau",
            ),
            ("latex", rf"v(t)={sp.latex(velocity)}"),
            (
                "latex",
                rf"v({sp.latex(time_value)})={sp.latex(velocity_value)}"
                rf"\approx {float(velocity_value):.5f}\ \text{{m/s}}",
            ),
        ],
        "signature": (
            f"I6:{motion_kind}:{amplitude}:{omega}:{v0}:"
            f"{sp.srepr(target_angle)}"
        ),
        "diagram": None,
        "teaching_point": (
            "Integrating acceleration gives the change in velocity, not the final "
            "velocity by itself. The initial velocity must be included."
        ),
    }



# -----------------------------------------------------------------------------
# Straight-line equations: exact arithmetic, generated graphs and worked steps.
# All plots below are drawn with Matplotlib; no external images are required.
# -----------------------------------------------------------------------------
def line_equation_latex(m, c, x_name="x", y_name="y", vertical=None):
    if vertical is not None:
        return rf"{x_name}={sp.latex(vertical)}"
    return rf"{y_name}={sp.latex(sp.sympify(m) * sp.Symbol(x_name) + c)}"


def _line_input_fraction(raw):
    compact = "".join(str(raw).strip().replace("−", "-").split())
    if "/" in compact:
        numerator, denominator = compact.split("/")
        return Fraction(int(numerator), int(denominator))
    return Fraction(compact)


def line_number_input(raw):
    """Accept a decimal or a simple fraction, without evaluating Python code."""
    value = str(raw).strip().replace("−", "-")
    if len(value) > 64 or not re.fullmatch(
        r"(?:[+-]?\d+\s*/\s*[+-]?\d+|[+-]?(?:\d+(?:\.\d*)?|\.\d+))", value
    ):
        raise ValueError("Enter a number such as -2, 0.75 or -3/4.")
    try:
        number = float(_line_input_fraction(value))
    except (ValueError, ZeroDivisionError, OverflowError):
        raise ValueError("Use a valid number or fraction with a nonzero denominator.") from None
    if not math.isfinite(number) or abs(number) > 1e9:
        raise ValueError("Enter a finite number with magnitude at most 1,000,000,000.")
    return number


def line_answer(label, value, unit=""):
    answer = make_answer(label, value, unit)
    # Four decimal places are sufficient, but a visibly different slope is not.
    answer["tolerance"] = 0.0001
    return answer


def _line_tick_step(span):
    target = max(float(span) / 12, 1)
    power = 10 ** math.floor(math.log10(target))
    return next(mult * power for mult in (1, 2, 5, 10) if mult * power >= target)


def straight_line_figure(data, stage="question", candidate=None):
    """Draw known information separately from solution overlays and attempts."""
    solved = stage in ("slope", "complete")
    points = list(data.get("points", []))
    visible = points if solved else points[:data.get("visible_points", len(points))]
    m, c = data.get("m"), data.get("c")
    vertical = data.get("vertical")
    x_name, y_name = data.get("x_symbol", "x"), data.get("y_symbol", "y")

    xs = [0.0] + [float(p[0]) for p in points]
    ys = [0.0] + [float(p[1]) for p in points]
    if c is not None:
        ys.append(float(c))
    if data.get("reference"):
        ref_m, ref_c = data["reference"]
        ys += [float(ref_c), float(ref_m * points[0][0] + ref_c)]
    if vertical is not None:
        xs.append(float(vertical))
    xspan, yspan = max(max(xs) - min(xs), 6), max(max(ys) - min(ys), 6)
    xlim = (math.floor(min(xs) - 0.2 * xspan - 1), math.ceil(max(xs) + 0.2 * xspan + 1))
    ylim = (math.floor(min(ys) - 0.22 * yspan - 1), math.ceil(max(ys) + 0.22 * yspan + 1))
    if data.get("nonnegative_x"):
        xlim = (0, xlim[1])
    xlim = data.get("x_limits", xlim)
    ylim = data.get("y_limits", ylim)

    fig, ax = plt.subplots(figsize=(8.2, 5.6), facecolor="white")
    ax.set_facecolor("#f8fafc")
    ax.set_xlim(*xlim)
    ax.set_ylim(*ylim)
    xstep = _line_tick_step(xlim[1] - xlim[0])
    ystep = _line_tick_step(ylim[1] - ylim[0])
    xticks = np.arange(math.ceil(xlim[0] / xstep) * xstep, xlim[1] + 0.01, xstep)
    yticks = np.arange(math.ceil(ylim[0] / ystep) * ystep, ylim[1] + 0.01, ystep)
    ax.set_xticks(xticks)
    ax.set_yticks(yticks)
    if xstep > 1:
        ax.set_xticks(np.arange(xlim[0], xlim[1] + 0.01, 1), minor=True)
    if ystep > 1:
        ax.set_yticks(np.arange(ylim[0], ylim[1] + 0.01, 1), minor=True)
    ax.grid(which="major", color="#cbd5e1", linewidth=0.8)
    ax.grid(which="minor", color="#e2e8f0", linewidth=0.45)
    ax.axhline(0, color="#334155", linewidth=1.2)
    ax.axvline(0, color="#334155", linewidth=1.2)
    ax.set_xlabel(data.get("x_label", "x"), fontsize=12, color="#172033")
    ax.set_ylabel(data.get("y_label", "y"), fontsize=12, color="#172033")
    ax.tick_params(colors="#334155", labelsize=10)
    for spine in ax.spines.values():
        spine.set_color("#94a3b8")
    domain = np.linspace(*xlim, 300)

    if data.get("reference"):
        ref_m, ref_c = data["reference"]
        ax.plot(domain, float(ref_m) * domain + float(ref_c), color="#7c3aed",
                linestyle="--", linewidth=2, label="Reference line")

    if solved or data.get("given_line", False):
        label = "Recovered line" if solved else "Given line"
        if vertical is not None:
            ax.axvline(float(vertical), color="#2563eb", linewidth=2.5, label=label)
        else:
            ax.plot(domain, float(m) * domain + float(c), color="#2563eb",
                    linewidth=2.5, label=label)

    for index, (px, py) in enumerate(visible):
        name = chr(ord("A") + index)
        ax.scatter([float(px)], [float(py)], s=68, color="#be123c", zorder=5)
        label = name
        if solved or data.get("label_coordinates", True):
            label = rf"${name}({sp.latex(px)},\ {sp.latex(py)})$"
        ax.annotate(label, (float(px), float(py)), xytext=(8, 13 if index % 2 == 0 else -21),
                    textcoords="offset points", fontsize=11, color="#881337", zorder=7,
                    bbox=dict(boxstyle="round,pad=0.2", facecolor="white", alpha=0.85, edgecolor="none"))

    if solved and vertical is None and len(points) >= 2:
        (x1, y1), (x2, y2) = points[:2]
        dx, dy = x2 - x1, y2 - y1
        ax.plot([float(x1), float(x2), float(x2)], [float(y1), float(y1), float(y2)],
                color="#d97706", linestyle="--", linewidth=2, zorder=4)
        ax.annotate(rf"$\Delta {x_name}={sp.latex(dx)}$",
                    (float((x1 + x2) / 2), float(y1)), xytext=(0, -29),
                    textcoords="offset points", ha="center", color="#92400e", fontsize=12,
                    bbox=dict(facecolor="white", edgecolor="none", alpha=0.9, pad=2))
        if dy != 0:
            ax.annotate(rf"$\Delta {y_name}={sp.latex(dy)}$",
                        (float(x2), float((y1 + y2) / 2)), xytext=(9, 0),
                        textcoords="offset points", va="center", color="#92400e", fontsize=12,
                        bbox=dict(facecolor="white", edgecolor="none", alpha=0.9, pad=2))
        else:
            ax.annotate(rf"$\Delta {y_name}=0$", (float(x2), float(y1)), xytext=(8, 14),
                        textcoords="offset points", color="#92400e", fontsize=12)

    if stage == "complete" and vertical is None:
        ax.scatter([0], [float(c)], s=90, marker="s", color="#059669", zorder=6,
                   label=rf"Intercept $c={sp.latex(c)}$")

    if candidate is not None:
        if candidate.get("vertical") is not None:
            ax.axvline(candidate["vertical"], color="#ea580c", linestyle=":",
                       linewidth=2.6, label="Your equation")
        else:
            ax.plot(domain, candidate["m"] * domain + candidate["c"], color="#ea580c",
                    linestyle=":", linewidth=2.6, label="Your equation")

    if stage == "complete":
        equation = line_equation_latex(m, c, x_name, y_name, vertical)
        title = rf"Recovered equation: ${equation}$"
    elif stage == "slope":
        title = "Read the signed changes: vertical change / horizontal change"
    else:
        title = data.get("graph_title", "Use the axis values to read the known information")
    ax.set_title(title, fontsize=12, color="#172033", pad=14)
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(handles, labels, loc="best", fontsize=9, facecolor="white", framealpha=0.94)
    fig.text(0.5, 0.015, "Use axis values: horizontal and vertical scales may differ. Minor grid spacing, when shown: 1 unit.",
             ha="center", fontsize=9, color="#475569")
    # Fixed margins keep axis labels inside the canvas even when annotations
    # sit near an axis boundary; they also give every learning graph room.
    fig.subplots_adjust(left=0.14, right=0.97, bottom=0.16, top=0.90)
    ax.yaxis.set_label_coords(-0.10, 0.5)
    return fig


def show_straight_line(data, stage="question", candidate=None):
    fig = straight_line_figure(data, stage, candidate)
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


def _line_formula_question(correct, explanation):
    options = [correct, "Use y/x from any single point, even if the line misses the origin",
               "Use horizontal change divided by vertical change",
               "Assume the vertical-axis intercept is always zero"]
    RNG.shuffle(options)
    return {"question": "Which method fits the information given?", "options": options,
            "correct": correct, "explanation": explanation}


def _line_gradient_steps(points, x_name="x", y_name="y"):
    (x1, y1), (x2, y2) = points[:2]
    dx, dy = sp.simplify(x2 - x1), sp.simplify(y2 - y1)
    m = sp.simplify(dy / dx)
    return [
        ("heading", "2. Calculate the gradient from changes"),
        ("text", "Move from A to B. Subtract the coordinates in the same order in the numerator and denominator. The gradient is vertical change divided by horizontal change."),
        ("latex", rf"\Delta {x_name}=({sp.latex(x2)})-({sp.latex(x1)})={sp.latex(dx)}"),
        ("latex", rf"\Delta {y_name}=({sp.latex(y2)})-({sp.latex(y1)})={sp.latex(dy)}"),
        ("latex", rf"m=\frac{{\Delta {y_name}}}{{\Delta {x_name}}}"
                  rf"=\frac{{({sp.latex(y2)})-({sp.latex(y1)})}}{{({sp.latex(x2)})-({sp.latex(x1)})}}"
                  rf"=\frac{{{sp.latex(dy)}}}{{{sp.latex(dx)}}}={sp.latex(m)}"),
        ("text", "A positive gradient rises as you move right; a negative gradient falls. A zero gradient gives a horizontal line. Use the numbered axes, rather than the apparent angle on the screen."),
        ("line_plot", "slope"),
    ]


def generate_straight_line(level):
    """Generate consistent exact data, answer checks and a matching explanation."""
    slopes = [sp.Rational(n, d) for n, d in [(-3, 1), (-2, 1), (-1, 1), (-1, 2),
                                            (1, 2), (1, 1), (2, 1), (3, 1),
                                            (2, 3), (-2, 3), (3, 2), (-3, 2)]]
    m = RNG.choice(slopes)
    c = sp.Integer(RNG.randint(-5, 5))
    denominator = int(sp.denom(m))
    x1 = sp.Integer(RNG.choice([-3, -2, -1, 1, 2]) * denominator)
    x2 = x1 + denominator * RNG.choice([1, 2, 3])
    # Keep the first graph approachable: two nonzero x-values and integer points.
    if level == 1:
        x1, x2 = -sp.Integer(denominator), sp.Integer(denominator)
    points = [(x1, m * x1 + c), (x2, m * x2 + c)]
    data = {"m": m, "c": c, "vertical": None, "points": points,
            "given_line": level == 1, "label_coordinates": level != 1}
    prefix = []
    table = None
    form_answer = None
    x_name, y_name = "x", "y"
    m_unit = c_unit = ""

    if level == 1:
        title = "Recover a line equation from its graph"
        prompt = "Read the coordinates of the marked points A and B from the graph. Find the gradient m and the intercept c, then write the complete equation y = mx + c. The equation is deliberately hidden on the graph."
        first_step = "Read two exact grid intersections on the blue line. A coordinate pair is written (horizontal value, vertical value). The marked points have integer coordinates."
        method = "Read two points, use change in y / change in x, then find c"
        display = None
    elif level == 2:
        title = "Recover a line equation from two points"
        prompt = "Find the equation of the straight line through the two points. Calculate m and c and assemble y = mx + c. The points are shown without the joining line so you can construct it yourself."
        first_step = "Two distinct points determine one straight line. Label them A = (x1, y1) and B = (x2, y2); keep each x-value paired with its own y-value."
        method = "Calculate m from the two points, then use c = y1 - m*x1"
        display = rf"A=({sp.latex(points[0][0])},{sp.latex(points[0][1])}),\quad B=({sp.latex(points[1][0])},{sp.latex(points[1][1])})"
    elif level == 3:
        title = "Recover a line equation from one point and its gradient"
        prompt = "The gradient and one point are given. Find the missing intercept c and write y = mx + c. Enter the given gradient as m as well."
        first_step = "The gradient is already known. One point fixes the line's position; a gradient alone would leave infinitely many parallel lines."
        method = "Use y - y1 = m(x - x1), or substitute the point into y = mx + c"
        data["visible_points"] = 1
        display = rf"m={sp.latex(m)},\qquad A=({sp.latex(x1)},{sp.latex(points[0][1])})"
    elif level == 4:
        a = sp.Integer(RNG.choice([i for i in range(-8, 9) if i]))
        b = sp.Integer(RNG.choice([i for i in range(-7, 8) if i]))
        m, c = -b / a, b
        points = sorted([(a, sp.Integer(0)), (sp.Integer(0), b)])
        data.update(m=m, c=c, points=points)
        title = "Recover a line equation from its intercepts"
        prompt = "The line crosses the x-axis at the given x-intercept and the y-axis at the given y-intercept. Find m and c and write y = mx + c."
        display = rf"x\text{{-intercept}}={a},\qquad y\text{{-intercept}}={b}"
        first_step = f"An x-intercept has y = 0, so the first intercept is ({a}, 0). A y-intercept has x = 0, so the other is (0, {b}). An intercept is a coordinate on an axis, not the gradient."
        method = "Convert the intercepts to (a, 0) and (0, b), then calculate m"
        prefix = [("text", "Here c is known immediately: it is the y-coordinate where x = 0. The intercept form is another useful route; both intercepts in this question are nonzero."),
                  ("latex", rf"\frac{{x}}{{({a})}}+\frac{{y}}{{({b})}}=1"
                            rf"\quad\Longrightarrow\quad y={sp.latex(m * x + c)}")]
    elif level == 5:
        table_x = [sp.Integer(i * denominator) for i in (-2, -1, 0, 1, 2)]
        table_y = [m * px + c for px in table_x]
        points = [(table_x[0], table_y[0]), (table_x[1], table_y[1])]
        data.update(points=points, visible_points=2)
        table = {"x": [str(v) for v in table_x], "y": [str(v) for v in table_y]}
        title = "Recover a line equation from a table"
        prompt = "The table contains exact values, with no measurement noise. Check that the rate of change is constant, then find m and c and write y = mx + c. The first two table rows are marked on the graph."
        first_step = "Take differences between neighbouring rows. Equal changes in x must give equal changes in y for these exact data to lie on one straight line."
        method = "Check that change in y / change in x is constant, then find c"
        display = None
        dx, dy = table_x[1] - table_x[0], table_y[1] - table_y[0]
        prefix = [("text", "For every neighbouring pair of rows, the changes are the same. A larger step in x must be divided out; the change in y by itself is not necessarily the gradient."),
                  ("latex", rf"\Delta x={sp.latex(dx)},\qquad\Delta y={sp.latex(dy)},\qquad\frac{{\Delta y}}{{\Delta x}}={sp.latex(m)}\quad\text{{for all four intervals}}")]
    elif level == 6:
        relation = RNG.choice(["parallel", "perpendicular"])
        ref_m = RNG.choice(slopes)
        m = ref_m if relation == "parallel" else -1 / ref_m
        ref_c = c + RNG.choice([-4, -2, 2, 4])
        x1 = sp.Integer(RNG.choice([-3, -2, -1, 1, 2, 3]))
        x2 = x1 + int(sp.denom(m)) * 2
        points = [(x1, m * x1 + c), (x2, m * x2 + c)]
        data.update(m=m, points=points, visible_points=1, reference=(ref_m, ref_c), relation=relation)
        title = f"A {relation} line through a point"
        prompt = f"Find the equation of the line through A that is {relation} to the purple reference line. The required line is not drawn yet. Enter its m and c."
        display = rf"\text{{Reference: }}y={sp.latex(ref_m * x + ref_c)},\qquad A=({sp.latex(x1)},{sp.latex(points[0][1])})"
        first_step = "Read the reference gradient from the coefficient of x. Its intercept belongs to the reference line; the new line must use the given point to find its own intercept."
        method = "Use the same gradient, then substitute A to find c" if relation == "parallel" else "Use the negative reciprocal gradient, then substitute A to find c"
        prefix = [("heading", "2. Find the required gradient"),
                  ("text", "Parallel lines have equal gradients. The different intercepts keep these two lines distinct." if relation == "parallel" else "For two nonvertical perpendicular lines with nonzero gradients, the gradients multiply to -1. Take the negative reciprocal, not just the negative."),
                  ("latex", rf"m=m_{{\rm ref}}={sp.latex(m)}" if relation == "parallel" else
                   rf"m\,m_{{\rm ref}}=-1\quad\Longrightarrow\quad m=-\frac{{1}}{{m_{{\rm ref}}}}=-\frac{{1}}{{({sp.latex(ref_m)})}}={sp.latex(m)}"),
                  ("text", "The axes can have different screen scales, so perpendicular lines may not look like a right angle on this display. The gradient calculation is the check.")]
    elif level == 7:
        vertical = RNG.choice([True, False])
        k = sp.Integer(RNG.randint(-6, 6))
        u1, u2 = sp.Integer(RNG.randint(-5, -1)), sp.Integer(RNG.randint(1, 5))
        if vertical:
            m, c = None, None
            points = [(k, u1), (k, u2)]
            data.update(m=None, c=None, vertical=k)
        else:
            m, c = sp.Integer(0), k
            points = [(u1, k), (u2, k)]
            data.update(m=m, c=c)
        data.update(points=points, given_line=True, label_coordinates=False)
        title = "Horizontal or vertical: choose the correct form"
        prompt = "Read the marked points from the graph. Choose the correct equation form, then enter its constant k. A vertical line cannot be written as y = mx + c with a finite gradient."
        display = None
        form_answer = "x = k (vertical)" if vertical else "y = k (horizontal)"
        method = "Check which coordinate stays constant before choosing x = k or y = k"
        first_step = "Read both marked points and check which coordinate stays constant. The line is vertical if x stays the same, and horizontal if y stays the same."
        dx, dy = points[1][0] - points[0][0], points[1][1] - points[0][1]
        equation = line_equation_latex(m, c, vertical=k if vertical else None)
        solution = [
            ("heading", "1. Read the coordinates"), ("text", first_step),
            ("latex", rf"A=({points[0][0]},{points[0][1]}),\qquad B=({points[1][0]},{points[1][1]})"),
            ("heading", "2. Calculate the changes"),
            ("latex", rf"\Delta x=({points[1][0]})-({points[0][0]})={dx},\qquad\Delta y=({points[1][1]})-({points[0][1]})={dy}"),
            ("text", "The horizontal change is zero. The slope formula would divide by zero, so the gradient is undefined; it is not zero and should not be entered as an ordinary number." if vertical else "The vertical change is zero and the horizontal change is nonzero. Therefore m = 0; the y-coordinate never changes."),
            ("latex", rf"m=\frac{{{dy}}}{{0}}\quad\text{{is undefined}}" if vertical else rf"m=\frac{{0}}{{{dx}}}=0"),
            ("heading", "3. Write the coordinate that remains constant"),
            ("text", f"Every point has x = {k}, regardless of y." if vertical else f"Every point has y = {k}, regardless of x."),
            ("latex", rf"\boxed{{{equation}}}"),
            ("line_plot", "complete"),
            ("heading", "4. Verify both points"),
            ("text", f"Both marked points have {'x' if vertical else 'y'} = {k}, so both satisfy the equation. " +
             ("A vertical line is not a function y(x), because one x-value has many y-values." if vertical else "A horizontal line is a function y(x) with zero gradient.")),
            ("text", "Two identical points would not determine a unique line. The generated points here are distinct."),
        ]
        return {"title": title, "difficulty": "Essential special cases", "prompt": prompt,
                "display_equation": display, "formula_question": _line_formula_question(method, first_step),
                "answers": [line_answer("Constant k", k)], "line_form_answer": form_answer,
                "line_data": data, "solution": solution, "diagram": ("straight_line", data),
                "signature": f"SL7:{vertical}:{k}:{u1}:{u2}",
                "teaching_point": "Horizontal: y = k and m = 0. Vertical: x = k and m is undefined. Never divide by zero."}
    elif level == 8:
        aa = sp.Integer(RNG.choice([-6, -4, -3, -2, -1, 1, 2, 3, 4, 6]))
        bb = sp.Integer(RNG.choice([-5, -3, -2, -1, 1, 2, 3, 5]))
        cc = sp.Integer(RNG.randint(-9, 9))
        m, c = -aa / bb, -cc / bb
        points = [(sp.Integer(0), c), (abs(bb), m * abs(bb) + c)]
        data.update(m=m, c=c, points=points, visible_points=0, given_line=True,
                    general_coefficients=(aa, bb, cc))
        title = "Convert a general equation to y = mx + c"
        prompt = "Rearrange the given equation to make y the subject. Identify the gradient m and the y-intercept c. The graph shows the same line."
        display = rf"{sp.latex(aa * x + bb * sp.Symbol('y') + cc)}=0"
        first_step = "The general form is Ax + By + C = 0. Here B is nonzero, so you can isolate y. Both terms on the other side must be divided by B."
        method = "Isolate B*y, then divide every term by B"
        prefix = [("heading", "2. Make y the subject"),
                  ("latex", rf"({bb})y={sp.latex(-aa * x - cc)}"),
                  ("text", f"Divide the entire right-hand side by B = {bb}. Keep the sign of B; do not divide only the x-term."),
                  ("latex", rf"y=\frac{{{sp.latex(-aa * x - cc)}}}{{({bb})}}={sp.latex(m * x + c)}"),
                  ("latex", rf"m=-\frac{{A}}{{B}}={sp.latex(m)},\qquad c=-\frac{{C}}{{B}}={sp.latex(c)}")]
    elif level == 9:
        scenario = RNG.choice(["motion", "load"])
        if scenario == "motion":
            x_name, y_name = "t", "v"
            m = sp.Rational(RNG.choice([-3, -2, -1, 1, 2, 3]), RNG.choice([1, 2]))
            c = sp.Integer(RNG.randint(2, 8))
            x1, x2 = sp.Integer(2), sp.Integer(RNG.choice([4, 6, 8]))
            points = [(x1, m * x1 + c), (x2, m * x2 + c)]
            data.update(m=m, c=c, points=points, given_line=True,
                        x_symbol="t", y_symbol="v", x_label="Time t (s)",
                        y_label="Velocity v (m/s)", nonnegative_x=True)
            title = "Recover a velocity-time equation"
            prompt = "The velocity-time graph is straight over the displayed time interval. Read A and B and find v(t) = mt + c. Give m in m/s² and c in m/s, and explain their physical meaning."
            first_step = "The horizontal axis is time t in seconds, and the vertical axis is velocity v in m/s. The same straight-line method applies with t instead of x and v instead of y."
            m_unit, c_unit = "m/s²", "m/s"
            physical = "Here m is the constant acceleration (change in velocity per second), and c is the initial velocity v(0). A negative velocity means motion in the negative direction; it is not a negative speed. Use this model only over the interval where the graph is straight."
        else:
            x_name, y_name = "d", "F"
            m, c = sp.Integer(RNG.randint(1, 5)), sp.Integer(RNG.choice([0, 2, 4, 6]))
            x1, x2 = sp.Integer(1), sp.Integer(RNG.choice([3, 4, 5]))
            points = [(x1, m * x1 + c), (x2, m * x2 + c)]
            data.update(m=m, c=c, points=points, given_line=True,
                        x_symbol="d", y_symbol="F", x_label="Extension d (mm)",
                        y_label="Force F (N)", nonnegative_x=True)
            title = "Recover a force-extension equation"
            prompt = "The force-extension graph is straight over the displayed range. Read A and B and find F(d) = md + c, using extension d in millimetres. Give m in N/mm and c in N."
            first_step = "The horizontal axis is extension d in millimetres, and the vertical axis is force F in newtons. Keep these units throughout the gradient calculation."
            m_unit, c_unit = "N/mm", "N"
            physical = "Here m is the stiffness over this linear range, and c is the force at zero plotted extension (an offset or preload). A force-extension line need not pass through the origin. To convert stiffness from N/mm to N/m, multiply by 1000."
        method = "Divide the change in vertical-axis quantity by the change in horizontal-axis quantity, retaining units"
        display = None
        prefix = [("text", f"For this graph the model is {y_name} = m{x_name} + c. The letters change, but the method does not.")]
    else:
        raise ValueError("Unknown straight-line level")

    solution = [("heading", "1. Identify the known information"), ("text", first_step)] + prefix
    if level not in (3, 6, 8):
        solution += [("latex", rf"A=({sp.latex(points[0][0])},{sp.latex(points[0][1])}),\quad B=({sp.latex(points[1][0])},{sp.latex(points[1][1])})")]
        solution += _line_gradient_steps(points, x_name, y_name)
    elif level == 3:
        solution += [("heading", "2. Use the given gradient"),
                     ("latex", rf"m={sp.latex(m)},\qquad {y_name}-{y_name}_1=m({x_name}-{x_name}_1)"),
                     ("text", "Point-gradient form describes the line through the given point. Expand it, or use c = y1 - m*x1 to reach slope-intercept form.")]

    px, py = points[0]
    product = sp.simplify(m * px)
    solution += [
        ("heading", "3. Find or confirm the intercept"),
        ("text", f"The intercept c is the value of {y_name} when {x_name} = 0. It is not generally the {y_name}-coordinate of A. Substitute A and the gradient into the line equation, then isolate c."),
        ("latex", rf"{y_name}=m{x_name}+c\quad\Longrightarrow\quad c={y_name}-m{x_name}"),
        ("latex", rf"c=({sp.latex(py)})-({sp.latex(m)})({sp.latex(px)})=({sp.latex(py)})-({sp.latex(product)})={sp.latex(c)}"),
        ("text", "Subtracting a negative quantity adds its magnitude; the brackets preserve the signs. If the graph includes x = 0, you can also read c directly at the vertical-axis crossing."),
        ("heading", "4. Assemble the complete equation"),
        ("text", "Replace m and c by their values. Keep the coordinate variables in the equation: a numerical gradient alone is not a line equation."),
        ("latex", rf"\boxed{{{line_equation_latex(m, c, x_name, y_name)}}}"),
        ("line_plot", "complete"),
        ("heading", "5. Substitute points to check the result"),
    ]
    if level in (3, 6):
        solution += [("text", "Check the supplied point A. B on the recovered graph is an additional constructed point, not a second point supplied in the question.")]
    elif level == 8:
        solution += [("text", "The two plotted check points below were constructed from the rearranged equation. Substituting either into the original general equation also gives zero.")]
    else:
        solution += [("text", "Each known point must reproduce its y-value. A wrong sign or an incorrect intercept will fail this check.")]
    for index, (px, py) in enumerate(points):
        point_name = chr(ord("A") + index)
        solution += [("latex", rf"{point_name}:\quad ({sp.latex(m)})({sp.latex(px)})+({sp.latex(c)})={sp.latex(sp.simplify(m * px + c))}={sp.latex(py)}\quad\checkmark")]
        if level == 8:
            solution += [("latex", rf"({aa})({sp.latex(px)})+({bb})({sp.latex(py)})+({cc})=0\quad\checkmark")]
    if level == 9:
        solution += [("heading", "6. Interpret the gradient and intercept with units"),
                     ("latex", rf"[m]=\frac{{[{y_name}]}}{{[{x_name}]}},\qquad [c]=[{y_name}]"),
                     ("text", f"m = {m} {m_unit}; c = {c} {c_unit}. {physical}")]
    if level == 5:
        solution += [("text", "All five table rows satisfy the same equation. If measured data do not have a constant rate, an exact line may be inappropriate; a fitted line is a separate modelling task.")]

    learning_point = "Use changes, keep the subtraction order consistent, and check the intercept by setting the horizontal variable to zero. Both points must satisfy the recovered equation."
    if level == 6:
        learning_point = "Parallel gradients are equal. Nonzero perpendicular gradients are negative reciprocals. A point on the required line determines its intercept."
    elif level == 8:
        learning_point = "For Ax + By + C = 0 with B nonzero, m = -A/B and c = -C/B. If B = 0 and A is nonzero, the line is vertical: x = -C/A."
    elif level == 9:
        learning_point = physical
    return {
        "title": title, "difficulty": "Foundation" if level <= 3 else "Developing application",
        "prompt": prompt, "display_equation": display,
        "formula_question": _line_formula_question(method, first_step),
        "answers": [line_answer("Gradient m", m, m_unit), line_answer("Intercept c", c, c_unit)],
        "solution": solution, "signature": f"SL{level}:{m}:{c}:{points}:{data.get('reference')}:{x_name}",
        "diagram": ("straight_line", data), "line_data": data, "table": table,
        "teaching_point": learning_point,
    }


def render_line_learning():
    st.markdown("### A line equation tells you how the coordinates are connected")
    st.latex(r"y=mx+c,\qquad m=\frac{y_2-y_1}{x_2-x_1},\qquad c=y_1-mx_1")
    st.markdown("**x** is the horizontal coordinate; **y** is the vertical coordinate. "
                "The **gradient m** tells you how much y changes for each one-unit increase in x. "
                "The **intercept c** is the y-value where x = 0. It can be positive, negative or zero.")
    st.markdown("### Explore the gradient and intercept")
    left, right = st.columns(2)
    with left:
        explore_m = st.slider("Gradient m: tilt the line", -3.0, 3.0, 1.0, 0.5, key="line_explore_m")
    with right:
        explore_c = st.slider("Intercept c: move the line vertically", -4, 4, 2, key="line_explore_c")
    example_m, example_c = sp.Rational(str(explore_m)), sp.Integer(explore_c)
    example = {"m": example_m, "c": example_c, "points": [(sp.Integer(0), example_c),
               (sp.Integer(2), 2 * example_m + example_c)], "given_line": True,
               "x_limits": (-4, 4), "y_limits": (-12, 12)}
    show_straight_line(example, "complete")
    st.markdown("Change **m** while holding c fixed: the line rotates about its vertical-axis intercept. "
                "Change **c** while holding m fixed: the line shifts vertically and stays parallel to its previous position.")
    st.markdown("### Recover an equation: five steps")
    st.markdown("1. Read the axis labels and units, then identify two exact points if available.\n"
                "2. Calculate the gradient using **vertical change / horizontal change**.\n"
                "3. Substitute one point into **c = y − mx**.\n"
                "4. Write the complete equation, keeping x and y as variables.\n"
                "5. Substitute both points and check the gradient's sign and units.")
    st.markdown("### Worked example with a falling line")
    st.latex(r"A=(-2,5),\quad B=(4,-1)")
    st.latex(r"m=\frac{(-1)-5}{4-(-2)}=\frac{-6}{6}=-1")
    st.latex(r"c=5-(-1)(-2)=5-2=3\quad\Longrightarrow\quad\boxed{y=-x+3}")
    st.latex(r"x=-2:\ y=-(-2)+3=5;\qquad x=4:\ y=-4+3=-1")
    st.markdown("The negative gradient means y falls by 1 each time x increases by 1. "
                "The line crosses the y-axis at (0, 3). Notice how subtracting a negative x-coordinate changes the denominator.")
    st.markdown("### Choose a method from the information available")
    st.markdown(
        "| Given information | Method |\n|---|---|\n"
        "| Graph | Read two well-separated exact points; use the numbered axis scales. |\n"
        "| Two points | $m=(y_2-y_1)/(x_2-x_1)$, then $c=y_1-mx_1$. |\n"
        "| One point and gradient | $y-y_1=m(x-x_1)$, or substitute to find $c$. |\n"
        "| Axis intercepts $a$ and $b$, both nonzero | Use $(a,0)$ and $(0,b)$; equivalently $x/a+y/b=1$. |\n"
        "| Exact table | Check the same rate $\\Delta y/\\Delta x$ across every interval. |\n"
        "| Parallel line through a point | Keep the reference gradient, then find the new intercept. |\n"
        "| Perpendicular line through a point | For nonzero finite gradients, $m_{new}=-1/m_{ref}$. |\n"
        "| $Ax+By+C=0$, $B\\ne0$ | Isolate $y$: $m=-A/B$, $c=-C/B$. |\n"
        "| Engineering graph | Use the plotted variables; gradient units are vertical units / horizontal units. |"
    )
    st.markdown("### Horizontal and vertical lines need different forms")
    st.latex(r"\text{Horizontal: }y=k,\quad m=0;\qquad\text{Vertical: }x=k,\quad m\text{ undefined}")
    st.markdown("A horizontal line has zero vertical change. A vertical line has zero horizontal change, "
                "so calculating its gradient would require division by zero. A horizontal line and a vertical line are perpendicular. "
                "Two identical points do not determine a unique line; one point by itself is also insufficient.")
    st.markdown("### Common mistakes to avoid")
    st.markdown("- Using $y/x$ instead of $\\Delta y/\\Delta x$; $y/x$ only gives the gradient when the line passes through the origin and $x\\ne0$.\n"
                "- Reversing the subtraction order for only one coordinate. Reversing both gives the same gradient.\n"
                "- Reading grid squares without checking the axis values and units.\n"
                "- Calling a vertical line's gradient zero, or assuming every line passes through (0, 0).\n"
                "- Losing a negative sign when substituting coordinates or calculating c.\n"
                "- Giving only m and forgetting to write the complete equation.")
    st.info("Select a level in the sidebar, then open Problem. New random question generates fresh data. "
            "In Solve and check, enter a decimal or a fraction such as -2/3. The Solution tab shows the graphical construction and every calculation.")


GENERATORS = {
    "Linear equations": generate_linear,
    "Trigonometry": generate_trigonometry,
    "Vector components": generate_vector,
    "Differentiation": generate_differentiation,
    "Integration": generate_integration,
    "Straight-line equations": generate_straight_line,
}


def render_diagram(problem):
    if not problem.get("diagram"):
        return

    kind, data = problem["diagram"]

    if kind == "trig":
        st.pyplot(trig_triangle_figure(data), use_container_width=True)
    elif kind == "vector":
        st.pyplot(vector_figure(data), use_container_width=True)
    elif kind == "direction_triangle":
        st.pyplot(direction_triangle_figure(data), use_container_width=True)
    elif kind == "straight_line":
        show_straight_line(data)


def render_learning(topic):
    st.markdown("## Main ideas and formulas")
    st.markdown(
        """
        <div class="info">
          Start here when the mathematics is unfamiliar. The formulas are written
          in the same notation used later in Statics and Dynamics.
        </div>
        """,
        unsafe_allow_html=True,
    )

    if topic == "Straight-line equations":
        render_line_learning()

    elif topic == "Linear equations":
        st.markdown("### Balancing an equation")
        st.latex(r"ax+b=c")
        st.latex(r"ax=c-b")
        st.latex(r"x=\frac{c-b}{a}")
        st.markdown(
            """
            **Main rule:** whatever operation is applied to one side must also be
            applied to the other side.

            **For simultaneous equations:** two unknowns need two independent
            equations. Use substitution or elimination.
            """
        )
        st.markdown("### Common mistakes")
        st.markdown(
            """
            - Changing a sign incorrectly when moving a term.
            - Dividing only one term instead of the whole side.
            - Stopping before the unknown is fully isolated.
            - Using one equation to solve two unknowns.
            """
        )

    elif topic == "Trigonometry":
        st.markdown("### SOH–CAH–TOA")
        st.latex(r"\sin\theta=\frac{\text{opposite}}{\text{hypotenuse}}")
        st.latex(r"\cos\theta=\frac{\text{adjacent}}{\text{hypotenuse}}")
        st.latex(r"\tan\theta=\frac{\text{opposite}}{\text{adjacent}}")
        st.markdown("### Finding an angle")
        st.latex(r"\theta=\sin^{-1}\left(\frac{O}{H}\right)")
        st.latex(r"\theta=\cos^{-1}\left(\frac{A}{H}\right)")
        st.latex(r"\theta=\tan^{-1}\left(\frac{O}{A}\right)")
        st.markdown(
            """
            **Important:** opposite and adjacent depend on which angle is being used.

            **Calculator:** use degree mode when the angle is given in degrees.
            """
        )
        st.markdown("### Common mistakes")
        st.markdown(
            """
            - Choosing opposite and adjacent before identifying the angle.
            - Using sine instead of inverse sine when finding an angle.
            - Leaving the calculator in radian mode.
            - Rounding intermediate values too early.
            """
        )

    elif topic == "Vector components":
        st.markdown("### Angle measured from the x-axis")
        st.latex(r"F_x=F\cos\theta,\qquad F_y=F\sin\theta")
        st.markdown("### Angle measured from the y-axis")
        st.latex(r"F_x=F\sin\theta,\qquad F_y=F\cos\theta")
        st.markdown("### Direction triangle")
        st.latex(
            r"\mathbf u=\frac{\Delta x\,\mathbf i+\Delta y\,\mathbf j}"
            r"{\sqrt{(\Delta x)^2+(\Delta y)^2}}"
        )
        st.latex(r"\mathbf F=F\mathbf u")
        st.markdown(
            """
            Trigonometry gives component magnitudes. The vector direction and
            quadrant determine the signs.
            """
        )
        st.markdown("### Common mistakes")
        st.markdown(
            """
            - Using cosine for x without checking where the angle is measured.
            - Forgetting negative signs for leftward or downward components.
            - Treating the small direction triangle sides as the actual components.
            - Adding component magnitudes instead of using vector notation.
            """
        )

    elif topic == "Differentiation":
        st.markdown("### Power rule")
        st.latex(r"\frac{d}{dx}(x^n)=nx^{n-1}")
        st.latex(r"\frac{d}{dx}(C)=0")

        st.markdown("### Trigonometric derivatives")
        st.latex(r"\frac{d}{dx}\sin(kx)=k\cos(kx)")
        st.latex(r"\frac{d}{dx}\cos(kx)=-k\sin(kx)")
        st.markdown(
            """
            The factor $k$ comes from the chain rule because the inside
            function is $kx$. These calculus formulas assume the angle is in
            **radians**.
            """
        )

        st.markdown("### Kinematics")
        st.latex(r"v(t)=\frac{ds}{dt}")
        st.latex(r"a(t)=\frac{dv}{dt}=\frac{d^2s}{dt^2}")

        st.markdown("### Special case: sinusoidal motion only")
        st.write(
            "The following relationship is correct only when position is a sine "
            "or cosine function with constant amplitude and angular frequency."
        )
        st.latex(r"s(t)=A\sin(\omega t)")
        st.latex(r"v(t)=\frac{ds}{dt}=A\omega\cos(\omega t)")
        st.latex(
            r"a(t)=\frac{d^2s}{dt^2}"
            r"=-A\omega^2\sin(\omega t)"
        )
        st.latex(r"a(t)=-\omega^2s(t)")
        st.markdown(
            """
            The same final relationship is obtained for
            $s(t)=A cos(ωt)$. It is **not** a general formula for every
            kinematics problem. In the questions, velocity and acceleration are
            calculated by differentiation first; $a=-ω²s$ is used only
            as a check for sinusoidal motion.
            """
        )

        st.markdown("### Common mistakes")
        st.markdown(
            """
            - Reducing the power but forgetting to multiply by the original power.
            - Differentiating a constant as though it contains x.
            - Forgetting the negative sign in the derivative of cosine.
            - Forgetting the inside-function factor k or ω.
            - Using degree-mode ideas inside calculus instead of radians.
            - Substituting the numerical x or t value before differentiating.
            """
        )

    else:
        st.markdown("### Reverse power rule")
        st.latex(r"\int x^n\,dx=\frac{x^{n+1}}{n+1}+C,\qquad n\ne-1")

        st.markdown("### Trigonometric antiderivatives")
        st.latex(r"\int\sin(kx)\,dx=-\frac{1}{k}\cos(kx)+C")
        st.latex(r"\int\cos(kx)\,dx=\frac{1}{k}\sin(kx)+C")
        st.markdown(
            """
            The factor $1/k$ reverses the chain rule. Trigonometric calculus
            uses radians.
            """
        )

        st.markdown("### Kinematics")
        st.latex(r"v(t)=v_0+\int_0^t a(\tau)\,d\tau")
        st.latex(r"s(t)=s_0+\int_0^t v(\tau)\,d\tau")
        st.markdown(
            """
            The constant of integration is essential. Initial conditions such as
            $v(0)$ or $s(0)$ determine its value.
            """
        )

        st.markdown("### Common mistakes")
        st.markdown(
            """
            - Forgetting to increase the power before dividing.
            - Forgetting the constant of integration.
            - Forgetting the factor 1/k for `sin(kx)` or `cos(kx)`.
            - Confusing a trigonometric derivative with its antiderivative.
            - Applying limits before finding the antiderivative.
            - Forgetting to add the initial velocity or initial position.
            """
        )


def award_xp(problem_id, points):
    completed = st.session_state.setdefault("completed_checks", set())
    if problem_id not in completed:
        completed.add(problem_id)
        st.session_state["xp"] = st.session_state.get("xp", 0) + points


def check_final_answers(problem, mode, entered, line_form=None):
    """Check coefficients and, for special cases, the chosen equation form."""
    values = {}
    invalid = False
    for index, answer in enumerate(problem["answers"]):
        try:
            values[index] = (
                line_number_input(entered[index])
                if problem.get("line_data") else entered[index]
            )
        except ValueError as exc:
            st.warning(f"{answer['label']}: {exc}")
            invalid = True
    if invalid:
        return

    form_correct = True
    if problem.get("line_form_answer"):
        if line_form == "Choose an equation form":
            st.warning("Choose horizontal or vertical as well as entering the constant k.")
            return
        form_correct = line_form == problem["line_form_answer"]
        if form_correct:
            st.success("Correct equation form.")
        else:
            st.warning("Check which coordinate stays constant: x gives a vertical line; y gives a horizontal line.")

    results = [close_enough(values[i], answer) for i, answer in enumerate(problem["answers"])]
    for result, answer in zip(results, problem["answers"]):
        if result:
            st.markdown(f"<div class='good'>{answer['label']}: correct.</div>", unsafe_allow_html=True)
        elif mode == "Practice":
            expected = fmt(answer["value"], 5)
            unit = f" {answer['unit']}" if answer["unit"] else ""
            st.markdown(f"<div class='bad'>{answer['label']}: check again. "
                        f"Expected approximately {expected}{unit}.</div>", unsafe_allow_html=True)
        else:
            st.markdown(f"<div class='bad'>{answer['label']}: check the formula, signs and arithmetic.</div>",
                        unsafe_allow_html=True)

    if all(results) and form_correct:
        st.success("Excellent — all answers are correct.")
        award_xp(f"{problem['uid']}_answers", 35)

    if problem.get("line_data"):
        data = problem["line_data"]
        # Keep a typed fraction exact in the assembled equation.
        display_values = {}
        for index in values:
            raw = "".join(str(entered[index]).strip().replace("−", "-").split())
            fraction = _line_input_fraction(raw)
            display_values[index] = (
                sp.Rational(fraction.numerator, fraction.denominator)
                if "/" in raw or fraction.denominator == 1 else sp.Float(raw)
            )
        if problem.get("line_form_answer"):
            k = values[0]
            candidate = {"vertical": k} if line_form == "x = k (vertical)" else {"m": 0, "c": k}
            display_m, display_c = sp.Integer(0), display_values[0]
            display_vertical = display_values[0] if line_form == "x = k (vertical)" else None
        else:
            candidate = {"m": values[0], "c": values[1]}
            display_m, display_c = display_values[0], display_values[1]
            display_vertical = None
        st.markdown("### The equation from your entries")
        st.latex(line_equation_latex(
            display_m, display_c,
            data.get("x_symbol", "x"), data.get("y_symbol", "y"),
            display_vertical,
        ))
        if mode == "Practice":
            st.caption("The orange dotted line is your equation. Check whether it passes through the known points and has the required direction.")
            show_straight_line(data, candidate=candidate)


# -----------------------------------------------------------------------------
# Persistent question state
# -----------------------------------------------------------------------------
# Streamlit session_state is intentionally temporary. If a student's browser is
# inactive long enough for the Streamlit session to expire, session_state can be
# recreated and the old app would therefore generate a different random problem.
#
# To make a question survive that reconnect, MathQuest stores only a compact
# deterministic random seed (plus topic/level and a short question history) in
# the page URL. The complete problem is regenerated from that seed on every run.
# No answer or worked solution is placed in the URL.
QUESTION_STATE_PARAM = "mq_q"
QUESTION_STATE_VERSION = 1
MAX_QUESTION_HISTORY = 30
TOPIC_ORDER = list(TOPICS.keys())


def _query_param_value(name):
    """Read one query parameter without depending on a particular Streamlit API."""
    try:
        if hasattr(st, "query_params"):
            value = st.query_params.get(name, "")
        else:
            value = st.experimental_get_query_params().get(name, "")
    except Exception:
        return ""

    if isinstance(value, (list, tuple)):
        value = value[-1] if value else ""
    return str(value or "")


def _set_query_param(name, value):
    """Update our query parameter while leaving any unrelated parameters alone."""
    try:
        if hasattr(st, "query_params"):
            st.query_params[name] = value
        else:
            params = st.experimental_get_query_params()
            params[name] = value
            st.experimental_set_query_params(**params)
    except Exception:
        # The app still works with normal session_state behaviour if a very old
        # Streamlit deployment does not permit query-parameter updates.
        pass


def _encode_question_state(state):
    topic_index = TOPIC_ORDER.index(state["topic"])
    payload = {
        "v": QUESTION_STATE_VERSION,
        "t": topic_index,
        "l": int(state["level"]),
        "i": int(state["index"]),
        "s": [int(seed) for seed in state["seeds"]],
    }
    raw = json.dumps(payload, separators=(",", ":")).encode("utf-8")
    return base64.urlsafe_b64encode(raw).decode("ascii").rstrip("=")


def _decode_question_state(token):
    if not token:
        return None

    try:
        padded = token + "=" * (-len(token) % 4)
        payload = json.loads(base64.urlsafe_b64decode(padded).decode("utf-8"))

        if int(payload.get("v", -1)) != QUESTION_STATE_VERSION:
            return None

        topic_index = int(payload["t"])
        if topic_index < 0 or topic_index >= len(TOPIC_ORDER):
            return None

        topic = TOPIC_ORDER[topic_index]
        level = int(payload["l"])
        if level not in TOPICS[topic]:
            return None

        seeds = [int(seed) for seed in payload.get("s", [])]
        seeds = [seed for seed in seeds if 0 < seed < 2**63]
        if not seeds:
            return None

        # Keep URLs compact even if an older version somehow saved more history.
        if len(seeds) > MAX_QUESTION_HISTORY:
            seeds = seeds[-MAX_QUESTION_HISTORY:]

        index = int(payload.get("i", len(seeds) - 1))
        index = max(0, min(index, len(seeds) - 1))

        return {
            "topic": topic,
            "level": level,
            "seeds": seeds,
            "index": index,
        }
    except Exception:
        return None


def _save_question_state(state):
    """Trim and persist the current question/history in the browser URL."""
    seeds = list(state["seeds"])
    index = int(state["index"])

    if len(seeds) > MAX_QUESTION_HISTORY:
        remove_count = len(seeds) - MAX_QUESTION_HISTORY
        seeds = seeds[remove_count:]
        index = max(0, index - remove_count)

    state = {
        "topic": state["topic"],
        "level": int(state["level"]),
        "seeds": seeds,
        "index": max(0, min(index, len(seeds) - 1)),
    }
    _set_query_param(QUESTION_STATE_PARAM, _encode_question_state(state))
    return state


def _fresh_seed(existing_seeds=()):
    """Create a new seed, avoiding exact seed reuse in the visible history."""
    used = set(int(seed) for seed in existing_seeds)
    for _ in range(100):
        seed = SEED_RNG.randrange(1, 2**63)
        if seed not in used:
            return seed
    return SEED_RNG.randrange(1, 2**63)


def _new_question_state(topic, level):
    return {
        "topic": topic,
        "level": int(level),
        "seeds": [_fresh_seed()],
        "index": 0,
    }


def build_problem_from_seed(topic, level, seed):
    """Regenerate exactly the same problem from a persistent random seed."""
    global RNG

    previous_rng = RNG
    RNG = random.Random(int(seed))
    try:
        problem = GENERATORS[topic](int(level))
    finally:
        RNG = previous_rng

    # A seed-based uid is stable across Streamlit reconnects, but different for
    # each generated question. It also keeps widget keys tied to the question.
    problem["uid"] = f"q_{TOPIC_ORDER.index(topic)}_{int(level)}_{int(seed)}"
    problem["seed"] = int(seed)
    return problem


render_header()

st.sidebar.markdown("## Mode")
mode = st.sidebar.radio(
    "Choose activity",
    ["Practice", "Self-test"],
    help=(
        "Practice gives formula clues and immediate feedback. "
        "Self-test hides the worked solution until it is revealed."
    ),
)

st.sidebar.markdown("---")
st.sidebar.markdown("## Practice setup")

# Restore the question after a Streamlit inactivity timeout/reconnect.
question_state = _decode_question_state(
    _query_param_value(QUESTION_STATE_PARAM)
)
if question_state is None:
    default_topic = TOPIC_ORDER[0]
    question_state = _save_question_state(
        _new_question_state(default_topic, TOPICS[default_topic][0])
    )

restored_topic = question_state["topic"]
topic = st.sidebar.radio(
    "Topic",
    TOPIC_ORDER,
    index=TOPIC_ORDER.index(restored_topic),
)

level_options = TOPICS[topic]
if topic == question_state["topic"] and question_state["level"] in level_options:
    restored_level = question_state["level"]
else:
    restored_level = level_options[0]

level = st.sidebar.selectbox(
    "Level",
    level_options,
    index=level_options.index(restored_level),
    format_func=lambda value: (
        f"{value}. {LINE_LEVELS[value]}" if topic == "Straight-line equations" else str(value)
    ),
)
level = int(level)

# Changing topic/level starts a fresh history for that setup. This mirrors the
# old app behaviour while ensuring that the selected question itself persists.
if topic != question_state["topic"] or level != question_state["level"]:
    question_state = _save_question_state(_new_question_state(topic, level))

new_question = st.sidebar.button(
    "🎲 New random question",
    use_container_width=True,
)

previous_col, next_col = st.sidebar.columns(2)
previous_question = previous_col.button(
    "← Previous",
    use_container_width=True,
    disabled=question_state["index"] <= 0,
    help="Return to the previous generated question.",
)
next_question = next_col.button(
    "Next →",
    use_container_width=True,
    disabled=question_state["index"] >= len(question_state["seeds"]) - 1,
    help="Move forward again after using Previous.",
)

if previous_question:
    question_state["index"] -= 1
    question_state = _save_question_state(question_state)
elif next_question:
    question_state["index"] += 1
    question_state = _save_question_state(question_state)
elif new_question:
    # If the student went back first, a new question starts a new branch and the
    # old forward history is discarded, which is the usual browser-history model.
    question_state["seeds"] = question_state["seeds"][: question_state["index"] + 1]
    question_state["seeds"].append(
        _fresh_seed(question_state["seeds"])
    )
    question_state["index"] = len(question_state["seeds"]) - 1
    question_state = _save_question_state(question_state)

if previous_question or next_question or new_question:
    # Refresh navigation controls using the updated index, so Previous/Next
    # immediately reflect the newly displayed question.
    st.rerun()

current_seed = question_state["seeds"][question_state["index"]]
problem = build_problem_from_seed(topic, level, current_seed)

st.sidebar.caption(f"Current problem: {problem['title']}")
st.sidebar.caption(
    f"Question {question_state['index'] + 1} of {len(question_state['seeds'])} in this history"
)
st.sidebar.caption(
    "The current question is saved in this page URL, so it can be restored after an inactivity timeout or reconnect."
)

st.sidebar.markdown("---")
st.sidebar.markdown("## Progress")
xp = st.session_state.get("xp", 0)

if xp >= 350:
    badge = "🏆 Maths Master"
elif xp >= 220:
    badge = "⭐ Strong Foundations"
elif xp >= 100:
    badge = "✅ Developing Well"
elif xp > 0:
    badge = "🛠 Getting Started"
else:
    badge = "None yet"

st.sidebar.markdown(f"**XP**  \n{xp}")
st.sidebar.markdown(f"**Badge**  \n{badge}")
st.sidebar.markdown(
    "<div class='skill'>New questions are kept in a short browser-linked history. "
    "Use Previous/Next to revisit them; the current question is also restored after a reconnect.</div>",
    unsafe_allow_html=True,
)

tabs = st.tabs(
    [
        "0. Learn the topic",
        "1. Problem",
        "2. Choose the method",
        "3. Solve and check",
        "4. Solution",
    ]
)

with tabs[0]:
    render_learning(topic)

with tabs[1]:
    left, right = st.columns([1.0, 1.05], gap="large")

    with left:
        st.markdown("## Current problem")
        st.caption(
            f"{topic} | Level {level} | Difficulty: {problem['difficulty']}"
        )
        st.markdown(f"### {problem['title']}")
        st.write(problem["prompt"])

        if problem.get("display_equation"):
            st.latex(problem["display_equation"])

        if problem.get("table"):
            st.table(problem["table"])

        st.markdown(
            """
            <div class="hint">
              Work carefully and keep full calculator precision until the final line.
              Use the New random question button for another problem.
            </div>
            """,
            unsafe_allow_html=True,
        )

    with right:
        if problem.get("diagram"):
            st.markdown("### Diagram")
            render_diagram(problem)
        else:
            st.markdown("### Suggested working method")
            st.markdown(
                """
                <div class="card">
                  1. Write the relevant formula or equation.<br>
                  2. Substitute the known values with signs.<br>
                  3. Rearrange carefully.<br>
                  4. Calculate.<br>
                  5. Check whether the answer is reasonable.
                </div>
                """,
                unsafe_allow_html=True,
            )

with tabs[2]:
    st.markdown("## Choose the method or formula")

    fq = problem["formula_question"]
    selected = st.radio(
        fq["question"],
        fq["options"],
        key=f"{problem['uid']}_formula",
    )

    if st.button(
        "Check method",
        key=f"{problem['uid']}_check_formula",
    ):
        if selected == fq["correct"]:
            st.success("Correct method.")
            if mode == "Practice":
                st.write(fq["explanation"])
            award_xp(f"{problem['uid']}_method", 10)
        else:
            st.warning("That is not the best method for this question.")
            if mode == "Practice":
                st.write(fq["explanation"])

with tabs[3]:
    st.markdown("## Solve and check")

    if mode == "Practice":
        st.markdown(
            """
            <div class="info">
              Enter the final numerical values. Signs and units matter.
              The detailed calculation appears in the Solution tab.
            </div>
            """,
            unsafe_allow_html=True,
        )

    entered = {}
    line_form = None
    if problem.get("line_data"):
        st.info("Write your complete equation on paper. Enter its coefficients below as decimals or fractions "
                "(for example, -2/3). Use at least four decimal places for recurring decimals. "
                "Checking your entries will assemble the complete equation.")
    if problem.get("line_form_answer"):
        line_form = st.selectbox(
            "Equation form",
            ["Choose an equation form", "y = k (horizontal)", "x = k (vertical)"],
            key=f"{problem['uid']}_line_form",
        )

    columns = st.columns(min(2, len(problem["answers"])))

    for index, answer in enumerate(problem["answers"]):
        with columns[index % len(columns)]:
            label = answer["label"]
            if answer["unit"]:
                label += f" ({answer['unit']})"

            if problem.get("line_data"):
                entered[index] = st.text_input(
                    label, value="", placeholder="Number or fraction, e.g. -2/3",
                    key=f"{problem['uid']}_answer_{index}",
                )
            else:
                entered[index] = st.number_input(
                    label,
                    value=0.0,
                    format="%.5f",
                    key=f"{problem['uid']}_answer_{index}",
                )

    if st.button(
        "Check final answer",
        type="primary",
        key=f"{problem['uid']}_check_answers",
    ):
        check_final_answers(problem, mode, entered, line_form)

    st.markdown("### Reasonableness check")
    st.write(problem["teaching_point"])

with tabs[4]:
    st.markdown("## Detailed worked solution")

    revealed = mode == "Practice" or st.session_state.get(
        f"reveal_{problem['uid']}",
        False,
    )

    if not revealed:
        st.warning(
            "The solution is hidden in Self-test mode until you finish your attempt."
        )
        if st.button(
            "Reveal worked solution",
            key=f"reveal_button_{problem['uid']}",
        ):
            st.session_state[f"reveal_{problem['uid']}"] = True
            st.rerun()
    else:
        st.markdown("### Original question")
        st.markdown(f"**{problem['title']}**")
        st.write(problem["prompt"])

        if problem.get("display_equation"):
            st.latex(problem["display_equation"])

        if problem.get("table"):
            st.table(problem["table"])

        if problem.get("diagram"):
            render_diagram(problem)

        st.markdown("---")
        st.markdown("### Step-by-step solution")
        st.markdown(
            """
            <div class="info">
              Each line explains what is being done and why. Follow the same
              sequence in your written working.
            </div>
            """,
            unsafe_allow_html=True,
        )

        for kind, content in problem["solution"]:
            if kind == "latex":
                st.latex(content)
            elif kind == "heading":
                st.markdown(f"### {content}")
            elif kind == "line_plot":
                show_straight_line(problem["line_data"], content)
            else:
                st.write(content)

        st.markdown("### Final learning point")
        st.markdown(
            f"<div class='hint'>{problem['teaching_point']}</div>",
            unsafe_allow_html=True,
        )
