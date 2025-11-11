from django.urls import path
from wildewidgets import WildewidgetDispatch

from .views import BookEditView, ExternalAPIView, FakeAPIView, WildewidgetsView

app_name = "core"

urlpatterns = [
    path(
        "wildewidgets_json",
        WildewidgetDispatch.as_view(),
        name="wildewidgets_json",
    ),
    path("", WildewidgetsView.as_view(), name="home"),
    path("book/<int:pk>/edit/", BookEditView.as_view(), name="edit_book"),
    path("fake-api/", FakeAPIView.as_view(), name="fake_api"),
    path("external-api/", ExternalAPIView.as_view(), name="external_api"),
]
