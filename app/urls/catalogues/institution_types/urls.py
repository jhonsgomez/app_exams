from django.urls import path
from app.views import (
    institution_types_table,
    institution_types_create,
    institution_types_update,
    institution_types_save,
    institution_types_delete,
)

urlpatterns = [
    path("", institution_types_table, name="institution_types_table"),
    path("create/", institution_types_create, name="institution_types_create"),
    path("update/<int:institution_type_id>/", institution_types_update, name="institution_types_update"),
    path("save/", institution_types_save, name="institution_types_save"),
    path("delete/<int:institution_type_id>/", institution_types_delete, name="institution_types_delete"),
]
