"""Generate the DataLab's teaching notebooks (.ipynb) with nbformat.

Notebooks are authored here as Python source so they are reviewable,
diffable and regenerable — the established EURIDICE pattern of
programmatic document generation.
"""

from pathlib import Path

import nbformat as nbf

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "lab" / "notebooks"

KERNELSPEC = {
    "kernelspec": {"name": "python", "display_name": "Python (Pyodide)", "language": "python"},
    "language_info": {"name": "python"},
}


def nb(cells):
    notebook = nbf.v4.new_notebook()
    notebook.metadata.update(KERNELSPEC)
    notebook.cells = cells
    return notebook


def md(source):
    return nbf.v4.new_markdown_cell(source)


def code(source):
    return nbf.v4.new_code_cell(source)


# ---------------------------------------------------------------------------
# 1. welcome.ipynb — Track 1, Lesson 1
# ---------------------------------------------------------------------------
welcome = nb([
    md(
        "# 👋 Welcome to the EURIDICE DataLab\n\n"
        "This is a **notebook** — the everyday tool of data scientists worldwide. "
        "It mixes text (like this) with **code you can run and edit**.\n\n"
        "**How to use it:** click a code cell and press **Shift + Enter** to run it. "
        "That's it — everything runs in your browser, nothing is installed on your computer.\n\n"
        "Try it with the cell below. 👇"
    ),
    code('print("Hello from the EURIDICE DataLab! 🇪🇺")'),
    md(
        "## Variables and calculations\n\n"
        "Python remembers values you store in *variables*. "
        "Here we compute how many learning hours one ECTS credit represents:"
    ),
    code(
        "hours_per_ects = 26   # 1 ECTS ≈ 25–28 hours; we use the midpoint\n"
        "credits = 1\n"
        "total_hours = hours_per_ects * credits\n"
        'print(f"{credits} ECTS ≈ {total_hours} learning hours")'
    ),
    md(
        "**Your turn:** change `credits` to `5` in the cell above and re-run it "
        "(that is the size of EURIDICE's *Digital Transition for Professionals* course)."
    ),
    md(
        "## Lists and loops\n\n"
        "Data science is about working with *collections* of values, not single numbers:"
    ),
    code(
        'partner_countries = ["Iceland", "Austria", "Germany", "Portugal", "Netherlands"]\n\n'
        "for country in partner_countries:\n"
        '    print(f"EURIDICE has partners in {country}")'
    ),
    md(
        "## Your first chart\n\n"
        "The `matplotlib` library draws charts. Watch how four lines of code become a figure "
        "(the first import takes a few seconds while the library loads):"
    ),
    code(
        "import matplotlib.pyplot as plt\n\n"
        'courses = ["AI Ethics", "Applied AI & ML", "Digital Transition"]\n'
        "ects = [2, 1, 5]\n\n"
        "plt.bar(courses, ects, color=\"#1d3fbf\")\n"
        'plt.ylabel("ECTS credits")\n'
        'plt.title("EURIDICE microcredential courses")\n'
        "plt.show()"
    ),
    md(
        "## Experiment freely\n\n"
        "You **cannot break anything**. This is your own copy: your changes are kept in this "
        "browser, and the **↺ Reset this notebook** button under it on the course page "
        "restores the original whenever you like. Use the empty cell below to try your own code:"
    ),
    code("# Your playground — try: print(2 + 2) or invent something\n"),
    md(
        "## ✅ What you learned\n\n"
        "- Notebooks mix explanation and runnable code\n"
        "- **Shift + Enter** runs a cell\n"
        "- Variables, lists, loops, and your first chart\n\n"
        "📚 **Want more on the basics?** (all free)\n"
        "- [Think Python](https://allendowney.github.io/ThinkPython/) — variables, lists, loops, "
        "from scratch\n"
        "- [Automate the Boring Stuff](https://automatetheboringstuff.com/) — practical Python "
        "for non-programmers\n"
        "- [The official Python tutorial](https://docs.python.org/3/tutorial/) — the reference\n\n"
        "**Next:** *Choosing the right chart* — six chart types, what each one hides, and how "
        "charts mislead."
    ),
])

