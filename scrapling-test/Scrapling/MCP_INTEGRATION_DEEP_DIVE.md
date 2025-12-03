# Scrapling's MCP Integration - Deep Dive

## Overview

Scrapling integrates with **Model Context Protocol (MCP)** to expose its powerful web scraping and adaptive capabilities to AI chatbots and coding assistants. This allows Claude, Claude Code, Cursor, WindSurf, and other AI tools to use Scrapling's fetchers and selectors directly.

## Architecture

### Core Components

#### 1. **ResponseModel** (Pydantic)
```python
class ResponseModel(BaseModel):
    """Request's response information structure."""
    status: int              # HTTP status code
    content: list[str]      # Extracted content as Markdown/HTML/text
    url: str                # Request URL
```

#### 2. **ScraplingMCPServer** (Main Service Class)
The server exposes **6 tools** via FastMCP:
- `get` - Basic HTTP requests (low-mid protection)
- `bulk_get` - Parallel HTTP requests
- `fetch` - JavaScript-rendered pages (Playwright)
- `bulk_fetch` - Parallel JS rendering
- `stealthy_fetch` - High-protection bypass (Camoufox)
- `bulk_stealthy_fetch` - Parallel high-protection bypass

#### 3. **FastMCP Server**
Built on `mcp.server.fastmcp`, handles:
- Tool registration with structured output
- Transport layer (stdio or streamable-http)
- Communication with AI clients

### Tool Hierarchy

```
HTTP Layer (Low-Mid Protection)
├── get(url, ...) → ResponseModel
└── bulk_get(urls, ...) → List[ResponseModel]

JavaScript Rendering (Mid Protection)
├── fetch(url, headless, ...) → ResponseModel
└── bulk_fetch(urls, ...) → List[ResponseModel]

Anti-Bot Bypass (High Protection)
├── stealthy_fetch(url, solve_cloudflare, ...) → ResponseModel
└── bulk_stealthy_fetch(urls, ...) → List[ResponseModel]
```

## Key Features

### 1. **CSS Selector Pre-Extraction**
All tools accept `css_selector` parameter:
```python
# Extract specific elements BEFORE passing to AI
result = server.get(
    url="https://example.com",
    css_selector=".product-card",  # Narrow to product cards only
    extraction_type="markdown"       # Convert to markdown
)
```

**Benefit**: Reduces token usage by filtering content before AI processing

### 2. **Extraction Types**
- `markdown` - Convert HTML to clean Markdown (recommended for AI)
- `html` - Return raw HTML
- `text` - Plain text content

### 3. **Anti-Bot Features**
The `stealthy_fetch` tool includes:
- **Cloudflare Turnstile/Interstitial**: `solve_cloudflare=True`
- **GeoIP spoofing**: `geoip=True` (use with proxies)
- **Browser impersonation**: Camoufox browser
- **WebRTC blocking**: `block_webrtc=True`
- **Ad blocking**: `disable_ads=True` (installs uBlock Origin)
- **Humanized interaction**: `humanize=True` (cursor movement, etc.)
- **OS fingerprint randomization**: `os_randomize=True`

### 4. **Content Filtering**
```python
# Extract main content only (inside <body> tag)
result = server.get(
    url="url",
    main_content_only=True,      # Default: True
    css_selector=".article > p"  # Further narrowing
)
```

### 5. **Network Configuration**
All tools support:
- **Proxy**: `proxy="http://user:pass@host:port"`
- **Proxy Auth**: `proxy_auth=("user", "password")`
- **Browser Impersonation**: `impersonate="chrome"` (default)
- **Custom Headers**: `headers={...}`
- **Cookies**: `cookies={...}`
- **Retry Logic**: `retries=3, retry_delay=1`

### 6. **Performance Features**
- **Resource blocking**: `disable_resources=True` (faster, saves bandwidth)
- **Image blocking**: `block_images=True` (DynamicFetcher & StealthyFetcher)
- **Network idle detection**: `network_idle=True` (waits for 500ms inactivity)
- **Selector waiting**: `wait_selector=".loaded"` (waits for element)

## Integration Flow

### CLI Entry Point
```bash
# Start MCP server via CLI
scrapling mcp                    # stdio transport (for Claude Desktop)
scrapling mcp --http            # streamable-http transport
scrapling mcp --http --host 0.0.0.0 --port 8000
```

