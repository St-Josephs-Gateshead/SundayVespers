#!/usr/bin/python3
"""Basic parser for psalms as downloaded and converted to tex.
Format is:
{XX~} half verse * half verse

Last two verses are Gloria.
"""

import argparse
import warnings
from pathlib import Path
from re import search, sub
from collections import namedtuple
from jinja2 import Template

Line = namedtuple("Line", ["flex", "start", "end"])

indented_line_template = Template(
    "{% if flex %}\\vin {{flex}}~+\\\\\n{%endif%}\\vin {{start}}~\*\\\\\n\\vin {{end}}\\\\\n"
)
unindented_line_template = Template(
    "{% if flex %}{{flex}}~+\\\\\n{%endif%}{{start}}~\*\\\\\n{{end}}\\\\\n"
)
unindent_first_line_template = Template(
    "{% if flex %}{{flex}}~+\\\\\n\\vin {%endif%}{{start}}~\*\\\\\n\\vin {{end}}\\\\\n"
)


parser = argparse.ArgumentParser()
parser.add_argument("ANTIPHON", help="Antiphon file to parse")
parser.add_argument("PSALM_NAME", help="psalm name to output")
parser.add_argument("--range", help="Range to print")
parser.add_argument("-ng", "--no-gloria", help="Omit Gloria?", action="store_true")
parser.add_argument("-nc", "--no-copy", action="store_true", help="Skip .gabc file")
parser.add_argument(
    "--indent-mode",
    help="Indentation mode, one of 'alternate', 'hangline' or 'none'.",
    default="alternate",
)
# parser.add_argument("--line-numbers", action="store_true", help="Show line numbers.")
args = parser.parse_args()

nos = [
    "Zero",
    "One",
    "Two",
    "Three",
    "Four",
    "Five",
    "Six",
    "Seven",
    "Eight",
    "Nine",
    "Ten",
]

antiphon = Path(args.ANTIPHON).expanduser()
mode, termination = None, None
with antiphon.open() as f:
    for line in f.readlines():
        if match := search("mode:(.+);", line):
            mode = match.group(1)
        if match := search("mode-differentia:(.+);", line):
            termination = match.group(1)
if not mode:
    raise Exception("No mode found")
if not termination:
    warnings.warn("No termination found")

if match := search("ant([0-9])", antiphon.stem):
    logical_name = match.group(1)
elif match := search("(.+)-ant", antiphon.stem):
    logical_name = match.group(1)
else:
    raise Exception("Unable to determine logical name")

try:
    int(args.PSALM_NAME)
except ValueError:
    args.PSALM_NAME = args.PSALM_NAME.title()

verses = {}
if termination:
    inf = Path(f"../../psalms/{args.PSALM_NAME}-{mode}{termination}.tex")
else:
    inf = Path(f"../../psalms/{args.PSALM_NAME}-{mode}.tex")

outd = Path(".")

verses = {}
with inf.open() as f:
    versetoggle = False
    for line in f:
        no = int(search(r"^{([0-9]+)", line).group(1))
        line = sub(r"^{.+?} *", "", line)
        match = search(r"(.+)~†(.+)~\* *(.+)\\\\$", line)
        if match:
            line = dict(flex=match.group(1), start=match.group(2), end=match.group(3))
        else:
            match = search(r"(.+)~\* *(.+)\\\\$", line)
            line = dict(flex=None, start=match.group(1), end=match.group(2))

        if args.indent_mode == "alternate":
            if versetoggle:
                verses[no] = indented_line_template.render(line)
            else:
                verses[no] = unindented_line_template.render(line)
        elif args.indent_mode == "hangline":
            verses[no] = unindent_first_line_template.render(line)
        else:
            verses[no] = unindented_line_template.render(line)
        versetoggle = not versetoggle

if args.range:
    start, stop = (int(x) for x in args.RANGE.split("-"))
else:
    start = min(verses.keys())
    stop = max(verses.keys()) - 2

try:
    logical_name = int(logical_name)
    outf = outd / f"psalm{logical_name}.gabc"
    tex_name = f"\\newcommand{{\\psalm{nos[int(logical_name)]}}}{{\n"
except ValueError:
    outf = outd / f"{logical_name}.gabc"
    tex_name = f"\\newcommand{{\\{logical_name}}}{{\n"

with (outd / "psalms.tex").open("a") as f:
    f.write(tex_name)

    for i in range(start, stop + 1):
        f.write(verses[i] + "\n")

    if not args.no_gloria:
        for i in list(verses.keys())[-2:]:
            f.write(verses[i] + "\n")

    f.write("}\n\n")

if not args.no_copy:
    with outf.open("w") as f:
        with inf.with_suffix(".gabc").open() as g:
            f.write(g.read())
