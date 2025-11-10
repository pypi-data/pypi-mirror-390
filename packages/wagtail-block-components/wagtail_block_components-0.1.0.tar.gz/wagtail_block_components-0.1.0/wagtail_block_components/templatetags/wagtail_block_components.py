import logging

from django import template
from django.db import models
from django.template import Context
from django.template.base import Node, NodeList, token_kwargs

from wagtail.blocks import (
    ChooserBlock,
    FieldBlock,
    ListBlock,
    StaticBlock,
    StreamBlock,
    StructBlock,
)
from wagtail.templatetags.wagtailcore_tags import IncludeBlockNode
from wagtail_block_components.registry import registry

logger = logging.getLogger(__name__)
register = template.Library()


class FieldNode(Node):
    def __init__(self, field_name, nodelist, value_var=None):
        self.field_name = field_name
        self.nodelist = nodelist
        self.value_var = value_var

    def render(self, context):
        return ""


class WagtailBlockNode(Node):
    def __init__(self, block_class, kwargs, nodelist):
        self.block_class = block_class
        self.kwargs = kwargs
        self.nodelist = nodelist

    def _normalize_chooser_value(self, value, field_block):
        if isinstance(field_block, ChooserBlock) and isinstance(value, models.Model):
            return value.pk
        return value

    def _extract_field_value(self, field_node, context, parent_block=None):
        # Get the field block from parent if available
        field_block = None
        if parent_block and isinstance(parent_block, StructBlock):
            field_block = parent_block.child_blocks.get(field_node.field_name)

        # Handle shorthand syntax: {% block_field "name" value %}
        if field_node.value_var:
            return field_node.value_var.resolve(context)

        # Check for nested WagtailBlockNode
        block_nodes = [
            n for n in field_node.nodelist if isinstance(n, WagtailBlockNode)
        ]
        if block_nodes:
            if len(block_nodes) > 1:
                raise template.TemplateSyntaxError(
                    f"Field '{field_node.field_name}' has multiple blocks. "
                    "Use multiple {% block_field %} tags for list fields."
                )

            # Build the nested block's raw value
            nested_block_node = block_nodes[0]
            block_name = nested_block_node.block_class.resolve(context)
            block_class = registry.get(block_name)
            if not block_class:
                return None

            block_instance = block_class()
            raw_value = self._collect_fields_from_node(
                nested_block_node, context, block_instance
            )

            # StreamBlock expects {"type": "name", "value": raw} format
            if field_block and isinstance(field_block, StreamBlock):
                return {"type": block_name, "value": raw_value}

            # ListBlock and StructBlock just expect the raw value
            return raw_value

        # Check for nested FieldNodes
        nested_fields = [n for n in field_node.nodelist if isinstance(n, FieldNode)]
        if nested_fields:
            # StreamBlock with nested field syntax: {% block_field "content" %}{% block_field "paragraph" %}...
            if field_block and isinstance(field_block, StreamBlock):
                # Multiple nested fields = multiple StreamBlock items
                stream_items = []
                for child_field in nested_fields:
                    child_block_name = child_field.field_name

                    if child_block_name not in field_block.child_blocks:
                        raise template.TemplateSyntaxError(
                            f"'{child_block_name}' is not in StreamBlock '{field_node.field_name}'"
                        )

                    # Get the child block for normalization
                    child_block = field_block.child_blocks.get(child_block_name)

                    # Recursively extract the child value
                    child_value = self._extract_field_value(
                        child_field, context, field_block
                    )

                    # Normalize ChooserBlock values (only if it's a ChooserBlock)
                    if isinstance(child_block, ChooserBlock):
                        child_value = self._normalize_chooser_value(
                            child_value, child_block
                        )

                    # Add in StreamBlock format
                    stream_items.append(
                        {"type": child_block_name, "value": child_value}
                    )

                # Always return list for StreamBlock (field collection will handle it)
                return stream_items

            # StructBlock with nested fields - build dict
            return {
                nf.field_name: self._extract_field_value(nf, context, field_block)
                for nf in nested_fields
            }

        # No nested blocks or fields - render content as raw value
        # This works for FieldBlock (CharBlock, RichTextBlock, etc.)
        return field_node.nodelist.render(context).strip()

    def _collect_fields_from_node(self, block_node, context, block_instance):
        kwargs = {}
        for k, v in block_node.kwargs.items():
            resolved = v.resolve(context)
            # Normalize ChooserBlock values (instances → pk)
            if isinstance(block_instance, (StructBlock, StreamBlock)):
                field_block = block_instance.child_blocks.get(k)
                if isinstance(field_block, ChooserBlock):
                    resolved = self._normalize_chooser_value(resolved, field_block)
            kwargs[k] = resolved

        return self._collect_fields(
            block_node.nodelist, context, block_instance, kwargs
        )

    def _collect_fields(self, nodelist, context, block_instance, initial_kwargs=None):
        kwargs = initial_kwargs or {}

        field_nodes = [n for n in nodelist if isinstance(n, FieldNode)]

        # StaticBlock - no fields needed
        if isinstance(block_instance, StaticBlock):
            return None

        # FieldBlock - content is the value (not a dict)
        if isinstance(block_instance, FieldBlock) and not field_nodes:
            context_dict = context.flatten() if hasattr(context, "flatten") else {}
            return nodelist.render(Context(context_dict)).strip()

        # Collect field values - track occurrences separately from values
        field_values = {}
        field_occurrences = {}
        for field_node in field_nodes:
            value = self._extract_field_value(field_node, context, block_instance)

            if field_node.field_name not in field_values:
                field_values[field_node.field_name] = []
                field_occurrences[field_node.field_name] = 0

            field_occurrences[field_node.field_name] += 1

            # Normalize ChooserBlock values (instances → pk) - only for ChooserBlocks
            if isinstance(block_instance, (StructBlock, StreamBlock)):
                field_block = block_instance.child_blocks.get(field_node.field_name)
                if isinstance(field_block, ChooserBlock):
                    value = self._normalize_chooser_value(value, field_block)

            # If value is a list (from StreamBlock with multiple nested fields), extend instead of append
            if isinstance(value, list):
                field_values[field_node.field_name].extend(value)
            else:
                field_values[field_node.field_name].append(value)

        # Build raw value based on block type
        raw_value = {**kwargs}

        for field_name, values in field_values.items():
            # Get the field block to check its type
            field_block = None
            if isinstance(block_instance, (StructBlock, StreamBlock)):
                field_block = block_instance.child_blocks.get(field_name)

                # Log warning if field doesn't exist on the block
                if (
                    field_block is None
                    and field_name not in block_instance.child_blocks
                ):
                    block_class_name = block_instance.__class__.__name__
                    logger.warning(
                        f"Field '{field_name}' does not exist on {block_class_name}. "
                        f"Available fields: {', '.join(block_instance.child_blocks.keys())}"
                    )

            # Determine how to handle multiple values
            if field_block and isinstance(field_block, ListBlock):
                # ListBlock expects a list
                raw_value[field_name] = values
            elif field_block and isinstance(field_block, StreamBlock):
                # StreamBlock expects a list, but should only appear once as a field tag
                if field_occurrences.get(field_name, 0) > 1:
                    raise template.TemplateSyntaxError(
                        f"StreamBlock field '{field_name}' appears {field_occurrences[field_name]} times. "
                        f"StreamBlock fields should appear once with multiple nested block fields inside."
                    )
                raw_value[field_name] = values
            # Single value - unwrap from list
            elif len(values) == 1:
                raw_value[field_name] = values[0]
            # Multiple values for same field - keep as list
            else:
                raw_value[field_name] = values

        return raw_value

    def render(self, context):
        """Build raw value and let Wagtail's to_python() and render() handle the rest"""
        try:
            block_name = self.block_class.resolve(context)
        except template.VariableDoesNotExist:
            return ""

        block_class = registry.get(block_name)
        if not block_class:
            return ""

        block_instance = block_class()

        # Collect fields into raw value
        raw_value = self._collect_fields_from_node(self, context, block_instance)

        # Let Wagtail convert to proper block value via to_python()
        block_value = block_instance.to_python(raw_value)

        # Delegate rendering to Wagtail's IncludeBlockNode
        class BlockValueWrapper:
            def resolve(self, ctx):
                return block_value

        include_node = IncludeBlockNode(
            block_var=BlockValueWrapper(), extra_context=None, use_parent_context=True
        )
        return include_node.render(context)


