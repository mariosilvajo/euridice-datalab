"""EURIDICE DataLab — ethics-in-the-loop measurement helpers.

Turn ethical questions into one-line, runnable measurements. Every helper
prints its result plus two guidance lines:

  🔎 what to look for   — how to read the number you just produced
  ⚖️ framework          — where this lands in EU law / Digital Humanism

It also keeps the learner's **portfolio**: the written judgments from every
ethics lab, plus the capstone model card, exportable as one HTML file that
can be submitted for formal assessment.

Loaded in a notebook with:  %run datalab_ethics.py
"""

import base64
import html
import json
import math
import sys
from datetime import datetime
from pathlib import Path

# IMPORTANT — only standard-library imports at the top of this file.
# In the browser, Pyodide loads packages such as pandas only when a *cell's own
# code* imports them; `%run datalab_ethics.py` does not trigger that. A
# top-level `import pandas` therefore fails in a fresh kernel, %run swallows
# the error, and every helper below goes missing. Functions that need pandas
# import it themselves — by the time they are called, the learner's data has
# loaded it. (scripts/check_notebooks.py enforces this rule.)

try:  # Windows consoles default to cp1252; the browser kernel is already UTF-8
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass

print("Ethics lab loaded — group_performance(), selection_rate_ratio(), representation(), "
      "compare_groups(), fairness_table() and reflect_submit() are ready. "
      "Portfolio: show_portfolio(), model_card(), export_portfolio().")


def _as_series(values, index):
    import pandas as pd  # loaded lazily — see the note at the top
    s = values if isinstance(values, pd.Series) else pd.Series(list(values), index=index)
    return s.reindex(index)


def group_performance(model, X, y, by):
    """Accuracy and false-negative rate per group.

    A gap means the model works better for some people than others.
    False negatives are the people who *deserved* a positive outcome
    but were denied it by the model.
    """
    import pandas as pd  # loaded lazily — see the note at the top
    by = _as_series(by, X.index)
    pred = pd.Series(model.predict(X), index=X.index)
    rows = []
    for g in sorted(by.dropna().unique()):
        m = by == g
        acc = float((pred[m] == y[m]).mean())
        pos = m & (y == 1)
        fnr = float((pred[pos] == 0).mean()) if int(pos.sum()) else float("nan")
        rows.append({"group": g, "n": int(m.sum()),
                     "accuracy": round(acc, 2), "false_negative_rate": round(fnr, 2)})
    table = pd.DataFrame(rows).set_index("group")
    print(table.to_string(), "\n")

    worst = table["accuracy"].idxmin()
    gap = float(table["accuracy"].max() - table["accuracy"].min())
    fnr_worst = table["false_negative_rate"].idxmax()
    fnr_gap = float(table["false_negative_rate"].max() - table["false_negative_rate"].min())
    print(f"🔎 What to look for: accuracy differs by {gap:.0%} points across groups "
          f"(worst for '{worst}').")
    if fnr_gap > 0:
        print(f"   False negatives — people who would have succeeded but the model "
              f"predicted failure — hit '{fnr_worst}' hardest ({fnr_gap:.0%} points more often).")
    print("⚖️ Framework: unequal error rates are how models discriminate in practice. "
          "The EU AI Act obliges providers of high-risk systems to examine their data "
          "for bias (Art. 10) and to achieve consistent accuracy (Art. 15) — but it "
          "sets no numeric threshold. Judging 'how unequal is too unequal' is yours.")
    return table


