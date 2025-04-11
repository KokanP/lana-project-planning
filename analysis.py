import requests
import json
import sys
import os
import time
from datetime import datetime

# print("--- Analysis.py script started execution! ---") # Debug

# --- Constants ---
# API base URL for LanaCoin on Chainz Cryptoid
API_BASE_URL = "https://chainz.cryptoid.info/lana/api.dws"
# Delay between API calls in seconds to respect rate limit (1 call / 10s)
API_DELAY = 10

# --- Helper Function for API Calls ---
def get_api_data(query_params, api_key):
    """
    Fetches data from the Cryptoid API for the given query parameters,
    requiring an API key passed as the 'key' query parameter.

    Args:
        query_params (dict): A dictionary of query parameters (e.g., {'q': 'circulating'}).
        api_key (str): The API key.

    Returns:
        dict or list or str or None: Parsed JSON data, raw text if not JSON, or None if the request fails.
    """
    if not api_key:
        print("Error: API Key is required but not provided.", file=sys.stderr)
        return None

    params_with_key = query_params.copy()
    params_with_key['key'] = api_key

    try:
        # print(f"Requesting: {API_BASE_URL} with params: {query_params}") # Debug
        response = requests.get(API_BASE_URL, params=params_with_key, timeout=15)
        response.raise_for_status()

        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return response.json()
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
    except json.JSONDecodeError:
        print(f"Error: Failed to decode JSON response for params: {query_params}. Response text: {response.text[:200]}...", file=sys.stderr)
        return None


# --- Main Analysis Logic ---
def run_analysis():
    """
    Runs the main analysis process: fetches data, analyzes, formats output.
    """
    # print("--- run_analysis() function started ---") # Debug

    api_key = os.environ.get('API_KEY')
    if not api_key:
        print("Error: Environment variable 'API_KEY' not set. Exiting.", file=sys.stderr)
        return None

    # print(f"Using API Key ending with: ...{api_key[-4:]}") # Debug

    # --- Make API calls ---
    # print(f"Waiting {API_DELAY}s before first API call...") # Debug
    time.sleep(API_DELAY)
    # print("Fetching circulating supply...") # Debug
    circulating_supply_data = get_api_data({'q': 'circulating'}, api_key)
    circulating_supply = None
    if circulating_supply_data is not None:
        try:
            circulating_supply = float(circulating_supply_data)
            # print(f"Received circulating supply: {circulating_supply}") # Debug
        except ValueError:
            print(f"Error: Could not convert circulating supply data '{circulating_supply_data}' to float.", file=sys.stderr)
            return None
    else:
        print("Failed to fetch circulating supply. Cannot continue analysis.", file=sys.stderr)
        return None

    # print(f"Waiting {API_DELAY}s...") # Debug
    time.sleep(API_DELAY)
    # print("Fetching rich list (top 1000)...") # Debug
    rich_list_data = get_api_data({'q': 'rich'}, api_key)

    # Initialize variables
    parsed_holders = []
    concentration_top_10 = "Error" # Default to Error
    concentration_top_100 = "Error"
    rich_list_snippet_for_log = 'Not Available'

    if rich_list_data and isinstance(rich_list_data, dict):
        # print(f"Received rich list data (type: {type(rich_list_data)}).") # Debug
        rich_list_snippet_for_log = str(rich_list_data) # Store snippet before processing

        # --- PARSE RICH LIST DATA ---
        print("\nParsing rich list data...")
        # Access the list of holders safely using .get()
        holders_list = rich_list_data.get('rich1000', [])

        if isinstance(holders_list, list):
            for holder_data in holders_list:
                if isinstance(holder_data, dict):
                    try:
                        address = holder_data.get('addr')
                        # Amount might be string or number, handle conversion
                        balance_raw = holder_data.get('amount')
                        if address is not None and balance_raw is not None:
                            balance = float(balance_raw)
                            parsed_holders.append({'address': address, 'balance': balance})
                        else:
                             print(f"Warning: Missing 'addr' or 'amount' in holder data: {holder_data}", file=sys.stderr)
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Could not parse balance for holder data {holder_data}: {e}", file=sys.stderr)
                else:
                    print(f"Warning: Expected dict item in rich1000 list, got {type(holder_data)}", file=sys.stderr)
            print(f"Successfully parsed {len(parsed_holders)} entries from rich list.")
        else:
            print(f"Error: Expected 'rich1000' key to contain a list, but got {type(holders_list)}.", file=sys.stderr)

        # --- PERFORM CALCULATIONS ---
        print("\nCalculating concentration...")
        if parsed_holders and circulating_supply is not None and circulating_supply > 0:
            # TODO: Implement filtering of exchange/contract addresses if needed
            # For now, use the raw parsed list. API likely returns sorted.
            # filtered_holders = [h for h in parsed_holders if h['address'] not in KNOWN_EXCHANGES]
            filtered_holders = parsed_holders # Using raw list for now

            if filtered_holders:
                # Ensure sorted by balance descending (API probably does this, but safer to ensure)
                filtered_holders.sort(key=lambda x: x['balance'], reverse=True)

                # Calculate sums for top N
                top_10_balance = sum(h['balance'] for h in filtered_holders[:10])
                top_100_balance = sum(h['balance'] for h in filtered_holders[:100])

                # Calculate percentages
                concentration_top_10 = f"{(top_10_balance / circulating_supply) * 100:.2f}%"
                concentration_top_100 = f"{(top_100_balance / circulating_supply) * 100:.2f}%"
                print("Calculations complete.")
            else:
                print("No holders left after filtering (or filtering not implemented).")
                concentration_top_10 = "N/A (No Holders)"
                concentration_top_100 = "N/A (No Holders)"
        else:
            print("Cannot perform calculations: Missing parsed holders or valid circulating supply.")
            concentration_top_10 = "Error (Missing Data)"
            concentration_top_100 = "Error (Missing Data)"

    else:
        print("Could not fetch rich list data or data is not a dictionary.", file=sys.stderr)
        # Keep default 'Error'/'Not Available' values

    # --- Format Output ---
    print("\nFormatting results...")
    report_time_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    output_string = f"""# LanaCoin Whale Analysis Report

**Data Fetched:** {report_time_utc}

* **Circulating Supply:** {circulating_supply:,.2f} LANA *(Used for calculations)*

## Top Holder Concentration (Based on Top 1000 from API)

* **Top 10 Holders (% of Circulating):** {concentration_top_10}
* **Top 100 Holders (% of Circulating):** {concentration_top_100}

*(Note: Based on raw API data. Known exchange/contract addresses are NOT filtered out in this version.)*

## Raw Rich List Data Snippet (for Debugging)

```json
{rich_list_snippet_for_log[:500]}...
```

*End of Report*
"""
    print("\n--- Analysis Output ---")
    print(output_string)
    print("--- End of Output ---")

    return output_string

# --- Script Execution ---
if __name__ == "__main__":
    # print("--- Script __main__ block started ---") # Debug
    # print("--- About to call run_analysis() ---") # Debug
    analysis_result_string = run_analysis()
    # if analysis_result_string: # Debug
    #     print("--- run_analysis() completed successfully ---") # Debug
    # else: # Debug
    #     print("--- run_analysis() did not complete successfully or returned None ---") # Debug

    # print("--- Analysis.py script finished execution! ---") # Debug
