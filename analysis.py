import requests
import json
import sys
import os
import time
from datetime import datetime

# print("--- Analysis.py script started execution! ---") # Debug

# --- Constants ---
# Note: Using different base URLs for different types of queries now
API_BASE_URL_GENERAL = "https://chainz.cryptoid.info/lana/api.dws"
API_BASE_URL_ADDR_TX = "https://chainz.cryptoid.info/lana/address.tx2.dws" # Undocumented endpoint for address TXs?
API_DELAY = 11 # Delay between API calls in seconds (increased slightly for safety)

# --- Helper Function for API Calls ---
def get_api_data(base_url, query_params, api_key):
    """ Fetches data using API key from a specified base URL """
    if not api_key:
        print("Error: API Key is required but not provided.", file=sys.stderr)
        return None
    params_with_key = query_params.copy()
    params_with_key['key'] = api_key
    try:
        print(f"Requesting: {base_url} with params: {query_params}") # Debug
        response = requests.get(base_url, params=params_with_key, timeout=30)
        response.raise_for_status()
        content_type = response.headers.get('Content-Type', '')
        # Assume address TX endpoint returns JSON based on network log fmt=js
        if 'application/json' in content_type or 'javascript' in content_type:
             # It might return JSONP (like fmt=js suggests), try to strip callback if needed
            text_response = response.text.strip()
            # Basic check for JSONP wrapper like "callback(...)"
            if text_response.endswith(')') and '(' in text_response:
                start = text_response.find('(') + 1
                end = text_response.rfind(')')
                if start < end:
                    text_response = text_response[start:end]
            try:
                return json.loads(text_response) # Try parsing potentially cleaned text
            except json.JSONDecodeError:
                 print(f"Error: Failed to decode JSON/JSONP response. Response text: {text_response[:200]}...", file=sys.stderr)
                 return None # Failed parsing
        else:
             # Handle plain text for simpler endpoints like 'circulating'
             return response.text.strip()

    except requests.exceptions.Timeout:
        print(f"Error: API request timed out for params: {query_params}", file=sys.stderr)
        return None
    except requests.exceptions.HTTPError as http_err:
        print(f"Error: HTTP error occurred: {http_err} for params: {query_params}", file=sys.stderr)
        # Special handling for 404 maybe?
        if response.status_code == 404:
            print("Note: Got a 404 Not Found error. Endpoint or parameters might be incorrect.")
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

    # --- Fetch Recent Transactions for Top Addresses (Individually) ---
    print(f"\nFetching recent transactions for top addresses individually...")
    address_tx_data = {} # Store tx data per address
    addresses_with_recent_rewards = [] # Store addresses identified with rewards
    processed_count = 0
    max_addresses_to_check = 5 # Limit for initial testing

    for holder in parsed_holders[:max_addresses_to_check]:
        address_to_check = holder['address']
        print(f"\nProcessing address {processed_count + 1}/{max_addresses_to_check}: {address_to_check}")
        print(f"Waiting {API_DELAY}s...")
        time.sleep(API_DELAY)

        # Try fetching data using the discovered endpoint and hypothesized parameter 'a'
        # Parameters might need adjustment (e.g., use 'id=', 'addr=', or the 'dud=' seen in logs)
        tx_data = get_api_data(API_BASE_URL_ADDR_TX, {'a': address_to_check}, api_key)

        if tx_data:
            address_tx_data[address_to_check] = tx_data # Store the raw data

            # DEBUG: Print structure for the FIRST address ONLY
            if processed_count == 0:
                print(f"\nReceived transaction data for first address (type: {type(tx_data)}).")
                print("Transaction data snippet (first address):")
                tx_snippet_for_log = str(tx_data)
                print(tx_snippet_for_log[:1500] + ('...' if len(tx_snippet_for_log) > 1500 else ''))
                # --- !!! PARSING LOGIC FOR TRANSACTIONS NEEDED HERE !!! ---
                print("\nParsing transaction data (placeholder - needs update based on snippet above)...")
                # TODO: Based on the snippet structure seen in logs, write code here to:
                # 1. Access the actual list of transactions.
                # 2. Iterate through transactions.
                # 3. Identify potential reward transactions (look for coinbase flags, specific input addresses like 'coinbase', consistent amounts, maybe output 'type'?).
                # 4. If recent rewards found, add address_to_check to addresses_with_recent_rewards.
                # Example *GUESS* assuming tx_data is a list of tx dicts:
                # if isinstance(tx_data, list):
                #    recent_rewards_found = False
                #    for tx in tx_data[:20]: # Check recent N transactions
                #        if isinstance(tx, dict):
                #             # Check for signs of coinbase/reward
                #             is_reward = tx.get('is_coinbase') or tx.get('input_addr') == 'coinbase' # Hypothetical keys
                #             if is_reward:
                #                 print(f"  Found potential reward transaction: {tx.get('hash')}")
                #                 recent_rewards_found = True
                #                 break # Found one, no need to check further for this address for now
                #    if recent_rewards_found:
                #        addresses_with_recent_rewards.append(address_to_check)
        else:
            print(f"Warning: Failed to fetch transaction data for address {address_to_check}", file=sys.stderr)

        processed_count += 1

    print(f"\nFinished fetching transaction data for {processed_count} addresses.")

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
    # TODO: After parsing works, format the output:
    if addresses_with_recent_rewards:
       recent_rewards_output += f"Found {len(addresses_with_recent_rewards)} addresses with potential recent rewards:\n\n"
       for addr in addresses_with_recent_rewards:
            recent_rewards_output += f"- {addr}\n"
    else:
       recent_rewards_output += f"No addresses with obvious recent reward activity identified among the first {processed_count} checked (or parsing logic not implemented).\n"


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

**Transaction Data Snippet (First Address Checked Only):**
```json
{tx_snippet_for_log if 'tx_snippet_for_log' in locals() else 'Not Available'}...
```

*End of Report*
"""
    # Assign snippet for report - handle case where loop didn't run
    if processed_count > 0 and address_to_check in address_tx_data:
         tx_snippet_for_log = str(address_tx_data[address_to_check])[:500]
    else:
         tx_snippet_for_log = 'Not Available'
    # Re-format the string with the potentially updated snippet
    output_string = output_string.replace("{tx_snippet_for_log if 'tx_snippet_for_log' in locals() else 'Not Available'}...", tx_snippet_for_log)


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

