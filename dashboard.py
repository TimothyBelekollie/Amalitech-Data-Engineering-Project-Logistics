"""AmaliTech | Last Mile Logistics Auditor — Streamlit dashboard.

Run: streamlit run dashboard.py
Requires: data/audit_master.csv (produced by the analysis notebook).
Optional: data/brazil_states.geojson (produced by the analysis notebook).
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

st.set_page_config(page_title="Last Mile | Logistics Auditor", page_icon="📦", layout="wide")
ROOT = Path(__file__).resolve().parent
DATA = ROOT / "data"
STATUS_ORDER = ["On Time", "Late", "Super Late"]
STATUS_COLORS = {"On Time": "#16A085", "Late": "#F5B041", "Super Late": "#E74C3C"}
SCALE = [[0, "#16A085"], [0.5, "#F5B041"], [1, "#E74C3C"]]

st.markdown("""<style>
.block-container {padding-top: 1.3rem; padding-bottom: 2rem; max-width: 1450px;}
[data-testid="stMetric"] {background: #F3F7FC; border: 1px solid #DCE6F2; border-radius: 12px; padding: 16px;}
[data-testid="stMetricLabel"] {color: #25466C;}
h1,h2,h3 {letter-spacing: -.025em;}
.hero {background: linear-gradient(115deg,#102D57,#205B98); padding: 25px 30px;
 border-radius: 15px; color: white; margin-bottom: 16px;}
.hero h1 {color:white; margin:0; font-size:2.1rem;}
.hero p {color:#DCEBFF; margin:8px 0 0;}
</style>""", unsafe_allow_html=True)

@st.cache_data(show_spinner="Loading prepared order data…")
def load_data(path: str) -> pd.DataFrame:
    frame = pd.read_csv(path, low_memory=False)
    required = {"order_id", "customer_state", "is_delivered", "is_late", "delivery_status", "review_score", "delay_days", "Days_Difference"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns in audit_master.csv: {', '.join(sorted(missing))}")
    for field in ("is_delivered", "is_late"):
        if frame[field].dtype != bool:
            frame[field] = frame[field].astype(str).str.lower().isin(["true", "1", "yes"])
    for field in ("review_score", "delay_days", "Days_Difference", "promised_window_days", "actual_transit_days"):
        if field in frame.columns:
            frame[field] = pd.to_numeric(frame[field], errors="coerce")
    return frame

@st.cache_data(show_spinner=False)
def load_geojson(path: str):
    with open(path, encoding="utf-8") as handle:
        return json.load(handle)


def chart_style(fig, height=430):
    fig.update_layout(template="plotly_white", height=height, margin=dict(l=15, r=20, t=45, b=30),
                      font=dict(color="#193756"), legend_title_text="")
    return fig


st.markdown('<div class="hero"><h1>📦 The Last Mile | Logistics Auditor</h1>'
            '<p>Veridi Logistics · Olist Brazilian e-commerce orders · AmaliTech Data Engineering Challenge</p></div>',
            unsafe_allow_html=True)
st.caption("Historical descriptive audit · A relationship between late deliveries and reviews does not establish causation.")

path = DATA / "audit_master.csv"
if not path.exists():
    st.error("Missing `data/audit_master.csv`. Run the analysis notebook, then copy its exported CSV into the `data/` folder alongside this app.")
    st.code("logistics/\n├── dashboard.py\n├── requirements.txt\n└── data/\n    ├── audit_master.csv\n    └── brazil_states.geojson  # optional")
    st.stop()
try:
    df = load_data(str(path))
except (ValueError, OSError) as exc:
    st.error(f"Could not load prepared dataset: {exc}")
    st.stop()

all_delivered = df.loc[df["is_delivered"]].copy()
all_delivered = all_delivered[all_delivered["delivery_status"].isin(STATUS_ORDER)]
if all_delivered.empty:
    st.error("No delivered orders with valid dates were found.")
    st.stop()

with st.sidebar:
    st.header("Explore the data")
    state_options = sorted(all_delivered["customer_state"].dropna().unique().tolist())
    selected_states = st.multiselect("Brazilian states", state_options, default=state_options)
    selected_status = st.multiselect("Delivery classification", STATUS_ORDER, default=STATUS_ORDER)
    if "category" in all_delivered.columns:
        category_options = sorted(all_delivered["category"].fillna("Unknown").astype(str).unique().tolist())
        selected_categories = st.multiselect("Product category (English)", category_options, default=category_options)
    else:
        selected_categories = None
    min_orders = st.slider("Minimum delivered orders per state", 1, 500, 30)
    st.divider()
    st.caption("Metrics and charts respond to the selected filters. State-level comparisons use delivered orders with valid dates.")

filtered = all_delivered.loc[
    all_delivered["customer_state"].isin(selected_states)
    & all_delivered["delivery_status"].isin(selected_status)
].copy()
if selected_categories is not None:
    filtered = filtered.loc[filtered["category"].fillna("Unknown").astype(str).isin(selected_categories)]
if filtered.empty:
    st.warning("No delivered orders match these filters. Expand the state, status, or category selection.")
    st.stop()

n = len(filtered)
late_count = int(filtered["is_late"].sum())
super_late = int((filtered["delivery_status"] == "Super Late").sum())
mae = filtered["Days_Difference"].abs().mean()
review_mean = filtered["review_score"].mean()

cols = st.columns(5)
for col, label, val in zip(cols,
    ["Delivered orders", "Late delivery rate", "Super-late orders", "Average review", "Promise error (MAE)"],
    [f"{n:,}", f"{late_count / n:.2%}", f"{super_late:,}", f"{review_mean:.2f} / 5" if pd.notna(review_mean) else "N/A", f"{mae:.2f} days"]):
    col.metric(label, val)
st.caption(f"Coverage: {n:,} filtered delivered orders from {len(df):,} total source orders. "
           "'Super Late' means more than five days after the estimated delivery date. "
           "Promise MAE measures absolute early-or-late error, not average lateness.")

geo_tab, reviews_tab, promise_tab, category_tab, quality_tab = st.tabs([
    "🗺️ Regional performance", "⭐ Customer sentiment", "⏱️ Delivery promises", "📦 Categories", "🔎 Data quality & export"
])

state_summary = filtered.groupby("customer_state", as_index=False).agg(
    orders=("order_id", "size"), late_orders=("is_late", "sum"),
    avg_review=("review_score", "mean"))
state_summary["late_rate_pct"] = 100 * state_summary["late_orders"] / state_summary["orders"]
state_visible = state_summary.loc[state_summary["orders"] >= min_orders].copy()

with geo_tab:
    st.subheader("Story 3 · Which Brazilian states are falling behind?")
    st.caption("Late rate = orders delivered after the estimated date ÷ delivered orders with valid dates. "
               "Compare order counts before interpreting rates for small states.")
    left, right = st.columns([1.2, 1])
    with left:
        geo_path = DATA / "brazil_states.geojson"
        if geo_path.exists():
            try:
                geo = load_geojson(str(geo_path))
                # The supplied GeoJSON uses two-letter state codes in properties.SIGLA.
                for feature in geo.get("features", []):
                    properties = feature.get("properties") or {}
                    code = properties.get("SIGLA") or feature.get("id")
                    if code is not None:
                        normalized_code = str(code).strip().upper()
                        properties["SIGLA"] = normalized_code
                        feature["id"] = normalized_code
                        feature["properties"] = properties

                geo_ids = {
                    feature["id"] for feature in geo.get("features", [])
                    if feature.get("id")
                }
                map_data = state_visible.copy()
                map_data["customer_state"] = (
                    map_data["customer_state"].astype("string").str.strip().str.upper()
                )
                unmatched = sorted(
                    set(map_data["customer_state"].dropna()) - geo_ids
                )
                if unmatched:
                    st.warning(
                        "State codes not found in the GeoJSON: "
                        + ", ".join(unmatched)
                        + ". These states are omitted from the map but remain in the bar chart."
                    )
                map_data = map_data.loc[map_data["customer_state"].isin(geo_ids)]
                if map_data.empty:
                    st.info("No matching state codes are available for the map. Use the state bar chart.")
                else:
                    map_fig = px.choropleth(
                        map_data,
                        geojson=geo,
                        locations="customer_state",
                        featureidkey="properties.SIGLA",
                        color="late_rate_pct",
                        color_continuous_scale=SCALE,
                        hover_name="customer_state",
                        hover_data={
                            "orders": True,
                            "late_orders": True,
                            "avg_review": ":.2f",
                            "late_rate_pct": ":.2f",
                        },
                        labels={
                            "late_rate_pct": "Late rate (%)",
                            "orders": "Delivered orders",
                            "late_orders": "Late orders",
                            "avg_review": "Mean review",
                        },
                        title="Late delivery rate across Brazil",
                    )
                    map_fig.update_geos(
                        fitbounds="locations", visible=False,
                        showcountries=False, showcoastlines=False
                    )
                    map_fig.update_layout(
                        coloraxis_colorbar=dict(title="Late %", thickness=13, len=0.65)
                    )
                    st.plotly_chart(chart_style(map_fig, 500), use_container_width=True)
            except (OSError, ValueError, KeyError, TypeError) as exc:
                st.info(f"Map unavailable ({exc}). The state bar chart remains available.")
        else:
            st.info("Add `data/brazil_states.geojson` to enable the interactive Brazil map.")
    with right:
        if not state_visible.empty:
            bar = px.bar(state_visible.sort_values("late_rate_pct", ascending=False),
                x="customer_state", y="late_rate_pct", color="late_rate_pct", color_continuous_scale=SCALE,
                hover_data=["orders", "late_orders"], title="Late-delivery rate by state",
                labels={"customer_state": "State", "late_rate_pct": "Late deliveries (%)"})
            bar.update_layout(coloraxis_showscale=False)
            st.plotly_chart(chart_style(bar, 500), use_container_width=True)
        else:
            st.info("No states meet the minimum-order threshold. Lower the slider.")
    st.dataframe(state_summary.sort_values("late_rate_pct", ascending=False).rename(columns={
        "customer_state": "State", "orders": "Delivered orders", "late_orders": "Late orders",
        "late_rate_pct": "Late rate (%)", "avg_review": "Average review"
    }).style.format({"Late rate (%)": "{:.2f}", "Average review": "{:.2f}"}),
        use_container_width=True, hide_index=True)
    st.info("Business action: prioritize states by both late-delivery rate and number of affected orders; "
            "the dataset does not identify warehouse locations or prove geographic remoteness caused delays.")

with reviews_tab:
    st.subheader("Story 4 · How does delivery performance relate to customer reviews?")
    review = filtered.groupby("delivery_status", as_index=False).agg(
        average_review=("review_score", "mean"), orders=("order_id", "size"))
    review["delivery_status"] = pd.Categorical(review["delivery_status"], STATUS_ORDER, ordered=True)
    review = review.sort_values("delivery_status")
    a, b = st.columns(2)
    with a:
        f = px.bar(review, x="delivery_status", y="average_review", color="delivery_status",
            color_discrete_map=STATUS_COLORS, text="average_review", hover_data=["orders"],
            labels={"delivery_status": "Delivery status", "average_review": "Average review (1–5)"},
            title="Average customer rating by delivery status")
        f.update_traces(texttemplate="%{text:.2f}", textposition="outside")
        f.update_layout(yaxis_range=[0, 5.4], showlegend=False)
        st.plotly_chart(chart_style(f), use_container_width=True)
    with b:
        scatter_data = filtered.dropna(subset=["delay_days", "review_score"])
        if not scatter_data.empty:
            sample = scatter_data.sample(min(3500, len(scatter_data)), random_state=42)
            f = px.scatter(sample, x="delay_days", y="review_score", color="delivery_status",
                color_discrete_map=STATUS_COLORS, opacity=0.3,
                labels={"delay_days": "Days late (0 = on time/early)", "review_score": "Review score"},
                title="Delay severity vs. individual review score")
            st.plotly_chart(chart_style(f), use_container_width=True)
    bins = [-0.001, 0, 1, 3, 5, 10, 20, np.inf]
    names = ["On time / early", "0–1 day", "1–3 days", "3–5 days", "5–10 days", "10–20 days", ">20 days"]
    scored = filtered.dropna(subset=["delay_days", "review_score"]).copy()
    scored["delay_band"] = pd.cut(scored["delay_days"], bins=bins, labels=names, include_lowest=True)
    trend = scored.groupby("delay_band", observed=True, as_index=False).agg(
        avg_review=("review_score", "mean"), orders=("order_id", "size"))
    if not trend.empty:
        f = px.line(trend, x="delay_band", y="avg_review", markers=True, hover_data=["orders"],
            title="Average review across delay bands", labels={"delay_band": "Delay band", "avg_review": "Average review (1–5)"})
        f.update_yaxes(range=[0, 5.1])
        st.plotly_chart(chart_style(f, 360), use_container_width=True)
    st.caption("Review scores are observational. Other factors, including product quality and seller service, may also affect ratings.")

with promise_tab:
    st.subheader("Candidate's Choice · Are estimated delivery dates accurate?")
    st.caption("The signed difference is estimated delivery date minus actual delivery date. "
               "Positive = arrived early; negative = arrived late. MAE ignores the sign.")
    a, b = st.columns(2)
    with a:
        diff = filtered["Days_Difference"].dropna()
        if not diff.empty:
            low, high = diff.quantile([0.01, 0.99])
            trimmed = diff.clip(lower=low, upper=high)
            f = px.histogram(x=trimmed, nbins=55, title="Estimated minus actual delivery date (1st–99th percentile capped)",
                             labels={"x": "Days difference", "y": "Orders"})
            f.add_vline(x=0, line_dash="dash", line_color="#D64545")
            st.plotly_chart(chart_style(f), use_container_width=True)
    with b:
        if {"promised_window_days", "actual_transit_days"}.issubset(filtered.columns):
            sample = filtered.dropna(subset=["promised_window_days", "actual_transit_days"])
            if not sample.empty:
                sample = sample.sample(min(3500, len(sample)), random_state=42)
                f = px.scatter(sample, x="promised_window_days", y="actual_transit_days",
                    color="delivery_status", color_discrete_map=STATUS_COLORS, opacity=0.35,
                    title="Promised window vs. actual transit time",
                    labels={"promised_window_days": "Promised delivery window (days)",
                            "actual_transit_days": "Actual transit time (days)"})
                maximum = max(sample["promised_window_days"].max(), sample["actual_transit_days"].max())
                f.add_shape(type="line", x0=0, y0=0, x1=maximum, y1=maximum,
                            line=dict(color="#2C3E50", dash="dash", width=1.5))
                st.plotly_chart(chart_style(f), use_container_width=True)
    st.info("Business action: calibrate estimated delivery windows by state and route. "
            "A large absolute error can reflect early deliveries as well as late ones.")

with category_tab:
    st.subheader("Bonus · English-language product category drill-down")
    if "category" not in filtered.columns:
        st.info("The exported master dataset has no `category` column. Re-run the notebook's category translation step.")
    else:
        cat = filtered.assign(category=filtered["category"].fillna("Unknown")).groupby("category", as_index=False).agg(
            orders=("order_id", "size"), late_orders=("is_late", "sum"), avg_review=("review_score", "mean"))
        cat["late_rate_pct"] = 100 * cat["late_orders"] / cat["orders"]
        cat = cat.loc[cat["orders"] >= min_orders].sort_values("orders", ascending=False)
        if not cat.empty:
            top = cat.head(15)
            f = px.bar(top.sort_values("late_rate_pct"), x="late_rate_pct", y="category", orientation="h",
                color="late_rate_pct", color_continuous_scale=SCALE,
                hover_data=["orders", "late_orders"], title="Late rate by product category (top 15 by volume)",
                labels={"category": "Category", "late_rate_pct": "Late rate (%)"})
            f.update_layout(coloraxis_showscale=False)
            st.plotly_chart(chart_style(f, 510), use_container_width=True)
            st.dataframe(cat, use_container_width=True, hide_index=True)
        else:
            st.info("No categories meet the minimum-order threshold.")
        st.caption("Each order is assigned its primary category in the notebook; mixed-category orders are not represented as multiple rows.")

with quality_tab:
    st.subheader("Story 1 & 2 · Audit integrity and delivery classification")
    c1, c2, c3 = st.columns(3)
    c1.metric("Total source orders", f"{len(df):,}")
    c2.metric("Unique order IDs", f"{df['order_id'].nunique():,}")
    c3.metric("Non-delivered / missing valid dates", f"{len(df) - int(df['is_delivered'].sum()):,}")
    st.caption("Non-delivered orders are excluded from late-rate denominators, not silently treated as on time.")
    st.dataframe(df["delivery_status"].fillna("Unknown").value_counts().rename_axis("Delivery status")
                 .reset_index(name="Orders"), hide_index=True, use_container_width=True)
    if df["order_id"].duplicated().any():
        st.error("Data quality warning: duplicate order IDs detected in the master dataset.")
    else:
        st.success("One row per order: no duplicate order IDs detected.")
    st.download_button("Download filtered delivered orders (CSV)",
                       filtered.to_csv(index=False).encode("utf-8"),
                       file_name="last_mile_filtered_orders.csv", mime="text/csv")
    st.download_button("Download filtered state summary (CSV)",
                       state_summary.to_csv(index=False).encode("utf-8"),
                       file_name="last_mile_state_summary.csv", mime="text/csv")
    st.caption("Source: Olist Brazilian E-Commerce public dataset. Data is historical; the dashboard does not track live shipments.")

st.divider()
st.caption("AmaliTech Data Engineering Challenge · Veridi Logistics case study · Built with Streamlit, pandas and Plotly")
