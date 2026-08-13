# Nondestructive Testing and Evaluation LaTeX template record

## Target journal

- Journal: Nondestructive Testing and Evaluation
- Publisher: Taylor & Francis
- Journal page: https://www.tandfonline.com/journals/gnte20/about-this-journal
- Submission system: ScholarOne Manuscripts

## Downloaded bundle

- Bundle: Taylor & Francis Interact + NLM reference style
- Official download URL: https://files.taylorandfrancis.com/InteractNLMLaTeX.zip
- Download date: 2026-08-12
- Server last-modified value at download: 2021-11-24
- SHA-256: `56FE0625442D5AB78F672D530E8A598030EFBA389BD4E2E656A74E49A1C5FB4B`
- Original archive: `InteractNLMLaTeX.zip`
- Unmodified extracted files: `official_files/`
- Compile verification output: `compile_test/interactnlmsample_verified.pdf`

The NLM bundle was selected because current articles in the target journal use
numbered references in square brackets and an NLM-like reference-list format.
If the ScholarOne submission portal later supplies a journal-specific bundle,
the portal bundle takes precedence and must be archived separately.

## Column layout

Use a single-column author manuscript:

```tex
\documentclass[]{interact}
```

Do not use the `twocolumn` option. The official Interact instructions state
that the class produces a single-column manuscript for peer review and that
the publisher will convert it to two columns during production if required.

Do not add `onecolumn`; it is already the default. Do not add `largeformat`
unless a later journal-specific instruction explicitly requires it.

## Length limits

No explicit hard limit for Research Article page count or total word count was
found on the current journal page or in the official Interact NLM bundle as of
the download date. The template also does not specify numerical limits for the
abstract or keywords.

The following are internal drafting controls, not publisher requirements:

- Abstract: target 200-250 words
- Main text: target 7,000-8,500 words, excluding references and captions
- Keywords: target 5-7
- Full review PDF: target no more than 25 single-column pages where practical
- Move audit details, extended tables, and secondary analyses to supplementary
  material when they interrupt the main evidence chain

These controls may be relaxed if essential evidence cannot be presented
clearly within them. Scientific completeness takes precedence over an
unpublished internal page target.

## Reference style

- Use numbered citations in square brackets.
- Use `natbib` with the settings in `interactnlmsample.tex`.
- Use `\bibliographystyle{tfnlm}`.
- Keep DOI fields in the BibTeX database when available.

## Compile verification

The unmodified sample compiled successfully with TeX Live 2026 and `latexmk`:

```powershell
latexmk -pdf -interaction=nonstopmode -halt-on-error interactnlmsample.tex
```

The local TeX Live installation fails when its output directory contains
Chinese path characters. Compile from an ASCII-only staging path, such as
`D:\codex_texbuild\gnte_manuscript`, and copy the final PDF back into the
project. This is a local toolchain constraint, not a template defect.

## Official-source notes

- Taylor & Francis formatting guidance:
  https://authorservices.taylorandfrancis.com/publishing-your-research/writing-your-paper/formatting-and-templates/
- The publisher states that journal-specific Instructions for Authors take
  precedence over general templates.
- Recheck the journal page and ScholarOne instructions immediately before
  submission because publisher requirements can change.

