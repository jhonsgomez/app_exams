from django.db import models
from django.conf import settings

class ExamAttempt(models.Model):
    class StatusChoices(models.TextChoices):
        IN_PROGRESS = "in_progress", "En Progreso"
        PASSED = "passed", "Aprobado"
        FAILED = "failed", "Reprobado"

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, default=None)
    exam = models.ForeignKey('app.Exam', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=StatusChoices.choices, default=StatusChoices.IN_PROGRESS)
    
    # Variables del algoritmo adaptativo (equivalentes a self.X, self.C, self.W)
    questions_answered = models.PositiveIntegerField(default=0) # X
    correct_count = models.PositiveIntegerField(default=0)      # C
    incorrect_count = models.PositiveIntegerField(default=0)    # W
    current_s_index = models.FloatField(default=0.0)            # S
    
    # Equivalente a self.historial_S para el semáforo final
    s_history = models.JSONField(default=list) 

    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "app_exam_attempts"

class AttemptResponse(models.Model):
    attempt = models.ForeignKey(ExamAttempt, on_delete=models.CASCADE, related_name='responses')
    question = models.ForeignKey('app.Question', on_delete=models.CASCADE)
    selected_option = models.ForeignKey('app.AnswerOption', on_delete=models.SET_NULL, null=True, blank=True)
    
    is_correct = models.BooleanField(default=False)
    time_taken = models.PositiveIntegerField(help_text="Tiempo tomado en segundos", default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "app_attempt_responses"