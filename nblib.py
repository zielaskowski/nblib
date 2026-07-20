#!/home/mi/docs/prog/python/nblib/.venv/bin/python
"""
Tool to manage jupyter notebooks.
"""

import argparse
import json
import pathlib
import sys
from argparse import Namespace

from app.parser import Nblib

lib = Nblib()


def scan(arg: Namespace):
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
    print(
        "Completed scanning. You can view with `nblib_fzf.sh` or `jless ./nblib.json`"
    )


def view(arg: Namespace):
    """flatten json structure so it is easy to view in fzf"""
    if not lib.load():
        scan(arg)
    for e in lib.flatten():
        disp_cols = [
            "\\e[1;34m" + e["id_disp"] + "\\e[0m",  # bold blue
            e["file_name"],
            e["uuid"] + "\n",
        ]  # color
        print("\t".join(disp_cols))


def preview(arg: Namespace) -> None:
    """preview markdown for selected uuid"""
    if not arg.id or not arg.what:
        print("please provide --id and --what to display")
        sys.exit(1)
    if arg.what not in ["code", "markdown"]:
        print(f"unknown value for --what: {arg.what}")
        print("Only `code` and `markdown` is accepted")
        sys.exit(1)
    if not lib.load():
        scan(arg)
    content = lib.get_data(uuid=arg.id, what=arg.what)
    if content is None:
        print(f"missing id: {arg.id}")
    if content == "":
        content = "--no data--"
    print(content)


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

parser.add_argument(
    "--preview",
    action="store_const",
    const=preview,
    dest="cmd",
    help=""" show markdown of uuid entry for fzf preview""",
)
parser.add_argument("--what", help=""" slect what to display: markdown or code""")
parser.add_argument("--id", help="""select chapter id to display or copy""")

args = parser.parse_args()
args.cmd(args)
