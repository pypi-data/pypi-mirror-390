# Wagtail Block Components

Use Wagtail blocks as reusable components in Django templates.

## Installation

```bash
pip install wagtail-block-components
```

Add to `INSTALLED_APPS`:

```python
INSTALLED_APPS = [
    # ...
    'wagtail_block_components',
    # ...
]
```

## Quick Start

### 1. Define Your Blocks

```python
# myapp/blocks.py
import uuid
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.documents.blocks import DocumentChooserBlock

class AccordionItemBlock(blocks.StructBlock):
    title = blocks.CharBlock(required=True)
    content = blocks.StreamBlock([
        ('paragraph', blocks.RichTextBlock()),
        ('page', blocks.PageChooserBlock()),
        ('image', ImageChooserBlock()),
        ('document', DocumentChooserBlock()),
        ('inline_structblock', blocks.StructBlock([
            ('heading', blocks.CharBlock()),
            ('content', blocks.RichTextBlock()),
        ])),
    ], required=False)

    class Meta:
        template = 'components/accordion_item.html'

class AccordionBlock(blocks.StructBlock):
    items = blocks.ListBlock(AccordionItemBlock())

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context)
        # Generate unique accordion ID for children to use
        context['accordion_id'] = f"accordion-{uuid.uuid4().hex[:8]}"
        return context

    class Meta:
        template = 'components/accordion.html'
```

### 2. Register Components

```python
# myapp/wagtail_hooks.py
from wagtail import hooks
from . import blocks

@hooks.register('register_components')
def register_components():
    return [
        blocks.AccordionBlock,
        blocks.AccordionItemBlock,
    ]
```

### 3. Use in Templates

```jinja
{% load wagtail_block_components %}

{# Self-closing block - empty accordion #}
{% wagtail_block "AccordionBlock" / %}


{# Block with kwargs passed directly #}
{% wagtail_block "AccordionItemBlock" title="Empty Item" / %}


{# Full accordion with all syntax variations #}
{% wagtail_block "AccordionBlock" %}

    {# First item: using block_field for title (template content) #}
    {% block_field "items" %}
        {% wagtail_block "AccordionItemBlock" %}
            {% block_field "title" %}Question 1{% endblock_field %}
            {% block_field "content" %}
                {% block_field "paragraph" %}<p>Answer 1 part 1</p>{% endblock_field %}
                {% block_field "paragraph" %}<p>Answer 1 part 2</p>{% endblock_field %}
            {% endblock_field %}
        {% endwagtail_block %}
    {% endblock_field %}

    {# Second item: using kwargs for title #}
    {% block_field "items" %}
        {% wagtail_block "AccordionItemBlock" title="Question 2" %}
            {% block_field "content" %}
                {% block_field "paragraph" %}<p>Answer 2</p>{% endblock_field %}
            {% endblock_field %}
        {% endwagtail_block %}
    {% endblock_field %}

    {# Third item: using shorthand block_field with variable #}
    {% block_field "items" %}
        {% wagtail_block "AccordionItemBlock" %}
            {% block_field "title" title_var / %}
            {% block_field "content" %}
                {% block_field "inline_structblock" %}
                    {% block_field "heading" %}Inline Struct Heading{% endblock_field %}
                    {% block_field "content" %}<p>Inline Struct Content</p>{% endblock_field %}
                {% endblock_field %}
            {% endblock_field %}
        {% endwagtail_block %}
    {% endblock_field %}

    {# Fourth item: shorthand with string literal + ChooserBlocks #}
    {% block_field "items" %}
        {% wagtail_block "AccordionItemBlock" %}
            {% block_field "title" "Question 4" / %}
            {% block_field "content" %}
                {% block_field "image" test_image / %}
                {% block_field "document" test_document / %}
                {% block_field "page" test_page / %}
                {% block_field "paragraph" %}<p>ChooserBlocks work!</p>{% endblock_field %}
            {% endblock_field %}
        {% endwagtail_block %}
    {% endblock_field %}

{% endwagtail_block %}
```

## How It Works

The tag processes your template syntax into the raw value format Wagtail blocks expect, then calls `block.to_python()` and `block.render()`.

## Syntax Options

### Passing Field Values

**As kwargs** when the value is simple:

```jinja
{% wagtail_block "AccordionItemBlock" title="Question 1" %}
    {# ... #}
{% endwagtail_block %}
```

**As block_field with content** when you need template rendering:

```jinja
{% wagtail_block "AccordionItemBlock" %}
    {% block_field "title" %}Question {{ question_number }}{% endblock_field %}
    {# ... #}
{% endwagtail_block %}
```

**As block_field shorthand** when passing simple values or variables:

```jinja
{% wagtail_block "AccordionItemBlock" %}
    {% block_field "title" "My Title" / %}
    {# Or from context: #}
    {% block_field "title" my_title_var / %}
{% endwagtail_block %}
```

### Block Types

**StructBlock** - Use `{% block_field %}` for each field:

```jinja
{% wagtail_block "AccordionItemBlock" title="Question" %}
    {% block_field "content" %}
        {% block_field "paragraph" %}<p>Answer</p>{% endblock_field %}
    {% endblock_field %}
{% endwagtail_block %}
```

**ListBlock** - Repeat `{% block_field %}` with the same name:

```jinja
{% wagtail_block "AccordionBlock" %}
    {% block_field "items" %}
        {% wagtail_block "AccordionItemBlock" title="Q1" %}...{% endwagtail_block %}
    {% endblock_field %}
    {% block_field "items" %}
        {% wagtail_block "AccordionItemBlock" title="Q2" %}...{% endwagtail_block %}
    {% endblock_field %}
{% endwagtail_block %}
```

**StreamBlock** - Use nested `{% block_field %}` for typed content:

```jinja
{% block_field "content" %}
    {% block_field "paragraph" %}<p>First paragraph</p>{% endblock_field %}
    {% block_field "paragraph" %}<p>Second paragraph</p>{% endblock_field %}
    {% block_field "image" my_image / %}
    {% block_field "page" my_page / %}
    {% block_field "document" my_document / %}
    {% block_field "inline_structblock" %}
        {% block_field "heading" "Nested Heading" / %}
        {% block_field "content" %}<p>Nested content</p>{% endblock_field %}
    {% endblock_field %}
{% endblock_field %}
```

**ChooserBlock fields** (PageChooserBlock, ImageChooserBlock, DocumentChooserBlock) - Pass pk or model instance:

```jinja
{# Using pk #}
{% block_field "page" 123 / %}

{# Using model instance (pk extracted automatically) #}
{% block_field "page" my_page / %}
```

## Use in Both Places

The same blocks work in Wagtail StreamFields:

```python
from wagtail.models import Page
from wagtail.fields import StreamField
from myapp.blocks import AccordionBlock

class HomePage(Page):
    body = StreamField([
        ('accordion', AccordionBlock()),
    ])
```

And in regular Django views:

```jinja
{% load wagtail_block_components %}

{% wagtail_block "AccordionBlock" %}
    {# ... #}
{% endwagtail_block %}
```
