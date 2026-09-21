from django.urls import path
from app.views import (
    available_exams,

    my_attempts,
    exam_students,
    
    export_attempt_csv,
    export_exam_results,
    
    start_exam,
    take_exam,
    process_answer,
    exam_feedback,
    exam_summary,
    
    export_exam_report,
)


urlpatterns = [
    # URLs para intentos de examen
    path('available/', available_exams, name='exams_available'),
       
    # URLs para tomar un intento de examen, enviar respuestas y ver resultados
    path('exam/<int:exam_id>/start/', start_exam, name='exam_start'),
    path('<int:attempt_id>/question/', take_exam, name='exam_take'),
    path('<int:attempt_id>/process/', process_answer, name='exam_process'),
    
    path('<int:attempt_id>/feedback/<int:response_id>/', exam_feedback, name='exam_feedback'),
    path('<int:attempt_id>/summary/', exam_summary, name='exam_summary'),
    
    # URLs para ver los intentos de un estudiante específico
    path('<int:student_id>/<int:exam_id>/', my_attempts, name='my_attempts'),
    path('<int:student_id>/', my_attempts, name='my_attempts'),
    
    # URLs para ver los estudiantes que han intentado un examen específico
    path('exam/<int:exam_id>/students/', exam_students, name='exam_students'),
    
    # URLs para exportar datos a CSV   
    path('exams/attempts/<int:attempt_id>/export-csv/', export_attempt_csv, name='attempt_export_csv'),
    path('exams/<int:exam_id>/export-results/', export_exam_results, name='exam_export_results'),
    
    # URL para exportar reporte completo de un examen a Excel
    path('exams/<int:exam_id>/export-report/', export_exam_report, name='exam_export_report'),
]