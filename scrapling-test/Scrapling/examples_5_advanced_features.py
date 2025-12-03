"""
Example 5: Advanced Features - Sessions, Async, Stealth & More
===============================================================

This example demonstrates advanced Scrapling features including:
- Session management for persistent state
- Async/await operations
- Stealth mode and anti-bot bypassing
- Multiple fetcher types with different capabilities

Use Case: Production-grade scrapers with advanced requirements
"""

import asyncio
from scrapling.fetchers import (
    Fetcher, FetcherSession,
    DynamicFetcher, DynamicSession,
    StealthyFetcher, StealthySession,
    AsyncFetcher, AsyncDynamicSession, AsyncStealthySession
)


# ============================================================================
# PART 1: SESSION MANAGEMENT
# ============================================================================

def example_session_persistence():
    """Demonstrate session persistence with cookies."""
    print("=" * 70)
    print("Example 5.1: Session Persistence & Cookie Management")
    print("=" * 70)
    
    print("\n🔐 FetcherSession maintains state across requests:\n")
    
    with FetcherSession() as session:
        # First request - establishes session
        print("1️⃣ First request (login page):")
        page1 = session.get('https://quotes.toscrape.com/')
        print(f"   Status: {page1.status}")
        print(f"   URL: {page1.url}")
        
        # Cookies are now stored in session
        print(f"\n🍪 Session has stored cookies")
        
        # Second request - uses same cookies
        print(f"\n2️⃣ Second request (authenticated page):")
        page2 = session.get('https://quotes.toscrape.com/page/2/')
        print(f"   Status: {page2.status}")
        print(f"   Same session used (cookies preserved)")
        
        # All requests share connection pool
        print(f"\n3️⃣ Benefits:")
        print(f"   ✅ Cookies persist across requests")
        print(f"   ✅ Connection pooling (faster)")
        print(f"   ✅ Headers preserved")
        print(f"   ✅ Session state maintained")


def example_multiple_fetchers():
    """Use different fetchers for different purposes."""
    print("\n" + "=" * 70)
    print("Example 5.2: Multiple Fetcher Types")
    print("=" * 70)
    
    print("\n🔄 Scrapling provides 3 fetcher types:\n")
    
    print("1️⃣ Fetcher - Fast HTTP requests:")
    print("   • Uses curl_cffi for TLS fingerprinting")
    print("   • Impersonate Chrome/Firefox")
    print("   • HTTP3 support")
    print("   • Fastest option")
    print("   • Best for: Static sites, APIs\n")
    
    try:
        page = Fetcher.get('https://quotes.toscrape.com/')
        print(f"   ✅ Fetched: {page.status}")
    except Exception as e:
        print(f"   ℹ️  Note: {type(e).__name__}")
    
    print("\n2️⃣ DynamicFetcher - Full browser automation:")
    print("   • Uses Playwright + Chromium")
    print("   • JavaScript execution")
    print("   • Full DOM rendering")
    print("   • Network control")
    print("   • Best for: SPAs, JS-heavy sites\n")
    
    print("\n3️⃣ StealthyFetcher - Anti-bot bypassing:")
    print("   • Custom Firefox (modified)")
    print("   • Fingerprint spoofing")
    print("   • Cloudflare Turnstile bypass")
    print("   • Most stealthy option")
    print("   • Best for: Protected sites\n")


def example_session_impersonation():
    """Use session with browser impersonation."""
    print("\n" + "=" * 70)
    print("Example 5.3: Browser Impersonation with Session")
    print("=" * 70)
    
    print("\n🎭 Impersonating different browsers:\n")
    
    print("1️⃣ Impersonate Chrome:")
    with FetcherSession(impersonate='chrome') as session:
        page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
        print(f"   ✅ Fetched as Chrome")
        print(f"   Status: {page.status}")
    
    print("\n2️⃣ Impersonate Firefox:")
    with FetcherSession(impersonate='firefox') as session:
        page = session.get('https://quotes.toscrape.com/')
        print(f"   ✅ Fetched as Firefox")
        print(f"   Status: {page.status}")
    
    print("\n3️⃣ Latest versions:")
    print("   • chrome (latest)")
    print("   • firefox (latest)")
    print("   • safari (latest)")
    print("   • Also supports specific versions like 'chrome119'")
    
    print("\n4️⃣ Benefits of impersonation:")
    print("   ✅ Real browser TLS fingerprint")
    print("   ✅ Real browser headers")
    print("   ✅ Bypasses simple bot detection")
    print("   ✅ HTTP3 support for stealth")


