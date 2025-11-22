from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.super_admin import is_super_admin
from app.models import (
    Institution,
    InstitutionType,
    Principal,
    Group,
    AcademicDepartment,
)
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone
from django.http import JsonResponse


@login_required(login_url="auth_login")
@is_super_admin
def table(request):
    query = request.GET.get("q", "").strip()
    institutions = Institution.objects.filter(deleted_at__isnull=True)

    if query:
        institutions = institutions.filter(Q(name__icontains=query))

    institutions = institutions.order_by("-created_at")

    paginator = Paginator(institutions, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    return render(request, "institutions/table.html", context)


@login_required(login_url="auth_login")
@is_super_admin
def create(request):
    institution_types = InstitutionType.objects.filter(deleted_at__isnull=True)
    principals = Principal.objects.filter(deleted_at__isnull=True)

    return render(
        request,
        "institutions/form.html",
        {
            "institution_types": institution_types,
            "principals": principals,
        },
    )


def institution_info(request, institution_id):
    try:
        institution = Institution.objects.get(
            pk=institution_id, deleted_at__isnull=True
        )
        institution_type = institution.institution_type.id

        if institution_type == 3:
            groups = Group.objects.filter(
                institution=institution, deleted_at__isnull=True
            )
            return JsonResponse(
                {
                    "institution_type": 3,
                    "groups": [{"id": g.id, "name": g.name} for g in groups],
                }
            )

        else:
            departments = AcademicDepartment.objects.filter(
                institution=institution, deleted_at__isnull=True
            )
            return JsonResponse(
                {
                    "institution_type": institution_type,
                    "departments": [{"id": d.id, "name": d.name} for d in departments],
                }
            )

    except Institution.DoesNotExist:
        return JsonResponse({"error": "Institución no encontrada"}, status=404)


@login_required(login_url="auth_login")
@is_super_admin
def update(request, institution_id):
    if request.method == "GET":
        try:
            institution = get_object_or_404(Institution, pk=institution_id)
            institution_types = InstitutionType.objects.filter(deleted_at__isnull=True)
            principals = Principal.objects.filter(deleted_at__isnull=True)

            return render(
                request,
                "institutions/form.html",
                {
                    "institution": institution,
                    "institution_types": institution_types,
                    "principals": principals,
                },
            )
        except Exception as e:
            messages.error(request, f"Error al cargar la institución: {str(e)}")
            return redirect("institutions_table")


@login_required(login_url="auth_login")
@is_super_admin
def save(request):
    if request.method == "POST":
        institution_id = request.POST.get("institution_id")

        if institution_id:
            try:
                institution = get_object_or_404(Institution, pk=institution_id)
                name = request.POST.get("name", "").strip()
                tax_id = request.POST.get("tax_id", "").strip()
                institution_type_id = request.POST.get("institution_type")
                principal_id = request.POST.get("principal")

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect(
                        "institutions_update", institution_id=institution.pk
                    )

                if not tax_id:
                    messages.error(request, "El NIT es obligatorio.")
                    return redirect(
                        "institutions_update", institution_id=institution.pk
                    )

                if not institution_type_id:
                    messages.error(request, "El tipo de institución es obligatorio.")
                    return redirect(
                        "institutions_update", institution_id=institution.pk
                    )

                if not principal_id:
                    messages.error(request, "El rector es obligatorio.")
                    return redirect(
                        "institutions_update", institution_id=institution.pk
                    )

                if (
                    Institution.objects.filter(name__iexact=name)
                    .exclude(pk=institution.pk)
                    .exists()
                ):
                    messages.error(
                        request, "Ya existe una institución con este nombre."
                    )
                    return redirect(
                        "institutions_update", institution_id=institution.pk
                    )

                institution.name = name
                institution.tax_id = tax_id
                institution.institution_type_id = institution_type_id
                institution.principal_id = principal_id
                institution.updated_at = timezone.now()
                institution.save()

                messages.success(request, "Institución actualizada correctamente.")
            except Exception as e:
                messages.error(request, f"Error al actualizar la institución: {str(e)}")

            return redirect("institutions_table")
        else:
            try:
                name = request.POST.get("name", "").strip()
                tax_id = request.POST.get("tax_id", "").strip()
                institution_type_id = request.POST.get("institution_type")
                principal_id = request.POST.get("principal")

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("institutions_create")

                if not tax_id:
                    messages.error(request, "El NIT es obligatorio.")
                    return redirect("institutions_create")

                if not institution_type_id:
                    messages.error(request, "El tipo de institución es obligatorio.")
                    return redirect("institutions_create")

                if not principal_id:
                    messages.error(request, "El rector es obligatorio.")
                    return redirect("institutions_create")

                if Institution.objects.filter(name__iexact=name).exists():
                    messages.error(
                        request, "Ya existe una institución con este nombre."
                    )
                    return redirect("institutions_create")

                Institution.objects.create(
                    name=name,
                    tax_id=tax_id,
                    institution_type_id=institution_type_id,
                    principal_id=principal_id,
                )
                messages.success(request, "Institución creada correctamente.")
            except Exception as e:
                messages.error(request, f"Error al crear la institución: {str(e)}")

            return redirect("institutions_table")


@login_required(login_url="auth_login")
@is_super_admin
def delete(request, institution_id):
    if request.method == "POST":
        try:
            institution = get_object_or_404(Institution, pk=institution_id)
            institution.deleted_at = timezone.now()
            institution.save()
            messages.success(request, "Institución eliminada correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar la institución: {str(e)}")

    return redirect("institutions_table")
