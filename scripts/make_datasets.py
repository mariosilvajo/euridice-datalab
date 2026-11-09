"""Generate the DataLab's synthetic teaching datasets.

Both datasets are fully synthetic (seeded, reproducible) but shaped to feel
real and to sit inside EURIDICE's sector focus: Communication & Media and
Education & Culture.

Outputs go to BOTH:
  - site/public/datasets/   (downloadable from the website)
  - lab/notebooks/data/     (preloaded inside the in-browser lab)
"""

from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
OUT_SITE = ROOT / "site" / "public" / "datasets"
OUT_LAB = ROOT / "lab" / "notebooks" / "data"

rng = np.random.default_rng(42)


def make_media_habits(n_per_country: int = 78) -> pd.DataFrame:
    """EU Media Habits 2026 — synthetic survey on news & media consumption."""
    countries = {
        # country: (base social-media hours/day, base trust in news 1-10)
        "Iceland": (2.1, 6.8),
        "Austria": (1.9, 6.2),
        "Germany": (1.7, 6.0),
        "Denmark": (2.0, 7.1),
        "Netherlands": (2.2, 6.5),
        "Portugal": (3.1, 5.6),  # clearly highest social-media use (exercise Q2)
        "Italy": (2.5, 5.4),
        "Ukraine": (2.6, 5.9),
    }
    rows = []
    rid = 1000
    for country, (base_social, base_trust) in countries.items():
        for _ in range(n_per_country):
            age = int(np.clip(rng.normal(41, 15), 16, 79))
            youth_boost = max(0.0, (35 - age) * 0.05)
            hours_social = round(
                float(np.clip(rng.normal(base_social + youth_boost, 0.7), 0, 9)), 1
            )
            hours_tv = round(float(np.clip(rng.normal(2.4 + (age - 40) * 0.03, 0.9), 0, 8)), 1)
            hours_news = round(float(np.clip(rng.normal(0.9 + (age - 40) * 0.01, 0.4), 0, 4)), 1)
            # Trust in news falls with heavy social-media use (the EDA lesson's
            # correlation). Centred on the mean so raising this effect doesn't
            # drag the whole trust scale down.
            trust = int(
                np.clip(round(rng.normal(base_trust - 0.70 * (hours_social - 2.4), 1.0)), 1, 10)
            )
            if age < 30:
                src = rng.choice(
                    ["social media", "online news", "TV", "radio", "print"],
                    p=[0.46, 0.30, 0.14, 0.06, 0.04],
                )
            else:
                src = rng.choice(
                    ["social media", "online news", "TV", "radio", "print"],
                    p=[0.18, 0.30, 0.34, 0.10, 0.08],
                )
            income = rng.choice(
                ["under 20k", "20-40k", "40-60k", "over 60k"], p=[0.22, 0.34, 0.28, 0.16]
            )
            rows.append(
                {
                    "respondent_id": rid,
                    "country": country,
                    "age": age,
                    "gender": rng.choice(["female", "male", "other"], p=[0.49, 0.49, 0.02]),
                    "household_income_band": income,
                    "hours_tv": hours_tv,
                    "hours_social": hours_social,
                    "hours_news": hours_news,
                    "main_news_source": src,
                    "trust_news": trust,
                    "pays_for_news": rng.choice(["yes", "no"], p=[0.27, 0.73]),
                }
            )
            rid += 1
    return pd.DataFrame(rows)


