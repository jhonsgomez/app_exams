from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from decorators.super_admin import is_super_admin
from app.models import DifficultyLevel
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone


@login_required(login_url="auth_login")
@is_super_admin
def table(request):
    query = request.GET.get("q", "").strip()
    difficulty_levels = DifficultyLevel.objects.filter(deleted_at__isnull=True)

    if query:
        difficulty_levels = difficulty_levels.filter(Q(name__icontains=query))

    difficulty_levels = difficulty_levels.order_by("-created_at")

    paginator = Paginator(difficulty_levels, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }
    return render(request, "questions/difficulty/table.html", context)


@login_required(login_url="auth_login")
@is_super_admin
def create(request):
    return render(request, "questions/difficulty/form.html")


@login_required(login_url="auth_login")
@is_super_admin
def update(request, difficulty_level_id):
    if request.method == "GET":
        try:
            difficulty_level = get_object_or_404(
                DifficultyLevel, pk=difficulty_level_id
            )
            return render(
                request,
                "questions/difficulty/form.html",
                {"difficulty_level": difficulty_level},
            )
        except Exception as e:
            messages.error(
                request, f"Error al obtener el nivel de dificultad: {str(e)}"
            )
            return redirect("difficulty_table")


@login_required(login_url="auth_login")
@is_super_admin
def save(request):
    if request.method == "POST":
        difficulty_level_id = request.POST.get("difficulty_level_id")

        if difficulty_level_id:
            try:
                difficulty_level = get_object_or_404(
                    DifficultyLevel, pk=difficulty_level_id
                )

                name = request.POST.get("name").strip()
                description = request.POST.get("description", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect(
                        "difficulty_update", difficulty_level_id=difficulty_level.pk
                    )

                if not description:
                    messages.error(request, "La descripción es obligatoria.")
                    return redirect(
                        "difficulty_update", difficulty_level_id=difficulty_level.pk
                    )

                if (
                    DifficultyLevel.objects.filter(name__iexact=name)
                    .exclude(pk=difficulty_level.pk)
                    .exists()
                ):
                    messages.error(
                        request, "Ya existe un nivel de dificultad con ese nombre."
                    )
                    return redirect(
                        "difficulty_update", difficulty_level_id=difficulty_level.pk
                    )

                difficulty_level.name = name
                difficulty_level.description = description
                difficulty_level.save()

                messages.success(
                    request, "Nivel de dificultad actualizado correctamente."
                )
                return redirect("difficulty_table")

            except Exception as e:
                messages.error(
                    request, f"Error al actualizar el nivel de dificultad: {str(e)}"
                )
            return redirect("difficulty_table")

        else:
            try:
                name = request.POST.get("name").strip()
                description = request.POST.get("description", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("difficulty_create")

                if not description:
                    messages.error(request, "La descripción es obligatoria.")
                    return redirect("difficulty_create")

                if DifficultyLevel.objects.filter(name__iexact=name).exists():
                    messages.error(
                        request, "Ya existe un nivel de dificultad con ese nombre."
                    )
                    return redirect("difficulty_create")

                DifficultyLevel.objects.create(name=name, description=description)
                messages.success(request, "Nivel de dificultad creado correctamente.")
            except Exception as e:
                messages.error(
                    request, f"Error al crear el nivel de dificultad: {str(e)}"
                )
            return redirect("difficulty_table")


@login_required(login_url="auth_login")
@is_super_admin
def delete(request, difficulty_level_id):
    if request.method == "POST":
        try:
            difficulty_level = get_object_or_404(
                DifficultyLevel, pk=difficulty_level_id
            )
            difficulty_level.deleted_at = timezone.now()
            difficulty_level.save()
            messages.success(request, "Nivel de dificultad eliminado correctamente.")
        except Exception as e:
            messages.error(
                request, f"Error al eliminar el nivel de dificultad: {str(e)}"
            )
    return redirect("difficulty_table")