def example_proxy_support():
    """Use proxies with sessions."""
    print("\n" + "=" * 70)
    print("Example 5.4: Proxy Support")
    print("=" * 70)
    
    print("\n🌐 Proxy configuration:\n")
    
    print("1️⃣ Direct proxy usage:")
    print("""
    with FetcherSession(proxy='http://proxy.example.com:8080') as session:
        page = session.get('https://example.com')
    """)
    
    print("2️⃣ With authentication:")
    print("""
    with FetcherSession(proxy='http://user:pass@proxy.com:8080') as session:
        page = session.get('https://example.com')
    """)
    
    print("3️⃣ With DynamicFetcher:")
    print("""
    with DynamicSession(proxy='http://proxy.example.com:8080') as session:
        page = session.fetch('https://example.com')
    """)
    
    print("\n💡 Tips:")
    print("   • Use SOCKS5 for better privacy: socks5://proxy:port")
    print("   • Rotate proxies by creating new sessions")
    print("   • Test proxy connection before scraping")


def example_timeout_handling():
    """Handle timeouts and connection errors."""
    print("\n" + "=" * 70)
    print("Example 5.5: Timeout & Error Handling")
    print("=" * 70)
    
    print("\n⏱️  Timeout management:\n")
    
    print("1️⃣ Global timeout:")
    print("""
    with FetcherSession(timeout=30) as session:
        page = session.get('https://slow-site.com')
    """)
    
    print("2️⃣ Per-request timeout:")
    print("""
    with FetcherSession() as session:
        page = session.get('https://example.com', timeout=10)
    """)
    
    print("3️⃣ Error handling:")
    print("""
    try:
        page = Fetcher.get('https://example.com', timeout=5)
    except TimeoutError:
        print('Request timed out')
    except ConnectionError:
        print('Connection failed')
    except Exception as e:
        print(f'Error: {e}')
    """)


# ============================================================================
# PART 2: ASYNC OPERATIONS
# ============================================================================

async def example_async_fetching():
    """Demonstrate async fetching."""
    print("\n" + "=" * 70)
    print("Example 5.6: Async Fetching")
    print("=" * 70)
    
    print("\n⚡ Async operations for concurrent requests:\n")
    
    print("1️⃣ Single async request:")
    print("""
    import asyncio
    from scrapling.fetchers import AsyncFetcher
    
    async def fetch_one():
        page = await AsyncFetcher.get('https://example.com')
        return page
    
    page = asyncio.run(fetch_one())
    """)
    
    print("2️⃣ Multiple concurrent requests:")
    print("""
    async def fetch_multiple():
        urls = [
            'https://quotes.toscrape.com/',
            'https://quotes.toscrape.com/page/2/',
            'https://quotes.toscrape.com/page/3/',
        ]
        
        tasks = [AsyncFetcher.get(url) for url in urls]
        pages = await asyncio.gather(*tasks)
        return pages
    
    pages = asyncio.run(fetch_multiple())
    print(f'Fetched {len(pages)} pages concurrently!')
    """)
    
    print("3️⃣ Async session:")
    print("""
    async def fetch_with_session():
        async with AsyncFetcher.session() as session:
            pages = []
            for url in urls:
                page = await session.get(url)
                pages.append(page)
            return pages
    """)
    
    # Actual async example would be:
    print("\n✅ Async benefits:")
    print("   • Fetch multiple pages simultaneously")
    print("   • 10x faster for I/O-bound operations")
    print("   • Lower memory usage than threading")
    print("   • Perfect for scraping many URLs")


# ============================================================================
# PART 3: STEALTH & ANTI-BOT
# ============================================================================

