import requests
import json
import sys
import os
import time
from datetime import datetime

# print("--- Analysis.py script started execution! ---") # Debug

# --- Constants ---
# Use the main documented API endpoint
API_BASE_URL_GENERAL = "https://chainz.cryptoid.info/lana/api.dws"
# Delay between API calls in seconds (using 11s for safety)
API_DELAY = 11
# Output filename for the transaction data
JSON_OUTPUT_FILENAME = "address_transactions.json"

# --- Helper Function for API Calls ---
# Note: This function now only needs one base URL
def get_api_data(base_url, query_params, api_key):
    """ Fetches data using API key from a specified base URL """
    if not api_key:
        print("Error: API Key is required but not provided.", file=sys.stderr)
        return None
    params_with_key = query_params.copy()
    params_with_key['key'] = api_key
    try:
        # Debug print showing the actual request details (q parameter visible)
        print(f"Requesting: {base_url} with params: {params_with_key}")
        response = requests.get(base_url, params=params_with_key, timeout=30) # Increased timeout
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')
        # multiaddr should return JSON
        if 'application/json' in content_type or 'javascript' in content_type:
            text_response = response.text.strip()
            # Basic check for JSONP wrapper like "callback(...)"
            if text_response.endswith(')') and '(' in text_response:
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
             # Handle plain text for simpler endpoints like 'circulating'
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


# --- Main Analysis Logic ---
def run_analysis():
    """ Runs the main analysis process """
    # print("--- run_analysis() function started ---") # Debug
    api_key = os.environ.get('API_KEY')
    if not api_key:
        print("Error: Environment variable 'API_KEY' not set. Exiting.", file=sys.stderr)
        return None
    # print(f"Using API Key ending with: ...{api_key[-4:]}") # Debug

    # --- Fetch Circulating Supply ---
    time.sleep(API_DELAY)
    circulating_supply_data = get_api_data(API_BASE_URL_GENERAL, {'q': 'circulating'}, api_key)
    circulating_supply = None
    if circulating_supply_data is not None:
        try:
            circulating_supply = float(circulating_supply_data)
        except ValueError:
            print(f"Error: Could not convert circulating supply data '{circulating_supply_data}' to float.", file=sys.stderr)
            return None
    else:
        print("Failed to fetch circulating supply. Cannot continue analysis.", file=sys.stderr)
        return None

    # --- Fetch Rich List ---
    time.sleep(API_DELAY)
    rich_list_data = get_api_data(API_BASE_URL_GENERAL, {'q': 'rich'}, api_key)
    parsed_holders = []
    rich_list_snippet_for_log = 'Not Available'
    if rich_list_data and isinstance(rich_list_data, dict):
        rich_list_snippet_for_log = str(rich_list_data) # Store snippet
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
            # Sort by balance descending
            parsed_holders.sort(key=lambda x: x['balance'], reverse=True)
        else:
            print(f"Error: Expected 'rich1000' key to contain a list.", file=sys.stderr)
    else:
        print("Could not fetch rich list data or data is not a dictionary.", file=sys.stderr)
        return None # Exit if rich list is essential

    # --- Fetch Recent Transactions for Top Addresses (Individually using q=multiaddr) ---
    print(f"\nFetching recent transactions for top addresses individually using q=multiaddr...")
    address_tx_data = {} # Store raw tx data per address
    addresses_with_recent_rewards = [] # Store addresses identified with rewards
    processed_count = 0
    max_addresses_to_check = 100 # <<< KEEPING TEST RUN AT 100

    # Store the first response snippet for debugging
    first_multiaddr_response_snippet = 'Not Available'

    for holder in parsed_holders[:max_addresses_to_check]:
        address_to_check = holder['address']
        print(f"\nProcessing address {processed_count + 1}/{max_addresses_to_check}: {address_to_check}")
        print(f"Waiting {API_DELAY}s...")
        time.sleep(API_DELAY)

        # --- API CALL using q=multiaddr for single address ---
        query_params = {'q': 'multiaddr', 'active': address_to_check}
        tx_data = get_api_data(API_BASE_URL_GENERAL, query_params, api_key)

        if tx_data:
            # Store the raw data returned by the API for this address
            address_tx_data[address_to_check] = tx_data

            # DEBUG: Print structure for the FIRST address ONLY
            if processed_count == 0:
                print(f"\nReceived multiaddr response for first address (type: {type(tx_data)}).")
                print("Multiaddr response snippet (first address):")
                first_multiaddr_response_snippet = str(tx_data) # Capture for report
                print(first_multiaddr_response_snippet[:1500] + ('...' if len(first_multiaddr_response_snippet) > 1500 else ''))
                # --- !!! PARSING LOGIC FOR TRANSACTIONS NEEDED HERE !!! ---
                print("\nParsing multiaddr transaction data (placeholder - needs update based on snippet above)...")
                # TODO: Based on the snippet structure seen in logs, write code here

        else:
            print(f"Warning: Failed to fetch multiaddr data for address {address_to_check}", file=sys.stderr)

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


    # --- Identify Addresses with Recent Rewards ---
    print("\nIdentifying addresses with recent rewards (placeholder)...")
    # TODO: Implement logic here based on parsed transaction data from address_tx_data
    # This parsing would now likely happen in a separate analysis step using the saved JSON file

    # --- Perform Original Concentration Calculations ---
    print("\nCalculating concentration (based on raw rich list)...")
    concentration_top_10 = "Error"
    concentration_top_100 = "Error"
    if parsed_holders and circulating_supply is not None and circulating_supply > 0:
        top_10_balance = sum(h['balance'] for h in parsed_holders[:10])
        top_100_balance = sum(h['balance'] for h in parsed_holders[:100])
        concentration_top_10 = f"{(top_10_balance / circulating_supply) * 100:.2f}%"
        concentration_top_100 = f"{(top_100_balance / circulating_supply) * 100:.2f}%"
    else:
        print("Cannot perform concentration calculations.")


    # --- Format Output ---
    print("\nFormatting results...")
    report_time_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    # --- Build Recent Rewards Output String (Placeholder) ---
    recent_rewards_output = f"### Addresses in Top {max_addresses_to_check} Checked with Recent Reward Activity\n\n"
    if addresses_with_recent_rewards:
       recent_rewards_output += f"Found {len(addresses_with_recent_rewards)} addresses with potential recent rewards:\n\n"
       for addr in addresses_with_recent_rewards: # Maybe limit printed list
            recent_rewards_output += f"- {addr}\n"
    else:
       # Updated message to reflect that analysis happens later
       recent_rewards_output += f"Transaction data for {len(address_tx_data)} addresses saved to {JSON_OUTPUT_FILENAME}. Analysis for reward activity pending.\n"


    # --- Construct the Final Markdown Report ---
    output_string = f"""# LanaCoin Whale Analysis Report

**Data Fetched:** {report_time_utc}

* **Circulating Supply:** {circulating_supply:,.2f} LANA

---

{recent_rewards_output}

---

## Top Holder Concentration (Based on Raw Top 1000 API Data)

* **Top 10 Holders (% of Circulating):** {concentration_top_10}
* **Top 100 Holders (% of Circulating):** {concentration_top_100}

*(Note: Concentration based on raw API data. Known exchange/contract addresses are NOT filtered out.)*

---

## Raw Data Snippets (for Debugging)

**Rich List Snippet:**
```json
{rich_list_snippet_for_log[:500]}...
```

**MultiAddr Response Snippet (First Address Checked Only):**
```json
{first_multiaddr_response_snippet[:500]}...
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

