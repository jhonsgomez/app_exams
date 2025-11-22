import uuid
import csv
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.admin import is_admin
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.db.models import Count, Q
from datetime import datetime
from app.models import (
    Exam,
    ExamAttempt,
    Question,
    AnswerOption,
    DifficultyLevel,
)
from app.services.sprt_service import SPRTService
from django.core.paginator import Paginator
from utils.report import export_attempt_to_csv


# -------------------------------------------------------------------
# Vista principal: Listar exámenes disponibles para estudiante
# -------------------------------------------------------------------
@login_required(login_url="auth_login")
def available_exams(request):
    """
    Muestra los exámenes disponibles para el estudiante actual.
    """
    now = timezone.now()

    # Filtrar exámenes activos y dentro del rango de fechas
    exams = Exam.objects.filter(
        is_active=True,
        deleted_at__isnull=True,
        start_date__lte=now,
        end_date__gte=now,
        institution=request.user.institution,
    ).annotate(
        total_questions=Count(
            "question_banks__questions",
            filter=Q(
                question_banks__questions__is_active=True,
                question_banks__questions__deleted_at__isnull=True,
            ),
        )
    )

    # Para cada examen, obtener información de intentos del estudiante
    exam_data = []
    for exam in exams:
        attempts = ExamAttempt.objects.filter(student=request.user, exam=exam).order_by(
            "-attempt_number"
        )

        attempts_used = attempts.count()
        attempts_remaining = exam.max_attempts - attempts_used
        can_attempt = attempts_remaining > 0

        # Verificar si hay un intento en progreso
        in_progress_attempt = attempts.filter(
            status=ExamAttempt.Status.IN_PROGRESS
        ).first()

        exam_data.append(
            {
                "exam": exam,
                "attempts_used": attempts_used,
                "attempts_remaining": attempts_remaining,
                "can_attempt": can_attempt,
                "in_progress_attempt": in_progress_attempt,
                "last_attempt": attempts.first() if attempts.exists() else None,
                "total_attempts": attempts if attempts.exists() else None,
            }
        )

    paginator = Paginator(exam_data, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
    }

    return render(request, "exams/available_exams.html", context)


# -------------------------------------------------------------------
# Iniciar un nuevo intento
# -------------------------------------------------------------------
@login_required(login_url="auth_login")
@require_http_methods(["POST"])
def start_attempt(request, exam_id):
    """
    Inicia un nuevo intento de examen para el estudiante.
    """
    exam = get_object_or_404(Exam, pk=exam_id, deleted_at__isnull=True)

    # Verificar que el examen esté disponible
    now = timezone.now()
    if not (exam.is_active and exam.start_date <= now <= exam.end_date):
        messages.error(request, "Este examen no está disponible en este momento.")
        return redirect("exams_available")

    # Verificar que el estudiante tenga intentos disponibles
    attempts_count = ExamAttempt.objects.filter(student=request.user, exam=exam).count()

    if attempts_count >= exam.max_attempts:
        messages.error(request, "Has agotado todos los intentos para este examen.")
        return redirect("exams_available")

    # Verificar que no haya un intento en progreso
    existing_attempt = ExamAttempt.objects.filter(
        student=request.user, exam=exam, status=ExamAttempt.Status.IN_PROGRESS
    ).first()

    if existing_attempt:
        messages.info(request, "Ya tienes un intento en progreso.")
        return redirect("attempt_take", attempt_id=existing_attempt.id)

    # Verificar que exista configuración SPRT
    if not hasattr(exam, "sprt_config"):
        messages.error(request, "Este examen no tiene configuración SPRT.")
        return redirect("exams_available")

    # Crear nuevo intento
    session_token = uuid.uuid4().hex

    # Obtener el nivel de dificultad inicial (el primero/más bajo)
    initial_level = (
        DifficultyLevel.objects.filter(deleted_at__isnull=True).order_by("id").first()
    )

    attempt = ExamAttempt.objects.create(
        student=request.user,
        exam=exam,
        attempt_number=attempts_count + 1,
        session_token=session_token,
        current_difficulty_level=initial_level,
        status=ExamAttempt.Status.IN_PROGRESS,
    )

    messages.success(
        request, f"Intento #{attempt.attempt_number} iniciado. ¡Buena suerte!"
    )
    return redirect("attempt_take", attempt_id=attempt.id)


