#!/home/mi/docs/prog/python/nblib/.venv/bin/python
"""
Tool to manage jupyter notebooks.

nblib markdown ID  # show markdown of ID entry for fzf preview
nblib code ID      # output code of ID entry (RAW!)
"""

import argparse
import json
import pathlib
import sys

from app.parser import Nblib

lib = Nblib()


def scan():
    """
    Scan for jupyter notebook in all subfolders and write json structure in ./conf/nblib.json
    starts search from current working path
    """
    root = pathlib.Path.cwd()
    print(f"Searching notebooks from {root} and below")

    for nb in root.rglob("*.ipynb"):
        if "checkpoint" in nb.name:
            continue
        with open(nb, "r", encoding="UTF8") as f:
            nb_json = json.load(f)
        print(f"Parsing: {nb.name}")
        lib.parse(nb_json, nb.resolve())
    lib.save()
    print("Completed scanning. You can view with `nblib view | fzf`")


def view():
    """flatten json structure so it is easy to view in fzf"""
    if not lib.load():
        scan()
    for e in lib.flatten():
        print(e)


parser = argparse.ArgumentParser(
    description=""" Tool to manage jupyter notebooks.
                    It organize notebooks content based on markdown 
                    header structure. Each header must be in separate
                    sell to be recognized.""",
)
parser.add_argument(
    "--scan",
    action="store_const",
    const=scan,
    dest="cmd",
    default=scan,
    help=""" scan all subfolders startig from cwd().
             Store result as json in `./conf/nblib.json` """,
)
parser.add_argument(
    "--view",
    action="store_const",
    const=view,
    dest="cmd",
    help="""generate flat list for fzf selection""",
)

args = parser.parse_args()
args.cmd()
