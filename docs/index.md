# Usage
## Getting the booklets

All booklets are available as
[releases](https://github.com/St-Josephs-Gateshead/SundayVespers/releases) allowing
you to select the desired version (hint: unless you need conformity with an
older pagination, you probably just want the latest).  The remainder of this
documentation is for people who want to *edit* the booklets, or make new
booklets.

## Technical Description

This repository is not fully automated.  (A fully automated solution for
producing booklets to sing *any* office is planned as part of the 
[OfficiumDivinum](https://github.com/OfficiumDivinum) project.)  Instead it aims
to make producing booklets by hand as little tedious as possible.  Every booklet
is in a self-contained directory, with a main latex file (`vespers.tex`), a file
for the propers `propers.tex` and, optionally, a file containing the psalms
(`psalms.tex`), and a makefile which handles building the booklet.

No output files are committed to version control.  Rather, on every push to
master (which includes every pull request) the entire repository is rebuilt with
Github Actions[^1].  If the push is *tagged*, a release is created with all the
pdfs attached; if not they are available as run artefacts from the 'Actions' tab
on github. In this way one does not need texlive/gregorio installed locally, and
output is consistent.

[^1]: We use the excellent texlive docker image maintained by [Xu
    Cheng](https://github.com/xu-cheng/texlive-action). TexLive now has a recent
    gregorio in it.
    
## Modifying the typography

To change the layout, edit `vespers.tex`.  It is a very standard LaTeX file
using `memoir`, so modification should be easy.  I have deliberately not tried
to provide a general solution for every use case, so occasional manual input to
prevent ugly typography may be required.

If the modification is designed to be *universal*, you will have to delete and
replace `vespers.tex` in every single directory.  Please do not be tempted to
symlink: it is important to be able to intervene manually as required.  TeX is
designed to *help* human typesetters, not to *replace* them.

## Modifying an extant booklet

If you have spotted a mistake in a booklet, or just want to change something in
the *content*, edit `propers.tex` (or `psalms.tex`).  These files provide the
macros which are substituted into `vespers.tex` at compile time.  If you want to
edit a *chant*, edit the corresponding `.gabc` file, as described below.

If you have only a small change, the easiest way is to find the file in
question in github's web interface, click the pencil icon to edit the file, edit
as required, and then enter a short description of the change and commit.

## Creating a new booklet

### With Cookiecutter (preferred)

Install [cookiecutter](https://github.com/cookiecutter/cookiecutter) if you do
not already have it.

```bash
cookiecutter vespers-template -o vespers/
```

And enter a name for the feast.  This will create a directory with a sensible
name and populate it with the correct files.

### Manually

Copy `vespers-template/{{cookiecutter.project_slug}}` to a sensibly named
directory. Insert the feast name in `propers.tex`. Edit anything else inside
`{{}}` and remove any directives inside `{% %}`.

## Adding Content

1. Begin by collecting all the antiphons, and saving the `.gabc` files as
   `antN.gabc` (e.g. `ant1.gabc`).  Most everything gregorian can be found at
   [gregobase](http://gregobase.selapa.net).
   
2. Ensure the mode *and termination* is specified in the antiphon file. The
   termination should be in the `mode-differentia` field, as according to the
   [gregorio documentation](http://gregorio-project.github.io/gabc/) this
   expresses: 
   > The mode or tone differentia of the piece. Typically, this expresses the
   > variant of the psalm tone to use for the piece.
   
3. Run `../../psalm_parser.py antN.gabc PSALM_NAME` for every antiphon. This
   will parse the antiphon file, find the right psalm in the relevant mode,
   format it correctly and drop the resulting .gabc file in the current
   directory with the correct name.  `PSALM_NAME` is the name of the psalm as in
   the `psalms/` directory.  If you want the solemn version of the tone add
   `--solemn`.
   
4. Add translations for everything.  I know of no reliable source of
   translations at the moment, although OfficiumDivinum aspires to become one.
   Thus I generally translate myself, or edit some available source.

5. Optionally, compile locally by running `make` in the directory to check
   everything works.
   
6. Push upstream with a new tag to generate a new release (if you have not
   checked locally, perhaps push *without* a tag first to check it works).  If
   you do not have push access, open a pull request and one of the admins will
   merge it.

   
   
   

