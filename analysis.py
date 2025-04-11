import requests
import json
import sys
import os
import time
from datetime import datetime

print("--- Analysis.py script started execution! ---")

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
    # Check if API key is provided
    if not api_key:
        print("Error: API Key is required but not provided.", file=sys.stderr)
        return None

    # Create a copy to avoid modifying the original dict
    params_with_key = query_params.copy()
    # Add the API key - documentation confirmed 'key' parameter
    params_with_key['key'] = api_key

    try:
        # Make request WITH the key included in parameters
        # Debug print to show the request being made (excluding key value)
        print(f"Requesting: {API_BASE_URL} with params: {query_params}")
        # Perform the GET request with a timeout
        response = requests.get(API_BASE_URL, params=params_with_key, timeout=15)
        # Raise an exception for bad status codes (4xx client error or 5xx server error)
        response.raise_for_status()

        # Check content type - some simple APIs might return plain text
        content_type = response.headers.get('Content-Type', '')
        # If JSON, parse and return
        if 'application/json' in content_type:
            return response.json()
        # Otherwise, return raw text stripped of whitespace
        else:
            return response.text.strip()

    # Handle specific exceptions
    except requests.exceptions.Timeout:
        print(f"Error: API request timed out for params: {query_params}", file=sys.stderr)
        return None
    except requests.exceptions.HTTPError as http_err:
        print(f"Error: HTTP error occurred: {http_err} for params: {query_params}", file=sys.stderr)
        return None
    except requests.exceptions.RequestException as req_err:
        # Catch any other request-related errors
        print(f"Error: An ambiguous request error occurred: {req_err} for params: {query_params}", file=sys.stderr)
        return None
    except json.JSONDecodeError:
        # Handle cases where JSON decoding fails (e.g., invalid JSON format)
        print(f"Error: Failed to decode JSON response for params: {query_params}. Response text: {response.text[:200]}...", file=sys.stderr)
        return None


# --- Main Analysis Logic ---
def run_analysis():
    """
    Runs the main analysis process: fetches data, analyzes, formats output.
    """
    # Debug print indicating function start
    print("--- run_analysis() function started ---")

    # Read API key from environment variable 'API_KEY'
    api_key = os.environ.get('API_KEY')
    # Check if API key was successfully retrieved
    if not api_key:
        print("Error: Environment variable 'API_KEY' not set. Exiting.", file=sys.stderr)
        return None # Stop execution if no key found

    # Print last few characters of API key for verification (masked)
    print(f"Using API Key ending with: ...{api_key[-4:]}")

    # --- Make API calls ---
    # Wait before the first call to respect rate limits
    print(f"Waiting {API_DELAY}s before first API call...")
    time.sleep(API_DELAY)
    # Fetch circulating supply data
    print("Fetching circulating supply...")
    circulating_supply_data = get_api_data({'q': 'circulating'}, api_key)
    circulating_supply = None # Initialize variable
    # Process circulating supply data if fetched successfully
    if circulating_supply_data is not None:
        try:
            # Convert data to float (assuming plain text number)
            circulating_supply = float(circulating_supply_data)
            print(f"Received circulating supply: {circulating_supply}")
        except ValueError:
            # Handle error if conversion fails
            print(f"Error: Could not convert circulating supply data '{circulating_supply_data}' to float.", file=sys.stderr)
            return None # Exit if supply data is invalid
    else:
        # Handle failure to fetch supply data
        print("Failed to fetch circulating supply. Cannot continue analysis.", file=sys.stderr)
        return None

    # Wait before the next call
    print(f"Waiting {API_DELAY}s...")
    time.sleep(API_DELAY)
    # Fetch rich list data (top 1000 holders)
    print("Fetching rich list (top 1000)...")
    rich_list_data = get_api_data({'q': 'rich'}, api_key) # Use confirmed 'rich' query

    # Initialize placeholder variables for results
    parsed_holders = []
    concentration_top_10 = "TBD" # To Be Determined
    concentration_top_100 = "TBD"
    rich_list_snippet_for_log = 'Not Available' # Default snippet value

    # Process rich list data if fetched successfully
    if rich_list_data:
        # Print data type for debugging
        print(f"Received rich list data (type: {type(rich_list_data)}).")
        # DEBUG: Print snippet for inspection in logs
        print("Rich list snippet:")
        rich_list_snippet_for_log = str(rich_list_data)
        # Print first 1000 characters, add ellipsis if longer
        print(rich_list_snippet_for_log[:1000] + ('...' if len(rich_list_snippet_for_log) > 1000 else ''))

        # --- !!! PARSING LOGIC NEEDED HERE !!! ---
        # Placeholder for parsing logic based on observed data structure
        print("\nParsing rich list data (placeholder - needs update based on snippet above)...")
        # TODO: Implement parsing based on actual data structure found in logs.
        # Steps:
        # 1. Access the actual list/dict containing holder info.
        # 2. Iterate through holders.
        # 3. Extract address and balance.
        # 4. Convert balance to float.
        # 5. Store in `parsed_holders`.

        # --- Perform Calculations (Placeholder) ---
        # Placeholder for concentration calculation logic
        print("\nCalculating concentration (placeholder - needs parsed data and filtering)...")
        # TODO: Implement calculations after parsing works.
        # Steps:
        # 1. Filter `parsed_holders` (e.g., remove exchanges).
        # 2. Sum balances for top N filtered holders.
        # 3. Calculate percentage of `circulating_supply`.

    else:
        # Handle failure to fetch rich list data
        print("Could not fetch rich list data.", file=sys.stderr)
        # Keep default placeholder values

    # --- Format Output ---
    # Prepare the final report string
    print("\nFormatting results...")
    # Get current UTC time for the report timestamp
    report_time_utc = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S UTC')

    # Construct the Markdown report string
    output_string = f"""# LanaCoin Whale Analysis Report

**Data Fetched:** {report_time_utc}

* **Circulating Supply:** {circulating_supply:,.2f} LANA *(Used for calculations)*

## Top Holder Concentration (Based on Top 1000 from API)

* **Top 10 Holders (% of Circulating):** {concentration_top_10}
* **Top 100 Holders (% of Circulating):** {concentration_top_100}

*(Note: Calculations are placeholders until data parsing is implemented. Exchange/Contract addresses should ideally be excluded for accuracy)*

## Raw Rich List Data Snippet (for Debugging)

```json
{rich_list_snippet_for_log[:500]}...
```

*End of Report*
"""
    # Print the final formatted output string to stdout
    print("\n--- Analysis Output ---")
    print(output_string)
    print("--- End of Output ---")

    # Return the formatted string (useful if called as a module)
    return output_string

# --- Script Execution Guard ---
# Ensures the following code only runs when the script is executed directly
if __name__ == "__main__":
    # Debug print indicating entry into the main execution block
    print("--- Script __main__ block started ---")
    # Debug print before calling the main function
    print("--- About to call run_analysis() ---")
    # Call the main analysis function
    analysis_result_string = run_analysis()
    # Check if the function returned a result (indicating success)
    if analysis_result_string:
        print("--- run_analysis() completed successfully ---")
    else:
        # Indicate if the function returned None (likely due to an error)
        print("--- run_analysis() did not complete successfully or returned None ---")

    # Debug print indicating the script is about to finish
    print("--- Analysis.py script finished execution! ---")
