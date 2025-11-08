# RusticSoup v0.2.0 Release Notes

## 🎉 Major Release: WebPage API

We're excited to announce RusticSoup v0.2.0 with the new **WebPage API** - a high-level, declarative interface for web scraping inspired by [web-poet](https://github.com/scrapinghub/web-poet)!

## 🌟 What's New

### WebPage API

The new WebPage API provides a powerful, object-oriented interface for HTML parsing:

```python
from rusticsoup import WebPage

page = WebPage(html, url="https://example.com")

# Extract single values
title = page.text("h1")
price = page.text(".price")
link = page.attr("a", "href")

# Extract multiple items
products = page.extract_all(".product", {
    "name": "h2",
    "price": ".price",
    "url": "a@href"
})

# Check existence & count
if page.has("nav.menu"):
    items = page.count("nav.menu li")
```

### Key Features

✅ **Declarative Extraction** - Define what you want, not how to get it
✅ **URL & Metadata Support** - Track page context
✅ **web-poet Compatible** - Similar patterns, Rust speed
✅ **Attribute Syntax** - `"selector@attr"` for easy attribute extraction
✅ **Bulk Operations** - Extract multiple items with one call
✅ **URL Resolution** - `absolute_url()` for relative URLs
✅ **Fast** - Same 2-10x speed advantage over BeautifulSoup

### API Methods

- `text(selector)` / `text_all(selector)` - Extract text
- `attr(selector, attr)` / `attr_all(selector, attr)` - Extract attributes
- `extract(mappings)` - Extract structured data
- `extract_all(container, mappings)` - Extract multiple items
- `has(selector)` - Check existence
- `count(selector)` - Count elements
- `absolute_url(url)` - Resolve URLs
- `css(selector)` / `css_all(selector)` - Get HTML
- `html()` - Raw HTML content

## 📚 Documentation

- **[WebPage API Documentation](WEBPAGE_API.md)** - Complete API reference with examples
- **[Quick Start Guide](WEBPAGE_QUICKSTART.md)** - Get started in 5 minutes
- **[Test Suite](test_webpage_api.py)** - 9+ real-world examples
- **[Updated README](README.md)** - Both APIs side-by-side

## 🔄 Migration Guide

**Good News**: v0.2.0 is **100% backward compatible**!

All existing code using the Universal Extraction API continues to work:

```python
# Old API (still works)
import rusticsoup
products = rusticsoup.extract_data(html, ".product", {...})
```

**New Recommended Approach**:

```python
# New WebPage API (recommended for new code)
from rusticsoup import WebPage
page = WebPage(html)
products = page.extract_all(".product", {...})
```

### When to Use Each API

- **WebPage API**: Single-page scraping, complex workflows, URL resolution
- **Universal API**: Batch processing, simple extraction, functional style

Both have the same performance!

## 📦 Installation

```bash
pip install --upgrade rusticsoup
```

Or install the specific version:

```bash
pip install rusticsoup==0.2.0
```

## 🚀 Examples

### E-commerce Scraping

```python
from rusticsoup import WebPage

page = WebPage(html, url="https://shop.example.com/product")

product = page.extract({
    "title": "h1.product-title",
    "price": ".current-price",
    "original_price": ".original-price",
    "rating": ".rating-stars",
    "reviews": ".review-count",
    "images": "img.product-image@src@get_all"
})

# Resolve relative URLs
product["url"] = page.absolute_url(product["url"])
```

### Search Results

```python
from rusticsoup import WebPage

page = WebPage(html)

results = page.extract_all(".search-result", {
    "title": "h3 a",
    "url": "h3 a@href",
    "description": ".description",
    "price": ".price"
})

print(f"Found {len(results)} results")
```

### News Articles

```python
from rusticsoup import WebPage

page = WebPage(html, url="https://news.example.com/article")

article = page.extract({
    "title": "h1",
    "author": ".author",
    "date": "time@datetime",
    "category": ".category"
})

# Extract all paragraphs
article["content"] = page.text_all("article p")

# Extract all tags
article["tags"] = page.text_all(".tag a")
```

## 🎯 Benefits Over BeautifulSoup

| Feature | BeautifulSoup | RusticSoup WebPage |
|---------|---------------|-------------------|
| **Speed** | Baseline | 2-10x faster |
| **Code** | Verbose loops | Declarative |
| **Attributes** | Manual `.get()` | `@attr` syntax |
| **Async** | Not needed | Not needed |
| **URL Resolution** | Manual | Built-in |
| **Metadata** | Not supported | Built-in |

### Code Comparison

```python
# BeautifulSoup (verbose)
from bs4 import BeautifulSoup
soup = BeautifulSoup(html, 'html.parser')
products = []
for div in soup.select('.product'):
    title = div.select_one('h2')
    price = div.select_one('.price')
    products.append({
        'title': title.text if title else '',
        'price': price.text if price else ''
    })

# RusticSoup WebPage (concise)
from rusticsoup import WebPage
page = WebPage(html)
products = page.extract_all('.product', {
    'title': 'h2',
    'price': '.price'
})
```

**90% less code, 2-10x faster!**

## 🔮 Future Plans

- Complete PageObject implementation with Python decorators
- XPath selector support
- Nested extraction
- Custom field processors
- Type validation
- Selector caching

## 🙏 Acknowledgments

- Inspired by [web-poet](https://github.com/scrapinghub/web-poet)
- Built on [html5ever](https://github.com/servo/html5ever) (Mozilla's parser)
- Powered by [Rust](https://www.rust-lang.org/) for maximum performance

## 📝 Full Changelog

See [CHANGELOG.md](CHANGELOG.md) for complete details.

## 🐛 Issues & Feedback

Found a bug or have a feature request? Please open an issue:
https://github.com/iristech-systems/RusticSoup/issues

## 📦 PyPI Release

**Wheel Built**: `rusticsoup-0.2.0-cp39-abi3-macosx_11_0_arm64.whl`

### Publishing to PyPI

```bash
# Install twine if needed
pip install twine

# Upload to PyPI
twine upload target/wheels/rusticsoup-0.2.0-*.whl

# Or upload to Test PyPI first
twine upload --repository testpypi target/wheels/rusticsoup-0.2.0-*.whl
```

### Building for Multiple Platforms

For CI/CD with GitHub Actions:

```yaml
- uses: PyO3/maturin-action@v1
  with:
    command: build
    args: --release --out dist
    manylinux: auto
```

## 🎊 Thank You!

Thank you to all users and contributors! This release brings RusticSoup closer to being the ultimate HTML parsing library for Python.

Happy scraping! 🦀🍲

---

**Made with 🦀 and ❤️ by the RusticSoup team**