# ---------------------------------------------------------------------------
# 1b. choosing-charts.ipynb — Track 1, Lesson 2
# ---------------------------------------------------------------------------
charts = nb([
    md(
        "# 📊 Choosing the right chart\n\n"
        "A chart is an *argument*. The same numbers can be made to look reassuring or "
        "alarming depending on how you draw them — so choosing a chart is a decision with "
        "consequences, not a matter of taste.\n\n"
        "This lesson walks through the six charts you will use 95% of the time, what each is "
        "**good at**, what each **hides**, and how charts mislead — on purpose or by accident.\n\n"
        "**The one question that decides everything:** *what am I comparing?*"
    ),
    code(
        "import pandas as pd\n"
        "import matplotlib.pyplot as plt\n"
        "import numpy as np\n\n"
        'df = pd.read_csv("data/eu_media_habits.csv")\n'
        'BLUE = "#1d3fbf"\n'
        "df.head(3)"
    ),
    md(
        "## 1. Bar chart — comparing categories\n\n"
        "*Use when:* you have distinct groups and want to compare an amount across them."
    ),
    code(
        'counts = df["main_news_source"].value_counts()\n\n'
        'counts.plot(kind="bar", color=BLUE)\n'
        'plt.ylabel("Number of respondents")\n'
        'plt.title("Where people get their news")\n'
        'plt.xticks(rotation=30, ha="right")\n'
        "plt.show()"
    ),
    md(
        "✅ **Good for:** precise comparison — humans judge *length* very accurately.\n\n"
        "⚠️ **Watch out:** bars must start at zero (see the last section), and beyond ~10 "
        "categories they turn into a picket fence. With many categories, use a horizontal "
        "bar chart (`kind=\"barh\"`) so the labels stay readable."
    ),
    md(
        "## 2. Histogram — the shape of one number\n\n"
        "*Use when:* you have one numeric column and want to know how it is distributed — "
        "where the bulk sits, whether it is skewed, whether there are outliers."
    ),
    code(
        'df["age"].plot(kind="hist", bins=20, color=BLUE, edgecolor="white")\n'
        'plt.xlabel("Age")\n'
        'plt.title("Age distribution of respondents")\n'
        "plt.show()"
    ),
    md(
        "### ⚠️ The bin trap — the same data, three stories\n\n"
        "A histogram's shape depends on a choice *you* make: how many bins. Run this and "
        "watch the same column tell three different stories."
    ),
    code(
        "fig, axes = plt.subplots(1, 3, figsize=(13, 3.5))\n"
        "for ax, b in zip(axes, [4, 20, 90]):\n"
        '    ax.hist(df["age"], bins=b, color=BLUE, edgecolor="white")\n'
        '    ax.set_title(f"bins = {b}")\n'
        '    ax.set_xlabel("Age")\n'
        "plt.tight_layout()\n"
        "plt.show()"
    ),
    md(
        "**Left:** too few bins — real structure is smoothed away into blocks. "
        "**Right:** too many — random noise looks like meaningful spikes. "
        "**Middle:** about right.\n\n"
        "There is no universally correct number. The honest habit: **try several before you "
        "believe any of them.**\n\n"
        "✅ **Good for:** seeing skew, gaps and outliers in one variable.\n"
        "⚠️ **Watch out:** the bin count changes the story; a histogram of a *category* is "
        "meaningless — use a bar chart."
    ),
    md(
        "## 3. Box plot — comparing distributions across groups\n\n"
        "*Use when:* you want to compare a numeric variable across several categories at once. "
        "Each box shows the median (line), the middle 50% (box), the range (whiskers) and "
        "outliers (dots)."
    ),
    code(
        'df.boxplot(column="hours_social", by="country", figsize=(10, 4), grid=False)\n'
        'plt.suptitle("")\n'
        'plt.title("Daily social media hours by country")\n'
        'plt.xlabel("")\n'
        'plt.ylabel("Hours per day")\n'
        'plt.xticks(rotation=30, ha="right")\n'
        "plt.show()"
    ),
    md(
        "Eight distributions compared in one glance — that is what box plots are for.\n\n"
        "### ⚠️ What box plots hide\n\n"
        "A box plot summarises a distribution into five numbers. If the real shape is unusual, "
        "those five numbers can hide it completely. Here is an invented example that proves it:"
    ),
    code(
        "rng = np.random.default_rng(0)\n"
        "# two very separate groups of people, combined into one column\n"
        "bimodal = np.concatenate([rng.normal(25, 4, 300), rng.normal(65, 4, 300)])\n\n"
        "fig, axes = plt.subplots(1, 2, figsize=(11, 3.5))\n"
        'axes[0].boxplot(bimodal, orientation="horizontal")\n'
        'axes[0].set_title("Box plot: looks like one ordinary group")\n'
        'axes[1].hist(bimodal, bins=40, color=BLUE, edgecolor="white")\n'
        'axes[1].set_title("Histogram: actually two separate groups!")\n'
        "plt.tight_layout()\n"
        "plt.show()"
    ),
    md(
        "The box plot shows a tidy median around 45 — an age **almost nobody in the data "
        "actually has**. The histogram reveals the truth instantly.\n\n"
        "✅ **Good for:** comparing many groups compactly; spotting outliers.\n"
        "⚠️ **Watch out:** hides multi-peaked (bimodal) data. Pair it with a histogram when a "
        "group matters."
    ),
    md(
        "## 4. Scatter plot — the relationship between two numbers\n\n"
        "*Use when:* you want to know whether two numeric variables move together."
    ),
    code(
        'df.plot(kind="scatter", x="hours_social", y="trust_news", color=BLUE)\n'
        'plt.title("Social media hours vs. trust in news")\n'
        "plt.show()"
    ),
    md(
        "### ⚠️ Overplotting — when dots hide dots\n\n"
        "`trust_news` is a whole number 1–10, so hundreds of people land on the *exact same "
        "spot*. A solid dot might be one person or fifty — you cannot tell. Two fixes: make "
        "dots transparent (`alpha`), and add a little random *jitter* to separate them."
    ),
    code(
        'jitter = np.random.default_rng(1).normal(0, 0.12, len(df))\n\n'
        "fig, axes = plt.subplots(1, 2, figsize=(11, 4))\n"
        'axes[0].scatter(df["hours_social"], df["trust_news"], color=BLUE)\n'
        'axes[0].set_title("Raw: dots stack invisibly")\n'
        'axes[1].scatter(df["hours_social"], df["trust_news"] + jitter, color=BLUE, alpha=0.25)\n'
        'axes[1].set_title("alpha + jitter: density becomes visible")\n'
        "for ax in axes:\n"
        '    ax.set_xlabel("Hours social media")\n'
        '    ax.set_ylabel("Trust in news")\n'
        "plt.tight_layout()\n"
        "plt.show()"
    ),
    md(
        "Now you can actually see where people cluster — and the downward drift.\n\n"
        "✅ **Good for:** relationships, clusters, outliers.\n"
        "⚠️ **Watch out:** overplotting with many or rounded values; and a visible pattern is "
        "**correlation, never proof of causation**."
    ),
    md(
        "## 5. Line chart — change along an ordered scale\n\n"
        "*Use when:* the x-axis has a natural order — time, age, temperature. The line implies "
        "*\"these points connect\"*, so the order must be real."
    ),
    code(
        '# group ages into 5-year bands so the line is not pure noise\n'
        'by_age = df.groupby(df["age"] // 5 * 5)["hours_social"].mean()\n\n'
        'by_age.plot(marker="o", color=BLUE)\n'
        'plt.xlabel("Age group")\n'
        'plt.ylabel("Average hours of social media")\n'
        'plt.title("Social media use declines with age")\n'
        "plt.show()"
    ),
    md(
        "✅ **Good for:** trends over time or any ordered scale.\n"
        "⚠️ **Watch out:** never use a line for unordered categories — connecting *Iceland → "
        "Austria → Germany* implies a journey that does not exist. That is a bar chart's job."
    ),
    md(
        "## 6. Pie chart — the one to avoid\n\n"
        "*Use when:* almost never. Here is the same data as a pie and as a bar — try to rank "
        "the slices by eye before you look at the bars."
    ),
    code(
        "fig, axes = plt.subplots(1, 2, figsize=(11, 4))\n"
        'axes[0].pie(counts.values, labels=counts.index, autopct="%1.0f%%")\n'
        'axes[0].set_title("Pie: can you rank these?")\n'
        'axes[1].barh(counts.index[::-1], counts.values[::-1], color=BLUE)\n'
        'axes[1].set_title("Bar: instantly obvious")\n'
        "plt.tight_layout()\n"
        "plt.show()"
    ),
    md(
        "People compare **lengths** accurately and **angles** poorly — that is a fact about "
        "human vision, not a style preference. The bar chart answers in a fraction of a second.\n\n"
        "✅ **Tolerable for:** two or three slices of an obvious whole.\n"
        "⚠️ **Watch out:** more than three slices, or slices of similar size — use a bar chart."
    ),
    md(
        "## 📐 How charts lie: the truncated axis\n\n"
        "This is the most common trick in published media, and you should be able to spot it "
        "in a second. Below is **exactly the same data**, drawn twice."
    ),
    code(
        'trust = df.groupby("country")["trust_news"].mean().sort_values()\n\n'
        "fig, axes = plt.subplots(1, 2, figsize=(12, 4))\n"
        "trust.plot(kind=\"bar\", ax=axes[0], color=BLUE)\n"
        "axes[0].set_ylim(0, 10)\n"
        'axes[0].set_title("Honest: axis starts at 0")\n'
        "trust.plot(kind=\"bar\", ax=axes[1], color=\"#c0392b\")\n"
        "axes[1].set_ylim(4.8, 7.6)\n"
        'axes[1].set_title("Misleading: axis starts at 4.8")\n'
        "for ax in axes:\n"
        '    ax.set_xlabel("")\n'
        '    ax.set_ylabel("Mean trust in news")\n'
        '    ax.tick_params(axis="x", rotation=30)\n'
        "plt.tight_layout()\n"
        "plt.show()"
    ),
    md(
        "**Left:** modest differences between countries. **Right:** one country looks like it "
        "has almost no trust at all. Same numbers. Only the axis changed.\n\n"
        "For a **bar chart the axis must start at zero**, because the bar's *length* is the "
        "message. (For line charts a trimmed axis is often legitimate — the message there is "
        "the *slope*.)\n\n"
        "This matters directly to EURIDICE's focus on **Communication & Media**: recognising "
        "this trick is a media-literacy skill, and *not* using it is a professional obligation."
    ),
    md(
        "## 🧭 Your decision table\n\n"
        "| What are you asking? | Chart | Main risk |\n"
        "|---|---|---|\n"
        "| How do categories compare? | **Bar** | Truncated axis exaggerates |\n"
        "| What does one variable look like? | **Histogram** | Bin count changes the story |\n"
        "| How do groups compare in spread? | **Box plot** | Hides multi-peaked data |\n"
        "| Do two numbers move together? | **Scatter** | Overplotting; ≠ causation |\n"
        "| How does something change over time? | **Line** | Only for ordered x-axes |\n"
        "| What share of a whole? | **Bar** (rarely pie) | Angles are hard to compare |\n\n"
        "## Your turn\n\n"
        "- Draw a bar chart of `household_income_band` — what do you notice about the total?\n"
        "- Make a box plot of `hours_tv` by `main_news_source`. Which group watches most?\n"
        "- Redraw the trust chart with `set_ylim(5.5, 7.0)`. How dishonest can you make it look?\n\n"
        "## ✅ What you learned\n\n"
        "Six chart types and what each is for · the bin trap · what box plots hide · "
        "overplotting and how to fix it · why pie charts fail · **how a truncated axis lies**.\n\n"
        "📚 **Go further:**\n"
        "- [From Data to Viz](https://www.data-to-viz.com/) — pick a chart from your data type\n"
        "- [Python Graph Gallery](https://python-graph-gallery.com/) — copy-paste recipes\n"
        "- [Matplotlib tutorials](https://matplotlib.org/stable/tutorials/index.html) — the "
        "official guide\n\n"
        "**Next:** [Seeing what's missing] — before you chart anything, find out what your "
        "data *isn't* telling you."
    ),
])

