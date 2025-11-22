from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from decorators.admin import is_admin
from utils.utils import generate_unique_filename
from app.models import (
    KnowledgeArea,
    Question,
    QuestionBank,
    DifficultyLevel,
    AnswerOption,
)
from django.core.paginator import Paginator
from django.db.models import Q
from django.db import transaction
from django.contrib import messages
from django.utils import timezone
import json
import html


@login_required(login_url="auth_login")
@is_admin
def create(request, question_bank_id):
    question_bank = get_object_or_404(QuestionBank, pk=question_bank_id)
    difficulty_levels = DifficultyLevel.objects.filter(
        deleted_at__isnull=True
    ).order_by("name")
    knowledge_areas = KnowledgeArea.objects.filter(deleted_at__isnull=True).order_by(
        "name"
    )
    return render(
        request,
        "questions/question/form.html",
        {
            "difficulty_levels": difficulty_levels,
            "knowledge_areas": knowledge_areas,
            "question_bank": question_bank,
        },
    )


@login_required(login_url="auth_login")
@is_admin
def update(request, question_bank_id, question_id):
    if request.method == "GET":
        try:
            question_bank = get_object_or_404(QuestionBank, pk=question_bank_id)
            question = get_object_or_404(Question, pk=question_id)
            difficulty_levels = DifficultyLevel.objects.filter(
                deleted_at__isnull=True
            ).order_by("name")
            knowledge_areas = KnowledgeArea.objects.filter(
                deleted_at__isnull=True
            ).order_by("name")
            options = list(
                question.options.values(
                    "id",
                    "option_type",
                    "option_text",
                    "option_image",
                    "option_audio",
                    "feedback",
                    "is_correct",
                    "is_active",
                )
            )

            for option in options:
                option["feedback"] = html.escape(option["feedback"])

            options_json = json.dumps(options, default=str)

            return render(
                request,
                "questions/question/form.html",
                {
                    "question": question,
                    "options_json": options_json,
                    "difficulty_levels": difficulty_levels,
                    "knowledge_areas": knowledge_areas,
                    "question_bank": question_bank,
                },
            )
        except Exception as e:
            messages.error(request, f"Error al obtener la pregunta: {str(e)}")
            return redirect(
                "questions_bank_questions", question_bank_id=question_bank_id
            )


