from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from decorators.admin import is_admin
from decorators.super_admin import is_super_admin
from app.models import QuestionBank, Institution
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.contrib import messages
from django.utils import timezone


@login_required(login_url="auth_login")
@is_admin
def table(request):
    query = request.GET.get("q", "").strip()
    question_banks = QuestionBank.objects.filter(deleted_at__isnull=True).annotate(
        total_questions=Count(
            "questions",
            filter=Q(questions__is_active=True, questions__deleted_at__isnull=True),
        )
    )

    if request.user.institution:
        question_banks = question_banks.filter(institution=request.user.institution)

    if query:
        question_banks = question_banks.filter(Q(name__icontains=query))

    question_banks = question_banks.order_by("-created_at")

    for qb in question_banks:
        basics_count = qb.questions.filter(
            difficulty_level__name="Básico", is_active=True, deleted_at__isnull=True
        ).count()

        intermediate_count = qb.questions.filter(
            difficulty_level__name="Intermedio", is_active=True, deleted_at__isnull=True
        ).count()

        advanced_count = qb.questions.filter(
            difficulty_level__name="Avanzado", is_active=True, deleted_at__isnull=True
        ).count()

        qb.total_questions_basics = basics_count
        qb.total_questions_intermediate = intermediate_count
        qb.total_questions_advanced = advanced_count

    paginator = Paginator(question_banks, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }
    return render(request, "questions/bank/table.html", context)


@login_required(login_url="auth_login")
@is_admin
def create(request):
    institutions = Institution.objects.filter(deleted_at__isnull=True)

    if request.user.institution:
        institutions = institutions.filter(id=request.user.institution.id)

    return render(
        request,
        "questions/bank/form.html",
        {
            "institutions": institutions,
        },
    )


@login_required(login_url="auth_login")
@is_admin
def update(request, question_bank_id):
    if request.method == "GET":
        try:
            question_bank = get_object_or_404(QuestionBank, id=question_bank_id)
            institutions = Institution.objects.filter(deleted_at__isnull=True)

            if request.user.institution:
                institutions = institutions.filter(id=request.user.institution.id)

            return render(
                request,
                "questions/bank/form.html",
                {
                    "question_bank": question_bank,
                    "institutions": institutions,
                },
            )
        except Exception as e:
            messages.error(request, f"Error al cargar el banco de preguntas: {str(e)}")
            return redirect("questions_bank_table")


@login_required(login_url="auth_login")
@is_admin
def save(request):
    if request.method == "POST":
        question_bank_id = request.POST.get("question_bank_id")

        if question_bank_id:
            try:
                question_bank = get_object_or_404(QuestionBank, id=question_bank_id)
                name = request.POST.get("name")
                description = request.POST.get("description")
                institution_id = request.POST.get("institution")

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect(
                        "questions_bank_update", question_bank_id=question_bank_id
                    )

                if not description:
                    messages.error(request, "La descripción es obligatoria.")
                    return redirect(
                        "questions_bank_update", question_bank_id=question_bank_id
                    )

                if not institution_id:
                    messages.error(request, "La institución es obligatoria.")
                    return redirect(
                        "questions_bank_update", question_bank_id=question_bank_id
                    )

                question_bank.name = name
                question_bank.description = description
                question_bank.institution_id = institution_id
                question_bank.is_active = True
                question_bank.save()

                messages.success(
                    request, "Banco de preguntas actualizado correctamente."
                )
            except Exception as e:
                messages.error(
                    request, f"Error al actualizar el banco de preguntas: {str(e)}"
                )
            return redirect("questions_bank_table")
        else:
            try:
                name = request.POST.get("name")
                description = request.POST.get("description")
                institution_id = request.POST.get("institution")

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("questions_bank_create")

                if not description:
                    messages.error(request, "La descripción es obligatoria.")
                    return redirect("questions_bank_create")

                if not institution_id:
                    messages.error(request, "La institución es obligatoria.")
                    return redirect("questions_bank_create")

                QuestionBank.objects.create(
                    name=name,
                    description=description,
                    institution_id=institution_id,
                    is_active=True,
                )

                messages.success(request, "Banco de preguntas creado correctamente.")
            except Exception as e:
                messages.error(
                    request, f"Error al crear el banco de preguntas: {str(e)}"
                )
            return redirect("questions_bank_table")


@login_required(login_url="auth_login")
@is_admin
def deactivate(request, question_bank_id):
    if request.method == "POST":
        try:
            question_bank = get_object_or_404(QuestionBank, id=question_bank_id)
            question_bank.is_active = False
            question_bank.save()
            messages.success(request, "Banco de preguntas desactivado correctamente.")
        except Exception as e:
            messages.error(
                request, f"Error al desactivar el banco de preguntas: {str(e)}"
            )
    return redirect("questions_bank_table")


@login_required(login_url="auth_login")
@is_admin
def activate(request, question_bank_id):
    if request.method == "POST":
        try:
            question_bank = get_object_or_404(QuestionBank, id=question_bank_id)
            question_bank.is_active = True
            question_bank.save()
            messages.success(request, "Banco de preguntas activado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al activar el banco de preguntas: {str(e)}")
    return redirect("questions_bank_table")


@login_required(login_url="auth_login")
@is_super_admin
def delete(request, question_bank_id):
    if request.method == "POST":
        try:
            question_bank = get_object_or_404(QuestionBank, id=question_bank_id)
            question_bank.deleted_at = timezone.now()
            question_bank.save()

            messages.success(request, "Banco de preguntas eliminado correctamente.")
        except Exception as e:
            messages.error(
                request, f"Error al eliminar el banco de preguntas: {str(e)}"
            )
    return redirect("questions_bank_table")


@login_required(login_url="auth_login")
@is_admin
def questions(request, question_bank_id):
    query = request.GET.get("q", "")
    question_bank = get_object_or_404(
        QuestionBank, id=question_bank_id, deleted_at__isnull=True
    )

    questions = question_bank.questions.filter(deleted_at__isnull=True).order_by(
        "-created_at"
    )

    if query:
        questions = questions.filter(
            Q(knowledge_area__name__icontains=query)
            | Q(topic__icontains=query)
            | Q(statement_text__icontains=query)
            | Q(start_statement__icontains=query)
            | Q(end_statement__icontains=query)
        )

    paginator = Paginator(questions, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)
    context = {"question_bank": question_bank, "page_obj": page_obj, "query": query}
    return render(request, "questions/question/table.html", context)
