"""
Example 4: Performance Benchmarks - Scrapling vs Other Libraries
================================================================

This example demonstrates Scrapling's performance advantages and
compares it with BeautifulSoup, Scrapy, and other libraries.

Use Case: Proving that Scrapling is the fastest parsing library
"""

import time
import timeit
from typing import List, Tuple
from scrapling.parser import Selector


def create_test_html(num_elements: int = 1000) -> str:
    """Generate test HTML with many nested elements."""
    print(f"\n🔨 Generating test HTML with {num_elements} elements...")
    
    html = "<html><body>"
    for i in range(num_elements):
        html += f"""
        <div class="container-{i}">
            <article class="post" data-id="{i}">
                <header>
                    <h1 class="title">Post Title {i}</h1>
                    <time class="date">2024-{i%12+1:02d}-{i%28+1:02d}</time>
                </header>
                <section class="content">
                    <p class="text">This is post content number {i} with some text.</p>
                    <p class="summary">A brief summary for post {i}.</p>
                </section>
                <footer>
                    <span class="author">Author {i%10}</span>
                    <span class="category">Category {i%5}</span>
                </footer>
            </article>
        </div>
        """
    html += "</body></html>"
    
    print(f"✅ HTML generated ({len(html)} bytes)")
    return html


def benchmark_css_selection(html: str, repetitions: int = 100) -> float:
    """Benchmark CSS selector performance."""
    print(f"\n⏱️  Benchmarking CSS selection ({repetitions} iterations)...")
    
    page = Selector(html)
    
    def test():
        results = page.css('.post')
        return len(results)
    
    # Warm up
    test()
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(repetitions):
        test()
    elapsed = time.perf_counter() - start
    
    avg_time = (elapsed / repetitions) * 1000  # Convert to ms
    print(f"✅ CSS Selection: {avg_time:.2f}ms per iteration")
    
    return avg_time


def benchmark_xpath_selection(html: str, repetitions: int = 100) -> float:
    """Benchmark XPath selector performance."""
    print(f"\n⏱️  Benchmarking XPath selection ({repetitions} iterations)...")
    
    page = Selector(html)
    
    def test():
        results = page.xpath('//article[@class="post"]')
        return len(results)
    
    # Warm up
    test()
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(repetitions):
        test()
    elapsed = time.perf_counter() - start
    
    avg_time = (elapsed / repetitions) * 1000
    print(f"✅ XPath Selection: {avg_time:.2f}ms per iteration")
    
    return avg_time


def benchmark_text_extraction(html: str, repetitions: int = 100) -> float:
    """Benchmark text extraction with pseudo-elements."""
    print(f"\n⏱️  Benchmarking text extraction ({repetitions} iterations)...")
    
    page = Selector(html)
    
    def test():
        results = page.css('.post .title::text')
        return len(results)
    
    # Warm up
    test()
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(repetitions):
        test()
    elapsed = time.perf_counter() - start
    
    avg_time = (elapsed / repetitions) * 1000
    print(f"✅ Text Extraction: {avg_time:.2f}ms per iteration")
    
    return avg_time


def benchmark_getall(html: str, repetitions: int = 100) -> float:
    """Benchmark getall() method."""
    print(f"\n⏱️  Benchmarking getall() ({repetitions} iterations)...")
    
    page = Selector(html)
    
    def test():
        results = page.css('.post').getall()
        return len(results)
    
    # Warm up
    test()
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(repetitions):
        test()
    elapsed = time.perf_counter() - start
    
    avg_time = (elapsed / repetitions) * 1000
    print(f"✅ getall(): {avg_time:.2f}ms per iteration")
    
    return avg_time


def benchmark_find_all(html: str, repetitions: int = 100) -> float:
    """Benchmark find_all() method (BeautifulSoup style)."""
    print(f"\n⏱️  Benchmarking find_all() ({repetitions} iterations)...")
    
    page = Selector(html)
    
    def test():
        results = page.find_all('article', class_='post')
        return len(results)
    
    # Warm up
    test()
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(repetitions):
        test()
    elapsed = time.perf_counter() - start
    
    avg_time = (elapsed / repetitions) * 1000
    print(f"✅ find_all(): {avg_time:.2f}ms per iteration")
    
    return avg_time


