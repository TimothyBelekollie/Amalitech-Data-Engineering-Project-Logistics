# The Last Mile Logistics Auditor — AmaliTech Data Engineering Challenge

## A. Executive Summary

An audit of **99,441 Olist orders** identified **96,470 delivered orders with usable delivery dates**, of which **8.11% arrived after the estimated date**. Delivery performance varied substantially by state: **Alagoas (23.93%)**, **Maranhão (19.67%)**, and **Piauí (15.97%)** had especially high late-delivery rates, while **Rio de Janeiro accounted for 1,664 late deliveries** and therefore merits attention for its operational volume. Customer reviews were strongly associated with delivery timeliness: average ratings fell from **4.29/5 for on-time orders** to **3.46/5 for late orders** and **1.79/5 for super-late orders**. The **12.73-day mean absolute delivery-promise error** shows that estimated and actual arrival dates often differ considerably, including for packages delivered early. Together, these results support prioritizing high-risk regions and improving delivery-date estimates, while recognizing that observational data cannot establish that lateness alone causes low reviews.

## B. Project Links

> **Action required before submission:** Replace every `ADD_LINK` placeholder with a public URL, then verify all links in an incognito/private browser window.

- **Notebook (Google Colab):** [drive.google.com/file/d/1wN_zBmlE2xxqMkHZcUiA8HZRwouhDKtT/view?usp=sharing](https://drive.google.com/file/d/1wN_zBmlE2xxqMkHZcUiA8HZRwouhDKtT/view?usp=sharing)
- **Notebook HTML or PDF export:** ADD_LINK_TO_NOTEBOOK_EXPORT
- **Interactive Streamlit dashboard:** ADD_LINK_TO_STREAMLIT_DASHBOARD
- **Insight presentation (PDF or PowerPoint):** ADD_LINK_TO_PRESENTATION
- **Optional two-minute walkthrough:** ADD_LINK_TO_VIDEO (optional; remove this line if not provided)

## C. Technical Explanation

### Data cleaning and integration

The analysis uses the [Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce). Orders were joined to customers using `customer_id`; review records were first aggregated to one row per `order_id` before joining, avoiding unintended one-to-many duplication. Product items were also aggregated to order level for category analysis, and Portuguese product-category names were translated into English. Dates were parsed consistently and the resulting master table was checked for unique order IDs and valid delivery-status assignments. Canceled, unavailable, and other orders without usable delivery timestamps were flagged as **Not Delivered** and excluded from delivered-order lateness calculations rather than treated as on-time deliveries.

For eligible delivered orders, `Days_Difference = order_estimated_delivery_date - order_delivered_customer_date`, expressed in days. Orders were classified as **On Time** (`Days_Difference >= 0`), **Late** (`-5 <= Days_Difference < 0`), or **Super Late** (`Days_Difference < -5`). State-level late-delivery percentages were calculated using delivered orders with valid dates as the denominator. Customer review results describe associations, not causal effects.

### Candidate's Choice: Delivery Promise Accuracy

Beyond the required regional and sentiment analyses, the project compares **promised delivery windows** with **actual transit times** and measures the **absolute error between estimated and actual delivery dates**. This matters because a delivery may arrive before its promised date yet still reflect a poorly calibrated estimate; late-delivery rate alone cannot reveal that problem. The observed **12.73-day mean absolute error** motivates better delivery-date forecasting and separate monitoring of early and late estimation errors. The dashboard includes a promised-versus-actual delivery comparison to help identify systematic estimation problems.

### Reproducibility and scope

- **Data source:** Olist's historical Brazilian e-commerce order, customer, review, item, and product tables.
- **Analysis unit:** One row per order; regional metrics use delivered orders with valid dates.
- **Dashboard input:** A derived order-level dataset (`data/audit_master.csv`), not the full raw Olist CSV collection.
- **Limitations:** Historical observational data, missing delivery/review fields, uneven state-level sample sizes, and no verified distribution-center-distance data. Regional differences should not be interpreted as proof that distance caused delays.
- **Deployment:** Streamlit Community Cloud; the derived dashboard dataset must be accessible to the deployed app without committing the massive raw source files.

---

## Original AmaliTech Project Brief and Requirements

# Project Brief: The "Last Mile" Logistics Auditor

**Client:** Veridi Logistics (Global E-Commerce Aggregator)
**Deliverable:** Public Dashboard, Code Notebook & Insight Presentation

---

## 1. Business Context

**Veridi Logistics** manages shipping for thousands of online sellers. Recently, the CEO has noticed a spike in negative customer reviews. She has a "gut feeling" that the problem isn't just that packages are late, but that the estimated delivery dates provided to customers are wildly inaccurate (i.e., we are over-promising and under-delivering).

She needs you to audit the delivery data to find the root cause. She specifically wants to know: **"Are we failing specific regions, or is this a nationwide problem?"**

Your job is to build a "Delivery Performance" audit tool that connects the dots between **Logistics Data** (when a package arrived) and **Customer Sentiment** (how they rated the experience).

## 2. The Data

You will use the **Olist E-Commerce Dataset**, a real commercial dataset from a Brazilian marketplace. This is a relational database dump, meaning the data is split across multiple CSV files.

- **Source:** [Kaggle - Olist Brazilian E-Commerce Dataset](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce)
- **Key Files to Use:**
  - `olist_orders_dataset.csv` (The central table)
  - `olist_order_reviews_dataset.csv` (Sentiment)
  - `olist_customers_dataset.csv` (Location)
  - `olist_products_dataset.csv` (Categories)

## 3. Tooling Requirements

You have the flexibility to choose your development environment:

- **Option A (Recommended):** Use a cloud-hosted notebook like **Google Colab**, or **Deepnote**, etc.
- **Option B:** Use a local **Jupyter Notebook** or **VS Code**.
  - _Condition:_ If you choose this, you must ensure your code is reproducible. Do not reference local file paths (e.g., `C:/Downloads/...`). Assume the dataset is in the same folder as your notebook.
- **Dashboarding:** The final output must be a **publicly accessible link** (e.g., Tableau Public, Google Looker Studio, Streamlit Cloud, or PowerBI Web, etc.).

---

## 4. User Stories & Acceptance Criteria

### Story 1: The Schema Builder

**As a** Data Engineer,
**I want** to join the Orders, Reviews, and Customers tables into a single master dataset,
**So that** I can analyze a customer's location and their review score in the same row.

- **Acceptance Criteria:**
  - Load the raw CSVs into your notebook.
  - Perform the correct joins (e.g., join Reviews to Orders on `order_id`, join Customers to Orders on `customer_id`).
  - **Check:** Ensure you don't accidentally duplicate rows (a common error with 1-to-many joins).

### Story 2: The "Real" Delay Calculator

**As a** Logistics Manager,
**I want** to know the difference between the "Estimated Delivery Date" and the "Actual Delivery Date,"
**So that** I can see how often we are lying to customers.

- **Acceptance Criteria:**
  - Create a new calculated column: `Days_Difference` = `order_estimated_delivery_date` - `order_delivered_customer_date`.
  - Classify orders into statuses: "On Time", "Late", and "Super Late" (> 5 days late).
  - Handle missing values: Some orders were never delivered (`order_status` = 'canceled' or 'unavailable'). These should be excluded or flagged separately.

### Story 3: The Geographic Heatmap

**As a** Regional Director,
**I want** to see which specific States (`customer_state`) have the highest percentage of late deliveries,
**So that** I can focus my repair efforts on the worst regions.

- **Acceptance Criteria:**
  - Calculate the % of late orders per State.
  - Visualize this on a map or a bar chart.
  - **Insight:** Identify if "Remote" states (far from the distribution center) are disproportionately affected.

### Story 4: The Sentiment Correlation

**As a** Customer Success Lead,
**I want** to see if late deliveries actually cause bad reviews,
**So that** I can prove to the CEO that logistics is the problem.

- **Acceptance Criteria:**
  - Create a visualization comparing "Delivery Delay (Days)" vs "Average Review Score (1-5)".
  - Show the average review score for "On Time" orders vs. "Late" orders.

---

## 5. Bonus User Story: The "Translation" Challenge

**As a** Global Analyst,
**I want** to see product categories in **English**, not Portuguese,
**So that** I can understand if "Furniture" is harder to ship than "Electronics".

- **Acceptance Criteria:**
  - The `product_category_name` is in Portuguese (e.g., `cama_mesa_banho`).
  - Use the `product_category_name_translation.csv` file included in the dataset (or create your own mapping) to translate these into English for your final dashboard.

---

## 6. The "Candidate's Choice" Challenge

**As a** Creative Problem Solver,
**I want** to include one extra feature or analysis that adds specific business value,
**So that** I can demonstrate my ability to think beyond the basic requirements.

- **Instructions:**
  - Add one more metric, chart, or drill-down.
  - **Requirement:** You must justify _why_ this feature matters to the business in your README.

---

## 7. Submission Guidelines

Please edit this `README.md` file in your forked repository to include the following three sections at the top:

### A. The Executive Summary

- A 3-5 sentence summary of your findings.

### B. Project Links

- **Link to Notebook:** (e.g., Google Colab, etc.). _Ensure sharing permissions are set to "Anyone with the link can view"._
- **Link to Dashboard:** (e.g., Tableau Public, etc.).
- **Link to Presentation:** A link to a short slide deck (PDF/PPT) AND (Optional) a 2-minute video walkthrough (YouTube) explaining your results.

### C. Technical Explanation

- Briefly explain how you handled the "Data Cleaning".
- Explain your "Candidate's Choice" addition.

**Important Note on Code Submission:**

- Upload your `.ipynb` notebook file to the repo.
- **Crucial:** Also upload an **HTML or PDF export** of your notebook so we can see your charts even if GitHub fails to render the notebook code.
- Once you are ready, please fill out the [Official Submission Form Here](https://forms.cloud.microsoft/e/CeQN2mCyUr) with your links

---

## 🛑 CRITICAL: Pre-Submission Checklist

**Before you submit your form, you MUST complete this checklist.**

> ⚠️ **WARNING:** If you miss any of these items, your submission will be flagged as "Incomplete" and you will **NOT** be invited to an interview.
>
> **We do not accept "permission error" excuses. Test your links in Incognito Mode.**

### 1. Repository & Code Checks

- [ ] **My GitHub Repo is Public.** (Open the link in a Private/Incognito window to verify).
- [ ] **I have uploaded the `.ipynb` notebook file.**
- [ ] **I have ALSO uploaded an HTML or PDF export** of the notebook.
- [ ] **I have NOT uploaded the massive raw dataset.** (Use `.gitignore` or just don't commit the CSV).
- [ ] **My code uses Relative Paths.**

### 2. Deliverable Checks

- [ ] **My Dashboard link is publicly accessible.** (No login required).
- [ ] **My Presentation link is publicly accessible.** (Permissions set to "Anyone with the link can view").
- [ ] **I have updated this `README.md` file** with my Executive Summary and technical notes.

### 3. Completeness

- [ ] I have completed **User Stories 1-4**.
- [ ] I have completed the **"Candidate's Choice"** challenge and explained it in the README.

**✅ Only when you have checked every box above, proceed to the submission form.**

---
