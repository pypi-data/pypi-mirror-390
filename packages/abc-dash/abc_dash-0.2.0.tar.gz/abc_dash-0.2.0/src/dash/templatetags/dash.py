from django import template
from django.apps import apps
from django.conf import settings
from django.contrib.admin.utils import display_for_field
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from django.utils import formats
from django.utils.html import format_html, linebreaks, mark_safe

register = template.Library()


@register.simple_tag
def service_name():
    name = getattr(settings, "SERVICE_NAME", "")
    if name:
        return name
    return ""


def display_for_field_mod(field, value):
    """
    display_for_field に加え、

    - もとの値に改行が含まれるときは `<p>` に変換。
    - URLFieldの場合は
    """
    if isinstance(value, str) and "\n" in value:
        value = mark_safe(linebreaks(value))
    elif isinstance(field, models.URLField):
        value = format_html(
            """<a href="{0}" target="_blank" rel="noopener noreferrer">{0}</a>""",
            value
        )
    elif isinstance(field, models.FileField) and value:
        value = format_html(
            """<a href="{0}" target="_blank" rel="noopener noreferrer">{1}</a>""",
            value.url,
            value
        )
    else:
        value = display_for_field(value, field, "-")
    return value


@register.simple_tag
def table_row(obj, field_name):
    if not obj:
        return ""

    field = obj._meta.get_field(field_name)
    label = field.verbose_name
    value = getattr(obj, field_name)
    value = display_for_field_mod(field, value)
    return format_html(
        """<tr><th scope="row">{0}</th><td>{1}</td></tr>""",
        label, value
    )


@register.simple_tag
def display_for(obj, field_name):
    if not obj:
        return ""

    field = obj._meta.get_field(field_name)
    value = getattr(obj, field_name)
    return display_for_field_mod(field, value)


@register.simple_tag(takes_context=True)
def field_verbose_name(context, obj_or_field_name, field_name=None):
    if field_name:
        obj = obj_or_field_name
    else:
        obj = None
        field_name = obj_or_field_name

    if obj is None or obj == "":
        view = context.get("view", None)
        if view and getattr(view, "model", None):
            model_class = view.model
            meta_class = model_class._meta
        else:
            return ""
    elif isinstance(obj, str) and "." in obj:
        model_class = apps.get_model(obj)
        meta_class = model_class._meta
    else:
        model_class = obj.__class__
        meta_class = obj._meta

    try:
        return meta_class.get_field(field_name).verbose_name
    except FieldDoesNotExist:
        return field_name


@register.simple_tag
def filefield_link(obj, field_name):
    """
    [フィールド名](ファイルURL) の形でリンクにする

    ファイルがない場合はフィールド名だけ返す
    """
    value = getattr(obj, field_name)
    field = obj._meta.get_field(field_name)
    if not value:
        return field.verbose_name

    return format_html(
        """<a href="{0}" target="_blank" rel="noopener noreferrer">{1}</a>""",
        value.url,
        field.verbose_name,
    )


def with_unit(value, unit):
    if not value and value != 0:
        return ""

    space = " " if unit.isascii() else ""

    return format_html(
        """<span class="number">{}</span>{}<span class="unit">{}</span>""",
        intcomma(value), space, unit
    )


@register.simple_tag(name="yen_format")
def as_yen_format(value, with_tax=None):
    return with_unit(value, "円")


@register.filter(expects_localtime=True)
def time_tag(dt):
    if not dt:
        return ""
    label = formats.localize(dt)
    return format_html(
        """<time datetime="{}">{}</time>""",
        dt.isoformat(),
        label
    )


def _status_tag(variant, label):
    return format_html(
        """<span class="badge text-bg-{0}">{1}</span>""",
        variant, label
    )


@register.simple_tag
def status_tag(obj):
    if hasattr(obj, "get_status_severity"):
        variant = obj.get_status_severity()
    else:
        return ""

    return _status_tag(variant, obj.get_status_display())
