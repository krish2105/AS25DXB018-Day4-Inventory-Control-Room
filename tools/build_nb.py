import json, os, sys, importlib
import nbformat
from nbformat.v4 import new_notebook, new_markdown_cell, new_code_cell
from nbclient import NotebookClient

TOOLS = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(TOOLS)
BUILD = os.path.join(ROOT, "build")
os.makedirs(BUILD, exist_ok=True)
sys.path.insert(0, TOOLS)
NAME = "AS25DXB018_Krishna_Mathur_Day4_Inventory_Management.ipynb"

import cells; importlib.reload(cells)
try:
    import interp as I; importlib.reload(I)
except ImportError:
    I = None

mpath = os.path.join(BUILD, "outputs", "metrics.json")
M = json.load(open(mpath)) if os.path.exists(mpath) and "--fresh" not in sys.argv else {}
def m(k):
    return M.get(k, 0.0)

nb = new_notebook()
for kind, txt in cells.CELLS:
    if kind == "md":
        nb.cells.append(new_markdown_cell(txt))
    elif kind == "code":
        nb.cells.append(new_code_cell(txt))
    else:
        t = I.get(txt, m) if I else None
        if t:
            nb.cells.append(new_markdown_cell(t.strip("\n")))

nb.metadata = {"colab": {"provenance": []}, "kernelspec": {"name": "python3", "display_name": "Python 3"},
               "language_info": {"name": "python"}}

# clean build dir (data/outputs) so the run is from scratch
import shutil
for d in ("data", "outputs"):
    shutil.rmtree(os.path.join(BUILD, d), ignore_errors=True)

client = NotebookClient(nb, kernel_name="day4", timeout=900, resources={"metadata": {"path": BUILD}},
                        allow_errors=False)
client.execute()

nb.metadata = {"colab": {"provenance": []}, "kernelspec": {"name": "python3", "display_name": "Python 3"},
               "language_info": {"name": "python"}}
for c in nb.cells:
    c.pop("id", None) if False else None
nbformat.validate(nb)
out = os.path.join(BUILD, NAME)
nbformat.write(nb, out)
print("WROTE", out, "cells:", len(nb.cells))