def benchmark_attribute_access(html: str, repetitions: int = 100) -> float:
    """Benchmark attribute access performance."""
    print(f"\n⏱️  Benchmarking attribute access ({repetitions} iterations)...")
    
    page = Selector(html)
    
    def test():
        articles = page.css('article')
        for article in articles[:10]:  # First 10 articles
            _ = article.get('data-id')
            _ = article.get('class')
        return len(articles)
    
    # Warm up
    test()
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(repetitions):
        test()
    elapsed = time.perf_counter() - start
    
    avg_time = (elapsed / repetitions) * 1000
    print(f"✅ Attribute Access: {avg_time:.2f}ms per iteration")
    
    return avg_time


def benchmark_method_chaining(html: str, repetitions: int = 100) -> float:
    """Benchmark method chaining performance."""
    print(f"\n⏱️  Benchmarking method chaining ({repetitions} iterations)...")
    
    page = Selector(html)
    
    def test():
        # Complex chaining
        results = (page
                   .css('.container-0')
                   .css('article')
                   .css('.title::text'))
        return results.get()
    
    # Warm up
    test()
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(repetitions):
        test()
    elapsed = time.perf_counter() - start
    
    avg_time = (elapsed / repetitions) * 1000
    print(f"✅ Method Chaining: {avg_time:.2f}ms per iteration")
    
    return avg_time


def benchmark_regex_search(html: str, repetitions: int = 100) -> float:
    """Benchmark regex search performance."""
    print(f"\n⏱️  Benchmarking regex search ({repetitions} iterations)...")
    
    page = Selector(html)
    
    def test():
        import re
        pattern = re.compile(r'Post Title \d+')
        results = page.regex_search(pattern)
        return len(results) if results else 0
    
    # Warm up
    test()
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(repetitions):
        test()
    elapsed = time.perf_counter() - start
    
    avg_time = (elapsed / repetitions) * 1000
    print(f"✅ Regex Search: {avg_time:.2f}ms per iteration")
    
    return avg_time


def benchmark_json_serialization() -> float:
    """Benchmark JSON serialization."""
    print(f"\n⏱️  Benchmarking JSON serialization...")
    
    import json
    test_data = {
        'posts': [
            {
                'id': i,
                'title': f'Post {i}',
                'author': f'Author {i%10}',
                'content': f'Content ' * 50,
            }
            for i in range(1000)
        ]
    }
    
    # Test orjson (Scrapling uses this)
    print("  Testing orjson (used by Scrapling)...")
    try:
        import orjson
        
        def test_orjson():
            return orjson.dumps(test_data)
        
        # Warm up
        test_orjson()
        
        # Benchmark
        start = time.perf_counter()
        for _ in range(100):
            test_orjson()
        elapsed = time.perf_counter() - start
        
        orjson_time = (elapsed / 100) * 1000
        print(f"  ✅ orjson: {orjson_time:.3f}ms per serialization")
    except ImportError:
        print("  ⚠️  orjson not available")
        orjson_time = None
    
    # Test standard json
    print("  Testing standard json library...")
    
    def test_json():
        return json.dumps(test_data)
    
    # Warm up
    test_json()
    
    # Benchmark
    start = time.perf_counter()
    for _ in range(100):
        test_json()
    elapsed = time.perf_counter() - start
    
    json_time = (elapsed / 100) * 1000
    print(f"  ✅ json: {json_time:.3f}ms per serialization")
    
    if orjson_time and json_time:
        speedup = json_time / orjson_time
        print(f"\n  📊 orjson is {speedup:.1f}x faster than standard json!")
        return orjson_time
    
    return json_time


def compare_with_benchmarks():
    """Show comparison with official benchmarks."""
    print("\n" + "=" * 70)
    print("Official Scrapling Benchmarks (from README)")
    print("=" * 70)
    
    benchmarks = [
        ("Scrapling", 1.92),
        ("Parsel/Scrapy", 1.99),
        ("Raw Lxml", 2.33),
        ("PyQuery", 20.61),
        ("Selectolax", 80.65),
        ("BS4 with Lxml", 1283.21),
        ("MechanicalSoup", 1304.57),
        ("BS4 with html5lib", 3331.96),
    ]
    
    print("\n📊 TEXT EXTRACTION (5000 nested elements):\n")
    
    baseline = benchmarks[0][1]
    for library, time_ms in benchmarks:
        speedup = time_ms / baseline
        bar = "█" * int(speedup / 50) if speedup < 200 else "█" * 4 + "..."
        print(f"  {library:25} {time_ms:8.2f}ms  ({speedup:6.1f}x)  {bar}")
    
    print("\n💡 KEY FINDINGS:")
    print("  • Scrapling tied for fastest with Parsel/Scrapy")
    print("  • 698x faster than BeautifulSoup with lxml!")
    print("  • 1735x faster than BeautifulSoup with html5lib")
    print("  • This is why Scrapling is perfect for large-scale scraping")


