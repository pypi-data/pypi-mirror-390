from django.template import Context, Template, TemplateSyntaxError
from django.test import TestCase

from wagtail.documents.models import Document
from wagtail.images.models import Image
from wagtail.models import Page
from wagtail.test.utils import WagtailTestUtils


class AccordionBlockTestCase(WagtailTestUtils, TestCase):
    """Tests for AccordionBlock demonstrating all syntax options"""

    fixtures = ["test.json"]

    def render_template(self, template_string, context=None):
        """Helper to render a template string"""
        if context is None:
            context = {}
        template = Template(template_string)
        return template.render(Context(context))

    def test_all_syntax_options(self):
        """
        Comprehensive test showing all supported syntax variations:
        - Self-closing blocks with kwargs
        - Block fields with content
        - Block fields with variables (shorthand)
        - Block fields with string literals (shorthand)
        - Multiple StreamBlock items (ListBlock)
        - Nested StructBlocks
        - ChooserBlock fields (page, image, document)
        """
        # Get test instances from Wagtail's test fixtures
        image = Image.objects.first()
        document = Document.objects.first()
        page = Page.objects.first()

        template_string = """
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
        """
        result = self.render_template(
            template_string,
            {
                "title_var": "Question 3",
                "test_image": image,
                "test_document": document,
                "test_page": page,
            },
        )

        # Self-closing accordion (empty)
        self.assertIn('class="accordion"', result)
        self.assertIn('id="accordion-', result)

        # Empty accordion item
        self.assertIn('<h3 class="accordion-title">Empty Item</h3>', result)

        # Full accordion with all variations
        self.assertIn('<h3 class="accordion-title">Question 1</h3>', result)
        self.assertIn('<h3 class="accordion-title">Question 2</h3>', result)
        self.assertIn('<h3 class="accordion-title">Question 3</h3>', result)
        self.assertIn('<h3 class="accordion-title">Question 4</h3>', result)
        self.assertIn("<p>Answer 1 part 1</p>", result)
        self.assertIn("<p>Answer 1 part 2</p>", result)
        self.assertIn("<p>Answer 2</p>", result)
        self.assertIn("Inline Struct Heading", result)
        self.assertIn("<p>Inline Struct Content</p>", result)
        self.assertIn("<p>ChooserBlocks work!</p>", result)

    def test_non_existent_field(self):
        """Test that using a non-existent field name logs a warning"""
        template_string = """
            {% load wagtail_block_components %}
            {% wagtail_block "AccordionBlock" %}
                {% block_field "non_existent_field" %}Test{% endblock_field %}
            {% endwagtail_block %}
        """
        # Should log a warning and still render
        with self.assertLogs(
            "wagtail_block_components.templatetags.wagtail_block_components",
            level="WARNING",
        ) as cm:
            result = self.render_template(template_string)
            self.assertIn('class="accordion"', result)

        # Check warning message
        self.assertEqual(len(cm.output), 1)
        self.assertIn(
            "Field 'non_existent_field' does not exist on AccordionBlock", cm.output[0]
        )
        self.assertIn("Available fields: items", cm.output[0])

    def test_streamblock_field_multiple_times_raises_error(self):
        """Test that using StreamBlock field multiple times raises an error"""
        template_string = """
            {% load wagtail_block_components %}
            {% wagtail_block "AccordionItemBlock" title="Test" %}
                {% block_field "content" %}
                    {% block_field "paragraph" %}<p>First</p>{% endblock_field %}
                {% endblock_field %}
                {% block_field "content" %}
                    {% block_field "paragraph" %}<p>Second</p>{% endblock_field %}
                {% endblock_field %}
            {% endwagtail_block %}
        """
        with self.assertRaises(TemplateSyntaxError) as cm:
            self.render_template(template_string)
        self.assertIn("StreamBlock field 'content' appears 2 times", str(cm.exception))
