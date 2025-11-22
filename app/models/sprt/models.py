from django.db import models
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model

User = get_user_model()


# -------------------------------------------------------------------
# Parámetros SPRT para cada examen
# -------------------------------------------------------------------
class ExamSPRTConfig(models.Model):
    """
    Configuración de parámetros SPRT por examen.
    Cada examen puede tener diferentes umbrales de aprobación.
    """

    exam = models.OneToOneField(
        "app.Exam", on_delete=models.CASCADE, related_name="sprt_config"
    )

    # Probabilidades de competencia
    p0 = models.FloatField(
        default=60.0, help_text="Probabilidad mínima aceptable de competencia (%)"
    )
    p1 = models.FloatField(default=40.0, help_text="Probabilidad de incompetencia (%)")

    # Errores tipo I y tipo II
    alpha = models.FloatField(
        default=0.1,
        help_text="Probabilidad de error tipo I (rechazar H0 cuando es verdadera)",
    )
    beta = models.FloatField(
        default=0.1,
        help_text="Probabilidad de error tipo II (aceptar H0 cuando es falsa)",
    )

    # Configuración de niveles
    min_questions_per_level = models.PositiveIntegerField(
        default=3, help_text="Mínimo de preguntas por nivel antes de avanzar"
    )
    success_threshold_to_advance = models.FloatField(
        default=0.70,
        help_text="Porcentaje de aciertos para avanzar al siguiente nivel (0-1)",
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "app_exam_sprt_configs"

    def clean(self):
        if self.p0 <= self.p1:
            raise ValidationError("P0 debe ser mayor que P1")
        if not (0 < self.alpha < 1):
            raise ValidationError("Alpha debe estar entre 0 y 1")
        if not (0 < self.beta < 1):
            raise ValidationError("Beta debe estar entre 0 y 1")
        if not (0 < self.success_threshold_to_advance <= 1):
            raise ValidationError("El umbral de éxito debe estar entre 0 y 1")

    def __str__(self):
        return f"SPRT Config for {self.exam.title}"


# -------------------------------------------------------------------
# Intento de examen
# -------------------------------------------------------------------
class ExamAttempt(models.Model):
    """
    Representa un intento individual de un estudiante en un examen.
    Almacena todo el estado de la sesión SPRT.
    """

    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress", "En Progreso"
        APPROVED = "approved", "Aprobado"
        FAILED = "failed", "Reprobado"
        ABANDONED = "abandoned", "Abandonado"

    class FeedbackConsistency(models.TextChoices):
        POSITIVE = "positive", "Consistente Positivo"
        NEGATIVE = "negative", "Consistente Negativo"
        INCONSISTENT = "inconsistent", "Inconsistente"
        INSUFFICIENT = "insufficient", "Datos Insuficientes"

    student = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="exam_attempts"
    )
    exam = models.ForeignKey(
        "app.Exam", on_delete=models.CASCADE, related_name="attempts"
    )

    # Estado del intento
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.IN_PROGRESS
    )
    attempt_number = models.PositiveIntegerField(default=1)

    # Nivel actual de dificultad
    current_difficulty_level = models.ForeignKey(
        "app.DifficultyLevel",
        on_delete=models.SET_NULL,
        null=True,
        related_name="current_attempts",
    )

    # Contadores SPRT generales
    total_questions = models.PositiveIntegerField(default=0)
    correct_answers = models.PositiveIntegerField(default=0)
    incorrect_answers = models.PositiveIntegerField(default=0)

    # Índice S acumulativo (SPRT)
    s_index = models.FloatField(default=0.0)

    # Historial de índice S (JSON array)
    s_history = models.JSONField(
        default=list, help_text="Lista de valores S en cada pregunta"
    )

    # Retroalimentación de consistencia
    consistency_feedback = models.CharField(
        max_length=20, choices=FeedbackConsistency.choices, null=True, blank=True
    )

    # Marcas de tiempo
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    last_activity_at = models.DateTimeField(auto_now=True)

    # Seguridad: token único por sesión
    session_token = models.CharField(max_length=64, unique=True)

    # Análisis por nivel
    level_analysis = models.JSONField(
        default=dict, help_text="Análisis detallado por nivel de dificultad"
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "app_exam_attempts"
        unique_together = ["student", "exam", "attempt_number"]
        ordering = ["-started_at"]

    def __str__(self):
        return f"{self.student.username} - {self.exam.title} (Intento #{self.attempt_number})"

    def get_accuracy(self):
        """Retorna el porcentaje de aciertos"""
        if self.total_questions == 0:
            return 0
        return (self.correct_answers / self.total_questions) * 100

    def get_duration(self):
        """Retorna la duración del intento"""
        if self.completed_at:
            return self.completed_at - self.started_at
        return None


# -------------------------------------------------------------------
# Respuesta individual en un intento
# -------------------------------------------------------------------
class AttemptAnswer(models.Model):
    """
    Cada respuesta dada en un intento específico.
    Incluye seguridad temporal y análisis SPRT.
    """

    attempt = models.ForeignKey(
        ExamAttempt, on_delete=models.CASCADE, related_name="answers"
    )
    question = models.ForeignKey(
        "app.Question", on_delete=models.CASCADE, related_name="attempt_answers"
    )
    selected_option = models.ForeignKey(
        "app.AnswerOption", on_delete=models.CASCADE, related_name="selections"
    )

    # Datos de la pregunta
    question_number = models.PositiveIntegerField()
    difficulty_level = models.ForeignKey(
        "app.DifficultyLevel", on_delete=models.SET_NULL, null=True
    )

    # Resultado
    is_correct = models.BooleanField()

    # Seguridad temporal
    question_shown_at = models.DateTimeField()
    answered_at = models.DateTimeField(auto_now_add=True)
    time_taken_seconds = models.PositiveIntegerField()
    allowed_time_seconds = models.PositiveIntegerField()
    time_violation = models.BooleanField(
        default=False, help_text="Si el tiempo excedió el permitido"
    )

    # Estado SPRT en este momento
    s_index_after = models.FloatField(
        help_text="Valor del índice S después de esta respuesta"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "app_attempt_answers"
        ordering = ["question_number"]

    def __str__(self):
        return f"Q{self.question_number} - {self.attempt}"

    def clean(self):
        """Validar que no se exceda el tiempo permitido"""
        if self.time_taken_seconds > self.allowed_time_seconds:
            self.time_violation = True


# -------------------------------------------------------------------
# Progreso por nivel de dificultad
# -------------------------------------------------------------------
class LevelProgress(models.Model):
    """
    Rastrea el progreso en cada nivel de dificultad durante un intento.
    """

    attempt = models.ForeignKey(
        ExamAttempt, on_delete=models.CASCADE, related_name="level_progress"
    )
    difficulty_level = models.ForeignKey(
        "app.DifficultyLevel", on_delete=models.CASCADE
    )

    # Estadísticas del nivel
    questions_answered = models.PositiveIntegerField(default=0)
    correct_count = models.PositiveIntegerField(default=0)
    incorrect_count = models.PositiveIntegerField(default=0)

    # SPRT específico del nivel
    s_index = models.FloatField(default=0.0)

    # Estado
    is_completed = models.BooleanField(default=False)
    passed_to_next_level = models.BooleanField(default=False)

    # Tiempos
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "app_level_progress"
        unique_together = ["attempt", "difficulty_level"]

    def __str__(self):
        return f"{self.attempt} - {self.difficulty_level}"

    def get_accuracy(self):
        if self.questions_answered == 0:
            return 0
        return (self.correct_count / self.questions_answered) * 100
