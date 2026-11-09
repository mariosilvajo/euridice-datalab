"""EURIDICE DataLab — instant exercise checker (Kaggle Learn style).

Learners load this with `%run datalab_checks.py` inside the lab, then call
check_q1(answer) ... check_q6(answer) and hint_q1() ... hint_q6().
Ground truth is computed from the dataset itself, so the checker stays
correct even if the dataset is regenerated.

Only standard-library imports at module level: in the browser, `%run` does not
make Pyodide load packages, so a top-level `import pandas` would fail in a
fresh kernel. pandas is imported where it is used.
"""

_df_cache = {}
_score = {}


def _data():
    import pandas as pd  # loaded lazily — see the note at the top
    if "media" not in _df_cache:
        _df_cache["media"] = pd.read_csv("data/eu_media_habits.csv")
    return _df_cache["media"]


def _correct(q, extra=""):
    _score[q] = True
    print(f"✅ Question {q}: correct! {extra}".rstrip())


def _wrong(q, hint):
    _score[q] = False
    print(f"❌ Question {q}: not quite. {hint}")


def _is_number(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


# ---------------------------------------------------------------- questions

def check_q1(answer):
    """How many respondents (rows) does the dataset have?"""
    truth = len(_data())
    if _is_number(answer) and int(answer) == truth:
        _correct(1)
    else:
        _wrong(1, "Try len(df) or df.shape[0].")


def hint_q1():
    print("Hint: df.shape returns (rows, columns). You want the first value.")


def check_q2(answer):
    """Which country has the highest average daily social media hours?"""
    truth = _data().groupby("country")["hours_social"].mean().idxmax()
    if isinstance(answer, str) and answer.strip().lower() == truth.lower():
        _correct(2, "Group by country, take the mean, then find the maximum.")
    else:
        _wrong(2, "Use df.groupby('country')['hours_social'].mean() and look for the largest value.")


def hint_q2():
    print("Hint: .groupby('country')['hours_social'].mean().sort_values(ascending=False) "
          "puts the biggest first. .idxmax() gives it to you directly.")


def check_q3(answer):
    """What is the median age of respondents who pay for news?"""
    truth = _data().loc[_data()["pays_for_news"] == "yes", "age"].median()
    if _is_number(answer) and abs(float(answer) - float(truth)) < 0.51:
        _correct(3)
    else:
        _wrong(3, "Filter rows where pays_for_news == 'yes' first, then take .median() of age.")


def hint_q3():
    print("Hint: payers = df[df['pays_for_news'] == 'yes'], then payers['age'].median().")


def check_q4(answer):
    """What is the most common main news source among under-30s?"""
    truth = _data().loc[_data()["age"] < 30, "main_news_source"].mode()[0]
    if isinstance(answer, str) and answer.strip().lower() == truth.lower():
        _correct(4)
    else:
        _wrong(4, "Filter df[df['age'] < 30] first, then look at main_news_source.")


def hint_q4():
    print("Hint: .value_counts() ranks categories by frequency; .mode()[0] returns the winner.")


def check_q5(answer):
    """Correlation between hours_social and trust_news, rounded to 2 decimals."""
    truth = round(_data()["hours_social"].corr(_data()["trust_news"]), 2)
    if _is_number(answer) and abs(float(answer) - truth) < 0.015:
        sign = "negative — heavier social media use goes with lower trust in news here"
        _correct(5, f"And notice the sign: it is {sign}. (Correlation, not causation!)")
    else:
        _wrong(5, "Use df['hours_social'].corr(df['trust_news']) and round(..., 2).")


def hint_q5():
    print("Hint: round(df['hours_social'].corr(df['trust_news']), 2)")


def check_q6(answer):
    """Which gender group's average is too small to report on its own?"""
    answered = _data().groupby("gender")["trust_news"].count()
    small = {g.lower(): int(n) for g, n in answered.items() if n < 30}
    if isinstance(answer, str) and answer.strip().lower() in small:
        n = small[answer.strip().lower()]
        _correct(6, f"Only {n} people in that group answered the trust question, so its "
                    "average is mostly noise — and, broken down any further, could even "
                    "identify individuals. Report it with its uncertainty, or not at all.")
    else:
        _wrong(6, "Look at the n column of compare_groups(): which group's average rests "
                  "on fewer than 30 answers? It's the one flagged ⚠️.")


def hint_q6():
    print("Hint: the flag column says '⚠️ too few to report alone' next to the group "
          "you're looking for. Answer with its name as a string, e.g. q6_answer = \"...\"")


def datalab_score():
    """Print your progress across all six questions."""
    total = 6
    done = sum(1 for v in _score.values() if v)
    bar = "▓" * done + "░" * (total - done)
    print(f"Progress {bar}  {done}/{total} correct")
    if done == total:
        print("\U0001f393 Excellent — you finished the EDA exercise! "
              "See the course page for how this counts toward a microcredential.")


print("Checker loaded — check_q1() to check_q6() are ready. Stuck? Try hint_q1() etc.")
