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

# --- Constants ---
API_BASE_URL_GENERAL = "https://chainz.cryptoid.info/lana/api.dws"
API_DELAY = 11
# Filenames for temporary plot files
PLOT_TOP_N_FILENAME = "top_holders_chart.png"
PLOT_LORENZ_FILENAME = "lorenz_curve.png"

# --- Helper Function for API Calls ---
def get_api_data(base_url, query_params, api_key):
    """ Fetches data using API key from a specified base URL """
    # (Same as in analysis_py_with_plots)
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
    # (Same plotting logic as in analysis_py_with_plots)
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
    # (Same plotting logic as in analysis_py_with_plots)
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

# --- Helper Function to Encode Image ---
def image_to_base64(filename):
    """Reads an image file and returns a base64 encoded data URI."""
    try:
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        # Check file extension for correct MIME type
        mime_type = "image/png" # Default assumption
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
                            balance = float(balance_raw)
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
            concentration_top_10 = f"{(top_10_balance / circulating_supply) * 100:.2f}%"
            concentration_top_100 = f"{(top_100_balance / circulating_supply) * 100:.2f}%"
            print("Calculations complete.")
        else:
            print("No holders available for calculation.")
    else:
        print("Cannot perform calculations: Missing parsed holders or valid circulating supply.")

    # --- Generate Plots ---
    top_n_plot_success = plot_top_n_chart(parsed_holders, 20, PLOT_TOP_N_FILENAME)
    lorenz_plot_success, gini_coefficient = plot_lorenz_curve(parsed_holders, PLOT_LORENZ_FILENAME)

    # --- Encode Images to Base64 ---
    print("\nEncoding images for HTML embedding...")
    top_n_base64 = image_to_base64(PLOT_TOP_N_FILENAME) if top_n_plot_success else None
    lorenz_base64 = image_to_base64(PLOT_LORENZ_FILENAME) if lorenz_plot_success else None

    # --- Format Output as HTML ---
    print("\nFormatting HTML report...")
    report_time_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    circ_supply_str = f"{circulating_supply:,.2f}" if circulating_supply is not None else "N/A"
    gini_str = f"Gini Coefficient: {gini_coefficient:.3f} (0 = perfect equality, 1 = perfect inequality)" if gini_coefficient is not None else ""

    # Basic CSS for styling
    html_style = """
<style>
  body { font-family: sans-serif; line-height: 1.6; padding: 20px; max-width: 900px; margin: auto; }
  h1, h2, h3 { color: #333; }
  h2 { border-bottom: 1px solid #eee; padding-bottom: 5px; margin-top: 30px; }
  h3 { margin-top: 25px; }
  ul { padding-left: 20px; }
  li { margin-bottom: 5px; }
  img { max-width: 100%; height: auto; display: block; margin-top: 10px; border: 1px solid #ddd; }
  .note { font-size: 0.9em; color: #555; }
  .error { color: red; font-style: italic; }
  .plot-section { margin-bottom: 30px; }
</style>
"""

    # Build HTML string
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

    <hr>

    <h2>Visualizations</h2>

    <div class="plot-section">
        <h3>Top 20 Holder Balances</h3>
"""
    if top_n_base64:
        html_string += f'        <img src="{top_n_base64}" alt="Top 20 Holders Chart">\n'
    else:
        html_string += '        <p class="error">Failed to generate Top Holders chart.</p>\n'
    html_string += "    </div>\n" # Close plot-section

    html_string += """
    <div class="plot-section">
        <h3>Wealth Distribution (Lorenz Curve)</h3>
"""
    if lorenz_base64:
        html_string += f'        <img src="{lorenz_base64}" alt="Lorenz Curve Chart">\n'
        if gini_str:
             html_string += f'        <p class="note">{gini_str}</p>\n'
    else:
        html_string += '        <p class="error">Failed to generate Lorenz Curve chart.</p>\n'
    html_string += "    </div>\n" # Close plot-section

    html_string += """
</body>
</html>
"""

    # Print the final HTML string to standard output
    # The workflow will redirect this to an HTML file
    print(html_string)

    return True # Indicate success for workflow

# --- Script Execution ---
if __name__ == "__main__":
    success = run_analysis()
    if not success:
        sys.exit(1) # Exit with error if analysis failed