@login_required(login_url="auth_login")
@is_admin
@transaction.atomic
def save(request):
    if request.method == "POST":
        question_id = request.POST.get("question_id")
        question_bank_id = request.POST.get("question_bank_id")

        if question_id:
            try:
                question = get_object_or_404(Question, pk=question_id)

                # 1. Recolectar datos de Question
                difficulty_level = request.POST.get("difficulty_level")
                knowledge_area = request.POST.get("knowledge_area")
                time = request.POST.get("time")
                topic = request.POST.get("topic", "").strip()
                start_statement = request.POST.get("start_statement", "").strip()
                statement_type = request.POST.get("statement_type")
                end_statement = request.POST.get("end_statement", "").strip()

                # 2. Validaciones
                if not difficulty_level:
                    messages.error(request, "El nivel de dificultad es obligatorio.")
                    return redirect(
                        "questions_bank_questions", question_bank_id=question_bank_id
                    )

                if not knowledge_area:
                    messages.error(request, "El área de conocimiento es obligatoria.")
                    return redirect(
                        "questions_bank_questions", question_bank_id=question_bank_id
                    )

                if not time:
                    messages.error(request, "El tiempo es obligatorio.")
                    return redirect(
                        "questions_bank_questions", question_bank_id=question_bank_id
                    )

                if not topic:
                    messages.error(request, "El tema es obligatorio.")
                    return redirect(
                        "questions_bank_questions", question_bank_id=question_bank_id
                    )

                if not statement_type:
                    messages.error(request, "El tipo de enunciado es obligatorio.")
                    return redirect(
                        "questions_bank_questions", question_bank_id=question_bank_id
                    )

                if not start_statement:
                    start_statement = Question._meta.get_field(
                        "start_statement"
                    ).default

                if not end_statement:
                    end_statement = Question._meta.get_field("end_statement").default

                # 3. Manejo del statement
                statement_text = None
                statement_image = None
                statement_audio = None

                if statement_type == "text":
                    statement_text = request.POST.get("statement_text", "").strip()

                elif statement_type == "image":
                    if "statement_image" in request.FILES:
                        statement_image = request.FILES["statement_image"]
                    elif request.POST.get("existing_statement_image"):
                        # Conservar archivo existente
                        statement_image = question.statement_image
                    else:
                        statement_image = None

                elif statement_type == "audio":
                    if "statement_audio" in request.FILES:
                        statement_audio = request.FILES["statement_audio"]
                    elif request.POST.get("existing_statement_audio"):
                        statement_audio = question.statement_audio
                    else:
                        statement_audio = None

                # 4. Guardar Question
                question.bank_id = question_bank_id
                question.difficulty_level_id = difficulty_level
                question.knowledge_area_id = knowledge_area
                question.time = time
                question.topic = topic
                question.start_statement = start_statement
                question.end_statement = end_statement
                question.statement_type = statement_type
                question.statement_text = statement_text
                question.statement_image = statement_image
                question.statement_audio = statement_audio
                question.is_active = True

                question.save()

                # 5. Recolectar opciones del formulario
                options_data = {}

                for key, value in request.POST.items():
                    if key.startswith("options["):
                        index = key.split("[")[1].split("]")[0]
                        field = key.split("[")[2].replace("]", "")
                        options_data.setdefault(index, {})[field] = value

                for key, value in request.FILES.items():
                    if key.startswith("options["):
                        index = key.split("[")[1].split("]")[0]
                        field = key.split("[")[2].replace("]", "")
                        options_data.setdefault(index, {})[field] = value

                # 6. Actualizar o crear opciones
                received_ids = []

                for index, data in options_data.items():
                    option_id = data.get("id") if data.get("id") else None
                    option_type = data.get("option_type", "text")

                    # Manejo de archivos
                    option_image = None
                    option_audio = None

                    if option_type == "image":
                        if (
                            "option_image" in data
                            and data["option_image"] != ""
                            and data["option_image"] is not None
                        ):
                            option_image = data["option_image"]
                            option_image.name = generate_unique_filename(option_image)
                        elif data.get("existing_option_image") and option_id:
                            old_option = AnswerOption.objects.filter(
                                pk=option_id
                            ).first()
                            option_image = (
                                old_option.option_image if old_option else None
                            )

                    elif option_type == "audio":
                        if (
                            "option_audio" in data
                            and data["option_audio"] != ""
                            and data["option_audio"] is not None
                        ):
                            option_audio = data["option_audio"]
                            option_audio.name = generate_unique_filename(option_audio)
                        elif data.get("existing_option_audio") and option_id:
                            old_option = AnswerOption.objects.filter(
                                pk=option_id
                            ).first()
                            option_audio = (
                                old_option.option_audio if old_option else None
                            )

                    # Crear o actualizar opción
                    option, created = AnswerOption.objects.update_or_create(
                        pk=option_id,
                        defaults={
                            "question": question,
                            "option_type": option_type,
                            "option_text": (
                                data.get("option_text", "").strip()
                                if option_type == "text"
                                else None
                            ),
                            "option_image": option_image,
                            "option_audio": option_audio,
                            "feedback": data.get("feedback", "").strip(),
                            "is_correct": data.get("is_correct", "") == "on",
                            "is_active": data.get("is_active", "") == "on",
                        },
                    )
                    received_ids.append(option.pk)

                # 7. Eliminar opciones que no llegaron en el POST
                question.options.exclude(pk__in=received_ids).delete()

                messages.success(request, "Pregunta actualizada exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al actualizar la pregunta: {str(e)}")

            return redirect(
                "questions_bank_questions", question_bank_id=question_bank_id
            )

        else:
            try:
                # 1. Recolectar datos de la question:
                difficulty_level = request.POST.get("difficulty_level")
                knowledge_area = request.POST.get("knowledge_area")
                time = request.POST.get("time")
                topic = request.POST.get("topic", "").strip()
                start_statement = request.POST.get("start_statement", "").strip()
                statement_type = request.POST.get("statement_type")
                end_statement = request.POST.get("end_statement", "").strip()

                # 2. Validaciones de la Question
                if not difficulty_level:
                    messages.error(request, "El nivel de dificultad es obligatorio.")
                    return redirect(
                        "questions_create", question_bank_id=question_bank_id
                    )

                if not knowledge_area:
                    messages.error(request, "El área de conocimiento es obligatoria.")
                    return redirect(
                        "questions_create", question_bank_id=question_bank_id
                    )

                if not time:
                    messages.error(request, "El tiempo es obligatorio.")
                    return redirect(
                        "questions_create", question_bank_id=question_bank_id
                    )

                if not topic:
                    messages.error(request, "El tema es obligatorio.")
                    return redirect(
                        "questions_create", question_bank_id=question_bank_id
                    )

                if not statement_type:
                    messages.error(request, "El tipo de enunciado es obligatorio.")
                    return redirect(
                        "questions_create", question_bank_id=question_bank_id
                    )

                if not start_statement:
                    start_statement = Question._meta.get_field(
                        "start_statement"
                    ).default

                if not end_statement:
                    end_statement = Question._meta.get_field("end_statement").default

                # 3. En base al statement_type se debe recolectar el dato correspondiente:
                statement_text = None
                statement_image = None
                statement_audio = None

                if statement_type == "text":
                    statement_text = request.POST.get("statement_text", "").strip()
                elif statement_type == "image":
                    if "statement_image" in request.FILES:
                        statement_image = request.FILES["statement_image"]
                        statement_image.name = generate_unique_filename(statement_image)
                elif statement_type == "audio":
                    if "statement_audio" in request.FILES:
                        statement_audio = request.FILES["statement_audio"]
                        statement_audio.name = generate_unique_filename(statement_audio)

                # 4. Guardamos la Question:
                question = Question.objects.create(
                    bank_id=question_bank_id,
                    difficulty_level_id=difficulty_level,
                    knowledge_area_id=knowledge_area,
                    time=time,
                    topic=topic,
                    start_statement=start_statement,
                    end_statement=end_statement,
                    statement_type=statement_type,
                    statement_text=statement_text,
                    statement_image=statement_image,
                    statement_audio=statement_audio,
                    is_active=True,
                )

                # 5. Recolectar las opciones de respuesta:
                options_data = {}
                for key, value in request.POST.items():
                    if key.startswith("options["):
                        # ejemplo key: options[1][option_type]
                        # sacamos el índice
                        index = key.split("[")[1].split("]")[0]
                        field = key.split("[")[2].replace("]", "")
                        options_data.setdefault(index, {})[field] = value

                # Añadir archivos (image/audio) de las opciones
                for key, value in request.FILES.items():
                    if key.startswith("options["):
                        index = key.split("[")[1].split("]")[0]
                        field = key.split("[")[2].replace("]", "")
                        options_data.setdefault(index, {})[field] = value

                # Crear las opciones
                for index, data in options_data.items():
                    if data.get("option_type") == "image":
                        data["option_image"].name = generate_unique_filename(
                            data["option_image"]
                        )
                    elif data.get("option_type") == "audio":
                        data["option_audio"].name = generate_unique_filename(
                            data["option_audio"]
                        )

                    option = AnswerOption.objects.create(
                        question=question,
                        option_type=data.get("option_type", "text"),
                        option_text=(
                            data.get("option_text", "").strip()
                            if data.get("option_type") == "text"
                            else None
                        ),
                        option_image=(
                            data.get("option_image")
                            if data.get("option_type") == "image"
                            else None
                        ),
                        option_audio=(
                            data.get("option_audio")
                            if data.get("option_type") == "audio"
                            else None
                        ),
                        feedback=data.get("feedback", "").strip(),
                        is_correct=data.get("is_correct", "") == "on",
                        is_active=data.get("is_active", "") == "on",
                    )
                    option.save()

                messages.success(request, "Pregunta creada exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al crear la pregunta: {str(e)}")
            return redirect(
                "questions_bank_questions", question_bank_id=question_bank_id
            )


@login_required(login_url="auth_login")
@is_admin
def deactivate(request, question_bank_id, question_id):
    if request.method == "POST":
        try:
            question = get_object_or_404(Question, pk=question_id)
            question.is_active = False
            question.save()
            messages.success(request, "Pregunta desactivada exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al desactivar la pregunta: {str(e)}")
    return redirect("questions_bank_questions", question_bank_id=question_bank_id)


@login_required(login_url="auth_login")
@is_admin
def activate(request, question_bank_id, question_id):
    if request.method == "POST":
        try:
            question = get_object_or_404(Question, pk=question_id)
            question.is_active = True
            question.save()
            messages.success(request, "Pregunta activada exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al activar la pregunta: {str(e)}")
    return redirect("questions_bank_questions", question_bank_id=question_bank_id)


@login_required(login_url="auth_login")
@is_admin
def delete(request, question_bank_id, question_id):
    if request.method == "POST":
        try:
            question = get_object_or_404(Question, pk=question_id)
            question.deleted_at = timezone.now()
            question.save()

            messages.success(request, "Pregunta eliminada exitosamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar la pregunta: {str(e)}")
    return redirect("questions_bank_questions", question_bank_id=question_bank_id)