def selection_rate_ratio(y_pred, groups):
    """The 'four-fifths rule' screen for disparate impact.

    Compares the rate of positive outcomes between groups. A ratio below
    0.8 is the classic red flag.

    Note on provenance: this is a **US** standard (EEOC Uniform Guidelines
    on Employee Selection Procedures, 1978, 29 CFR 1607.4(D)). It is not EU
    law and the EU prescribes no equivalent number — see the printed output.
    """
    import pandas as pd  # loaded lazily — see the note at the top
    pred = pd.Series(list(y_pred)).reset_index(drop=True)
    grp = pd.Series(list(groups)).reset_index(drop=True)
    rates = pred.groupby(grp).mean().astype(float)
    print("Positive-outcome rate per group:")
    for g, r in rates.items():
        print(f"   {g}: {r:.0%}")
    ratio = float(rates.min() / rates.max()) if float(rates.max()) > 0 else float("nan")
    print(f"\nSelection-rate ratio (min/max): {ratio:.2f}")
    if ratio < 0.8:
        print("⚠️  Below 0.80 — this FAILS the 'four-fifths rule', the most widely used "
              "screen for disparate impact.")
    else:
        print("🔎 Above 0.80 — this PASSES the 'four-fifths rule'. But the test only "
              "asks who RECEIVES a positive outcome; it says nothing about who the "
              "model gets WRONG. Always read group_performance() alongside it.")
    print("\n📏 Where this test comes from: the four-fifths rule is **US** law — the "
          "EEOC's Uniform Guidelines on Employee Selection Procedures (1978), "
          "29 CFR 1607.4(D). It is a screening heuristic, global only because every "
          "fairness toolkit ships it.")
    print("⚖️ What EU law says: **no numeric threshold exists.** Indirect "
          "discrimination (Directives 2000/43/EC, 2000/78/EC) is a qualitative test — "
          "does a neutral rule put a protected group at a 'particular disadvantage'? "
          "And the AI Act makes systems governing access to education high-risk "
          "(Annex III), requiring bias examination (Art. 10), transparency (Art. 13) "
          "and human oversight (Art. 14) — while prescribing no metric. "
          "Europe gives you duties, not a number: choosing the measure is your call.")
    return ratio


def representation(df, by):
    """Who is in the data — and who is missing from it?

    Shows each group's share of the dataset and how much missing data it
    carries. Under-represented groups get worse models; groups with more
    missing data get noisier ones.
    """
    import pandas as pd  # loaded lazily — see the note at the top
    counts = df[by].value_counts(dropna=False)
    share = counts / len(df)
    missing = df.isna().groupby(df[by]).mean().mean(axis=1)
    table = pd.DataFrame({"n": counts, "share": share.round(2),
                          "avg_missingness": missing.round(3)})
    print(table.to_string(), "\n")
    print(f"🔎 What to look for: groups with a small share or high missingness — "
          f"the model will understand them least.")
    print("⚖️ Framework: the EU AI Act requires training data for high-risk systems to "
          "be 'relevant, sufficiently representative' (Art. 10(3)) — representation is "
          "a legal duty, not just good practice. The Vienna Manifesto's call for "
          "inclusive technology starts in the same place: whose reality is in here?")
    return table


