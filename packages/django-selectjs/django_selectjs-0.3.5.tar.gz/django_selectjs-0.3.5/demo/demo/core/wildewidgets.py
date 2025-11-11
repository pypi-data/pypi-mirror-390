from typing import List, Tuple

from academy_theme.wildewidgets import AcademyThemeMainMenu
from book_manager.models import Book
from django.templatetags.static import static
from django.urls import reverse
from wildewidgets import (
    ActionButtonModelTable,
    BreadcrumbBlock,
    MenuMixin,
    RowDjangoUrlButton,
    StandardWidgetMixin,
)


class MainMenu(AcademyThemeMainMenu):
    brand_image: str = static("/images/dark_logo.png")
    brand_text: str = "Django SelectJS Demo"
    items: List[Tuple[str, str]] = [
        ("Home", "core:home"),
        ("External API", "core:external_api"),
    ]


class BaseBreadcrumbs(BreadcrumbBlock):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_breadcrumb("Home", reverse("core:home"))


class DemoStandardMixin(StandardWidgetMixin, MenuMixin):
    template_name = "core/base.html"
    menu_class = MainMenu


class BookModelTable(ActionButtonModelTable):
    model = Book
    fields = ["title", "authors__full_name", "isbn"]
    verbose_names = {"authors__full_name": "Authors"}
    striped = True
    actions = [
        RowDjangoUrlButton(
            text="Edit",
            color="primary",
            url_path="core:edit_book",
            url_args=["pk"],
        ),
    ]

    def render_authors__full_name_column(self, row, column):
        authors = row.authors.all()
        author_names = [author.full_name for author in authors]
        author_string = "<br>".join(author_names)
        return author_string
