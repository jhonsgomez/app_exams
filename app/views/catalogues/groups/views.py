from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from decorators.admin import is_admin
from app.models import Group, Institution
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils import timezone


@login_required(login_url="auth_login")
@is_admin
def table(request):
    query = request.GET.get("q", "").strip()
    groups = Group.objects.filter(deleted_at__isnull=True)

    if request.user.institution:
        institution = request.user.institution
        groups = groups.filter(institution=institution)

    if query:
        groups = groups.filter(Q(name__icontains=query))

    groups = groups.order_by("-created_at")

    paginator = Paginator(groups, 5)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    context = {
        "page_obj": page_obj,
        "query": query,
    }

    return render(request, "catalogues/groups/table.html", context)


@login_required(login_url="auth_login")
@is_admin
def create(request):
    institutions = Institution.objects.filter(
        deleted_at__isnull=True, institution_type=3
    )

    return render(
        request, "catalogues/groups/form.html", {"institutions": institutions}
    )


@login_required(login_url="auth_login")
@is_admin
def update(request, group_id):
    if request.method == "GET":
        try:
            group = get_object_or_404(Group, pk=group_id)
            institutions = Institution.objects.filter(
                deleted_at__isnull=True, institution_type=3
            )
            return render(
                request,
                "catalogues/groups/form.html",
                {"group": group, "institutions": institutions},
            )
        except Exception as e:
            messages.error(request, f"Error al cargar el grupo: {str(e)}")
            return redirect("groups_table")


@login_required(login_url="auth_login")
@is_admin
def save(request):
    if request.method == "POST":
        group_id = request.POST.get("group_id")

        if group_id:
            try:
                group = get_object_or_404(Group, pk=group_id)
                name = request.POST.get("name", "").strip()
                institution_id = request.POST.get("institution", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("groups_update", group_id=group.pk)

                if not institution_id:
                    messages.error(request, "La institución es obligatoria.")
                    return redirect("groups_update", group_id=group.pk)

                if (
                    Group.objects.filter(
                        name__iexact=name, institution_id=institution_id
                    )
                    .exclude(pk=group.pk)
                    .exists()
                ):
                    messages.error(
                        request, "Ya existe un grupo con ese nombre en la institución."
                    )
                    return redirect("groups_update", group_id=group.pk)

                group.name = name
                group.institution_id = institution_id
                group.updated_at = timezone.now()
                group.save()
                messages.success(request, "Grupo actualizado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al actualizar el grupo: {str(e)}")

            return redirect("groups_table")
        else:
            try:
                name = request.POST.get("name", "").strip()
                institution_id = request.POST.get("institution", "").strip()

                if not name:
                    messages.error(request, "El nombre es obligatorio.")
                    return redirect("groups_create")

                if not institution_id:
                    messages.error(request, "La institución es obligatoria.")
                    return redirect("groups_create")

                if Group.objects.filter(
                    name__iexact=name, institution_id=institution_id
                ).exists():
                    messages.error(
                        request, "Ya existe un grupo con ese nombre en la institución."
                    )
                    return redirect("groups_create")

                Group.objects.create(name=name, institution_id=institution_id)
                messages.success(request, "Grupo creado correctamente.")
            except Exception as e:
                messages.error(request, f"Error al crear el grupo: {str(e)}")

            return redirect("groups_table")


@login_required(login_url="auth_login")
@is_admin
def delete(request, group_id):
    if request.method == "POST":
        try:
            group = get_object_or_404(Group, pk=group_id)
            group.deleted_at = timezone.now()
            group.save()
            messages.success(request, "Grupo eliminado correctamente.")
        except Exception as e:
            messages.error(request, f"Error al eliminar el grupo: {str(e)}")

    return redirect("groups_table")