# ---------------------------------------------------------------------------
# 1c. missing-data.ipynb — Track 1, Lesson 3
# ---------------------------------------------------------------------------
missing = nb([
    md(
        "# 🕳️ Seeing what's missing\n\n"
        "Every real dataset has holes. The dangerous mistake is treating them as a nuisance to "
        "delete — because **the pattern of what's missing is itself data.** Who refused to "
        "answer, and why, can matter more than the answers you received.\n\n"
        "In this lesson you will use **`missingno`**, a library built for exactly one job: "
        "*making missing data visible*. Then you will prove that our survey's gaps are not "
        "random — and measure how badly they distort the findings.\n\n"
        "First, install it. It is not built into the browser's Python, so we add it — this "
        "takes a few seconds."
    ),
    code(
        "%pip install missingno\n\n"
        "import missingno as msno\n"
        "import pandas as pd\n"
        "import matplotlib.pyplot as plt\n\n"
        'df = pd.read_csv("data/eu_media_habits.csv")\n'
        'print("Loaded", len(df), "survey responses")'
    ),
    md("The blunt summary first — how many values are missing in each column?"),
    code("df.isna().sum()"),
    md(
        "Four columns have gaps. But *counts* tell you nothing about **pattern** — and pattern "
        "is where the story is.\n\n"
        "## The missingness matrix\n\n"
        "Every row of the dataset is a thin horizontal line. **White gaps = missing values.**"
    ),
    code("msno.matrix(df)\nplt.show()"),
    md(
        "Look at the two right-hand columns with gaps (`trust_news`, `pays_for_news`) and at "
        "`household_income_band`. If missingness were purely random, the white marks would be "
        "scattered like static. Do some gaps appear to line up on the same rows?\n\n"
        "## Completeness per column"
    ),
    code("msno.bar(df)\nplt.show()"),
    md(
        "## The three flavours of missing\n\n"
        "Statisticians distinguish three kinds, and the difference decides what you are allowed "
        "to do about them:\n\n"
        "| Type | Meaning | Example | Is it safe? |\n"
        "|---|---|---|---|\n"
        "| **MCAR** | Missing Completely At Random | a sensor glitched | Mostly harmless |\n"
        "| **MAR** | Missing At Random *given other columns* | older people skip a question | Fixable if you model it |\n"
        "| **MNAR** | Missing **because of the answer itself** | people who distrust the media refuse the trust question | **Dangerous — cannot be fixed from the data** |\n\n"
        "You cannot read these off a chart directly, but you *can* gather strong evidence. "
        "Let's investigate.\n\n"
        "## Do gaps travel together?\n\n"
        "The heatmap shows **correlation between missingness** — not between values. "
        "+1 means: when one is missing, the other almost always is too."
    ),
    code("msno.heatmap(df)\nplt.show()"),
    md(
        "There it is: **`household_income_band` and `pays_for_news` co-disappear at about "
        "+0.75.** That is not a coincidence — it is a *person*. Some respondents guard their "
        "financial privacy, so they skip both money-related questions.\n\n"
        "Meanwhile `hours_tv`'s gaps correlate with nothing (≈0) — a hint that it is MCAR, the "
        "harmless kind.\n\n"
        "The dendrogram groups columns that go missing together:"
    ),
    code("msno.dendrogram(df)\nplt.show()"),
    md(
        "Columns joined at a **short distance** disappear as a team. The tighter the join, the "
        "more they behave like one shared decision — here, the privacy-guarded respondent.\n\n"
        "## 🔍 Detective work: is `trust_news` MNAR?\n\n"
        "We suspect people who distrust the news refuse to rate their trust. If so, the "
        "refusers should look different in the columns we **can** see. Let's check whether "
        "they differ in social media use:"
    ),
    code(
        'skipped = df["trust_news"].isna()\n\n'
        'print("Refused the trust question:", skipped.sum(), "people\\n")\n'
        'for col in ["hours_social", "hours_news", "age"]:\n'
        '    a = df.loc[skipped, col].mean()\n'
        '    b = df.loc[~skipped, col].mean()\n'
        '    print(f"{col:14s} refusers {a:5.2f} vs answered {b:5.2f}   (diff {a - b:+.2f})")'
    ),
    md(
        "People who refused use **more social media** than those who answered. Small, but "
        "consistent — and remember from the EDA track that heavy social media use goes with "
        "*lower* trust. So the refusers are likely the low-trust group, exactly as suspected: "
        "**the answer itself caused the silence. That is MNAR.**\n\n"
        "This is real detective work — with ordinary data this is as far as you can get, "
        "because the missing answers are gone forever.\n\n"
        "## 🎭 The reveal\n\n"
        "Our dataset is **synthetic**, which lets us do something no real survey can: look at "
        "the answers *before* anyone refused. Here is the truth the survey never saw."
    ),
    code(
        'truth = pd.read_csv("data/eu_media_habits_answer_key.csv")\n'
        'check = df.merge(truth, on="respondent_id")\n\n'
        '# "deep distrust" = a trust rating of 4 or below\n'
        'really_distrust = (check["trust_news_true"] <= 4).mean()\n'
        'answered = check["trust_news"].notna()\n'
        'you_would_report = (check.loc[answered, "trust_news"] <= 4).mean()\n\n'
        'print(f"TRUE share who deeply distrust the news: {really_distrust:.1%}")\n'
        'print(f"What your survey would report:           {you_would_report:.1%}")\n'
        'print(f"\\nYou would under-count media distrust by "\n'
        '      f"{1 - you_would_report / really_distrust:.0%}.")'
    ),
    md(
        "**Roughly one in three distrustful people is invisible in your results.**\n\n"
        "Nothing was done wrong. No bug, no bad code. The survey ran correctly and still "
        "produced a conclusion that is meaningfully wrong — because the people least willing "
        "to answer were exactly the people the question was about.\n\n"
        "If this were a real study on media trust in Europe, it would report a healthier "
        "picture than reality. Policy could be written on that number.\n\n"
        "## ⚖️ Ethics lab — who disappears when you clean?\n\n"
        "The standard reflex for missing data is `dropna()` — delete incomplete rows. "
        "**Beat 1 — Build it:** let's do exactly that. **Beat 2 — Measure it:** and count the "
        "cost."
    ),
    code(
        "%run datalab_ethics.py\n\n"
        "clean = df.dropna()\n"
        'print(f"Before: {len(df)} respondents")\n'
        'print(f"After dropna(): {len(clean)} respondents")\n'
        'print(f"You deleted {len(df) - len(clean)} people — '
        '{1 - len(clean) / len(df):.0%} of your survey.\\n")\n\n'
        'representation(df, by="country")'
    ),
    md(
        "**Beat 3 — Name it.** One line of 'cleaning' silently discarded about a third of the "
        "sample — and not a random third. The people deleted are disproportionately those who "
        "guard their privacy and those who distrust institutions. Their views leave the "
        "dataset entirely, and every number you publish afterwards is calculated *as if they "
        "did not exist*.\n\n"
        "This connects straight to EURIDICE's commitments. Under the **GDPR**, consent must "
        "be *freely given* and can be withdrawn at any time (Art. 4(11), Art. 7) — refusing "
        "a question is a **right**, not a defect in your data. An analysis that silently "
        "deletes everyone who exercises that right turns a legal protection into a "
        "disadvantage. And where this data trains a high-risk system, the **EU AI Act** "
        "requires training data to be *relevant and sufficiently representative* "
        "(Art. 10(3)) — so quietly dropping a third of your respondents is a compliance "
        "problem as well as an ethical one.\n\n"
        "The *Vienna Manifesto*'s call for inclusive technology begins with the same "
        "question: **whose reality does your dataset actually represent?**\n\n"
        "**Beat 4 — Judge it.** Your call, in writing:"
    ),
    code(
        'my_decision = """\n'
        "Your answer: you must publish a report on media trust from this survey.\n"
        "Do you use dropna()? What do you tell readers about the people who refused?\n"
        '"""\n\n'
        'reflect_submit("missing-data-ethics", my_decision)'
    ),
    md(
        "## Practical guidance\n\n"
        "| Situation | Reasonable response |\n"
        "|---|---|\n"
        "| A few values, no pattern (MCAR) | Fill with median/mode, or drop — low risk |\n"
        "| Gaps predicted by other columns (MAR) | Keep those columns and model it; note it |\n"
        "| Gaps caused by the answer (MNAR) | **You cannot fix this with statistics.** Report it as a limitation |\n"
        "| A whole column mostly empty | Consider dropping the *column*, not the people |\n\n"
        "The professional habit is simple: **always look at missingness before you analyse, "
        "and always tell your reader what was missing.**\n\n"
        "## ✅ What you learned\n\n"
        "`missingno`'s matrix, bar, heatmap and dendrogram · MCAR vs MAR vs MNAR · how to "
        "gather evidence for MNAR from observed columns · that missing data can bias a "
        "headline finding by a third · why `dropna()` is an ethical decision, not a "
        "housekeeping one.\n\n"
        "📚 **Go further:**\n"
        "- [missingno on GitHub](https://github.com/ResidentMario/missingno) — every plot type\n"
        "- [pandas: working with missing data](https://pandas.pydata.org/docs/user_guide/missing_data.html)"
        " — the official guide\n\n"
        "**Next:** Track 2 puts this to work — [Explore a real dataset]."
    ),
])

