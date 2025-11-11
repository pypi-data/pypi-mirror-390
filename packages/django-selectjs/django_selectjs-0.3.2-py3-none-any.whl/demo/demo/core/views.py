from book_manager.models import Book
from django.contrib import messages
from django.urls import reverse_lazy
from django.views.generic import FormView, TemplateView, UpdateView, View
from wildewidgets import (
    Block,
    BreadcrumbBlock,
    CardWidget,
    CrispyFormWidget,
    PageHeader,
)
from wildewidgets.views import JsonResponse

from demo.core.forms import BookForm, FakeAPIForm

from .wildewidgets import BaseBreadcrumbs, BookModelTable, DemoStandardMixin


class WildewidgetsView(DemoStandardMixin, TemplateView):
    menu_item: str = "Home"

    def get_content(self) -> Block:
        return Block(
            PageHeader(
                header_text="Books",
                badge_text=Book.objects.count(),
                badge_class="success",
            ),
            CardWidget(widget=BookModelTable()),
        )

    def get_breadcrumbs(self) -> BreadcrumbBlock:
        breadcrumbs = BaseBreadcrumbs()
        breadcrumbs.add_breadcrumb("Django SelectJS Demo")
        return breadcrumbs


class BookEditView(DemoStandardMixin, UpdateView):
    menu_item: str = "Home"
    model = Book
    form_class = BookForm
    success_url = reverse_lazy("core:home")

    def post(self, request, *args, **kwargs):
        print(request.POST)
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        print(form.cleaned_data)
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def get_content(self) -> Block:
        return Block(
            PageHeader(
                header_text="Edit Book",
            ),
            CardWidget(widget=CrispyFormWidget(), overflow="visible"),
        )

    def get_breadcrumbs(self) -> BreadcrumbBlock:
        breadcrumbs = BaseBreadcrumbs()
        breadcrumbs.add_breadcrumb("Django SelectJS Demo")
        return breadcrumbs


class ExternalAPIView(DemoStandardMixin, FormView):
    menu_item: str = "External API"
    form_class = FakeAPIForm
    success_url = reverse_lazy("core:external_api")

    def get_content(self) -> Block:
        return Block(
            PageHeader(
                header_text="External API Demo",
            ),
            CardWidget(
                widget=CrispyFormWidget(form=self.form_class()),
                overflow="visible",
            ),
        )

    def form_valid(self, form):
        widget = form.cleaned_data["main_widget"]
        sub_widgets = form.cleaned_data["sub_widgets"]
        msg = f"Widget: {widget}\nSub Widgets: {', '.join(sub_widgets)}"
        messages.success(self.request, msg)

        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def get_breadcrumbs(self) -> BreadcrumbBlock:
        breadcrumbs = BaseBreadcrumbs()
        breadcrumbs.add_breadcrumb("External API Demo")
        return breadcrumbs


class FakeAPIView(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        widgets = [
            {"id": "simple-table", "text": "Simple Table"},
            {"id": "card-table", "text": "Card Table"},
            {"id": "tabbed-widget", "text": "Tabbed Widget"},
            {"id": "form-widget", "text": "Form Widget"},
            {"id": "stat-widget", "text": "Stat Widget"},
            {"id": "progress-widget", "text": "Progress Bar"},
            {"id": "search-table", "text": "Search Table"},
            {"id": "calendar-widget", "text": "Calendar Widget"},
            {"id": "user-profile", "text": "User Profile Card"},
            {"id": "activity-feed", "text": "Activity Feed"},
        ]
        if query:
            filtered_widgets = [
                w for w in widgets if query.lower() in w["text"].lower()
            ]
        else:
            filtered_widgets = []
        return JsonResponse({"results": filtered_widgets})
