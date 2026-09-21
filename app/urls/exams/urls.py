from django.urls import path
from app.views import (
    exams_table,
    exams_create,
    exams_update,
    exams_save,
    exams_deactivate,
    exams_activate,
    exams_delete,
)

urlpatterns = [
    path("", exams_table, name="exams_table"),
    path("create/", exams_create, name="exams_create"),
    path("update/<int:exam_id>/", exams_update, name="exams_update"),
    path("save/", exams_save, name="exams_save"),
    path("deactivate/<int:exam_id>/", exams_deactivate, name="exams_deactivate"),
    path("activate/<int:exam_id>/", exams_activate, name="exams_activate"),
    path("delete/<int:exam_id>/", exams_delete, name="exams_delete"),
]
