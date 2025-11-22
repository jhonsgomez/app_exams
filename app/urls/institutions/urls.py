from django.urls import path
from app.views import (
    institutions_table,
    institutions_create,
    institutions_update,
    institutions_save,
    institutions_delete,
    institutions_info,
)

urlpatterns = [
    path("", institutions_table, name="institutions_table"),
    path("create/", institutions_create, name="institutions_create"),
    path("info/<int:institution_id>/", institutions_info, name="institutions_info"),
    path("update/<int:institution_id>/", institutions_update, name="institutions_update"),
    path("save/", institutions_save, name="institutions_save"),
    path("delete/<int:institution_id>/", institutions_delete, name="institutions_delete"),
]
