import requests
import json
import sys
import os
import time
from datetime import datetime

# --- Configuration ---
# !!! SET THE TARGET ADDRESS TO TEST !!!
TARGET_ADDRESS = "LTdb5KrqryPihAU1RebDCy8tVxi1SVtGqu" # Replace if needed

# !!! SET SAMPLE HASHES FOR RAW DATA TESTS !!!
# Hashes obtained from user-provided data for block 950849
SAMPLE_TX_HASH = "fb030c17b03b078ea059de715df14526d070b49ecbbabe8e5eb054dd840d6656"
SAMPLE_BLOCK_HASH = "0a3e1281a3f9b45b6d39904ff5f28ca69612ac7fbf8c16ee8296e1594b4330c3"

# Output filename
API_TEST_OUTPUT_FILENAME = "api_test_results.txt"

# Base URLs
API_BASE_URL_GENERAL = "https://chainz.cryptoid.info/lana/api.dws"
API_BASE_URL_EXPLORER = "https://chainz.cryptoid.info/lana/explorer/" # Base for raw endpoints

# Delay between API calls
API_DELAY = 11

# --- Helper Function for API Calls ---
# (Same as previous version)
def get_api_data(base_url, query_params, api_key):
    """ Fetches data using API key from a specified base URL """
    # Allow calls without key for testing public/undocumented endpoints
    current_params = query_params.copy()
    if api_key:
        current_params['key'] = api_key

    http_method = requests.get
    try:
        print(f"Requesting: {base_url} with params: {current_params}", file=sys.stderr)
        response = http_method(base_url, params=current_params, timeout=30)
        print(f"Response Status Code: {response.status_code}", file=sys.stderr)

        try:
            text_response = response.text.strip()
            # Basic JSONP check
            if text_response.endswith(')') and '(' in text_response:
                 start = text_response.find('(') + 1
                 end = text_response.rfind(')')
                 if start < end:
                     text_response = text_response[start:end]
            # Return parsed JSON
            return json.loads(text_response)
        except json.JSONDecodeError:
            # Return raw text if not JSON
            return response.text.strip()

    except requests.exceptions.Timeout:
        error_msg = f"Error: API request timed out for params: {query_params}"
        print(error_msg, file=sys.stderr)
        return error_msg # Return error message
    except requests.exceptions.RequestException as req_err:
        error_msg = f"Error: An ambiguous request error occurred: {req_err} for params: {query_params}"
        print(error_msg, file=sys.stderr)
        return error_msg # Return error message

