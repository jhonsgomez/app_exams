from django.urls import path
from app.views import (
    students_table,
    students_create,
    students_update,
    students_save,
    students_activate,
    students_deactivate,
    students_delete,
)
    

urlpatterns = [
    path("", students_table, name="students_table"),
    path("create/", students_create, name="students_create"),
    path("update/<int:student_id>/", students_update, name="students_update"),
    path("save/", students_save, name="students_save"),
    path("activate/<int:student_id>/", students_activate, name="students_activate"),
    path("deactivate/<int:student_id>/", students_deactivate, name="students_deactivate"),
    path("delete/<int:student_id>/", students_delete, name="students_delete"),
]
