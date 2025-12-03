# Scrapling Library Analysis & Examples

Comprehensive analysis of the **Scrapling** web scraping library, demonstrating its superiority over other popular libraries and providing practical examples for all use cases.

## 📋 Contents

### 1. **SCRAPLING_ANALYSIS.md**
Complete comparative analysis of Scrapling vs:
- BeautifulSoup
- Scrapy
- Selenium
- Playwright
- And more...

**Key Takeaways:**
- ✅ **698x faster** than BeautifulSoup for text extraction
- ✅ **Unique adaptive scraping** feature (no other library has this!)
- ✅ **Best-in-class anti-bot protection** with Cloudflare bypass
- ✅ **Production-ready** with 92% test coverage
- ✅ **Free & open source** (BSD-3-Clause)

---

## 🔧 Example Scripts

All examples use the `quotes.toscrape.com` as a testing ground (or simulated data).

### Example 1: Basic HTTP Scraping (`examples_1_basic_scraping.py`)
Learn the fundamentals of Scrapling:
- Simple static website scraping
- Multiple selection methods (CSS, XPath, BeautifulSoup-style)
- Element navigation (parent, sibling, child)
- Structured data extraction
- Session management
- Attribute extraction
- Regex & text processing

**Run it:**
```bash
python examples_1_basic_scraping.py
```

**Key Topics:**
- `Fetcher.get()` for HTTP requests
- `page.css()` and `page.xpath()` for selection
- `page.find_all()` for BeautifulSoup compatibility
- Element relationships and navigation
- Data extraction patterns

---

### Example 2: Dynamic Website Scraping (`examples_2_dynamic_scraping.py`)
Master JavaScript-heavy websites:
- JavaScript rendering with DynamicFetcher
- Network control (disable images for speed)
- DynamicSession for multiple pages
- Waiting for elements
- Performance comparison (static vs dynamic)
- Error handling and timeouts
- XPath with dynamic content

**Run it:**
```bash
python examples_2_dynamic_scraping.py
```

**Key Topics:**
- `DynamicFetcher.fetch()` for JS rendering
- `network_idle=True` for reliable waiting
- `disable_resources=True` for faster loading
- `DynamicSession` for browser pool management
- Timeout handling

---

### Example 3: Adaptive Scraping (`examples_3_adaptive_scraping.py`)
**THE GAME-CHANGER** - Scrapling's unique feature:
- Adaptive scraping basics
- Selector configuration
- Simulating website structure changes
- Adaptive domain management
- Storage and matching algorithms
- Similarity metrics
- Best practices

**Run it:**
```bash
python examples_3_adaptive_scraping.py
```

**Key Topics:**
- `adaptive=True` mode activation
- `auto_save=True` for element tracking
- Element similarity algorithms
- Automatic element relocation
- Adaptive storage location
- Why other libraries break but Scrapling doesn't

---

### Example 4: Performance Benchmarks (`examples_4_performance.py`)
Prove why Scrapling is fastest:
- CSS/XPath selection benchmarking
- Text extraction performance
- Attribute access
- Method chaining
- Regex search
- JSON serialization (orjson)
- Comparison with official benchmarks
- Memory efficiency

**Run it:**
```bash
python examples_4_performance.py
```

**Key Results:**
- CSS Selection: ~1.92ms (fastest)
- Text Extraction: Same speed as Parsel/Scrapy
- 698x faster than BeautifulSoup
- Memory-efficient lazy loading

---

### Example 5: Advanced Features (`examples_5_advanced_features.py`)
Production-grade scraping:
- Session persistence & cookies
- Multiple fetcher types comparison
- Browser impersonation
- Proxy support
- Timeout handling
- **Async/await** operations
- Stealth mode & anti-bot bypass
- Cloudflare protection
- Global configuration
- Error recovery strategies
- Monitoring & logging
- Production best practices

**Run it:**
```bash
python examples_5_advanced_features.py
```

**Key Topics:**
- `FetcherSession` for cookie management
- Browser impersonation (Chrome, Firefox, Safari)
- `StealthyFetcher` for protected sites
- Async operations with `AsyncFetcher`
- Retry logic and fallback strategies
- Health monitoring and metrics

---

## 🚀 Quick Start

### Installation

```bash
# Core parser only (lightweight)
pip install scrapling

# With browser support (recommended)
pip install "scrapling[fetchers]"
scrapling install  # Install browsers

# Everything (shell + AI + fetchers)
pip install "scrapling[all]"
scrapling install

# Or Docker
docker pull pyd4vinci/scrapling
```

### First Script

```python
from scrapling.fetchers import Fetcher
from scrapling.parser import Selector

# Method 1: Fetch and parse
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text')
print(f"Found {len(quotes)} quotes")

# Method 2: Parse local HTML
html = "<html>...</html>"
page = Selector(html)
```

---

## 📊 Performance Comparison

