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
            print("\nParsing rich list data...") # Moved print here
            for holder_data in holders_list:
                if isinstance(holder_data, dict):
                    try:
                        address = holder_data.get('addr')
                        balance_raw = holder_data.get('amount')
                        if address is not None and balance_raw is not None:
                            balance = float(balance_raw)
                            parsed_holders.append({'address': address, 'balance': balance})
                        # else: # Reduce noise
                        #      print(f"Warning: Missing 'addr' or 'amount' in holder data: {holder_data}", file=sys.stderr)
                    except (ValueError, TypeError) as e:
                        print(f"Warning: Could not parse balance for holder data {holder_data}: {e}", file=sys.stderr)
                # else: # Reduce noise
                #     print(f"Warning: Expected dict item in rich1000 list, got {type(holder_data)}", file=sys.stderr)
            print(f"Successfully parsed {len(parsed_holders)} entries from rich list.")
        else:
            print(f"Error: Expected 'rich1000' key to contain a list, but got {type(holders_list)}.", file=sys.stderr)
    else:
        print("Could not fetch rich list data or data is not a dictionary.", file=sys.stderr)
        return None # Exit if rich list is essential

    # --- Fetch Masternode Info ---
    print(f"Waiting {API_DELAY}s...")
    time.sleep(API_DELAY)
    print("Fetching masternode info...")
    masternode_data = get_api_data({'q': 'masternodeinfo'}, api_key)
    active_masternode_addresses = set() # Initialize as empty set
    masternode_snippet_for_log = 'Not Available'

    if masternode_data:
        print(f"Received masternode info data (type: {type(masternode_data)}).")
        # DEBUG: Print snippet for inspection - THIS IS WHAT WE NEED TO SEE IN LOGS
        print("Masternode info snippet:")
        masternode_snippet_for_log = str(masternode_data)
        print(masternode_snippet_for_log[:1000] + ('...' if len(masternode_snippet_for_log) > 1000 else ''))

        # --- !!! PARSING LOGIC FOR MASTERNODES NEEDED HERE !!! ---
        print("\nParsing masternode info (placeholder - needs update based on snippet above)...")
        # TODO: Based on the snippet structure seen in logs, write code here to:
        # 1. Access the actual list or dict containing masternode operator addresses.
        # 2. Extract the addresses.
        # 3. Add them to the `active_masternode_addresses` set.
        # Example *GUESS* assuming a list of dicts like [{'address': 'LAddrMN1', ...}, ...]:
        # if isinstance(masternode_data, list):
        #     for mn_info in masternode_data:
        #         if isinstance(mn_info, dict) and 'address' in mn_info:
        #             active_masternode_addresses.add(mn_info['address'])
        # elif isinstance(masternode_data, dict) and 'nodes' in masternode_data: # Another guess
        #     # Maybe it's nested?
        #     if isinstance(masternode_data['nodes'], list):
        #        for mn_info in masternode_data['nodes']:
        #           if isinstance(mn_info, dict) and 'address' in mn_info:
        #               active_masternode_addresses.add(mn_info['address'])
        # print(f"Found {len(active_masternode_addresses)} potential active masternode addresses.")

    else:
        print("Could not fetch masternode info.", file=sys.stderr)
        # Continue without masternode info if desired, or return None

    # --- Identify Active Operators in Rich List ---
    print("\nIdentifying active operators in rich list (placeholder)...")
    rich_list_active_operators = []
    # TODO: Implement cross-referencing AFTER masternode parsing works
    # if active_masternode_addresses:
    #     rich_list_active_operators = [
    #         holder for holder in parsed_holders
    #         if holder['address'] in active_masternode_addresses
    #     ]
    #     # Sort them by balance
    #     rich_list_active_operators.sort(key=lambda x: x['balance'], reverse=True)
    #     print(f"Found {len(rich_list_active_operators)} active masternode operators within the top {len(parsed_holders)} rich list.")
    # else:
    #     print("No active masternode addresses found or parsed.")


    # --- Perform Original Concentration Calculations (Optional) ---
    # Keep previous calculations for context if desired
    print("\nCalculating concentration (based on raw rich list)...")
    concentration_top_10 = "Error"
    concentration_top_100 = "Error"
    if parsed_holders and circulating_supply is not None and circulating_supply > 0:
        filtered_holders = parsed_holders # Using raw list for now
        filtered_holders.sort(key=lambda x: x['balance'], reverse=True)
        if filtered_holders:
            top_10_balance = sum(h['balance'] for h in filtered_holders[:10])
            top_100_balance = sum(h['balance'] for h in filtered_holders[:100])
            concentration_top_10 = f"{(top_10_balance / circulating_supply) * 100:.2f}%"
            concentration_top_100 = f"{(top_100_balance / circulating_supply) * 100:.2f}%"
            # print("Concentration calculations complete.") # Debug
        else:
             concentration_top_10 = "N/A"
             concentration_top_100 = "N/A"
    else:
        print("Cannot perform concentration calculations: Missing parsed holders or valid circulating supply.")


    # --- Format Output ---
    print("\nFormatting results...")
    report_time_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    # --- Build Active Operators Output String (Placeholder) ---
    active_operators_output = "### Active Masternode Operators in Top 1000 Rich List\n\n"
    active_operators_output += "(Parsing logic for masternode info needed to populate this section)\n"
    # TODO: After parsing and cross-referencing works, format the output:
    # if rich_list_active_operators:
    #    active_operators_output += f"Found {len(rich_list_active_operators)} active operators. Top 10 shown:\n\n"
    #    active_operators_output += "| Rank | Address | Balance |\n"
    #    active_operators_output += "|---|---|---|\n"
    #    for i, operator in enumerate(rich_list_active_operators[:10]):
    #         active_operators_output += f"| {i+1} | {operator['address']} | {operator['balance']:,.2f} |\n"
    # else:
    #    active_operators_output += "No active masternode operators identified in the rich list (or data not parsed).\n"


    # --- Construct the Final Markdown Report ---
    output_string = f"""# LanaCoin Whale Analysis Report

**Data Fetched:** {report_time_utc}

* **Circulating Supply:** {circulating_supply:,.2f} LANA

---

{active_operators_output}

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

**Masternode Info Snippet:**
```json
{masternode_snippet_for_log[:500]}...
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

