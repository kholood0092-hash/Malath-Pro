# Malath (Malath Pro)

Small Streamlit app for sustainable home design prototypes and PDF presentation generator.

Quick start

- Create a Python environment and install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

- Run the Streamlit app:

```bash
streamlit run app.py
```

- Generate the PDF presentation (creates `Malath_Submission.pdf`):

```bash
python3 create_presentation.py
```

Notes & special files
- `requirements.txt` — project dependencies.
- `create_presentation.py` — builds a 2-page PDF using `reportlab`. If `Cairo-Regular.ttf` is present in the project root it will be used to render Arabic correctly; otherwise the script falls back to a default font and will warn about possible Arabic rendering issues.
- `Malath_Submission.pdf` — generated presentation (may be created with fallback font).
- `test_strings.txt` — example/test data you provided.

Maintenance
- `recommendations.py` contains `generate_blueprint_figure()` and Arabic helpers (`fix_ar`) — modify here to change 2D blueprint visuals.
- `scoring.py` currently returns randomized environmental data and a deterministic scoring formula — swap `get_environmental_data()` with real APIs for production.

If you'd like, I can:
- Pin dependency versions in `requirements.txt`.
- Package the app into a ZIP or Docker image.
- Replace the fallback font by adding a provided Arabic TTF and regenerating the PDF.
