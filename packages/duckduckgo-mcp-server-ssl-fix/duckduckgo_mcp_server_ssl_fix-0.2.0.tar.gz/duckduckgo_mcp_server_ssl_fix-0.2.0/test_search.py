#!/usr/bin/env python3
"""
Test script for DuckDuckGo MCP Server search functionality.
This script directly tests the search and fetch_content functions.
"""

import asyncio
import sys
from typing import Optional


class MockContext:
    """Mock context for testing without MCP server"""

    async def info(self, message: str):
        print(f"[INFO] {message}")

    async def error(self, message: str):
        print(f"[ERROR] {message}", file=sys.stderr)


async def test_search(query: str, max_results: int = 5):
    """Test the search functionality"""
    print(f"\n{'='*60}")
    print(f"Testing Search: '{query}'")
    print(f"{'='*60}\n")

    from duckduckgo_mcp_server.server import searcher

    ctx = MockContext()

    try:
        results = await searcher.search(query, ctx, max_results)

        if results:
            print(f"✓ Success! Found {len(results)} results:\n")
            for result in results:
                print(f"{result.position}. {result.title}")
                print(f"   URL: {result.link}")
                print(f"   Snippet: {result.snippet[:100]}...")
                print()
        else:
            print("✗ No results returned (could be blocked or no matches)")

        # Also test the formatted output
        formatted = searcher.format_results_for_llm(results)
        print("\n--- Formatted Output ---")
        print(formatted)

        return results

    except Exception as e:
        print(f"✗ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return None


async def test_fetch_content(url: str):
    """Test the fetch_content functionality"""
    print(f"\n{'='*60}")
    print(f"Testing Fetch Content: '{url}'")
    print(f"{'='*60}\n")

    from duckduckgo_mcp_server.server import fetcher

    ctx = MockContext()

    try:
        content = await fetcher.fetch_and_parse(url, ctx)

        if content and not content.startswith("Error:"):
            print(f"✓ Success! Fetched {len(content)} characters")
            print(f"\nFirst 500 characters:")
            print(content[:500])
            print("...")
        else:
            print(f"✗ Failed or returned error:")
            print(content)

        return content

    except Exception as e:
        print(f"✗ Exception occurred: {e}")
        import traceback
        traceback.print_exc()
        return None


async def run_all_tests():
    """Run all tests"""
    print("\n" + "="*60)
    print("DuckDuckGo MCP Server Test Suite")
    print("="*60)

    # Test 1: Simple search
    await test_search("Python programming", max_results=3)

    # Small delay to avoid rate limiting
    await asyncio.sleep(2)

    # Test 2: Another search
    await test_search("OpenAI GPT", max_results=3)

    # Small delay
    await asyncio.sleep(2)

    # Test 3: Fetch content
    await test_fetch_content("https://example.com")

    print("\n" + "="*60)
    print("Test Suite Complete")
    print("="*60 + "\n")


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(description="Test DuckDuckGo MCP Server")
    parser.add_argument("--search", type=str, help="Test search with a specific query")
    parser.add_argument("--fetch", type=str, help="Test fetch_content with a specific URL")
    parser.add_argument("--max-results", type=int, default=5, help="Maximum results for search")
    parser.add_argument("--all", action="store_true", help="Run all tests")

    args = parser.parse_args()

    if args.search:
        asyncio.run(test_search(args.search, args.max_results))
    elif args.fetch:
        asyncio.run(test_fetch_content(args.fetch))
    elif args.all:
        asyncio.run(run_all_tests())
    else:
        print("Usage:")
        print("  Test search:        python test_search.py --search 'your query'")
        print("  Test fetch:         python test_search.py --fetch 'https://example.com'")
        print("  Run all tests:      python test_search.py --all")
        print("\nExamples:")
        print("  python test_search.py --search 'Python programming' --max-results 3")
        print("  python test_search.py --fetch 'https://python.org'")
        print("  python test_search.py --all")


if __name__ == "__main__":
    main()
