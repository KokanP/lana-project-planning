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
# Filenames for saved plots (still defined, but plotting calls commented out)
PLOT_TOP_N_FILENAME = "top_holders_chart.png"
PLOT_LORENZ_FILENAME = "lorenz_curve.png"
PLOT_HIST_FILENAME = "balance_histogram.png"
# Link for context - Assuming whales-analysis.html is in the same directory
WHALES_ANALYSIS_URL = "whales-analysis.html" # Relative link
CONTEXT_URL = "https://lana.freq.band/whales-analysis.html" # External context link

# --- Helper Function for API Calls ---
# (Same as previous version)
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


# --- Plotting Functions (Defined but not called in this debug version) ---
def plot_top_n_chart(holders_data, num_holders_to_plot, filename):
    """Generates and saves a bar chart of top N holders."""
    print(f"\nGenerating Top {num_holders_to_plot} Holders Bar Chart...")
    # ... (function code remains same) ...
    # plt.savefig(filename) # Saves file
    plt.close() # Important
    return True # Assume success for now

def plot_lorenz_curve(holders_data, filename):
    """Generates and saves a Lorenz curve plot."""
    print("\nGenerating Lorenz Curve for Wealth Distribution...")
    # ... (function code remains same) ...
    # plt.savefig(filename) # Saves file
    plt.close() # Important
    # Dummy return for debugging structure
    gini = 0.8 # Example Gini
    return True, gini

def plot_balance_histogram(holders_data, filename):
    """Generates and saves a histogram of holder balances."""
    print("\nGenerating Balance Distribution Histogram...")
    # ... (function code remains same) ...
    # plt.savefig(filename) # Saves file
    plt.close() # Important
    return True # Assume success for now