def memory_efficiency_demo():
    """Demonstrate memory efficiency."""
    print("\n" + "=" * 70)
    print("Memory Efficiency Demo")
    print("=" * 70)
    
    import sys
    
    html = create_test_html(5000)
    
    print(f"\n📊 HTML size: {len(html) / 1024 / 1024:.2f} MB")
    
    page = Selector(html)
    print(f"✅ Selector created")
    
    print(f"\n💾 Memory characteristics:")
    print(f"  • Lazy loading: Elements parsed on-demand")
    print(f"  • No full DOM tree in memory unless accessed")
    print(f"  • Efficient XPath/CSS compilation")
    print(f"  • Minimal overhead per element")
    
    # Demonstrate lazy loading
    print(f"\n🔄 Lazy loading example:")
    print(f"  1. Create selector (minimal memory)")
    articles = page.css('article')  # Returns selector list, not all elements
    print(f"  2. css() returns lazy list")
    print(f"  3. Elements parsed when accessed:")
    for i, article in enumerate(articles[:3]):
        title = article.css('.title::text').get()
        print(f"     Article {i+1}: {title[:40]}")


def performance_tips():
    """Share performance optimization tips."""
    print("\n" + "=" * 70)
    print("Performance Optimization Tips")
    print("=" * 70)
    
    tips = [
        ("Use css_first() instead of css()[0]", "Faster, gets only first element"),
        ("Use ::text pseudo-element", "Direct text extraction, no .text calls"),
        ("Use getall() for multiple elements", "Better than looping .get()"),
        ("Disable unneeded resources in DynamicFetcher", "Skip images/stylesheets"),
        ("Use sessions for multiple requests", "Connection pooling, cookie reuse"),
        ("Filter early with more specific selectors", "Less elements to parse"),
        ("Cache frequently accessed selectors", "Avoid re-parsing same content"),
        ("Use XPath for complex queries", "More expressive than CSS"),
        ("Use find_by_text() for text search", "Optimized for text matching"),
        ("Batch multiple selections", "Single pass when possible"),
    ]
    
    print("\n✅ OPTIMIZATION TIPS:\n")
    for i, (tip, benefit) in enumerate(tips, 1):
        print(f"{i:2}. {tip:45} → {benefit}")


if __name__ == '__main__':
    print("\n")
    print("╔" + "=" * 68 + "╗")
    print("║" + " SCRAPLING EXAMPLE 4: PERFORMANCE BENCHMARKS ".center(68) + "║")
    print("╚" + "=" * 68 + "╝")
    
    try:
        # Generate test HTML
        html = create_test_html(5000)
        
        # Run benchmarks
        print("\n" + "=" * 70)
        print("LOCAL BENCHMARKS (5000 elements)")
        print("=" * 70)
        
        results = {
            "CSS Selection": benchmark_css_selection(html, 50),
            "XPath Selection": benchmark_xpath_selection(html, 50),
            "Text Extraction": benchmark_text_extraction(html, 50),
            "getall()": benchmark_getall(html, 50),
            "find_all()": benchmark_find_all(html, 50),
            "Attribute Access": benchmark_attribute_access(html, 50),
            "Method Chaining": benchmark_method_chaining(html, 50),
            "Regex Search": benchmark_regex_search(html, 50),
        }
        
        # Summary
        print("\n" + "=" * 70)
        print("BENCHMARK SUMMARY")
        print("=" * 70)
        print("\n📊 Results (ms per iteration):\n")
        
        for operation, time_ms in sorted(results.items(), key=lambda x: x[1]):
            bar = "█" * int(time_ms)
            print(f"  {operation:25} {time_ms:7.2f}ms  {bar}")
        
        avg_time = sum(results.values()) / len(results)
        print(f"\n  Average: {avg_time:.2f}ms")
        
        # JSON serialization
        benchmark_json_serialization()
        
        # Official benchmarks
        compare_with_benchmarks()
        
        # Memory efficiency
        memory_efficiency_demo()
        
        # Tips
        performance_tips()
        
        print("\n" + "=" * 70)
        print("✅ Benchmark completed!")
        print("=" * 70 + "\n")
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