# ---------------------------------------------------------------------------
# 2. eda-tutorial.ipynb — Track 2, Lesson 1
# ---------------------------------------------------------------------------
eda_tutorial = nb([
    md(
        "# 🔍 Explore a real dataset\n\n"
        "Meet **EU Media Habits 2026** — a survey of 624 people across 8 European countries "
        "about how they consume news and media. "
        "*(The data is synthetic — generated for teaching — but shaped like a real survey.)*\n\n"
        "This is **Exploratory Data Analysis (EDA)**: the first thing a data scientist does with "
        "any new dataset — look at it, summarise it, visualise it, question it."
    ),
    md("## Step 1 — Load the data\n\n`pandas` is Python's workhorse for tabular data:"),
    code(
        "import pandas as pd\n\n"
        'df = pd.read_csv("data/eu_media_habits.csv")\n'
        "df.head()  # first 5 rows"
    ),
    md(
        "Each **row** is one survey respondent; each **column** is one answer. "
        "How big is the table, and what types are the columns?"
    ),
    code('print("Rows and columns:", df.shape)\ndf.info()'),
    md(
        "Notice several columns have **missing values** (fewer non-null entries than rows) — "
        "real data is never perfectly clean. Track 1's *[Seeing what's missing]* lesson showed "
        "you how to diagnose those gaps; here we deal with them.\n\n"
        "## Step 2 — Summarise\n\n"
        "`describe()` gives instant statistics for every numeric column:"
    ),
    code("df.describe().round(2)"),
    md(
        "Read that table for a moment. What is the average age? The maximum daily social media "
        "hours? Summary tables are the fastest reality-check in data science.\n\n"
        "### Dealing with the missing values\n\n"
        "Count them, then fill them with the column median (a common, defensible choice):"
    ),
    code(
        "print(df.isna().sum())\n\n"
        'df["hours_tv"] = df["hours_tv"].fillna(df["hours_tv"].median())\n'
        'print("\\nMissing values in hours_tv after filling:", df["hours_tv"].isna().sum())'
    ),
    md("### Categorical columns\n\nFor text columns, `value_counts()` shows the distribution:"),
    code('df["main_news_source"].value_counts()'),
    md(
        "## Step 3 — Compare groups\n\n"
        "`groupby` is EDA's power tool: split the data by a category, then aggregate. "
        "Which countries spend most time on social media?"
    ),
    code(
        'social_by_country = df.groupby("country")["hours_social"].mean().sort_values(ascending=False)\n'
        "social_by_country.round(2)"
    ),
    md("## Step 4 — Visualise\n\nNumbers persuade analysts; pictures persuade everyone."),
    code(
        "import matplotlib.pyplot as plt\n\n"
        'social_by_country.plot(kind="barh", color="#1d3fbf")\n'
        'plt.xlabel("Average hours of social media per day")\n'
        'plt.title("Social media use by country — EU Media Habits 2026")\n'
        "plt.gca().invert_yaxis()\n"
        "plt.show()"
    ),
    code(
        'df["age"].plot(kind="hist", bins=25, color="#1d3fbf", edgecolor="white")\n'
        'plt.xlabel("Age")\n'
        'plt.title("Age distribution of respondents")\n'
        "plt.show()"
    ),
    md(
        "### Relationships between variables\n\n"
        "Does heavy social media use go together with trust in the news? "
        "A scatter plot and a correlation matrix answer this:"
    ),
    code(
        'df.plot(kind="scatter", x="hours_social", y="trust_news", alpha=0.35, color="#1d3fbf")\n'
        'plt.title("Social media hours vs. trust in news")\n'
        "plt.show()"
    ),
    code('df[["age", "hours_tv", "hours_social", "hours_news", "trust_news"]].corr().round(2)'),
    md(
        "A correlation near **0** means no linear relationship; near **+1/−1** means a strong one. "
        "Look at `hours_social` vs `trust_news`: there is a clear **negative** correlation in this "
        "data. ⚠️ **Correlation is not causation** — and the stronger the correlation, the more "
        "tempting the causal story becomes. Does social media erode trust? Do people who already "
        "distrust the news turn to social media instead? Is something else driving both? "
        "This data cannot tell you."
    ),
    md(
        "## ⚖️ Ethics lab — before it becomes a headline\n\n"
        "You have just produced the kind of result that ends up in a news story. Look at your "
        "country ranking and imagine the headline: *\"Austrians spend the least time on social "
        "media in Europe.\"* This lab asks whether the data can actually carry that sentence.\n\n"
        "**Beat 1 — Build it** ✅ (the country ranking above). Now:\n\n"
        "**Beat 2 — Measure it.** An average is only half a fact. The other half is *how sure "
        "you can be of it* — which depends on how many people it rests on and how much they "
        "vary. `compare_groups()` puts an approximate 95% confidence interval around every "
        "group's average:"
    ),
    code(
        "%run datalab_ethics.py\n\n"
        'compare_groups(df, "hours_social", by="country")'
    ),
    md(
        "Read the chart from the top. **Portugal's interval stands clear of everyone else's** "
        "— that difference is real. Below it, every neighbouring pair overlaps, all the way "
        "down to the bottom: seven countries put in order by differences smaller than the "
        "margin of error. \"Austria last\" is a statistical tie with Germany.\n\n"
        "Now the second question every responsible analyst asks: *how many people does each "
        "number rest on?*"
    ),
    code('compare_groups(df, "trust_news", by="gender")'),
    md(
        "**Beat 3 — Name it.** Two different problems, both common in published statistics:\n\n"
        "1. **A ranking claims more than the data holds.** Only one step of the country "
        "ranking is larger than the uncertainty. The *European Statistics Code of Practice* "
        "asks official statistics for *accuracy and reliability* and for *clarity* — which "
        "means publishing the uncertainty alongside the average, not quietly dropping it. And "
        "a country average says nothing about any single person in that country (the "
        "*ecological fallacy*).\n"
        "2. **Some groups are almost invisible.** About a dozen respondents chose `other` for "
        "gender, and fewer than ten of them answered the trust question — so their interval "
        "is over three times wider than everyone else's. Split by country, that is between "
        "one and three people per cell: a figure for \"respondents who chose *other* in "
        "Iceland\" describes **one identifiable person**. Under the GDPR (Recital 26), data is "
        "only anonymous if no one can be *singled out*.\n\n"
        "There is no clean answer to the second problem. Drop the group, and you erase people "
        "who are already under-counted. Report them on their own, and you publish noise — and "
        "possibly a person. The professional middle ground: report them **with the "
        "uncertainty stated**, never break them down further, and say plainly when a sample is "
        "too small to support a claim.\n\n"
        "**Beat 4 — Judge it.** Your call, in writing:"
    ),
    code(
        'my_decision = """\n'
        "Your answer: write the headline you would actually publish from these country\n"
        "results, and one sentence on how you would report the respondents who chose 'other'.\n"
        '"""\n\n'
        'reflect_submit("eda-headline-ethics", my_decision)'
    ),
    md(
        "## ✅ What you learned\n\n"
        "The complete first-contact EDA workflow: `read_csv` → `head` / `info` / `describe` → "
        "handle missing values → `value_counts` → `groupby` → plots → correlations — and the "
        "step most analyses skip: **measuring how certain each group's number is** before "
        "anyone turns it into a headline.\n\n"
        "📚 **Go further:**\n"
        "- [10 minutes to pandas](https://pandas.pydata.org/docs/user_guide/10min.html) — the "
        "official quick tour\n"
        "- [Python for Data Analysis](https://wesmckinney.com/book/) — the free book by pandas' "
        "creator\n\n"
        "**Next:** prove it. The *Graded exercise* notebook asks you six questions about this "
        "same dataset — with an instant checker."
    ),
])

