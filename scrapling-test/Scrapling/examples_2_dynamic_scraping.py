"""
Example 2: Dynamic Website Scraping with JavaScript Rendering
==============================================================

This example shows how to scrape websites that require JavaScript
execution to render content dynamically.

Use Case: Scraping SPAs (Single Page Applications) and JS-heavy sites
"""

from scrapling.fetchers import DynamicFetcher, DynamicSession


def example_javascript_rendering():
    """Fetch and scrape a page that requires JavaScript execution."""
    print("=" * 70)
    print("Example 2.1: JavaScript Rendering with DynamicFetcher")
    print("=" * 70)
    
    print("\n⏳ Fetching JavaScript-heavy page (this will take a moment)...")
    
    # DynamicFetcher uses Playwright to render JavaScript
    page = DynamicFetcher.fetch(
        'https://quotes.toscrape.com/js/',  # JS-based quotes site
        headless=True,
        timeout=30000,  # 30 seconds
        network_idle=True  # Wait for network to be idle
    )
    
    if page.status == 200:
        print(f"✅ Successfully fetched dynamic page (Status: {page.status})\n")
        
        # After JS execution, we can scrape normally
        quotes = page.css('.quote')
        print(f"📊 Found {len(quotes)} quotes after JS rendering\n")
        
        # Extract data
        for i, quote in enumerate(quotes[:3], 1):
            text = quote.css('.text::text').get()
            author = quote.css('.author::text').get()
            print(f"Quote {i}:")
            print(f"  {text}")
            print(f"  — {author}\n")
    else:
        print(f"❌ Failed to fetch page (Status: {page.status})")


def example_dynamic_with_network_control():
    """Control network behavior for faster scraping."""
    print("\n" + "=" * 70)
    print("Example 2.2: Network Control & Performance Optimization")
    print("=" * 70)
    
    print("\n🚀 Fetching with resource optimization...")
    
    # Disable image/media loading for faster scraping
    page = DynamicFetcher.fetch(
        'https://quotes.toscrape.com/js/',
        headless=True,
        disable_resources=True,  # Don't load images/stylesheets
        network_idle=True,
        timeout=20000
    )
    
    print(f"✅ Page loaded without images/media (Status: {page.status})")
    print(f"📊 Found {len(page.css('.quote'))} quotes")
    print(f"💾 Memory & bandwidth saved by skipping resources\n")


def example_dynamic_session():
    """Use DynamicSession for multiple page renders."""
    print("\n" + "=" * 70)
    print("Example 2.3: DynamicSession for Multiple Pages")
    print("=" * 70)
    
    # Sessions keep browser alive for multiple requests
    print("\n🌐 Opening browser session...\n")
    
    with DynamicSession(headless=True, max_pages=3) as session:
        print("Browser session opened with max 3 concurrent pages")
        print("(This keeps the browser alive, reducing startup overhead)\n")
        
        # Fetch multiple pages
        pages = []
        urls = [
            'https://quotes.toscrape.com/js/',
            'https://quotes.toscrape.com/js/page/2/',
        ]
        
        for url in urls:
            try:
                page = session.fetch(url, timeout=15000)
                pages.append((url, page))
                print(f"✅ Fetched: {url}")
                print(f"   Status: {page.status}")
                print(f"   Quotes: {len(page.css('.quote'))}\n")
            except Exception as e:
                print(f"❌ Error fetching {url}: {e}\n")
        
        # Show browser pool stats
        try:
            stats = session.get_pool_stats()
            print(f"🔄 Browser Pool Stats: {stats}")
        except:
            pass


def example_waiting_for_elements():
    """Wait for specific elements to appear after JS execution."""
    print("\n" + "=" * 70)
    print("Example 2.4: Waiting for Elements")
    print("=" * 70)
    
    print("\n⏳ Fetching page and waiting for elements to render...\n")
    
    page = DynamicFetcher.fetch(
        'https://quotes.toscrape.com/js/',
        headless=True,
        network_idle=True,
        timeout=30000
    )
    
    # After the page loads, we can directly query for elements
    print("Page fully rendered with JavaScript")
    
    # Get all quotes
    quotes = page.css('.quote')
    print(f"✅ Found {len(quotes)} quotes\n")
    
    # Extract detailed information
    print("📋 First 3 quotes with full details:\n")
    for i, quote in enumerate(quotes[:3], 1):
        text = quote.css('.text::text').get()
        author = quote.css('.author::text').get()
        tags = quote.css('.tag-item::text').getall()
        
        print(f"Quote {i}:")
        print(f"  Text: {text[:60]}...")
        print(f"  Author: {author}")
        print(f"  Tags: {', '.join(tags)}")
        print()


