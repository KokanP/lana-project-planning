import requests
import json
import sys
import os
import time
from datetime import datetime

# print("--- Analysis.py script started execution! ---") # Debug

# --- Constants ---
API_BASE_URL = "https://chainz.cryptoid.info/lana/api.dws"
API_DELAY = 10 # Delay between API calls in seconds
MULTIADDR_BATCH_SIZE = 20 # Number of addresses per multiaddr call

# --- Helper Function for API Calls ---
def get_api_data(query_params, api_key):
    """ Fetches data using API key """
    if not api_key:
        print("Error: API Key is required but not provided.", file=sys.stderr)
        return None
    params_with_key = query_params.copy()
    params_with_key['key'] = api_key
    try:
        # print(f"Requesting: {API_BASE_URL} with params: {query_params}") # Debug
        # Use POST for multiaddr if the address list gets long? Docs say GET, but sometimes POST is needed. Stick to GET for now.
        response = requests.get(API_BASE_URL, params=params_with_key, timeout=30) # Increased timeout for potentially larger request
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
    """ Runs the main analysis process """
    # print("--- run_analysis() function started ---") # Debug
    api_key = os.environ.get('API_KEY')
    if not api_key:
        print("Error: Environment variable 'API_KEY' not set. Exiting.", file=sys.stderr)
        return None
    # print(f"Using API Key ending with: ...{api_key[-4:]}") # Debug

    # --- Fetch Circulating Supply ---
    time.sleep(API_DELAY)
    circulating_supply_data = get_api_data({'q': 'circulating'}, api_key)
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
    rich_list_data = get_api_data({'q': 'rich'}, api_key)
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
        else:
            print(f"Error: Expected 'rich1000' key to contain a list.", file=sys.stderr)
    else:
        print("Could not fetch rich list data or data is not a dictionary.", file=sys.stderr)
        return None # Exit if rich list is essential

    # --- Fetch Recent Transactions for Rich List (Batched) ---
    print(f"\nFetching recent transactions for {len(parsed_holders)} rich list addresses (in batches of {MULTIADDR_BATCH_SIZE})...")
    all_multiaddr_data = {} # Store data per address
    processed_batches = 0
    # Sort holders by balance just in case, process top ones first if needed
    parsed_holders.sort(key=lambda x: x['balance'], reverse=True)

    for i in range(0, len(parsed_holders), MULTIADDR_BATCH_SIZE):
        batch = parsed_holders[i:i + MULTIADDR_BATCH_SIZE]
        if not batch:
            continue

        batch_addresses = [holder['address'] for holder in batch]
        address_param_string = "|".join(batch_addresses)

        print(f"Processing batch {processed_batches + 1} ({len(batch_addresses)} addresses starting with {batch_addresses[0]}...)")
        print(f"Waiting {API_DELAY}s...")
        time.sleep(API_DELAY)

        # Fetch data for the batch
        # Optional: add n= parameter to get more/fewer than 50 transactions, e.g., {'q': 'multiaddr', 'active': address_param_string, 'n': 20}
        multiaddr_data = get_api_data({'q': 'multiaddr', 'active': address_param_string}, api_key)

        if multiaddr_data:
            # Store data keyed by address for easier lookup later
            # We need to know the structure first! Assuming it's a dict where keys are addresses
            if isinstance(multiaddr_data, dict):
                 all_multiaddr_data.update(multiaddr_data) # Merge results
            else:
                 print(f"Warning: Expected dict response from multiaddr, got {type(multiaddr_data)}", file=sys.stderr)


            # DEBUG: Print structure for the FIRST batch ONLY
            if processed_batches == 0:
                print(f"\nReceived multiaddr data for first batch (type: {type(multiaddr_data)}).")
                print("Multiaddr data snippet (first batch):")
                multiaddr_snippet_for_log = str(multiaddr_data)
                print(multiaddr_snippet_for_log[:1500] + ('...' if len(multiaddr_snippet_for_log) > 1500 else ''))
                # --- !!! PARSING LOGIC FOR TRANSACTIONS NEEDED HERE !!! ---
                print("\nParsing multiaddr transaction data (placeholder - needs update based on snippet above)...")
                # TODO: Based on the snippet structure seen in logs, write code here to:
                # 1. Iterate through addresses in `all_multiaddr_data`.
                # 2. Access the transaction list for each address (key might be 'txs' or similar).
                # 3. Iterate through transactions.
                # 4. Identify potential reward transactions (look for coinbase flags, specific input addresses like 'coinbase', consistent amounts).
                # 5. Store findings (e.g., list of addresses with recent rewards).
        else:
            print(f"Warning: Failed to fetch multiaddr data for batch {processed_batches + 1}", file=sys.stderr)

        processed_batches += 1
        # Optional: break after first batch during debugging
        # if processed_batches >= 1:
        #    print("DEBUG: Stopping after first batch.")
        #    break

    print(f"Finished fetching transaction data for {processed_batches} batches.")

    # --- Identify Addresses with Recent Rewards ---
    print("\nIdentifying addresses with recent rewards (placeholder)...")
    addresses_with_recent_rewards = []
    # TODO: Implement logic here based on parsed transaction data from all_multiaddr_data

    # --- Perform Original Concentration Calculations ---
    print("\nCalculating concentration (based on raw rich list)...")
    concentration_top_10 = "Error"
    concentration_top_100 = "Error"
    if parsed_holders and circulating_supply is not None and circulating_supply > 0:
        # Using originally parsed holders for concentration, sort by balance
        parsed_holders.sort(key=lambda x: x['balance'], reverse=True)
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
    recent_rewards_output = "### Addresses in Top 1000 Rich List with Recent Reward Activity\n\n"
    recent_rewards_output += "(Parsing logic for transaction data needed to populate this section)\n"
    # TODO: After parsing and identification works, format the output:
    # if addresses_with_recent_rewards:
    #    recent_rewards_output += f"Found {len(addresses_with_recent_rewards)} addresses with potential recent rewards. Examples:\n\n"
    #    for addr in addresses_with_recent_rewards[:10]: # Show first 10
    #         recent_rewards_output += f"- {addr}\n"
    # else:
    #    recent_rewards_output += "No addresses with recent reward activity identified (or data not parsed).\n"


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

**MultiAddr Data Snippet (First Batch Only):**
```json
{multiaddr_snippet_for_log if 'multiaddr_snippet_for_log' in locals() else 'Not Available'}...
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