# ---------------------------------------------------------------------------
# 3. eda-exercise.ipynb — Track 2, Lesson 2 (auto-checked)
# ---------------------------------------------------------------------------
eda_exercise = nb([
    md(
        "# 🎯 Graded exercise — EU Media Habits\n\n"
        "Six questions about the dataset you just explored. For each one:\n\n"
        "1. Write your code in the answer cell\n"
        "2. Store your final answer in the variable provided (e.g. `q1_answer`)\n"
        "3. Run the check cell — you get **instant feedback** ✅/❌\n\n"
        "Stuck? Every question has a `hint_qN()` you can call. "
        "First, run the setup cell below."
    ),
    code(
        "%run datalab_checks.py\n"
        "import pandas as pd\n"
        'df = pd.read_csv("data/eu_media_habits.csv")\n'
        "df.head(3)"
    ),
    md("## Question 1\n\n**How many respondents (rows) does the dataset contain?**"),
    code(
        "q1_answer = ...  # replace ... with your code\n\n"
        "check_q1(q1_answer)"
    ),
    md("## Question 2\n\n**Which country has the highest average daily social media hours?** (a string)"),
    code(
        "q2_answer = ...\n\n"
        "check_q2(q2_answer)"
    ),
    md("## Question 3\n\n**What is the median age of respondents who pay for news?** (`pays_for_news == 'yes'`)"),
    code(
        "q3_answer = ...\n\n"
        "check_q3(q3_answer)"
    ),
    md("## Question 4\n\n**What is the most common main news source among under-30s?** (a string)"),
    code(
        "q4_answer = ...\n\n"
        "check_q4(q4_answer)"
    ),
    md(
        "## Question 5\n\n"
        "**What is the correlation between `hours_social` and `trust_news`, rounded to 2 decimals?**"
    ),
    code(
        "q5_answer = ...\n\n"
        "check_q5(q5_answer)"
    ),
    md(
        "## Question 6 — the responsible-analyst question\n\n"
        "Before reporting any group's average, check how many people it rests on. Run "
        "`compare_groups()` on `trust_news` by `gender` and read the `n` and `flag` columns.\n\n"
        "**Which gender group's average should *not* be reported on its own?** (a string)"
    ),
    code(
        "%run datalab_ethics.py\n"
        'compare_groups(df, "trust_news", by="gender", plot=False)\n\n'
        "q6_answer = ...\n\n"
        "check_q6(q6_answer)"
    ),
    md("## Your score\n\nRun the cell below any time to see your progress:"),
    code("datalab_score()"),
    md(
        "## One more — ungraded, but it goes in your portfolio\n\n"
        "A colleague wants to publish the average trust score of the respondents who chose "
        "`other` as a headline figure. Using what you measured in Question 6, what do you tell "
        "them?"
    ),
    code(
        'my_decision = """\n'
        "Your answer: what do you tell your colleague, and what would you publish instead?\n"
        '"""\n\n'
        'reflect_submit("eda-small-groups", my_decision)'
    ),
    md(
        "## 🏁 Done?\n\n"
        "If you scored 6/6 — congratulations, you can genuinely do exploratory data analysis, "
        "*and* you checked whether your numbers deserve to be published. Head back to the "
        "course site: *Track 3 — Machine Learning Fundamentals* is next, where you train your "
        "first model."
    ),
])