def _inject_missingness(df: pd.DataFrame) -> None:
    """Add three *different kinds* of missing data, in place.

    Real survey data is never missing at random, and the pattern itself
    carries information. Track 1's missing-data lesson teaches learners to
    read these three signatures with `missingno`:

      1. hours_tv               — MCAR: genuinely random dropout (~4%)
      2. trust_news             — MNAR: low-trust respondents skip the
                                  question *because* their answer is low, so
                                  the observed average is biased upward
      3. household_income_band  — sensitive question, refused more by older
         + pays_for_news          and higher-income respondents; the same
                                  privacy-guarded people also skip
                                  'do you pay for news', which makes the two
                                  columns' missingness strongly correlated
    """
    n = len(df)

    # 1. MCAR — no pattern at all
    df.loc[rng.random(n) < 0.04, "hours_tv"] = np.nan

    # 2. MNAR — refusal is a threshold behaviour, not a gentle slope: people who
    #    actively distrust the media are the ones who refuse the trust question.
    p_skip_trust = 0.02 + 0.45 / (1 + np.exp(1.5 * (df["trust_news"] - 5.3)))
    df.loc[rng.random(n) < p_skip_trust, "trust_news"] = np.nan

    # 3. A shared "privacy-guarded respondent" tendency drives both columns
    guarded = (
        0.06
        + 0.004 * (df["age"] - 40).clip(lower=0)
        + df["household_income_band"].map(
            {"under 20k": 0.04, "20-40k": 0.06, "40-60k": 0.12, "over 60k": 0.22}
        )
    )
    is_guarded = rng.random(n) < guarded
    df.loc[is_guarded & (rng.random(n) < 0.85), "household_income_band"] = np.nan
    df.loc[is_guarded & (rng.random(n) < 0.70), "pays_for_news"] = np.nan


def make_student_skills(n: int = 900, share_laptop: float = 0.70,
                        damp: float = 0.12) -> pd.DataFrame:
    """Student Digital Skills — synthetic education dataset for the ML track.

    Uses its OWN generator, deliberately: this dataset previously shared the
    module-level `rng` with the media survey, so editing the survey silently
    reshuffled the ML lesson's results and inverted its fairness finding.

    The design encodes one teaching point, structurally rather than by luck:

      For learners who own a laptop, the recorded features really do predict
      whether they pass. For learners who don't, what actually decides the
      outcome — shared devices, library opening hours, borrowed time — was
      never recorded, so the features predict them far more weakly (`damp`).

    Because laptop ownership is independent of every other feature, and both
    groups are calibrated to the same pass rate, a model that never sees the
    laptop column produces near-identical *selection rates* for both groups —
    so the four-fifths screen passes — while being markedly less *accurate*
    for the group it cannot describe. That gap is irreducible noise, not a
    sampling fluke, which is why the ethics lab's conclusion holds.
    """
    srng = np.random.default_rng(20260042)
    fields = ["ICT", "Business", "Humanities", "Education", "Science", "Media"]
    countries = ["Iceland", "Austria", "Germany", "Denmark", "Netherlands", "Portugal",
                 "Italy", "Ukraine"]
    rows = []
    for sid in range(5000, 5000 + n):
        field = srng.choice(fields, p=[0.22, 0.18, 0.16, 0.16, 0.16, 0.12])
        age = int(np.clip(srng.normal(28, 8), 18, 60))
        hours = round(float(np.clip(srng.normal(7, 4), 0, 20)), 1)
        base_score = 62 if field == "ICT" else 48
        score = int(np.clip(srng.normal(base_score + hours * 1.2, 12), 20, 100))
        laptop = int(srng.random() < share_laptop)
        prior = int(np.clip(srng.poisson(1.6 if field == "ICT" else 0.8), 0, 5))
        logit = 0.075 * (score - 55) + 0.16 * (hours - 6) + 0.28 * prior - 0.45
        rows.append(
            {
                "student_id": sid,
                "country": srng.choice(countries),
                "age": age,
                "study_field": field,
                "hours_online_learning": hours,
                "digital_skill_score": score,
                "has_own_laptop": laptop,
                "prior_ict_courses": prior,
                "_logit": logit,
            }
        )
    df = pd.DataFrame(rows)

    # Calibrate both groups to the same expected pass rate, so the disparity
    # the lesson finds is about predictability — not a different success rate.
    lap = df["has_own_laptop"] == 1
    target = float((1 / (1 + np.exp(-df.loc[lap, "_logit"]))).mean())
    shrunk = damp * df.loc[~lap, "_logit"]
    lo, hi = -6.0, 6.0
    for _ in range(60):
        mid = (lo + hi) / 2
        if float((1 / (1 + np.exp(-(shrunk + mid)))).mean()) < target:
            lo = mid
        else:
            hi = mid

    p_pass = 1 / (1 + np.exp(-df["_logit"]))
    p_pass[~lap] = 1 / (1 + np.exp(-(shrunk + (lo + hi) / 2)))
    df["passed_certification"] = (srng.random(len(df)) < p_pass).astype(int)
    return df.drop(columns=["_logit"])


