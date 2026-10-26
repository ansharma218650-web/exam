"""SuperTET PRT Practice v2 - chalkboard & notebook themed exam practice app."""
import html
import json
import random
import time
import uuid

import pandas as pd
import streamlit as st

import utils as U

st.set_page_config(
    page_title="SuperTET PRT Practice",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)
S = st.session_state
NEW = "➕ Create new"


# =====================================================================
# STYLE
# =====================================================================
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,500;12..96,700;12..96,800&family=Figtree:wght@400;500;600;700&display=swap');
:root{--board:#14342B;--board2:#1D4A3C;--chalk:#F2EFE4;--gold:#F2B01E;--paper:#EEF2EE;--card:#FFFFFF;--ink:#1A2422;--muted:#5E6B66;--line:#D8E0DA;--ok:#1E8A5E;--ok-bg:#E3F4EB;--bad:#C2413A;--bad-bg:#FBE9E7;--margin:#E8A9A4;--rule:#DDE7F1;--wood:#9A6B3E;}
.stApp,.stApp p,.stApp li,.stApp label,.stApp button,.stApp input,.stApp textarea,.stApp td,.stApp th,.stApp [data-testid="stMarkdownContainer"],.stApp [data-testid="stCaptionContainer"],.stApp [data-baseweb="select"] *,.stApp [data-baseweb="tab"]{font-family:'Figtree',system-ui,-apple-system,'Segoe UI',sans-serif !important;}
.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stApp h5,.disp{font-family:'Bricolage Grotesque','Figtree',sans-serif !important;letter-spacing:-.015em;color:var(--ink);}
.stApp{background:var(--paper);}
#MainMenu,footer{visibility:hidden;}
header[data-testid="stHeader"]{background:transparent;}
.block-container{padding-top:2.2rem;padding-bottom:4rem;max-width:1120px;}
.stApp h3{font-size:1.45rem;margin-top:.4rem;}

/* sidebar */
section[data-testid="stSidebar"]{background:var(--board) !important;border-right:6px solid var(--wood);}
section[data-testid="stSidebar"] *{color:var(--chalk) !important;}
section[data-testid="stSidebar"] .stButton>button{background:transparent !important;border:1px solid transparent !important;justify-content:flex-start;text-align:left;font-weight:600;padding:.62rem .9rem;color:var(--chalk) !important;}
section[data-testid="stSidebar"] .stButton>button:hover{background:rgba(255,255,255,.09) !important;border-color:rgba(255,255,255,.18) !important;}
.brand{padding:.4rem .2rem 1.1rem;}
.brand b{display:block;font-family:'Bricolage Grotesque',sans-serif;font-size:1.7rem;line-height:1.05;color:var(--gold) !important;}
.brand span{font-size:.85rem;opacity:.75;}
.side-note{font-size:.8rem;opacity:.65;padding:.2rem .3rem;}

/* buttons / inputs */
.stButton>button,.stDownloadButton>button,[data-testid="stFormSubmitButton"]>button{width:100%;border-radius:10px;font-weight:600;min-height:2.7rem;}
[data-testid="stMetric"]{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:.8rem 1rem;}
[data-testid="stMetricLabel"]{color:var(--muted);}
div[data-testid="stVerticalBlockBorderWrapper"]:has(> div > div[data-testid="stVerticalBlock"]) {border-radius:16px;}
.stTabs [data-baseweb="tab-list"]{gap:.4rem;}
.stTabs [data-baseweb="tab"]{border-radius:10px 10px 0 0;font-weight:600;}

/* hero - the chalkboard */
.hero{background:radial-gradient(1200px 400px at 20% -10%,rgba(255,255,255,.07),transparent 60%),var(--board);border:7px solid var(--wood);border-radius:14px;box-shadow:inset 0 0 50px rgba(0,0,0,.4),0 18px 30px -22px rgba(20,52,43,.8);padding:2rem 2.2rem;display:flex;flex-wrap:wrap;gap:1.6rem 2.4rem;align-items:center;justify-content:space-between;margin-bottom:1.6rem;}
.hero-text{flex:1 1 340px;max-width:560px;}
.hero h1{font-size:2.6rem;line-height:1.08;color:var(--chalk) !important;margin:0 0 .7rem;padding:0;font-weight:800;}
.hero p{color:rgba(242,239,228,.82) !important;font-size:1.05rem;line-height:1.55;margin:0;}
.hero-stats{display:flex;gap:.9rem;flex-wrap:wrap;}
.hero-stat{border:2px dashed rgba(242,239,228,.45);border-radius:12px;padding:.8rem 1.1rem;min-width:104px;text-align:center;}
.hero-stat b{display:block;font-family:'Bricolage Grotesque',sans-serif;font-size:2.1rem;color:var(--gold);line-height:1;}
.hero-stat span{font-size:.85rem;color:var(--chalk);opacity:.85;}

/* cards & chips */
.stApp .stProgress>div>div>div>div{background:var(--gold);}
.card-title{font-family:'Bricolage Grotesque',sans-serif;font-weight:700;font-size:1.2rem;color:var(--ink);line-height:1.2;}
.card-sub{color:var(--muted);font-size:.9rem;margin:.2rem 0 .6rem;}
.chips{display:flex;flex-wrap:wrap;gap:.45rem;margin-top:.5rem;}
.chip{display:inline-block;background:#E6EEE9;color:var(--board2);border-radius:999px;padding:.18rem .7rem;font-size:.82rem;font-weight:600;}
.chip.gold{background:#FBEFC9;color:#7A5600;}
.chip.red{background:var(--bad-bg);color:var(--bad);}
.chip.green{background:var(--ok-bg);color:var(--ok);}
.page-title{font-family:'Bricolage Grotesque',sans-serif;font-weight:800;font-size:2rem;margin:0 0 .2rem;color:var(--ink);}
.page-sub{color:var(--muted);margin:0 0 1.1rem;}
[class*="st-key-sub_"],[class*="st-key-ser_"]{background:var(--card);}

/* the notebook page that holds each question */
[class*="st-key-qcard"]{position:relative;background-color:#FEFEFC;background-image:repeating-linear-gradient(to bottom,transparent 0,transparent 33px,var(--rule) 33px,var(--rule) 34px);border:1px solid var(--line);border-left:0;border-radius:6px 16px 16px 6px;padding:.3rem 1.4rem 1.1rem 4.4rem !important;box-shadow:0 14px 26px -20px rgba(20,52,43,.55);gap:0 !important;margin-bottom:.9rem;}
[class*="st-key-qcard"]::before{content:"";position:absolute;left:3.1rem;top:0;bottom:0;width:2px;background:var(--margin);}
[class*="st-key-qcard"]::after{content:"";position:absolute;left:.8rem;top:0;bottom:0;width:16px;background:radial-gradient(circle at 8px 50%,var(--paper) 0 6.5px,transparent 7.5px) 0 0/16px 130px repeat-y;}
[class*="st-key-qcard"] [data-testid="stMarkdownContainer"] p{font-size:1.14rem;line-height:34px;margin:0;color:var(--ink);}
.qmeta{height:34px;line-height:34px;font-size:.85rem;color:var(--muted);font-weight:600;}

/* radio options styled as answer cards */
[class*="st-key-optbox"] div[role="radiogroup"]{gap:.55rem;}
[class*="st-key-optbox"] div[role="radiogroup"]>label{background:#fff;border:1.5px solid var(--line);border-radius:12px;padding:.8rem 1rem;margin:0;width:100%;transition:border-color .15s,background .15s;}
[class*="st-key-optbox"] div[role="radiogroup"]>label:hover{border-color:var(--board2);}
[class*="st-key-optbox"] div[role="radiogroup"]>label:has(input:checked){border-color:var(--board2);background:#E6F0EA;}

/* revealed option cards */
.opt{display:flex;align-items:center;gap:.85rem;padding:.72rem 1rem;margin:.5rem 0;background:#fff;border:1.5px solid var(--line);border-radius:12px;color:var(--ink);}
.opt .ltr{flex:0 0 auto;width:30px;height:30px;border-radius:50%;display:grid;place-items:center;font-weight:700;font-size:.9rem;background:#E9EFEB;color:var(--board2);}
.opt .tag{margin-left:auto;font-size:.78rem;font-weight:700;white-space:nowrap;}
.opt.ok{background:var(--ok-bg);border-color:var(--ok);}
.opt.ok .ltr{background:var(--ok);color:#fff;}
.opt.ok .tag{color:var(--ok);}
.opt.bad{background:var(--bad-bg);border-color:var(--bad);}
.opt.bad .ltr{background:var(--bad);color:#fff;}
.opt.bad .tag{color:var(--bad);}
.verdict{border-radius:12px;padding:.75rem 1rem;font-weight:600;margin:.4rem 0 .6rem;}
.verdict.ok{background:var(--ok-bg);color:#126343;border:1px solid #A8DCC3;}
.verdict.bad{background:var(--bad-bg);color:#8E2A24;border:1px solid #EDB6B1;}

/* timer */
.timer{background:var(--board);color:var(--chalk);border-radius:14px;border:3px solid var(--wood);padding:.45rem 1rem;text-align:center;}
.timer small{display:block;font-size:.75rem;opacity:.75;}
.timer b{font-family:'Bricolage Grotesque',sans-serif;font-size:1.9rem;font-variant-numeric:tabular-nums;line-height:1.1;}
.timer.warn{background:#7A1F1A;}
.timer.warn b{color:#FFD9A0;}

/* score ring and tiles */
.ring{width:158px;height:158px;border-radius:50%;background:conic-gradient(var(--ok) calc(var(--p) * 1%),#D8E0DA 0);display:grid;place-items:center;margin:0 auto;}
.ring-in{width:124px;height:124px;border-radius:50%;background:#fff;display:flex;flex-direction:column;align-items:center;justify-content:center;}
.ring-in b{font-family:'Bricolage Grotesque',sans-serif;font-size:1.9rem;line-height:1;color:var(--ink);}
.ring-in span{font-size:.8rem;color:var(--muted);}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:.7rem;}
.tile{background:#F4F7F5;border:1px solid var(--line);border-radius:12px;padding:.7rem .9rem;}
.tile b{display:block;font-family:'Bricolage Grotesque',sans-serif;font-size:1.6rem;line-height:1.1;}
.tile span{font-size:.82rem;color:var(--muted);}
.tile.ok b{color:var(--ok);} .tile.bad b{color:var(--bad);}
.legend{display:flex;flex-wrap:wrap;gap:.5rem .9rem;font-size:.8rem;color:var(--muted);margin-top:.5rem;}
.legend i{display:inline-block;width:11px;height:11px;border-radius:3px;margin-right:.3rem;vertical-align:-1px;border:1px solid var(--line);}
/* sidebar inputs */
section[data-testid="stSidebar"] [data-baseweb="input"] *,section[data-testid="stSidebar"] input{color:#1A2422 !important;-webkit-text-fill-color:#1A2422;}
.side-hi{font-size:.85rem;opacity:.8;margin:.1rem 0 .6rem;}
/* dashboard */
.bars{display:grid;gap:.65rem;}
.bar-row{display:grid;grid-template-columns:minmax(110px,210px) 1fr 46px;gap:.7rem;align-items:center;font-size:.92rem;}
.bar{height:12px;border-radius:99px;background:#DDE5DF;overflow:hidden;}
.bar i{display:block;height:100%;border-radius:99px;}
.bar-row em{font-style:normal;font-weight:700;text-align:right;}
.tile.gold b{color:#B07A00;}
.empty{color:var(--muted);padding:.4rem 0;}
/* ---- always light: readable even when the phone or browser is in dark mode ---- */
.stApp{color-scheme:light;background:var(--paper) !important;color:var(--ink);}
:where(.stApp) :where([data-testid="stMarkdownContainer"] p,[data-testid="stMarkdownContainer"] li,[data-testid="stMarkdownContainer"] h1,[data-testid="stMarkdownContainer"] h2,[data-testid="stMarkdownContainer"] h3,[data-testid="stMarkdownContainer"] h4,[data-testid="stMarkdownContainer"] h5,[data-testid="stMarkdownContainer"] strong,[data-testid="stMarkdownContainer"] em,[data-testid="stWidgetLabel"] *,label,summary){color:var(--ink) !important;}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] *{color:var(--muted) !important;}
[data-testid="stAlert"] *{color:var(--ink) !important;}
header[data-testid="stHeader"] *,[data-testid="stExpandSidebarButton"] *,[data-testid="stSidebarCollapsedControl"] *{color:var(--ink) !important;}
:where(.stApp) :where(input,textarea){color:var(--ink) !important;-webkit-text-fill-color:var(--ink);background:#fff !important;caret-color:var(--ink);}
[data-baseweb="select"]>div,[data-baseweb="input"],[data-baseweb="base-input"],[data-baseweb="textarea"]{background:#fff !important;border-color:var(--line) !important;}
[data-baseweb="select"] *,[data-baseweb="input"] *{color:var(--ink) !important;}
[data-testid="stNumberInput"] button{background:#F1F5F2 !important;}
[data-baseweb="popover"],[data-baseweb="popover"]>div,[data-baseweb="menu"],[data-baseweb="popover"] ul{background:#fff !important;}
[data-baseweb="popover"] *{color:var(--ink) !important;}
[data-testid="stExpander"] details{background:#fff !important;border-color:var(--line) !important;}
[data-testid="stExpander"] summary *{color:var(--ink) !important;}
div[data-testid="stVerticalBlockBorderWrapper"]{border-color:var(--line) !important;}
:where(.stApp) :where(button[kind="secondary"],button[data-testid="stBaseButton-secondary"],button[data-testid="stBaseButton-secondaryFormSubmit"],[data-testid="stPopoverButton"]){background:#fff !important;color:var(--ink) !important;border:1px solid var(--line) !important;}
:where(.stApp) button p{color:inherit !important;}
button[kind="primary"],button[data-testid="stBaseButton-primary"],button[data-testid="stBaseButton-primaryFormSubmit"]{background:var(--board2) !important;border:1px solid var(--board2) !important;}
button[kind="primary"] *,button[data-testid="stBaseButton-primary"] *,button[data-testid="stBaseButton-primaryFormSubmit"] *{color:#fff !important;}
button:disabled{opacity:.5;}
.chartbox{background:#fff;border:1px solid var(--line);border-radius:14px;padding:.6rem .8rem;}
@media (max-width:640px){.hero{padding:1.3rem;}.hero h1{font-size:1.9rem;}[class*="st-key-qcard"]{padding-left:3.6rem !important;}[class*="st-key-qcard"]::before{left:2.5rem;}}
@media (prefers-reduced-motion:reduce){*{transition:none !important;}}
"""


def H(s: str) -> str:
    """Collapse an indented HTML snippet so markdown never mistakes it for a code block."""
    return "".join(line.strip() for line in s.splitlines())


def esc(x) -> str:
    return html.escape(str(x))


def md(s: str) -> None:
    st.markdown(H(s), unsafe_allow_html=True)


def show_df(data) -> None:
    try:
        st.dataframe(data, width="stretch", hide_index=True)
    except Exception:  # older Streamlit versions
        st.dataframe(data, use_container_width=True, hide_index=True)


def page_head(title: str, sub: str = "") -> None:
    md(f'<div class="page-title">{esc(title)}</div><div class="page-sub">{esc(sub)}</div>')


def option_cards(q: dict, picked=None) -> None:
    """Revealed answer options: green for correct, red for the wrong pick."""
    rows = []
    for k, o in enumerate(q["options"]):
        cls, tag = "opt", ""
        if k == q["answer"]:
            cls += " ok"
            tag = "Your answer" if picked == k else "Correct answer"
        elif k == picked:
            cls += " bad"
            tag = "Your answer"
        tag_html = f'<span class="tag">{tag}</span>' if tag else ""
        rows.append(f'<div class="{cls}"><span class="ltr">{chr(65 + k)}</span><span>{esc(o)}</span>{tag_html}</div>')
    md("".join(rows))


def opt_fmt(opts):
    return lambda k: f"{chr(65 + k)}.  {opts[k]}"


def ring(pct: float, big: str, small: str) -> str:
    pct = max(0.0, min(100.0, pct))
    return H(f'<div class="ring" style="--p:{pct:.0f}"><div class="ring-in"><b>{esc(big)}</b><span>{esc(small)}</span></div></div>')


def mmss(sec: int) -> str:
    sec = max(0, int(sec))
    return f"{sec // 60:02d}:{sec % 60:02d}"


def go(page: str) -> None:
    S.page = page


def user() -> str:
    return S.get("user", "")


def toggle_bm(key: str) -> None:
    U.toggle_bookmark(user(), key)


def keep(*keys) -> None:
    """Stop Streamlit from forgetting widget values while the user visits other pages."""
    for k in keys:
        if k in S:
            S[k] = S[k]


# =====================================================================
# HOME
# =====================================================================
def open_subject(slug):
    S.p_mode = "By subject"
    S.p_subject = slug
    S.page = "practice"


def open_series(series):
    S.t_series = series
    S.page = "tests"


def load_demo():
    U.seed_sample()


def history_df(hist) -> pd.DataFrame:
    df = pd.DataFrame(hist)
    for c in ("score", "max_score", "correct", "wrong", "unattempted"):
        df[c] = pd.to_numeric(df[c], errors="coerce").fillna(0)
    df["Score %"] = (df["score"] / df["max_score"].where(df["max_score"] > 0, 1) * 100).clip(lower=0).round(1)
    return df


def score_chart(vals) -> str:
    """Self-contained SVG line chart of recent mock scores (always readable)."""
    vals = [float(v) for v in vals][-20:]
    W, Ht, pad = 560, 210, 36
    n = len(vals)

    def X(i):
        return pad + (W - 2 * pad) * (i / (n - 1) if n > 1 else 0.5)

    def Y(v):
        return Ht - pad + 6 - (Ht - 2 * pad) * max(0.0, min(100.0, v)) / 100

    grid = "".join(
        f'<line x1="{pad}" x2="{W - pad}" y1="{Y(g):.1f}" y2="{Y(g):.1f}" stroke="#DDE5DF"/>'
        f'<text x="{pad - 8}" y="{Y(g) + 4:.1f}" text-anchor="end" font-size="11" fill="#5E6B66">{g}%</text>'
        for g in (0, 50, 100))
    pts = " ".join(f"{X(i):.1f},{Y(v):.1f}" for i, v in enumerate(vals))
    line = f'<polyline points="{pts}" fill="none" stroke="#1D4A3C" stroke-width="3" stroke-linejoin="round"/>' if n > 1 else ""
    dots = "".join(f'<circle cx="{X(i):.1f}" cy="{Y(v):.1f}" r="5" fill="#F2B01E" stroke="#1D4A3C" stroke-width="2"/>'
                   for i, v in enumerate(vals))
    last = f'<text x="{X(n - 1):.1f}" y="{Y(vals[-1]) - 11:.1f}" text-anchor="middle" font-size="12" font-weight="700" fill="#1A2422">{vals[-1]:.0f}%</text>' if n else ""
    return H(f'<div class="chartbox"><svg viewBox="0 0 {W} {Ht}" role="img" aria-label="Recent mock test scores" '
             f'style="width:100%;height:auto;display:block">{grid}{line}{dots}{last}</svg></div>')


def bar_color(pct: float) -> str:
    return "#C2413A" if pct < 50 else "#E0A100" if pct < 75 else "#1E8A5E"


def dashboard(prog, subjects):
    groups = {g: v for g, v in prog["groups"].items() if v["a"] > 0}
    total = sum(v["a"] for v in groups.values())
    right = sum(v["c"] for v in groups.values())
    acc = f"{right / total * 100:.0f}%" if total else "–"
    today, goal, streak = U.today_count(prog), prog["goal"], U.streak(prog)
    md(f"""<div class="tiles" style="margin-bottom:.7rem">
        <div class="tile gold"><b>{streak}</b><span>day streak</span></div>
        <div class="tile"><b>{today}/{goal}</b><span>today's goal</span></div>
        <div class="tile ok"><b>{acc}</b><span>overall accuracy</span></div>
        <div class="tile"><b>{total}</b><span>questions answered</span></div></div>""")
    st.progress(min(1.0, today / goal) if goal else 0.0)
    if today >= goal:
        st.caption("Daily goal reached. Great work!")

    if not groups:
        md('<div class="empty">Answer a few practice questions and your strengths will show up here.</div>')
        return
    rows = sorted(groups.items(), key=lambda kv: kv[1]["c"] / kv[1]["a"])[:6]
    bars = "".join(
        f'<div class="bar-row"><span>{esc(g)}</span><div class="bar"><i style="width:{v["c"] / v["a"] * 100:.0f}%;'
        f'background:{bar_color(v["c"] / v["a"] * 100)}"></i></div><em>{v["c"] / v["a"] * 100:.0f}%</em></div>'
        for g, v in rows)
    st.markdown("##### Where you stand")
    md(f'<div class="bars">{bars}</div>')
    names = {n: s for s, n in subjects}
    weak = [(g, v) for g, v in rows if g in names and v["a"] >= 3 and v["c"] / v["a"] < 0.75]
    if weak:
        g = weak[0][0]
        st.write("")
        st.button(f"Focus on {g}", key="focus", on_click=open_subject, args=(names[g],))


def home_page():
    subjects = U.list_subjects()
    series = U.list_series()
    pcount = {slug: len(U.load_practice(slug)["questions"]) for slug, _ in subjects}
    n_q = sum(pcount.values())
    n_t = sum(len(U.list_tests(s)) for s in series)
    who = (S.get("student_name") or "").strip()
    hello = f"Welcome back, {esc(who)}. " if who else ""

    md(f"""
        <div class="hero">
          <div class="hero-text">
            <h1>Practice like the paper is tomorrow.</h1>
            <p>{hello}Subject-wise MCQs with instant explanations, and timed mock tests that feel like the real exam.</p>
          </div>
          <div class="hero-stats">
            <div class="hero-stat"><b>{len(subjects)}</b><span>subjects</span></div>
            <div class="hero-stat"><b>{n_q}</b><span>questions</span></div>
            <div class="hero-stat"><b>{n_t}</b><span>mock tests</span></div>
          </div>
        </div>""")

    if not U.has_content():
        with st.container(border=True):
            st.markdown("#### Nothing here yet")
            st.write("Add your own questions from the **Admin** page, or load a small demo set to see how the app looks.")
            a, b = st.columns(2)
            a.button("Load demo questions", type="primary", on_click=load_demo)
            b.button("Go to Admin", on_click=go, args=("admin",))
        return

    prog = U.load_progress(user())
    st.markdown("### Your progress")
    dashboard(prog, subjects)

    if subjects:
        st.markdown("### Practice by subject")
        for r in range(0, len(subjects), 3):
            cols = st.columns(3)
            for col, (slug, name) in zip(cols, subjects[r:r + 3]):
                with col:
                    with st.container(border=True, key=f"sub_{slug}"):
                        md(f'<div class="card-title">{esc(name)}</div><div class="card-sub">{pcount[slug]} questions</div>')
                        st.button("Start practice", key=f"go_{slug}", on_click=open_subject, args=(slug,),
                                  disabled=pcount[slug] == 0)

    if series:
        st.markdown("### Mock test series")
        for r in range(0, len(series), 3):
            cols = st.columns(3)
            for col, s in zip(cols, series[r:r + 3]):
                with col:
                    with st.container(border=True, key=f"ser_{s}"):
                        n = len(U.list_tests(s))
                        md(f'<div class="card-title">{esc(U.pretty(s))}</div><div class="card-sub">{n} test{"s" if n != 1 else ""}</div>')
                        st.button("Open series", key=f"gs_{s}", on_click=open_series, args=(s,))

    hist = U.load_results(user())
    if hist:
        st.markdown("### Your recent mock scores")
        df = history_df(hist)
        c1, c2 = st.columns([2, 1])
        with c1:
            md(score_chart(df.iloc[::-1]["Score %"].tolist()))
        with c2:
            md(f"""<div class="tiles">
                <div class="tile"><b>{len(df)}</b><span>tests attempted</span></div>
                <div class="tile ok"><b>{df['Score %'].max():.0f}%</b><span>best score</span></div>
                <div class="tile"><b>{df['Score %'].mean():.0f}%</b><span>average</span></div></div>""")


# =====================================================================
# QUIZ ENGINE (used by Practice, Mixed quiz and Revision)
# =====================================================================
def _pq(ns):
    return S.pq[ns]


def _p_go(ns, d):
    P = _pq(ns)
    P["i"] = max(0, min(len(P["order"]) - 1, P["i"] + d))


def _p_jump(ns, j):
    _pq(ns)["i"] = j


def _p_restart(ns):
    S.pq.pop(ns, None)


def _on_pick(ns, i, wkey):
    """Runs the moment an option is tapped: check it, and move on if it was right."""
    P = S.get("pq", {}).get(ns)
    if not P or i in P["checked"]:
        return
    choice = S.get(wkey)
    if choice is None:
        return
    q = P["qs"][P["order"][i]]
    ok = choice == q["answer"]
    P["picked"][i] = choice
    P["checked"][i] = True
    U.record_answers(user(), [(q["_key"], ok, q["_group"])])
    advance = ok and S.get("auto_next", True) and i < len(P["order"]) - 1
    if advance:
        P["i"] = i + 1
    try:
        st.toast("✅ Correct! Next question." if advance else "✅ Correct!" if ok else "❌ Not quite. See the answer below.")
    except Exception:
        pass


def run_quiz(ns, sig, qs_fn, shuffle=False, empty="No questions here yet."):
    """ns = unique name of this quiz; sig changes -> a new run starts; qs_fn() builds the question list."""
    S.setdefault("pq", {})
    keep("auto_next")
    P = S.pq.get(ns)
    if P is None or P["sig"] != sig:
        qs = qs_fn()
        if not qs:
            S.pq.pop(ns, None)
            st.warning(empty)
            return
        order = list(range(len(qs)))
        if shuffle:
            random.shuffle(order)
        P = S.pq[ns] = {"sig": sig, "qs": qs, "order": order, "i": 0, "picked": {}, "checked": {},
                        "run": uuid.uuid4().hex[:6], "celebrated": False}
    qs = P["qs"]
    n, i = len(P["order"]), P["i"]
    q = qs[P["order"][i]]
    saved = set(U.load_progress(user())["bm"])
    done = len(P["checked"])
    correct = sum(1 for k in P["checked"] if P["picked"][k] == qs[P["order"][k]]["answer"])
    acc = f"{correct / done * 100:.0f}%" if done else "–"

    c1, c2 = st.columns([5, 1], vertical_alignment="center")
    c1.markdown(H(f"""<div class="chips"><span class="chip">Attempted {done}/{n}</span>
        <span class="chip green">Correct {correct}</span><span class="chip red">Wrong {done - correct}</span>
        <span class="chip gold">Accuracy {acc}</span></div>"""), unsafe_allow_html=True)
    c2.button("Restart", key=f"rs_{ns}", on_click=_p_restart, args=(ns,))
    st.progress(done / n)
    st.checkbox("Go to the next question automatically when my answer is correct", value=True, key="auto_next")

    if done == n:
        _quiz_summary(ns, P, correct, n)

    checked = i in P["checked"]
    with st.container(key=f"qcard_{ns}"):
        md(f'<div class="qmeta">Question {i + 1} of {n} &nbsp;<span class="chip">{esc(q["_group"])}</span></div>')
        st.markdown(q["question"])

    if checked:
        option_cards(q, P["picked"][i])
        choice = P["picked"][i]
    else:
        wkey = f"p_{ns}_{P['run']}_{i}"
        with st.container(key=f"optbox_{ns}"):
            st.radio("Options", list(range(len(q["options"]))), index=P["picked"].get(i),
                     format_func=opt_fmt(q["options"]), key=wkey, label_visibility="collapsed",
                     on_change=_on_pick, args=(ns, i, wkey))
        st.caption("Tap an option to answer. It is checked straight away.")

    b1, b2, b3 = st.columns(3)
    b1.button("⬅ Previous", key=f"pv_{ns}", disabled=(i == 0), on_click=_p_go, args=(ns, -1))
    b2.button("🔖 Saved" if q["_key"] in saved else "🔖 Save", key=f"bm_{ns}", on_click=toggle_bm, args=(q["_key"],))
    b3.button("Next ➡", key=f"nx_{ns}", disabled=(i == n - 1), on_click=_p_go, args=(ns, 1), type="primary")

    if checked:
        if P["picked"][i] == q["answer"]:
            md('<div class="verdict ok">Correct. Well done!</div>')
        else:
            md('<div class="verdict bad">Not quite. The correct answer is highlighted above, and this question is added to <b>My mistakes</b>.</div>')
        with st.expander("💡 Explanation", expanded=P["picked"][i] != q["answer"]):
            st.write(q["explanation"] or "No explanation added for this question.")

    with st.expander("Jump to a question"):
        per = 10
        for r in range(0, n, per):
            cols = st.columns(per)
            for off, col in enumerate(cols):
                j = r + off
                if j >= n:
                    break
                mark = ""
                if j in P["checked"]:
                    mark = "✓" if P["picked"][j] == qs[P["order"][j]]["answer"] else "✗"
                col.button(f"{j + 1}{mark}", key=f"pj_{ns}_{j}", on_click=_p_jump, args=(ns, j),
                           type="primary" if j == i else "secondary")


def _quiz_summary(ns, P, correct, n):
    pct = correct / n * 100
    if pct >= 80 and not P["celebrated"]:
        P["celebrated"] = True
        st.balloons()
    with st.container(border=True):
        a, b = st.columns([1, 3], vertical_alignment="center")
        a.markdown(ring(pct, f"{pct:.0f}%", "accuracy"), unsafe_allow_html=True)
        with b:
            msg = ("Excellent work!" if pct >= 80 else
                   "Good effort. Review the wrong answers." if pct >= 50 else
                   "Keep going. Read the explanations and try again.")
            st.markdown(f"#### Set complete: {correct} of {n} correct")
            st.write(msg)
            st.button("Start again", key=f"again_{ns}", type="primary", on_click=_p_restart, args=(ns,))


# =====================================================================
# PRACTICE
# =====================================================================
def practice_page():
    page_head("Practice questions", "Tap an answer to check it instantly. Correct answers move you on automatically.")
    subjects = U.list_subjects()
    if not subjects:
        st.info("No subjects yet. Add questions from the Admin page.")
        return
    names = dict(subjects)
    if S.get("p_subject") not in names:
        S.pop("p_subject", None)
    keep("p_mode", "p_subject", "p_shuffle")

    mode = st.radio("Mode", ["By subject", "Mixed quiz"], horizontal=True, key="p_mode", label_visibility="collapsed")
    with st.container(border=True):
        if mode == "By subject":
            c1, c2 = st.columns([4, 1], vertical_alignment="bottom")
            slug = c1.selectbox("Subject", list(names), format_func=names.get, key="p_subject")
            shuffle = c2.checkbox("Shuffle", key="p_shuffle")
        else:
            c1, c2 = st.columns([4, 1], vertical_alignment="bottom")
            chosen = c1.multiselect("Subjects to include", list(names), default=list(names),
                                    format_func=names.get, key="mix_subjects")
            count = c2.number_input("Questions", 5, 100, 10, 5, key="mix_count")

    if mode == "By subject":
        qs = U.subject_questions(slug)
        run_quiz(f"subj_{slug}", (slug, shuffle, len(qs)), lambda: qs, shuffle,
                 empty="This subject has no questions yet.")
    else:
        if not chosen:
            st.info("Pick at least one subject.")
            return

        def build():
            pool = [q for s in chosen for q in U.subject_questions(s)]
            return random.sample(pool, min(int(count), len(pool)))

        run_quiz("mixed", (tuple(sorted(chosen)), int(count)), build, False, empty="No questions found.")


# =====================================================================
# REVISION
# =====================================================================
def revision_page():
    page_head("Revision", "Questions you saved and the ones you got wrong, ready to practise again.")
    prog = U.load_progress(user())
    bm, mk = prog["bm"], U.mistake_keys(prog)
    keep("rev_kind")
    labels = {"saved": f"🔖 Saved ({len(bm)})", "mistakes": f"🔁 My mistakes ({len(mk)})"}
    pick = st.radio("Revise", list(labels), format_func=labels.get, horizontal=True,
                    label_visibility="collapsed", key="rev_kind")
    saved_mode = pick == "saved"
    keys = bm if saved_mode else mk
    if not keys:
        st.info("Nothing saved yet. Tap **🔖 Save** on any question while practising." if saved_mode
                else "No mistakes to revise. Questions you answer wrongly appear here until you get them right.")
        return
    ns = "rev_saved" if saved_mode else "rev_mistakes"
    run_quiz(ns, ("rev", ns), lambda: U.questions_for(keys), shuffle=True, empty="Those questions no longer exist.")


# =====================================================================
# NOTES
# =====================================================================
def show_pdf(data: bytes) -> None:
    """In-app PDF reader. Falls back to the browser's viewer if st.pdf is unavailable."""
    import base64
    try:
        if not hasattr(st, "pdf"):
            raise RuntimeError("st.pdf not available")
        st.pdf(data, height=620)
        return
    except Exception:
        pass
    if len(data) > 8_000_000:
        st.info("This PDF is large. Please use the Download button to read it.")
        return
    b64 = base64.b64encode(data).decode()
    st.markdown(f'<iframe src="data:application/pdf;base64,{b64}" width="100%" height="620" '
                f'style="border:1px solid #D8E0DA;border-radius:12px"></iframe>', unsafe_allow_html=True)
    st.caption("If the preview is blank on your phone, tap Download PDF and open it in your PDF app.")


def size_label(n: int) -> str:
    return f"{n / 1_000_000:.1f} MB" if n >= 1_000_000 else f"{max(1, n // 1000)} KB"


def notes_page():
    page_head("Notes & concepts", "Revision notes from your teacher. Read them here or download the PDF.")
    notes = U.list_notes()
    if not notes:
        st.info("No notes yet. Your teacher can add PDF notes from the Admin page.")
        return
    subjects = sorted({n["subject"] for n in notes})
    if S.get("n_subject") not in ["All"] + subjects:
        S.pop("n_subject", None)
    keep("n_subject")
    c1, c2 = st.columns([2, 3])
    subj = c1.selectbox("Subject", ["All"] + subjects, key="n_subject")
    term = c2.text_input("Search notes", placeholder="Type a topic, e.g. Piaget").strip().lower()
    shown = [n for n in notes
             if (subj == "All" or n["subject"] == subj)
             and term in f'{n["title"]} {n.get("description", "")} {n.get("text", "")}'.lower()]
    if not shown:
        st.caption("No notes match your search.")
    for n in shown:
        kind = f'PDF · {size_label(n.get("size", 0))}' if n["kind"] == "pdf" else "Quick note"
        with st.container(border=True, key=f"note_{n['id']}"):
            md(f"""<div class="card-title">{esc(n['title'])}</div>
                <div class="chips"><span class="chip">{esc(n['subject'])}</span>
                <span class="chip gold">{kind}</span><span class="chip">{esc(n['added'][:10])}</span></div>""")
            if n.get("description"):
                st.write(n["description"])
            if n["kind"] == "pdf":
                data = U.read_note_file(n["id"])
                if not data:
                    st.warning("This file is missing on the server.")
                    continue
                a, b = st.columns(2)
                a.download_button("⬇ Download PDF", data, file_name=f"{U.slugify(n['title'])}.pdf",
                                  mime="application/pdf", key=f"dl_{n['id']}")
                if b.checkbox("👁 Read here", key=f"view_{n['id']}"):
                    show_pdf(data)
            else:
                with st.expander("📖 Read note"):
                    st.markdown(n["text"])


# =====================================================================
# TEST SERIES
# =====================================================================
def _start_test(series, test):
    d = U.load_test(series, test)
    now = time.time()
    S.t = {
        "series": series, "test": test, "title": d["title"], "qs": d["questions"],
        "marks": d.get("marks_per_question", 1), "neg": d.get("negative_marks", 0),
        "start": now, "end": now + d.get("duration_minutes", 30) * 60, "finished": None,
        "answers": {}, "flags": set(), "cur": 0, "submitted": False, "saved": False, "delta": None,
        "run": uuid.uuid4().hex[:6],
    }


def _t_goto(j):
    S.t["cur"] = max(0, min(len(S.t["qs"]) - 1, j))


def _t_submit():
    S.t["submitted"] = True
    S.t["finished"] = min(time.time(), S.t["end"])


def _t_clear(cur, key):
    S.t["answers"].pop(cur, None)
    S.pop(key, None)


def _t_flag(cur):
    f = S.t["flags"]
    f.discard(cur) if cur in f else f.add(cur)


def _t_exit():
    S.t = None


def test_menu():
    series = U.list_series()
    if not series:
        st.info("No test series yet. Add one from the Admin page.")
        return
    if S.get("t_series") not in series:
        S.pop("t_series", None)
    keep("t_series")
    s = st.selectbox("Test series", series, format_func=U.pretty, key="t_series")
    tests = U.list_tests(s)
    hist = U.load_results(user())
    if not tests:
        st.warning("This series has no tests yet.")
    for slug, title in tests:
        d = U.load_test(s, slug)
        nq, mpq = len(d["questions"]), d.get("marks_per_question", 1)
        mine = [r for r in hist if r["series"] == U.pretty(s) and r["test"] == title]
        best = ""
        if mine:
            b = max(mine, key=lambda r: float(r["score"]))
            best = f'<span class="chip green">Best {float(b["score"]):g}/{float(b["max_score"]):g}</span>'
        with st.container(border=True):
            a, b = st.columns([4, 1], vertical_alignment="center")
            with a:
                md(f"""<div class="card-title">{esc(title)}</div>
                    <div class="chips"><span class="chip">{nq} questions</span>
                    <span class="chip">{d.get('duration_minutes', 30)} min</span>
                    <span class="chip gold">+{mpq:g} / -{d.get('negative_marks', 0):g}</span>{best}</div>""")
            b.button("Start test", key=f"start_{s}_{slug}", type="primary", disabled=not nq,
                     on_click=_start_test, args=(s, slug))
    if hist:
        with st.expander("📈 My previous attempts", expanded=False):
            df = history_df(hist)
            show_df(df.rename(columns={"time": "When", "series": "Series", "test": "Test", "score": "Score",
                                       "max_score": "Out of", "correct": "Correct", "wrong": "Wrong",
                                       "unattempted": "Skipped"}))


@st.fragment(run_every=1)
def timer_box():
    t = S.t
    left = int(t["end"] - time.time())
    if left <= 0:
        t["submitted"] = True
        t["finished"] = t["end"]
        st.rerun()  # full app rerun -> shows the result
    cls = "timer warn" if left <= 300 else "timer"
    md(f'<div class="{cls}"><small>Time left</small><b>{mmss(left)}</b></div>')


def _palette_css(t) -> str:
    rules = []
    for j in range(len(t["qs"])):
        if j == t["cur"]:
            style = "background:#14342B !important;color:#F2B01E !important;border:2px solid #F2B01E !important;"
        elif j in t["flags"]:
            style = "background:#F2B01E !important;color:#3D2C00 !important;border-color:#C98F0A !important;"
        elif j in t["answers"]:
            style = "background:#CFEBDD !important;color:#0F5236 !important;border-color:#8CCBAE !important;"
        else:
            continue
        rules.append(f".st-key-pal_{j} button{{{style}}}.st-key-pal_{j} button p{{color:inherit !important;}}")
    return "<style>" + "".join(rules) + "</style>"


def test_running():
    t = S.t
    qs, n, cur = t["qs"], len(t["qs"]), t["cur"]
    h1, h2 = st.columns([3, 1], vertical_alignment="center")
    h1.markdown(f"### {t['title']}")
    with h2:
        timer_box()

    st.markdown(_palette_css(t), unsafe_allow_html=True)
    main, side = st.columns([3, 1.1])

    with side:
        with st.container(border=True):
            st.markdown("**Question palette**")
            per = 5
            for r in range(0, n, per):
                cols = st.columns(per)
                for off, col in enumerate(cols):
                    j = r + off
                    if j < n:
                        col.button(str(j + 1), key=f"pal_{j}", on_click=_t_goto, args=(j,))
            md("""<div class="legend">
                <span><i style="background:#14342B"></i>Current</span>
                <span><i style="background:#CFEBDD"></i>Answered</span>
                <span><i style="background:#F2B01E"></i>For review</span>
                <span><i style="background:#fff"></i>Not visited</span></div>""")
            st.caption(f"{len(t['answers'])} answered  •  {len(t['flags'])} flagged  •  {n - len(t['answers'])} left")

    with main:
        q = qs[cur]
        with st.container(key="qcard_test"):
            flag = " 🚩" if cur in t["flags"] else ""
            md(f'<div class="qmeta">Question {cur + 1} of {n}{flag}</div>')
            st.markdown(q["question"])
        key = f"t_{t['run']}_{cur}"
        with st.container(key="optbox_test"):
            choice = st.radio("Options", list(range(len(q["options"]))), index=t["answers"].get(cur),
                              format_func=opt_fmt(q["options"]), key=key, label_visibility="collapsed")
        if choice is not None:
            t["answers"][cur] = choice

        b1, b2, b3, b4, b5 = st.columns([1, 1.3, 1, 1, 1.3])
        b1.button("⬅ Prev", disabled=cur == 0, on_click=_t_goto, args=(cur - 1,))
        b2.button("Unflag" if cur in t["flags"] else "🚩 Mark for review", on_click=_t_flag, args=(cur,))
        b3.button("Clear", on_click=_t_clear, args=(cur, key))
        b4.button("Next ➡", disabled=cur == n - 1, on_click=_t_goto, args=(cur + 1,))
        with b5.popover("Submit test"):
            left = n - len(t["answers"])
            st.write(f"Answered **{len(t['answers'])}** of **{n}**.")
            if left:
                st.write(f"**{left}** question{'s' if left != 1 else ''} left unanswered.")
            if t["flags"]:
                st.write(f"**{len(t['flags'])}** marked for review.")
            st.button("Yes, submit now", type="primary", on_click=_t_submit)


def test_result():
    t = S.t
    qs, ans = t["qs"], t["answers"]
    correct = sum(1 for j, a in ans.items() if a == qs[j]["answer"])
    wrong = len(ans) - correct
    skipped = len(qs) - len(ans)
    score = correct * t["marks"] - wrong * t["neg"]
    max_score = len(qs) * t["marks"]
    pct = (score / max_score * 100) if max_score else 0
    taken = int((t["finished"] or time.time()) - t["start"])

    if not t["saved"]:
        title_pretty = U.pretty(t["series"])
        prev = [r for r in U.load_results(user()) if r["series"] == title_pretty and r["test"] == t["title"]]
        if prev:
            t["delta"] = round(score - float(prev[0]["score"]), 2)
        U.save_result({"series": title_pretty, "test": t["title"], "score": round(score, 2),
                       "max_score": max_score, "correct": correct, "wrong": wrong, "unattempted": skipped}, user())
        U.record_answers(user(), [(U.tkey(t["series"], t["test"], qs[j]), a == qs[j]["answer"], "Mock tests")
                                  for j, a in ans.items()])
        t["saved"] = True
        if pct >= 80:
            st.balloons()

    st.markdown(f"### Result: {t['title']}")
    with st.container(border=True):
        a, b = st.columns([1, 3], vertical_alignment="center")
        a.markdown(ring(pct, f"{score:g}", f"out of {max_score:g}"), unsafe_allow_html=True)
        with b:
            verdict = ("Outstanding. You are exam-ready." if pct >= 80 else
                       "Good progress. A little more revision will push you higher." if pct >= 60 else
                       "Getting there. Study the explanations below and retake." if pct >= 40 else
                       "Time to revise the basics. Every attempt makes the next one better.")
            st.write(verdict)
            if t["delta"] is not None:
                d = t["delta"]
                cls = "green" if d > 0 else "red" if d < 0 else "gold"
                txt = f"{d:+g} marks vs your last attempt" if d else "Same as your last attempt"
                md(f'<div class="chips" style="margin:0 0 .6rem"><span class="chip {cls}">{txt}</span></div>')
            md(f"""<div class="tiles">
                <div class="tile ok"><b>{correct}</b><span>correct</span></div>
                <div class="tile bad"><b>{wrong}</b><span>wrong</span></div>
                <div class="tile"><b>{skipped}</b><span>skipped</span></div>
                <div class="tile"><b>{mmss(taken)}</b><span>time taken</span></div></div>""")
    r1, r2 = st.columns(2)
    r1.button("Retake this test", type="primary", on_click=_start_test, args=(t["series"], t["test"]))
    r2.button("⬅ Back to test series", on_click=_t_exit)

    st.markdown("### Review & explanations")
    flt = st.radio("Show", ["All", "Wrong", "Correct", "Skipped"], horizontal=True, label_visibility="collapsed")
    saved = set(U.load_progress(user())["bm"])
    shown = 0
    for j, q in enumerate(qs):
        your = ans.get(j)
        state = "Skipped" if your is None else ("Correct" if your == q["answer"] else "Wrong")
        if flt != "All" and state != flt:
            continue
        shown += 1
        icon = {"Skipped": "⚪", "Correct": "✅", "Wrong": "❌"}[state]
        k = U.tkey(t["series"], t["test"], q)
        with st.expander(f"{icon}  Q{j + 1}. {q['question'][:90]}"):
            st.markdown(f"**{q['question']}**")
            option_cards(q, your)
            st.info(q["explanation"] or "No explanation added.")
            st.button("🔖 Saved for revision" if k in saved else "🔖 Save for revision", key=f"rv_{j}",
                      on_click=toggle_bm, args=(k,))
    if not shown:
        st.caption("Nothing to show for this filter.")


def test_page():
    t = S.get("t")
    if t is None:
        page_head("Test series", "Timed mock tests with a question palette, review flags and full solutions.")
        test_menu()
    elif t["submitted"]:
        test_result()
    else:
        test_running()


# =====================================================================
# ADMIN
# =====================================================================
def _admin_password():
    try:
        return st.secrets["ADMIN_PASSWORD"]
    except Exception:
        return "admin123"


def target_selector(prefix):
    """Pick where questions go. Returns a dict or None."""
    kind = st.radio("Add to", ["Practice (subject-wise)", "Test Series"], horizontal=True, key=f"{prefix}_kind")
    if kind.startswith("Practice"):
        subs = U.list_subjects()
        names = [n for _, n in subs]
        ch = st.selectbox("Subject", names + [NEW], key=f"{prefix}_sub")
        name = st.text_input("New subject name", key=f"{prefix}_subnew") if ch == NEW else ch
        return {"kind": "practice", "subject": name} if name.strip() else None

    series = U.list_series()
    sc = st.selectbox("Test series", series + [NEW], format_func=lambda s: s if s == NEW else U.pretty(s),
                      key=f"{prefix}_ser")
    sname = st.text_input("New test series name", key=f"{prefix}_sernew") if sc == NEW else sc
    if not sname.strip():
        return None
    tmap = dict(U.list_tests(sc)) if sc != NEW else {}
    tc = st.selectbox("Test", list(tmap) + [NEW], format_func=lambda s: s if s == NEW else tmap[s],
                      key=f"{prefix}_test_{sc}")
    settings = None
    if tc == NEW:
        tname = st.text_input("New test name (e.g. Mock Test 1)", key=f"{prefix}_testnew")
        a, b, c = st.columns(3)
        settings = {
            "duration_minutes": a.number_input("Duration (min)", 1, 300, 150, key=f"{prefix}_dur"),
            "marks_per_question": b.number_input("Marks / question", 0.0, 10.0, 1.0, 0.25, key=f"{prefix}_mk"),
            "negative_marks": c.number_input("Negative marks", 0.0, 10.0, 0.0, 0.25, key=f"{prefix}_neg"),
        }
    else:
        tname = tc
    return {"kind": "test", "series": sname, "test": tname, "settings": settings} if tname.strip() else None


def save_to_target(tg, questions):
    if tg["kind"] == "practice":
        return U.add_practice(tg["subject"], questions)
    return U.add_test(tg["series"], tg["test"], questions, tg["settings"])


def report_added(added, total):
    skipped = total - added
    msg = f"Added {added} question{'s' if added != 1 else ''} ✅"
    if skipped:
        msg += f"  ({skipped} duplicate{'s' if skipped != 1 else ''} skipped)"
    (st.success if added else st.info)(msg)


SAMPLE_CSV = (
    "question,option_a,option_b,option_c,option_d,answer,explanation\n"
    "Capital of India?,Mumbai,New Delhi,Kolkata,Chennai,B,New Delhi is the capital of India.\n"
)
SAMPLE_JSON = json.dumps([{
    "question": "Capital of India?", "options": ["Mumbai", "New Delhi", "Kolkata", "Chennai"],
    "answer": "B", "explanation": "New Delhi is the capital of India."}], indent=2)


def _admin_login():
    page_head("Admin", "Sign in to add and manage questions.")
    with st.form("login"):
        pw = st.text_input("Admin password", type="password")
        ok = st.form_submit_button("Log in", type="primary")
    if ok:
        if pw == _admin_password():
            S.admin = True
            st.rerun()
        else:
            st.error("Wrong password.")


def admin_page():
    if not S.get("admin"):
        _admin_login()
        return

    page_head("Admin", "Add questions, import in bulk, review students and keep your content tidy.")
    if _admin_password() == "admin123":
        st.warning("You are using the default password. Change `ADMIN_PASSWORD` in `.streamlit/secrets.toml`.")

    t1, t2, t_notes, t3, t4 = st.tabs(["➕ Add one question", "📤 Bulk upload", "📄 Notes", "🗂 Manage", "👥 Students"])

    with t1:
        tg = target_selector("one")
        with st.form("add_q", clear_on_submit=True):
            question = st.text_area("Question")
            o = [st.text_input(f"Option {c}") for c in "ABCD"]
            ans = st.selectbox("Correct answer", list("ABCD"))
            expl = st.text_area("Explanation / solution")
            ok = st.form_submit_button("Add question", type="primary")
        if ok:
            if not tg:
                st.error("Choose or type a target subject / test first.")
            else:
                try:
                    q = U.normalize_question({"question": question, "options": o, "answer": ans, "explanation": expl})
                    report_added(save_to_target(tg, [q]), 1)
                except Exception as e:
                    st.error(f"Could not add: {e}")

    with t2:
        st.caption("Upload a CSV or JSON file with many questions at once. Duplicates are skipped automatically.")
        d1, d2 = st.columns(2)
        d1.download_button("⬇ CSV template", SAMPLE_CSV, "template.csv", "text/csv")
        d2.download_button("⬇ JSON template", SAMPLE_JSON, "template.json", "application/json")
        tg2 = target_selector("bulk")
        up = st.file_uploader("Upload file", type=["csv", "json"])
        if up:
            qs, errs = U.parse_upload(up.name, up.getvalue())
            st.write(f"Valid questions found: **{len(qs)}**")
            for e in errs:
                st.warning(e)
            if qs:
                with st.expander("Preview first questions"):
                    for q in qs[:3]:
                        st.markdown(f"**{q['question']}**")
                        option_cards(q, None)
            if qs and st.button("Import questions", type="primary"):
                if not tg2:
                    st.error("Choose or type a target subject / test first.")
                else:
                    report_added(save_to_target(tg2, qs), len(qs))

    with t_notes:
        _admin_notes()

    with t3:
        _admin_manage()

    with t4:
        _admin_students()

    st.sidebar.divider()
    st.sidebar.button("Log out of admin", key="logout", on_click=lambda: S.update(admin=False))


def _admin_notes():
    st.markdown("##### Add notes for students")
    kind = st.radio("Type", ["PDF file", "Typed note"], horizontal=True, key="note_kind")
    subs = [n for _, n in U.list_subjects()]
    ch = st.selectbox("Subject", ["General"] + subs + [NEW], key="note_sub")
    subject = st.text_input("New subject name", key="note_subnew") if ch == NEW else ch
    with st.form("note_form", clear_on_submit=True):
        title = st.text_input("Title", placeholder="e.g. Piaget's stages - concept notes")
        desc = st.text_area("Short description (optional)", height=80)
        if kind == "PDF file":
            up = st.file_uploader("PDF file", type=["pdf"])
            text = None
        else:
            up = None
            text = st.text_area("Note (Markdown works: **bold**, lists, tables)", height=220)
        ok = st.form_submit_button("Save note", type="primary")
    if ok:
        try:
            if kind == "PDF file":
                if up is None:
                    raise ValueError("choose a PDF file first")
                title = title.strip() or up.name.rsplit(".", 1)[0]
                U.add_note(title, subject, desc, pdf_bytes=up.getvalue())
            else:
                U.add_note(title, subject, desc, text=text)
            st.success("Note saved ✅ Students can see it on the Notes page.")
        except Exception as e:
            st.error(f"Could not save: {e}")

    notes = U.list_notes()
    st.divider()
    st.markdown(f"##### Existing notes ({len(notes)})")
    if not notes:
        st.caption("Nothing uploaded yet.")
        return
    show_df([{"Title": n["title"], "Subject": n["subject"],
              "Type": "PDF" if n["kind"] == "pdf" else "Typed", "Added": n["added"]} for n in notes])
    labels = {n["id"]: f'{n["title"]}  ({n["subject"]})' for n in notes}
    pick = st.selectbox("Select a note to delete", list(labels), format_func=labels.get, key="note_del")
    if st.button("🗑 Delete selected note"):
        U.delete_note(pick)
        st.rerun()


def _admin_students():
    rows = []
    for slug, name in U.list_students():
        hist = U.load_results(slug)
        prog = U.load_progress(slug)
        answered = sum(v["a"] for v in prog["groups"].values())
        right = sum(v["c"] for v in prog["groups"].values())
        avg = f"{history_df(hist)['Score %'].mean():.0f}%" if hist else "–"
        last = max(prog["days"]) if prog["days"] else "–"
        rows.append({"Student": name, "Tests taken": len(hist), "Avg mock score": avg,
                     "Questions answered": answered, "Accuracy": f"{right / answered * 100:.0f}%" if answered else "–",
                     "Streak (days)": U.streak(prog), "Last active": last})
    if rows:
        show_df(rows)
    else:
        st.info("No student activity yet. Students enter their name in the sidebar to keep their own progress.")
    st.download_button("⬇ Backup everything (ZIP)", U.backup_zip(), "supertet_backup.zip", "application/zip")


def _admin_manage():
    sets = U.all_sets()
    if not sets:
        st.info("Nothing to manage yet.")
        return
    labels = [l for l, _ in sets]
    label = st.selectbox("Select set", labels)
    path = dict(sets)[label]
    data = U.read_set(path)
    qs = data["questions"]
    st.write(f"**{len(qs)}** questions")
    term = st.text_input("Search questions", placeholder="Type a word to filter").strip().lower()
    table = [{"No.": i + 1, "Question": q["question"], "Answer": chr(65 + q["answer"])}
             for i, q in enumerate(qs) if term in q["question"].lower()]
    show_df(table)
    st.download_button("⬇ Download this set (JSON)", json.dumps(data, ensure_ascii=False, indent=2),
                       file_name=path.name, mime="application/json")

    if qs:
        st.markdown("##### Edit or delete a question")
        num = int(st.number_input("Question number", 1, len(qs), 1, key="manage_num"))
        q = qs[num - 1]
        with st.form(f"edit_form_{num}_{len(qs)}"):
            new_q = st.text_area("Question", q["question"])
            new_o = [st.text_input(f"Option {chr(65 + k)}", o) for k, o in enumerate(q["options"])]
            new_a = st.selectbox("Correct answer", [chr(65 + k) for k in range(len(q["options"]))], index=q["answer"])
            new_e = st.text_area("Explanation", q["explanation"])
            save = st.form_submit_button("Save changes", type="primary")
        if save:
            try:
                qs[num - 1] = U.normalize_question({"id": q["id"], "question": new_q, "options": new_o,
                                                     "answer": new_a, "explanation": new_e})
                U.write_set(path, data)
                st.success("Saved ✅")
                st.rerun()
            except Exception as e:
                st.error(f"Could not save: {e}")
        if st.button("🗑 Delete this question"):
            qs.pop(num - 1)
            U.write_set(path, data)
            st.rerun()

    st.divider()
    if st.checkbox("I want to delete this entire set"):
        if st.button("❌ Delete set", type="primary"):
            U.delete_set(path)
            st.rerun()


# =====================================================================
# NAVIGATION
# =====================================================================
PAGES = {
    "home": ("🏠", "Home", home_page),
    "practice": ("📝", "Practice", practice_page),
    "revision": ("🔖", "Revision", revision_page),
    "notes": ("📚", "Notes", notes_page),
    "tests": ("🧪", "Test Series", test_page),
    "admin": ("⚙️", "Admin", admin_page),
}
if S.get("page") not in PAGES:
    S.page = "home"

with st.sidebar:
    md('<div class="brand"><b>SuperTET PRT</b><span>Practice &amp; mock tests</span></div>')
    for key, (icon, label, _) in PAGES.items():
        st.button(f"{icon}  {label}", key=f"nav_{key}", on_click=go, args=(key,))
    st.markdown(
        f"<style>section[data-testid=\"stSidebar\"] .st-key-nav_{S.page} button{{background:#F2B01E !important;color:#2B2100 !important;"
        f"border-color:#F2B01E !important;}}section[data-testid=\"stSidebar\"] .st-key-nav_{S.page} button *{{color:#2B2100 !important;}}</style>",
        unsafe_allow_html=True,
    )
    st.divider()
    keep("student_name")
    name = st.text_input("Your name", key="student_name", placeholder="Guest",
                         help="Type your name to keep your own scores, streak and saved questions.")
    S.user = U.slugify(name) if name.strip() else ""
    _prog = U.load_progress(S.user)
    goal = st.number_input("Daily goal (questions)", 5, 200, int(_prog["goal"]), 5)
    if int(goal) != int(_prog["goal"]):
        U.set_goal(S.user, goal)
    if S.get("t") and not S.t["submitted"] and S.page != "tests":
        md('<div class="side-note">⏱ A test is running. The timer keeps counting.</div>')

st.markdown(f"<style>{H(CSS)}</style>", unsafe_allow_html=True)
PAGES[S.page][2]()
