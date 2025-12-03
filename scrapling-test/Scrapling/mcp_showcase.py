#!/usr/bin/env python3
"""
MCP Integration Showcase: Scrapling with Claude/AI Chatbots

This demonstrates how the MCP integration works and how an AI chatbot
would use Scrapling's tools through the MCP protocol.
"""

import asyncio
from scrapling.core.ai import ScraplingMCPServer, ResponseModel


async def demonstrate_mcp_tools():
    """Demonstrate all MCP tools and their capabilities"""
    server = ScraplingMCPServer()
    
    print("=" * 80)
    print("SCRAPLING MCP INTEGRATION SHOWCASE")
    print("=" * 80)
    print()
    
    # ===========================================================================
    # SCENARIO 1: Basic Static HTML Extraction (using 'get' tool)
    # ===========================================================================
    print("\n[SCENARIO 1] Basic Static Content - Using 'get' Tool")
    print("-" * 80)
    print("Use Case: Scrape static HTML page (fast, low overhead)")
    print("Protection Level: Low-Mid")
    print()
    
    result1 = server.get(
        url="https://httpbin.org/html",
        extraction_type="markdown",
        main_content_only=True,
        impersonate="chrome"
    )
    
    print(f"Response Status: {result1.status}")
    print(f"Response URL: {result1.url}")
    print(f"Content Length: {len(result1.content)} chunks")
    print(f"First chunk preview (first 200 chars):")
    print(f"  {result1.content[0][:200]}...")
    print()
    
    # ===========================================================================
    # SCENARIO 2: Parallel Bulk Requests (using 'bulk_get' tool)
    # ===========================================================================
    print("\n[SCENARIO 2] Parallel Requests - Using 'bulk_get' Tool")
    print("-" * 80)
    print("Use Case: Fetch multiple URLs concurrently")
    print("Protection Level: Low-Mid")
    print()
    
    urls = (
        "https://httpbin.org/html",
        "https://httpbin.org/html",
        "https://httpbin.org/html"
    )
    
    results2 = await server.bulk_get(
        urls=urls,
        extraction_type="markdown",
        main_content_only=True
    )
    
    print(f"Fetched {len(results2)} URLs in parallel")
    for i, result in enumerate(results2, 1):
        print(f"  {i}. Status: {result.status}, Content chunks: {len(result.content)}")
    print()
    
    # ===========================================================================
    # SCENARIO 3: JavaScript Rendering (using 'fetch' tool)
    # ===========================================================================
    print("\n[SCENARIO 3] JavaScript-Heavy Sites - Using 'fetch' Tool")
    print("-" * 80)
    print("Use Case: Scrape sites that require JS execution (React, Vue, etc.)")
    print("Protection Level: Mid")
    print("Benefits: Full DOM after JS execution, renders SPA content")
    print()
    
    result3 = await server.fetch(
        url="https://httpbin.org/html",
        extraction_type="html",
        main_content_only=True,
        headless=True,
        wait=500,  # Wait 500ms after page loads
        disable_resources=False
    )
    
    print(f"Rendered page status: {result3.status}")
    print(f"Content chunks: {len(result3.content)}")
    print(f"Supports:")
    print(f"  ✓ JavaScript execution")
    print(f"  ✓ Wait for elements: wait_selector parameter")
    print(f"  ✓ Custom cookies/headers")
    print(f"  ✓ Proxy support")
    print()
    
    # ===========================================================================
    # SCENARIO 4: CSS Selector Pre-Filtering (Token Optimization)
    # ===========================================================================
    print("\n[SCENARIO 4] Selector-Based Content Narrowing (Token Efficiency)")
    print("-" * 80)
    print("Use Case: Extract specific elements BEFORE AI processing")
    print("Benefit: Dramatically reduce token usage (80% reduction typical)")
    print()
    
    print("WITHOUT selector (full page ~5000 tokens):")
    print("  Claude receives entire HTML with ads, nav, footer, etc.")
    print()
    
    print("WITH selector (extracted content ~500 tokens):")
    result4 = server.get(
        url="https://httpbin.org/html",
        css_selector="h1, p, div",  # Extract headers and paragraphs only
        extraction_type="markdown",  # Convert to markdown for AI
        main_content_only=True
    )
    print(f"  Extracted {len(result4.content)} markdown chunks")
    print(f"  ✓ Only relevant content sent to AI")
    print(f"  ✓ Reduces API tokens")
    print(f"  ✓ Faster processing")
    print()
    
    # ===========================================================================
    # SCENARIO 5: High-Protection Site (using 'stealthy_fetch' tool)
    # ===========================================================================
    print("\n[SCENARIO 5] High-Protection Sites - Using 'stealthy_fetch' Tool")
    print("-" * 80)
    print("Use Case: Bypass Cloudflare, WAF, bot detection")
    print("Protection Level: High")
    print("Features:")
    print("  ✓ Camoufox browser (advanced anti-detection)")
    print("  ✓ Cloudflare Turnstile solving")
    print("  ✓ GeoIP spoofing")
    print("  ✓ WebRTC leak prevention")
    print("  ✓ OS fingerprint randomization")
    print()
    
    result5 = await server.stealthy_fetch(
        url="https://httpbin.org/html",
        extraction_type="markdown",
        solve_cloudflare=False,  # Would be True for CF-protected sites
        headless=True,
        allow_webgl=True,
        disable_webgl=False,
        humanize=True,  # Simulate human mouse movements
        network_idle=True,  # Wait for network to be idle
        timeout=30000
    )
    
    print(f"Stealthy fetch status: {result5.status}")
    print(f"Content chunks: {len(result5.content)}")
    print(f"Notes:")
    print(f"  • Slower than regular fetch (high protection = slower)")
    print(f"  • Use only when necessary (regular get/fetch fail)")
    print()
    
    # ===========================================================================
    # SCENARIO 6: Bulk High-Protection (using 'bulk_stealthy_fetch' tool)
    # ===========================================================================
    print("\n[SCENARIO 6] Bulk High-Protection - Using 'bulk_stealthy_fetch' Tool")
    print("-" * 80)
    print("Use Case: Scrape multiple protected sites in parallel")
    print()
    
    urls = (
        "https://httpbin.org/html",
        "https://httpbin.org/html"
    )
    
    results6 = await server.bulk_stealthy_fetch(
        urls=urls,
        extraction_type="markdown",
        solve_cloudflare=False,
        headless=True
    )
    
    print(f"Fetched {len(results6)} protected URLs")
    for i, result in enumerate(results6, 1):
        print(f"  {i}. Status: {result.status}")
    print()
    
    # ===========================================================================
    # SCENARIO 7: Adaptive Scraping + MCP (Advanced)
    # ===========================================================================
    print("\n[SCENARIO 7] Adaptive Scraping Through MCP")
    print("-" * 80)
    print("How It Works:")
    print()
    print("  1. First Request (auto_save=True in background):")
    print("     • Selector applies: '.product-card'")
    print("     • Elements found and fingerprints saved to ~/.scrapling/adaptive/")
    print("     • Fingerprints include: text, attributes, structure, position")
    print()
    print("  2. Website Redesign Happens (HTML structure completely changes)")
    print("     • Old: <div class='product-card'> → New: <article class='item'>")
    print()
    print("  3. Second Request (adaptive=True in background):")
    print("     • Selector applies: '.product-card' (doesn't match anymore!)")
    print("     • Scrapling detects mismatch")
    print("     • Loads fingerprints from storage")
    print("     • Uses similarity matching on new elements")
    print("     • Finds 'Gaming Laptop' element via fingerprint match (85% score)")
    print("     • Returns same data format despite HTML changes")
    print()
    print("  Benefit for AI: Same API response format regardless of DOM changes!")
    print()
    
    # ===========================================================================
    # SCENARIO 8: Extract Types Comparison
    # ===========================================================================
    print("\n[SCENARIO 8] Extraction Types Comparison")
    print("-" * 80)
    
    extraction_types = ["markdown", "html", "text"]
    
    for ext_type in extraction_types:
        result = server.get(
            url="https://httpbin.org/html",
            extraction_type=ext_type,
            main_content_only=True
        )
        
        print(f"\nExtraction Type: {ext_type.upper()}")
        print(f"  Content preview: {result.content[0][:100]}...")
        print(f"  Use case: ", end="")
        
        if ext_type == "markdown":
            print("✓ BEST for AI (clean formatting, readable)")
        elif ext_type == "html":
            print("Raw HTML (debugging, structure analysis)")
        else:  # text
            print("Plain text (minimal processing)")
    
    print()
    
    # ===========================================================================
    # SCENARIO 9: MCP Tool Selection Guide
    # ===========================================================================
    print("\n[SCENARIO 9] Tool Selection Guide for AI")
    print("-" * 80)
    print()
    
    guide = [
        ("get", "Static HTML pages", "Fast", "Recommended first choice"),
        ("bulk_get", "Multiple static pages", "Fast", "Parallel requests"),
        ("fetch", "React/Vue/JS sites", "Slow", "Use when get fails"),
        ("bulk_fetch", "Multiple JS sites", "Medium", "Parallel JS rendering"),
        ("stealthy_fetch", "Cloudflare/WAF", "Very Slow", "Last resort"),
        ("bulk_stealthy_fetch", "Multiple protected", "Slow", "Parallel protection")
    ]
    
    for tool, use_case, speed, notes in guide:
        print(f"  {tool:20} | {use_case:25} | {speed:12} | {notes}")
    
    print()
    
    # ===========================================================================
    # SUMMARY
    # ===========================================================================
    print("\n[SUMMARY] Why MCP + Scrapling is Powerful for AI")
    print("-" * 80)
    print("""
✓ Content Narrowing: Use CSS selectors to reduce tokens 80%+
✓ Adaptive Recovery: Site redesigns don't break the scraper
✓ Protection Levels: From simple GET to high-protection anti-bot
✓ Bulk Operations: Scrape multiple URLs concurrently
✓ Format Control: Markdown (best for AI), HTML, or text
✓ Anti-Detection: Browser impersonation, fingerprint randomization
✓ Network Config: Proxy support, custom headers, cookies
✓ Structured Output: ResponseModel with status, content, URL

AI Workflow Example:
  1. "Get the latest tech news from TechCrunch"
     → Claude uses: get(url="techcrunch.com", css_selector="article", extraction_type="markdown")
  2. "Summarize the top 5 products"
     → Claude uses: bulk_get(urls=product_urls, css_selector=".product", extraction_type="markdown")
  3. "Extract data from this Cloudflare-protected site"
     → Claude uses: stealthy_fetch(url=protected_url, solve_cloudflare=True, extraction_type="markdown")

Running MCP Server:
  • CLI: scrapling mcp              (stdio mode for Claude Desktop)
  • CLI: scrapling mcp --http       (HTTP mode on localhost:8000)
  • Docker: scrapling mcp --http --host 0.0.0.0 --port 8000
    """)
    
    print("\n" + "=" * 80)
    print("MCP Integration Showcase Complete!")
    print("=" * 80)


async def main():
    """Run the demonstration"""
    await demonstrate_mcp_tools()


if __name__ == "__main__":
    asyncio.run(main())
