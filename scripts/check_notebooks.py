"""Check that every DataLab notebook runs — and re-runs — cleanly.

    python scripts/check_notebooks.py

Works on a throwaway COPY of lab/notebooks, so nothing a test writes (for
example reflections.json) can ever end up in the published site.

For each notebook it runs three passes, mirroring what learners do:

  A  "Run all"                 fresh kernel, every code cell in order
  B  "Run all" again           same kernel — catches cells that break or
                               change their answer when re-run
  C  "Reload page, run all"    fresh kernel, files left over on disk

Then a learner scenario: write real reflections and a model card in every
ethics lab, export the portfolio, and validate the resulting file — plus
the store's edge cases (old file format, corrupted file, overwrites,
HTML escaping).

Exits non-zero on any failure.
"""

import contextlib
import io
import json
import re
import shutil
import sys
import tempfile
import traceback
import warnings
from pathlib import Path

from types import SimpleNamespace

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

try:
    import nbformat  # noqa: E402
except ImportError:  # e.g. when run inside Pyodide to mirror the browser exactly
    nbformat = None


def read_nb(path):
    """Read (and, when nbformat is available, validate) a notebook."""
    if nbformat is not None:
        nb = nbformat.read(path, as_version=4)
        nbformat.validate(nb)
        return nb
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    assert data.get("nbformat") == 4, f"{path}: not an nbformat-4 notebook"
    return SimpleNamespace(cells=[
        SimpleNamespace(cell_type=c["cell_type"],
                        source="".join(c["source"]) if isinstance(c["source"], list)
                        else c["source"])
        for c in data["cells"]])

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "lab" / "notebooks"
VOLATILE = re.compile(r"\d{4}-\d{2}-\d{2} \d{2}:\d{2}")
QUIET = ("FigureCanvasAgg is non-interactive",)

try:  # the browser kernel is UTF-8; Windows consoles are not
    sys.stdout.reconfigure(encoding="utf-8")
except (AttributeError, ValueError):
    pass


def translate(src):
    """Turn the IPython magics our notebooks use into plain Python."""
    out = []
    for line in src.splitlines():
        s = line.strip()
        if s.startswith("%run "):
            target = s.split(None, 1)[1]
            out.append(f"exec(__import__('pathlib').Path({target!r}).read_text("
                       f"encoding='utf-8'), globals())")
        elif s.startswith("%pip install"):
            for pkg in s.split()[2:]:
                out.append(f"__import__({pkg!r})")  # must be importable, as in the lab
        elif s.startswith("%"):
            raise ValueError(f"unhandled magic: {s}")
        else:
            out.append(line)
    return "\n".join(out)


def check_run_targets(workdir):
    """Files loaded with %run must import only the standard library at top level.

    In the browser, Pyodide loads packages (pandas, numpy, ...) only when a
    cell's own code imports them; `%run helper.py` does not trigger that. A
    top-level `import pandas` in a helper therefore fails in a fresh kernel —
    silently, because %run swallows it — and every helper function goes
    missing. This failed exactly that way once; this check stops it recurring.
    """
    import ast

    targets = set()
    for nb_path in workdir.glob("*.ipynb"):
        for cell in read_nb(nb_path).cells:
            if cell.cell_type == "code":
                for line in cell.source.splitlines():
                    if line.strip().startswith("%run "):
                        targets.add(line.strip().split(None, 1)[1])

    class TopLevelImports(ast.NodeVisitor):
        def __init__(self):
            self.found = []

        def visit_FunctionDef(self, node):  # imports inside functions are fine
            pass

        visit_AsyncFunctionDef = visit_ClassDef = visit_FunctionDef

        def visit_Import(self, node):
            self.found += [(a.name.split(".")[0], node.lineno) for a in node.names]

        def visit_ImportFrom(self, node):
            if node.level == 0 and node.module:
                self.found.append((node.module.split(".")[0], node.lineno))

    problems = []
    for target in sorted(targets):
        visitor = TopLevelImports()
        visitor.visit(ast.parse((workdir / target).read_text(encoding="utf-8")))
        for module, line in visitor.found:
            if module not in sys.stdlib_module_names:
                problems.append(f"{target}:{line} imports '{module}' at top level — "
                                f"`%run {target}` would fail in a fresh browser kernel")
    return sorted(targets), problems


