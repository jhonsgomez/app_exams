import math
import random
from datetime import datetime, timezone
from django.db import transaction
from django.db.models import Q
from app.models import (
    Exam,
    ExamAttempt,
    AttemptAnswer,
    LevelProgress,
    Question,
    DifficultyLevel,
    ExamSPRTConfig,
)


class SPRTService:
    """
    Servicio para manejar toda la lógica SPRT del examen adaptativo.
    """

    def __init__(self, exam_attempt):
        self.attempt = exam_attempt
        self.exam = exam_attempt.exam
        self.config = self.exam.sprt_config

        # Calcular límites SPRT
        self.lower_limit = math.log(self.config.beta / (1 - self.config.alpha))
        self.upper_limit = math.log((1 - self.config.beta) / self.config.alpha)

    def get_next_question(self):
        """
        Obtiene la siguiente pregunta apropiada basada en:
        1. Nivel de dificultad actual
        2. Preguntas ya respondidas
        3. Bancos de preguntas del examen
        """
        # Verificar si el examen ya terminó
        if self.attempt.status != ExamAttempt.Status.IN_PROGRESS:
            return None

        # Verificar límite máximo de preguntas
        if self.attempt.total_questions >= self.exam.max_questions:
            self._finalize_attempt("max_questions_reached")
            return None

        # Obtener nivel actual
        current_level = self.attempt.current_difficulty_level
        if not current_level:
            # Iniciar con el nivel más bajo
            current_level = (
                DifficultyLevel.objects.filter(deleted_at__isnull=True)
                .order_by("id")
                .first()
            )
            self.attempt.current_difficulty_level = current_level
            self.attempt.save()

        # Obtener preguntas ya respondidas
        answered_question_ids = self.attempt.answers.values_list(
            "question_id", flat=True
        )

        # Buscar pregunta del nivel actual
        available_questions = Question.objects.filter(
            bank__in=self.exam.question_banks.all(),
            difficulty_level=current_level,
            is_active=True,
            deleted_at__isnull=True,
        ).exclude(id__in=answered_question_ids)

        if not available_questions.exists():
            # No hay más preguntas en este nivel
            return self._handle_no_questions_available(current_level)

        # Seleccionar pregunta aleatoria
        question = random.choice(list(available_questions))
        return question

    def _handle_no_questions_available(self, current_level):
        """
        Maneja el caso cuando no hay preguntas disponibles en el nivel actual.
        """
        # Verificar si puede avanzar al siguiente nivel
        level_progress = LevelProgress.objects.filter(
            attempt=self.attempt, difficulty_level=current_level
        ).first()

        if level_progress and self._should_advance_level(level_progress):
            next_level = self._get_next_difficulty_level(current_level)
            if next_level:
                self.attempt.current_difficulty_level = next_level
                self.attempt.save()
                return self.get_next_question()

        # No hay más preguntas disponibles
        self._finalize_attempt("no_more_questions")
        return None

    @transaction.atomic
    def process_answer(self, question, selected_option, question_shown_at):
        """
        Procesa una respuesta y actualiza el estado SPRT.

        Returns:
            dict: Resultado del procesamiento con estado actualizado
        """
        now = datetime.now(timezone.utc)

        # Calcular tiempo tomado
        time_taken = (now - question_shown_at).total_seconds()
        allowed_time = question.time

        # Verificar violación de tiempo
        time_violation = time_taken > allowed_time

        if self.exam.enforce_time_limits and time_violation:
            # Si se excede el tiempo, considerarla incorrecta
            is_correct = False
        else:
            is_correct = selected_option.is_correct

        # Actualizar contadores
        self.attempt.total_questions += 1
        if is_correct:
            self.attempt.correct_answers += 1
        else:
            self.attempt.incorrect_answers += 1

        # Calcular nuevo índice S (SPRT)
        p0 = self.config.p0 / 100
        p1 = self.config.p1 / 100

        if is_correct:
            delta_s = math.log(p1 / p0)
        else:
            delta_s = math.log((1 - p1) / (1 - p0))

        self.attempt.s_index += delta_s
        self.attempt.s_history.append(self.attempt.s_index)
        self.attempt.save()

        # Registrar la respuesta
        answer = AttemptAnswer.objects.create(
            attempt=self.attempt,
            question=question,
            selected_option=selected_option,
            question_number=self.attempt.total_questions,
            difficulty_level=question.difficulty_level,
            is_correct=is_correct,
            question_shown_at=question_shown_at,
            time_taken_seconds=int(time_taken),
            allowed_time_seconds=allowed_time,
            time_violation=time_violation,
            s_index_after=self.attempt.s_index,
        )

        # Actualizar progreso por nivel
        self._update_level_progress(question.difficulty_level, is_correct, delta_s)

        # Evaluar decisión SPRT
        decision = self._evaluate_sprt_decision()

        return {
            "answer": answer,
            "is_correct": is_correct,
            "time_violation": time_violation,
            "s_index": self.attempt.s_index,
            "decision": decision,
            "feedback": selected_option.feedback,
        }

    def _update_level_progress(self, difficulty_level, is_correct, delta_s):
        """
        Actualiza el progreso en el nivel actual.
        """
        progress, created = LevelProgress.objects.get_or_create(
            attempt=self.attempt,
            difficulty_level=difficulty_level,
            defaults={
                "questions_answered": 0,
                "correct_count": 0,
                "incorrect_count": 0,
                "s_index": 0.0,
            },
        )

        progress.questions_answered += 1
        if is_correct:
            progress.correct_count += 1
        else:
            progress.incorrect_count += 1

        progress.s_index += delta_s
        progress.save()

    def _evaluate_sprt_decision(self):
        """
        Evalúa si el examen debe terminar según los límites SPRT.

        Returns:
            str: 'continue', 'approved', 'failed'
        """
        s = self.attempt.s_index

        if s <= self.lower_limit:
            # El estudiante ha demostrado competencia
            self._finalize_attempt("approved")
            return "approved"

        elif s >= self.upper_limit:
            # El estudiante no ha demostrado competencia
            self._finalize_attempt("failed")
            return "failed"

        elif self.attempt.total_questions >= self.exam.max_questions:
            # Se alcanzó el límite de preguntas
            # Decidir basándose en el índice S actual
            if s < 0:
                self._finalize_attempt("approved")
                return "approved"
            else:
                self._finalize_attempt("failed")
                return "failed"

        else:
            # Verificar si debe avanzar de nivel
            if self.exam.enable_difficulty_progression:
                self._check_level_progression()

            return "continue"

    def _check_level_progression(self):
        """
        Verifica si el estudiante debe avanzar al siguiente nivel de dificultad.
        """
        current_level = self.attempt.current_difficulty_level
        progress = LevelProgress.objects.filter(
            attempt=self.attempt, difficulty_level=current_level
        ).first()

        if progress and self._should_advance_level(progress):
            next_level = self._get_next_difficulty_level(current_level)
            if next_level:
                progress.is_completed = True
                progress.passed_to_next_level = True
                progress.completed_at = datetime.now(timezone.utc)
                progress.save()

                self.attempt.current_difficulty_level = next_level
                self.attempt.save()

    def _should_advance_level(self, level_progress):
        """
        Determina si el estudiante debe avanzar al siguiente nivel.
        """
        # Verificar mínimo de preguntas
        if level_progress.questions_answered < self.config.min_questions_per_level:
            return False

        # Verificar porcentaje de aciertos
        accuracy = level_progress.get_accuracy() / 100
        return accuracy >= self.config.success_threshold_to_advance

    def _get_next_difficulty_level(self, current_level):
        """
        Obtiene el siguiente nivel de dificultad.
        """
        levels = list(
            DifficultyLevel.objects.filter(deleted_at__isnull=True).order_by("id")
        )

        try:
            current_index = levels.index(current_level)
            if current_index < len(levels) - 1:
                return levels[current_index + 1]
        except ValueError:
            pass

        return None

    def _finalize_attempt(self, reason):
        """
        Finaliza el intento con el estado correspondiente.
        """
        if reason in ["approved", "max_questions_reached"]:
            if self.attempt.s_index < 0:
                self.attempt.status = ExamAttempt.Status.APPROVED
            else:
                self.attempt.status = ExamAttempt.Status.FAILED
        elif reason == "failed":
            self.attempt.status = ExamAttempt.Status.FAILED
        else:
            self.attempt.status = ExamAttempt.Status.FAILED

        # Generar retroalimentación de consistencia
        self.attempt.consistency_feedback = self._generate_consistency_feedback()

        # Generar análisis por nivel
        self.attempt.level_analysis = self._generate_level_analysis()

        self.attempt.completed_at = datetime.now(timezone.utc)
        self.attempt.save()

    def _generate_consistency_feedback(self):
        """
        Genera retroalimentación sobre la consistencia del desempeño.
        """
        history = self.attempt.s_history

        if len(history) < 3:
            return ExamAttempt.FeedbackConsistency.INSUFFICIENT

        # Analizar tendencia
        increasing = 0
        decreasing = 0

        for i in range(1, len(history)):
            if history[i] < history[i - 1]:
                decreasing += 1
            elif history[i] > history[i - 1]:
                increasing += 1

        threshold = len(history) // 2

        if decreasing >= threshold:
            return ExamAttempt.FeedbackConsistency.POSITIVE
        elif increasing >= threshold:
            return ExamAttempt.FeedbackConsistency.NEGATIVE
        else:
            return ExamAttempt.FeedbackConsistency.INCONSISTENT

    def _generate_level_analysis(self):
        """
        Genera análisis detallado por nivel de dificultad.
        """
        analysis = {}

        for progress in self.attempt.level_progress.all():
            analysis[progress.difficulty_level.name] = {
                "questions_answered": progress.questions_answered,
                "correct": progress.correct_count,
                "incorrect": progress.incorrect_count,
                "accuracy": progress.get_accuracy(),
                "s_index": progress.s_index,
                "completed": progress.is_completed,
                "advanced": progress.passed_to_next_level,
            }

        return analysis
