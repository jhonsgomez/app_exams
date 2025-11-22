from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.super_admin import is_super_admin
from app.models import InstitutionType
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone


@login_required(login_url="auth_login")
@is_super_admin
def table(request):
    query = request.GET.get("q", "").strip()
    institution_types = InstitutionType.objects.filter(deleted_at__isnull=True)

    if query:
        institution_types = institution_types.filter(Q(name__icontains=query))

    institution_types = institution_types.order_by("-created_at")

    paginator = Paginator(institution_types, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    return render(request, "catalogues/institution_types/table.html", context)


@login_required(login_url="auth_login")
@is_super_admin
def create(request):
    return render(request, "catalogues/institution_types/form.html")


@login_required(login_url="auth_login")
@is_super_admin
def update(request, institution_type_id):
    if request.method == "GET":
        try:
            institution_type = get_object_or_404(
                InstitutionType, pk=institution_type_id
            )
            return render(
                request,
                "catalogues/institution_types/form.html",
                {"institution_type": institution_type},
            )
        except Exception as e:
            messages.error(request, f"Error al cargar el tipo de institución: {str(e)}")
            return redirect("institution_types_table")


@login_required(login_url="auth_login")
@is_super_admin
def save(request):
    if request.method == "POST":
        institution_type_id = request.POST.get("institution_type_id")

        if institution_type_id:
            try:
                institution_type = get_object_or_404(
                    InstitutionType, pk=institution_type_id
                )
                name = request.POST.get("name", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect(
                        "institution_types_update",
                        institution_type_id=institution_type.pk,
                    )

                if (
                    InstitutionType.objects.filter(name__iexact=name)
                    .exclude(pk=institution_type.pk)
                    .exists()
                ):
                    messages.error(
                        request, "Ya existe un tipo de institución con ese nombre."
                    )
                    return redirect(
                        "institution_types_update",
                        institution_type_id=institution_type.pk,
                    )

                institution_type.name = name
                institution_type.save()
                messages.success(
                    request, "Tipo de institución actualizado correctamente."
                )
            except Exception as e:
                messages.error(
                    request, f"Error al actualizar el tipo de institución: {str(e)}"
                )

            return redirect("institution_types_table")
        else:
            try:
                name = request.POST.get("name", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("institution_types_create")

                if InstitutionType.objects.filter(name__iexact=name).exists():
                    messages.error(
                        request, "Ya existe un tipo de institución con ese nombre."
                    )
                    return redirect("institution_types_create")

                InstitutionType.objects.create(name=name)
                messages.success(request, "Tipo de institución creado correctamente.")
            except Exception as e:
                messages.error(
                    request, f"Error al crear el tipo de institución: {str(e)}"
                )

            return redirect("institution_types_table")


@login_required(login_url="auth_login")
@is_super_admin
def delete(request, institution_type_id):
    if request.method == "POST":
        try:
            institution_type = get_object_or_404(
                InstitutionType, pk=institution_type_id
            )
            institution_type.deleted_at = timezone.now()
            institution_type.save()
            messages.success(request, "Tipo de institución eliminado correctamente.")
        except Exception as e:
            messages.error(
                request, f"Error al eliminar el tipo de institución: {str(e)}"
            )

    return redirect("institution_types_table")
