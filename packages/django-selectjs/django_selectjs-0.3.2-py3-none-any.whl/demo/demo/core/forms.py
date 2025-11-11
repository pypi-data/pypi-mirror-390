from book_manager.models import Author, Binding, Book, Publisher
from crispy_bootstrap5.bootstrap5 import FloatingField
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    ButtonHolder,
    Field,
    Fieldset,
    Layout,
    Submit,
)
from django import forms
from django.urls import reverse_lazy
from selectjs.widgets import (
    ModelM2MSearchSelectWidget,
    ModelSearchSelectWidget,
)


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ["title", "binding", "publisher", "authors"]
        widgets = {
            "authors": ModelM2MSearchSelectWidget(
                model=Author,
                search_field="full_name",
                api_endpoint=reverse_lazy("async_select_search"),
            ),
            "publisher": ModelSearchSelectWidget(
                model=Publisher,
                search_field="name",
                api_endpoint=reverse_lazy("async_select_search"),
            ),
            "binding": ModelSearchSelectWidget(
                model=Binding,
                search_field="name",
                api_endpoint=reverse_lazy("async_select_search"),
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Set up crispy forms helper
        self.helper = FormHelper()
        self.helper.form_class = "form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "Book Details",
                FloatingField("title", css_class="mb-2"),
                FloatingField("binding", css_class="mb-2"),
                FloatingField("publisher", css_class="mb-2"),
                Field("authors", css_class="mb-2"),
            ),
            ButtonHolder(
                Submit("submit", "Save", css_class="btn btn-primary"),
                css_class="d-flex flex-row justify-content-end w-100 mt-3",
            ),
        )


class FreeMultipleChoiceField(forms.MultipleChoiceField):
    def validate(self, value):
        # Skip the standard choice validation
        if self.required and not value:
            raise forms.ValidationError(
                self.error_messages["required"], code="required"
            )
        # Do not call super().validate(value) to avoid choices check


class FakeAPIForm(forms.Form):
    main_widget = forms.CharField(
        widget=ModelSearchSelectWidget(
            api_endpoint=reverse_lazy("core:fake_api"),
        )
    )
    sub_widgets = FreeMultipleChoiceField(
        widget=ModelM2MSearchSelectWidget(
            api_endpoint=reverse_lazy("core:fake_api"),
        )
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_class = "form"
        self.helper.form_method = "post"
        self.helper.layout = Layout(
            Fieldset(
                "External API Form",
                FloatingField("main_widget", css_class="mb-2"),
                Field("sub_widgets", css_class="mb-2"),
            ),
            ButtonHolder(
                Submit("submit", "Save", css_class="btn btn-primary"),
                css_class="d-flex flex-row justify-content-end w-100 mt-3",
            ),
        )
