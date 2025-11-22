from django.urls import path
from app.views import (
    questions_create,
    questions_update,
    questions_save,
    questions_deactivate,
    questions_activate,
    questions_delete,
)


urlpatterns = [
    path("create/<int:question_bank_id>/", questions_create, name="questions_create"),
    path("update/<int:question_bank_id>/<int:question_id>/", questions_update, name="questions_update"),
    path("save/", questions_save, name="questions_save"),
    path("deactivate/<int:question_bank_id>/<int:question_id>/", questions_deactivate, name="questions_deactivate"),
    path("activate/<int:question_bank_id>/<int:question_id>/", questions_activate, name="questions_activate"),
    path("delete/<int:question_bank_id>/<int:question_id>/", questions_delete, name="questions_delete"),
]