def run_cells(nb, env):
    """Run every code cell in `env`. Returns (outputs, error, warnings)."""
    outputs, caught = [], []
    for i, cell in enumerate(nb.cells):
        if cell.cell_type != "code":
            continue
        buf = io.StringIO()
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            try:
                with contextlib.redirect_stdout(buf):
                    exec(compile(translate(cell.source), f"<cell {i}>", "exec"), env)
            except Exception:
                return outputs, f"cell {i}:\n{cell.source}\n\n{traceback.format_exc()}", caught
            finally:
                plt.close("all")
        caught += [f"cell {i}: {x.message}" for x in w
                   if not any(q in str(x.message) for q in QUIET)]
        outputs.append((i, VOLATILE.sub("<time>", buf.getvalue())))
    return outputs, None, caught


def check_notebook(name, workdir):
    nb = read_nb(workdir / name)
    problems = []

    env = {"__name__": "__main__"}
    a, err, warns = run_cells(nb, env)
    if err:
        return [f"pass A (run all) failed at {err}"], warns
    b, err, _ = run_cells(nb, env)
    if err:
        return [f"pass B (re-run in the same kernel) failed at {err}"], warns
    for (i, out_a), (_, out_b) in zip(a, b):
        if out_a != out_b:
            problems.append(f"cell {i} prints something different when re-run:\n"
                            f"--- first run ---\n{out_a[-600:]}\n--- re-run ---\n{out_b[-600:]}")
    _, err, _ = run_cells(nb, {"__name__": "__main__"})
    if err:
        problems.append(f"pass C (reload and run all) failed at {err}")
    return problems, warns


# ------------------------------------------------------------ learner flow

REFLECTION = re.compile(r'my_decision = """.*?"""', re.S)
CARD_FIELD = re.compile(r'(intended_use|out_of_scope|limitations|recommendation)="""(.*?)"""', re.S)
NASTY = "Fine </p><script>alert('x')</script> & <b>bold</b> — €, ñ, ü"


def as_learner(nb):
    """Fill every template answer with genuine-looking text."""
    for cell in nb.cells:
        if cell.cell_type != "code":
            continue
        cell.source = REFLECTION.sub(
            f'my_decision = """I would not publish this as it stands. {NASTY}. The audit shows '
            'the model serves one group far worse, so a human must review those cases."""',
            cell.source)
        cell.source = CARD_FIELD.sub(
            lambda m: f'{m.group(1)}="""A considered answer for {m.group(1)}: the model '
            'helps rank applicants but must never decide alone; it is unreliable for '
            'learners without a laptop."""', cell.source)
        cell.source = cell.source.replace('export_portfolio(name="")',
                                          'export_portfolio(name="Test Learner")')
    return nb