def check_model_choice_lesson(students, X_tr, X_te, y_tr, y_te, lap) -> None:
    """Assert the claims of Track 3 · Lesson 2 (overfitting & choosing a model)."""
    from sklearn.dummy import DummyClassifier
    from sklearn.ensemble import RandomForestClassifier
    from sklearn.linear_model import LogisticRegression
    from sklearn.model_selection import cross_val_score
    from sklearn.pipeline import make_pipeline
    from sklearn.preprocessing import StandardScaler
    from sklearn.tree import DecisionTreeClassifier

    base_test = max(y_te.mean(), 1 - y_te.mean())

    # overfitting: an unlimited tree memorises the training set and loses to doing nothing
    deep = DecisionTreeClassifier(random_state=42).fit(X_tr, y_tr)
    assert deep.score(X_tr, y_tr) >= 0.99, deep.score(X_tr, y_tr)
    assert deep.score(X_te, y_te) < base_test, (deep.score(X_te, y_te), base_test)

    cv = {d: cross_val_score(DecisionTreeClassifier(max_depth=d, random_state=42),
                             X_tr, y_tr, cv=5).mean() for d in range(1, 16)}
    best_depth = max(cv, key=cv.get)
    assert 3 <= best_depth <= 5, best_depth

    serious = {
        "tree": DecisionTreeClassifier(max_depth=best_depth, random_state=42),
        "logistic": make_pipeline(StandardScaler(), LogisticRegression()),
        "forest": RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42),
    }
    cvs, gaps, none_acc, has_acc, ratios = {}, {}, {}, {}, {}
    for name, mdl in serious.items():
        cvs[name] = cross_val_score(mdl, X_tr, y_tr, cv=5).mean()
        pred = pd.Series(mdl.fit(X_tr, y_tr).predict(X_te), index=X_te.index)
        a1 = (pred[lap == 1] == y_te[lap == 1]).mean()
        a0 = (pred[lap == 0] == y_te[lap == 0]).mean()
        gaps[name], none_acc[name], has_acc[name] = a1 - a0, a0, a1
        s1, s0 = pred[lap == 1].mean(), pred[lap == 0].mean()
        ratios[name] = min(s1, s0) / max(s1, s0)
    dummy = DummyClassifier(strategy="most_frequent").fit(X_tr, y_tr)
    dpred = pd.Series(dummy.predict(X_te), index=X_te.index)
    base_none = (dpred[lap == 0] == y_te[lap == 0]).mean()
    base_has = (dpred[lap == 1] == y_te[lap == 1]).mean()

    # "statistically a tie on accuracy..."
    assert max(cvs.values()) - min(cvs.values()) <= 0.03, cvs
    # "...but not on fairness"
    assert max(gaps.values()) - min(gaps.values()) >= 0.04, gaps
    assert max(gaps, key=gaps.get) == "forest", gaps
    # "every trained model is worse than predicting 'pass' for the no-laptop group"
    assert all(v < base_none for v in none_acc.values()), (none_acc, base_none)
    # "all the accuracy gained was gained on laptop owners"
    assert all(v > base_has for v in has_acc.values()), (has_acc, base_has)
    assert all(r >= 0.85 for r in ratios.values()), ratios
    print(f"Model-choice lesson — best depth {best_depth}; CV spread "
          f"{max(cvs.values()) - min(cvs.values()):.3f}; gaps "
          + ", ".join(f"{k} {v:+.2f}" for k, v in gaps.items())
          + f"; no-laptop acc max {max(none_acc.values()):.2f} < baseline {base_none:.2f}")


