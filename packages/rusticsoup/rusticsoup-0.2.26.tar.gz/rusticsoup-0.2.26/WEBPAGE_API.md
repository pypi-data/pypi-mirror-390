# WebPage API - WebPoet-style Parsing for RusticSoup

RusticSoup now includes a powerful WebPage API inspired by [web-poet](https://github.com/scrapinghub/web-poet), providing a high-level, declarative interface for web scraping.

## Table of Contents

- [Quick Start](#quick-start)
- [Core Concepts](#core-concepts)
- [API Reference](#api-reference)
- [Real-World Examples](#real-world-examples)
- [Comparison with web-poet](#comparison-with-web-poet)

## Quick Start

```python
from rusticsoup import WebPage

# Create a WebPage from HTML
html = """
<div class="product">
    <h2>Amazing Widget</h2>
    <span class="price">$29.99</span>
    <a href="/buy">Buy Now</a>
    <img src="/widget.jpg">
</div>
"""

page = WebPage(html, url="https://example.com/products")

# Extract single values
title = page.text("h2")  # "Amazing Widget"
price = page.text("span.price")  # "$29.99"
link = page.attr("a", "href")  # "/buy"
image = page.attr("img", "src")  # "/widget.jpg"

# Extract structured data
data = page.extract({
    "title": "h2",
    "price": "span.price",
    "link": "a@href",  # @ syntax for attributes
    "image": "img@src"
})
# Returns: {'title': 'Amazing Widget', 'price': '$29.99', 'link': '/buy', 'image': '/widget.jpg'}
```

## Core Concepts

### 1. WebPage Class

The `WebPage` class represents a parsed HTML document with metadata:

```python
page = WebPage(
    html="<html>...</html>",
    url="https://example.com/page",
    metadata={"source": "api", "timestamp": "2025-01-01"}
)
```

**Properties:**
- `url` - The page URL
- `metadata` - Dictionary of custom metadata

**Methods:**
- `text(selector)` - Extract text from first matching element
- `text_all(selector)` - Extract text from all matching elements
- `attr(selector, attribute)` - Extract attribute from first matching element
- `attr_all(selector, attribute)` - Extract attribute from all matching elements
- `css(selector)` - Get HTML of first matching element
- `css_all(selector)` - Get HTML of all matching elements
- `has(selector)` - Check if selector matches any elements
- `count(selector)` - Count matching elements
- `extract(mappings)` - Extract structured data using field mappings
- `extract_all(container, mappings)` - Extract multiple items
- `absolute_url(url)` - Convert relative URL to absolute
- `html()` - Get raw HTML content

### 2. Extraction Patterns

#### Single Field Extraction

```python
# Text content
title = page.text("h1")

# Attribute extraction
link = page.attr("a", "href")

# Check existence
has_nav = page.has("nav.main-menu")

# Count elements
num_products = page.count("div.product")
```

#### Multiple Field Extraction

```python
# Extract all matching elements
all_links = page.attr_all("a", "href")
all_paragraphs = page.text_all("p")
```

#### Structured Data Extraction

```python
# Extract single item
product = page.extract({
    "title": "h2.product-title",
    "price": "span.price",
    "url": "a@href",          # @ syntax for attributes
    "image": "img@src",
    "rating": "div.rating"
})

# Extract multiple items
products = page.extract_all("div.product", {
    "title": "h2",
    "price": "span.price",
    "url": "a@href"
})
```

### 3. Field Specification Syntax

Field selectors support a special syntax for common operations:

| Syntax | Description | Example |
|--------|-------------|---------|
| `"selector"` | Extract text content | `"h1"` → "Page Title" |
| `"selector@attr"` | Extract attribute | `"a@href"` → "/page.html" |
| `"selector@get_all"` | Extract text from all matches | `"p@get_all"` → ["Para 1", "Para 2"] |
| `"selector@attr@get_all"` | Extract attribute from all matches | `"img@src@get_all"` → ["/img1.jpg", "/img2.jpg"] |

## API Reference

### WebPage

```python
class WebPage:
    def __init__(
        self,
        html: str,
        url: Optional[str] = None,
        metadata: Optional[Dict[str, str]] = None
    )
```

#### Properties

- **`url: Optional[str]`** - The page URL
- **`metadata: Dict[str, str]`** - Custom metadata dictionary

#### Methods

##### text(selector: str) -> str
Extract text content from the first element matching the CSS selector.

```python
title = page.text("h1")  # "Welcome"
```

##### text_all(selector: str) -> List[str]
Extract text content from all elements matching the CSS selector.

```python
paragraphs = page.text_all("p")  # ["First paragraph", "Second paragraph"]
```

##### attr(selector: str, attribute: str) -> Optional[str]
Extract an attribute value from the first element matching the CSS selector.

```python
link = page.attr("a.download", "href")  # "/downloads/file.pdf"
```

##### attr_all(selector: str, attribute: str) -> List[str]
Extract an attribute value from all elements matching the CSS selector.

```python
images = page.attr_all("img", "src")  # ["/img1.jpg", "/img2.jpg", "/img3.jpg"]
```

##### css(selector: str) -> Optional[str]
Get the HTML content of the first element matching the CSS selector.

```python
nav_html = page.css("nav.main-menu")
```

##### css_all(selector: str) -> List[str]
Get the HTML content of all elements matching the CSS selector.

```python
all_divs = page.css_all("div.item")
```

##### has(selector: str) -> bool
Check if any elements match the CSS selector.

```python
has_nav = page.has("nav")  # True or False
```

##### count(selector: str) -> int
Count the number of elements matching the CSS selector.

```python
num_products = page.count("div.product")  # 10
```

##### extract(field_mappings: Dict[str, str]) -> Dict[str, Any]
Extract structured data using field mappings.

```python
data = page.extract({
    "title": "h1",
    "price": "span.price",
    "link": "a@href"
})
```

##### extract_all(container_selector: str, field_mappings: Dict[str, str]) -> List[Dict[str, Any]]
Extract multiple items using a container selector and field mappings.

```python
products = page.extract_all("div.product", {
    "name": "h2",
    "price": "span.price",
    "url": "a@href"
})
```

##### absolute_url(url: str) -> str
Convert a relative URL to an absolute URL using the page's base URL.

```python
abs_url = page.absolute_url("/products/123")
# Returns: "https://example.com/products/123"
```

##### html() -> str
Get the raw HTML content of the entire page.

```python
html_content = page.html()
```

### Field

The `Field` class allows defining reusable field extractors (for future PageObject integration).

```python
from rusticsoup import Field

# Create field descriptors
title_field = Field(css="h1")
link_field = Field(css="a", attr="href")
tags_field = Field(css="span.tag", get_all=True)
```

**Parameters:**
- `css` (str, optional) - CSS selector
- `xpath` (str, optional) - XPath selector (not yet implemented)
- `attr` (str, optional) - Attribute name to extract
- `get_all` (bool, default=False) - Extract from all matching elements
- `default` (str, optional) - Default value if not found
- `required` (bool, default=True) - Whether the field is required

## Real-World Examples

### Example 1: E-commerce Product Scraping

```python
from rusticsoup import WebPage

html = """
<div class="product" data-id="123">
    <h2 class="title">Wireless Mouse</h2>
    <div class="price">
        <span class="current">$24.99</span>
        <span class="original">$34.99</span>
    </div>
    <div class="rating">
        <span class="stars">★★★★☆</span>
        <span class="count">1,234 reviews</span>
    </div>
    <a href="/products/wireless-mouse" class="view-details">View Details</a>
    <img src="/images/mouse.jpg" alt="Wireless Mouse">
    <ul class="features">
        <li>Ergonomic design</li>
        <li>Wireless connectivity</li>
        <li>Long battery life</li>
    </ul>
</div>
"""

page = WebPage(html, url="https://shop.example.com")

# Extract product data
product = page.extract({
    "title": "h2.title",
    "current_price": "span.current",
    "original_price": "span.original",
    "rating": "span.stars",
    "review_count": "span.count",
    "url": "a.view-details@href",
    "image": "img@src",
    "image_alt": "img@alt"
})

# Convert to absolute URL
product["url"] = page.absolute_url(product["url"])
product["image"] = page.absolute_url(product["image"])

print(product)
# {
#     'title': 'Wireless Mouse',
#     'current_price': '$24.99',
#     'original_price': '$34.99',
#     'rating': '★★★★☆',
#     'review_count': '1,234 reviews',
#     'url': 'https://shop.example.com/products/wireless-mouse',
#     'image': 'https://shop.example.com/images/mouse.jpg',
#     'image_alt': 'Wireless Mouse'
# }

# Extract features list
features = page.text_all("ul.features li")
print(features)
# ['Ergonomic design', 'Wireless connectivity', 'Long battery life']
```

### Example 2: News Article Scraping

```python
from rusticsoup import WebPage

html = """
<article class="news-article">
    <header>
        <h1>Breaking: New Technology Breakthrough</h1>
        <div class="meta">
            <span class="author">By John Doe</span>
            <time datetime="2025-01-07">January 7, 2025</time>
            <span class="category">Technology</span>
        </div>
    </header>
    <div class="content">
        <p class="lead">Scientists have announced a major breakthrough...</p>
        <p>The research team, led by Dr. Smith...</p>
        <p>This discovery could lead to...</p>
    </div>
    <div class="tags">
        <a href="/tag/science">Science</a>
        <a href="/tag/technology">Technology</a>
        <a href="/tag/research">Research</a>
    </div>
</article>
"""

page = WebPage(html, url="https://news.example.com/article/123")

# Extract article data
article = page.extract({
    "title": "h1",
    "author": "span.author",
    "date": "time@datetime",
    "category": "span.category",
    "lead": "p.lead"
})

# Extract all paragraphs
article["paragraphs"] = page.text_all("div.content p")

# Extract all tags
article["tags"] = page.text_all("div.tags a")
article["tag_urls"] = page.attr_all("div.tags a", "href")

print(article)
# {
#     'title': 'Breaking: New Technology Breakthrough',
#     'author': 'By John Doe',
#     'date': '2025-01-07',
#     'category': 'Technology',
#     'lead': 'Scientists have announced a major breakthrough...',
#     'paragraphs': [
#         'Scientists have announced a major breakthrough...',
#         'The research team, led by Dr. Smith...',
#         'This discovery could lead to...'
#     ],
#     'tags': ['Science', 'Technology', 'Research'],
#     'tag_urls': ['/tag/science', '/tag/technology', '/tag/research']
# }
```

### Example 3: Search Results Scraping

```python
from rusticsoup import WebPage

html = """
<div class="search-results">
    <div class="result">
        <h3><a href="/item/1">First Result</a></h3>
        <p class="description">Description of first result...</p>
        <span class="price">$10.00</span>
    </div>
    <div class="result">
        <h3><a href="/item/2">Second Result</a></h3>
        <p class="description">Description of second result...</p>
        <span class="price">$20.00</span>
    </div>
    <div class="result">
        <h3><a href="/item/3">Third Result</a></h3>
        <p class="description">Description of third result...</p>
        <span class="price">$30.00</span>
    </div>
</div>
"""

page = WebPage(html, url="https://example.com/search")

# Extract all results at once
results = page.extract_all("div.result", {
    "title": "h3 a",
    "url": "h3 a@href",
    "description": "p.description",
    "price": "span.price"
})

# Post-process results
for result in results:
    result["url"] = page.absolute_url(result["url"])
    # Clean price
    result["price_value"] = float(result["price"].replace("$", ""))

print(f"Found {len(results)} results")
for i, result in enumerate(results, 1):
    print(f"\nResult {i}:")
    print(f"  Title: {result['title']}")
    print(f"  URL: {result['url']}")
    print(f"  Price: {result['price']} (${result['price_value']:.2f})")
```

### Example 4: Table Data Extraction

```python
from rusticsoup import WebPage

html = """
<table class="data-table">
    <thead>
        <tr>
            <th>Name</th>
            <th>Age</th>
            <th>City</th>
        </tr>
    </thead>
    <tbody>
        <tr class="row">
            <td class="name">Alice</td>
            <td class="age">30</td>
            <td class="city">New York</td>
        </tr>
        <tr class="row">
            <td class="name">Bob</td>
            <td class="age">25</td>
            <td class="city">Los Angeles</td>
        </tr>
        <tr class="row">
            <td class="name">Charlie</td>
            <td class="age">35</td>
            <td class="city">Chicago</td>
        </tr>
    </tbody>
</table>
"""

page = WebPage(html)

# Extract table rows
rows = page.extract_all("tr.row", {
    "name": "td.name",
    "age": "td.age",
    "city": "td.city"
})

# Convert age to int
for row in rows:
    row["age"] = int(row["age"])

print(rows)
# [
#     {'name': 'Alice', 'age': 30, 'city': 'New York'},
#     {'name': 'Bob', 'age': 25, 'city': 'Los Angeles'},
#     {'name': 'Charlie', 'age': 35, 'city': 'Chicago'}
# ]
```

## Comparison with web-poet

RusticSoup's WebPage API is inspired by [web-poet](https://github.com/scrapinghub/web-poet) but optimized for speed and simplicity:

| Feature | web-poet | RusticSoup WebPage | Notes |
|---------|----------|-------------------|-------|
| **Language** | Python | Rust + Python | RusticSoup is 2-10x faster |
| **WebPage class** | ✅ | ✅ | Similar API design |
| **CSS selectors** | ✅ | ✅ | Full support |
| **XPath** | ✅ | 🚧 Planned | Coming soon |
| **Field descriptors** | ✅ | ✅ | For PageObject pattern |
| **PageObject pattern** | ✅ | 🚧 Partial | Field class available |
| **Dependency injection** | ✅ | 🚧 Planned | Future feature |
| **URL resolution** | ✅ | ✅ | `absolute_url()` method |
| **Metadata** | ✅ | ✅ | Custom metadata support |
| **Browser support** | Via scrapy-poet | ❌ | Not planned |
| **Async support** | ✅ | ❌ | Not needed (Rust speed) |

### Migration from web-poet

```python
# web-poet
from web_poet import WebPage

async def parse(page: WebPage):
    title = await page.css("h1::text").get()
    links = await page.css("a::attr(href)").getall()
    return {"title": title, "links": links}

# RusticSoup WebPage (no async needed - it's fast enough!)
from rusticsoup import WebPage

def parse(html: str):
    page = WebPage(html)
    title = page.text("h1")
    links = page.attr_all("a", "href")
    return {"title": title, "links": links}
```

## Best Practices

### 1. Use Specific Selectors

```python
# Good - specific selector
title = page.text("h1.product-title")

# Less good - too generic
title = page.text("h1")
```

### 2. Handle Missing Data

```python
# Check if element exists before extracting
if page.has("div.optional-info"):
    info = page.text("div.optional-info")
else:
    info = None

# Or use empty string as default for missing elements
info = page.text("div.optional-info")  # Returns "" if not found
```

### 3. Process URLs

```python
# Always convert relative URLs to absolute
product_url = page.attr("a.product-link", "href")
product_url = page.absolute_url(product_url)
```

### 4. Batch Extraction

```python
# Good - extract all fields at once
data = page.extract({
    "title": "h1",
    "price": "span.price",
    "description": "p.description"
})

# Less efficient - multiple calls
title = page.text("h1")
price = page.text("span.price")
description = page.text("p.description")
```

## Performance Tips

1. **Use `extract()` for single items** - More efficient than multiple individual calls
2. **Use `extract_all()` for lists** - Optimized for batch extraction
3. **Avoid XPath when possible** - CSS selectors are faster
4. **Cache WebPage objects** - Reuse for multiple extractions
5. **Process data after extraction** - Let RusticSoup do the parsing, do transformations in Python

## Future Enhancements

- **XPath Support**: Full XPath selector support
- **PageObject Pattern**: Complete PageObject implementation with Python decorators
- **Nested Extraction**: Support for nested field mappings
- **Custom Processors**: Plugin system for custom field processors
- **Type Validation**: Automatic type conversion and validation
- **Caching**: Selector caching for repeated extractions

## License

MIT License - Same as RusticSoup

## See Also

- [RusticSoup Main Documentation](README.md)
- [web-poet](https://github.com/scrapinghub/web-poet) - The inspiration for this API
- [Test Examples](test_webpage_api.py) - Complete test suite with examples
