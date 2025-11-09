from django.urls import path  # type: ignore

from . import views

app_name = "blogs"

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("category/<str:category>/", views.CategoryView.as_view(), name="category"),
    path("detail/<int:pk>/", views.BlogDetailView.as_view(), name="detail"),
    path("private_index/", views.PrivateIndexView.as_view(), name="private_index"),
    path(
        "private_index/private_detail/<int:pk>/",
        views.PrivateDetailView.as_view(),
        name="private_detail",
    ),
    path("new_blog/", views.BlogFormView.as_view(), name="new_blog"),
    path("edit/<int:pk>/", views.EditBlogFormView.as_view(), name="edit"),
    path("release/<pk>/", views.release, name="release"),
    path("private/<pk>/", views.private, name="private"),
]
