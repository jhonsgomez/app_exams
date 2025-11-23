from django.db import models
from django.core.exceptions import ValidationError


# -------------------------------------------------------------------
# Nivel de dificultad
# -------------------------------------------------------------------
class DifficultyLevel(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "app_difficulty_levels"

    def __str__(self):
        return self.name


# -------------------------------------------------------------------
# Area de Conocimiento
# -------------------------------------------------------------------
class KnowledgeArea(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "app_knowledge_areas"

    def __str__(self):
        return self.name


# -------------------------------------------------------------------
# Banco de preguntas
# -------------------------------------------------------------------
class QuestionBank(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True)
    institution = models.ForeignKey(
        "app.Institution",
        on_delete=models.SET_NULL,
        related_name="question_banks",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "app_question_banks"

    def total_questions(self):
        return self.questions.filter(is_active=True).count()

    def __str__(self):
        return self.name


# -------------------------------------------------------------------
# Pregunta
# -------------------------------------------------------------------
class Question(models.Model):
    class StatementType(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        AUDIO = "audio", "Audio"

    bank = models.ForeignKey(
        "app.QuestionBank",
        on_delete=models.SET_NULL,
        related_name="questions",
        null=True,
        blank=True,
    )

    difficulty_level = models.ForeignKey(
        "app.DifficultyLevel",
        on_delete=models.SET_NULL,
        related_name="questions",
        null=True,
        blank=True,
    )

    knowledge_area = models.ForeignKey(
        "app.KnowledgeArea",
        on_delete=models.SET_NULL,
        related_name="questions",
        null=True,
        blank=True,
    )
    topic = models.CharField(max_length=255)
    time = models.PositiveIntegerField()
    start_statement = models.TextField(
        default="A continuación se presenta la pregunta, por favor lea con atención y seleccione la opción correcta.",
        null=True,
        blank=True,
    )
    statement_type = models.CharField(
        max_length=10, choices=StatementType.choices, default=StatementType.TEXT
    )
    statement_text = models.TextField(blank=True, null=True)
    statement_image = models.ImageField(
        upload_to="questions/statements/image/", blank=True, null=True
    )
    statement_audio = models.FileField(
        upload_to="questions/statements/audio/", blank=True, null=True
    )
    end_statement = models.TextField(
        default="Seleccione la opción que considere correcta.",
        null=True,
        blank=True,
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "app_questions"

    def __str__(self):
        return f"{self.topic} ({self.knowledge_area})"
    
    def get_question_type_display(self):
        return self.StatementType(self.statement_type).label

    def clean(self):
        """
        Validación: la pregunta debe tener al menos 2 opciones
        y exactamente 1 marcada como correcta.
        """
        options = self.options.all() if self.pk else []
        if len(options) < 2:
            raise ValidationError("La pregunta debe tener al menos 2 opciones.")

        correct_count = sum(1 for opt in options if opt.is_correct)
        if correct_count != 1:
            raise ValidationError(
                "La pregunta debe tener exactamente 1 opción correcta."
            )


# -------------------------------------------------------------------
# Opción de respuesta
# -------------------------------------------------------------------
class AnswerOption(models.Model):
    class OptionType(models.TextChoices):
        TEXT = "text", "Text"
        IMAGE = "image", "Image"
        AUDIO = "audio", "Audio"

    question = models.ForeignKey(
        "app.Question",
        on_delete=models.SET_NULL,
        related_name="options",
        null=True,
        blank=True,
    )
    option_type = models.CharField(
        max_length=10, choices=OptionType.choices, default=OptionType.TEXT
    )
    option_text = models.TextField(blank=True, null=True)
    option_image = models.ImageField(
        upload_to="questions/options/image/", blank=True, null=True
    )
    option_audio = models.FileField(
        upload_to="questions/options/audio/", blank=True, null=True
    )

    is_correct = models.BooleanField(default=False)
    feedback = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = "app_answer_options"

    def __str__(self):
        return f"Option for Question {self.question.id} ({'Correct' if self.is_correct else 'Incorrect'})"

    def clean(self):
        """
        Validación extra: evitar que existan múltiples correctas en la misma pregunta.
        """
        if self.is_correct:
            qs = AnswerOption.objects.filter(question=self.question, is_correct=True)
            if self.pk:
                qs = qs.exclude(pk=self.pk)
            if qs.exists():
                raise ValidationError(
                    "Solo se permite una opción correcta por pregunta."
                )
