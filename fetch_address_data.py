import requests
import json
import sys
import os
import time
from datetime import datetime

# --- Constants ---
# Use the main documented API endpoint
API_BASE_URL_GENERAL = "https://chainz.cryptoid.info/lana/api.dws"
# Delay between API calls in seconds (using 11s for safety)
API_DELAY = 11
# Output filename for the transaction data
JSON_OUTPUT_FILENAME = "address_transactions.json"
# Set to None or 1000 to run for all, or a smaller number for testing
MAX_ADDRESSES_TO_CHECK = 1000 # Set to None or 1000 for full run

# --- Helper Function for API Calls ---
def get_api_data(base_url, query_params, api_key):
    """ Fetches data using API key from a specified base URL """
    if not api_key:
        print("Error: API Key is required but not provided.", file=sys.stderr)
        return None
    params_with_key = query_params.copy()
    params_with_key['key'] = api_key
    try:
        print(f"Requesting: {base_url} with params: {query_params}") # Log the request
        response = requests.get(base_url, params=params_with_key, timeout=45) # Increased timeout further
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

# --- Main Data Fetching Logic ---
def run_data_fetch():
    """
    Fetches rich list and then fetches transaction details for each address
    using q=multiaddr, saving the results to a JSON file.
    Outputs a simple status report to stdout.
    """
    print("Starting full address data fetch...")
    api_key = os.environ.get('API_KEY')
    if not api_key:
        print("Error: Environment variable 'API_KEY' not set. Exiting.", file=sys.stderr)
        return None
    print(f"Using API Key ending with: ...{api_key[-4:]}")

    # --- Fetch Rich List ---
    print(f"Waiting {API_DELAY}s...")
    time.sleep(API_DELAY)
    print("Fetching rich list (top 1000)...")
    rich_list_data = get_api_data(API_BASE_URL_GENERAL, {'q': 'rich'}, api_key)
    parsed_holders = []
    if rich_list_data and isinstance(rich_list_data, dict):
        holders_list = rich_list_data.get('rich1000', [])
        if isinstance(holders_list, list):
            print("Parsing rich list data...")
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
            return None # Cannot proceed without rich list
    else:
        print("Could not fetch rich list data or data is not a dictionary.", file=sys.stderr)
        return None

    # Determine addresses to check
    addresses_to_process = parsed_holders
    if MAX_ADDRESSES_TO_CHECK is not None and MAX_ADDRESSES_TO_CHECK < len(parsed_holders):
        addresses_to_process = parsed_holders[:MAX_ADDRESSES_TO_CHECK]
    total_to_check = len(addresses_to_process)
    print(f"\nFetching recent transactions for {total_to_check} addresses individually using q=multiaddr...")
    print(f"Estimated minimum runtime: {total_to_check * API_DELAY / 60:.1f} minutes.")

    # --- Fetch Recent Transactions (Individually using q=multiaddr) ---
    address_tx_data = {} # Store raw tx data per address
    processed_count = 0

    for holder in addresses_to_process:
        address_to_check = holder['address']
        print(f"\nProcessing address {processed_count + 1}/{total_to_check}: {address_to_check}")
        print(f"Waiting {API_DELAY}s...")
        time.sleep(API_DELAY)

        query_params = {'q': 'multiaddr', 'active': address_to_check}
        # Optional: Get more/fewer transactions using 'n', e.g., query_params['n'] = 50
        tx_data = get_api_data(API_BASE_URL_GENERAL, query_params, api_key)

        if tx_data:
            # Store the raw data returned by the API for this address
            address_tx_data[address_to_check] = tx_data
            print(f"Successfully fetched data for {address_to_check}")
        else:
            print(f"Warning: Failed to fetch multiaddr data for address {address_to_check}", file=sys.stderr)
            # Store failure indication? Or just skip? Let's skip for now.
            address_tx_data[address_to_check] = {"error": "Failed to fetch data"}

        processed_count += 1

    print(f"\nFinished fetching transaction data for {processed_count} addresses.")

    # --- Save Collected Transaction Data ---
    print(f"\nSaving transaction data for {len(address_tx_data)} addresses to {JSON_OUTPUT_FILENAME}...")
    try:
        with open(JSON_OUTPUT_FILENAME, 'w') as f:
            json.dump(address_tx_data, f, indent=4)
        print(f"Successfully saved data to {JSON_OUTPUT_FILENAME}")
    except IOError as e:
        print(f"Error: Failed to save data to {JSON_OUTPUT_FILENAME}: {e}", file=sys.stderr)
    except TypeError as e:
         print(f"Error: Failed to serialize data to JSON: {e}", file=sys.stderr)

    # --- Format Simple Status Report Output ---
    print("\nFormatting status report...")
    report_time_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')
    output_string = f"""# LanaCoin Address Data Fetch Report

**Run Completed:** {report_time_utc}

* **Addresses Processed:** {processed_count} / {total_to_check}
* **Data Saved To:** `{JSON_OUTPUT_FILENAME}` (Contains raw responses from `q=multiaddr` for each processed address)

*Note: Detailed analysis (e.g., for reward transactions) needs to be performed separately on the saved JSON data.*

*End of Report*
"""
    print("\n--- Status Report Output ---")
    print(output_string)
    print("--- End of Output ---")

    return output_string

# --- Script Execution ---
if __name__ == "__main__":
    status_report = run_data_fetch()
    if not status_report:
        sys.exit(1) # Exit with error if fetch failed early

