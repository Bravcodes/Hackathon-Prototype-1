"""
Rankings vs. Reality -- Streamlit demo.

Run from the project folder (after src/clean.py and src/analysis.py):
    .venv/bin/streamlit run app/app.py

This file only does layout. Each tab lives in its own file in app/sections/.
"""

import sys
from pathlib import Path

import pandas as pd
import streamlit as st

# Let the app import our shared code in src/ (config.py, plots.py)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))

import config  # noqa: E402
import scoring  # noqa: E402
from sections import about, fragility, map_view, ranking, scatter, sidebar, value_added  # noqa: E402

st.set_page_config(page_title="Rankings vs. Reality", page_icon="🎓", layout="wide")


@st.cache_data
def load_results():
    return pd.read_csv(config.RESULTS_CSV)


def main():
    if not config.RESULTS_CSV.exists():
        st.error("data/results.csv not found. Run `src/clean.py` then `src/analysis.py` first.")
        st.stop()

    st.title("Rankings vs. Reality")
    st.write(
        "Do college rankings measure what's good for students? Pick what matters to you "
        "and see how the list changes, especially for low-income and first-gen students."
    )

    all_schools = load_results()
    weights = sidebar.weight_sliders()
    df = sidebar.filters(all_schools)
    if df.empty:
        st.warning("No schools match these filters.")
        st.stop()

    # Percentiles use ALL schools, so filtering doesn't change a school's score
    pcts = scoring.percentiles(all_schools).loc[df.index]
    scores = scoring.weighted_score(pcts, weights)

    tabs = st.tabs(["Your ranking", "Fragility", "Prestige vs. outcomes",
                    "Overperformers", "Map", "About & limitations"])
    with tabs[0]:
        table = ranking.render(df, scores)
    with tabs[1]:
        fragility.render(df, pcts, weights)
    with tabs[2]:
        scatter.render(df)
    with tabs[3]:
        value_added.render(df)
    with tabs[4]:
        map_view.render(table)
    with tabs[5]:
        about.render()


main()