# -------------------------------------------------------------------
# Tomar el examen (vista principal de preguntas)
# -------------------------------------------------------------------
@login_required(login_url="auth_login")
def take_attempt(request, attempt_id):
    """
    Vista principal para presentar el examen.
    """
    attempt = get_object_or_404(ExamAttempt, pk=attempt_id, student=request.user)

    # Verificar que el intento esté en progreso
    if attempt.status != ExamAttempt.Status.IN_PROGRESS:
        messages.info(request, "Este intento ya ha finalizado.")
        return redirect(
            "attempt_results", attempt_id=attempt.id, student_id=request.user.id
        )

    # Verificar que el examen siga disponible
    now = timezone.now()
    if not (attempt.exam.is_active and attempt.exam.end_date >= now):
        messages.error(request, "Este examen ya no está disponible.")
        attempt.status = ExamAttempt.Status.ABANDONED
        attempt.completed_at = now
        attempt.save()
        return redirect("exams_available")

    # Obtener la siguiente pregunta usando el servicio SPRT
    sprt_service = SPRTService(attempt)
    question = sprt_service.get_next_question()

    if not question:
        # No hay más preguntas o el examen terminó
        messages.info(request, "El examen ha finalizado.")
        return redirect(
            "attempt_results", attempt_id=attempt.id, student_id=request.user.id
        )

    # Obtener opciones de respuesta
    options = question.options.filter(is_active=True, deleted_at__isnull=True).order_by(
        "?"
    )  # Aleatorizar orden

    context = {
        "attempt": attempt,
        "question": question,
        "options": options,
        "question_number": attempt.total_questions + 1,
        "max_questions": attempt.exam.max_questions,
        "current_level": attempt.current_difficulty_level,
        "progress_percentage": (attempt.total_questions / attempt.exam.max_questions)
        * 100,
    }

    return render(request, "exams/take_attempt.html", context)


# -------------------------------------------------------------------
# Procesar respuesta del estudiante (AJAX)
# -------------------------------------------------------------------
@login_required(login_url="auth_login")
@require_http_methods(["POST"])
def submit_answer(request, attempt_id):
    """
    Procesa la respuesta del estudiante vía AJAX.
    Valida tiempo y actualiza el estado SPRT.
    """
    try:
        attempt = get_object_or_404(
            ExamAttempt,
            pk=attempt_id,
            student=request.user,
            status=ExamAttempt.Status.IN_PROGRESS,
        )

        # Obtener datos del POST
        question_id = request.POST.get("question_id")
        option_id = request.POST.get("option_id")
        question_shown_at_str = request.POST.get("question_shown_at")

        if not all([question_id, option_id, question_shown_at_str]):
            return JsonResponse(
                {"success": False, "error": "Datos incompletos"}, status=400
            )

        # Validar pregunta y opción
        question = get_object_or_404(Question, pk=question_id)
        option = get_object_or_404(AnswerOption, pk=option_id, question=question)

        # Parsear timestamp
        try:
            question_shown_at = datetime.fromisoformat(
                question_shown_at_str.replace("Z", "+00:00")
            )
        except ValueError:
            return JsonResponse(
                {"success": False, "error": "Formato de fecha inválido"}, status=400
            )

        # Procesar respuesta usando el servicio SPRT
        sprt_service = SPRTService(attempt)
        result = sprt_service.process_answer(
            question=question,
            selected_option=option,
            question_shown_at=question_shown_at,
        )

        # Alamcenar todas las demas opciones de respuesta
        all_options = question.options.filter(
            is_active=True, deleted_at__isnull=True
        ).exclude(id=option.id)
        options_data = []

        for opt in all_options:
            if opt.option_type == AnswerOption.OptionType.TEXT:
                statement = opt.option_text
            elif opt.option_type == AnswerOption.OptionType.IMAGE:
                statement = opt.option_image.url if opt.option_image else ""
            elif opt.option_type == AnswerOption.OptionType.AUDIO:
                statement = opt.option_audio.url if opt.option_audio else ""
            else:
                statement = ""

            options_data.append(
                {
                    "id": opt.id,
                    "type": opt.option_type,
                    "statement": statement,
                    "feedback": opt.feedback,
                }
            )

        # Preparar respuesta
        response_data = {
            "success": True,
            "is_correct": result["is_correct"],
            "time_violation": result["time_violation"],
            "feedback": result["feedback"],
            "options_data": options_data,
            "s_index": round(result["s_index"], 4),
            "decision": result["decision"],
            "question_number": result["answer"].question_number,
            "correct_answers": attempt.correct_answers,
            "incorrect_answers": attempt.incorrect_answers,
            "total_questions": attempt.total_questions,
            "accuracy": round(attempt.get_accuracy(), 2),
        }

        # Si el examen terminó, agregar URL de resultados
        if result["decision"] in ["approved", "failed"]:
            response_data["redirect_url"] = (
                f"/sprt/attempts/{attempt.id}/{attempt.student.id}/results/"
            )
            response_data["status"] = result["decision"]

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


