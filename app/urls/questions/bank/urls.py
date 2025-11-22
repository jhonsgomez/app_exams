from django.urls import path
from app.views import (
    questions_bank_table,
    questions_bank_create,
    questions_bank_update,
    questions_bank_save,
    questions_bank_delete,
    questions_bank_deactivate,
    questions_bank_activate,
    questions_bank_questions
)

urlpatterns = [
    path('', questions_bank_table, name='questions_bank_table'),
    path('create/', questions_bank_create, name='questions_bank_create'),
    path('update/<int:question_bank_id>/', questions_bank_update, name='questions_bank_update'),
    path('save/', questions_bank_save, name='questions_bank_save'),
    path('delete/<int:question_bank_id>/', questions_bank_delete, name='questions_bank_delete'),
    path('deactivate/<int:question_bank_id>/', questions_bank_deactivate, name='questions_bank_deactivate'),
    path('activate/<int:question_bank_id>/', questions_bank_activate, name='questions_bank_activate'),
    path('questions/<int:question_bank_id>/', questions_bank_questions, name='questions_bank_questions'),
]
