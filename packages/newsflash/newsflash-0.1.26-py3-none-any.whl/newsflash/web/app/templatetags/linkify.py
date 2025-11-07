import re
from django import template
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.template.loader import render_to_string


register = template.Library()

URL_PATTERN = re.compile(r"\[([^\]]+)\]\((https://[^\s)]+)\)")


@register.filter(name="linkify")
@stringfilter
def linkify(value: str) -> str:
    def replace_url(match):
        text = match.group(1)
        url = match.group(2)
        return render_to_string("app/link.html", context={"url": url, "text": text})

    result = URL_PATTERN.sub(replace_url, value)
    return mark_safe(result)
