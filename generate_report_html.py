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
PLOT_PIE_FILENAME = "concentration_pie_chart.png"
PLOT_HIST_FILENAME = "balance_histogram.png"

# --- Helper Function for API Calls ---
def get_api_data(base_url, query_params, api_key):
    """ Fetches data using API key from a specified base URL """
    # (Same as previous version)
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
    # (Same as previous version)
    print(f"\nGenerating Top {num_holders_to_plot} Holders Bar Chart...")
    if not holders_data or len(holders_data) < num_holders_to_plot:
        print(f"Error: Not enough holder data ({len(holders_data)}) to plot top {num_holders_to_plot}.")
        return False
    try:
        top_n_holders = holders_data[:num_holders_to_plot]
        addresses = [f"...{h.get('address', 'Unknown')[-6:]}" for h in top_n_holders]
        balances = [float(h.get('balance', 0)) / 1e8 for h in top_n_holders]
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
    # (Same as previous version)
    print("\nGenerating Lorenz Curve for Wealth Distribution...")
    if not holders_data:
        print("Error: No holder data available for Lorenz curve.")
        return False, None
    try:
        balances_lorenz = np.array([float(h['balance']) / 1e8 for h in holders_data if isinstance(h.get('balance'), (int, float))])
        balances_lorenz = np.sort(balances_lorenz)
        balances_lorenz = balances_lorenz[balances_lorenz > 0]
        if len(balances_lorenz) == 0:
            print("Error: No valid positive balances found for Lorenz curve.")
            return False, None
        total_balance = balances_lorenz.sum()
        if total_balance == 0:
             print("Error: Total balance is zero, cannot generate Lorenz curve.")
             return False, None
        cum_balance_perc = np.cumsum(balances_lorenz) / total_balance
        num_holders = len(balances_lorenz)
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

# --- NEW Plotting Function: Pie Chart ---
def plot_pie_chart(holders_data, circulating_supply, filename):
    """Generates and saves a pie chart showing concentration."""
    # (Same as previous version)
    print("\nGenerating Concentration Pie Chart...")
    if not holders_data or circulating_supply is None or circulating_supply <= 0:
        print("Error: Insufficient data for pie chart.")
        return False
    try:
        bal_top_10 = sum(float(h.get('balance', 0)) for h in holders_data[:10])
        bal_11_100 = sum(float(h.get('balance', 0)) for h in holders_data[10:100])
        bal_101_1000 = sum(float(h.get('balance', 0)) for h in holders_data[100:])
        total_top_1000_bal = bal_top_10 + bal_11_100 + bal_101_1000
        bal_remainder = (circulating_supply * 1e8) - total_top_1000_bal
        bal_remainder = max(0, bal_remainder)
        sizes = [bal_top_10 / 1e8, bal_11_100 / 1e8, bal_101_1000 / 1e8, bal_remainder / 1e8]
        labels = [
            f'Top 10 ({bal_top_10 / (circulating_supply * 1e8):.1%})',
            f'Next 90 (11-100) ({bal_11_100 / (circulating_supply * 1e8):.1%})',
            f'Next 900 (101-1000) ({bal_101_1000 / (circulating_supply * 1e8):.1%})',
            f'Remainder ({bal_remainder / (circulating_supply * 1e8):.1%})'
        ]
        non_zero_sizes = [size for size in sizes if size > 0.001 * circulating_supply]
        non_zero_labels = [labels[i] for i, size in enumerate(sizes) if size > 0.001 * circulating_supply]
        if not non_zero_sizes:
             print("Error: No significant slices found for pie chart.")
             return False
        plt.figure(figsize=(8, 8))
        plt.pie(non_zero_sizes, labels=non_zero_labels, autopct='%1.1f%%', startangle=90, pctdistance=0.85)
        plt.title('LanaCoin Balance Concentration by Holder Group')
        plt.tight_layout()
        plt.savefig(filename)
        plt.close()
        print(f"Successfully saved pie chart to {filename}")
        return True
    except Exception as e:
        print(f"Error generating pie chart: {e}", file=sys.stderr)
        return False

