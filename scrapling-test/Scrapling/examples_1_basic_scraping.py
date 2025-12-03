"""
Example 1: Basic HTTP Scraping with Scrapling
================================================

This example demonstrates how to scrape static websites using Scrapling's
simple Fetcher with various selection methods.

Use Case: Fast scraping of static websites with HTTP requests
"""

from scrapling.fetchers import Fetcher, FetcherSession
from scrapling.parser import Selector


def example_simple_scraping():
    """Scrape quotes from a simple website using CSS selectors."""
    print("=" * 70)
    print("Example 1.1: Simple Static Website Scraping")
    print("=" * 70)
    
    # Fetch the page
    page = Fetcher.get('https://quotes.toscrape.com/')
    
    if page.status == 200:
        print(f"✅ Successfully fetched page (Status: {page.status})\n")
        
        # Get all quotes using CSS selector
        quotes = page.css('.quote')
        print(f"Found {len(quotes)} quotes\n")
        
        # Extract first 3 quotes
        for i, quote in enumerate(quotes[:3], 1):
            text = quote.css('.text::text').get()  # Get first text
            author = quote.css('.author::text').get()
            print(f"Quote {i}:")
            print(f"  Text: {text}")
            print(f"  Author: {author}\n")
    else:
        print(f"❌ Failed to fetch page (Status: {page.status})")


def example_multiple_selection_methods():
    """Demonstrate different selection methods (CSS, XPath, BeautifulSoup-style)."""
    print("=" * 70)
    print("Example 1.2: Multiple Selection Methods")
    print("=" * 70)
    
    page = Fetcher.get('https://quotes.toscrape.com/')
    
    print("\n1️⃣ CSS Selector:")
    css_quotes = page.css('.quote .text::text')
    print(f"   Found {len(css_quotes)} quotes with CSS")
    print(f"   First quote: {css_quotes.get()[:80]}...")
    
    print("\n2️⃣ XPath Selector:")
    xpath_quotes = page.xpath('//span[@class="text"]/text()')
    print(f"   Found {len(xpath_quotes)} quotes with XPath")
    print(f"   First quote: {xpath_quotes.get()[:80]}...")
    
    print("\n3️⃣ BeautifulSoup-style (find_all):")
    bs_quotes = page.find_all('span', class_='text')
    print(f"   Found {len(bs_quotes)} quote elements")
    print(f"   First quote text: {bs_quotes[0].text[:80]}...")
    
    print("\n4️⃣ Find by text:")
    print("   Looking for elements containing 'The'...")
    elements = page.find_by_text('The', tag='span')
    print(f"   Found {len(elements)} elements")
    if elements:
        print(f"   First match: {elements[0].text[:80]}...")


def example_element_navigation():
    """Demonstrate parent, sibling, and child navigation."""
    print("\n" + "=" * 70)
    print("Example 1.3: Element Navigation & Relationships")
    print("=" * 70)
    
    page = Fetcher.get('https://quotes.toscrape.com/')
    
    # Get first quote
    first_quote = page.css_first('.quote')
    
    print(f"\n📍 First Quote Element:")
    print(f"   Text: {first_quote.css('.text::text').get()[:60]}...")
    print(f"   Author: {first_quote.css('.author::text').get()}")
    
    # Navigate to parent
    print(f"\n⬆️ Parent Element:")
    parent = first_quote.parent
    print(f"   Tag: {parent.name}")
    print(f"   Class: {parent.get('class', 'N/A')}")
    
    # Navigate to next sibling (next quote)
    print(f"\n➡️ Next Sibling (next quote):")
    next_quote = first_quote.next_sibling
    if next_quote:
        next_text = next_quote.css('.text::text').get()
        print(f"   Text: {next_text[:60]}...")
    
    # Get all siblings (other quotes in same container)
    print(f"\n🔗 All Siblings (quotes in same section):")
    siblings = first_quote.get_siblings()
    print(f"   Total siblings: {len(siblings)}")


def example_data_extraction_patterns():
    """Extract structured data from multiple elements."""
    print("\n" + "=" * 70)
    print("Example 1.4: Structured Data Extraction")
    print("=" * 70)
    
    page = Fetcher.get('https://quotes.toscrape.com/')
    
    # Extract all quotes with their data
    quotes_data = []
    
    for quote_elem in page.css('.quote')[:5]:
        data = {
            'text': quote_elem.css('.text::text').get(),
            'author': quote_elem.css('.author::text').get(),
            'tags': quote_elem.css('.tags a::text').getall()
        }
        quotes_data.append(data)
    
    print(f"\n📊 Extracted {len(quotes_data)} structured quotes:\n")
    
    for i, quote in enumerate(quotes_data, 1):
        print(f"Quote {i}:")
        print(f"  Author: {quote['author']}")
        print(f"  Tags: {', '.join(quote['tags'])}")
        print(f"  Text: {quote['text'][:60]}...")
        print()


def example_with_session():
    """Use FetcherSession for multiple requests with session persistence."""
    print("\n" + "=" * 70)
    print("Example 1.5: Session Management with Cookies")
    print("=" * 70)
    
    # Sessions maintain cookies and headers across requests
    with FetcherSession() as session:
        print("\n📝 Using FetcherSession for multiple requests:")
        
        # First request
        page1 = session.get('https://quotes.toscrape.com/')
        print(f"✅ Request 1: {page1.status}")
        quotes1 = page1.css('.quote .text::text')
        print(f"   Found {len(quotes1)} quotes")
        
        # Second request (cookies are maintained)
        page2 = session.get('https://quotes.toscrape.com/page/2/')
        print(f"✅ Request 2: {page2.status}")
        quotes2 = page2.css('.quote .text::text')
        print(f"   Found {len(quotes2)} quotes")
        
        print(f"\n🔗 Both requests shared the same session (cookies, connection pool, etc.)")


def example_attribute_extraction():
    """Extract attributes from HTML elements."""
    print("\n" + "=" * 70)
    print("Example 1.6: Attribute & Link Extraction")
    print("=" * 70)
    
    page = Fetcher.get('https://quotes.toscrape.com/')
    
    print("\n🔗 Extracting links:")
    links = page.css('a')
    for link in links[:5]:
        href = link.get('href')
        text = link.text
        print(f"   Link: {text:20} → {href}")
    
    print(f"\n   Total links: {len(links)}")


def example_regex_and_cleaning():
    """Use regex and text cleaning methods."""
    print("\n" + "=" * 70)
    print("Example 1.7: Regex & Text Processing")
    print("=" * 70)
    
    page = Fetcher.get('https://quotes.toscrape.com/')
    
    # Get quote text with whitespace
    raw_text = page.css_first('.quote .text').text
    print(f"\n1️⃣ Raw text (with quotes):")
    print(f"   {raw_text}\n")
    
    # Remove the decorative quotes
    import re
    clean_text = re.sub(r'^["\']|["\']$', '', raw_text)
    print(f"2️⃣ Cleaned text (quotes removed):")
    print(f"   {clean_text}\n")
    
    # Extract with regex
    print(f"3️⃣ Using regex extraction:")
    quote_elem = page.css_first('.quote')
    author_full = quote_elem.css_first('.author').text
    print(f"   Full author element: {author_full}")


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " SCRAPLING EXAMPLE 1: BASIC HTTP SCRAPING ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        example_simple_scraping()
        example_multiple_selection_methods()
        example_element_navigation()
        example_data_extraction_patterns()
        example_with_session()
        example_attribute_extraction()
        example_regex_and_cleaning()
        
        print("\n" + "=" * 70)
        print("✅ All examples completed successfully!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