# ---------------------------------------------------------------------------
# 4. first-classifier.ipynb — Track 3, Lesson 1
# ---------------------------------------------------------------------------
classifier = nb([
    md(
        "# 🤖 Train your first classifier\n\n"
        "Machine learning in one sentence: **show the computer examples, let it find the "
        "pattern, then test it on examples it has never seen.**\n\n"
        "Our task: predict whether a learner will **pass a digital-skills certification**, using "
        "the *Student Digital Skills* dataset (synthetic, education-sector themed — 900 learners). "
        "This is a **classification** problem: the answer is pass (1) or fail (0)."
    ),
    code(
        "import pandas as pd\n\n"
        'df = pd.read_csv("data/student_digital_skills.csv")\n'
        "df.head()"
    ),
    md(
        "## Features and target\n\n"
        "- **Features (X):** what we know *before* the exam — age, study hours, skill score…\n"
        "- **Target (y):** what we want to predict — `passed_certification`\n\n"
        "Notice one deliberate choice: we **leave `has_own_laptop` out of the features**. "
        "It feels like the responsible thing to do — if the model never sees who can afford a "
        "laptop, it cannot discriminate on it, right? Hold that thought; we will test it later."
    ),
    code(
        'features = ["age", "hours_online_learning", "digital_skill_score",\n'
        '            "prior_ict_courses"]          # note: has_own_laptop deliberately excluded\n'
        "X = df[features]\n"
        'y = df["passed_certification"]\n\n'
        'print("Pass rate in the data:", round(y.mean(), 2))'
    ),
    md(
        "## Split: train vs. test\n\n"
        "**The golden rule of ML:** never evaluate a model on the data it learned from — that's "
        "like grading students on the exact questions they rehearsed. We hold back 25% as a "
        "surprise exam. (The first scikit-learn import takes a few seconds to load.)"
    ),
    code(
        "from sklearn.model_selection import train_test_split\n\n"
        "X_train, X_test, y_train, y_test = train_test_split(\n"
        "    X, y, test_size=0.25, random_state=42\n"
        ")\n"
        'print(f"Training on {len(X_train)} learners, testing on {len(X_test)}")'
    ),
    md("## Train a decision tree\n\nTwo lines. Really."),
    code(
        "from sklearn.tree import DecisionTreeClassifier\n\n"
        "tree = DecisionTreeClassifier(max_depth=4, random_state=42)\n"
        "tree.fit(X_train, y_train)\n\n"
        "accuracy = tree.score(X_test, y_test)\n"
        'print(f"Accuracy on unseen learners: {accuracy:.0%}")'
    ),
    md(
        "The model now predicts pass/fail for learners it has **never seen**.\n\n"
        "Before celebrating, ask the question every honest analyst asks: **what would a lazy "
        "baseline score?** If you simply predicted *\"everyone passes\"*, you would be right "
        "about 61% of the time. Our model manages ~66% — a real improvement, but a modest one. "
        "Hold on to that mild disappointment: by the end of this notebook you will know exactly "
        "where it comes from.\n\n"
        "Where does the model go wrong? A **confusion matrix** shows the four possible outcomes:"
    ),
    code(
        "from sklearn.metrics import ConfusionMatrixDisplay\n"
        "import matplotlib.pyplot as plt\n\n"
        "ConfusionMatrixDisplay.from_estimator(\n"
        "    tree, X_test, y_test, display_labels=[\"failed\", \"passed\"], cmap=\"Blues\"\n"
        ")\n"
        'plt.title("Where the model is right and wrong")\n'
        "plt.show()"
    ),
    md(
        "## What drives the prediction?\n\n"
        "Decision trees can tell us which features mattered most:"
    ),
    code(
        "importances = pd.Series(tree.feature_importances_, index=features).sort_values()\n"
        'importances.plot(kind="barh", color="#1d3fbf")\n'
        'plt.title("Feature importance — what the model relies on")\n'
        "plt.show()"
    ),
    md(
        "## ⚖️ Ethics lab — measure what you built\n\n"
        "Imagine a university used this model to decide **who gets a scholarship place**.\n\n"
        "We were careful: the model never saw `has_own_laptop`, so it *cannot* be biased by "
        "who can afford a computer. This is such a common instinct that it has a name — "
        "**fairness through unawareness**.\n\n"
        "Most courses would ask you to *reflect* on whether that is enough. Here, we "
        "**measure it** — fairness is an empirical question, and you have the tools.\n\n"
        "**Beat 1 — Build it** ✅ (you already did). Now:\n\n"
        "**Beat 2 — Measure it.** We audit *by* laptop ownership even though the model never "
        "used it — which is exactly how real fairness audits work."
    ),
    code(
        "%run datalab_ethics.py\n\n"
        "# the audit attribute — present in the data, never given to the model\n"
        'laptop = df.loc[X_test.index, "has_own_laptop"].map({1: "has laptop", 0: "no laptop"})\n'
        "group_performance(tree, X_test, y_test, by=laptop)"
    ),
    md(
        "Read that table slowly. The model is right about **72%** of learners who own a "
        "laptop — but only **54%** of those who don't, barely better than guessing. And its "
        "*false negatives* (learners who **would have passed** but were predicted to fail) are "
        "**twice as common** in the no-laptop group: 38% against 19%.\n\n"
        "If this model allocated scholarship places, it would wrongly reject the most "
        "disadvantaged applicants twice as often — while never once looking at who owns a "
        "laptop.\n\n"
        "Now the screen the industry reaches for by default — the **four-fifths rule**: do "
        "both groups *receive* positive predictions at similar rates?"
    ),
    code("selection_rate_ratio(tree.predict(X_test), groups=laptop)"),
    md(
        "**Beat 3 — Name it.** Here is the twist that makes this lesson worth an hour of "
        "your life. This model:\n\n"
        "- never saw the sensitive attribute — *fairness through unawareness* ✅\n"
        "- gives both groups positive predictions at nearly the same rate — "
        "**passes the four-fifths screen** (ratio ≈ 0.91) ✅\n"
        "- and is **wrong about nearly half** the learners without a laptop, rejecting "
        "deserving ones twice as often ❌\n\n"
        "An analyst running the two standard checks would sign this off. The harm would sail "
        "straight through.\n\n"
        "**Why does it happen?** Not because the model is prejudiced — it is because the "
        "dataset *cannot describe* these learners. What actually determines whether they pass "
        "— a shared family computer, library opening hours, time borrowed around a job — was "
        "never recorded. For them the model is close to guessing, and that is also where our "
        "disappointing 66% headline accuracy came from.\n\n"
        "**Two lessons, and they are the heart of this course:**\n\n"
        "1. **Deleting the sensitive column does not create fairness.** It removes your "
        "ability to *detect* unfairness while leaving the unfairness in place.\n"
        "2. **One fairness metric is never enough.** Selection-rate parity and error-rate "
        "fairness are different properties; a model can satisfy one while badly violating "
        "the other. This is the central finding of a decade of fairness research.\n\n"
        "### Mind the jurisdiction\n\n"
        "The four-fifths rule you just ran is **American**: it comes from the US EEOC's "
        "*Uniform Guidelines on Employee Selection Procedures* (1978). It is not European "
        "law, and it travelled the world only because every fairness toolkit ships it.\n\n"
        "**EU law gives you no threshold at all.** Two things apply instead:\n\n"
        "- **Non-discrimination law** (Directives 2000/43/EC, 2000/78/EC) defines *indirect "
        "discrimination* qualitatively — does an apparently neutral rule put a protected "
        "group at a *particular disadvantage*, without objective justification? A court "
        "weighs the evidence; no number decides it.\n"
        "- **The EU AI Act** classifies systems governing **access to education** as "
        "**high-risk** (Annex III), obliging providers to examine data for bias "
        "(Art. 10), provide transparency (Art. 13) and ensure human oversight (Art. 14) — "
        "yet it prescribes **no fairness metric**.\n\n"
        "So Europe hands you *duties*, not a pass mark. Which measure to trust, and what "
        "gap is too large, is a judgement you must make and defend — which is precisely "
        "why the next beat exists.\n\n"
        "In Digital Humanism terms (the *Vienna Manifesto*): the model optimised accuracy "
        "but encoded an economic inequality as if it were ability — technology deciding who "
        "gets a chance, which is exactly what human-centred design exists to prevent.\n\n"
        "**Beat 4 — Judge it.** Your call, in writing. This is the skill employers and "
        "regulators actually need:"
    ),
    code(
        'my_decision = """\n'
        "Your answer: would you deploy this model to allocate scholarships? Why / why not?\n"
        "What single change would most reduce the harm you measured above?\n"
        '"""\n\n'
        'reflect_submit("ml-classifier-ethics", my_decision)'
    ),
    md(
        "*(Your judgment is now part of your DataLab portfolio. `show_portfolio()` lists "
        "what you have saved so far; the Track 3 capstone exports all of it as one file.)*\n\n"
        "## Experiment\n\n"
        "- Change `max_depth` to 2 or 10 and re-run — does test accuracy improve or get worse?\n"
        "- **Add `has_own_laptop` back into `features`** and re-run the whole notebook, ethics "
        "lab included. Does giving the model the sensitive attribute make the audit better or "
        "worse? (There is no comfortable answer — that is the point.)\n"
        "- Train on *only* the learners who own a laptop. Does the accuracy gap grow?\n"
        "- Try `from sklearn.linear_model import LogisticRegression` instead of the tree — does "
        "a different model rescue the group this data cannot describe?\n\n"
        "## ✅ What you learned\n\n"
        "Features vs. target · train/test split · fitting a classifier · accuracy against a "
        "baseline · confusion matrix · feature importance · **auditing group fairness** · why "
        "*fairness through unawareness* fails · why one fairness metric is never enough · and "
        "that EU law gives you duties rather than a threshold.\n\n"
        "📚 **Go further:**\n"
        "- [scikit-learn user guide](https://scikit-learn.org/stable/user_guide.html) — every "
        "model, explained\n"
        "- [Fairlearn](https://fairlearn.org/) — the open-source toolkit for measuring fairness\n\n"
        "EURIDICE's *AI Ethics & Digital Humanism* course goes deep on everything you just "
        "touched: bias, fairness metrics and their trade-offs, accountability, and the "
        "regulatory landscape.\n\n"
        "**Next:** *Overfitting, and choosing a model* — is a better model a fairer one?"
    ),
])

