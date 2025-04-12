import requests
import json
import sys
import os
import time
from datetime import datetime

# --- Configuration ---
# !!! SET THE TARGET ADDRESS TO TEST !!!
TARGET_ADDRESS = "LTdb5KrqryPihAU1RebDCy8tVxi1SVtGqu" # Replace with a valid LanaCoin address you want to test

# Base URLs (Add more if testing other paths like /ext/)
API_BASE_URL_GENERAL = "https://chainz.cryptoid.info/lana/api.dws"
# API_BASE_URL_EXT = "https://chainz.cryptoid.info/lana/ext/" # Example for /ext/ path

# Delay between API calls
API_DELAY = 11

# --- Helper Function for API Calls ---
# (Same as used previously, adapted slightly)
def get_api_data(base_url, query_params, api_key):
    """ Fetches data using API key from a specified base URL """
    if not api_key:
        print("Error: API Key is required but not provided.", file=sys.stderr)
        return None
    params_with_key = query_params.copy()
    # Only add key if it's not None or empty
    if api_key:
        params_with_key['key'] = api_key

    # Use GET method for api.dws calls
    http_method = requests.get

    # Simple check if base_url suggests a different path structure
    # if "/ext/" in base_url:
    #    # Might need different method or parameter handling for /ext/ path
    #    pass

    try:
        print(f"Requesting: {base_url} with params: {params_with_key}", file=sys.stderr)
        response = http_method(base_url, params=params_with_key, timeout=30)
        # Don't raise for status immediately, let's see the raw response even for errors
        # response.raise_for_status()
        print(f"Response Status Code: {response.status_code}", file=sys.stderr)

        # Try to decode JSON if possible, otherwise return text
        try:
            # Handle potential JSONP from fmt.js if needed (though not specified in params here)
            text_response = response.text.strip()
            if text_response.endswith(')') and '(' in text_response:
                 start = text_response.find('(') + 1
                 end = text_response.rfind(')')
                 if start < end:
                     text_response = text_response[start:end]
            # Return parsed JSON or raw text
            return json.loads(text_response)
        except json.JSONDecodeError:
            # Return raw text if not JSON
            return response.text.strip()

    except requests.exceptions.Timeout:
        return f"Error: API request timed out for params: {query_params}"
    except requests.exceptions.RequestException as req_err:
        return f"Error: An ambiguous request error occurred: {req_err} for params: {query_params}"

# --- Main Test Logic ---
def run_api_tests():
    """ Runs tests for various API endpoints """
    print("Starting API endpoint tests...")
    api_key = os.environ.get('API_KEY')
    if not api_key:
        print("Warning: Environment variable 'API_KEY' not set. Key-required endpoints will likely fail.", file=sys.stderr)
        # Continue without key for non-key endpoints

    print(f"Testing for Address: {TARGET_ADDRESS}")
    if api_key:
        print(f"Using API Key ending with: ...{api_key[-4:]}")
    else:
        print("API Key not provided.")

    # --- List of Queries to Test ---
    # Each dict defines the query parameters and the base URL
    queries_to_test = [
        # Documented Simple Queries (Not address specific, but useful context)
        {'params': {'q': 'circulating'}, 'base': API_BASE_URL_GENERAL, 'desc': 'Circulating Supply'},
        {'params': {'q': 'totalcoins'}, 'base': API_BASE_URL_GENERAL, 'desc': 'Total Coins'},
        {'params': {'q': 'getblockcount'}, 'base': API_BASE_URL_GENERAL, 'desc': 'Block Count'},
        {'params': {'q': 'getdifficulty'}, 'base': API_BASE_URL_GENERAL, 'desc': 'Difficulty'},
        {'params': {'q': 'masternodecount'}, 'base': API_BASE_URL_GENERAL, 'desc': 'Masternode Count'},
        {'params': {'q': 'masternodeinfo'}, 'base': API_BASE_URL_GENERAL, 'desc': 'Masternode Info'},

        # Documented Address Queries
        {'params': {'q': 'addressfirstseen', 'a': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'Address First Seen'},
        {'params': {'q': 'addressinfo', 'a': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'Address Info'},
        {'params': {'q': 'getbalance', 'a': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'Get Balance (Cached without Key)'},
        {'params': {'q': 'getbalance', 'a': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'Get Balance (Live with Key)', 'needs_key': True},
        {'params': {'q': 'getreceivedbyaddress', 'a': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'Total Received by Address'},
        {'params': {'q': 'richrank', 'a': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'Rich List Rank'},

        # Documented Key-Required Queries
        {'params': {'q': 'multiaddr', 'active': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'MultiAddr (Single Address)', 'needs_key': True},
        {'params': {'q': 'multiaddr', 'active': TARGET_ADDRESS, 'n': 5}, 'base': API_BASE_URL_GENERAL, 'desc': 'MultiAddr (Single Address, n=5 TXs)', 'needs_key': True},
        {'params': {'q': 'unspent', 'active': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'Unspent Outputs (Single Address)', 'needs_key': True},
        # {'params': {'q': 'allbalances'}, 'base': API_BASE_URL_GENERAL, 'desc': 'All Balances (If supported)', 'needs_key': True}, # Might be too large

        # --- Potential Undocumented / Extended ---
        # How to call get_current_fee_per_kb is unknown, might not be a 'q' param. Skip for now.
        # {'params': {'q': 'get_current_fee_per_kb'}, 'base': API_BASE_URL_GENERAL, 'desc': 'Fee Estimation (Undocumented - GUESS)'},
        # Testing /ext/ path - Requires knowing the exact endpoint name after /ext/
        # {'params': {}, 'base': API_BASE_URL_EXT + "getlasttxs", 'desc': '/ext/getlasttxs (Undocumented - GUESS)'}, # Needs correct base + params?

        # Add more documented or potential undocumented queries here to test...
    ]

    results = {}

    for i, query_info in enumerate(queries_to_test):
        print(f"\n--- Test {i+1}: {query_info['desc']} ---")
        print(f"Parameters: {query_info['params']}")
        print(f"Base URL: {query_info['base']}")

        # Skip key-required endpoints if no key is provided
        if query_info.get('needs_key', False) and not api_key:
            print("Skipping test: API Key required but not provided.")
            results[query_info['desc']] = "Skipped (API Key Required)"
            continue

        # Wait before making the call
        print(f"Waiting {API_DELAY}s...", file=sys.stderr)
        time.sleep(API_DELAY)

        # Make the API call
        response_data = get_api_data(query_info['base'], query_info['params'], api_key)

        # Print the raw response
        print("\nRaw Response:")
        print("```") # Start code block for readability in logs
        if isinstance(response_data, (dict, list)):
            # Pretty print JSON
            print(json.dumps(response_data, indent=2))
        elif response_data is None:
            print("None (Request likely failed, check stderr logs above)")
        else:
            # Print plain text or error string
            print(response_data)
        print("```") # End code block

        results[query_info['desc']] = response_data # Store result (optional)

        # Check if we need to stop early (e.g., rate limited) - basic check
        if isinstance(response_data, str) and "Rate limit exceeded" in response_data:
             print("\nRate limit likely exceeded. Stopping tests.", file=sys.stderr)
             break

    print("\n--- API Endpoint Testing Finished ---")
    # Optionally print summary of results dict here if needed

# --- Script Execution ---
if __name__ == "__main__":
    run_api_tests()

