# The Last Mile Logistics Auditor

**AmaliTech Data Engineering Challenge | Olist Brazilian E-Commerce Dataset**
**Author:Timothy Belekollie**

## A. Executive Summary

An audit of **99,441 Olist orders** identified **96,470 delivered orders with usable delivery dates**, of which **8.11% arrived after the estimated date**. Delivery performance varied substantially by state: **Alagoas (23.93%)**, **Maranhão (19.67%)**, and **Piauí (15.97%)** had especially high late-delivery rates, while **Rio de Janeiro recorded 1,664 late deliveries**. Customer reviews were associated with delivery timeliness: average ratings fell from **4.29/5 for on-time orders** to **3.46/5 for late orders** and **1.79/5 for super-late orders**. The **12.73-day mean absolute delivery-promise error** indicates substantial differences between estimated and actual arrival dates, including early deliveries. These findings support prioritizing high-risk regions, accounting for affected-order volume, and improving delivery-date estimates; the observational data do not establish causation.

## B. Project Links

- **GitHub repository:** [Amalitech-Data-Engineering-Project-Logistics](https://github.com/TimothyBelekollie/Amalitech-Data-Engineering-Project-Logistics)
- **Analysis notebook:** [View notebook on Google Drive](https://drive.google.com/file/d/1wN_zBmlE2xxqMkHZcUiA8HZRwouhDKtT/view?usp=sharing)
- **Notebook PDF export:** [Public link to PDF export](<https://github.com/TimothyBelekollie/Amalitech-Data-Engineering-Project-Logistics/blob/main/TimothyBelekollie_Last_Mile_Logistics_Auditor.ipynb%20-%20Colab.pdf>)
- **Interactive Streamlit dashboard:** [Last Mile Logistics Auditor](https://tbelekol-logistics.streamlit.app/)
- **Insight presentation:** [Public link to presentation](https://docs.google.com/presentation/d/1O8Eba6xxv1QdJY8KqF0P_KT05BbH-N0X/edit?usp=sharing&ouid=105877769423016947018&rtpof=true&sd=true)
- **Insight presentation Recording:** [Public link to presentation Recording ](https://docs.google.com/videos/d/1buRZfk0SGkOR7YvUJ7PGulbknIJPQW7S3lcKbFYfUpE/play?usp=sharing)

## C. Technical Explanation

### Data cleaning and integration

The analysis uses the [Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Orders were joined to customers using `customer_id`; review records were aggregated to one row per `order_id` before joining to prevent one-to-many row inflation. Product items were aggregated to order level for category analysis, and Portuguese product-category names were translated into English. Delivery timestamps were parsed consistently, and the master table was checked for unique order IDs and valid delivery-status assignments. Orders without usable delivery timestamps were excluded from delivered-order lateness calculations instead of being counted as on time.

For eligible delivered orders, `Days_Difference = order_estimated_delivery_date - order_delivered_customer_date`, measured in days. The classification is **On Time** (`Days_Difference >= 0`), **Late** (`-5 <= Days_Difference < 0`), and **Super Late** (`Days_Difference < -5`). State late-delivery rates use eligible delivered orders as the denominator. Customer review comparisons are descriptive associations, not causal estimates.

### Candidate's Choice: Delivery Promise Accuracy

In addition to geographic delay rates and customer sentiment, the project evaluates how closely estimated delivery dates match actual arrivals. The **mean absolute promise error is 12.73 days**, and the **median absolute promise error is 12.17 days**. Absolute error includes both early and late arrivals: **12.73 days does not mean the average order arrived 12.73 days late**. This additional metric matters because late-delivery rates alone cannot identify overly conservative or otherwise poorly calibrated delivery estimates.

## Business Question

Are estimated delivery dates reliable? Where are late deliveries concentrated? How is delivery timeliness associated with customer satisfaction?

## Dataset and Scope

The project analyzes historical Brazilian e-commerce orders, customers, reviews, items, and products from Olist. The order-level audit preserves **99,441 original orders**, while **96,470** have the delivered status and valid timestamps required for the timing analysis. The dashboard uses processed data rather than the full collection of raw source CSVs.

## Key Findings

| Measure                                    |     Result |
| ------------------------------------------ | ---------: |
| Original orders                            |     99,441 |
| Eligible delivered orders                  |     96,470 |
| National late-delivery rate                |      8.11% |
| Super-late rate (more than five days late) |      4.37% |
| Average delay among late orders            |  9.55 days |
| Alagoas late-delivery rate                 |     23.93% |
| Maranhão late-delivery rate               |     19.67% |
| Piauí late-delivery rate                  |     15.97% |
| Rio de Janeiro late orders                 |      1,664 |
| Average review: on time                    |   4.29 / 5 |
| Average review: late                       |   3.46 / 5 |
| Average review: super late                 |   1.79 / 5 |
| Mean absolute delivery-promise error       | 12.73 days |
| Median absolute delivery-promise error     | 12.17 days |

## Interactive Dashboard

The Streamlit dashboard presents national delivery metrics, state-level performance, review scores by delivery timeliness, delivery promise accuracy, and downloadable summaries. The geographic visualization uses a Brazilian state GeoJSON and state abbreviations to connect each state's metrics to its boundary.

## Business Recommendations

1. **Investigate high-rate states** such as Alagoas, Maranhão, and Piauí, while considering sample sizes.
2. **Consider total customer impact** as well as percentages; higher-volume states can generate more late orders despite lower late rates.
3. **Improve delivery-date estimates** by analyzing both early and late prediction errors across regions.
4. **Track customer experience alongside logistics metrics**, using review scores and delay severity together.

## Repository Layout

```text
.
├── README.md
├── dashboard.py
├── requirements.txt
├── analysis.ipynb
├── <notebook-export>.pdf
└── data/
    ├── audit_master.csv
    ├── state_summary.csv
    ├── promise_summary.csv
    └── brazil_states.geojson
```

*The notebook and PDF may have longer descriptive filenames in the actual repository. The tree above illustrates their roles.*

## Run the Dashboard Locally

```bash
pip install -r requirements.txt
streamlit run dashboard.py
```

Run these commands from the repository root. The dashboard's input files must be present in `data/`, and file paths should be relative to the repository rather than to a personal Google Drive or local machine. The analysis notebook may require the original Olist CSV files to regenerate the processed exports; those large raw files are not included in the repository.

## Limitations

This is a historical observational analysis. Missing delivery timestamps or reviews affect the applicable analysis samples; state sample sizes differ; and the available data do not establish the operational causes of regional delays or prove that lateness alone causes negative reviews.

## Data Source

[Olist Brazilian E-Commerce Public Dataset — Kaggle](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