def example_load_dom_false():
    """Fetch raw HTML without waiting for DOM rendering."""
    print("\n" + "=" * 70)
    print("Example 2.5: Fetch HTML Without DOM Wait")
    print("=" * 70)
    
    print("\n⚡ Fetching page without waiting for full DOM rendering...\n")
    
    page = DynamicFetcher.fetch(
        'https://quotes.toscrape.com/js/',
        headless=True,
        load_dom=False,  # Don't wait for DOM
        timeout=10000
    )
    
    print(f"✅ Page loaded (Status: {page.status})")
    quotes = page.css('.quote')
    print(f"📊 Quotes found: {len(quotes)}")
    print(f"(Note: May be less than with network_idle=True)\n")


def example_comparison_static_vs_dynamic():
    """Compare static vs dynamic fetching performance."""
    print("\n" + "=" * 70)
    print("Example 2.6: Static vs Dynamic Fetching Comparison")
    print("=" * 70)
    
    import time
    
    print("\n⏱️ Comparing fetch methods...\n")
    
    # Static fetch (HTTP only)
    print("1️⃣ Static Fetcher (HTTP only):")
    start = time.time()
    static_page = None
    try:
        from scrapling.fetchers import Fetcher
        static_page = Fetcher.get('https://quotes.toscrape.com/')
        static_time = time.time() - start
        static_quotes = len(static_page.css('.quote'))
        print(f"   Time: {static_time:.2f}s")
        print(f"   Quotes: {static_quotes}")
    except Exception as e:
        print(f"   Error: {e}")
    
    # Dynamic fetch (with JavaScript rendering)
    print("\n2️⃣ Dynamic Fetcher (with JS rendering):")
    start = time.time()
    dynamic_page = DynamicFetcher.fetch(
        'https://quotes.toscrape.com/js/',
        headless=True,
        network_idle=True,
        timeout=30000
    )
    dynamic_time = time.time() - start
    dynamic_quotes = len(dynamic_page.css('.quote'))
    print(f"   Time: {dynamic_time:.2f}s")
    print(f"   Quotes: {dynamic_quotes}")
    
    if static_page:
        print(f"\n📊 Comparison:")
        print(f"   Dynamic is ~{dynamic_time/static_time:.1f}x slower")
        print(f"   But necessary for JavaScript-rendered content")


def example_error_handling():
    """Handle errors gracefully when fetching dynamic pages."""
    print("\n" + "=" * 70)
    print("Example 2.7: Error Handling & Timeouts")
    print("=" * 70)
    
    print("\n🛡️ Handling errors gracefully...\n")
    
    try:
        # Short timeout to demonstrate error handling
        page = DynamicFetcher.fetch(
            'https://quotes.toscrape.com/js/',
            headless=True,
            timeout=2000  # 2 seconds - likely too short
        )
        print(f"✅ Fetched: {page.status}")
    except Exception as e:
        print(f"⚠️ Caught error (as expected with short timeout):")
        print(f"   Error type: {type(e).__name__}")
        print(f"   Message: {str(e)[:100]}...")
        print(f"\n💡 In production, use try/except to handle timeouts")


def example_xpath_with_dynamic():
    """Use XPath selectors with dynamic content."""
    print("\n" + "=" * 70)
    print("Example 2.8: XPath Selectors with Dynamic Content")
    print("=" * 70)
    
    print("\n📍 Using XPath to select from rendered content...\n")
    
    page = DynamicFetcher.fetch(
        'https://quotes.toscrape.com/js/',
        headless=True,
        network_idle=True,
        timeout=30000
    )
    
    # XPath selectors work the same way
    print("1️⃣ Get all quote texts with XPath:")
    texts = page.xpath('//span[@class="text"]/text()')
    print(f"   Found {len(texts)} texts")
    print(f"   First: {texts.get()[:60]}...\n")
    
    print("2️⃣ Get quotes by author with XPath:")
    author_elements = page.xpath('//small[contains(@class, "author")]')
    print(f"   Found {len(author_elements)} authors")
    for author in author_elements.getall()[:3]:
        name = author.xpath('./text()').get()
        print(f"   - {name}\n")


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " SCRAPLING EXAMPLE 2: DYNAMIC SCRAPING ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        example_javascript_rendering()
        example_dynamic_with_network_control()
        example_dynamic_session()
        example_waiting_for_elements()
        example_load_dom_false()
        example_comparison_static_vs_dynamic()
        example_error_handling()
        example_xpath_with_dynamic()
        
        print("\n" + "=" * 70)
        print("✅ All dynamic examples completed!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
