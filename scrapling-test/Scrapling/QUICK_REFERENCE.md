# Scrapling Quick Reference Guide

## Installation

```bash
# Minimal (parser only)
pip install scrapling

# Recommended (with fetchers)
pip install "scrapling[fetchers]"
scrapling install

# Complete
pip install "scrapling[all]"
scrapling install
```

---

## Core Concepts

### 1. Selector - Parsing Engine
```python
from scrapling.parser import Selector

html = "<html>...</html>"
page = Selector(html, adaptive=True)
```

### 2. Fetcher - HTTP Requests
```python
from scrapling.fetchers import Fetcher

page = Fetcher.get('https://example.com')
```

### 3. DynamicFetcher - Browser Automation
```python
from scrapling.fetchers import DynamicFetcher

page = DynamicFetcher.fetch('https://spa.com')
```

### 4. StealthyFetcher - Anti-Bot Bypass
```python
from scrapling.fetchers import StealthyFetcher

page = StealthyFetcher.fetch('https://protected.com', solve_cloudflare=True)
```

---

## Selection Methods

### CSS Selectors
```python
page.css('.product')              # All products
page.css_first('.product')         # First product only
page.css('.price::text')           # Text extraction
page.css('.price::text').get()     # Get first
page.css('.price::text').getall()  # Get all
```

### XPath
```python
page.xpath('//div[@class="product"]')
page.xpath('//span/text()')
page.xpath_first('//div[@class="product"]')
```

### BeautifulSoup Style
```python
page.find_all('div', class_='product')
page.find_all('div', {'class': 'product'})
page.find('div', class_='product')
```

### Text Search
```python
page.find_by_text('sale', tag='span')
page.find_by_text(lambda x: 'sale' in x.lower())
```

### Regex
```python
import re
page.regex_search(r'Price: \$(\d+\.\d+)')
```

---

## Navigation

### Element Relationships
```python
element = page.css_first('.product')

element.parent           # Parent element
element.next_sibling     # Next sibling
element.previous_sibling # Previous sibling
element.get_siblings()   # All siblings
element.below_elements() # Elements below
```

### Chaining Selectors
```python
page.css('.container').css('.product').css('.price::text')
```

### Traversal
```python
element.xpath('../..')  # Go up
element.css('::parent') # Parent
element.css('::child')  # Child
```

---

## Element Operations

### Get Text
```python
element.text           # All text
element.text.strip()   # Trimmed
element.text.split()   # Split by whitespace
```

### Get Attributes
```python
element.get('href')              # Single attribute
element.get('class', 'default')  # With default
element.attrs                    # All attributes
element.attr_dict                # Attribute dictionary
```

### Element Info
```python
element.name        # Tag name
element.tag         # Tag name (same as .name)
element.html        # Outer HTML
element.inner_html  # Inner HTML
element.text        # All text
```

---

## Session Management

### HTTP Session
```python
from scrapling.fetchers import FetcherSession

with FetcherSession() as session:
    page1 = session.get('https://example.com')
    page2 = session.get('https://example.com/page2')
    # Cookies maintained between requests
```

### Dynamic Session
```python
from scrapling.fetchers import DynamicSession

with DynamicSession(headless=True, max_pages=3) as session:
    page1 = session.fetch(url1)
    page2 = session.fetch(url2)
    # Browser pool maintained
```

### Stealth Session
```python
from scrapling.fetchers import StealthySession

with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch(url)
```

---

## Adaptive Scraping

### Enable Adaptive
```python
# Global
Fetcher.configure(adaptive=True)

# Per fetcher
page = Fetcher.get(url, adaptive=True)

# Per selector
element = page.css('.product', adaptive=True)
```

### Save Properties
```python
element = page.css_first('.product', auto_save=True)
# Properties saved for later adaptation
```

### Configure Domain
```python
Fetcher.configure(adaptive_domain='example.com')
# Use same adaptive data for related domains
```

---

## Async Operations

### Basic Async
```python
import asyncio
from scrapling.fetchers import AsyncFetcher

async def main():
    page = await AsyncFetcher.get('https://example.com')
    return page

page = asyncio.run(main())
```

### Concurrent Requests
```python
async def fetch_multiple(urls):
    tasks = [AsyncFetcher.get(url) for url in urls]
    pages = await asyncio.gather(*tasks)
    return pages

pages = asyncio.run(fetch_multiple(urls))
```

### Async Session
```python
async with AsyncFetcher.session() as session:
    page = await session.get(url)
```

---

## Advanced Options

### Fetcher Options
```python
page = Fetcher.get(
    url,
    timeout=30,                    # Seconds
    impersonate='chrome',          # Browser to impersonate
    stealthy_headers=True,         # Use stealthy headers
    http3=True,                    # Use HTTP/3
    proxy='http://proxy:8080',     # Proxy URL
    adaptive=True,                 # Enable adaptive
)
```