def check_eda_lesson(media: pd.DataFrame) -> None:
    """Assert the claims of Track 2's 'before it becomes a headline' ethics lab."""
    def ci(s):
        s = s.dropna()
        h = 1.96 * s.std(ddof=1) / np.sqrt(len(s))
        return len(s), s.mean(), s.mean() - h, s.mean() + h, h

    rows = sorted(((c, *ci(g["hours_social"])) for c, g in media.groupby("country")),
                  key=lambda r: -r[2])
    assert rows[0][0] == "Portugal", rows[0]
    assert rows[0][3] > rows[1][4], "Portugal must stand clear of second place"
    for upper, lower in zip(rows[1:], rows[2:]):
        assert upper[3] <= lower[4], f"{upper[0]} vs {lower[0]} should be within the noise"
    assert rows[-1][0] == "Austria", rows[-1]

    gender = {g: ci(s["trust_news"]) for g, s in media.groupby("gender")}
    n_other_rows = int((media["gender"] == "other").sum())
    assert 8 <= n_other_rows <= 15, n_other_rows               # "about a dozen"
    assert gender["other"][0] < 10, gender["other"]             # "fewer than ten answered"
    widest_other = min(gender["female"][4], gender["male"][4])
    assert gender["other"][4] >= 3 * widest_other, gender       # "over three times wider"
    per_country = media[media["gender"] == "other"].groupby("country").size()
    assert per_country.max() <= 3 and per_country.min() == 1, per_country
    print(f"EDA lesson — Portugal clear; ranks 2-8 within noise; 'other' n={n_other_rows} "
          f"({gender['other'][0]} answered trust), CI x{gender['other'][4] / widest_other:.1f} wider")


def check_ml_lesson(students: pd.DataFrame) -> None:
    """Assert every claim the ML ethics lab makes about this dataset.

    Without this, a change elsewhere can silently invert the lesson's
    conclusion — which is exactly what happened once already.
    """
    from sklearn.model_selection import train_test_split
    from sklearn.tree import DecisionTreeClassifier

    features = ["age", "hours_online_learning", "digital_skill_score", "prior_ict_courses"]
    X, y = students[features], students["passed_certification"]
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, random_state=42)
    tree = DecisionTreeClassifier(max_depth=4, random_state=42).fit(X_tr, y_tr)
    pred = pd.Series(tree.predict(X_te), index=X_te.index)
    lap = students.loc[X_te.index, "has_own_laptop"]

    acc, base = tree.score(X_te, y_te), max(y_te.mean(), 1 - y_te.mean())
    stats = {}
    for g, lbl in [(1, "has laptop"), (0, "no laptop")]:
        m = lap == g
        pos = m & (y_te == 1)
        stats[lbl] = {
            "n": int(m.sum()),
            "acc": float((pred[m] == y_te[m]).mean()),
            "fnr": float((pred[pos] == 0).mean()),
            "sel": float(pred[m].mean()),
        }
    a, b = stats["has laptop"], stats["no laptop"]
    ratio = min(a["sel"], b["sel"]) / max(a["sel"], b["sel"])

    assert acc > base, f"model must beat the always-pass baseline: {acc:.3f} vs {base:.3f}"
    assert b["n"] >= 50, f"no-laptop test group too small to audit honestly: {b['n']}"
    assert a["acc"] - b["acc"] >= 0.10, f"accuracy gap too small/inverted: {a['acc'] - b['acc']:+.3f}"
    assert b["fnr"] - a["fnr"] >= 0.05, f"false-negative gap too small/inverted: {b['fnr'] - a['fnr']:+.3f}"
    assert ratio >= 0.85, f"four-fifths screen must PASS for the lesson's twist: {ratio:.3f}"

    check_model_choice_lesson(students, X_tr, X_te, y_tr, y_te, lap)

    print(f"ML lesson — accuracy {acc:.0%} vs {base:.0%} baseline | "
          f"has laptop {a['acc']:.0%} acc / {a['fnr']:.0%} FNR (n={a['n']}) | "
          f"no laptop {b['acc']:.0%} acc / {b['fnr']:.0%} FNR (n={b['n']}) | "
          f"selection-rate ratio {ratio:.2f} (passes four-fifths)")


