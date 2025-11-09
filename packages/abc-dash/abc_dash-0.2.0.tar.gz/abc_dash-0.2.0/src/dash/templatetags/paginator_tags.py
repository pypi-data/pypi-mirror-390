from django import template
from django.utils.html import format_html, mark_safe

register = template.Library()


def bs5_pagination_item(content, url="", outer_html_class=""):
    if url:
        tmpl = """<a class="page-link" href="{url}">{content}</a>"""
    else:
        tmpl = """<a class="page-link">{content}</a>"""
    tmpl = """<li class="page-item {outer_html_class}">""" + tmpl + "</li>"
    context = {
        "content": content,
        "url": url,
        "outer_html_class": outer_html_class
    }
    return format_html(tmpl.strip(), **context)


@register.simple_tag(takes_context=True)
def bs5_pagination(context, paginator=None, page_obj=None):
    if paginator is None:
        paginator = context["paginator"]
    if page_obj is None:
        page_obj = context["page_obj"]

    html = []

    if page_obj.has_previous():
        html.append(bs5_pagination_item(
            mark_safe("""<i class="fas fa-chevron-left" aria-label="前へ"></i>"""),
            previous_page_url(context)
        ))

    page_range = paginator.get_elided_page_range(number=page_obj.number, on_each_side=1, on_ends=1)
    for num in page_range:
        content = str(num)
        outer_html_class = ""
        if num == page_obj.number:
            url = ""
            outer_html_class = " active"
        elif isinstance(num, int):
            url = numbered_page_url(context, num)
        else:
            url = ""
        html.append(bs5_pagination_item(
            content,
            url,
            outer_html_class
        ))

    if page_obj.has_next():
        html.append(bs5_pagination_item(
            mark_safe("""<i class="fas fa-chevron-right" aria-label="次へ"></i>"""),
            next_page_url(context)
        ))

    return mark_safe("\n".join(html))


def generate_page_url(context, attrname=None, num=None):
    page_obj = context["page_obj"]
    new_params = context["request"].GET.copy()
    if attrname:
        new_params["page"] = getattr(page_obj, attrname)()
    elif num:
        new_params["page"] = num
    else:
        raise ValueError("Either attrname or num required.")
    return "?" + new_params.urlencode()


@register.simple_tag(takes_context=True)
def previous_page_url(context):
    return generate_page_url(context, attrname="previous_page_number")


@register.simple_tag(takes_context=True)
def next_page_url(context):
    return generate_page_url(context, attrname="next_page_number")


@register.simple_tag(takes_context=True)
def numbered_page_url(context, num):
    return generate_page_url(context, num=int(num))
