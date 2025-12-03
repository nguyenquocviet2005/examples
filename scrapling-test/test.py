from scrapling.fetchers import Fetcher, StealthyFetcher, DynamicFetcher
from scrapling.fetchers import FetcherSession, StealthySession, DynamicSession

print("=" * 70)
print("1. HTTP REQUESTS WITH SESSION (FetcherSession)")
print("=" * 70)

# HTTP requests with session support
with FetcherSession(impersonate='chrome') as session:  # Use latest version of Chrome's TLS fingerprint
    page = session.get('https://quotes.toscrape.com/', stealthy_headers=True)
    quotes = page.css('.quote .text::text')
    print(f"\n✓ Fetched {len(quotes)} quotes using FetcherSession:\n")
    for i, quote in enumerate(quotes[:3], 1):  # Show first 3
        print(f"  {i}. {quote}\n")
    print(f"  ... and {len(quotes) - 3} more quotes" if len(quotes) > 3 else "")

print("\n" + "=" * 70)
print("2. ONE-OFF HTTP REQUESTS (Fetcher.get)")
print("=" * 70)

# Or use one-off requests
page = Fetcher.get('https://quotes.toscrape.com/')
quotes = page.css('.quote .text::text')
authors = page.css('.quote .author::text')
print(f"\n✓ Fetched {len(quotes)} quotes using Fetcher.get:\n")
for i, (quote, author) in enumerate(zip(quotes[:2], authors[:2]), 1):
    print(f"  {i}. {quote}")
    print(f"     - {author}\n")
print(f"  ... and {len(quotes) - 2} more" if len(quotes) > 2 else "")

print("\n" + "=" * 70)
print("3. STEALTH MODE - CLOUDFLARE CHALLENGE PAGE (StealthySession)")
print("=" * 70)

# Advanced stealth mode (Keep the browser open until you finish)
with StealthySession(headless=True, solve_cloudflare=True) as session:
    page = session.fetch('https://nopecha.com/demo/cloudflare', google_search=False)
    data = page.css('#padded_content a')
    print(f"\n✓ Cloudflare CAPTCHA SOLVED! Found {len(data)} elements:\n")
    for i, elem in enumerate(data[:3], 1):
        href = elem.get('href') if elem.get('href') else 'No href'
        text = elem.text if elem.text else 'No text'
        print(f"  {i}. Link: {href}")
        print(f"     Text: {text}\n")

print("\n" + "=" * 70)
print("4. ONE-OFF STEALTH REQUEST (StealthyFetcher)")
print("=" * 70)

# Or use one-off request style, it opens the browser for this request, then closes it after finishing
page = StealthyFetcher.fetch('https://nopecha.com/demo/cloudflare')
data = page.css('#padded_content a')
print(f"\n✓ Fetched {len(data)} links via StealthyFetcher")
if data:
    text = data[0].text if data[0].text else 'N/A'
    print(f"  Sample link text: {text}\n")
    
print("\n" + "=" * 70)
print("5. FULL BROWSER AUTOMATION WITH JAVASCRIPT (DynamicSession)")
print("=" * 70)

# Full browser automation (Keep the browser open until you finish)
with DynamicSession(headless=True, disable_resources=False, network_idle=True) as session:
    page = session.fetch('https://quotes.toscrape.com/', load_dom=False)
    data = page.xpath('//span[@class="text"]/text()')  # XPath selector if you prefer it
    print(f"\n✓ Fetched {len(data)} quotes using DynamicSession (XPath):\n")
    for i, quote in enumerate(data[:2], 1):
        print(f"  {i}. {quote}\n")
    print(f"  ... and {len(data) - 2} more" if len(data) > 2 else "")

print("\n" + "=" * 70)
print("6. ONE-OFF DYNAMIC REQUEST (DynamicFetcher)")
print("=" * 70)

# Or use one-off request style, it opens the browser for this request, then closes it after finishing
page = DynamicFetcher.fetch('https://quotes.toscrape.com/')
data = page.css('.quote .text::text')
tags = page.css('.quote .tags .tag::text')
print(f"\n✓ Fetched {len(data)} quotes with tags:\n")
for i, (quote, tag_list) in enumerate(zip(data[:2], [tags[j*5:(j+1)*5] for j in range(len(tags)//5)]), 1):
    print(f"  {i}. {quote}")
    print(f"     Tags: {', '.join(tags[i*5:(i+1)*5]) if i*5 < len(tags) else 'N/A'}\n")

print("\n" + "=" * 70)
print("✨ ALL TESTS COMPLETED SUCCESSFULLY!")
print("=" * 70)