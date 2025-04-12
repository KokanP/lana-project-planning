# Lana Project - Cost Estimation Calculator & Documentation

This repository hosts files related to the planning and cost estimation for the Lana Project, including automated analysis reports.

## Hosted Version

The interactive cost calculator and links to other documents are hosted at:

**[`https://lana.freq.band/`](https://lana.freq.band/)**

## Contents

### Project Related
* **[`lana-cost-calculator.html`](./lana-cost-calculator.html)**: The main **interactive** cost estimation tool built with HTML, CSS, and JavaScript. Allows for live calculation updates based on user inputs. *(Direct Link to Calculator)*
* **[`lana_project_cost_sample.html`](./lana_project_cost_sample.html)**: A **static HTML version** of the project documentation containing sample cost estimations based on default parameters (10% EUR Rate Adjustment, 10x LANA Multiplier). *(Direct Link to Static Sample Doc)*
* **[`presentation.html`](./presentation.html)**: A scrollable presentation demo covering the project plan, calculator, sample costs, and next steps. *(Direct Link to Presentation Demo)*


### General Analysis
* **[`static_lana_report.html`](./static_lana_report.html)**: Static report combining API and website data analysis. *(Manually generated snapshot)*
* **[`whales-analysis.html`](./whales-analysis.html)**: An analytical article examining the role and impact of cryptocurrency "whales" holding assets in low-volume market conditions. *(Direct Link to Whale Analysis Context)*
    * **[`LANA_Whale_Report.html`](./LANA_Whale_Report.html)**: Automated report showing LanaCoin top holder concentration and distribution analysis. *(Auto-updated daily via GitHub Actions)*
* **[`lana_decentralization_dilemma.html`](./lana_decentralization_dilemma.html)**: Analysis of wealth concentration risks and the need for funded project management. *(Direct Link to Decentralization Dilemma Analysis)*
* **[`Building-Trust.html`](./Building-Trust.html)**: Static HTML version of the 'Building Trust: Essential Website Elements for Level 1 Blockchain Cryptocurrencies' guidelines document. *(Direct Link to Trust Guidelines)*

* **`README.md`**: This file, explaining the repository contents.

## Slovenske različice dokumentov

Spodaj so povezave do slovenskih prevodov ključnih dokumentov. Prevedeni so bili bistveni deli, povezani s projektom, za lažje razumevanje.

* **[`staticno_porocilo_lana_sl.html`](./staticno_porocilo_lana_sl.html)**: Statično poročilo analize verige LanaCoin.
* **[`analiza-kitov_sl.html`](./analiza-kitov_sl.html)**: Vpliv kitov na kripto trgih z nizkim obsegom.
* **[`lana_decentralizacija_dilema_sl.html`](./lana_decentralizacija_dilema_sl.html)**: Onkraj decentralizacije: argument za financirano upravljanje v projektu Lana.
* **[`grajenje-zaupanja_sl.html`](./grajenje-zaupanja_sl.html)**: Grajenje zaupanja: bistveni elementi spletne strani kriptovalut.

## Using the Interactive Calculator (`lana-cost-calculator.html`)

This HTML file provides a dynamic interface to explore estimated costs for the Lana Project, incorporating a risk/reward model for LANA token payments.

**Editable Inputs:**

* **Current LANA/EUR Rate:** Located at the top, allows you to set the exchange rate used for LANA cost calculations (default: 0.0011).
* **EUR Rate Adjustment (%):** Percentage of the base EUR rate to use for cost calculation (default: 10%). This models scenarios where contributors accept a lower effective EUR rate in exchange for higher potential LANA compensation (e.g., 10% means effective rate is 0.1x base rate).
* **LANA Payment Multiplier:** Adjusts the risk/reward factor for payment in LANA (default: 10). A higher value increases the amount of LANA calculated relative to the (adjusted) EUR cost, compensating for token volatility risk.
* **Base Est. Hourly Rate (€):** Modify the **base** estimated hourly rate in Euros for each specific task row. The EUR Rate Adjustment (%) is applied to this base rate for actual cost calculations.
* **Rough Est. Hours:** Adjust the estimated number of hours required for each specific task row.

**Automatic Outputs:**

* **Calculated Task Cost (€):** Updates automatically. Calculated as: `(Base Est. Hourly Rate (€) * (EUR Rate Adjustment % / 100)) * Rough Est. Hours`.
* **Est. Task Cost (LANA):** Updates automatically based on the calculated (adjusted) EUR cost, the specified LANA/EUR Rate, and the LANA Payment Multiplier.
    * *Calculation:* `Est. Task Cost (LANA) = (Calculated EUR Cost * Multiplier) / Current LANA/EUR Rate`
* **Phase Subtotals:** Automatically calculated sums for hours, adjusted EUR costs, and LANA costs for each project phase.
* **Grand Totals:** Automatically calculated sums for the initial project phases (1-6).

## Project Context

The cost estimations cover various phases of the Lana Project as outlined in the included documentation, including:

* Pre-Launch
* ICO Equivalent
* Development
* Marketing & Promotion
* Community Building
* Launch Phase
* Post-Launch Phase (Ongoing)

## Disclaimer

* The cost estimations provided are based on speculative inputs (especially hours) and specific assumptions regarding rates, adjustments, and multipliers. These are **SAMPLE** values.
* The data is intended for planning and simulation purposes. Actual values require agreement among project personnel.
* The specific project tasks are currently To Be Determined (TBD).
* The project timeline is currently To Be Determined (TBD).