# -------------------------------------------------------------------
# Ver resultados de un intento
# -------------------------------------------------------------------
@login_required(login_url="auth_login")
def attempt_results(request, attempt_id, student_id):
    """
    Muestra los resultados detallados de un intento.
    """
    attempt = get_object_or_404(ExamAttempt, pk=attempt_id, student__id=student_id)

    # Obtener todas las respuestas
    answers = attempt.answers.select_related(
        "question", "selected_option", "difficulty_level"
    ).order_by("question_number")

    # Obtener progreso por nivel
    level_progress = attempt.level_progress.select_related("difficulty_level").order_by(
        "difficulty_level__id"
    )

    # Calcular estadísticas adicionales
    total_time_spent = sum(answer.time_taken_seconds for answer in answers)
    time_violations_count = answers.filter(time_violation=True).count()

    # Preparar datos para gráfica de índice S
    s_history_data = [
        {"question": i + 1, "s_index": round(s, 4)}
        for i, s in enumerate(attempt.s_history)
    ]

    # Configuración SPRT para mostrar límites
    sprt_config = attempt.exam.sprt_config
    lower_limit = SPRTService(attempt).lower_limit
    upper_limit = SPRTService(attempt).upper_limit

    context = {
        "attempt": attempt,
        "answers": answers,
        "level_progress": level_progress,
        "total_time_spent": total_time_spent,
        "time_violations_count": time_violations_count,
        "s_history_data": s_history_data,
        "sprt_config": sprt_config,
        "lower_limit": round(lower_limit, 4),
        "upper_limit": round(upper_limit, 4),
    }

    return render(request, "exams/attempt_results.html", context)


