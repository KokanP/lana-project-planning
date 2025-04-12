import requests
import json
import sys
import os
import time
import base64 # Needed for embedding images
from datetime import datetime
import numpy as np # For calculations

# --- Matplotlib Setup for Non-Interactive Environment ---
import matplotlib
matplotlib.use('Agg') # Use non-interactive backend BEFORE importing pyplot
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker # For formatting axes

# --- Constants ---
API_BASE_URL_GENERAL = "https://chainz.cryptoid.info/lana/api.dws"
API_DELAY = 11
# Filenames for saved plots
PLOT_TOP_N_FILENAME = "top_holders_chart.png"
PLOT_LORENZ_FILENAME = "lorenz_curve.png"
PLOT_HIST_FILENAME = "balance_histogram.png"
# Link for context
CONTEXT_URL = "https://lana.freq.band/whales-analysis.html"

# --- Helper Function for API Calls ---
def get_api_data(base_url, query_params, api_key):
    """ Fetches data using API key from a specified base URL """
    if not api_key:
        print("Error: API Key is required but not provided.", file=sys.stderr)
        return None
    params_with_key = query_params.copy()
    params_with_key['key'] = api_key
    try:
        # print(f"Requesting: {base_url} with params: {params_with_key}") # Optional Debug
        response = requests.get(base_url, params=params_with_key, timeout=30)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type or 'javascript' in content_type:
            text_response = response.text.strip()
            if text_response.endswith(')') and '(' in text_response: # Basic JSONP check
                start = text_response.find('(') + 1
                end = text_response.rfind(')')
                if start < end:
                    text_response = text_response[start:end]
            try:
                return json.loads(text_response)
            except json.JSONDecodeError:
                 print(f"Error: Failed to decode JSON/JSONP response. Response text: {text_response[:200]}...", file=sys.stderr)
                 return None
        else:
             return response.text.strip()
    except requests.exceptions.Timeout:
        print(f"Error: API request timed out for params: {query_params}", file=sys.stderr)
        return None
    except requests.exceptions.HTTPError as http_err:
        print(f"Error: HTTP error occurred: {http_err} for params: {query_params}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as req_err:
        print(f"Error: An ambiguous request error occurred: {req_err} for params: {query_params}", file=sys.stderr)
        return None

# --- Plotting Functions (Save to file) ---
def plot_top_n_chart(holders_data, num_holders_to_plot, filename):
    """Generates and saves a bar chart of top N holders."""
    print(f"\nGenerating Top {num_holders_to_plot} Holders Bar Chart...")
    if not holders_data or len(holders_data) < num_holders_to_plot:
        print(f"Error: Not enough holder data ({len(holders_data)}) to plot top {num_holders_to_plot}.")
        return False
    try:
        top_n_holders = holders_data[:num_holders_to_plot]
        addresses = [f"...{h.get('address', 'Unknown')[-6:]}" for h in top_n_holders]
        balances = [h.get('balance', 0) for h in top_n_holders] # Already in whole coins
        plt.figure(figsize=(12, 6))
        bars = plt.bar(addresses, balances)
        plt.xlabel("Address (Last 6 Chars)")
        plt.ylabel("Balance (LANA)")
        plt.title(f"Top {num_holders_to_plot} LanaCoin Holders by Balance")
        plt.xticks(rotation=45, ha='right')
        plt.ticklabel_format(style='plain', axis='y')
        plt.bar_label(bars, fmt='{:,.0f}', padding=3, rotation=45, size=8)
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        print(f"Successfully saved top holders chart to {filename}")
        return True
    except Exception as e:
        print(f"Error generating top N chart: {e}", file=sys.stderr)
        return False

def plot_lorenz_curve(holders_data, filename):
    """Generates and saves a Lorenz curve plot."""
    print("\nGenerating Lorenz Curve for Wealth Distribution...")
    if not holders_data:
        print("Error: No holder data available for Lorenz curve.")
        return False, None
    try:
        balances_lorenz_coins = np.array([h['balance'] for h in holders_data if isinstance(h.get('balance'), (int, float))])
        balances_lorenz_coins = np.sort(balances_lorenz_coins)
        balances_lorenz_coins = balances_lorenz_coins[balances_lorenz_coins > 0]
        if len(balances_lorenz_coins) == 0:
            print("Error: No valid positive balances found for Lorenz curve.")
            return False, None
        total_balance_coins = balances_lorenz_coins.sum()
        if total_balance_coins == 0:
             print("Error: Total balance is zero, cannot generate Lorenz curve.")
             return False, None
        cum_balance_perc = np.cumsum(balances_lorenz_coins) / total_balance_coins
        num_holders = len(balances_lorenz_coins)
        holders_perc = np.linspace(0., 1., num_holders + 1)[1:]
        holders_axis = np.insert(holders_perc, 0, 0)
        balance_axis = np.insert(cum_balance_perc, 0, 0)
        area_lorenz = np.trapz(balance_axis, holders_axis)
        gini = (0.5 - area_lorenz) / 0.5
        plt.figure(figsize=(7, 7))
        plt.plot(holders_axis, balance_axis, label=f'Lorenz Curve (Gini={gini:.3f})')
        plt.plot([0, 1], [0, 1], label='Perfect Equality', linestyle='--', color='grey')
        plt.xlabel("Cumulative % of Holders")
        plt.ylabel("Cumulative % of Balance Held")
        plt.title(f"LanaCoin Wealth Distribution (Top {len(holders_data)} Holders)")
        plt.legend()
        plt.grid(True, linestyle='--', alpha=0.6)
        plt.axis('equal')
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        print(f"Successfully saved Lorenz curve to {filename}")
        return True, gini
    except Exception as e:
        print(f"Error generating Lorenz curve: {e}", file=sys.stderr)
        return False, None

def plot_balance_histogram(holders_data, filename):
    """Generates and saves a histogram of holder balances."""
    print("\nGenerating Balance Distribution Histogram...")
    if not holders_data:
        print("Error: No holder data available for histogram.")
        return False
    try:
        balances_hist = np.array([h['balance'] for h in holders_data if isinstance(h.get('balance'), (int, float))]) # Already whole coins
        balances_hist = balances_hist[balances_hist > 0]
        if len(balances_hist) == 0:
            print("Error: No valid positive balances found for histogram.")
            return False
        plt.figure(figsize=(10, 6))
        min_log_bal = np.log10(max(balances_hist.min(), 1e-8))
        max_log_bal = np.log10(balances_hist.max())
        if max_log_bal <= min_log_bal: max_log_bal = min_log_bal + 1
        log_bins = np.logspace(min_log_bal, max_log_bal, num=15)
        plt.hist(balances_hist, bins=log_bins, edgecolor='black')
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel("Balance Held (LANA) - Log Scale")
        plt.ylabel("Number of Holders - Log Scale")
        plt.title(f"Distribution of Balances within Top {len(holders_data)} Holders")
        plt.gca().xaxis.set_major_formatter(mticker.ScalarFormatter())
        plt.gca().xaxis.get_major_formatter().set_scientific(False)
        plt.gca().xaxis.get_major_formatter().set_useOffset(False)
        plt.grid(True, which='both', linestyle='--', alpha=0.5)
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        print(f"Successfully saved balance histogram to {filename}")
        return True
    except Exception as e:
        print(f"Error generating balance histogram: {e}", file=sys.stderr)
        return False

# --- Helper Function to Encode Image ---
def image_to_base64(filename):
    """Reads an image file and returns a base64 encoded data URI."""
    try:
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        mime_type = "image/png"
        return f"data:{mime_type};base64,{encoded_string}"
    except FileNotFoundError:
        print(f"Error: Image file not found: {filename}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error encoding image {filename} to base64: {e}", file=sys.stderr)
        return None

# --- Concentration Calculation Function ---
def calculate_and_format_concentration(holders_data, circulating_supply):
    """Calculates and formats Top 10 and Top 100 concentration."""
    print("\nCalculating concentration...")
    conc_10_str = "N/A"
    conc_100_str = "N/A"

    if not holders_data:
        print("Cannot calculate concentration: No parsed holder data.")
        return conc_10_str, conc_100_str
    if circulating_supply is None or not isinstance(circulating_supply, (int, float)) or circulating_supply <= 0:
        print(f"Cannot calculate concentration: Invalid circulating supply ({circulating_supply}).")
        return conc_10_str, conc_100_str

    # Use holders with valid numeric balances (already sorted)
    filtered_holders = [h for h in holders_data if isinstance(h.get('balance'), (int, float))]

    if not filtered_holders:
        print("Cannot calculate concentration: No holders with valid balances found.")
        return conc_10_str, conc_100_str

    try:
        # Calculate sums using whole coin balances
        top_10_balance = sum(h['balance'] for h in filtered_holders[:10])
        top_100_balance = sum(h['balance'] for h in filtered_holders[:100])

        # Calculate directly with whole coin values
        conc_10_val = (top_10_balance / circulating_supply) * 100
        conc_100_val = (top_100_balance / circulating_supply) * 100

        conc_10_str = f"{conc_10_val:.2f}%"
        conc_100_str = f"{conc_100_val:.2f}%"
        print("Calculations complete.")

    except Exception as e:
        print(f"Error during concentration calculation: {e}", file=sys.stderr)
        conc_10_str = "Error (Calc)"
        conc_100_str = "Error (Calc)"

    return conc_10_str, conc_100_str


# --- Main Analysis Logic ---
def run_analysis():
    """ Fetches data, calculates concentration, generates plots, formats HTML report. """
    print("Starting concentration analysis with HTML plotting...")
    api_key = os.environ.get('API_KEY')
    if not api_key:
        print("Error: Environment variable 'API_KEY' not set. Exiting.", file=sys.stderr)
        return None

    # Initialize variables
    circulating_supply = None
    parsed_holders = []
    gini_coefficient = None
    rich_list_snippet_for_log = 'Not Available'

    # --- Fetch Circulating Supply ---
    print(f"Waiting {API_DELAY}s...")
    time.sleep(API_DELAY)
    print("Fetching circulating supply...")
    circulating_supply_data = get_api_data(API_BASE_URL_GENERAL, {'q': 'circulating'}, api_key)
    if circulating_supply_data is not None:
        try:
            circulating_supply = float(circulating_supply_data) # Supply is in whole coins
            print(f"Received circulating supply: {circulating_supply}")
        except ValueError:
            print(f"Error: Could not convert circulating supply data '{circulating_supply_data}' to float.", file=sys.stderr)
    else:
        print("Failed to fetch circulating supply.", file=sys.stderr)

    # --- Fetch Rich List ---
    print(f"Waiting {API_DELAY}s...")
    time.sleep(API_DELAY)
    print("Fetching rich list (top 1000)...")
    rich_list_data = get_api_data(API_BASE_URL_GENERAL, {'q': 'rich'}, api_key)
    if rich_list_data and isinstance(rich_list_data, dict):
        rich_list_snippet_for_log = str(rich_list_data)
        holders_list = rich_list_data.get('rich1000', [])
        if isinstance(holders_list, list):
            print("\nParsing rich list data...")
            temp_holders = []
            for holder_data in holders_list:
                if isinstance(holder_data, dict):
                    try:
                        address = holder_data.get('addr')
                        balance_raw = holder_data.get('amount')
                        if address is not None and balance_raw is not None:
                            balance = float(balance_raw) # Balance is in whole coins
                            temp_holders.append({'address': address, 'balance': balance})
                        else:
                             print(f"Warning: Missing 'addr' or 'amount' in holder data: {holder_data}", file=sys.stderr)
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Could not parse balance for holder data {holder_data}: {e}", file=sys.stderr)
                else:
                     print(f"Warning: Expected dict item in rich1000 list, got {type(holder_data)}", file=sys.stderr)
            parsed_holders = temp_holders
            print(f"Successfully parsed {len(parsed_holders)} entries from rich list.")
            parsed_holders.sort(key=lambda x: x.get('balance', 0), reverse=True)
        else:
            print(f"Error: Expected 'rich1000' key to contain a list.", file=sys.stderr)
    else:
        print("Could not fetch rich list data or data is not a dictionary.", file=sys.stderr)

    # --- Perform Concentration Calculations ---
    concentration_top_10, concentration_top_100 = calculate_and_format_concentration(
        parsed_holders, circulating_supply
    )

    # --- Generate Plots ---
    top_n_plot_success = plot_top_n_chart(parsed_holders, 20, PLOT_TOP_N_FILENAME)
    lorenz_plot_success, gini_coefficient = plot_lorenz_curve(parsed_holders, PLOT_LORENZ_FILENAME)
    # pie_chart_success = plot_pie_chart(parsed_holders, circulating_supply, PLOT_PIE_FILENAME) # Keep removed
    hist_success = plot_balance_histogram(parsed_holders, PLOT_HIST_FILENAME)

    # --- Encode Images to Base64 ---
    print("\nEncoding images for HTML embedding...")
    top_n_base64 = image_to_base64(PLOT_TOP_N_FILENAME) if top_n_plot_success else None
    lorenz_base64 = image_to_base64(PLOT_LORENZ_FILENAME) if lorenz_plot_success else None
    # pie_base64 = image_to_base64(PLOT_PIE_FILENAME) if pie_chart_success else None # Keep removed
    hist_base64 = image_to_base64(PLOT_HIST_FILENAME) if hist_success else None

    # --- Format Output as HTML ---
    print("\nFormatting HTML report...")
    report_time_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    # Define circ_supply_str safely
    circ_supply_str = "N/A"
    if circulating_supply is not None:
        try:
            circ_supply_str = f"{circulating_supply:,.2f}"
        except Exception as e:
            print(f"Error formatting circulating_supply ({circulating_supply}): {e}", file=sys.stderr)
            circ_supply_str = "Error"

    gini_str = f"{gini_coefficient:.3f}" if gini_coefficient is not None else "N/A"

    # Basic CSS for styling + Debug CSS adjustments
    html_style = """
<style>
  body { font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; line-height: 1.6; padding: 20px; max-width: 1000px; margin: auto; background-color: #f9f9f9; color: #333; }
  h1, h2, h3 { color: #1a1a1a; border-bottom: 1px solid #ddd; padding-bottom: 6px; }
  h1 { text-align: center; border-bottom: 2px solid #ccc; margin-bottom: 20px;}
  h2 { margin-top: 40px; }
  h3 { margin-top: 30px; border-bottom: none; }
  ul { padding-left: 20px; list-style: square; }
  li { margin-bottom: 8px; }
  img { max-width: 100%; height: auto; display: block; margin: 15px auto; background-color: white; padding: 5px; border: 1px solid #ccc; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
  table { border-collapse: collapse; width: 100%; margin-top: 15px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 0.9em; }
  th { background-color: #f2f2f2; }
  tr:nth-child(even) { background-color: #f9f9f9; }
  tr:hover { background-color: #f1f1f1; }
  .note { font-size: 0.9em; color: #555; margin-top: 5px; }
  .error { color: #d9534f; font-style: italic; }
  .plot-section { background-color: #fff; padding: 15px; margin-bottom: 30px; border: 1px solid #eee; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
  .interpretation { background-color: #eef; border-left: 4px solid #aac; padding: 10px 15px; margin: 20px 0; font-size: 0.95em; }
  .debug-info { margin-top: 40px; border-top: 2px dashed #ccc; padding-top: 15px; }
  .debug-info summary { cursor: pointer; font-weight: bold; color: #555; margin-top: 10px; font-size: 0.9em; } /* Smaller summary */
  .debug-info pre { background-color: #f0f0f0; padding: 8px; font-size: 0.75em; /* Made font smaller */ overflow-x: auto; border: 1px solid #ddd; border-radius: 4px; }
  hr { border: 0; height: 1px; background: #ddd; margin: 30px 0; }
</style>
"""

    # --- Build Top 10 Table ---
    top_10_table_html = "<h3>Top 10 Holders Table</h3>\n"
    if parsed_holders:
        top_10_table_html += "<table>\n<thead><tr><th>Rank</th><th>Address</th><th>Balance (LANA)</th><th>% of Circulating</th></tr></thead>\n<tbody>\n"
        num_to_show = min(10, len(parsed_holders))
        for i in range(num_to_show):
            holder = parsed_holders[i]
            address = holder.get('address', 'N/A')
            balance_coins = holder.get('balance', 0)
            percent_circ_val = (balance_coins / circulating_supply) * 100 if circulating_supply and circulating_supply > 0 else 0
            percent_circ_str = f"{percent_circ_val:.3f}%"
            display_address = f"{address[:8]}...{address[-6:]}" if len(address) > 14 else address
            top_10_table_html += f"<tr><td>{i+1}</td><td title='{address}'>{display_address}</td><td>{balance_coins:,.2f}</td><td>{percent_circ_str}</td></tr>\n"
        top_10_table_html += "</tbody>\n</table>\n"
    else:
        top_10_table_html += "<p>No holder data parsed to display table.</p>\n"


    # --- Build the entire HTML string ---
    # Prepare conditional image tags
    top_n_img_html = f'<img src="{top_n_base64}" alt="Top 20 Holders Chart">' if top_n_base64 else '<p class="error">Failed to generate Top Holders chart.</p>'
    hist_img_html = f'<img src="{hist_base64}" alt="Balance Histogram">' if hist_base64 else '<p class="error">Failed to generate Balance Histogram.</p>'
    # pie_img_html = ... # Removed
    lorenz_img_html = f'<img src="{lorenz_base64}" alt="Lorenz Curve Chart">' if lorenz_base64 else '<p class="error">Failed to generate Lorenz Curve chart.</p>'
    lorenz_note_html = f'<p class="note">Gini Coefficient: {gini_str} (0 = perfect equality, 1 = perfect inequality)</p>' if lorenz_base64 and gini_str != "N/A" else ''

    # --- Add Interpretive Comments ---
    interpretation_text = f"""
    <h2>Interpretation</h2>
    <div class="interpretation">
        <p>The concentration metrics (Top 10: <strong>{concentration_top_10}</strong>, Top 100: <strong>{concentration_top_100}</strong>) show the percentage of the total circulating supply held by the wealthiest addresses. High percentages indicate that wealth is concentrated in fewer hands, which can potentially lead to increased market volatility or influence by large holders ("whales").</p>
        <p>The Gini coefficient ({gini_str}) derived from the Lorenz curve provides a single measure of inequality. A value closer to 1 signifies higher inequality in balance distribution among the analyzed holders, while a value closer to 0 indicates more equal distribution.</p>
        <p>The histogram visualizes how many addresses fall into different balance ranges (note the logarithmic scale). A distribution heavily skewed towards the right (higher balances) with a long tail also suggests significant wealth concentration.</p>
        <p>Remember, this analysis is based on the top 1000 addresses returned by the API and does not filter out potential exchange or contract addresses. For further context and discussion on LanaCoin whale analysis, see: <a href="{CONTEXT_URL}" target="_blank" rel="noopener noreferrer">{CONTEXT_URL}</a></p>
    </div>
    """

    # --- Add Debug Info Section (Moved to Bottom) ---
    debug_info_html = f"""
    <div class="debug-info">
        <details>
            <summary>Raw Data Snippets (for Debugging)</summary>
            <h3>Rich List Snippet:</h3>
            <pre><code>{rich_list_snippet_for_log[:500]}...</code></pre>
            <p class="note">Full rich list data available via API call q=rich.</p>
        </details>
    </div>
    """


    # --- Construct Final HTML ---
    # Ensure debug info is at the very end before </body>
    html_string = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LanaCoin Whale Analysis Report</title>
    {html_style}
</head>
<body>
    <h1>LanaCoin Whale Analysis Report</h1>
    <p><strong>Data Fetched:</strong> {report_time_utc}</p>
    <p><strong>Circulating Supply:</strong> {circ_supply_str} LANA</p>

    <h2>Top Holder Concentration</h2>
    <p>(Based on Top 1000 from API)</p>
    <ul>
        <li>Top 10 Holders (% of Circulating): <strong>{concentration_top_10}</strong></li>
        <li>Top 100 Holders (% of Circulating): <strong>{concentration_top_100}</strong></li>
    </ul>
    <p class="note">(Note: Concentration based on raw API data. Known exchange/contract addresses are NOT filtered out.)</p>

    {top_10_table_html}

    {interpretation_text}

    <hr>

    <h2>Visualizations</h2>

    <div class="plot-section">
        <h3>Top 20 Holder Balances</h3>
        {top_n_img_html}
    </div>

    <div class="plot-section">
        <h3>Balance Distribution (Top 1000 Holders)</h3>
        {hist_img_html}
    </div>

    <div class="plot-section">
        <h3>Wealth Distribution (Lorenz Curve)</h3>
        {lorenz_img_html}
        {lorenz_note_html}
    </div>

    {debug_info_html}

</body>
</html>
""" # <<< End of the single f-string literal

    print("\n--- Analysis Output ---")
    print(html_string) # Print the generated HTML to stdout
    print("--- End of Output ---")

    # Clean up temporary plot files
    for plot_file in [PLOT_TOP_N_FILENAME, PLOT_LORENZ_FILENAME, PLOT_HIST_FILENAME]: # Pie chart removed
        if os.path.exists(plot_file):
            try:
                os.remove(plot_file)
                print(f"Removed temporary plot file: {plot_file}")
            except OSError as e:
                print(f"Error removing temporary plot file {plot_file}: {e}", file=sys.stderr)


    return True # Indicate success for workflow

# --- Script Execution ---
if __name__ == "__main__":
    success = run_analysis()
    if not success:
        sys.exit(1) # Exit with error if analysis failed