# --- NEW Plotting Function: Histogram ---
def plot_balance_histogram(holders_data, filename):
    """Generates and saves a histogram of holder balances."""
    # (Same as previous version)
    print("\nGenerating Balance Distribution Histogram...")
    if not holders_data:
        print("Error: No holder data available for histogram.")
        return False
    try:
        balances_hist = np.array([float(h.get('balance', 0)) / 1e8 for h in holders_data if isinstance(h.get('balance'), (int, float))])
        balances_hist = balances_hist[balances_hist > 0]
        if len(balances_hist) == 0:
            print("Error: No valid positive balances found for histogram.")
            return False
        plt.figure(figsize=(10, 6))
        min_log_bal = np.log10(balances_hist.min())
        max_log_bal = np.log10(balances_hist.max())
        # Ensure max > min before creating bins
        if max_log_bal <= min_log_bal:
            max_log_bal = min_log_bal + 1 # Add a small range if all values are the same
        log_bins = np.logspace(min_log_bal, max_log_bal, num=15)
        plt.hist(balances_hist, bins=log_bins, edgecolor='black')
        plt.xscale('log')
        plt.yscale('log')
        plt.xlabel("Balance Held (LANA) - Log Scale")
        plt.ylabel("Number of Holders - Log Scale")
        plt.title(f"Distribution of Balances within Top {len(holders_data)} Holders")
        plt.gca().xaxis.set_major_formatter(mticker.FormatStrFormatter('%d'))
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
    # (Same as previous version)
    try:
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        mime_type = "image/png"
        if filename.lower().endswith(".jpg") or filename.lower().endswith(".jpeg"):
            mime_type = "image/jpeg"
        elif filename.lower().endswith(".gif"):
             mime_type = "image/gif"
        elif filename.lower().endswith(".svg"):
             mime_type = "image/svg+xml"
        return f"data:{mime_type};base64,{encoded_string}"
    except FileNotFoundError:
        print(f"Error: Image file not found: {filename}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error encoding image {filename} to base64: {e}", file=sys.stderr)
        return None