# -------------------------------------------------------------------
# Ver historial de todos los intentos del estudiante
# -------------------------------------------------------------------
@login_required(login_url="auth_login")
def my_attempts(request, student_id, exam_id=None):
    """
    Muestra el historial de todos los intentos del estudiante.
    """
    attempts = (
        ExamAttempt.objects.filter(student__id=student_id)
        .select_related("exam", "exam__institution")
        .order_by("-started_at")
    )

    if exam_id:
        attempts = attempts.filter(exam__id=exam_id)

    paginator = Paginator(attempts, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {"page_obj": page_obj}

    return render(request, "exams/my_attempts.html", context)


# -------------------------------------------------------------------
# Abandonar intento (opcional)
# -------------------------------------------------------------------
@login_required(login_url="auth_login")
@require_http_methods(["POST"])
def abandon_attempt(request, attempt_id):
    """
    Permite al estudiante abandonar un intento en progreso.
    """
    attempt = get_object_or_404(
        ExamAttempt,
        pk=attempt_id,
        student=request.user,
        status=ExamAttempt.Status.IN_PROGRESS,
    )

    attempt.status = ExamAttempt.Status.ABANDONED
    attempt.completed_at = timezone.now()
    attempt.save()

    messages.warning(request, "Has abandonado el intento.")
    return redirect("exams_available")


# -------------------------------------------------------------------
# Mostar Estudiantes que han realizado un examen específico
# -------------------------------------------------------------------
@login_required(login_url="auth_login")
@is_admin
def exam_students(request, exam_id):
    """
    Muestra los estudiantes que han realizado un examen específico.
    """
    exam = get_object_or_404(Exam, pk=exam_id, deleted_at__isnull=True)

    # Obtener intentos del examen
    attempts = ExamAttempt.objects.filter(exam=exam).select_related("student")

    # Agrupar por estudiante y contar intentos
    student_data = {}
    for attempt in attempts:
        student_id = attempt.student.id
        if student_id not in student_data:
            student_data[student_id] = {
                "student": attempt.student,
                "attempts": [],
            }
        student_data[student_id]["attempts"].append(attempt)

    # Preparar lista para la plantilla
    exam_data = []
    for data in student_data.values():
        attempts = data["attempts"]
        attempts_used = len(attempts)
        attempts_remaining = exam.max_attempts - attempts_used
        can_attempt = attempts_remaining > 0

        # Verificar si hay un intento en progreso
        in_progress_attempt = next(
            (a for a in attempts if a.status == ExamAttempt.Status.IN_PROGRESS), None
        )

        # cada attempt tiene un metodo get_accuracy() que devuelve el porcentaje de aciertos
        total_accuracy = sum(
            a.get_accuracy() for a in attempts if a.get_accuracy() is not None
        )
        average_score = total_accuracy / attempts_used if attempts_used > 0 else 0

        exam_data.append(
            {
                "student": data["student"],
                "attempts_used": attempts_used,
                "attempts_remaining": attempts_remaining,
                "can_attempt": can_attempt,
                "in_progress_attempt": in_progress_attempt,
                "last_attempt": attempts[0] if attempts else None,
                "total_attempts": attempts if attempts else None,
                "average_score": average_score,
            }
        )

    paginator = Paginator(exam_data, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "exam": exam,
    }

    return render(request, "exams/exam_students.html", context)


# -------------------------------------------------------------------
# Generar y descargar reporte CSV de un intento
# -------------------------------------------------------------------
@login_required(login_url="auth_login")
def export_attempt_csv(request, attempt_id):
    """
    Exporta los resultados de un intento a CSV.
    """
    attempt = get_object_or_404(ExamAttempt, pk=attempt_id)

    # Verificar permisos
    if request.user != attempt.student and not request.user.role.name in [
        "super_admin",
        "admin",
    ]:
        messages.error(request, "No tienes permiso para exportar este intento.")
        return redirect("exams_available")

    # Generar CSV
    csv_content = export_attempt_to_csv(attempt)

    # Crear respuesta HTTP
    response = HttpResponse(csv_content, content_type="text/csv")
    filename = f"Intento # {attempt.id} de {attempt.student} ({attempt.started_at.strftime('%Y-%m-%d')}).csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'

    return response


# -------------------------------------------------------------------
# Exportar reporte completo de un examen
# -------------------------------------------------------------------
@login_required(login_url="auth_login")
@is_admin
def export_exam_results(request, exam_id):
    """
    Exporta todos los resultados de un examen a CSV.
    """
    exam = get_object_or_404(Exam, pk=exam_id, deleted_at__isnull=True)

    attempts = (
        ExamAttempt.objects.filter(exam=exam)
        .exclude(status=ExamAttempt.Status.IN_PROGRESS)
        .select_related("student")
        .order_by("-started_at")
    )

    # Crear CSV
    response = HttpResponse(content_type="text/csv")
    filename = f"Resultados de {exam.title} ({timezone.now().strftime('%Y-%m-%d')}).csv"
    response["Content-Disposition"] = f'attachment; filename="{filename}"'
    response.write(u'\ufeff'.encode('utf8'))

    writer = csv.writer(response)

    # Encabezados
    writer.writerow(
        [
            "#",
            "Documento",
            "Estudiante",
            "Intento #",
            "Fecha Inicio",
            "Fecha Fin",
            "Total Preguntas",
            "Correctas",
            "Incorrectas",
            "Precisión %",
            "Índice S",
            "Resultado",
            "Consistencia",
        ]
    )
    
    contador = 1

    # Datos
    for attempt in attempts:
        writer.writerow(
            [
                contador,
                attempt.student.document_number,
                attempt.student or attempt.student.username,
                attempt.attempt_number,
                attempt.started_at.strftime("%Y-%m-%d %H:%M"),
                (
                    attempt.completed_at.strftime("%Y-%m-%d %H:%M")
                    if attempt.completed_at
                    else "N/A"
                ),
                attempt.total_questions,
                attempt.correct_answers,
                attempt.incorrect_answers,
                round(attempt.get_accuracy(), 2),
                round(attempt.s_index, 4),
                attempt.get_status_display(),
                attempt.get_consistency_feedback_display() or "N/A",
            ]
        )
        contador += 1

    return response
