# Lana Project - Cost Estimation Calculator & Documentation

This repository hosts files related to the planning and cost estimation for the Lana Project.

## Hosted Version

The interactive cost calculator and links to other documents are hosted via GitHub Pages at:

**[`https://KokanP.github.io/lana-project-planning/`](https://KokanP.github.io/lana-project-planning/)**

## Contents

* **[`lana-cost-calculator.html`](https://KokanP.github.io/lana-project-planning/lana-cost-calculator.html)**: The main **interactive** cost estimation tool built with HTML, CSS, and JavaScript. Allows for live calculation updates based on user inputs. *(Direct Link to Calculator)*
* **[`lana_project_cost_sample.html`](https://KokanP.github.io/lana-project-planning/lana_project_cost_sample.html)**: A **static HTML version** of the project documentation containing sample cost estimations based on default parameters (10% EUR Rate Adjustment, 10x LANA Multiplier). *(Direct Link to Static Sample Doc)*
* **[`Building-Trust.html`](https://KokanP.github.io/lana-project-planning/Building-Trust.html)**: Static HTML version of the 'Building Trust: Essential Website Elements for Level 1 Blockchain Cryptocurrencies' guidelines document. *(Direct Link to Trust Guidelines)*
* **[`presentation.html`](https://KokanP.github.io/lana-project-planning/presentation.html)**: A scrollable presentation demo covering the project plan, calculator, sample costs, and next steps. *(Direct Link to Presentation Demo)*
* **`README.md`**: This file, explaining the repository contents.

## Using the Interactive Calculator (`lana-costs-calculator.html`)

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