### Code Flow: CLI → Server → Tools → Extractors
```
scrapling/cli.py::mcp(http, host, port)
    ↓
ScraplingMCPServer()
    ↓
server.serve(http, host, port)
    ↓
FastMCP(name="Scrapling", host, port)
    ↓
server.add_tool(
    self.get, 
    title="get",
    description=self.get.__doc__,
    structured_output=True
)
    ↓
server.run(transport="stdio" | "streamable-http")
```

### Tool Execution Flow: Tool → Fetcher → Convertor → Response
```
MCP Tool (e.g., get)
    ↓
Fetcher.get(url, ...)  # curl-cffi based HTTP
    ↓
Convertor._extract_content(page, css_selector, extraction_type)
    ↓
_ContentTranslator(content_generator, page)
    ↓
ResponseModel(status, content_list, url)
    ↓
Return to AI Client
```

## Real-World Usage Examples

### Example 1: Basic Web Scraping with AI
```python
# In Claude Desktop or Claude Code

# User: "Get the main article from techcrunch.com"
# Claude uses MCP tool:

result = get(
    url="https://techcrunch.com",
    extraction_type="markdown",
    main_content_only=True,
    css_selector="article"
)
# Returns: ResponseModel with markdown article content
```

### Example 2: E-Commerce Scraping
```python
# Narrow to product cards, convert to markdown for LLM analysis
result = get(
    url="https://amazon.com/s?k=laptop",
    css_selector=".s-result-item",  # Product cards only
    extraction_type="markdown",
    impersonate="chrome"
)
# AI can now process only product cards, not entire page
```

### Example 3: High-Protection Site with Cloudflare
```python
# Use stealthy_fetch for protected sites
result = stealthy_fetch(
    url="https://protected-site.com",
    solve_cloudflare=True,           # Bypass Cloudflare challenge
    headless=True,
    extraction_type="markdown",
    css_selector=".content"          # Extract specific section
)
```

### Example 4: Parallel Bulk Scraping
```python
# Scrape multiple URLs concurrently
results = bulk_get(
    urls=("https://site1.com", "https://site2.com", "https://site3.com"),
    css_selector=".main-content",
    extraction_type="markdown"
)
# Returns: List[ResponseModel] with all results
```

### Example 5: GeoIP Spoofing with Proxy
```python
# Scrape from specific region with proxy
result = stealthy_fetch(
    url="https://geo-blocked-site.com",
    proxy="http://user:pass@proxy-jp.com:8080",  # Japan IP
    geoip=True,                                     # Spoof timezone, locale, etc.
    solve_cloudflare=True,
    extraction_type="markdown"
)
```

## Adaptive Scraping Integration

### How MCP + Adaptive Works

The MCP integration works **seamlessly** with Scrapling's adaptive scraping:

1. **First run with auto_save=True**:
   - Selector is applied and element fingerprints are saved
   - Fingerprints stored in `~/.scrapling/adaptive/{domain}/`

2. **Subsequent runs with adaptive=True**:
   - Same selector still used initially
   - If elements move/change, fingerprint matching kicks in
   - Elements relocated via similarity scoring
   - AI gets same data format regardless of DOM changes

**Example in MCP context**:
```python
# Session 1: Initial scrape - saves fingerprints
result1 = get(
    url="https://ecommerce.com/products",
    css_selector=".product-card",
    extraction_type="markdown"
    # Internally: auto_save=True (can be configured)
)

# Later: Website redesigns completely (different HTML structure)
# Session 2: Automatic recovery - uses fingerprints
result2 = get(
    url="https://ecommerce.com/products",
    css_selector=".product-card",  # Same selector, but...
    extraction_type="markdown"
    # Internally: adaptive=True matches old .product-card elements
    # to new HTML structure via fingerprints
)
# Result: Same product data extracted despite HTML changes!
```

## Token Efficiency

### Without MCP (Full Page):
```
Claude reads entire HTML page (thousands of tokens):
<html>
  <head>...</head>
  <body>
    <nav>...</nav>
    <sidebar>...</sidebar>
    <article>...actual content...</article>  ← Only this matters
    <footer>...</footer>
  </body>
</html>
```

### With MCP + Selectors (Optimized):
```
Claude reads only extracted content (hundreds of tokens):
# Article content in markdown
**Article Title**
Article content here...
```

**Benefit**: ~80% token reduction for large pages

## Transport Modes

### Mode 1: stdio (Claude Desktop)
```bash
scrapling mcp
```
- Direct stdio communication
- No network exposure
- Lowest latency
- Recommended for Claude Desktop setup