| Library | Speed | Adaptive | Anti-bot | Ease | Type Hints |
|---------|-------|----------|----------|------|-----------|
| **Scrapling** | ⚡⚡⚡ | ✅ | ✅✅✅ | ⭐⭐⭐⭐⭐ | ✅ |
| BeautifulSoup | 🐢 | ❌ | ❌ | ⭐⭐⭐⭐⭐ | ❌ |
| Scrapy | ⚡⚡ | ❌ | ❌ | ⭐⭐⭐ | ⚠️ |
| Selenium | 🐢🐢 | ❌ | ⚠️ | ⭐⭐ | ❌ |
| Playwright | ⚡ | ❌ | ⚠️ | ⭐⭐⭐ | ✅ |

---

## 🎯 Use Case Guide

### Static Websites
```python
# Simple, fast HTTP requests
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://example.com')
data = page.css('.data')
```

### JavaScript-Heavy Sites
```python
# Full browser automation
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch('https://spa-app.com', network_idle=True)
data = page.css('.data')
```

### Protected Sites (Cloudflare, etc.)
```python
# Stealth mode with anti-bot bypass
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch(
    'https://protected-site.com',
    solve_cloudflare=True
)
data = page.css('.data')
```

### Large-Scale Scraping
```python
# Async for concurrent requests
import asyncio
from scrapling.fetchers import AsyncFetcher

async def scrape_urls(urls):
    tasks = [AsyncFetcher.get(url) for url in urls]
    pages = await asyncio.gather(*tasks)
    return pages

results = asyncio.run(scrape_urls(urls))
```

### Long-Term Projects (Website Changes)
```python
# Adaptive mode survives website changes
from scrapling.fetchers import Fetcher

Fetcher.configure(adaptive=True)
page = Fetcher.get('https://example.com')

# First run: saves element properties
element = page.css('.product', auto_save=True)

# Later: if website changes, still finds it!
element = page.css('.product', adaptive=True)
```

---

## 🔑 Key Features Summary

### 🔄 Adaptive Scraping
The **only** library with intelligent element tracking. Survives website redesigns automatically.

### ⚡ Performance
- **1.92ms** for text extraction (fastest)
- **5.5x faster** than alternatives
- Optimized lxml parsing engine

### 🛡️ Stealth & Anti-Bot
- Fingerprint spoofing
- Cloudflare bypass
- HTTP3 support
- Real TLS impersonation

### 📦 Complete Fetching
- 3 fetchers built-in (HTTP, Dynamic, Stealth)
- Session management
- Async/await support
- Proxy support

### 🎯 Rich Selection
- CSS selectors
- XPath
- BeautifulSoup-style
- Text search
- Regex search
- Custom filtering

### 💎 Production-Ready
- 92% test coverage
- 100% type hints
- Error handling
- Docker image included

---

## 📚 Running the Examples

```bash
# Run all examples
python examples_1_basic_scraping.py
python examples_2_dynamic_scraping.py
python examples_3_adaptive_scraping.py
python examples_4_performance.py
python examples_5_advanced_features.py

# Or selectively
python examples_1_basic_scraping.py  # Start here!
```

---

## 🔗 Resources

- **Official Docs**: https://scrapling.readthedocs.io/
- **GitHub**: https://github.com/D4Vinci/Scrapling
- **PyPI**: https://pypi.org/project/scrapling/
- **Discord**: https://discord.gg/EMgGbDceNQ
- **Twitter**: https://twitter.com/Scrapling_dev

---

## 💡 Why Scrapling is Superior

### Problem: Websites Change
- BeautifulSoup ❌ → Selectors break
- Scrapy ❌ → Need manual updates
- Scrapling ✅ → Automatically adapts!

### Problem: Anti-Bot Detection
- Selenium ⚠️ → Easy to detect
- Playwright ⚠️ → Limited options
- Scrapling ✅ → Best fingerprint spoofing

### Problem: Performance
- BeautifulSoup 🐢 → 698x slower
- Scrapy ⚡ → Close to Scrapling
- Scrapling ⚡⚡ → Lightning fast

### Problem: Easy to Use
- Scrapy 📚 → Steep learning curve
- BeautifulSoup ⭐⭐⭐⭐⭐ → Simple
- Scrapling ⭐⭐⭐⭐⭐ → Simple + Powerful

---

## 📝 License & Credits

- **Scrapling**: BSD-3-Clause License
- **Created by**: Karim Shoair
- **Analysis**: Comprehensive comparison with 5+ libraries

---

## 🎓 Learning Path

1. **Start**: `examples_1_basic_scraping.py` - Learn the basics
2. **Progress**: `examples_2_dynamic_scraping.py` - Master JS rendering
3. **Master**: `examples_3_adaptive_scraping.py` - Learn Scrapling's superpower
4. **Optimize**: `examples_4_performance.py` - Understand performance
5. **Advanced**: `examples_5_advanced_features.py` - Production techniques

---

## 🎯 Next Steps

1. Install Scrapling: `pip install scrapling[all]`
2. Run the examples: `python examples_1_basic_scraping.py`
3. Read `SCRAPLING_ANALYSIS.md` for deep dive comparison
4. Check official documentation
5. Build your first scraper!

---

**Happy Scraping! 🚀**
