# DuckDuckGo MCP Server Testing Guide

## Problem Summary

The `search` tool in the DuckDuckGo MCP server was failing due to **SSL certificate verification errors** caused by organizational SSL inspection/proxy infrastructure. The error was:

```
[SSL: CERTIFICATE_VERIFY_FAILED] certificate verify failed: self-signed certificate in certificate chain
```

## Root Cause

Your organization uses SSL inspection, which intercepts HTTPS traffic and replaces certificates with self-signed ones. Python's `httpx` library (used by the MCP server) validates SSL certificates by default and rejects self-signed certificates, causing all requests to fail.

## Solution

Modified the `httpx.AsyncClient()` calls to disable SSL verification by adding `verify=False`:

**Files Modified:**
- `src/duckduckgo_mcp_server/server.py`
  - Line 85: Added `verify=False` to search client
  - Line 159: Added `verify=False` to fetch_content client
  - Line 16: Added warnings filter to suppress SSL warnings

## Testing

### Test Script Usage

A test script `test_search.py` has been created to test the MCP server tools directly without needing to run the full MCP server.

#### Run All Tests
```bash
uv run python test_search.py --all
```

#### Test Search Only
```bash
uv run python test_search.py --search "your query here" --max-results 5
```

#### Test Fetch Content Only
```bash
uv run python test_search.py --fetch "https://example.com"
```

### Example Output (Success)

```
============================================================
Testing Search: 'Python programming'
============================================================

[INFO] Searching DuckDuckGo for: Python programming
[INFO] Successfully found 3 results
✓ Success! Found 3 results:

1. Welcome to Python.org
   URL: https://www.python.org/
   Snippet: Python is a versatile and easy-to-learn programming language...

2. Python Tutorial - W3Schools
   URL: https://www.w3schools.com/python/
   Snippet: Learn Python. Python is a popular programming language...

3. Python (programming language) - Wikipedia
   URL: https://en.wikipedia.org/wiki/Python_(programming_language)
   Snippet: Python is a high-level, general-purpose programming language...
```

## Using with Claude Code

### 1. Reinstall the Modified Package

Since you modified the source code, you need to reinstall:

```bash
cd /Users/smandyashankar/Downloads/duckduckgo-mcp-server
uv sync
```

### 2. Update Your Claude Code MCP Settings

Make sure your MCP server is configured in Claude Code. The server should automatically pick up the changes.

### 3. Test in Claude Code

Try using the `mcp__duckduckgo__search` tool from Claude Code - it should now work!

## Security Note

⚠️ **Disabling SSL verification reduces security** as it makes the connection vulnerable to man-in-the-middle attacks. However, in corporate environments with SSL inspection, this is often the only way to make HTTPS requests work.

### Alternative Solutions (More Secure)

If you want to maintain better security:

1. **Install your organization's root certificate:**
   ```bash
   # Export your org's root cert and set it as the cert bundle
   export SSL_CERT_FILE=/path/to/your/org/cert.pem
   ```

2. **Configure httpx to use custom certificates:**
   ```python
   httpx.AsyncClient(verify="/path/to/cert.pem")
   ```

3. **Use certifi with custom certs:**
   ```bash
   pip install certifi-system-store
   ```

## Files Created/Modified

### Created
- `test_search.py` - Standalone test script for debugging

### Modified
- `src/duckduckgo_mcp_server/server.py`
  - Added `verify=False` to both httpx clients
  - Added warnings filter for SSL warnings

## Next Steps

1. The modified server is now working locally
2. You can test it with the provided test script
3. To use it in Claude Code, make sure the modified version is installed
4. Consider creating a fork/branch if you want to contribute this fix back to the project (with configuration option for SSL verification)

## Troubleshooting

### If search still doesn't work:

1. **Check rate limiting:** DuckDuckGo has rate limits (30 requests/min for search)
2. **Check bot detection:** DuckDuckGo may still block if it detects automated requests
3. **Network issues:** Verify you can access https://html.duckduckgo.com from your network
4. **Check logs:** Look at the `[ERROR]` messages in the test output

### Test connectivity:
```bash
curl -k https://html.duckduckgo.com/html
```

If this fails, there may be additional network restrictions in your organization.