def compare_groups(df, value, by, min_n=30, plot=True):
    """Group averages WITH their uncertainty — before anything becomes a headline.

    For each group: how many people the number rests on, the average, and an
    approximate 95% confidence interval (mean ± 1.96·sd/√n). Groups smaller
    than `min_n` are flagged as too small to report on their own.

    Ranking check: when two neighbouring groups' intervals overlap, their
    order is uncertain. (Non-overlap is strong evidence of a real difference;
    overlap is a conservative signal to stop ranking — a rule of thumb, not a
    formal test.)
    """
    import pandas as pd  # loaded lazily — see the note at the top
    rows = []
    for g, s in df.groupby(by, observed=True)[value]:
        s = s.dropna()
        n = len(s)
        mean = float(s.mean()) if n else float("nan")
        half = float(1.96 * s.std(ddof=1) / math.sqrt(n)) if n > 1 else float("nan")
        rows.append({by: g, "n": n, "mean": round(mean, 2),
                     "ci_low": round(mean - half, 2), "ci_high": round(mean + half, 2),
                     "flag": "⚠️ too few to report alone" if n < min_n else ""})
    table = pd.DataFrame(rows).sort_values("mean", ascending=False).reset_index(drop=True)
    table.index = table.index + 1
    table.index.name = "rank"
    print(table.to_string(), "\n")

    steps = []
    for i in range(1, len(table)):
        upper, lower = table.loc[i], table.loc[i + 1]
        steps.append((upper[by], lower[by], upper["ci_low"] > lower["ci_high"]))
    clear = [f"{a} → {b}" for a, b, ok in steps if ok]
    small = table.loc[table["n"] < min_n, by].tolist()

    if steps:
        print(f"🔎 What to look for: of the {len(steps)} steps down this ranking, "
              f"{len(clear)} {'is' if len(clear) == 1 else 'are'} larger than the margin "
              f"of error{': ' + ', '.join(clear) if clear else ''}. Every other step is "
              f"within the noise — a ranking there claims more than the data shows.")
    if small:
        print(f"   Too few people to report alone (n < {min_n}): {', '.join(map(str, small))}. "
              f"Their interval is wide because the number rests on a handful of people.")
    print("⚖️ Framework: the European Statistics Code of Practice asks for *accuracy and "
          "reliability* and for statistics presented with *clarity* — which means stating "
          "uncertainty, not just averages. Tiny groups add a privacy risk: under GDPR "
          "(Recital 26) data is only anonymous if no one can be *singled out*, and a table "
          "cell describing one or two people can single them out.")

    if plot:
        import matplotlib.pyplot as plt
        ordered = table.iloc[::-1]
        err = [ordered["mean"] - ordered["ci_low"], ordered["ci_high"] - ordered["mean"]]
        colors = ["#c0392b" if n < min_n else "#1d3fbf" for n in ordered["n"]]
        plt.figure(figsize=(8, 0.45 * len(ordered) + 1.2))
        plt.errorbar(ordered["mean"], ordered[by].astype(str), xerr=err, fmt="none",
                     ecolor="#8a94a6", elinewidth=2, capsize=4)
        plt.scatter(ordered["mean"], ordered[by].astype(str), color=colors, zorder=3)
        plt.xlabel(f"Average {value}  (bars = approx. 95% confidence interval)")
        plt.title(f"{value} by {by} — with uncertainty")
        plt.tight_layout()
        plt.show()
    return table


def fairness_table(models, X_test, y_test, by):
    """Compare fitted models on accuracy AND on how evenly it is shared.

    `models` is a dict of {name: fitted model}. For each model: overall test
    accuracy, accuracy within each group, the gap between the best- and
    worst-served group, and the four-fifths selection-rate ratio.
    """
    import pandas as pd  # loaded lazily — see the note at the top
    by = _as_series(by, X_test.index)
    groups = sorted(by.dropna().unique(), key=str)
    rows = []
    for name, model in models.items():
        pred = pd.Series(model.predict(X_test), index=X_test.index)
        row = {"model": name, "test_accuracy": float((pred == y_test).mean())}
        accs, sels = [], []
        for g in groups:
            m = by == g
            acc = float((pred[m] == y_test[m]).mean())
            row[f"accuracy: {g}"] = acc
            accs.append(acc)
            sels.append(float(pred[m].mean()))
        row["accuracy_gap"] = max(accs) - min(accs)
        row["selection_ratio"] = min(sels) / max(sels) if max(sels) > 0 else float("nan")
        rows.append(row)
    table = pd.DataFrame(rows).set_index("model").round(2)
    print(table.to_string(), "\n")

    best = table["test_accuracy"].idxmax()
    widest = table["accuracy_gap"].idxmax()
    print(f"🔎 What to look for: the most accurate model overall is '{best}'; the widest "
          f"accuracy gap belongs to '{widest}'."
          + (" Same model." if best == widest else ""))
    if (table["selection_ratio"] >= 0.8).all():
        print("   Every model passes the four-fifths screen — so that screen cannot tell "
              "you which of them is fairest.")
    print("⚖️ Framework: the EU AI Act requires high-risk systems to reach an 'appropriate "
          "level of accuracy' (Art. 15(1)) and their accuracy metrics to be declared to "
          "deployers (Art. 15(3)) — but it does not say *whose* accuracy. Picking a model "
          "by its overall score is itself a value choice.")
    return table


# --------------------------------------------------------------- portfolio
#
# Every ethics lab ends with a written judgment. They are stored in
# reflections.json in the lab's browser storage, so they survive between
# visits and across lessons, and export_portfolio() bundles them — with the
# capstone model card — into one HTML file a learner can submit.

_STORE = Path("reflections.json")

