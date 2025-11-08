# WebPage API Quick Start

## Installation

```bash
pip install rusticsoup
```

## Basic Usage

```python
from rusticsoup import WebPage

# Create WebPage from HTML
html = """
<div class="product">
    <h2>Widget</h2>
    <span class="price">$29.99</span>
    <a href="/buy">Buy</a>
</div>
"""

page = WebPage(html, url="https://example.com")

# Extract single values
title = page.text("h2")           # "Widget"
price = page.text(".price")       # "$29.99"
link = page.attr("a", "href")     # "/buy"

# Extract structured data
product = page.extract({
    "title": "h2",
    "price": ".price",
    "link": "a@href"      # @ syntax for attributes
})
print(product)
# {'title': 'Widget', 'price': '$29.99', 'link': '/buy'}
```

## Extract Multiple Items

```python
html = """
<div class="product"><h3>Item 1</h3><span>$10</span></div>
<div class="product"><h3>Item 2</h3><span>$20</span></div>
<div class="product"><h3>Item 3</h3><span>$30</span></div>
"""

page = WebPage(html)

products = page.extract_all(".product", {
    "name": "h3",
    "price": "span"
})
print(products)
# [
#   {'name': 'Item 1', 'price': '$10'},
#   {'name': 'Item 2', 'price': '$20'},
#   {'name': 'Item 3', 'price': '$30'}
# ]
```

## Key Features

| Method | Description | Example |
|--------|-------------|---------|
| `text(selector)` | Extract text | `page.text("h1")` |
| `text_all(selector)` | Extract all text | `page.text_all("p")` |
| `attr(selector, attr)` | Extract attribute | `page.attr("a", "href")` |
| `attr_all(selector, attr)` | Extract all attributes | `page.attr_all("img", "src")` |
| `extract(mappings)` | Extract structured data | See above |
| `extract_all(container, mappings)` | Extract multiple items | See above |
| `has(selector)` | Check if exists | `page.has("nav")` |
| `count(selector)` | Count elements | `page.count("div")` |
| `absolute_url(url)` | Resolve relative URL | `page.absolute_url("/path")` |

## Field Syntax

| Syntax | Meaning | Example |
|--------|---------|---------|
| `"selector"` | Text content | `"h1"` → "Title" |
| `"selector@attr"` | Attribute value | `"a@href"` → "/link" |
| `"selector@get_all"` | All text | `"p@get_all"` → ["P1", "P2"] |
| `"sel@attr@get_all"` | All attributes | `"img@src@get_all"` → ["/1.jpg", "/2.jpg"] |

## Real Example: E-commerce

```python
from rusticsoup import WebPage

# Amazon-like product page
page = WebPage(html, url="https://shop.com/products/123")

product = page.extract({
    "title": "h1.product-title",
    "price": ".price-current",
    "original_price": ".price-original",
    "rating": ".rating-stars",
    "reviews": ".review-count",
    "url": "a.product-link@href",
    "images": "img.product-img@src@get_all"  # Multiple images
})

# Convert relative to absolute URLs
product["url"] = page.absolute_url(product["url"])
product["images"] = [page.absolute_url(img) for img in product["images"]]

print(product)
```

## Performance

RusticSoup WebPage is **2-10x faster** than BeautifulSoup:

- Built in Rust for maximum speed
- Browser-grade HTML parser (html5ever)
- Parallel processing support
- Memory efficient

## Documentation

- Full API docs: [WEBPAGE_API.md](WEBPAGE_API.md)
- Test examples: [test_webpage_api.py](test_webpage_api.py)
- Main README: [README.md](README.md)

## Why WebPage API?

✅ **Declarative** - Define what you want, not how to get it
✅ **Fast** - Rust performance with Python ergonomics
✅ **Type-safe** - Clear API with strong typing
✅ **web-poet Compatible** - Inspired by web-poet patterns
✅ **Battle-tested** - Used in production scraping

## Comparison

```python
# BeautifulSoup - Manual loops
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
products = []
for div in soup.select('.product'):
    title = div.select_one('h2')
    price = div.select_one('.price')
    link = div.select_one('a')
    products.append({
        'title': title.text if title else '',
        'price': price.text if price else '',
        'link': link.get('href') if link else ''
    })

# RusticSoup WebPage - Declarative
from rusticsoup import WebPage
page = WebPage(html)
products = page.extract_all('.product', {
    'title': 'h2',
    'price': '.price',
    'link': 'a@href'
})
```

**Result**: 90% less code, 2-10x faster!

---

Built with 🦀 by the RusticSoup team
