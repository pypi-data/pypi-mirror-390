from django import forms


class ModelM2MSearchSelectWidget(forms.SelectMultiple):
    template_name = "widgets/model_many_to_many_search_select.html"

    def __init__(
        self,
        attrs=None,
        model=None,
        search_field="name",
        api_endpoint=None,
        min_length=3,
    ):
        super().__init__(attrs)
        self.model = model
        self.search_field = search_field
        self.api_endpoint = api_endpoint
        self.min_length = min_length

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        if self.model:
            context["widget"]["model"] = self.model._meta.model_name
            context["widget"]["app_label"] = self.model._meta.app_label
        else:
            context["widget"]["model"] = None
            context["widget"]["app_label"] = None
        context["widget"]["search_field"] = self.search_field
        context["widget"]["api_endpoint"] = self.api_endpoint
        context["widget"]["min_length"] = self.min_length

        # Handle multiple selected values
        # value might be a list of PKs or a queryset
        selected_items = []
        if value:
            # Convert queryset to list of PKs if needed
            if hasattr(value, "__iter__") and not isinstance(
                value, (str, bytes)
            ):
                # Handle queryset or list
                pks = []
                for item in value:
                    if hasattr(item, "pk"):
                        # It's a model instance
                        pks.append(item.pk)
                    else:
                        # It's already a PK
                        pks.append(item)
            else:
                pks = [value] if value else []

            # Fetch objects for display
            for pk in pks:
                if pk:
                    try:
                        obj = self.model.objects.get(pk=pk)
                        selected_items.append({"id": pk, "text": str(obj)})
                    except (self.model.DoesNotExist, ValueError, TypeError):
                        pass

        context["widget"]["selected_items"] = selected_items
        return context

    class Media:
        css = {"all": ("css/model_many_to_many_search_select.css",)}
        js = ("js/model_many_to_many_search_select.js",)
