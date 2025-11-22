from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth.decorators import login_required
from decorators.admin import is_admin
from app.models import KnowledgeArea
from django.core.paginator import Paginator
from django.db.models import Q
from django.contrib import messages
from django.utils import timezone


@login_required(login_url="auth_login")
@is_admin
def table(request):
    query = request.GET.get("q", "").strip()
    knowledge_areas = KnowledgeArea.objects.filter(deleted_at__isnull=True)

    if query:
        knowledge_areas = knowledge_areas.filter(Q(name__icontains=query))

    knowledge_areas = knowledge_areas.order_by("-created_at")

    paginator = Paginator(knowledge_areas, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }
    return render(request, "questions/knowledge/table.html", context)


@login_required(login_url="auth_login")
@is_admin
def create(request):
    return render(request, "questions/knowledge/form.html")


@login_required(login_url="auth_login")
@is_admin
def update(request, knowledge_area_id):
    if request.method == "GET":
        try:
            knowledge_area = get_object_or_404(KnowledgeArea, pk=knowledge_area_id)
            return render(
                request,
                "questions/knowledge/form.html",
                {"knowledge_area": knowledge_area},
            )
        except Exception as e:
            messages.error(
                request, f"Error al obtener el área de conocimiento: {str(e)}"
            )
            return redirect("knowledge_table")


@login_required(login_url="auth_login")
@is_admin
def save(request):
    if request.method == "POST":
        knowledge_area_id = request.POST.get("knowledge_area_id")

        if knowledge_area_id:
            try:
                knowledge_area = get_object_or_404(KnowledgeArea, pk=knowledge_area_id)
                name = request.POST.get("name").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect(
                        "knowledge_update", knowledge_area_id=knowledge_area.pk
                    )

                if (
                    KnowledgeArea.objects.filter(name__iexact=name)
                    .exclude(pk=knowledge_area.pk)
                    .exists()
                ):
                    messages.error(
                        request, "Ya existe un área de conocimiento con ese nombre."
                    )
                    return redirect(
                        "knowledge_update", knowledge_area_id=knowledge_area.pk
                    )

                knowledge_area.name = name
                knowledge_area.save()
                messages.success(
                    request, "Área de conocimiento actualizada correctamente."
                )
            except Exception as e:
                messages.error(
                    request, f"Error al actualizar el área de conocimiento: {str(e)}"
                )
            return redirect("knowledge_table")
        else:
            try:
                name = request.POST.get("name").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("knowledge_create")

                if KnowledgeArea.objects.filter(name__iexact=name).exists():
                    messages.error(
                        request, "Ya existe un área de conocimiento con ese nombre."
                    )
                    return redirect("knowledge_create")

                KnowledgeArea.objects.create(name=name)
                messages.success(request, "Área de conocimiento creada correctamente.")
            except Exception as e:
                messages.error(
                    request, f"Error al crear el área de conocimiento: {str(e)}"
                )
            return redirect("knowledge_table")


@login_required(login_url="auth_login")
@is_admin
def delete(request, knowledge_area_id):
    if request.method == "POST":
        try:
            knowledge_area = get_object_or_404(KnowledgeArea, pk=knowledge_area_id)
            knowledge_area.deleted_at = timezone.now()
            knowledge_area.save()
            messages.success(request, "Área de conocimiento eliminada correctamente.")
        except Exception as e:
            messages.error(
                request, f"Error al eliminar el área de conocimiento: {str(e)}"
            )
    return redirect("knowledge_table")