# --- Main Test Logic ---
def run_api_tests():
    """ Runs tests for various API endpoints and writes results to a file """
    print("Starting API endpoint tests...", file=sys.stderr)
    api_key = os.environ.get('API_KEY') # Still needed for some calls
    if not api_key:
        print("Warning: API Key environment variable 'API_KEY' not set.", file=sys.stderr)

    print(f"Testing for Address: {TARGET_ADDRESS}", file=sys.stderr)
    if api_key: print(f"Using API Key ending with: ...{api_key[-4:]}", file=sys.stderr)
    print(f"Testing with TX Hash: {SAMPLE_TX_HASH}", file=sys.stderr)
    print(f"Testing with Block Hash: {SAMPLE_BLOCK_HASH}", file=sys.stderr)


    # --- List of Queries to Test ---
    queries_to_test = [
        # Documented Simple Queries
        {'params': {'q': 'circulating'}, 'base': API_BASE_URL_GENERAL, 'desc': 'Circulating Supply'},
        {'params': {'q': 'totalcoins'}, 'base': API_BASE_URL_GENERAL, 'desc': 'Total Coins'},
        {'params': {'q': 'getblockcount'}, 'base': API_BASE_URL_GENERAL, 'desc': 'Block Count'},
        {'params': {'q': 'getdifficulty'}, 'base': API_BASE_URL_GENERAL, 'desc': 'Difficulty'},

        # Documented Address Queries
        {'params': {'q': 'addressfirstseen', 'a': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'Address First Seen'},
        {'params': {'q': 'addressinfo', 'a': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'Address Info'},
        {'params': {'q': 'getbalance', 'a': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'Get Balance (Live with Key)', 'needs_key': True},
        {'params': {'q': 'getreceivedbyaddress', 'a': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'Total Received by Address'},
        {'params': {'q': 'richrank', 'a': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'Rich List Rank'},

        # Documented Key-Required Queries
        {'params': {'q': 'multiaddr', 'active': TARGET_ADDRESS, 'n': 5}, 'base': API_BASE_URL_GENERAL, 'desc': 'MultiAddr (Single Address, n=5 TXs)', 'needs_key': True},
        {'params': {'q': 'unspent', 'active': TARGET_ADDRESS}, 'base': API_BASE_URL_GENERAL, 'desc': 'Unspent Outputs (Single Address)', 'needs_key': True},

        # --- Potential Undocumented / Extended ---
        # Test /explorer/tx.raw.dws - Using SAMPLE_TX_HASH now
        # Note: Might need explicit 'coin=lana' parameter if base URL doesn't imply it
        {'params': {'id': SAMPLE_TX_HASH}, 'base': API_BASE_URL_EXPLORER + "tx.raw.dws", 'desc': 'Raw Transaction Data (Undocumented)', 'needs_key': False},
        # Test /explorer/block.raw.dws - Using SAMPLE_BLOCK_HASH now
        # Note: Might need explicit 'coin=lana' parameter
        {'params': {'hash': SAMPLE_BLOCK_HASH}, 'base': API_BASE_URL_EXPLORER + "block.raw.dws", 'desc': 'Raw Block Data (Undocumented)', 'needs_key': False},

    ]

    # --- Open output file and run tests ---
    try:
        with open(API_TEST_OUTPUT_FILENAME, 'w', encoding='utf-8') as f:
            f.write(f"API Test Results for LanaCoin Address: {TARGET_ADDRESS}\n")
            f.write(f"Run Timestamp: {datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')}\n")
            f.write(f"Sample TX Hash Tested: {SAMPLE_TX_HASH}\n")
            f.write(f"Sample Block Hash Tested: {SAMPLE_BLOCK_HASH}\n")
            f.write("="*50 + "\n\n")

            for i, query_info in enumerate(queries_to_test):
                # Log progress to stderr
                print(f"\n--- Running Test {i+1}: {query_info['desc']} ---", file=sys.stderr)

                # Write test info to file
                f.write(f"--- Test {i+1}: {query_info['desc']} ---\n")
                f.write(f"Parameters: {query_info['params']}\n")
                f.write(f"Base URL: {query_info['base']}\n")

                # Determine if API key should be used for this call
                current_api_key = api_key if query_info.get('needs_key', False) else None
                if query_info.get('needs_key', False) and not api_key:
                    skip_msg = "Skipped (API Key Required but not provided)"
                    print(skip_msg, file=sys.stderr)
                    f.write(f"Result: {skip_msg}\n\n")
                    continue

                # Wait before making the call
                print(f"Waiting {API_DELAY}s...", file=sys.stderr)
                time.sleep(API_DELAY)

                # Make the API call
                response_data = get_api_data(query_info['base'], query_info['params'], current_api_key)

                # Write the raw response to the file
                f.write("\nRaw Response:\n")
                f.write("```\n") # Start code block markdown
                if isinstance(response_data, (dict, list)):
                    # Pretty print JSON to file
                    json.dump(response_data, f, indent=2)
                    f.write("\n") # Add newline after JSON dump
                elif response_data is None:
                    f.write("None (Request likely failed, check workflow stderr logs)")
                else:
                    # Write plain text or error string to file
                    f.write(str(response_data))
                f.write("\n```\n\n") # End code block markdown and add spacing

                # Check for rate limiting in response (basic check)
                if isinstance(response_data, str) and "Rate limit exceeded" in response_data:
                     print("\nRate limit likely exceeded. Stopping tests.", file=sys.stderr)
                     f.write("\nSTOPPED DUE TO RATE LIMIT\n")
                     break

            f.write("--- API Endpoint Testing Finished ---\n")
        print(f"Successfully wrote test results to {API_TEST_OUTPUT_FILENAME}", file=sys.stderr)

    except IOError as e:
        print(f"Error: Failed to write results to {API_TEST_OUTPUT_FILENAME}: {e}", file=sys.stderr)
        sys.exit(1) # Exit with error if file cannot be written
    except Exception as e:
         print(f"An unexpected error occurred during testing: {e}", file=sys.stderr)
         sys.exit(1)

# --- Script Execution ---
if __name__ == "__main__":
    run_api_tests()
    print("Test script finished.", file=sys.stderr)

