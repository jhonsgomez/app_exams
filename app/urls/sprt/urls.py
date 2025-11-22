from django.urls import path
from app.views import (
    available_exams,
    start_attempt,
    take_attempt,
    submit_answer,
    attempt_results,
    my_attempts,
    abandon_attempt,
    exam_students,
    export_attempt_csv,
    export_exam_results,
)


urlpatterns = [
    # URLs para intentos de examen
    path('available/', available_exams, name='exams_available'),
    path('<int:exam_id>/start/', start_attempt, name='attempt_start'),
    path('attempts/<int:attempt_id>/', take_attempt, name='attempt_take'),
    path('attempts/<int:attempt_id>/submit/', submit_answer, name='attempt_submit'),
    path('attempts/<int:attempt_id>/<int:student_id>/results/', attempt_results, name='attempt_results'),
    path('attempts/<int:attempt_id>/abandon/', abandon_attempt, name='attempt_abandon'),
    path('my-attempts/<int:student_id>/<int:exam_id>/', my_attempts, name='my_attempts'),
    path('my-attempts/<int:student_id>/', my_attempts, name='my_attempts'),
    path('exam/<int:exam_id>/students/', exam_students, name='exam_students'),   
    path('exams/attempts/<int:attempt_id>/export-csv/', export_attempt_csv, name='attempt_export_csv'),
    path('exams/<int:exam_id>/export-results/', export_exam_results, name='exam_export_results'),
]