### DynamicFetcher Options
```python
page = DynamicFetcher.fetch(
    url,
    headless=True,                 # Headless mode
    network_idle=True,             # Wait for network idle
    load_dom=True,                 # Wait for DOM
    disable_resources=True,        # Don't load images
    timeout=30000,                 # Milliseconds
    max_pages=5,                   # With session
)
```

### StealthyFetcher Options
```python
page = StealthyFetcher.fetch(
    url,
    headless=True,
    solve_cloudflare=True,         # Auto-solve CAPTCHA
    google_search=False,           # No Google search
    timeout=30000,
)
```

---

## Data Extraction Patterns

### Single Element
```python
element = page.css_first('.product')
name = element.css('.name::text').get()
price = element.css('.price::text').get()
```

### Multiple Elements
```python
products = page.css('.product')
for product in products:
    name = product.css('.name::text').get()
    price = product.css('.price::text').get()
    print(f"{name}: {price}")
```

### Structured Data
```python
data = []
for item in page.css('.item'):
    data.append({
        'title': item.css('.title::text').get(),
        'price': item.css('.price::text').get(),
        'link': item.css('a::attr(href)').get(),
        'tags': item.css('.tag::text').getall(),
    })
```

### Nested Selection
```python
for container in page.css('.container'):
    header = container.css_first('.header')
    body = container.css_first('.body')
    
    title = header.css('.title::text').get()
    content = body.css('.text::text').getall()
```

---

## Error Handling

### Try-Except
```python
try:
    page = Fetcher.get(url)
    data = page.css('.data')
except TimeoutError:
    print('Timeout')
except ConnectionError:
    print('Connection failed')
except Exception as e:
    print(f'Error: {e}')
```

### Retry Logic
```python
def fetch_with_retry(url, max_retries=3):
    for attempt in range(max_retries):
        try:
            return Fetcher.get(url)
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)
            else:
                raise
```

### Fallback Fetchers
```python
page = None
try:
    page = Fetcher.get(url, timeout=10)
except:
    try:
        page = DynamicFetcher.fetch(url)
    except:
        page = StealthyFetcher.fetch(url)
```

---

## Configuration

### Global Config
```python
Fetcher.configure(
    timeout=30,
    impersonate='chrome',
    adaptive=True,
)

DynamicFetcher.configure(
    timeout=60000,
    headless=True,
)

StealthyFetcher.configure(
    solve_cloudflare=True,
)
```

---

## Performance Tips

| Tip | Benefit |
|-----|---------|
| Use `css_first()` over `css()[0]` | Faster for first element |
| Use `::text` pseudo-element | Direct text extraction |
| Use `getall()` over loop `.get()` | More efficient |
| `disable_resources=True` | Faster JS rendering |
| Use sessions | Connection pooling |
| Specific selectors | Less parsing |
| Cache selectors | Avoid re-parsing |
| Use async for bulk scraping | Concurrent requests |

---

## Common Patterns

### Scrape Multiple Pages
```python
for page_num in range(1, 4):
    url = f'https://example.com/page/{page_num}/'
    page = Fetcher.get(url)
    
    for item in page.css('.item'):
        title = item.css('.title::text').get()
        print(title)
```

### Pagination with Next Button
```python
page = Fetcher.get('https://example.com')

while True:
    # Process current page
    for item in page.css('.item'):
        print(item.css('.title::text').get())
    
    # Find next button
    next_btn = page.css_first('a.next')
    if not next_btn:
        break
    
    # Get next URL
    next_url = next_btn.get('href')
    page = Fetcher.get(next_url)
```

### Extract Links
```python
links = []
for link in page.css('a'):
    href = link.get('href')
    text = link.text
    links.append({'url': href, 'text': text})
```

### Extract Tables
```python
rows = []
for tr in page.css('table tbody tr'):
    cells = tr.css('td::text').getall()
    rows.append(cells)
```

---

## Debugging

### Print HTML
```python
print(page.html)        # Full HTML
print(element.html)     # Element HTML
```

### Interactive Shell
```bash
scrapling shell
# Then use page object interactively
```

### CLI Extraction
```bash
scrapling extract get 'https://example.com' output.md
scrapling extract get 'https://example.com' output.txt --css-selector '.data'
```

---

## Common Issues

| Issue | Solution |
|-------|----------|
| Selector not found | Check selector with browser dev tools |
| Timeout | Increase timeout, use DynamicFetcher |
| Blocked by site | Use StealthyFetcher, proxies |
| JS not rendered | Use DynamicFetcher |
| Elements change | Enable adaptive mode |
| Memory issues | Use lazy loading, sessions |
| Slow performance | Use specific selectors, async |

---

## Resources

- **Docs**: https://scrapling.readthedocs.io/
- **GitHub**: https://github.com/D4Vinci/Scrapling
- **PyPI**: https://pypi.org/project/scrapling/
- **Examples**: See the 5 example scripts included

---

**Happy Scraping! 🚀**
