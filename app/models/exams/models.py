from django.db import models


# -------------------------------------------------------------------
# Exámenes
# -------------------------------------------------------------------
class Exam(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    max_attempts = models.PositiveIntegerField(default=1)
    max_questions = models.PositiveIntegerField(default=10)
    
    p0 = models.FloatField(default=60.0, help_text="Umbral de competencia esperado (P0)")
    p1 = models.FloatField(default=40.0, help_text="Umbral de conocimiento inaceptable (P1)")
    a = models.FloatField(default=0.1, help_text="Margen de error falsos positivos (a)")
    b = models.FloatField(default=0.1, help_text="Margen de error falsos negativos (b)")
    
    question_banks = models.ManyToManyField("app.QuestionBank", related_name="exams")
    institution = models.ForeignKey(
        "app.Institution", on_delete=models.CASCADE, related_name="exams"
    )
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "app_exams"

    def __str__(self):
        return self.title