# ---------------------------------------------------------------------------
# 4b. choosing-a-model.ipynb — Track 3, Lesson 2
# ---------------------------------------------------------------------------
model_choice = nb([
    md(
        "# 🧪 Overfitting, and choosing a model\n\n"
        "In Lesson 1 you trained one model with one setting (`max_depth=4`) and took its score "
        "at face value. Professionals don't. This lesson answers two questions:\n\n"
        "1. **How complex should a model be?** Too simple and it misses the pattern; too "
        "complex and it memorises noise.\n"
        "2. **Which model should you deploy?** The obvious answer — *the most accurate one* — "
        "turns out to be an ethical choice in disguise.\n\n"
        "Same data and same split as Lesson 1, so the results are comparable."
    ),
    code(
        "import pandas as pd\n"
        "import matplotlib.pyplot as plt\n"
        "from sklearn.model_selection import train_test_split\n\n"
        'df = pd.read_csv("data/student_digital_skills.csv")\n'
        'features = ["age", "hours_online_learning", "digital_skill_score", "prior_ict_courses"]\n'
        'X, y = df[features], df["passed_certification"]\n'
        "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)\n\n"
        "baseline = max(y_test.mean(), 1 - y_test.mean())\n"
        'print(f"Always predicting \'pass\' would score {baseline:.0%} on the test set.")'
    ),
    md(
        "## Overfitting: memorising instead of learning\n\n"
        "A decision tree with more depth can carve the training data into ever smaller "
        "pieces. At some point it stops learning the *pattern* and starts memorising the "
        "*examples*. Watch both scores as the depth grows:"
    ),
    code(
        "from sklearn.tree import DecisionTreeClassifier\n\n"
        "depths = range(1, 16)\n"
        "train_acc, test_acc = [], []\n"
        "for d in depths:\n"
        "    t = DecisionTreeClassifier(max_depth=d, random_state=42).fit(X_train, y_train)\n"
        "    train_acc.append(t.score(X_train, y_train))\n"
        "    test_acc.append(t.score(X_test, y_test))\n\n"
        'plt.plot(depths, train_acc, marker="o", color="#1d3fbf", label="training data (seen)")\n'
        'plt.plot(depths, test_acc, marker="o", color="#c0392b", label="test data (unseen)")\n'
        'plt.axhline(baseline, color="gray", linestyle="--", label="always predict \'pass\'")\n'
        'plt.xlabel("Tree depth (complexity)")\n'
        'plt.ylabel("Accuracy")\n'
        'plt.title("More complexity: better at memorising, worse at predicting")\n'
        "plt.legend()\n"
        "plt.show()"
    ),
    md("Now take complexity to its limit — a tree with **no depth limit at all**:"),
    code(
        "deep = DecisionTreeClassifier(random_state=42).fit(X_train, y_train)\n\n"
        'print(f"On the data it trained on: {deep.score(X_train, y_train):.0%}")\n'
        'print(f"On new learners:           {deep.score(X_test, y_test):.0%}")\n'
        'print(f"Always predicting \'pass\':  {baseline:.0%}")'
    ),
    md(
        "A perfect score on the training data — and **worse than doing nothing** on learners "
        "it has never seen. That is **overfitting**: the model memorised 675 individual "
        "learners, noise and all, instead of learning what predicts success.\n\n"
        "## Choosing the depth honestly: cross-validation\n\n"
        "It is tempting to just pick the depth with the best *test* score from the chart. "
        "Don't: the moment the test set helps you choose, it is no longer a surprise exam, "
        "and your final score becomes optimistic.\n\n"
        "**Cross-validation** chooses using the *training* data only. It splits it into 5 "
        "parts, trains on 4 and scores on the 5th — five times, rotating — then averages:"
    ),
    code(
        "from sklearn.model_selection import cross_val_score\n\n"
        "cv_scores = {}\n"
        "for d in depths:\n"
        "    tree_d = DecisionTreeClassifier(max_depth=d, random_state=42)\n"
        "    cv_scores[d] = cross_val_score(tree_d, X_train, y_train, cv=5).mean()\n\n"
        "best_depth = max(cv_scores, key=cv_scores.get)\n"
        'print(f"Best depth by cross-validation: {best_depth} '
        '(average accuracy {cv_scores[best_depth]:.1%})")'
    ),
    md(
        "Cross-validation lands on the same depth Lesson 1 used — chosen this time without "
        "ever looking at the test set.\n\n"
        "## Comparing models\n\n"
        "Depth is one choice; the *type* of model is another. Here are five candidates, each "
        "scored by cross-validation on the training data first. *(The random forest trains "
        "100 trees, so this cell takes a few seconds in the browser.)*"
    ),
    code(
        "from sklearn.dummy import DummyClassifier\n"
        "from sklearn.ensemble import RandomForestClassifier\n"
        "from sklearn.linear_model import LogisticRegression\n"
        "from sklearn.pipeline import make_pipeline\n"
        "from sklearn.preprocessing import StandardScaler\n\n"
        "models = {\n"
        '    "Always \'pass\'": DummyClassifier(strategy="most_frequent"),\n'
        '    f"Decision tree (depth {best_depth})": '
        "DecisionTreeClassifier(max_depth=best_depth, random_state=42),\n"
        '    "Decision tree (no limit)": DecisionTreeClassifier(random_state=42),\n'
        '    "Logistic regression": make_pipeline(StandardScaler(), LogisticRegression()),\n'
        '    "Random forest": RandomForestClassifier(n_estimators=100, max_depth=5, '
        "random_state=42),\n"
        "}\n\n"
        "results = {}\n"
        "for name, model in models.items():\n"
        "    results[name] = cross_val_score(model, X_train, y_train, cv=5).mean()\n"
        "    model.fit(X_train, y_train)\n\n"
        'pd.Series(results, name="cross-validated accuracy").sort_values(ascending=False).round(3)'
    ),
    md(
        "The unlimited tree sinks to the bottom, as expected. But look at the top three: "
        "the depth-limited tree, logistic regression and the random forest are **within "
        "about a point of each other**. With 675 training examples, differences that small "
        "are noise — on accuracy, it is a tie.\n\n"
        "So how do you choose?\n\n"
        "## ⚖️ Ethics lab — the price of a better score\n\n"
        "**Beat 1 — Build it** ✅ (five fitted models).\n\n"
        "**Beat 2 — Measure it.** In Lesson 1, the tree was far less accurate for learners "
        "without their own laptop. Does a more powerful model fix that? `fairness_table()` "
        "audits every model at once:"
    ),
    code(
        "%run datalab_ethics.py\n\n"
        'laptop = df.loc[X_test.index, "has_own_laptop"].map({1: "has laptop", 0: "no laptop"})\n'
        "fairness_table(models, X_test, y_test, by=laptop)"
    ),
    md(
        "Read the `accuracy: no laptop` column, then compare it with the `Always 'pass'` row.\n\n"
        "**For learners without a laptop, every model you trained is *less* accurate than "
        "simply predicting \"pass\" for everyone.** All the accuracy these models gained, they "
        "gained on laptop owners. And the most powerful model, the random forest, has the "
        "**widest** gap of all — it extracts more from the group the data describes well, and "
        "nothing from the group it cannot.\n\n"
        "Meanwhile every row passes the four-fifths screen. On the usual checks, all of these "
        "models look fine.\n\n"
        "**Beat 3 — Name it.** \"Pick the most accurate model\" sounds neutral. It is not: "
        "overall accuracy is an average dominated by the majority, so optimising it quietly "
        "decides that the majority's errors matter more. The EU AI Act requires high-risk "
        "systems to reach an *appropriate level of accuracy* (Art. 15(1)) and their accuracy "
        "metrics to be declared to deployers (Art. 15(3)) — but it does not tell you *whose* "
        "accuracy counts. That choice is yours, and it should be made openly.\n\n"
        "What a professional would weigh:\n\n"
        "- **A simpler model with a smaller gap**, even at a small cost in overall accuracy\n"
        "- **Reporting accuracy per group**, not just overall, in the model's documentation\n"
        "- **Human review** for decisions about the group the model serves badly (Art. 14)\n"
        "- **Better data** about that group — the only option that actually fixes the cause\n\n"
        "**Beat 4 — Judge it.** Your call, in writing:"
    ),
    code(
        'my_decision = """\n'
        "Your answer: which model would you deploy to allocate scholarship places, and why?\n"
        "Name exactly what you are trading off.\n"
        '"""\n\n'
        'reflect_submit("ml-model-choice", my_decision)'
    ),
    md(
        "## ✅ What you learned\n\n"
        "Overfitting and how to see it · why the test set must not choose your model · "
        "cross-validation · comparing models against a baseline · that models tied on "
        "accuracy can differ sharply on fairness · and that *\"the most accurate model\"* is "
        "a value choice, not a neutral one.\n\n"
        "📚 **Go further:**\n"
        "- [scikit-learn: cross-validation](https://scikit-learn.org/stable/modules/cross_validation.html)\n"
        "- [Fairlearn: assessing fairness](https://fairlearn.org/main/user_guide/assessment/index.html)\n\n"
        "**Next:** the *capstone* — build, audit and document a model of your own, and export "
        "your portfolio."
    ),
])