# --- Main Analysis Logic ---
def run_analysis():
    """ Fetches data, calculates concentration, generates plots, formats HTML report. """
    print("Starting concentration analysis with HTML plotting...")
    api_key = os.environ.get('API_KEY')
    if not api_key:
        print("Error: Environment variable 'API_KEY' not set. Exiting.", file=sys.stderr)
        return None

    # --- Fetch Circulating Supply ---
    print(f"Waiting {API_DELAY}s...")
    time.sleep(API_DELAY)
    print("Fetching circulating supply...")
    circulating_supply_data = get_api_data(API_BASE_URL_GENERAL, {'q': 'circulating'}, api_key)
    circulating_supply = None
    if circulating_supply_data is not None:
        try:
            circulating_supply = float(circulating_supply_data)
            print(f"Received circulating supply: {circulating_supply}")
        except ValueError:
            print(f"Error: Could not convert circulating supply data '{circulating_supply_data}' to float.", file=sys.stderr)
            return None
    else:
        print("Failed to fetch circulating supply.", file=sys.stderr)
        return None

    # --- Fetch Rich List ---
    print(f"Waiting {API_DELAY}s...")
    time.sleep(API_DELAY)
    print("Fetching rich list (top 1000)...")
    rich_list_data = get_api_data(API_BASE_URL_GENERAL, {'q': 'rich'}, api_key)
    parsed_holders = []
    if rich_list_data and isinstance(rich_list_data, dict):
        holders_list = rich_list_data.get('rich1000', [])
        if isinstance(holders_list, list):
            print("\nParsing rich list data...")
            for holder_data in holders_list:
                if isinstance(holder_data, dict):
                    try:
                        address = holder_data.get('addr')
                        balance_raw = holder_data.get('amount')
                        if address is not None and balance_raw is not None:
                            balance = float(balance_raw) # Keep balance in base units
                            parsed_holders.append({'address': address, 'balance': balance})
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Could not parse balance for holder data {holder_data}: {e}", file=sys.stderr)
            print(f"Successfully parsed {len(parsed_holders)} entries from rich list.")
            parsed_holders.sort(key=lambda x: x['balance'], reverse=True)
        else:
            print(f"Error: Expected 'rich1000' key to contain a list.", file=sys.stderr)
    else:
        print("Could not fetch rich list data or data is not a dictionary.", file=sys.stderr)

    # --- Perform Concentration Calculations ---
    print("\nCalculating concentration...")
    concentration_top_10 = "N/A"
    concentration_top_100 = "N/A"
    if parsed_holders and circulating_supply is not None and circulating_supply > 0:
        filtered_holders = parsed_holders
        if filtered_holders:
            top_10_balance = sum(h['balance'] for h in filtered_holders[:10])
            top_100_balance = sum(h['balance'] for h in filtered_holders[:100])
            concentration_top_10 = f"{(top_10_balance / (circulating_supply * 1e8)) * 100:.2f}%"
            concentration_top_100 = f"{(top_100_balance / (circulating_supply * 1e8)) * 100:.2f}%"
            print("Calculations complete.")
        else:
            print("No holders available for calculation.")
    else:
        print("Cannot perform calculations: Missing parsed holders or valid circulating supply.")

    # --- Generate Plots ---
    top_n_plot_success = plot_top_n_chart(parsed_holders, 20, PLOT_TOP_N_FILENAME)
    lorenz_plot_success, gini_coefficient = plot_lorenz_curve(parsed_holders, PLOT_LORENZ_FILENAME)
    pie_chart_success = plot_pie_chart(parsed_holders, circulating_supply, PLOT_PIE_FILENAME)
    hist_success = plot_balance_histogram(parsed_holders, PLOT_HIST_FILENAME)

    # --- Encode Images to Base64 ---
    print("\nEncoding images for HTML embedding...")
    top_n_base64 = image_to_base64(PLOT_TOP_N_FILENAME) if top_n_plot_success else None
    lorenz_base64 = image_to_base64(PLOT_LORENZ_FILENAME) if lorenz_plot_success else None
    pie_base64 = image_to_base64(PLOT_PIE_FILENAME) if pie_chart_success else None
    hist_base64 = image_to_base64(PLOT_HIST_FILENAME) if hist_success else None

    # --- Format Output as HTML ---
    print("\nFormatting HTML report...")
    report_time_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    circ_supply_str = f"{circulating_supply:,.2f}" if circulating_supply is not None else "N/A"
    gini_str = f"Gini Coefficient: {gini_coefficient:.3f} (0 = perfect equality, 1 = perfect inequality)" if gini_coefficient is not None else ""

    # Basic CSS for styling
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
  th, td { border: 1px solid #ddd; padding: 8px; text-align: left; font-size: 0.9em; } /* Smaller font for table */
  th { background-color: #f2f2f2; }
  tr:nth-child(even) { background-color: #f9f9f9; }
  tr:hover { background-color: #f1f1f1; }
  .note { font-size: 0.9em; color: #555; margin-top: 5px; }
  .error { color: #d9534f; font-style: italic; }
  .plot-section { background-color: #fff; padding: 15px; margin-bottom: 30px; border: 1px solid #eee; border-radius: 5px; box-shadow: 0 1px 3px rgba(0,0,0,0.05); }
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
            balance_base = holder.get('balance', 0)
            balance_lana = balance_base / 1e8
            percent_circ = (balance_base / (circulating_supply * 1e8)) * 100 if circulating_supply and circulating_supply > 0 else 0
            # Shorten address for display in table
            display_address = f"{address[:8]}...{address[-6:]}" if len(address) > 14 else address
            top_10_table_html += f"<tr><td>{i+1}</td><td title='{address}'>{display_address}</td><td>{balance_lana:,.2f}</td><td>{percent_circ:.3f}%</td></tr>\n"
        top_10_table_html += "</tbody>\n</table>\n"
    else:
        top_10_table_html += "<p>No holder data parsed to display table.</p>\n"


    # --- Build the entire HTML string using ONE f-string literal ---
    # Prepare conditional image tags
    top_n_img_html = f'<img src="{top_n_base64}" alt="Top 20 Holders Chart">' if top_n_base64 else '<p class="error">Failed to generate Top Holders chart.</p>'
    hist_img_html = f'<img src="{hist_base64}" alt="Balance Histogram">' if hist_base64 else '<p class="error">Failed to generate Balance Histogram.</p>'
    pie_img_html = f'<img src="{pie_base64}" alt="Concentration Pie Chart">' if pie_base64 else '<p class="error">Failed to generate Concentration Pie Chart.</p>'
    lorenz_img_html = f'<img src="{lorenz_base64}" alt="Lorenz Curve Chart">' if lorenz_base64 else '<p class="error">Failed to generate Lorenz Curve chart.</p>'
    lorenz_note_html = f'<p class="note">{gini_str}</p>' if lorenz_base64 and gini_str else ''


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
        <h3>Wealth Concentration (Pie Chart)</h3>
        {pie_img_html}
    </div>

    <div class="plot-section">
        <h3>Wealth Distribution (Lorenz Curve)</h3>
        {lorenz_img_html}
        {lorenz_note_html}
    </div>

</body>
</html>
""" # <<< End of the single f-string literal

    print("\n--- Analysis Output ---")
    print(html_string) # Print the generated HTML to stdout
    print("--- End of Output ---")

    # Clean up temporary plot files
    for plot_file in [PLOT_TOP_N_FILENAME, PLOT_LORENZ_FILENAME, PLOT_PIE_FILENAME, PLOT_HIST_FILENAME]:
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