@register.tag(name="wagtail_block")
def do_wagtail_block(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError(
            f"'{bits[0]}' tag requires a block class argument"
        )

    block_class = parser.compile_filter(bits[1])
    is_self_closing = bits[-1] == "/"

    if is_self_closing:
        bits = bits[:-1]

    kwargs = token_kwargs(bits[2:], parser)
    nodelist = NodeList() if is_self_closing else parser.parse(("endwagtail_block",))

    if not is_self_closing:
        parser.delete_first_token()

    return WagtailBlockNode(block_class, kwargs, nodelist)


@register.tag(name="block_field")
def do_block_field(parser, token):
    bits = token.split_contents()
    if len(bits) < 2:
        raise template.TemplateSyntaxError(
            f"'{bits[0]}' tag requires at least one argument"
        )

    # Check for self-closing syntax
    is_self_closing = bits[-1] == "/"
    if is_self_closing:
        bits = bits[:-1]

    if len(bits) < 2 or len(bits) > 3:
        raise template.TemplateSyntaxError(
            f"'{bits[0]}' tag requires one or two arguments"
        )

    field_name = bits[1].strip("\"'")

    # Shorthand syntax: {% block_field "name" value / %}
    if len(bits) == 3:
        value_var = parser.compile_filter(bits[2])
        return FieldNode(field_name, NodeList(), value_var)

    # Self-closing with no value: {% block_field "name" / %}
    if is_self_closing:
        return FieldNode(field_name, NodeList())

    # Standard syntax: {% block_field "name" %}...{% endblock_field %}
    nodelist = parser.parse(("endblock_field",))
    parser.delete_first_token()

    return FieldNode(field_name, nodelist)
