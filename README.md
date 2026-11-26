# Agentic AI Incident Resolution Assistant

## Run on Windows

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run app.py
```

## Performance changes
- Excel workbook and search index are cached with Streamlit `st.cache_resource` and loaded once per workbook version.
- LangGraph is compiled once and reused across Streamlit reruns.
- Search uses local BM25, token coverage and character n-gram similarity; no remote Groq call is required for each query.
- No scikit-learn, embeddings, or vector database.
- The Excel workbook remains in `data/IncidentResolution.xlsx` and must contain the `Resolution_Comments` sheet with `Issue` and `Resolution` columns.

The highest-ranked historical record is returned when its score is at least 0.10. The score is a ranking score, not a probability of correctness.