### Mode 2: Streamable HTTP (Claude Code, Cloud)
```bash
scrapling mcp --http --host 0.0.0.0 --port 8000
```
- HTTP endpoint (typically on localhost:8000)
- Can be accessed remotely
- Better for Docker/cloud deployments
- Used by Claude Code, Cursor, WindSurf

## Implementation Details

### _ContentTranslator Function
```python
def _ContentTranslator(
    content: Generator[str, None, None], 
    page: _ScraplingResponse
) -> ResponseModel:
    """Convert content generator to ResponseModel"""
    return ResponseModel(
        status=page.status,
        content=[result for result in content],  # Collect all chunks
        url=page.url
    )
```

### Tool Registration Pattern
```python
def serve(self, http: bool, host: str, port: int):
    server = FastMCP(name="Scrapling", host=host, port=port)
    
    # Register each tool with metadata
    server.add_tool(
        self.get,                              # Method to expose
        title="get",                            # Tool name in MCP
        description=self.get.__doc__,          # Auto-docstring
        structured_output=True                 # Return ResponseModel
    )
    
    # ... repeat for all 6 tools ...
    
    server.run(
        transport="stdio" if not http else "streamable-http"
    )
```

## Performance Characteristics

| Tool | Protection | Speed | Use Case |
|------|-----------|-------|----------|
| `get` | Low | Very Fast | Static HTML, APIs |
| `bulk_get` | Low | Fast | Multiple static pages |
| `fetch` | Mid | Slow | JavaScript-heavy sites |
| `bulk_fetch` | Mid | Medium | Multiple dynamic pages |
| `stealthy_fetch` | High | Very Slow | Cloudflare, WAF, Anti-bot |
| `bulk_stealthy_fetch` | High | Slow | Multiple protected sites |

## Security Features

1. **Browser Impersonation**
   - Real Chrome/Firefox fingerprints
   - Google search referer spoofing (default)
   - Custom User-Agent support

2. **Request Fingerprinting**
   - stealthy_headers: Real browser headers
   - Randomized browser fingerprints (stealthy_fetch)
   - HTTP/3 support

3. **Anti-Detection**
   - Canvas fingerprint randomization
   - WebGL disabling
   - WebRTC leak prevention
   - OS fingerprint randomization

## Troubleshooting

### Issue: Selector not matching
**Solution**: Use `main_content_only=False` if selector is outside `<body>`

### Issue: Cloudflare blocking requests
**Solution**: Use `stealthy_fetch` with `solve_cloudflare=True`

### Issue: Too many tokens in AI context
**Solution**: Narrow with more specific `css_selector`, use `disable_resources=True`

### Issue: Slow performance
**Solution**: Use `disable_resources=True`, `block_images=True`, or try `get` instead of `fetch`

## Testing

```python
# Unit tests in tests/ai/test_ai_mcp.py
from scrapling.core.ai import ScraplingMCPServer, ResponseModel

server = ScraplingMCPServer()

# Test basic GET
result = server.get(url="https://httpbin.org/html", extraction_type="markdown")
assert isinstance(result, ResponseModel)
assert result.status == 200

# Test async bulk operations
results = await server.bulk_get(
    urls=("https://httpbin.org/html", "https://httpbin.org/html"),
    extraction_type="html"
)
assert len(results) == 2
```

## Configuration & Setup

### Installation
```bash
pip install "scrapling[ai]"
scrapling install  # Downloads MCP dependencies
```

### Claude Desktop Setup
```json
{
  "mcpServers": {
    "scrapling": {
      "command": "scrapling",
      "args": ["mcp"]
    }
  }
}
```

### Docker Setup
```dockerfile
FROM python:3.11
RUN pip install "scrapling[ai]"
RUN scrapling install
EXPOSE 8000
CMD ["scrapling", "mcp", "--http", "--host", "0.0.0.0", "--port", "8000"]
```

## Summary

Scrapling's MCP integration bridges the gap between AI chatbots and web scraping by:

1. **Exposing 6 versatile tools** for different protection levels
2. **Enabling CSS selector pre-filtering** to reduce token usage
3. **Maintaining adaptive capabilities** automatically
4. **Supporting both sync and async** operations
5. **Providing anti-bot protection** for high-protection sites
6. **Integrating seamlessly** with Claude, Claude Code, Cursor, and WindSurf

The key innovation is allowing AI systems to narrow page content BEFORE processing, dramatically reducing token usage while maintaining Scrapling's unique adaptive scraping capabilities across DOM changes.
