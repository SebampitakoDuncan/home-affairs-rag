#!/usr/bin/env python
"""
Test API Keys - Verify OpenRouter and Firecrawl API connections
"""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

from dotenv import load_dotenv

load_dotenv()


def test_openrouter_api():
    """Test OpenRouter API key"""
    print("=" * 60)
    print("Testing OpenRouter API")
    print("=" * 60)

    api_key = os.getenv("OPENROUTER_API_KEY")
    if not api_key:
        print("❌ OPENROUTER_API_KEY not found")
        return False

    print(f"✅ API Key found (length: {len(api_key)} chars)")

    try:
        from openai import OpenAI

        client = OpenAI(
            base_url=os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
            api_key=api_key,
        )

        # Test with a simple request
        response = client.chat.completions.create(
            model=os.getenv("OPENROUTER_MODEL", "gpt-4o-mini"),
            messages=[{"role": "user", "content": "Say 'Hello from OpenRouter'"}],
            max_tokens=10,
        )

        result = response.choices[0].message.content
        print(f"✅ API Response: {result}")
        return True

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_firecrawl_api():
    """Test Firecrawl API key"""
    print("\n" + "=" * 60)
    print("Testing Firecrawl API")
    print("=" * 60)

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        print("❌ FIRECRAWL_API_KEY not found")
        return False

    print(f"✅ API Key found (length: {len(api_key)} chars)")

    try:
        from firecrawl import FirecrawlApp

        client = FirecrawlApp(api_key=api_key)

        # Test with a simple scrape
        result = client.scrape_url(
            url="https://example.com",
            params={"formats": ["markdown"]},
        )

        if result.get("success") or result.get("markdown"):
            print(f"✅ API Response: Successfully scraped example.com")
            print(f"   Content length: {len(result.get('markdown', ''))} chars")
            return True
        else:
            print(f"❌ API returned error: {result.get('error', 'Unknown error')}")
            return False

    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def main():
    """Test all API connections"""

    print("\n" + "=" * 60)
    print("API Connection Test")
    print("=" * 60 + "\n")

    results = []

    # Test OpenRouter
    results.append(("OpenRouter", test_openrouter_api()))

    # Test Firecrawl
    results.append(("Firecrawl", test_firecrawl_api()))

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)

    for name, success in results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{name}: {status}")

    all_passed = all(success for _, success in results)

    print("\n" + "=" * 60)
    if all_passed:
        print("All API connections successful! 🎉")
    else:
        print("Some API connections failed. Please check your keys.")
    print("=" * 60 + "\n")

    return 0 if all_passed else 1


if __name__ == "__main__":
    sys.exit(main())
