# RusticSoup v0.2.2 Release Summary

## Overview

Version 0.2.2 introduces **Field Transforms** - a powerful feature for automatic data transformation during extraction.

## What's New

### Field Transform Feature

Apply transformations to extracted data automatically without manual post-processing:

```python
from rusticsoup import WebPage, Field
from rusticsoup_helpers import ItemPage

class Article(ItemPage):
    # Single transform
    title = Field(css="h1", transform=str.upper)

    # Chain multiple transforms
    author = Field(
        css=".author",
        transform=[str.strip, str.title, lambda s: s.replace("by ", "")]
    )

    # Transform with type conversion
    price = Field(
        css=".price",
        transform=[str.strip, lambda s: float(s.replace("$", ""))]
    )

    # Transform lists
    tags = Field(
        css=".tag",
        get_all=True,
        transform=lambda tags: [t.upper() for t in tags]
    )

page = WebPage(html)
article = Article(page)

print(article.title)   # "UNDERSTANDING RUST"
print(article.author)  # "Jane Smith"
print(article.price)   # 19.99
print(article.tags)    # ["PYTHON", "RUST", "WEB"]
```

## Key Features

✅ **Single or Multiple Transforms**: Apply one function or chain multiple functions
✅ **Execution Order**: Transforms execute in the order specified
✅ **Universal Compatibility**: Works with text, attributes, and `get_all`
✅ **ItemPage Integration**: Seamless integration with PageObject pattern
✅ **Type Conversion**: Easy type conversion (string → float, string → date, etc.)

## Transform Types

### 1. Single Transform
```python
Field(css="h1", transform=str.upper)
```

### 2. Multiple Transforms (Pipeline)
```python
Field(
    css="h1",
    transform=[
        str.strip,      # First
        str.upper,      # Second
        lambda s: s.replace(" ", "_")  # Third
    ]
)
```

### 3. List Transforms
```python
Field(
    css=".tag",
    get_all=True,
    transform=lambda tags: [t.upper() for t in tags]
)
```

### 4. Attribute Transforms
```python
Field(
    css="a",
    attr="href",
    transform=lambda url: f"https://example.com{url}"
)
```

## Benefits

1. **No Manual Post-Processing**: Data is transformed automatically during extraction
2. **Clean Code**: Declarative field definitions with embedded transformations
3. **Reusable Functions**: Define transform functions once, use across multiple fields
4. **Type Safety**: Convert strings to proper types (float, int, datetime, etc.)
5. **Maintainability**: Easy to understand and modify transformation logic

## Files Added

- `FIELD_TRANSFORM.md` - Complete documentation with examples
- `test_field_transform.py` - Comprehensive test suite (7 tests, all passing)
- `RELEASE_0.2.2_SUMMARY.md` - This file

## Files Modified

- `src/page_object.rs` - Added transform parameter and execution logic
- `README.md` - Added Field transform section with examples
- `CHANGELOG.md` - Added v0.2.2 release notes
- `Cargo.toml` - Version bump to 0.2.2
- `src/lib.rs` - Version bump to 0.2.2

## Build Information

**Version**: 0.2.2
**Wheel**: `dist/rusticsoup-0.2.2-cp39-abi3-macosx_11_0_arm64.whl` (958KB)
**Build Status**: ✅ Success (warnings only, no errors)
**Tests**: ✅ All tests passing (7/7)

## Upload to PyPI

Ready to upload with:
```bash
twine upload dist/rusticsoup-0.2.2-*.whl
```

## Backward Compatibility

✅ 100% backward compatible with v0.2.1
- All existing code continues to work
- `transform` parameter is optional (defaults to None)
- No breaking changes

## Documentation

- **[Field Transform Guide](FIELD_TRANSFORM.md)** - Complete documentation
- **[README](README.md)** - Updated with transform examples
- **[CHANGELOG](CHANGELOG.md)** - Full release notes

## Example Use Cases

### Price Extraction
```python
import re

def extract_price(text):
    match = re.search(r'\$([0-9,]+\.[0-9]{2})', text)
    return match.group(1) if match else "0.00"

class Product(ItemPage):
    price = Field(
        css=".price-container",
        transform=[
            extract_price,
            lambda s: s.replace(",", ""),
            float
        ]
    )
```

### Date Formatting
```python
from datetime import datetime

def format_date(iso_date):
    dt = datetime.fromisoformat(iso_date)
    return dt.strftime("%B %d, %Y")

class Article(ItemPage):
    date = Field(
        css="time",
        attr="datetime",
        transform=format_date
    )
```

### Text Cleaning
```python
def clean_text(text):
    import re
    return re.sub(r'\s+', ' ', text).strip()

class BlogPost(ItemPage):
    content = Field(
        css=".content",
        transform=[
            lambda s: html.unescape(s),
            clean_text
        ]
    )
```

## Next Steps

After uploading to PyPI:
1. Create GitHub release with tag `v0.2.2`
2. Update GitHub release notes with CHANGELOG content
3. Announce on social media/forums if applicable
4. Monitor PyPI downloads and user feedback

## Performance

Transform execution adds minimal overhead:
- Transforms execute in Rust-managed Python context
- No additional parsing or DOM traversal
- Same performance characteristics as v0.2.1 for non-transformed fields

---

**Release Date**: January 7, 2025
**Previous Version**: 0.2.1
**Next Version**: TBD (likely 0.2.3 or 0.3.0 depending on next features)
