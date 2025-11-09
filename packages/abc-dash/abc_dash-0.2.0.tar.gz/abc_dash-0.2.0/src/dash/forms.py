from django import forms
from django.utils.text import camel_case_to_spaces

from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.bootstrap import InlineCheckboxes, InlineRadios


def camel_case_to_kebabs(value):
    return camel_case_to_spaces(value).lower().replace(" ", "-")


class SimpleFormHelper(FormHelper):
    def __init__(self, *args, submit_label=None, **kwargs):
        if submit_label is None:
            submit_label = "保存"
        form_class = kwargs.pop("form_class", None)
        super().__init__(*args, **kwargs)
        btn = Submit("submit", submit_label)
        btn.field_classes = "btn btn-primary"
        self.add_input(btn)
        self.wrapper_class = "form-field"
        self.field_class = "field-wrapper"
        if not hasattr(self, "form_class"):
            self.form_class = ""

        if getattr(self, "form", None):
            self.form_class += camel_case_to_kebabs(self.form.__class__.__name__)

        if form_class:
            self.form_class += " "
            self.form_class += form_class


class ModelForm(forms.ModelForm):
    # この数以下なら<select>の代わりにラジオボタンを使う
    SELECT_RADIO_THRESHOLD = 10

    INLINE_CHECKBOX_THRESHOLD = 5

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if getattr(self, "submit_label", None):
            submit_label = self.submit_label
        elif hasattr(self, "instance"):
            submit_label = "追加" if self.instance._state.adding else "更新"
        else:
            submit_label = None
        self.helper = SimpleFormHelper(form=self, submit_label=submit_label)
        self.tweak_choice_fields()
        self.tweak_date_fields()

    def tweak_date_fields(self):
        for _, field in self.fields.items():
            if isinstance(field, forms.DateField):
                field.widget = forms.DateInput(attrs={"type": "date"})

    def tweak_choice_fields(self):
        for fieldname, field in self.fields.items():
            if isinstance(field, forms.BooleanField):
                continue

            if isinstance(field.widget, forms.Select):
                # BlankChoiceIteratorの時はselectのままにしないと空欄にできない
                if isinstance(field.choices, list) and len(field.choices) < self.SELECT_RADIO_THRESHOLD:
                    field.widget = forms.RadioSelect()

            if isinstance(field.widget, (forms.CheckboxInput, forms.RadioSelect)) and not isinstance(field.choices, forms.models.ModelChoiceIterator):
                # checkbox・radioでの不要な "---" を除く。
                # ただし ModelChoiceIterator の場合は __iter__ してしまうと確定してしまうので除外。
                field.choices = [
                    choice for choice in field.choices if choice[0] != ""
                ]

                if len(field.choices) < self.INLINE_CHECKBOX_THRESHOLD:
                    layout_cls = InlineCheckboxes if isinstance(field.widget, forms.CheckboxInput) else InlineRadios
                    self.helper[fieldname].wrap(layout_cls)


class CrispyFilterMixin:
    form_direction = "horizontal"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        helper = SimpleFormHelper(form=self._get_form(), submit_label="検索")
        helper.form_method = "get"
        if self.form_direction == "horizontal":
            helper.form_class = "form--search form-horizontal"
            helper.label_class = "col-2"
            helper.field_class = "col-10"
        self._get_form().helper = helper

    def _get_form(self):
        return self.form
