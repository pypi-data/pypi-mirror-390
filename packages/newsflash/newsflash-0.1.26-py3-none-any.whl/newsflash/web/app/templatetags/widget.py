from django import template

register = template.Library()


@register.simple_tag(takes_context=True, name="widget")
def widget(context: dict, widget_id: str):
    """Insert widget from ID."""
    if widget_id in context:
        return context[widget_id]
    else:
        return widget_id