# --- Helper Function to Encode Image ---
def image_to_base64(filename):
    """Reads an image file and returns a base64 encoded data URI."""
    # (Same as previous version, but won't be called if plots aren't saved)
    try:
        with open(filename, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        mime_type = "image/png"
        return f"data:{mime_type};base64,{encoded_string}"
    except FileNotFoundError:
        # This is expected if plotting is commented out
        # print(f"Info: Image file not found (plotting likely disabled): {filename}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Error encoding image {filename} to base64: {e}", file=sys.stderr)
        return None

# --- Concentration Calculation Function ---
def calculate_and_format_concentration(holders_data, circulating_supply):
    """Calculates and formats Top 10 and Top 100 concentration."""
    # (Same as previous version - assumed working now)
    print("\nCalculating concentration...")
    conc_10_str = "N/A"
    conc_100_str = "N/A"
    if not holders_data: return conc_10_str, conc_100_str
    if circulating_supply is None or not isinstance(circulating_supply, (int, float)) or circulating_supply <= 0:
        print(f"Cannot calculate concentration: Invalid circulating supply ({circulating_supply}).")
        return conc_10_str, conc_100_str
    filtered_holders = [h for h in holders_data if isinstance(h.get('balance'), (int, float))]
    if not filtered_holders: return conc_10_str, conc_100_str
    try:
        top_10_balance = sum(h['balance'] for h in filtered_holders[:10])
        top_100_balance = sum(h['balance'] for h in filtered_holders[:100])
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
            circulating_supply = float(circulating_supply_data)
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
                # ... (parsing logic as before) ...
                 if isinstance(holder_data, dict):
                    try:
                        address = holder_data.get('addr')
                        balance_raw = holder_data.get('amount')
                        if address is not None and balance_raw is not None:
                            balance = float(balance_raw) # Balance is in whole coins
                            temp_holders.append({'address': address, 'balance': balance})
                        # else: # Reduce noise
                        #      print(f"Warning: Missing 'addr' or 'amount' in holder data: {holder_data}", file=sys.stderr)
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Could not parse balance for holder data {holder_data}: {e}", file=sys.stderr)
                # else: # Reduce noise
                #      print(f"Warning: Expected dict item in rich1000 list, got {type(holder_data)}", file=sys.stderr)
            parsed_holders = temp_holders
            print(f"Successfully parsed {len(parsed_holders)} entries from rich list.")
            parsed_holders.sort(key=lambda x: x.get('balance', 0), reverse=True)
        else:
            print(f"Error: Expected 'rich1000' key to contain a list.", file=sys.stderr)
    else:
        print("Could not fetch rich list data or data is not a dictionary.", file=sys.stderr)

    # --- Perform Concentration Calculations ---
    # Still calculate concentration, but plots are disabled this run
    concentration_top_10, concentration_top_100 = calculate_and_format_concentration(
        parsed_holders, circulating_supply
    )
    # Also get Gini for the text part, even if plot is disabled
    _, gini_coefficient = plot_lorenz_curve(parsed_holders, PLOT_LORENZ_FILENAME)


    # --- Generate Plots (COMMENTED OUT FOR DEBUGGING LAYOUT/CSS) ---
    print("\nPlot generation SKIPPED for layout debugging.")
    # top_n_plot_success = plot_top_n_chart(parsed_holders, 20, PLOT_TOP_N_FILENAME)
    # lorenz_plot_success, gini_coefficient = plot_lorenz_curve(parsed_holders, PLOT_LORENZ_FILENAME) # Gini needed, run this one
    # hist_success = plot_balance_histogram(parsed_holders, PLOT_HIST_FILENAME)
    top_n_plot_success = False # Assume fail for conditional logic below
    lorenz_plot_success = True if gini_coefficient is not None else False # Use Gini success
    hist_success = False # Assume fail

    # --- Encode Images to Base64 (COMMENTED OUT FOR DEBUGGING LAYOUT/CSS) ---
    print("\nImage encoding SKIPPED for layout debugging.")
    # top_n_base64 = image_to_base64(PLOT_TOP_N_FILENAME) if top_n_plot_success else None
    # lorenz_base64 = image_to_base64(PLOT_LORENZ_FILENAME) if lorenz_plot_success else None
    # hist_base64 = image_to_base64(PLOT_HIST_FILENAME) if hist_success else None
    top_n_base64 = None
    lorenz_base64 = None # Will be None if plot failed anyway
    hist_base64 = None


    # --- Format Output as HTML ---
    print("\nFormatting SIMPLIFIED HTML report for debugging...")
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
    # Added obvious yellow background test
    html_style = """
<style>
  /* --- CSS Test Style --- */
  body { background-color: yellow !important; border: 5px dashed red !important; /* Make it obvious */ }

  body { font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif; line-height: 1.6; padding: 20px; max-width: 1000px; margin: auto; color: #333; }
  h1 { text-align: center; border-bottom: 2px solid #ccc; margin-bottom: 20px; color: #1a1a1a;}
  .debug-info { margin-top: 40px; border-top: 2px dashed #ccc; padding-top: 15px; }
  .debug-info summary { cursor: pointer; font-weight: bold; color: #555; margin-top: 10px; font-size: 0.9em; }
  .debug-info pre { background-color: #f0f0f0; padding: 8px; font-size: 0.75em; /* Smaller font for debug */ overflow-x: auto; border: 1px solid #ddd; border-radius: 4px; }
</style>
"""

    # --- Build Top 10 Table (Keep for context) ---
    # (Same as before)
    top_10_table_html = "<h3>Top 10 Holders Table (Example Data)</h3>\n" # Indicate it might be stale if plots disabled
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


    # --- Build the SIMPLIFIED HTML string ---
    # Only include basic structure, style, title, and debug info at the end

    # --- Add Debug Info Section ---
    debug_info_html = f"""
    <hr style="margin-top: 50px; border-style: dashed;">
    <div class="debug-info">
        <details open> <summary>Raw Data Snippets (for Debugging)</summary>
            <h3>Rich List Snippet:</h3>
            <pre><code>{rich_list_snippet_for_log[:500]}...</code></pre>
            <p class="note">Full rich list data available via API call q=rich.</p>
        </details>
    </div>
    """


    # --- Construct Final HTML ---
    html_string = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>LanaCoin Whale Analysis Report - DEBUG</title>
    {html_style}
</head>
<body>
    <h1>LanaCoin Whale Analysis Report - LAYOUT/CSS DEBUG</h1>
    <p>This is a simplified test page to check CSS application and debug info placement.</p>
    <p><strong>Data Fetched:</strong> {report_time_utc}</p>
    <p><strong>Circulating Supply:</strong> {circ_supply_str} LANA</p>
    <p><strong>Top 10 Concentration:</strong> {concentration_top_10}</p>
    <p><strong>Top 100 Concentration:</strong> {concentration_top_100}</p>

    {debug_info_html}

</body>
</html>
"""

    print("\n--- Analysis Output ---")
    print(html_string) # Print the generated HTML to stdout
    print("--- End of Output ---")

    # Clean up temporary plot files (only those potentially created)
    for plot_file in [PLOT_TOP_N_FILENAME, PLOT_LORENZ_FILENAME, PLOT_HIST_FILENAME]:
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