def example_stealth_mode():
    """Demonstrate stealth features."""
    print("\n" + "=" * 70)
    print("Example 5.7: Stealth Mode & Anti-Bot Bypass")
    print("=" * 70)
    
    print("\n🛡️ Advanced stealth capabilities:\n")
    
    print("1️⃣ StealthyFetcher - Modified Firefox:")
    print("   • Custom Firefox build with anti-detection")
    print("   • Real fingerprint")
    print("   • Passes bot detection tests")
    
    print("""
    page = StealthyFetcher.fetch(
        'https://protected-site.com',
        headless=True,
        network_idle=True
    )
    """)
    
    print("\n2️⃣ Cloudflare protection bypass:")
    print("   • Automatic Turnstile CAPTCHA solving")
    print("   • Interstitial page bypass")
    
    print("""
    page = StealthyFetcher.fetch(
        'https://cloudflare-protected.com',
        headless=True,
        solve_cloudflare=True
    )
    """)
    
    print("\n3️⃣ Fingerprint components spoofed:")
    print("   ✅ User-Agent")
    print("   ✅ Accept-Language")
    print("   ✅ WebGL vendor/renderer")
    print("   ✅ Canvas fingerprint")
    print("   ✅ Timezone")
    print("   ✅ Geolocation")
    print("   ✅ CPU cores")
    print("   ✅ Memory")
    
    print("\n4️⃣ Detection prevention:")
    print("   ✅ No 'headless' browser detection")
    print("   ✅ Real chrome processes")
    print("   ✅ Realistic mouse/keyboard patterns")
    print("   ✅ Timing variations")


def example_stealthy_session():
    """Use StealthySession for persistent stealthy requests."""
    print("\n" + "=" * 70)
    print("Example 5.8: StealthySession Management")
    print("=" * 70)
    
    print("\n🔐 StealthySession for persistent anti-bot protection:\n")
    
    print("1️⃣ Basic usage:")
    print("""
    with StealthySession(headless=True) as session:
        page = session.fetch('https://protected-site.com')
        # Browser stays open for next request
        page2 = session.fetch('https://protected-site.com/page2')
    """)
    
    print("2️⃣ With max_pages (tab pooling):")
    print("""
    with StealthySession(
        headless=True,
        max_pages=5,  # Max 5 concurrent tabs
        solve_cloudflare=True
    ) as session:
        # Fetches use tab pool
        page1 = session.fetch(url1)
        page2 = session.fetch(url2)
    """)
    
    print("3️⃣ Pool statistics:")
    print("""
    with StealthySession() as session:
        page = session.fetch(url)
        stats = session.get_pool_stats()
        print(stats)  # {'busy': 1, 'free': 4, 'error': 0}
    """)


# ============================================================================
# PART 4: ADVANCED CONFIGURATION
# ============================================================================

def example_global_configuration():
    """Configure Scrapling globally."""
    print("\n" + "=" * 70)
    print("Example 5.9: Global Configuration")
    print("=" * 70)
    
    print("\n⚙️ Configure all fetchers at once:\n")
    
    print("1️⃣ Enable adaptive globally:")
    print("""
    Fetcher.configure(adaptive=True)
    DynamicFetcher.configure(adaptive=True)
    StealthyFetcher.configure(adaptive=True)
    
    # Now all requests use adaptive mode
    page = Fetcher.get(url)  # Has adaptive
    """)
    
    print("\n2️⃣ Default impersonation:")
    print("""
    Fetcher.configure(impersonate='chrome')
    # All Fetcher requests now impersonate Chrome
    """)
    
    print("\n3️⃣ Default timeout:")
    print("""
    Fetcher.configure(timeout=30)
    DynamicFetcher.configure(timeout=60000)  # 60 seconds
    """)
    
    print("\n4️⃣ Adaptive domain:")
    print("""
    # Use same adaptive data for archive.org and example.com
    Fetcher.configure(adaptive_domain='example.com')
    """)


