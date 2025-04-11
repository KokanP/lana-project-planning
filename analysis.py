import requests
import json
import sys
import os
import time # Import time module for delays
from datetime import datetime # If needed for output string

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

    # Create a copy to avoid modifying the original dict
    params_with_key = query_params.copy()
    # Add the API key - documentation confirmed 'key' parameter
    params_with_key['key'] = api_key

    try:
        # Make request WITH the key included in parameters
        print(f"Requesting: {API_BASE_URL} with params: {query_params}") # Debug: Show which query is made (key hidden)
        response = requests.get(API_BASE_URL, params=params_with_key, timeout=15) # Added timeout
        response.raise_for_status() # Raise HTTPError for bad responses (4xx or 5xx)

        # Check content type - some simple APIs might return plain text
        content_type = response.headers.get('Content-Type', '')
        if 'application/json' in content_type:
            return response.json() # Attempt to parse JSON
        else:
            # Return raw text for non-JSON responses (like totalcoins/circulating might be)
            return response.text.strip() # Strip whitespace

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
        # This might happen if plain text is returned but we expected JSON (should be less likely now)
        print(f"Error: Failed to decode JSON response for params: {query_params}. Response text: {response.text[:200]}...", file=sys.stderr)
        return None


# --- Main Analysis Logic ---
def run_analysis():
    """
    Runs the main analysis process: fetches data, analyzes, formats output.
    """
    print("Starting analysis...")

    # Read API key from environment variable 'API_KEY'
    api_key = os.environ.get('API_KEY')
    if not api_key:
        print("Error: Environment variable 'API_KEY' not set. Exiting.", file=sys.stderr)
        # Optional: Add fallback for local .env file using python-dotenv
        # try:
        #     from dotenv import load_dotenv
        #     load_dotenv()
        #     api_key = os.environ.get('API_KEY')
        # except ImportError:
        #     pass # dotenv not installed
        # if not api_key: # Check again after trying dotenv
        #     print("API_KEY not found in environment or .env file. Exiting.", file=sys.stderr)
        #     return None # Stop if no key found
        return None # Stop if no key found via environment

    print(f"Using API Key ending with: ...{api_key[-4:]}") # Mask key in logs

    # --- Make API calls ---
    print(f"Waiting {API_DELAY}s before first API call...")
    time.sleep(API_DELAY)
    print("Fetching circulating supply...")
    circulating_supply_data = get_api_data({'q': 'circulating'}, api_key)
    circulating_supply = None
    if circulating_supply_data is not None:
        try:
            # Assuming circulating supply is returned as plain text number
            circulating_supply = float(circulating_supply_data)
            print(f"Received circulating supply: {circulating_supply}")
        except ValueError:
            print(f"Error: Could not convert circulating supply data '{circulating_supply_data}' to float.", file=sys.stderr)
            return None # Exit if we can't get supply
    else:
        print("Failed to fetch circulating supply. Cannot continue analysis.", file=sys.stderr)
        return None

    print(f"Waiting {API_DELAY}s...")
    time.sleep(API_DELAY)
    print("Fetching rich list (top 1000)...")
    rich_list_data = get_api_data({'q': 'rich'}, api_key) # Use confirmed 'rich' query

    # Placeholder variables for results
    parsed_holders = []
    concentration_top_10 = "TBD"
    concentration_top_100 = "TBD"

    if rich_list_data:
        print(f"Received rich list data (type: {type(rich_list_data)}).")
        # DEBUG: Print snippet for inspection - THIS IS WHAT WE NEED TO SEE IN LOGS
        print("Rich list snippet:")
        rich_list_snippet_for_log = str(rich_list_data)
        print(rich_list_snippet_for_log[:1000] + ('...' if len(rich_list_snippet_for_log) > 1000 else ''))

        # --- !!! PARSING LOGIC NEEDED HERE !!! ---
        print("\nParsing rich list data (placeholder - needs update based on snippet above)...")
        # TODO: Based on the snippet structure seen in logs, write code here to:
        # 1. Access the actual list of holders (it might be nested inside the JSON)
        # 2. Iterate through the list
        # 3. Extract the 'address' and 'balance' for each holder
        # 4. Convert balance to float
        # 5. Store results (e.g., in the `parsed_holders` list as dicts: [{'address': addr, 'balance': bal}, ...])
        # Example *GUESS* assuming list of lists: [[rank, address, balance], ...]
        # if isinstance(rich_list_data, list):
        #    for item in rich_list_data:
        #        try:
        #            if len(item) >= 3:
        #                 address = item[1]
        #                 balance = float(item[2])
        #                 parsed_holders.append({'address': address, 'balance': balance})
        #        except (IndexError, ValueError, TypeError) as e:
        #             print(f"Warning: Could not parse item {item}: {e}", file=sys.stderr)
        # else:
        #     print("Warning: Rich list data not in expected list format.", file=sys.stderr)

        # --- Perform Calculations (Placeholder - needs parsed_holders) ---
        print("\nCalculating concentration (placeholder - needs parsed data and filtering)...")
        # TODO: Implement actual calculation AFTER parsing works
        # 1. Filter `parsed_holders` to exclude known exchange addresses (requires a list)
        # 2. Sum balances for Top 10, Top 100 filtered holders
        # 3. Calculate percentage of `circulating_supply`
        # Example:
        # if parsed_holders and circulating_supply > 0:
        #     # Assuming parsed_holders is sorted by balance descending
        #     # Add filtering logic here
        #     filtered_holders = parsed_holders # Replace with actual filtered list
        #     top_10_balance = sum(h['balance'] for h in filtered_holders[:10])
        #     top_100_balance = sum(h['balance'] for h in filtered_holders[:100])
        #     concentration_top_10 = f"{(top_10_balance / circulating_supply) * 100:.2f}%"
        #     concentration_top_100 = f"{(top_100_balance / circulating_supply) * 100:.2f