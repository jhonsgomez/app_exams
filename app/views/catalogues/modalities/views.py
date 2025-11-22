from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.super_admin import is_super_admin
from app.models import Modality
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone


@login_required(login_url="auth_login")
@is_super_admin
def table(request):
    query = request.GET.get("q", "").strip()
    modalities = Modality.objects.filter(deleted_at__isnull=True)

    if query:
        modalities = modalities.filter(Q(name__icontains=query))

    modalities = modalities.order_by("-created_at")

    paginator = Paginator(modalities, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    return render(request, "catalogues/modalities/table.html", context)


@login_required(login_url="auth_login")
@is_super_admin
def create(request):
    return render(request, "catalogues/modalities/form.html")


@login_required(login_url="auth_login")
@is_super_admin
def update(request, modality_id):
    if request.method == "GET":
        try:
            modality = get_object_or_404(Modality, pk=modality_id)
            return render(
                request,
                "catalogues/modalities/form.html",
                {"modality": modality},
            )
        except Exception as e:
            messages.error(request, f"Error al cargar la modalidad: {str(e)}")
            return redirect("modalities_table")


@login_required(login_url="auth_login")
@is_super_admin
def save(request):
    if request.method == "POST":
        modality_id = request.POST.get("modality_id")

        if modality_id:
            try:
                modality = get_object_or_404(Modality, pk=modality_id)
                name = request.POST.get("name", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect(
                        "modalities_update",
                        modality_id=modality.pk,
                    )

                if (
                    Modality.objects.filter(name__iexact=name)
                    .exclude(pk=modality.pk)
                    .exists()
                ):
                    messages.error(request, "Ya existe una modalidad con ese nombre.")
                    return redirect(
                        "modalities_update",
                        modality_id=modality.pk,
                    )

                modality.name = name
                modality.save()
                messages.success(request, "Modalidad actualizada correctamente.")
            except Exception as e:
                messages.error(request, f"Error al actualizar la modalidad: {str(e)}")

            return redirect("modalities_table")
        else:
            try:
                name = request.POST.get("name", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("modalities_create")

                if Modality.objects.filter(name__iexact=name).exists():
                    messages.error(request, "Ya existe una modalidad con ese nombre.")
                    return redirect("modalities_create")

                Modality.objects.create(name=name)
                messages.success(request, "Modalidad creada correctamente.")
            except Exception as e:
                messages.error(request, f"Error al crear la modalidad: {str(e)}")

            return redirect("modalities_table")


@login_required(login_url="auth_login")
@is_super_admin
def delete(request, modality_id):
    if request.method == "POST":
        try:
            modality = get_object_or_404(Modality, pk=modality_id)
            modality.deleted_at = timezone.now()
            modality.save()
            messages.success(request, "Modalidad eliminada correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar la modalidad: {str(e)}")

        return redirect("modalities_table")
