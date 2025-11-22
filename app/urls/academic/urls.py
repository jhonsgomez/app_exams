from django.urls import path
from app.views import (
    academic_departments_table,
    academic_departments_create,
    academic_departments_update,
    academic_departments_save,
    academic_departments_delete,
)

urlpatterns = [
    path("", academic_departments_table, name="academic_departments_table"),
    path("create/", academic_departments_create, name="academic_departments_create"),
    path("update/<int:academic_department_id>/", academic_departments_update, name="academic_departments_update"),
    path("save/", academic_departments_save, name="academic_departments_save"),
    path("delete/<int:academic_department_id>/", academic_departments_delete, name="academic_departments_delete"),
]
