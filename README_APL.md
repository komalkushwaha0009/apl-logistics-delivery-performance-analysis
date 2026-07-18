# APL Logistics — Delivery Performance & Delay Risk Analysis

Diagnostic analysis of 172,765 global shipment records to quantify on-time delivery performance and identify the structural drivers of late deliveries for APL Logistics (KWE Group), completed as part of the Unified Mentor Data Analytics Internship.

## Key Finding

Only **18.6%** of orders are delivered exactly on schedule; **57.3%** are late. The dominant driver isn't geography or customer segment — it's shipping-mode SLA design. **First Class shipments are late 100% of the time**: they are promised in 1 day but consistently take 2 days to fulfill, a fixed scheduling mismatch rather than random operational variance.

| KPI | Value |
|---|---|
| Orders analyzed | 172,765 |
| On-time delivery rate | 18.6% |
| Late delivery rate | 57.3% |
| Average delay gap | +0.57 days |
| First Class late risk | 100% |
| Standard Class late risk | 39.8% (best-performing mode) |

## Repository Structure

```
├── data/                    Cleaned dataset used by both dashboards
├── notebooks/               Data cleaning, KPI computation, and chart generation scripts
├── dashboard/
│   ├── streamlit_app/       Interactive Python/Streamlit dashboard
│   └── powerbi/             Power BI Desktop (.pbix) dashboard
├── docs/                    Research paper, executive summary, and dashboard screenshots
└── figures/                 Static charts used in the research paper
```

## Dashboards

### Streamlit (Python)
```bash
cd dashboard/streamlit_app
pip install -r requirements.txt
streamlit run app.py
```
Requires `data/cleaned_data.csv` to be copied into the same folder as `app.py` (or update `DATA_PATH` in the script).

### Power BI
Open `dashboard/powerbi/APL_Logistics_Dashboard.pbix` in Power BI Desktop. Data is embedded, so no additional setup is required.

**Pages:** Overview · Regional & Product Analysis · Trends

## Methodology

1. **Data cleaning** — removed cancelled/invalid shipping records (7,754 rows), validated shipping-duration fields, standardized categorical text fields.
2. **Delay Gap calculation** — `Days for shipping (real) − Days for shipment (scheduled)`, classifying each order as On-time / Delayed / Early.
3. **KPI computation** — on-time rate, late delivery risk ratio, shipping-mode efficiency, regional/market diagnostics, customer-segment impact.
4. **Diagnostics** — isolated shipping mode as the dominant driver of delay risk versus geography, market, and customer segment.

Full methodology and findings are in [`docs/Research_Paper.docx`](docs/Research_Paper.docx); a condensed version is in [`docs/Executive_Summary.docx`](docs/Executive_Summary.docx).

## Dataset

Source data matches the schema of the public DataCo Smart Supply Chain dataset (order, shipping, customer, and product fields). See `data/cleaned_data.csv` for the cleaned version used in this analysis, or the [`notebooks/`](notebooks/) scripts for the full cleaning pipeline.

## Recommendations

- Re-align First Class SLA promises to 2 days, or invest in fulfillment capacity to genuinely support 1-day delivery.
- Review and extend the Second Class delivery window (79.8% late).
- Prioritize shipping-mode fixes over regional programs — delay risk is nearly flat across regions/markets (55–70% band).
- Add segment-aware SLA monitoring for higher-value Corporate and Home Office accounts.

## Tech Stack

- **Python**: pandas, matplotlib, streamlit, plotly
- **Power BI Desktop**: DAX measures, interactive slicers, geographic visuals
- **Data**: 180,519 raw order-line records, 40 fields

## License

MIT — see [LICENSE](LICENSE).