PORTFOLIO_ITEMS = {
    "missing-data-ethics": "Track 1 · 3 — Seeing what's missing: who disappears when you clean?",
    "eda-headline-ethics": "Track 2 · 1 — Explore a real dataset: before it becomes a headline",
    "eda-small-groups": "Track 2 · 2 — Graded exercise: reporting a very small group",
    "ml-classifier-ethics": "Track 3 · 1 — First classifier: would you deploy it?",
    "ml-model-choice": "Track 3 · 2 — Choosing a model: accuracy or fairness?",
    "capstone-model-card": "Track 3 · 3 — Capstone: your model card",
}

_TEMPLATE_MARK = "Your answer"


def _is_template(text, min_len):
    text = (text or "").strip()
    return len(text) < min_len or _TEMPLATE_MARK in text


def _load():
    if not _STORE.exists():
        return {}
    try:
        data = json.loads(_STORE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        print("⚠️  reflections.json could not be read — starting a fresh portfolio "
              "(the damaged file was kept as reflections.broken.json).")
        _STORE.replace(_STORE.with_suffix(".broken.json"))
        return {}
    # earlier DataLab versions stored plain strings
    return {k: (v if isinstance(v, dict) else {"text": v, "saved": None}) for k, v in data.items()}


def _save(data):
    _STORE.write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def _now():
    return datetime.now().strftime("%Y-%m-%d %H:%M")


def _progress(data):
    done = sum(1 for k in PORTFOLIO_ITEMS if k in data)
    return f"{done} of {len(PORTFOLIO_ITEMS)} portfolio items"


def reflect_submit(key, text):
    """Save a written ethical judgment to your portfolio.

    Re-running with new text simply replaces your earlier answer.
    """
    if _is_template(text, 60):
        print("✍️  Not saved yet — replace the template with your own reasoning "
              "(a few honest sentences). The judgment is the exercise.")
        return
    data = _load()
    data[key] = {"text": text.strip(), "saved": _now()}
    _save(data)
    print(f"✅ Saved to your portfolio ({_progress(data)}).")
    print("   It stays in this browser between visits. Review it with show_portfolio(); "
          "download it with export_portfolio().")


def show_portfolio():
    """List what your portfolio contains so far, and what is still missing."""
    data = _load()
    print(f"Your DataLab portfolio — {_progress(data)}\n")
    for key, title in PORTFOLIO_ITEMS.items():
        item = data.get(key)
        if item:
            words = len(item.get("text", "").split())
            when = f", saved {item['saved']}" if item.get("saved") else ""
            print(f"  ✅ {title}  ({words} words{when})")
        else:
            print(f"  ⬜ {title}")
    extra = [k for k in data if k not in PORTFOLIO_ITEMS]
    for k in extra:
        print(f"  •  {k} (other)")
    print("\nTip: export_portfolio() downloads everything as one file. Clearing this "
          "site's browser data deletes the portfolio, so export it regularly.")


def model_card(model, X_test, y_test, audit_by, *, model_name, features,
               intended_use, out_of_scope, limitations, recommendation):
    """Assemble and save the capstone model card.

    The numbers are computed from YOUR model; the four written fields are yours
    to write. A model card is the standard practical format for what the EU AI
    Act asks providers of high-risk systems to document: intended purpose,
    accuracy and known limitations (Art. 11 / Annex IV; Art. 13).
    """
    import pandas as pd  # loaded lazily — see the note at the top
    written = {"intended_use": intended_use, "out_of_scope": out_of_scope,
               "limitations": limitations, "recommendation": recommendation}
    missing = [k for k, v in written.items() if _is_template(v, 40)]
    if missing:
        print("✍️  Model card not saved yet — these fields still hold the template text: "
              + ", ".join(missing) + ". A sentence or two each, in your own words.")
        return None

    pred = pd.Series(model.predict(X_test), index=X_test.index)
    by = _as_series(audit_by, X_test.index)
    accuracy = float((pred == y_test).mean())
    baseline = float(max(y_test.mean(), 1 - y_test.mean()))
    groups = {}
    for g in sorted(by.dropna().unique(), key=str):
        m = by == g
        pos = m & (y_test == 1)
        groups[str(g)] = {
            "n": int(m.sum()),
            "accuracy": round(float((pred[m] == y_test[m]).mean()), 3),
            "false_negative_rate": round(float((pred[pos] == 0).mean()), 3) if int(pos.sum()) else None,
            "selection_rate": round(float(pred[m].mean()), 3),
        }
    sel = [v["selection_rate"] for v in groups.values()]
    ratio = round(min(sel) / max(sel), 3) if sel and max(sel) > 0 else None
    accs = [v["accuracy"] for v in groups.values()]

    card = {
        "model": model_name,
        "features": list(features),
        "test_accuracy": round(accuracy, 3),
        "baseline_accuracy": round(baseline, 3),
        "groups": groups,
        "accuracy_gap": round(max(accs) - min(accs), 3) if accs else None,
        "selection_rate_ratio": ratio,
        **{k: v.strip() for k, v in written.items()},
    }

    print(f"MODEL CARD — {model_name}\n")
    print(f"  Features: {', '.join(card['features'])}")
    print(f"  Test accuracy: {accuracy:.0%}  (always-predict-the-majority baseline: {baseline:.0%})")
    for g, v in groups.items():
        fnr = f"{v['false_negative_rate']:.0%}" if v["false_negative_rate"] is not None else "n/a"
        print(f"  {g:>12}: accuracy {v['accuracy']:.0%}, false negatives {fnr}, "
              f"selected {v['selection_rate']:.0%}  (n={v['n']})")
    if ratio is not None:
        print(f"  Selection-rate ratio: {ratio:.2f}")
    for k, label in [("intended_use", "Intended use"), ("out_of_scope", "Out of scope"),
                     ("limitations", "Known limitations"), ("recommendation", "Recommendation")]:
        print(f"\n  {label}: {card[k]}")

    data = _load()
    data["capstone-model-card"] = {"text": card["recommendation"], "card": card, "saved": _now()}
    _save(data)
    print(f"\n✅ Model card saved to your portfolio ({_progress(data)}).")
    return card


def _portfolio_html(data, name):
    esc = html.escape
    parts = []
    for key, title in PORTFOLIO_ITEMS.items():
        item = data.get(key)
        if not item:
            parts.append(f'<section class="todo"><h2>{esc(title)}</h2>'
                         f'<p class="muted">Not completed yet.</p></section>')
            continue
        saved = f'<p class="muted">Saved {esc(item["saved"])}</p>' if item.get("saved") else ""
        card = item.get("card")
        if card:
            rows = "".join(
                f"<tr><td>{esc(g)}</td><td>{v['n']}</td><td>{v['accuracy']:.0%}</td>"
                f"<td>{'n/a' if v['false_negative_rate'] is None else format(v['false_negative_rate'], '.0%')}</td>"
                f"<td>{v['selection_rate']:.0%}</td></tr>"
                for g, v in card["groups"].items())
            ratio = card.get("selection_rate_ratio")
            body = (
                f"<p><b>Model:</b> {esc(card['model'])}<br>"
                f"<b>Features:</b> {esc(', '.join(card['features']))}<br>"
                f"<b>Test accuracy:</b> {card['test_accuracy']:.0%} "
                f"(majority-class baseline {card['baseline_accuracy']:.0%})"
                + (f"<br><b>Selection-rate ratio:</b> {ratio:.2f}" if ratio is not None else "")
                + "</p><table><tr><th>Group</th><th>n</th><th>Accuracy</th>"
                "<th>False negatives</th><th>Selected</th></tr>" + rows + "</table>"
                + "".join(f"<h3>{label}</h3><p class='answer'>{esc(card[k])}</p>"
                          for k, label in [("intended_use", "Intended use"),
                                           ("out_of_scope", "Out of scope"),
                                           ("limitations", "Known limitations"),
                                           ("recommendation", "Recommendation")]))
        else:
            body = f"<p class='answer'>{esc(item.get('text', ''))}</p>"
        parts.append(f"<section><h2>{esc(title)}</h2>{saved}{body}</section>")
    for key in data:
        if key not in PORTFOLIO_ITEMS:
            parts.append(f"<section><h2>{esc(key)}</h2>"
                         f"<p class='answer'>{esc(data[key].get('text', ''))}</p></section>")

    done = sum(1 for k in PORTFOLIO_ITEMS if k in data)
    # Escape <, > and & so learner text can never close or confuse the <script> block.
    record = (json.dumps({"learner": name, "generated": _now(), "items": data},
                         ensure_ascii=False)
              .replace("&", "\\u0026").replace("<", "\\u003c").replace(">", "\\u003e"))
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>EURIDICE DataLab — learning portfolio</title>
<style>
 body {{ font: 16px/1.6 system-ui, sans-serif; max-width: 52rem; margin: 2rem auto;
        padding: 0 1rem; color: #1b1f2a; background: #fff; }}
 h1 {{ color: #1d3fbf; margin-bottom: .2rem; }} h2 {{ font-size: 1.1rem; margin: 0 0 .4rem; }}
 h3 {{ font-size: .95rem; margin: 1rem 0 .2rem; }}
 section {{ border: 1px solid #d5dbe6; border-radius: 8px; padding: 1rem 1.2rem; margin: 1rem 0; }}
 .todo {{ background: #f6f7f9; }} .muted {{ color: #6b7385; font-size: .85rem; margin: .2rem 0; }}
 .answer {{ white-space: pre-wrap; }} .notice {{ background: #eef2ff; border-color: #c7d2fe; }}
 table {{ border-collapse: collapse; margin-top: .6rem; font-size: .9rem; }}
 th, td {{ border: 1px solid #d5dbe6; padding: .3rem .6rem; text-align: left; }}
 footer {{ color: #6b7385; font-size: .8rem; margin-top: 2rem; }}
 @media print {{ section {{ break-inside: avoid; }} }}
</style></head><body>
<h1>EURIDICE DataLab — learning portfolio</h1>
<p class="muted">Learner: {esc(name) if name else '____________________'} ·
Generated {_now()} · {done} of {len(PORTFOLIO_ITEMS)} items completed</p>
<section class="notice"><p>Self-reported learning evidence from the open
EURIDICE DataLab. This file is <b>not</b> itself a credential: submit it to a
EURIDICE partner institution for formal assessment toward a microcredential.</p></section>
{''.join(parts)}
<footer>Co-funded by the European Union under the Digital Europe Programme, project
EURIDICE (Grant Agreement No. 101123121). Views and opinions expressed are those of
the author(s) only and do not necessarily reflect those of the European Union or the
European Commission. Learning materials © IIIM, CC BY 4.0.</footer>
<script type="application/json" id="datalab-portfolio">{record}</script>
</body></html>"""


def export_portfolio(name=""):
    """Bundle your saved judgments and model card into one downloadable HTML file.

    Pass your name if you want it printed on the portfolio, e.g.
    export_portfolio("Ana Silva"). It stays on your device — nothing is uploaded.
    """
    data = _load()
    if not data:
        print("Your portfolio is empty so far — the ethics labs' reflect_submit() cells "
              "fill it. Run show_portfolio() to see which ones exist.")
        return None
    page = _portfolio_html(data, (name or "").strip())
    out = Path("portfolio.html")
    out.write_text(page, encoding="utf-8")
    print(f"📄 Portfolio built ({_progress(data)}) and saved as portfolio.html.")
    try:
        from IPython.display import HTML, display
        b64 = base64.b64encode(page.encode("utf-8")).decode("ascii")
        display(HTML(
            f'<a download="datalab-portfolio.html" '
            f'href="data:text/html;charset=utf-8;base64,{b64}" '
            f'style="display:inline-block;padding:.55rem 1rem;border-radius:6px;'
            f'background:#1d3fbf;color:#fff;text-decoration:none;font-weight:600">'
            f'⬇ Download your portfolio</a>'
            f'<p style="font-size:.85rem;color:#6b7385">Opens in any browser; use the '
            f'browser\'s Print → Save as PDF if your institution asks for a PDF.</p>'))
    except Exception:  # no rich display available (e.g. a plain Python run)
        print("   (No download button in this environment — the file is at portfolio.html.)")
    return out