# ---------------------------------------------------------------------------
# 4c. capstone.ipynb — Track 3, Lesson 3
# ---------------------------------------------------------------------------
capstone = nb([
    md(
        "# 🏁 Capstone — audit and document a model\n\n"
        "**The brief.** A university wants a model that predicts which applicants will pass a "
        "digital-skills certification, to help decide who receives a funded study place. "
        "You are the analyst. Your job is to:\n\n"
        "1. **Build** the best model you can *justify* — your choice of features and model\n"
        "2. **Audit** it with the measurements from the ethics labs\n"
        "3. **Document** it in a *model card* that a regulator, a journalist or an applicant "
        "could read\n"
        "4. **Export** your DataLab portfolio — your model card plus every judgment you wrote "
        "in the ethics labs\n\n"
        "There is no single right answer. What matters is that your decisions follow from "
        "your evidence, and that your documentation is honest about what the model gets wrong."
    ),
    code(
        "import pandas as pd\n"
        "from sklearn.ensemble import RandomForestClassifier\n"
        "from sklearn.linear_model import LogisticRegression\n"
        "from sklearn.model_selection import cross_val_score, train_test_split\n"
        "from sklearn.pipeline import make_pipeline\n"
        "from sklearn.preprocessing import StandardScaler\n"
        "from sklearn.tree import DecisionTreeClassifier\n\n"
        "%run datalab_ethics.py\n\n"
        'df = pd.read_csv("data/student_digital_skills.csv")\n'
        "df.head()"
    ),
    md(
        "## Step 1 — Your design choices\n\n"
        "Edit the settings below, then run the next two cells.\n\n"
        "- **`FEATURES`** — which columns may the model use? Available: `age`, "
        "`hours_online_learning`, `digital_skill_score`, `prior_ict_courses`, "
        "`has_own_laptop`. Including or excluding `has_own_laptop` is a decision you will "
        "have to defend.\n"
        "- **`MODEL_CHOICE`** — `\"tree\"`, `\"logistic\"` or `\"forest\"`.\n"
        "- **`TREE_DEPTH`** — only used by the tree."
    ),
    code(
        'FEATURES = ["age", "hours_online_learning", "digital_skill_score", "prior_ict_courses"]\n'
        'MODEL_CHOICE = "tree"     # "tree", "logistic" or "forest"\n'
        "TREE_DEPTH = 4"
    ),
    code(
        'ALLOWED = ["age", "hours_online_learning", "digital_skill_score",\n'
        '           "prior_ict_courses", "has_own_laptop"]\n'
        "unknown = [f for f in FEATURES if f not in ALLOWED]\n"
        "if unknown or not FEATURES:\n"
        '    raise ValueError(f"FEATURES must be a non-empty list chosen from {ALLOWED}; "\n'
        '                     f"these are not available: {unknown}")\n\n'
        "def build(choice):\n"
        '    if choice == "tree":\n'
        "        return DecisionTreeClassifier(max_depth=TREE_DEPTH, random_state=42)\n"
        '    if choice == "logistic":\n'
        "        return make_pipeline(StandardScaler(), LogisticRegression())\n"
        '    if choice == "forest":\n'
        "        return RandomForestClassifier(n_estimators=100, max_depth=5, random_state=42)\n"
        "    raise ValueError(f\"MODEL_CHOICE must be 'tree', 'logistic' or 'forest', "
        "not {choice!r}\")\n\n"
        'X, y = df[FEATURES], df["passed_certification"]\n'
        "X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)\n"
        "model = build(MODEL_CHOICE)\n"
        "cv = cross_val_score(model, X_train, y_train, cv=5).mean()\n"
        "model.fit(X_train, y_train)\n\n"
        "baseline = max(y_test.mean(), 1 - y_test.mean())\n"
        'print(f"Model: {MODEL_CHOICE}   Features: {FEATURES}")\n'
        'print(f"Cross-validated accuracy: {cv:.0%}   Test accuracy: {model.score(X_test, y_test):.0%}'
        '   Always-\'pass\' baseline: {baseline:.0%}")'
    ),
    md(
        "## Step 2 — Audit it\n\n"
        "Run both measurements from the ethics labs. Audit by laptop ownership **whether or "
        "not** your model uses that column — auditors check the people affected, not just "
        "the inputs."
    ),
    code(
        'laptop = df.loc[X_test.index, "has_own_laptop"].map({1: "has laptop", 0: "no laptop"})\n\n'
        "group_performance(model, X_test, y_test, by=laptop)\n"
        "print()\n"
        "selection_rate_ratio(model.predict(X_test), groups=laptop)"
    ),
    md(
        "## Step 3 — Iterate\n\n"
        "Go back to **Step 1**, change one thing, and re-run Steps 1 and 2. Some experiments "
        "worth trying:\n\n"
        "- Add `has_own_laptop` to `FEATURES`. Does the gap shrink, grow, or stay put?\n"
        "- Try each `MODEL_CHOICE`. Which gives the smallest gap? At what cost in accuracy?\n"
        "- Try a very shallow tree (`TREE_DEPTH = 2`).\n\n"
        "Keep notes: a good model card mentions what you tried and why you rejected it."
    ),
    md(
        "## Step 4 — Write the model card\n\n"
        "A **model card** is the standard short document that travels with a model: what it "
        "is for, how well it works, for whom it works badly. It is the practical format for "
        "what the EU AI Act asks providers of high-risk systems to document — intended "
        "purpose, accuracy and known limitations (Art. 11 and Annex IV; Art. 13).\n\n"
        "The numbers fill themselves in from the model you just built. **The four written "
        "fields are yours.** A few honest sentences each.\n\n"
        "**What a strong model card shows:**\n\n"
        "- you know how much your model beats the baseline — and say so plainly\n"
        "- the audit is reported as found, including what looks bad\n"
        "- the limitations name **who** the model serves poorly, and why\n"
        "- the recommendation follows from the evidence above it"
    ),
    code(
        "card = model_card(\n"
        "    model, X_test, y_test, audit_by=laptop,\n"
        '    model_name=f"{MODEL_CHOICE} (features: {len(FEATURES)})",\n'
        "    features=FEATURES,\n"
        '    intended_use="""Your answer: what is this model for, who would use it,\n'
        '        and what decision does it inform?""",\n'
        '    out_of_scope="""Your answer: what must it NOT be used for?""",\n'
        '    limitations="""Your answer: what did your audit find? For whom is the\n'
        '        model unreliable, and why?""",\n'
        '    recommendation="""Your answer: deploy, deploy with conditions, or do not\n'
        '        deploy — and why?""",\n'
        ")"
    ),
    md(
        "## Step 5 — Export your portfolio\n\n"
        "Your portfolio collects this model card and every judgment you wrote in the "
        "DataLab's ethics labs. First check what it contains:"
    ),
    code("show_portfolio()"),
    md(
        "Then build the file. Put your name in the quotes if you want it on the portfolio — "
        "it stays on your device; nothing is uploaded."
    ),
    code('export_portfolio(name="")'),
    md(
        "## 🎓 What happens next\n\n"
        "The downloaded file is **self-reported learning evidence**. It opens in any browser, "
        "and your browser's *Print → Save as PDF* turns it into a PDF if you need one.\n\n"
        "To have it count toward a **EURIDICE microcredential**, submit it through a EURIDICE "
        "partner institution — see *Earning a microcredential* on the course site.\n\n"
        "⚠️ Your portfolio lives in this browser's storage. Clearing the site's data deletes "
        "it — **download it whenever you add something.**\n\n"
        "Congratulations on finishing the DataLab."
    ),
])

# ---------------------------------------------------------------------------

NOTEBOOKS = {
    "welcome.ipynb": welcome,
    "choosing-charts.ipynb": charts,
    "missing-data.ipynb": missing,
    "eda-tutorial.ipynb": eda_tutorial,
    "eda-exercise.ipynb": eda_exercise,
    "first-classifier.ipynb": classifier,
    "choosing-a-model.ipynb": model_choice,
    "capstone.ipynb": capstone,
}

def write_content_manifest():
    """Fingerprint the shipped lessons for the site.

    JupyterLite keeps an autosaved copy of every notebook a learner has open
    for a couple of minutes, and from then on that browser shows its copy
    instead of the published file — so lesson updates would never reach it.
    The site compares this fingerprint with the one it last saw in the
    learner's browser and, on a new release, drops the stale copies of these
    notebooks (and only these: the portfolio and learners' own files stay).
    """
    import hashlib
    import json

    digest = hashlib.sha256()
    shipped = sorted(OUT.glob("*.ipynb")) + sorted(OUT.glob("datalab_*.py"))
    for f in shipped:
        digest.update(f.name.encode())
        digest.update(f.read_bytes())
    manifest = {
        "version": digest.hexdigest()[:16],
        "notebooks": sorted(f.name for f in OUT.glob("*.ipynb")),
    }
    target = ROOT / "site" / "src" / "data" / "datalab-content.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {target} (content version {manifest['version']})")


if __name__ == "__main__":
    OUT.mkdir(parents=True, exist_ok=True)
    for name, notebook in NOTEBOOKS.items():
        nbf.validate(notebook)
        nbf.write(notebook, OUT / name)
        print(f"wrote {OUT / name}")
    write_content_manifest()