def example_error_recovery():
    """Implement error recovery strategies."""
    print("\n" + "=" * 70)
    print("Example 5.10: Error Recovery & Retries")
    print("=" * 70)
    
    print("\n🔄 Implementing robust error handling:\n")
    
    print("1️⃣ Simple retry logic:")
    print("""
    def fetch_with_retry(url, max_retries=3):
        for attempt in range(max_retries):
            try:
                page = Fetcher.get(url, timeout=30)
                return page
            except TimeoutError:
                if attempt < max_retries - 1:
                    print(f'Timeout, retrying... ({attempt+1}/{max_retries})')
                    continue
            except Exception as e:
                print(f'Error: {e}')
                return None
        return None
    """)
    
    print("2️⃣ Exponential backoff:")
    print("""
    import time
    
    def fetch_with_backoff(url, max_retries=3):
        for attempt in range(max_retries):
            try:
                page = Fetcher.get(url)
                return page
            except Exception as e:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1, 2, 4 seconds
                    print(f'Retrying in {wait_time}s...')
                    time.sleep(wait_time)
        return None
    """)
    
    print("3️⃣ Fallback fetchers:")
    print("""
    def fetch_with_fallback(url):
        # Try fast HTTP first
        try:
            page = Fetcher.get(url, timeout=10)
            return page
        except:
            pass
        
        # Fall back to dynamic if needed
        try:
            page = DynamicFetcher.fetch(url)
            return page
        except:
            pass
        
        # Last resort: stealth
        try:
            page = StealthyFetcher.fetch(url)
            return page
        except:
            return None
    """)


def example_monitoring_and_logging():
    """Add monitoring and logging."""
    print("\n" + "=" * 70)
    print("Example 5.11: Monitoring & Logging")
    print("=" * 70)
    
    print("\n📊 Production scraper monitoring:\n")
    
    print("1️⃣ Simple logging:")
    print("""
    import logging
    
    logger = logging.getLogger('scraper')
    
    def scrape_with_logging(url):
        logger.info(f'Fetching: {url}')
        try:
            page = Fetcher.get(url)
            logger.info(f'Success: {page.status}')
            return page
        except Exception as e:
            logger.error(f'Failed: {e}')
            return None
    """)
    
    print("2️⃣ Metrics collection:")
    print("""
    from collections import defaultdict
    import time
    
    metrics = {
        'total_requests': 0,
        'successful': 0,
        'failed': 0,
        'avg_time': 0,
        'times': [],
    }
    
    def scrape_tracked(url):
        metrics['total_requests'] += 1
        start = time.time()
        
        try:
            page = Fetcher.get(url)
            metrics['successful'] += 1
            return page
        except:
            metrics['failed'] += 1
            return None
        finally:
            elapsed = time.time() - start
            metrics['times'].append(elapsed)
            metrics['avg_time'] = sum(metrics['times']) / len(metrics['times'])
    """)
    
    print("3️⃣ Health checks:")
    print("""
    def health_check(urls):
        results = {}
        for url in urls:
            try:
                page = Fetcher.get(url, timeout=5)
                results[url] = 'OK' if page.status == 200 else 'ERROR'
            except Exception as e:
                results[url] = f'FAIL: {type(e).__name__}'
        return results
    """)


def example_best_practices():
    """Share best practices for production scrapers."""
    print("\n" + "=" * 70)
    print("Example 5.12: Production Best Practices")
    print("=" * 70)
    
    practices = [
        ("Use sessions", "Reuse connections, save cookies"),
        ("Set timeouts", "Prevent hanging requests"),
        ("Handle errors gracefully", "Try/except everything"),
        ("Implement retries", "Exponential backoff"),
        ("Use fallback fetchers", "HTTP → Dynamic → Stealth"),
        ("Log everything", "Debug issues later"),
        ("Monitor performance", "Track success rate"),
        ("Respect robots.txt", "Check before scraping"),
        ("Use User-Agent", "Identify your scraper"),
        ("Rate limit requests", "Don't hammer servers"),
        ("Cache responses", "Avoid redundant requests"),
        ("Use async for bulk scraping", "Concurrent requests"),
        ("Rotate proxies", "Avoid blocking"),
        ("Test selectors", "Verify before deployment"),
        ("Version your code", "Git for reproducibility"),
    ]
    
    print("\n✅ BEST PRACTICES:\n")
    for i, (practice, reason) in enumerate(practices, 1):
        print(f"{i:2}. {practice:30} → {reason}")


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " SCRAPLING EXAMPLE 5: ADVANCED FEATURES ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        # Session management
        example_session_persistence()
        example_multiple_fetchers()
        example_session_impersonation()
        example_proxy_support()
        example_timeout_handling()
        
        # Async
        asyncio.run(example_async_fetching())
        
        # Stealth & anti-bot
        example_stealth_mode()
        example_stealthy_session()
        
        # Configuration & best practices
        example_global_configuration()
        example_error_recovery()
        example_monitoring_and_logging()
        example_best_practices()
        
        print("\n" + "=" * 70)
        print("✅ All advanced examples completed!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
