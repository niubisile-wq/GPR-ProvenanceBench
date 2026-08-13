# Python figure author-review return inbox

Place returned author-review files here only after the author has reviewed the figure packet.

Expected file:
1. Filled `python_figure_author_review_form.csv`, or
2. An equivalent author-marked sheet that can be manually transcribed into the canonical review form.

Do not edit tracker files inside this inbox. After manual transcription, rerun:

```powershell
py scripts\build_python_figure_author_review_intake_validator.py
```
