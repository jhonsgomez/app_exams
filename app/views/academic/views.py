from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.admin import is_admin
from app.models import (
    AcademicDepartment,
    Modality,
    Representative,
    Institution,
    AcademicLevel,
)
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone


@login_required(login_url="auth_login")
@is_admin
def table(request):
    query = request.GET.get("q", "").strip()
    academic_departments = AcademicDepartment.objects.filter(deleted_at__isnull=True)

    if request.user.institution:
        academic_departments = academic_departments.filter(
            institution=request.user.institution
        )

    if query:
        academic_departments = academic_departments.filter(Q(name__icontains=query))

    academic_departments = academic_departments.order_by("-created_at")

    paginator = Paginator(academic_departments, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    return render(request, "academic/table.html", context)


@login_required(login_url="auth_login")
@is_admin
def create(request):
    modalities = Modality.objects.filter(deleted_at__isnull=True)
    representatives = Representative.objects.filter(deleted_at__isnull=True)
    institutions = Institution.objects.filter(
        deleted_at__isnull=True, institution_type__in=[1, 2]
    )
    academic_levels = AcademicLevel.objects.all()

    return render(
        request,
        "academic/form.html",
        {
            "modalities": modalities,
            "representatives": representatives,
            "institutions": institutions,
            "academic_levels": academic_levels,
        },
    )


@login_required(login_url="auth_login")
@is_admin
def update(request, academic_department_id):
    if request.method == "GET":
        try:
            academic_department = get_object_or_404(
                AcademicDepartment, pk=academic_department_id
            )
            modalities = Modality.objects.filter(deleted_at__isnull=True)
            representatives = Representative.objects.filter(deleted_at__isnull=True)
            institutions = Institution.objects.filter(
                deleted_at__isnull=True, institution_type__in=[1, 2]
            )
            academic_levels = AcademicLevel.objects.filter(deleted_at__isnull=True)

            return render(
                request,
                "academic/form.html",
                {
                    "academic_department": academic_department,
                    "modalities": modalities,
                    "representatives": representatives,
                    "institutions": institutions,
                    "academic_levels": academic_levels,
                },
            )
        except Exception as e:
            messages.error(request, f"Error al cargar el programa académico: {e}")
            return redirect("academic_departments_table")


@login_required(login_url="auth_login")
@is_admin
def save(request):
    if request.method == "POST":
        academic_department_id = request.POST.get("academic_department_id")

        if academic_department_id:
            try:
                academic_department = get_object_or_404(
                    AcademicDepartment, pk=academic_department_id
                )
                name = request.POST.get("name", "").strip()
                modality_id = request.POST.get("modality")
                representative_id = request.POST.get("representative")
                institution_id = request.POST.get("institution")
                academic_level_id = request.POST.get("academic_level")

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect(
                        "academic_departments_update", academic_department_id
                    )

                if not modality_id:
                    messages.error(request, "La modalidad es obligatoria.")
                    return redirect(
                        "academic_departments_update", academic_department_id
                    )

                if not representative_id:
                    messages.error(request, "El representante es obligatorio.")
                    return redirect(
                        "academic_departments_update", academic_department_id
                    )

                if not institution_id:
                    messages.error(request, "La institución es obligatoria.")
                    return redirect(
                        "academic_departments_update", academic_department_id
                    )
                    
                if not academic_level_id:
                    messages.error(request, "El nivel académico es obligatorio.")
                    return redirect(
                        "academic_departments_update", academic_department_id
                    )

                academic_department.name = name
                academic_department.modality_id = modality_id
                academic_department.representative_id = representative_id
                academic_department.institution_id = institution_id
                academic_department.academic_level_id = academic_level_id
                academic_department.updated_at = timezone.now()
                academic_department.save()

                messages.success(
                    request, "Programa académico actualizado exitosamente."
                )
            except Exception as e:
                messages.error(
                    request, f"Error al actualizar el programa académico: {e}"
                )

            return redirect("academic_departments_table")
        else:
            try:
                name = request.POST.get("name", "").strip()
                modality_id = request.POST.get("modality")
                representative_id = request.POST.get("representative")
                institution_id = request.POST.get("institution")
                academic_level_id = request.POST.get("academic_level")

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("academic_departments_create")

                if not modality_id:
                    messages.error(request, "La modalidad es obligatoria.")
                    return redirect("academic_departments_create")

                if not representative_id:
                    messages.error(request, "El representante es obligatorio.")
                    return redirect("academic_departments_create")

                if not institution_id:
                    messages.error(request, "La institución es obligatoria.")
                    return redirect("academic_departments_create")
                
                if not academic_level_id:
                    messages.error(request, "El nivel académico es obligatorio.")
                    return redirect("academic_departments_create")

                AcademicDepartment.objects.create(
                    name=name,
                    modality_id=modality_id,
                    representative_id=representative_id,
                    institution_id=institution_id,
                    academic_level_id=academic_level_id,
                )

                messages.success(request, "Programa académico creado exitosamente.")
            except Exception as e:
                messages.error(request, f"Error al crear el programa académico: {e}")

            return redirect("academic_departments_table")


@login_required(login_url="auth_login")
@is_admin
def delete(request, academic_department_id):
    if request.method == "POST":
        try:
            academic_department = get_object_or_404(
                AcademicDepartment, pk=academic_department_id
            )
            academic_department.deleted_at = timezone.now()
            academic_department.save()

            messages.success(request, "Programa académico eliminado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar el programa académico: {e}")

    return redirect("academic_departments_table")