def main() -> None:
    OUT_SITE.mkdir(parents=True, exist_ok=True)
    OUT_LAB.mkdir(parents=True, exist_ok=True)

    media = make_media_habits()
    # Capture the answers BEFORE anyone refuses to give them. A real survey can
    # never know this; because our data is synthetic, the missing-data lesson can
    # reveal exactly how much the refusals distort the findings.
    truth = media[["respondent_id", "trust_news"]].rename(
        columns={"trust_news": "trust_news_true"}
    )
    _inject_missingness(media)

    students = make_student_skills()

    # sanity checks so the graded exercise has unambiguous answers
    by_country = media.groupby("country")["hours_social"].mean().sort_values(ascending=False)
    assert by_country.index[0] == "Portugal", by_country
    assert by_country.iloc[0] - by_country.iloc[1] > 0.3, by_country
    pass_rate = students["passed_certification"].mean()
    assert 0.35 < pass_rate < 0.75, pass_rate
    check_ml_lesson(students)

    check_eda_lesson(media)

    # the EDA lesson teaches this negative relationship — it must survive missingness
    corr = media["hours_social"].corr(media["trust_news"])
    assert corr < -0.1, corr

    # checks that the missing-data lesson's claims are actually true of the data
    miss = media.isna().mean()
    assert 0.02 < miss["hours_tv"] < 0.07, miss["hours_tv"]
    assert 0.08 < miss["trust_news"] < 0.25, miss["trust_news"]
    assert 0.06 < miss["household_income_band"] < 0.25, miss["household_income_band"]
    # MNAR is *detectable from observed columns*: skippers use social media more
    gap = (
        media.loc[media["trust_news"].isna(), "hours_social"].mean()
        - media.loc[media["trust_news"].notna(), "hours_social"].mean()
    )
    assert gap > 0.15, gap
    # the two sensitive columns must co-miss, or the heatmap has nothing to show
    co = media["household_income_band"].isna().corr(media["pays_for_news"].isna())
    assert co > 0.4, co
    complete = media.dropna()
    print(
        f"Missingness — hours_tv {miss['hours_tv']:.0%} (MCAR), "
        f"trust_news {miss['trust_news']:.0%} (MNAR), "
        f"income {miss['household_income_band']:.0%} / pays {miss['pays_for_news']:.0%} "
        f"(co-missing r={co:.2f})"
    )
    print(f"  MNAR check — skippers' extra social hours: +{gap:.2f}")
    print(f"  Complete rows if you dropna(): {len(complete)}/{len(media)} "
          f"({len(complete) / len(media):.0%})")
    print(f"  hours_social vs trust_news correlation: {corr:.2f}")

    # the reveal used by Track 1's missing-data lesson
    hidden = (truth["trust_news_true"] <= 4).mean()
    observed = (media["trust_news"] <= 4).sum() / media["trust_news"].notna().sum()
    assert hidden - observed > 0.02, (hidden, observed)
    print(f"MNAR reveal — truly distrustful (trust<=4): {hidden:.1%} of everyone, "
          f"but only {observed:.1%} of the answers you receive "
          f"({1 - observed / hidden:.0%} under-count)")

    for name, df in [
        ("eu_media_habits.csv", media),
        ("eu_media_habits_answer_key.csv", truth),
        ("student_digital_skills.csv", students),
    ]:
        for out in (OUT_SITE, OUT_LAB):
            df.to_csv(out / name, index=False)
        print(f"{name}: {len(df)} rows -> {OUT_SITE / name} and {OUT_LAB / name}")

    print("Top countries by social media hours:")
    print(by_country.round(2).head(3).to_string())
    print(f"Certification pass rate: {pass_rate:.2f}")


if __name__ == "__main__":
    main()
