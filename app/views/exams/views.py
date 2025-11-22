from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.admin import is_admin
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count
from utils.date import to_aware
from app.models import (
    Institution,
    QuestionBank,
    Exam,
    DifficultyLevel,
)


@login_required(login_url="auth_login")
@is_admin
def table(request):
    query = request.GET.get("q", "").strip()
    exams = Exam.objects.filter(deleted_at__isnull=True)

    if request.user.institution:
        exams = exams.filter(institution=request.user.institution)

    if query:
        exams = exams.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    exams = exams.order_by("-created_at")

    paginator = Paginator(exams, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    return render(request, "exams/table.html", context)


@login_required(login_url="auth_login")
@is_admin
def create(request):
    institutions = Institution.objects.filter(deleted_at__isnull=True)
    question_banks = QuestionBank.objects.filter(
        deleted_at__isnull=True, is_active=True
    ).annotate(
        total_questions=Count(
            "questions",
            filter=Q(questions__is_active=True, questions__deleted_at__isnull=True),
        )
    )

    total_available_questions = 0

    for bank in question_banks:
        total_available_questions += bank.total_questions

        basics_count = bank.questions.filter(
            difficulty_level__name="Básico", is_active=True, deleted_at__isnull=True
        ).count()

        intermediate_count = bank.questions.filter(
            difficulty_level__name="Intermedio", is_active=True, deleted_at__isnull=True
        ).count()

        advanced_count = bank.questions.filter(
            difficulty_level__name="Avanzado", is_active=True, deleted_at__isnull=True
        ).count()

        bank.total_questions_basics = basics_count
        bank.total_questions_intermediate = intermediate_count
        bank.total_questions_advanced = advanced_count

    difficulty_levels = DifficultyLevel.objects.filter(
        deleted_at__isnull=True
    ).order_by("id")

    if request.user.institution:
        institutions = institutions.filter(id=request.user.institution.id)
        question_banks = question_banks.filter(institution=request.user.institution)

    return render(
        request,
        "exams/form.html",
        {
            "institutions": institutions,
            "question_banks": question_banks,
            "total_available_questions": total_available_questions,
            "difficulty_levels": difficulty_levels,
        },
    )


@login_required(login_url="auth_login")
@is_admin
def update(request, exam_id):
    if request.method == "GET":
        try:
            exam = get_object_or_404(Exam, pk=exam_id)
            institutions = Institution.objects.filter(deleted_at__isnull=True)
            question_banks = QuestionBank.objects.filter(
                deleted_at__isnull=True, is_active=True
            ).annotate(
                total_questions=Count(
                    "questions",
                    filter=Q(
                        questions__is_active=True, questions__deleted_at__isnull=True
                    ),
                )
            )

            total_available_questions = 0

            for bank in question_banks:
                total_available_questions += bank.total_questions
                
                basics_count = bank.questions.filter(
                    difficulty_level__name="Básico", is_active=True, deleted_at__isnull=True
                ).count()

                intermediate_count = bank.questions.filter(
                    difficulty_level__name="Intermedio", is_active=True, deleted_at__isnull=True
                ).count()

                advanced_count = bank.questions.filter(
                    difficulty_level__name="Avanzado", is_active=True, deleted_at__isnull=True
                ).count()

                bank.total_questions_basics = basics_count
                bank.total_questions_intermediate = intermediate_count
                bank.total_questions_advanced = advanced_count

            difficulty_levels = DifficultyLevel.objects.filter(
                deleted_at__isnull=True
            ).order_by("id")

            if request.user.institution:
                institutions = institutions.filter(id=request.user.institution.id)
                question_banks = question_banks.filter(
                    institution=request.user.institution
                )

            return render(
                request,
                "exams/form.html",
                {
                    "exam": exam,
                    "institutions": institutions,
                    "question_banks": question_banks,
                    "difficulty_levels": difficulty_levels,
                    "total_available_questions": total_available_questions,
                },
            )
        except Exception as e:
            messages.error(request, f"Error al cargar el examen: {str(e)}")
            return redirect("exams_table")


@login_required(login_url="auth_login")
@is_admin
def save(request):
    if request.method == "POST":
        exam_id = request.POST.get("exam_id")

        try:
            if exam_id:
                try:
                    # 1. Recolectar datos del formulario
                    exam = get_object_or_404(Exam, pk=exam_id)
                    title = request.POST.get("title")
                    description = request.POST.get("description")
                    attempts = request.POST.get("attempts")
                    max_questions = request.POST.get("max_questions")
                    start_date = to_aware(request.POST.get("start_date"))
                    end_date = to_aware(request.POST.get("end_date"))
                    institution_id = request.POST.get("institution")
                    selected_banks = request.POST.getlist("question_banks")
                    if request.user.institution:
                        institution_id = request.user.institution.id

                    # 2. Validar datos
                    if not title:
                        messages.error(request, "El título es obligatorio.")
                        return redirect("exams_update", exam_id=exam_id)

                    if not description:
                        messages.error(request, "La descripción es obligatoria.")
                        return redirect("exams_update", exam_id=exam_id)

                    if not attempts or int(attempts) < 1:
                        messages.error(
                            request, "El número de intentos debe ser al menos 1."
                        )
                        return redirect("exams_update", exam_id=exam_id)

                    if not max_questions or int(max_questions) < 1:
                        messages.error(
                            request,
                            "El número máximo de preguntas debe ser al menos 1.",
                        )
                        return redirect("exams_update", exam_id=exam_id)

                    if not start_date or not end_date:
                        messages.error(
                            request, "Las fechas de inicio y fin son obligatorias."
                        )
                        return redirect("exams_update", exam_id=exam_id)

                    if start_date >= end_date:
                        messages.error(
                            request,
                            "La fecha de inicio debe ser anterior a la fecha de fin.",
                        )
                        return redirect("exams_update", exam_id=exam_id)

                    if not institution_id:
                        messages.error(request, "La institución es obligatoria.")
                        return redirect("exams_update", exam_id=exam_id)

                    if not selected_banks:
                        messages.error(
                            request,
                            "Debe seleccionar al menos un banco de preguntas.",
                        )
                        return redirect("exams_update", exam_id=exam_id)

                    total_available_questions = 0

                    for bank_id in selected_banks:
                        bank = QuestionBank.objects.get(pk=bank_id)
                        total_available_questions += bank.total_questions()

                    if int(max_questions) > total_available_questions:
                        messages.error(
                            request,
                            f"El número máximo de preguntas no puede exceder el total disponible ({total_available_questions}).",
                        )
                        return redirect("exams_update", exam_id=exam_id)

                    # 3. Actualizar el examen
                    exam.title = title
                    exam.description = description
                    exam.max_attempts = attempts
                    exam.max_questions = max_questions
                    exam.start_date = start_date
                    exam.end_date = end_date
                    exam.institution_id = institution_id
                    exam.is_active = True
                    exam.save()

                    # 4. Actualizar bancos de preguntas
                    exam.question_banks.set(
                        QuestionBank.objects.filter(pk__in=selected_banks)
                    )

                    messages.success(request, "Examen actualizado correctamente.")
                except Exception as e:
                    messages.error(request, f"Error al actualizar el examen: {str(e)}")

                return redirect("exams_table")
            else:
                try:
                    # 1. Recolectar datos del formulario
                    title = request.POST.get("title")
                    description = request.POST.get("description")
                    attempts = request.POST.get("attempts")
                    max_questions = request.POST.get("max_questions")
                    start_date = to_aware(request.POST.get("start_date"))
                    end_date = to_aware(request.POST.get("end_date"))
                    institution_id = request.POST.get("institution")
                    selected_banks = request.POST.getlist("question_banks")
                    if request.user.institution:
                        institution_id = request.user.institution.id

                    # 2. Validar datos
                    if not title:
                        messages.error(request, "El título es obligatorio.")
                        return redirect("exams_create")

                    if not description:
                        messages.error(request, "La descripción es obligatoria.")
                        return redirect("exams_create")

                    if not attempts or int(attempts) < 1:
                        messages.error(
                            request, "El número de intentos debe ser al menos 1."
                        )
                        return redirect("exams_create")

                    if not max_questions or int(max_questions) < 1:
                        messages.error(
                            request,
                            "El número máximo de preguntas debe ser al menos 1.",
                        )
                        return redirect("exams_create")

                    if not start_date or not end_date:
                        messages.error(
                            request, "Las fechas de inicio y fin son obligatorias."
                        )
                        return redirect("exams_create")

                    if start_date >= end_date:
                        messages.error(
                            request,
                            "La fecha de inicio debe ser anterior a la fecha de fin.",
                        )
                        return redirect("exams_create")

                    if not institution_id:
                        messages.error(request, "La institución es obligatoria.")
                        return redirect("exams_create")

                    if not selected_banks:
                        messages.error(
                            request,
                            "Debe seleccionar al menos un banco de preguntas.",
                        )
                        return redirect("exams_create")

                    total_available_questions = 0

                    for bank_id in selected_banks:
                        bank = QuestionBank.objects.get(pk=bank_id)
                        total_available_questions += bank.total_questions()

                    if int(max_questions) > total_available_questions:
                        messages.error(
                            request,
                            f"El número máximo de preguntas no puede exceder el total disponible ({total_available_questions}).",
                        )
                        return redirect("exams_create")

                    # 3. Crear el examen
                    exam = Exam.objects.create(
                        title=title,
                        description=description,
                        max_attempts=attempts,
                        max_questions=max_questions,
                        start_date=start_date,
                        end_date=end_date,
                        institution_id=institution_id,
                        is_active=True,
                    )

                    # 4. Asociar bancos de preguntas
                    exam.question_banks.set(
                        QuestionBank.objects.filter(pk__in=selected_banks)
                    )

                    messages.success(request, "Examen creado correctamente.")
                except Exception as e:
                    messages.error(request, f"Error al crear el examen: {str(e)}")

                return redirect("exams_table")
        except Exception as e:
            messages.error(request, f"Error al guardar examen: {str(e)}")
            return redirect("exams_table")


@login_required(login_url="auth_login")
@is_admin
def deactivate(request, exam_id):
    if request.method == "POST":
        try:
            exam = get_object_or_404(Exam, pk=exam_id)
            exam.is_active = False
            exam.save()
            messages.success(request, "Examen desactivado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al desactivar el examen: {str(e)}")

    return redirect("exams_table")


@login_required(login_url="auth_login")
@is_admin
def activate(request, exam_id):
    if request.method == "POST":
        try:
            exam = get_object_or_404(Exam, pk=exam_id)
            exam.is_active = True
            exam.save()
            messages.success(request, "Examen activado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al activar el examen: {str(e)}")

    return redirect("exams_table")


@login_required(login_url="auth_login")
@is_admin
def delete(request, exam_id):
    if request.method == "POST":
        try:
            exam = get_object_or_404(Exam, pk=exam_id)
            exam.deleted_at = timezone.now()
            exam.save()
            messages.success(request, "Examen eliminado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar el examen: {str(e)}")

    return redirect("exams_table")


# SPRT

# Agregar estos imports al inicio del archivo
from app.models import ExamSPRTConfig, DifficultyLevel, ExamAttempt
from django.db import models


# Agregar esta vista después de la función create existente
@login_required(login_url="auth_login")
@is_admin
def configure_sprt(request, exam_id):
    """
    Vista para configurar parámetros SPRT de un examen.
    """
    exam = get_object_or_404(Exam, pk=exam_id, deleted_at__isnull=True)

    # Obtener o crear configuración SPRT
    sprt_config, created = ExamSPRTConfig.objects.get_or_create(
        exam=exam,
        defaults={
            "p0": 60.0,
            "p1": 40.0,
            "alpha": 0.1,
            "beta": 0.1,
            "min_questions_per_level": 3,
            "success_threshold_to_advance": 0.70,
        },
    )

    if request.method == "POST":
        try:
            # Actualizar configuración
            sprt_config.p0 = float(request.POST.get("p0", 60.0))
            sprt_config.p1 = float(request.POST.get("p1", 40.0))
            sprt_config.alpha = float(request.POST.get("alpha", 0.1))
            sprt_config.beta = float(request.POST.get("beta", 0.1))
            sprt_config.min_questions_per_level = int(
                request.POST.get("min_questions_per_level", 3)
            )
            sprt_config.success_threshold_to_advance = float(
                request.POST.get("success_threshold_to_advance", 0.70)
            )

            # Validar antes de guardar
            sprt_config.full_clean()
            sprt_config.save()

            messages.success(request, "Configuración SPRT actualizada correctamente.")
            return redirect("exams_table")

        except Exception as e:
            messages.error(request, f"Error al guardar configuración: {str(e)}")

    context = {
        "exam": exam,
        "sprt_config": sprt_config,
    }

    return render(request, "exams/configure_sprt.html", context)


# Vista para ver estadísticas de intentos de un examen
@login_required(login_url="auth_login")
@is_admin
def exam_statistics(request, exam_id):
    """
    Muestra estadísticas generales de un examen.
    """
    exam = get_object_or_404(Exam, pk=exam_id, deleted_at__isnull=True)

    attempts = ExamAttempt.objects.filter(exam=exam)

    # Estadísticas generales
    total_attempts = attempts.count()
    approved_count = attempts.filter(status=ExamAttempt.Status.APPROVED).count()
    failed_count = attempts.filter(status=ExamAttempt.Status.FAILED).count()
    in_progress_count = attempts.filter(status=ExamAttempt.Status.IN_PROGRESS).count()
    abandoned_count = attempts.filter(status=ExamAttempt.Status.ABANDONED).count()

    # Calcular promedios
    completed_attempts = attempts.exclude(status=ExamAttempt.Status.IN_PROGRESS)

    if completed_attempts.exists():
        avg_questions = completed_attempts.aggregate(avg=models.Avg("total_questions"))[
            "avg"
        ]
        avg_accuracy = (
            sum(a.get_accuracy() for a in completed_attempts)
            / completed_attempts.count()
        )
    else:
        avg_questions = 0
        avg_accuracy = 0

    context = {
        "exam": exam,
        "total_attempts": total_attempts,
        "approved_count": approved_count,
        "failed_count": failed_count,
        "in_progress_count": in_progress_count,
        "abandoned_count": abandoned_count,
        "avg_questions": round(avg_questions, 2) if avg_questions else 0,
        "avg_accuracy": round(avg_accuracy, 2),
        "approval_rate": (
            round((approved_count / total_attempts * 100), 2)
            if total_attempts > 0
            else 0
        ),
        "recent_attempts": attempts.order_by("-started_at")[:10],
    }

    return render(request, "exams/exam_statistics.html", context)