def check_learner_flow(workdir):
    problems = []
    order = ["missing-data.ipynb", "eda-tutorial.ipynb", "eda-exercise.ipynb",
             "first-classifier.ipynb", "choosing-a-model.ipynb", "capstone.ipynb"]
    for name in order:
        nb = as_learner(read_nb(workdir / name))
        _, err, _ = run_cells(nb, {"__name__": "__main__"})
        if err:
            return [f"learner flow failed in {name} at {err}"]

    store = json.loads((workdir / "reflections.json").read_text(encoding="utf-8"))
    env = {"__name__": "__main__"}
    with contextlib.redirect_stdout(io.StringIO()):
        exec(open(workdir / "datalab_ethics.py", encoding="utf-8").read(), env)
    expected = set(env["PORTFOLIO_ITEMS"])
    if set(store) != expected:
        problems.append(f"portfolio items: expected {sorted(expected)}, got {sorted(store)}")
    if "card" not in store.get("capstone-model-card", {}):
        problems.append("capstone model card was not saved")

    page_path = workdir / "portfolio.html"
    if not page_path.exists():
        return problems + ["export_portfolio() did not write portfolio.html"]
    page = page_path.read_text(encoding="utf-8")
    if "<script>alert" in page:
        problems.append("learner text is NOT escaped in portfolio.html (script injection)")
    if "&lt;script&gt;" not in page or "€, ñ, ü" not in page:
        problems.append("learner text missing or mangled in portfolio.html")
    if "Test Learner" not in page or "Not completed yet" in page:
        problems.append("portfolio.html is missing the learner name or some items")
    m = re.search(r'<script type="application/json" id="datalab-portfolio">(.*?)</script>',
                  page, re.S)
    try:
        record = json.loads(m.group(1))
        assert set(record["items"]) == expected
        assert NASTY in json.dumps(record, ensure_ascii=False), "learner text lost in JSON"
    except Exception as e:  # noqa: BLE001
        problems.append(f"embedded JSON record is broken: {e}")

    # edge cases of the store, in a clean directory of their own
    import os
    here = Path.cwd()
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        shutil.copy(workdir / "datalab_ethics.py", tmp)
        os.chdir(tmp)
        try:
            env = {"__name__": "__main__"}
            with contextlib.redirect_stdout(io.StringIO()):
                exec(open("datalab_ethics.py", encoding="utf-8").read(), env)
                # earlier DataLab versions stored plain strings
                Path("reflections.json").write_text(json.dumps({"ml-classifier-ethics": "old"}))
                loaded = env["_load"]()
                assert loaded["ml-classifier-ethics"]["text"] == "old", loaded
                # re-submitting replaces the earlier answer
                env["reflect_submit"]("ml-classifier-ethics", "x" * 80)
                env["reflect_submit"]("ml-classifier-ethics", "y" * 80)
                assert env["_load"]()["ml-classifier-ethics"]["text"] == "y" * 80
                # template text is refused and the store is left alone
                env["reflect_submit"]("eda-small-groups", "Your answer: ...")
                assert "eda-small-groups" not in env["_load"]()
                # a corrupted file must not crash the lab
                Path("reflections.json").write_text("{ not json")
                assert env["_load"]() == {}
                assert Path("reflections.broken.json").exists()
                env["show_portfolio"]()
                # exporting an empty portfolio is a friendly message, not an error
                assert env["export_portfolio"]() is None
        except AssertionError as e:
            problems.append(f"portfolio store edge case failed: {e!r}\n{traceback.format_exc()}")
        finally:
            os.chdir(here)
    return problems


def main():
    notebooks = sorted(p.name for p in SOURCE.glob("*.ipynb"))
    failures = 0
    print(f"Checking {len(notebooks)} notebooks in an isolated copy of {SOURCE}\n")
    cwd = Path.cwd()
    with tempfile.TemporaryDirectory() as tmp:
        work = Path(tmp) / "notebooks"
        shutil.copytree(SOURCE, work, ignore=shutil.ignore_patterns("__pycache__"))
        import os
        os.chdir(work)
        try:
            targets, problems = check_run_targets(work)
            failures += bool(problems)
            print(f"  {'OK  ' if not problems else 'FAIL'} %run helpers load in a fresh browser "
                  f"kernel (standard-library imports only): {', '.join(targets)}")
            for p in problems:
                print("       " + p)
            for name in notebooks:
                problems, warns = check_notebook(name, work)
                status = "OK  " if not problems else "FAIL"
                failures += bool(problems)
                print(f"  {status} {name}   (run all · re-run · reload)"
                      + (f"   [{len(warns)} warning(s)]" if warns else ""))
                for p in problems:
                    print("       " + p.replace("\n", "\n       "))
                for wmsg in warns[:3]:
                    print(f"       warning — {wmsg}")
            # a clean directory for the learner scenario
            for f in ("reflections.json", "portfolio.html", "reflections.broken.json"):
                (work / f).unlink(missing_ok=True)
            problems = check_learner_flow(work)
            failures += bool(problems)
            print(f"\n  {'OK  ' if not problems else 'FAIL'} learner scenario — 6 reflections "
                  f"+ model card → portfolio export, escaping, old/corrupt store, overwrites")
            for p in problems:
                print("       " + p)
        finally:
            os.chdir(cwd)

    leaked = [p.name for p in SOURCE.iterdir()
              if p.name in {"reflections.json", "portfolio.html", "reflections.broken.json"}]
    if leaked:
        failures += 1
        print(f"\n  FAIL test files leaked into the published source folder: {leaked}")

    print("\nRESULT:", "ALL CHECKS PASSED" if not failures else f"{failures} FAILURE(S)")
    sys.exit(1 if failures else 0)


if __name__ == "__main__":
    main()
