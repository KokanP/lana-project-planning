Requesting: https://chainz.cryptoid.info/lana/api.dws with params: {'q': 'circulating', 'key': '29e9ef74c886'}
Requesting: https://chainz.cryptoid.info/lana/api.dws with params: {'q': 'rich', 'key': '29e9ef74c886'}

Parsing rich list data...
Successfully parsed 1000 entries from rich list.

Fetching recent transactions for top addresses individually using q=multiaddr...

Processing address 1/5: LTdb5KrqryPihAU1RebDCy8tVxi1SVtGqu
Waiting 11s...
Requesting: https://chainz.cryptoid.info/lana/api.dws with params: {'q': 'multiaddr', 'active': 'LTdb5KrqryPihAU1RebDCy8tVxi1SVtGqu', 'key': '29e9ef74c886'}

Received multiaddr response for first address (type: <class 'dict'>).
Multiaddr response snippet (first address):
{'addresses': [{'address': 'LTdb5KrqryPihAU1RebDCy8tVxi1SVtGqu', 'total_sent': 245070714418857776, 'total_received': 274101449795473279, 'final_balance': 29030735376615503, 'n_tx': 77389}], 'txs': [{'hash': 'b38048c77741757c8a62a51c0d00ebd34455ec692036b5e31b055d13d14b769a', 'confirmations': 4, 'change': 453846178974, 'time_utc': '2025-04-11T23:27:44Z', 'n': 2}, {'hash': 'b38048c77741757c8a62a51c0d00ebd34455ec692036b5e31b055d13d14b769a', 'confirmations': 4, 'change': 453846000000, 'time_utc': '2025-04-11T23:27:44Z', 'n': 1}, {'hash': 'b38048c77741757c8a62a51c0d00ebd34455ec692036b5e31b055d13d14b769a', 'confirmations': 4, 'change': -667786049795, 'time_utc': '2025-04-11T23:27:44Z'}, {'hash': '1ff4af3aa7f6e93aac096db23c217f902a6e2d7a12bf32fd7b091b7aee3c21ea', 'confirmations': 13, 'change': 419624838297, 'time_utc': '2025-04-11T22:27:44Z', 'n': 2}, {'hash': '1ff4af3aa7f6e93aac096db23c217f902a6e2d7a12bf32fd7b091b7aee3c21ea', 'confirmations': 13, 'change': 419622999999, 'time_utc': '2025-04-11T22:27:44Z', 'n': 1}, {'hash': '1ff4af3aa7f6e93aac096db23c217f902a6e2d7a12bf32fd7b091b7aee3c21ea', 'confirmations': 13, 'change': -596569000000, 'time_utc': '2025-04-11T22:27:44Z'}, {'hash': '8aa63f1bb3384c5a60a6ea64354a072aed0d05be7a4d69daea414dd5376b2e5b', 'confirmations': 36, 'change': 366129262922, 'time_utc': '2025-04-11T19:38:40Z', 'n': 2}, {'hash': '8aa63f1bb3384c5a60a6ea64354a072aed0d05be7a4d69daea414dd5376b2e5b', 'confirmations': 36, 'change': 366129000000, 'time_utc': '2025-04-11T19:3...

Parsing multiaddr transaction data (placeholder - needs update based on snippet above)...

Processing address 2/5: LaFnKHXxj4KEuVMbtyLnNCJTpUtTPWXjJC
Waiting 11s...
Requesting: https://chainz.cryptoid.info/lana/api.dws with params: {'q': 'multiaddr', 'active': 'LaFnKHXxj4KEuVMbtyLnNCJTpUtTPWXjJC', 'key': '29e9ef74c886'}

Processing address 3/5: LLZr9vsHWjcL6Tohu12TrYJtrgctapZHjH
Waiting 11s...
Requesting: https://chainz.cryptoid.info/lana/api.dws with params: {'q': 'multiaddr', 'active': 'LLZr9vsHWjcL6Tohu12TrYJtrgctapZHjH', 'key': '29e9ef74c886'}

Processing address 4/5: LbRugxTQt4eJFHaDc73zKjViVEuNcP3NwD
Waiting 11s...
Requesting: https://chainz.cryptoid.info/lana/api.dws with params: {'q': 'multiaddr', 'active': 'LbRugxTQt4eJFHaDc73zKjViVEuNcP3NwD', 'key': '29e9ef74c886'}

Processing address 5/5: LaXTGF8X6FGXCSgWc3WFXimw5fWHMAcFQe
Waiting 11s...
Requesting: https://chainz.cryptoid.info/lana/api.dws with params: {'q': 'multiaddr', 'active': 'LaXTGF8X6FGXCSgWc3WFXimw5fWHMAcFQe', 'key': '29e9ef74c886'}

Finished fetching transaction data for 5 addresses.

Calculating concentration (based on raw rich list)...

Formatting results...

--- Analysis Output ---
# LanaCoin Whale Analysis Report

**Data Fetched:** 2025-04-11 23:47:51 UTC

* **Circulating Supply:** 3,521,570,385.42 LANA

---

### Addresses in Top 5 Checked with Recent Reward Activity

No addresses with obvious recent reward activity identified among the first 5 checked (or parsing logic not implemented).


---

## Top Holder Concentration (Based on Raw Top 1000 API Data)

* **Top 10 Holders (% of Circulating):** 35.64%
* **Top 100 Holders (% of Circulating):** 73.04%

*(Note: Concentration based on raw API data. Known exchange/contract addresses are NOT filtered out.)*

---

## Raw Data Snippets (for Debugging)

**Rich List Snippet:**
```json
{'total': 3521561132.86507, 'rich1000': [{'amount': 290304954.704863, 'addr': 'LTdb5KrqryPihAU1RebDCy8tVxi1SVtGqu', 'wallet': 78322}, {'amount': 155306576.851586, 'addr': 'LaFnKHXxj4KEuVMbtyLnNCJTpUtTPWXjJC', 'wallet': 96575}, {'amount': 142913571.089058, 'addr': 'LLZr9vsHWjcL6Tohu12TrYJtrgctapZHjH', 'wallet': 213166}, {'amount': 122423485.497355, 'addr': 'LbRugxTQt4eJFHaDc73zKjViVEuNcP3NwD', 'wallet': 166701}, {'amount': 104701232.113773, 'addr': 'LaXTGF8X6FGXCSgWc3WFXimw5fWHMAcFQe', 'wallet': ...
```

**MultiAddr Response Snippet (First Address Checked Only):**
```json
{'addresses': [{'address': 'LTdb5KrqryPihAU1RebDCy8tVxi1SVtGqu', 'total_sent': 245070714418857776, 'total_received': 274101449795473279, 'final_balance': 29030735376615503, 'n_tx': 77389}], 'txs': [{'hash': 'b38048c77741757c8a62a51c0d00ebd34455ec692036b5e31b055d13d14b769a', 'confirmations': 4, 'change': 453846178974, 'time_utc': '2025-04-11T23:27:44Z', 'n': 2}, {'hash': 'b38048c77741757c8a62a51c0d00ebd34455ec692036b5e31b055d13d14b769a', 'confirmations': 4, 'change': 453846000000, 'time_utc': '20...
```

*End of Report*

--- End of Output ---
