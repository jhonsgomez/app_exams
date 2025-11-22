from django.db import models


# -------------------------------------------------------------------
# Exámenes
# -------------------------------------------------------------------
class Exam(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    max_attempts = models.PositiveIntegerField(default=1)
    max_questions = models.PositiveIntegerField(default=10)
    question_banks = models.ManyToManyField("app.QuestionBank", related_name="exams")
    institution = models.ForeignKey(
        "app.Institution", on_delete=models.CASCADE, related_name="exams"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()

    # Nuevos campos para SPRT
    enable_adaptive_testing = models.BooleanField(
        default=True, help_text="Activar evaluación adaptativa SPRT"
    )
    enable_difficulty_progression = models.BooleanField(
        default=True, help_text="Permitir progresión por niveles de dificultad"
    )
    enforce_time_limits = models.BooleanField(
        default=True, help_text="Aplicar límites de tiempo estrictos"
    )

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "app_exams"

    def __str__(self):
        return self.title
